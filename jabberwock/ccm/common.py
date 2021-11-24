from jabberwock.ccm.abstracts import BaseCUCMModel
from jabberwock.ccm.mixings import MixingAbstractLines
from jabberwock.ccm.mixings import MixingAbstractTemplate
from jabberwock.axlsql import AXLSQLUtils
from jabberwock import exceptions
from jabberwock import utils


class DeviceProfile(BaseCUCMModel,
                    MixingAbstractTemplate,
                    MixingAbstractLines):
    pass
    
    
class User(BaseCUCMModel, MixingAbstractTemplate):

    def add_associated_devices(self, phones):
        if not self.associatedDevices:
            self.set_associated_devices(phones)
            return
        if not isinstance(phones, list):
            phones = [phones]
        if not isinstance(phones[0], str):
            phones = [i.name for i in phones]
        union = list(set(phones) | set(self.associatedDevices['device']))
        self.associatedDevices = dict(device=union) if union else ''

    def set_associated_devices(self, phones):
        if not isinstance(phones, list):
            phones = [phones]
        if not isinstance(phones[0], str):
            phones = [i.name for i in phones]
        self.associatedDevices = dict(device=phones) if phones else ''

    def set_cti_controlled_device_profiles(self, device_profiles):
        if not isinstance(device_profiles, list):
            device_profiles = [device_profiles]
        self.ctiControlledDeviceProfiles = dict(profileName=[dict(uuid=i.uuid) for i in device_profiles]) \
            if device_profiles else ''

    def set_phone_profiles(self, device_profiles):
        if not isinstance(device_profiles, list):
            device_profiles = [device_profiles]
        self.phoneProfiles = dict(profileName=[dict(uuid=i.uuid) for i in device_profiles]) if device_profiles else ''

    def get_mobility_association(self):
        """
        Return phones that are associated with this user.
        """
        sql_utils = AXLSQLUtils(self.__config_name__)
        if not self.__attached__:
            raise exceptions.NotAttachedException('User is not attached')
        for i in sql_utils.user_phone_association(self.uuid):
            yield Phone(uuid=i['fkdevice'])

    def get_cups_cupc(self):
        cups, cupc, pkid = self._get_cups_cupc()
        return cups, cupc

    def set_cups_cupc(self, cups, cupc):
        sqlutils = AXLSQLUtils(self.__config_name__)
        if cupc and not cups:
            raise exceptions.PyAXLException('If cupc is true, cups must also be true')
        rcups, rcupc, pkid = self._get_cups_cupc()
        if rcups is None and cups:
            sqlutils.insert_cups(self._uuid, cupc)
        elif rcups and not cups:
            sqlutils.remove_cups(self._uuid)
        elif rcups and cups:
            sqlutils.update_cups(self._uuid, cupc)

    def _get_cups_cupc(self):
        sql_utils = AXLSQLUtils(self.__config_name__)
        if not self.__attached__:
            raise exceptions.NotAttachedException('User is not attached')
        re = sql_utils.has_cups_cupc(self.uuid)
        if re is None:
            return None, None, None
        return re['enablecups'] == 't', re['enablecupc'] == 't', re['pkid']


class UserGroup(BaseCUCMModel):
    pass


class Line(BaseCUCMModel):
    def __init__(self, **kwargs):
        kwargs.setdefault('usage', 'Device')
        super().__init__(**kwargs)

    def get_primary_users(self):
        """ Return users that have this line set as a primary extension."""
        sql_utils = AXLSQLUtils(self.__config_name__)
        if not self.__attached__:
            raise exceptions.NotAttachedException('Line is not attached')
        for i in sql_utils.number_user_association(self.uuid):
            yield User(uuid=i['fkenduser'])

    def get_associated_devices(self):
        """ Return devices that are associated to this directory number."""
        sql_utils = AXLSQLUtils(self.__config_name__)
        if not self.__attached__:
            raise exceptions.NotAttachedException('Line is not attached')
        for i in sql_utils.number_user_association(self.uuid):
            yield User(uuid=i['fkenduser'])


