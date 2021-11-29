import logging
from boltons.iterutils import remap
from zeep.xsd.valueobjects import CompoundValue
from jabberwock.axlhandler import AXLClient
from jabberwock import exceptions


PF_LIST = 'list'
PF_GET = 'get'
PF_UPDATE = 'update'
PF_ADD = 'add'
PF_REMOVE = 'remove'
PF_RESET = 'reset'
XSD_NS = 'ns0'

log = logging.getLogger('jabberwock')


class BaseCUCMModel(object):
    """
    Provide base functionality for all logical entities in Cisco Unified Communications Solutions (CUCM).

    This will make the bridge between zeep and CUCM objects.
    In addition, all standard AXL operations are implemented here.

    Attributes:
        __name__: Name of the logical CUCM object (e.g. User, Phone, RoutePartition)
        __config__: Name of the configuration
        __client: Client object used to communicate with AXL API
        __attached__: Is this object associated with an AXL object?
        __updateable__: List containing all changed attributes since last object load
    """

    __config_name__ = ''
    __config__ = None
    __client__ = None
    __attached__ = False
    __update_request__ = None
    __update_substitutions__ = None
    uuid = None

    def __init__(self, *args, **kwargs):
        """
        Create a new CUCM object.
        """
        config_name = kwargs.pop('config_name', 'default')
        self._configure(config_name=config_name)
        self._initialize(**kwargs)

    def __setattr__(self, name, value):
        """
        Set the value of an attribute.

        Keeps track of the name of the attribute that is changed. Generally used for the update method.
        """
        builtin = name.startswith('__') and name.endswith('__')
        if not builtin:
            if self.__attached__:
                self.__setattr_update__(name, value)
        super().__setattr__(name, value)

    def __setattr_update__(self, name, value):
        if name in self.__update_substitutions__.keys():
            name = self.__update_substitutions__[name]
        setattr(self.__update_request__, name, value)

    @classmethod
    def _axl_operation(cls, prefix, name, client):
        """
        Return an AXL operation.
        """
        return getattr(client.axl, '%s%s' % (prefix, name,))

    @classmethod
    def _prepare_result(cls, result, returns):
        """

        :param result:
        :param returns:
        :return:
        """
        unwrapped = result['return']
        if not unwrapped:
            return
        if isinstance(unwrapped, str):
            return
        unwrapped = getattr(unwrapped, cls._first_lower(cls.__name__))
        for obj in unwrapped:
            yield {key: value for (key, value) in obj.__dict__['__values__'].items() if key in returns}

    def _initialize(self, **kwargs):
        """
        a part of init method. If some search criteria was found it
            will automatically load this object.
        """
        self._load(**kwargs)
        self.__update_request__ = self._get_update_request()
        self.__update_substitutions__ = self._get_update_substitutions(self.__update_request__)
        if self.uuid:
            self.__attached__ = True

    def _load(self, **kwargs):
        """
        Get the specified object from Call Manager and merge its attributes with this CUCM object.
        """
        operation = self._axl_operation(PF_GET, self.__name__, self.__client__)
        uuid = kwargs.pop('uuid', '')
        request = getattr(self.__client__.factory, '%s%sReq' % (PF_GET.capitalize(), self.__name__))()
        if uuid:
            criteria = {'uuid': uuid}
        else:
            criteria = {key: value for (key, value) in kwargs.items() if key in request.__dict__['__values__'].keys()}
        try:
            result = operation(**criteria)
            result = getattr(getattr(result, 'return'), self._first_lower(self.__name__))
        except:
            print('Unable to get object. Creating xtype...')
            result = self._get_xtype(**kwargs)
        self._loadattr(result)

    @classmethod
    def _first_lower(cls, name):
        return name[:1].lower() + name[1:] if name else ''

    @classmethod
    def _strip_empty_tags(cls, obj):
        """
        Recursively strip all attributes equal to -1 from an object.

        The AXL update operation can't handle values of -1. This will recursively create a copy of object and remove
        all attributes with a value of -1.
        """
        def visit(path, key, value):
            if value == -1:
                return False
            elif isinstance(value, CompoundValue):
                for i in dir(value):
                    if getattr(value, i) == -1:
                        return False
            return key, value

        return remap(obj, visit=visit)

    @property
    def __name__(self):
        return self.__class__.__name__

    def _configure(self, config_name, toolkit_path):
        """
        Set up AXL client connection.
        """
        self.__client__ = AXLClient.get_client(config_name=config_name)
        self.__config_name__ = config_name

    def _loadattr(self, obj):
        """
        Copy all attributes from an AXL object to this CUCM object.
        """
        for k, v in obj.__dict__['__values__'].items():
            self.__setattr__(k, v)

    def _get_xtype(self, **kwargs):
        """
        Return an XType AXL object.
        """
        x_type = getattr(self.__client__.factory, 'X%s' % self.__name__)()
        tags = dir(x_type)
        kwargs = {key: value for (key, value) in kwargs.items() if key in tags}
        kwargs = self._strip_empty_tags(kwargs)
        x_type = getattr(self.__client__.factory, 'X%s' % self.__name__)(**kwargs)
        return x_type

    def _get_update_request(self, **kwargs):
        return getattr(self.__client__.factory, '%s%sReq' % (PF_UPDATE.capitalize(), self.__name__))(**kwargs)

    def _get_update_substitutions(self, update_request):
        subs = {}
        for key in dir(update_request):
            if key.startswith('new'):
                tag = self._first_lower(key[3:])
                if tag in dir(self):
                    subs[tag] = key
        return subs

    def create(self):
        """
        Add this object to CUCM.
        """
        if self.__attached__:
            raise exceptions.CreationException('this object is already attached')
        operation = self._axl_operation(PF_ADD, self.__name__, self.__client__)
        x_type = getattr(self.__client__.factory, 'X%s' % self.__name__)()
        tags = dir(x_type)
        unwrapped = {key: value for (key, value) in self.__dict__.items() if key in tags}
        x_type = self._get_xtype(**unwrapped)
        result = operation(x_type)
        self.uuid = result['return']
        self.__attached__ = True
        self.__update_request__ = self._get_update_request(uuid=self.uuid)
        log.info('new %s was created, uuid=%s' % (self.__name__, self.uuid,))
        return self.uuid

    def update(self):
        """
        Update the CUCM object with all changes made to this object.
        """
        if not self.__attached__:
            raise exceptions.UpdateException('you must create an object with "create" before update')
        self.__update_request__.uuid = self.uuid
        operation = self._axl_operation(PF_UPDATE, self.__name__, self.__client__)
        operation(**self.__update_request__.__dict__['__values__'])
        self.__update_request__ = self._get_update_request(uuid=self.uuid)
        log.info('%s was updated, uuid=%s' % (self.__name__, self.uuid,))

    def remove(self):
        """
        Delete this object from CUCM.
        """
        if not self.__attached__:
            msg = 'This object is not attached and can not removed from CUCM'
            raise exceptions.RemoveException(msg)
        operation = self._axl_operation(PF_REMOVE, self.__name__, self.__client__)
        operation(uuid=self.uuid)
        self.uuid = None
        self.__attached__ = False
        self.__update_request__ = self._get_update_request()
        log.info('%s was removed, uuid=%s' % (self.__name__, self.uuid,))

    def reload(self):
        """
        Reload this object from CUCM.
        """
        if not self.__attached__:
            msg = 'This object is not attached and can not be reloaded from CUCM'
            raise exceptions.ReloadException(msg)
        self._load(uuid=self.uuid)
        self.__update_request__ = self._get_update_request(uuid=self.uuid)

    def reset(self):
        """
        Reset this object.
        """
        if not self.__attached__:
            msg = 'This object is not attached and can not be reset.'
            raise exceptions.ResetException(msg)
        operation = self._axl_operation(PF_RESET, self.__name__, self.__client__)
        try:
            operation(uuid=self.uuid)
        except:
            print("Unable to reset object.")

    def clone(self):
        """
        Return a clone of this object.

        After cloning, the new object will be detached.
        This means the cloned object can be directly added to CUCM with the create function.
        """
        obj = self.__class__()
        obj.__dict__.update(self.__dict__)
        obj.uuid = None
        obj.__attached__ = False
        log.debug('%s was cloned' % self.__name__)
        return obj

    @classmethod
    def list(cls, criteria, returns, skip=None, first=None, configname='default'):
        """

        :param criteria: Dictionary of search criteria.
        :param returns: List of the desired returned tags.
        :param skip: The number of results to skip, starting at the first.
        :param first: The maximum number of results to return, starting at the first.
        :param configname: Name of the configuration. Default value is 'default'
        :yeild: Returns the matching search results.
        """
        client = AXLClient.get_client(configname)
        operation = cls._axl_operation(PF_LIST, cls.__name__, client)
        tags = dict([(i, '') for i in returns])
        log.debug('fetch list of %ss, search criteria=%s' % (cls.__name__, str(criteria)))
        args = criteria, tags
        if skip is not None or first is not None:
            if skip is None:
                skip = 0
            if first is None:
                args = criteria, tags, skip
            else:
                args = criteria, tags, skip, first
        return cls._prepare_result(operation(*args), returns)

    @classmethod
    def list_obj(cls, criteria, skip=None, first=None, configname='default'):
        """
        Return all objects that match the given search criteria.

        The return value is generator. Each next() call will fetch a new instance and return it as an object.
        """
        for obj in cls.list(criteria, 'uuid', skip, first, configname):
            yield cls(uuid=obj['uuid'])


class BaseXType(object):

    def __new__(cls, *args, **kwargs):
        client = AXLClient.get_client()
        return getattr(client.factory, cls.__name__)(*args, **kwargs)


class BaseXTypeListItem(dict):
    """ A special XType that can be used to fill into a list.
    """
    def __init__(self, *args, **kwargs):
        name = self.__class__.__name__
        xtype = type(name, (BaseXType, self.__class__), dict())(*args, **kwargs)
        self[name[1:]] = xtype
