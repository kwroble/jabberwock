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
import os


class AXLClient(Client):
    """
    The AXLClient class sets up the connection to the call manager with methods for configuring UCM
    Tested with environment of Python 3 and zeep.
    """

    clients = dict()

    def __init__(self, config_name='default'):
        """
        Args:
            config_name: the name of the config file
        """
        BINDING_NAME = "{http://www.cisco.com/AXLAPIService/}AXLAPIBinding"
        os_path = 'C:/git/jabberwocky/jabberwocky'  # os.getcwd() #FIX THIS TO NOT HAVE TO USE STATIC PATH
        # os_path = (os_path.replace('\\', '/'))
        config = configparser.ConfigParser()
        config.read('{os_path}/config/{config_name}.ini'.format(os_path=os_path, config_name=config_name))
        username = config['authentication']['username']
        password = config['authentication']['password']
        server = config['authentication']['server']
        version = config['authentication']['version']
        disable_warnings(InsecureRequestWarning)
        settings = Settings(strict=False)
        wsdl = 'file://' + os_path + '/axlsqltoolkit/schema/' + version + '/AXLAPI.wsdl'
        address = "https://{server}:8443/axl/".format(server=server)
        session = Session()
        session.verify = False
        session.auth = HTTPBasicAuth(username, password)
        transport = Transport(cache=SqliteCache(), session=session, timeout=20)
        kwargs = dict(transport=transport, plugins=[HistoryPlugin()], settings=settings)

        super().__init__(wsdl, **kwargs)
        self.axl = self.create_service(BINDING_NAME, address)
        self.factory = self.type_factory('ns0')

    @classmethod
    def get_client(cls, config_name='default', recreate=False):
        """ return a single instance of client for each configuration.
        """
        client = None
        if config_name not in cls.clients or recreate:
            client = AXLClient(config_name)
        return cls.clients.setdefault(config_name, client)
