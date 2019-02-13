import logging
from boltons.iterutils import remap
from collections import namedtuple
from zeep.xsd.valueobjects import CompoundValue
from jabberwocky.axlhandler import AXLClient
from jabberwocky import exceptions


PF_LIST = 'list'
PF_GET = 'get'
PF_UPDATE = 'update'
PF_ADD = 'add'
PF_REMOVE = 'remove'
XSD_NS = 'ns0'

log = logging.getLogger('jabberwocky')


class BaseCCModel(object):
    """ Provide base functionality for Abstract
        or XTypes Objects.
    """

    __name__ = ''
    __configname__ = ''
    __config__ = None
    __client__ = None
    __attached__ = False
    __updateable__ = list()

    def __init__(self, *args, **kwargs):
        """
        Create a new CUCM object.
        """
        configname = kwargs.pop('configname', 'default')
        self._configure(configname)
        self._initialize(*args, **kwargs)

    def __setattr__(self, name, value):
        """
        Set the value of an attribute.

        Keeps track of the name of the attribute that is changed. Generally used for the update method.
        """
        builtin = name.startswith('__') and name.endswith('__')
        if not builtin:
            self.__updateable__.append(name)
        super().__setattr__(name, value)

    @classmethod
    def _axl_method(cls, prefix, name, client):
        """ return a function to call the callmanager.
        """
        return getattr(client.axl, '%s%s' % (prefix, name,))

    @classmethod
    def _prepare_result(cls, result, returns):
        """
        Unwrap a SOAP object as a named tuple and return a generator.
        """
        first_lower = lambda s: s[:1].lower() + s[1:] if s else ''
        unwrapped = result['return']
        if isinstance(unwrapped, str):
            return
        unwrapped = getattr(unwrapped, first_lower(cls.__name__))
        named_tuple = namedtuple('named_tuple', returns)
        for obj in unwrapped:
            yield named_tuple(*[getattr(obj, r) for r in returns])

    def _initialize(self, *args, **kwargs):
        """
        
        a part of init method. If some search criteria was found it
            will automatically load this object.
        """
        if not args and not kwargs:
            self._create_empty()
            return
        self._load(*args, **kwargs)
        self.__updateable__ = list()

    def _load(self, *args, **kwargs):
        """
        Get the specified object from Call Manager and merge its attributes with this CUCM object.
        """
        first_lower = lambda s: s[:1].lower() + s[1:] if s else ''
        method = self._axl_method(PF_GET, self.__name__, self.__client__)
        result = method(*args, **kwargs)
        result = getattr(getattr(result, 'return'), first_lower(self.__name__))
        self._loadattr(result)
        self.__attached__ = True

    @classmethod
    def _strip_empty_tags(cls, obj):
        """
        Recursively strip all empty values or values equal to -1 from an object.

        CUCM can't handle attributes that are empty. This will recursively create a copy of object and remove
        all empty tags.
        """
        def visit(path, key, value):
            if value == '' or value is None or value == -1:
                return False
            elif isinstance(value, CompoundValue):
                for i in dir(value):
                    if not getattr(value, i) or getattr(value, i) == -1:
                        return False
            return key, value
        return remap(obj, visit=visit)

    def _set_name(self):
        """
        Set __name__ variable to the name of the class.
        """
        if self.__name__ is '':
            self.__name__ = self.__class__.__name__

    def _configure(self, configname):
        """

        """
        self.__client__ = AXLClient.get_client(configname)
        self.__configname__ = configname
        self._set_name()

    def _create_empty(self):
        """
        Create an empty CUCM object.
        """
        obj = getattr(self.__client__.factory, 'X%s' % self.__name__)()
        self._loadattr(obj)

    def _loadattr(self, obj):
        """
        Merge an AXL object with this object.

        first: update object attributes with suds attributes.
        second: copy all attributes of class instance to object.

        The result will be a object that has all attributes as those in XSD.
        """

        for k, v in obj.__dict__['__values__'].items():
            self.__setattr__(k, v)


