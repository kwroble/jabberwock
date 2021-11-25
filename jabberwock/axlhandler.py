from zeep import Client
from zeep.transports import Transport
from zeep.plugins import HistoryPlugin
from requests import Session
from requests.auth import HTTPBasicAuth
from urllib3 import disable_warnings
from urllib3.exceptions import InsecureRequestWarning
from zeep.cache import SqliteCache
from zeep.settings import Settings
import configparser


class AXLClient(Client):
    """
    The AXLClient class sets up the connection to the call manager with methods for configuring UCM
    Tested with environment of Python 3 and zeep.
    """

    clients = dict()
    BINDING_NAME = "{http://www.cisco.com/AXLAPIService/}AXLAPIBinding"

    def __init__(self, config_name='default', toolkit_path='/axlsqltoolkit', **kwargs):
        """
        Args:
            config_name: the name of the config file
        """
        self.config = configparser.ConfigParser()
        self.config.read('{toolkit_path}/config/{config_name}.ini'.format(toolkit_path=toolkit_path,
                                                                          config_name=config_name))
        username = self.config['authentication']['username']
        password = self.config['authentication']['password']
        version = self.config['authentication']['version']
        disable_warnings(InsecureRequestWarning)
        settings = Settings(strict=False, xml_huge_tree=True)
        wsdl = 'file://' + toolkit_path + '/schema/' + version + '/AXLAPI.wsdl'
        session = Session()
        session.verify = False
        session.auth = HTTPBasicAuth(username, password)
        transport = Transport(cache=SqliteCache(), session=session, timeout=20)
        defaults = dict(wsdl=wsdl, transport=transport, plugins=[HistoryPlugin()], settings=settings)
        merged_kwargs = {**defaults, **kwargs}
        super().__init__(**merged_kwargs)

    @property
    def axl(self):
        server = self.config['authentication']['server']
        address = "https://{server}:8443/axl/".format(server=server)
        return self.create_service(self.BINDING_NAME, address)

    @property
    def factory(self):
        return self.type_factory('ns0')

    @classmethod
    def get_client(cls, config_name='default', toolkit_path='/axlsqltoolkit', recreate=False):
        """ return a single instance of client for each configuration.
        """
        client = None
        if config_name not in cls.clients or recreate:
            client = AXLClient(config_name, toolkit_path)
        return cls.clients.setdefault(config_name, client)


def main():
    return


if __name__ == "__main__":
    main()
