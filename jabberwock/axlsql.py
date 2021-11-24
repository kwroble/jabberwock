import logging
from jabberwock import utils
from jabberwock.axlhandler import AXLClient

log = logging.getLogger('jabberwock')


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
        sql = ('SELECT d.name, d.pkid, n.dnorpattern AS dn FROM device AS d, '
               'numplan AS n, '
               'devicenumplanmap AS dnpm '
               'WHERE dnpm.fkdevice = d.pkid AND dnpm.fknumplan = n.pkid AND dnpm.fknumplan="%(fknumplan)s"')
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
        sql = ('UPDATE remotedestinationdynamic SET enablesinglenumberreach = "%(value)s" '
               'WHERE fkremotedestination = "%(fkremotedestination)s"')
        self._exec_update(sql % dict(fkremotedestination=utils.uuid(fkremotedestination), value=self._tobool(value)))

    def get_single_number_reach(self, fkremotedestination):
        sql = ('SELECT enablesinglenumberreach FROM remotedestinationdynamic '
               'WHERE fkremotedestination = "%(fkremotedestination)s"')
        return self._gen_result(self._exec(sql % dict(fkremotedestination=utils.uuid(fkremotedestination))))

    def get_assigned_dn_list(self):
        sql = ("SELECT dnorpattern AS dn, MIN(r.name) AS name FROM numplan n, routepartition r "
               "WHERE r.pkid = n.fkroutepartition AND n.pkid IN (SELECT fknumplan FROM devicenumplanmap "
               "WHERE fkdevice IN (SELECT pkid FROM device)) GROUP BY dn ORDER BY dn")
        return self._gen_result_list(self._exec(sql))

    def get_inactive_dn_list(self):
        sql = ("SELECT n.pkid FROM numplan n LEFT OUTER JOIN devicenumplanmap m ON m.fkdevice = n.pkid "
               "WHERE m.fkdevice IS NULL AND n.tkpatternusage = '2' AND n.iscallable = 'f'")
        return self._gen_result_list(self._exec(sql))

    def get_users_with_self_service_id(self, self_service_id):
        sql = 'SELECT userid FROM enduser WHERE keypadenteredalternateidentifier LIKE "%(self_service_id)s"'
        return self._gen_result_list(self._exec(sql % dict(self_service_id='%' + self_service_id + '%')))

    def get_device_num_plan_map(self):
        sql = ("SELECT * FROM devicenumplanmap dnpm "
               "WHERE dnpm.fknumplan IN (SELECT n.pkid "
               "FROM numplan AS n INNER JOIN routepartition AS rp ON n.fkroutepartition=rp.pkid "
               "WHERE rp.name IN "
               "('SG-AA-Internal', 'SG-DA-Internal', 'SG-DT-Internal', 'SG-PH-Internal', 'SG-SH-Internal'))")
        return self._gen_result_list(self._exec(sql))