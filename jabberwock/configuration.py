from zeep.settings import Settings


class AXLClientSettings(object):

    def __init__(self, host, username, password, version,
                 schema_path=None, zeep_settings=None, proxy=None,
                 transport_debugger=False):
        if proxy is None:
            proxy = dict()
        if zeep_settings is None:
            zeep_settings = {'strict': False, 'xml_huge_tree': True}
        self.host = host
        self.username = username
        self.password = password
        self.schema_path = schema_path
        self.zeep_settings = Settings(**zeep_settings)
        self.proxy = proxy
        self.transport_debugger = transport_debugger
        self.version = version


class ConfigurationRegistry(object):

    configurations = dict()

    def register(self, configuration, name='default'):
        self.configurations[name] = configuration

    def get(self, name='default'):
        return self.configurations[name]


registry = ConfigurationRegistry()