class TransPattern(BaseCUCMModel):
    pass

    
class Phone(BaseCUCMModel,
            MixingAbstractTemplate,
            MixingAbstractLines):

    def get_vendor_config(self):
        return utils.elements_to_dict(self.vendorConfig['_value_1'])

    def set_vendor_config(self, **kwargs):
        self.vendorConfig = dict(_value_1=utils.dict_to_elements(kwargs))
            
    def logout(self):
        if not self.__attached__:
            raise exceptions.LogoutException('Phone is not attached')
        self.__client__.service.doDeviceLogout(dict(_uuid=self._uuid))

    def login(self, user, deviceProfile, duration=1):
        if not self.__attached__:
            raise exceptions.LogoutException('Phone is not attached')
        self.__client__.service.doDeviceLogin(dict(_uuid=self._uuid),
                                              duration,
                                              dict(_uuid=deviceProfile._uuid),
                                              user.userid)

            
class AppUser(BaseCUCMModel):
    pass


class CallPickupGroup(BaseCUCMModel):
    pass


class Css(BaseCUCMModel):
    pass


class CtiRoutingPoint(BaseCUCMModel):
    pass  

    
class DevicePool(BaseCUCMModel):
    pass


class Gateway(BaseCUCMModel):
    pass


class GatewayEndpointAnalogAccess(BaseCUCMModel):
    pass


class HuntList(BaseCUCMModel):
    pass


class HuntPilot(BaseCUCMModel):
    pass


class LineGroup(BaseCUCMModel):
    pass


class PhoneButtonTemplate(BaseCUCMModel):
    pass


class RoutePartition(BaseCUCMModel):
    pass


class RouteList(BaseCUCMModel):
    pass


class VoiceMailPilot(BaseCUCMModel):
    pass


class VoiceMailProfile(BaseCUCMModel):
    pass


class RemoteDestination(BaseCUCMModel):

    def set_single_number_reach(self, value):
        """ Set single number reach flag is not possible in version 10.5
            see ticket: https://supportforums.cisco.com/discussion/12438721/single-number-reach-axl
            The workaround is again to set some value with SQL! Yupiiiii!
        """
        if not self.__attached__:
            raise exceptions.NotAttachedException('User is not attached')
        sqlutils = AXLSQLUtils(self.__config_name__)
        sqlutils.set_single_number_reach(self._uuid, value)

    def get_single_number_reach(self):
        if not self.__attached__:
            raise exceptions.NotAttachedException('User is not attached')
        sqlutils = AXLSQLUtils(self.__config_name__)
        value = sqlutils.get_single_number_reach(self._uuid)
        return value['enablesinglenumberreach'] == 't'


class RemoteDestinationProfile(BaseCUCMModel,
                               MixingAbstractLines,
                               MixingAbstractTemplate):
    @classmethod
    def template(cls, *args, **kwargs):
        return super().template(*args, typeclass='Remote Destination Profile', **kwargs)


class TodAccess(BaseCUCMModel):
    pass


class TimeSchedule(BaseCUCMModel):

    def removeMembers(self, members):
        if not isinstance(members, list):
            members = [members]
        removeMembers = [dict(member=dict(timePeriodName=dict(_uuid=uuid))) for uuid in members]
        self.__client__.service.updateTimeSchedule(removeMembers=removeMembers, uuid=self._uuid)

    def addMembers(self, members):
        if not isinstance(members, list):
            members = [members]
        addMembers = [dict(member=dict(timePeriodName=dict(_uuid=uuid))) for uuid in members]
        self.__client__.service.updateTimeSchedule(addMembers=addMembers, uuid=self._uuid)


class TimePeriod(BaseCUCMModel):
    pass


def main():
    return


if __name__ == "__main__":
    main()