class AbstractCCMModel(BaseCCModel):
    """ Base class for all CiscoCallmanager objects.
        This will make the bridge between zeep and CCM
        objects. In addition all standard method are implement here.
    """
    def create(self):
        """
        Add this object to CUCM.
        """
        if self.__attached__:
            raise exceptions.CreationException('this object is already attached')
        method = self._axl_method(PF_ADD, self.__name__, self.__client__)
        x_type = getattr(self.__client__.factory, 'X%s' % self.__name__)()
        tags = dir(x_type)
        unwrapped = dict()
        for key in tags:
            unwrapped[key] = getattr(self, key)
        unwrapped = self._strip_empty_tags(unwrapped)
        result = method(unwrapped)
        self.uuid = result['return']
        self.__attached__ = True
        self.__updateable__ = list()
        log.info('new %s was created, uuid=%s' % (self.__name__, self.uuid,))
        return self.uuid

    def update(self):
        """
        Update the CUCM object with all changes made to this object.
        """
        first_lower = lambda s: s[:1].lower() + s[1:] if s else ''
        if not self.__attached__:
            raise exceptions.UpdateException('you must create an object with "create" before update')
        method = self._axl_method(PF_UPDATE, self.__name__, self.__client__)
        req_type = getattr(self.__client__.factory, '%s%sReq' % (PF_UPDATE.capitalize(), self.__name__))()
        tags = dir(req_type)
        unwrapped = dict([(i, getattr(self, i),) for i in self.__updateable__ if i in tags])
        unwrapped.update(dict(uuid=self.uuid))
        for key in dir(req_type):
            if key.startswith('new') and first_lower(key[3:]) in self.__updateable__:
                unwrapped[key] = unwrapped[first_lower(key[3:])]
                del unwrapped[first_lower(key[3:])]
        method(**unwrapped)
        self.__updateable__ = list()
        log.info('%s was updated, uuid=%s' % (self.__name__, self.uuid,))

    def remove(self):
        """
        Delete this object from CUCM.
        """
        if not self.__attached__:
            msg = 'This object is not attached and can not removed from CUCM'
            raise exceptions.RemoveException(msg)
        method = self._axl_method(PF_REMOVE, self.__name__, self.__client__)
        method(uuid=self.uuid)
        self.uuid = None
        self.__attached__ = False
        self.__updateable__ = list()
        log.info('%s was removed, uuid=%s' % (self.__name__, self.uuid,))

    def reload(self, force=False):
        """
        Reload this object from CUCM.
        """
        if not self.__attached__:
            msg = 'This object is not attached and can not reloaded from CUCM'
            raise exceptions.ReloadException(msg)
        if not force and len(self.__updateable__):
            msg = 'This object failed to reload because there are changes pending update. ' \
                  'Update the object or run reload(force=True).'
            raise exceptions.ReloadException(msg)
        self._load(uuid=self.uuid)
        self.__updateable__ = list()

    def clone(self):
        """
        Return a clone of this object.

        After cloning, the new object will be detached.
        This means the cloned object can be directly added to CUCM with the create method.
        """
        obj = self.__class__()
        obj.__dict__.update(self.__dict__)
        obj.uuid = None
        obj.__attached__ = False
        log.debug('%s was cloned' % self.__name__)
        return obj

    @classmethod
    def list(cls, criteria, returns, skip=None, first=None, configname='default'):
        """ find all object with the given search criteria. It also
            required a list with return values. The return value is a
            generator and the next call will return a tuple with the returnsValues.
        """
        client = AXLClient.get_client(configname)
        method = cls._axl_method(PF_LIST, cls.__name__, client)
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
        return cls._prepare_result(method(*args), returns)

    @classmethod
    def list_obj(cls, criteria, skip=None, first=None, configname='default'):
        """
        Return all objects that match the given search criteria.

        The return value is generator. Each next() call will fetch a new instance and return it as an object.
        """
        for uuid, in cls.list(criteria, ('uuid',), skip, first, configname):
            yield cls(uuid=uuid)


class AbstractXType(object):

    def __new__(cls, *args, **kwargs):
        client = AXLClient.get_client()
        return getattr(client.factory, cls.__name__)(*args, **kwargs)

class AbstractXTypeListItem(dict):
    """ A special XType that can be used to fill into a list.
    """
    def __init__(self, *args, **kwargs):
        name = self.__class__.__name__
        xtype = type(name, (AbstractXType, self.__class__), dict())(*args, **kwargs)
        self[name[1:]] = xtype
