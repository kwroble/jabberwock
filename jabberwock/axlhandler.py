from zeep import Client
from zeep.transports import Transport
from zeep.plugins import HistoryPlugin
from requests import Session
from requests.auth import HTTPBasicAuth
from urllib3 import disable_warnings
from urllib3.exceptions import InsecureRequestWarning
from zeep.cache import SqliteCache
import jabberwock


class AXLClient(Client):
    """
    The AXLClient class sets up the connection to the call manager with methods for configuring UCM
    Tested with environment of Python 3 and zeep.
    """

    clients = dict()
    BINDING_NAME = "{http://www.cisco.com/AXLAPIService/}AXLAPIBinding"

    def __init__(self, config_name='default', **kwargs):
        """
        Args:
            config_name: the name of the config file
        """
        self.config = jabberwock.configuration.registry.get(config_name)
        disable_warnings(InsecureRequestWarning)
        wsdl = 'file://' + self.config.schema_path + '/' + self.config.version + '/AXLAPI.wsdl'
        session = Session()
        session.verify = False
        session.auth = HTTPBasicAuth(self.config.username, self.config.password)
        transport = Transport(cache=SqliteCache(), session=session, timeout=60)
        defaults = dict(wsdl=wsdl, transport=transport, plugins=[HistoryPlugin()], settings=self.config.zeep_settings)
        merged_kwargs = {**defaults, **kwargs}
        super().__init__(**merged_kwargs)

    @property
    def axl(self):
        address = "https://{host}:8443/axl/".format(host=self.config.host)
        return self.create_service(self.BINDING_NAME, address)

    @property
    def factory(self):
        return self.type_factory('ns0')

    @classmethod
    def get_client(cls, config_name='default', recreate=False):
        """ return a single instance of client for each configuration.
        """
        client = None
        if config_name not in cls.clients or recreate:
            client = AXLClient(config_name)
        return cls.clients.setdefault(config_name, client)


def main():
    return


if __name__ == "__main__":
    main()
