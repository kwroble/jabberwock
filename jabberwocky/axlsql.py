import logging
from jabberwocky import utils
from jabberwocky.axlhandler import AXLClient

log = logging.getLogger('jabberwocky')


class AXLSQL(object):

    def __init__(self, configname):
        self.client = AXLClient.get_client(configname)

    def _exec(self, sql):
        log.info('Execute SqlQuery "%s"' % sql)
        return self.client.axl.executeSQLQuery(sql)

    def _exec_update(self, sql):
        log.info('Execute SqlUpdate "%s"' % sql)
        return self.client.axl.executeSQLUpdate(sql)

    def _gen_result(self, dom_or_part, ispart=False):
        if not ispart:
            if 'row' not in dom_or_part['return']:
                return None
            li = dom_or_part['return']['row']
            if len(li) < 1:
                return None
            if len(li) > 1:
                raise ValueError('too many results.')
            dom_or_part = li[0]
        return {x.tag: x.text for x in dom_or_part}

    def _gen_result_list(self, dom):
        if not dom['return']:
            return None
        if 'row' not in dom['return']:
            return
        for part in dom['return']['row']:
            yield self._gen_result(part, True)

    def _to_bool(self, value):
        return 't' if bool(value) else 'f'


class AXLSQLUtils(AXLSQL):

    def user_phone_association(self, fkenduser):
        sql = 'SELECT * FROM enduserdevicemap WHERE fkenduser="%(fkenduser)s"'
        return self._gen_result_list(self._exec(sql % dict(fkenduser=utils.uuid(fkenduser))))

    def number_user_association(self, fknumplan):
        sql = 'SELECT * FROM endusernumplanmap WHERE fknumplan="%(fknumplan)s"'
        return self._gen_result_list(self._exec(sql % dict(fknumplan=utils.uuid(fknumplan))))

    def number_device_association(self, fknumplan):
        sql = 'select d.name, d.pkid, n.dnorpattern as DN from device as d, numplan as n, devicenumplanmap as dnpm where dnpm.fkdevice = d.pkid and dnpm.fknumplan = n.pkid and dnpm.fknumplan="%(fknumplan)s"'
        return self._gen_result_list(self._exec(sql % dict(fknumplan=utils.uuid(fknumplan))))

    def has_cups_cupc(self, fkenduser):
        sql = 'SELECT * FROM enduserlicense WHERE fkenduser="%(fkenduser)s"'
        return self._gen_result(self._exec(sql % dict(fkenduser=utils.uuid(fkenduser))))

    def insert_cups(self, fkenduser, cupc):
        sql = 'INSERT INTO enduserlicense (fkenduser, enablecups, enablecupc) VALUES ("%(fkenduser)s", "t", "%(cupc)s")'
        self._exec_update(sql % dict(fkenduser=utils.uuid(fkenduser), cupc=self._tobool(cupc)))

    def remove_cups(self, fkenduser):
        sql = 'DELETE FROM enduserlicense WHERE fkenduser = "%(fkenduser)s"'
        self._exec_update(sql % dict(fkenduser=utils.uuid(fkenduser)))

    def update_cups(self, fkenduser, cupc):
        sql = 'UPDATE enduserlicense SET enablecupc = "%(cupc)s" WHERE fkenduser = "%(fkenduser)s"'
        self._exec_update(sql % dict(fkenduser=utils.uuid(fkenduser), cupc=self._tobool(cupc)))

    def update_bfcp(self, fkenduser, bfcp):
        sql = 'UPDATE device SET enablebfcp = "%(bfcp)s" WHERE pkid = "%(fkenduser)s"'
        self._exec_update(sql % dict(fkenduser=utils.uuid(fkenduser), bfcp=self._tobool(bfcp)))

    def set_single_number_reach(self, fkremotedestination, value):
        sql = 'UPDATE remotedestinationdynamic SET enablesinglenumberreach = "%(value)s" WHERE fkremotedestination = "%(fkremotedestination)s"'
        self._exec_update(sql % dict(fkremotedestination=utils.uuid(fkremotedestination), value=self._tobool(value)))

    def get_single_number_reach(self, fkremotedestination):
        sql = 'SELECT enablesinglenumberreach FROM remotedestinationdynamic WHERE fkremotedestination = "%(fkremotedestination)s"'
        return self._gen_result(self._exec(sql % dict(fkremotedestination=utils.uuid(fkremotedestination))))

    def get_assigned_dn_list(self):
        sql = "select dnorpattern as dn, MIN(r.name) as name from numplan n, routepartition r where r.pkid = n.fkroutepartition AND n.pkid IN(select fknumplan from devicenumplanmap where fkdevice IN (select pkid from device)) GROUP BY dn ORDER BY DN"
        return self._gen_result_list(self._exec(sql))

    def get_inactive_dn_list(self):
        sql = "select n.pkid from numplan n left outer join devicenumplanmap m on m.fkdevice = n.pkid where m.fkdevice is null and n.tkpatternusage = '2' and n.iscallable = 'f'"
        return self._gen_result_list(self._exec(sql))

    def get_users_with_self_service_id(self, self_service_id):
        sql = 'SELECT userid FROM enduser WHERE keypadenteredalternateidentifier like "%(self_service_id)s"'
        return self._gen_result_list(self._exec(sql % dict(self_service_id='%' + self_service_id + '%')))

    def get_device_num_plan_map(self):
        sql = "select * from devicenumplanmap dnpm WHERE dnpm.fknumplan IN (select n.pkid from numplan as n inner join routepartition as rp on n.fkroutepartition=rp.pkid where rp.name IN ('SG-AA-Internal', 'SG-DA-Internal', 'SG-DT-Internal', 'SG-PH-Internal', 'SG-SH-Internal'))"
        return self._gen_result_list(self._exec(sql))