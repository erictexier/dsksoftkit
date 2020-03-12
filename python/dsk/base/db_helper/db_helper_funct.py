import sys
if sys.version_info[0] >= 3:
    from six import string_types as basestring

from dsk.base.db_helper.shotgun_script import connect_to_shotgun

from dsk.base.db_helper.show_info_db import ShowInfoDb
from dsk.base.db_helper.shot_info_db import ShotInfoDb
from dsk.base.db_helper.asset_info_db import AssetInfoDb
from dsk.base.db_helper.dept_info_db import DeptInfoDb
from dsk.base.db_helper.step_info_db import StepInfoDb
from dsk.base.db_helper.version_info_db import VersionInfoDb
from dsk.base.db_helper.scrroom_info_db import ScreenRoomInfoDb
from dsk.base.db_helper.pft_info_db import PftInfoDb
from dsk.base.db_helper.pf_info_db import PfInfoDb
from dsk.base.db_helper.user_info_db import UserInfoDb
from dsk.base.db_helper.task_info_db import TaskInfoDb
from dsk.base.db_helper.pipeconfig_info_db import PipeConfigInfoDb
from dsk.base.db_helper.settings_info_db import SettingsInfoDb

CurrentProjects = set(["xxxx", "yyyy", "zzzz", "tttt"])
IgnoreProject = set(["site",
                     ])


def show_default(show_name, idi, show_label):
    """Build a ShowInfoDb
    """
    s = ShowInfoDb()
    s.setName(show_name)
    if s.setdata(idi,show_label):
        return s
    return None


def shot_default(code, idi=-1, cut_order=-1, assets=None, status='wtg'):
    """ build a Shot id
    """
    s = ShotInfoDb()
    if s.setdata(code, idi, cut_order, assets=assets):
        return s
    return None


def asset_default(code, idi, asset_type, status):
    s = AssetInfoDb()
    s.setName(code)
    if s.setdata(idi, asset_type, status):
        return s
    return None


def dept_default(code, idi, dept_type, label):
    s = DeptInfoDb()
    s.setName(code)
    if s.setdata(idi, dept_type, label):
        return s
    return None

def step_default(code, idi, arg):
    s = StepInfoDb()
    s.setName("%s" % code)
    if s.setdata(arg):
        return s
    return None


def version_default(data):
    n = data.get('code', None)
    if n:
        v = VersionInfoDb()
        v.setdata_shotgun(data)
        return v
    return None


def screenroom_default(data):
    n = data.get('code', None)
    if n:
        v = ScreenRoomInfoDb()
        v.setdata_shotgun(data)
        return v
    return None


def pft_default(data):
    pft = PftInfoDb()
    if pft.setdata(data):
        return pft
    return None


def pf_default(data):
    pft = PfInfoDb()
    if pft.setdata(data):
        return pft
    return None


def settings_default(data):
    settings = SettingsInfoDb()
    if settings.setdata(data):
        return settings
    return None


def user_default(data):
    user = UserInfoDb()
    if user.setdata(data):
        return user
    return None


def task_default(data):
    task = TaskInfoDb()
    if task.setdata(data):
        return task
    return None


def pipeconfig_default(data):
    pc = PipeConfigInfoDb()
    if pc.setdata(data):
        return pc
    return None


# raw query
class ShotgunQuery(object):
    _settings = {"project_settings":"CustomEntity24"}

    @classmethod
    def get_current_projects(cls, conn = None, tank_names = None, call_default = show_default):
        """ return all the current project, tank_names can be a list of show
        """
        result = list()
        if conn == None:
            conn = connect_to_shotgun()

        prj = cls.project_list(conn, tank_names)

        for k in prj:
            if k['tank_name'] in CurrentProjects:
                result.append(call_default(k['tank_name'],k['id'],k['name']))
            elif k['name'] != None and not k['tank_name'] in IgnoreProject and not 'emplate' in k['name']:
                if k['tank_name'] != None:
                    result.append(call_default(k['tank_name'],k['id'],k['name']))
        return result

    @staticmethod
    def shot_list_with_id(show_id, conn = None, call_default = shot_default):
        """ return a list of shot for a given show
        """
        if conn == None:
            conn = connect_to_shotgun()
        bad_statuses = ['omt']
        res = conn.find('Shot',
                        [['project','is', {'type':'Project', 'id':show_id}],
                         ['sg_status_list', 'not_in', bad_statuses]],
                        ['code', 'sg_cut_order', 'assets', 'sg_status_list'])

        return [call_default(x['code'],
                             x['id'],
                             x['sg_cut_order'],
                             x['assets'],x['sg_status_list']) for x in res]

    @staticmethod
    def asset_list_with_id(show_id, conn=None, call_default=asset_default):
        """ return all asset for a given show
        """
        if conn == None:
            conn = connect_to_shotgun()
        bad_statuses = ['omt']
        res = conn.find('Asset',
                        [['project','is', {'type':'Project', 'id': show_id}],
                        ['sg_status_list', 'not_in', bad_statuses]],
                        ['code', 'sg_asset_type', 'sg_status_list'])


        return [call_default(x['code'],
                             x['id'],
                             x['sg_asset_type'],
                             x['sg_status_list']) for x in res]


    @staticmethod
    def shots_with_id(show_id,
                      shot_names, conn=None, call_default=shot_default):
        """ return a list of shot for a given show and code list
        """
        if conn == None:
            conn = connect_to_shotgun()
        bad_statuses = ['omt']
        res = conn.find('Shot',
                        [['project','is', {'type': 'Project', 'id': show_id}],
                         ["code", "in", shot_names],
                         ['sg_status_list', 'not_in', bad_statuses]],
                        ['code','sg_cut_order', 'assets', 'sg_status_list'])

        return [call_default(x['code'],
                             x['id'],
                             x['sg_cut_order'],
                             x['assets'],x['sg_status_list']) for x in res]

    @staticmethod
    def assets_with_id(show_id, asset_names,
                       conn=None, call_default=asset_default):
        """ return a list of asset for a given show
        """
        if conn == None:
            conn = connect_to_shotgun()
        bad_statuses = ['na','omt']
        res = conn.find('Asset',
                        [['project','is', {'type':'Project', 'id':show_id}],
                         ["code", "in", asset_names],
                        ['sg_status_list','not_in',bad_statuses]],
                        ['code','sg_asset_type','sg_status_list'])

        return [call_default(x['code'],
                             x['id'],
                             x['sg_asset_type'],
                             x['sg_status_list']) for x in res]

    @staticmethod
    def dept_list_with_id(conn = None, call_default = dept_default):
        """
        departments are not show dependent 
        return a list of DeptIndfoDb
        """
        if conn == None:
            conn = connect_to_shotgun()

        res = conn.find('Department', 
                        [], # not project specific
                        ['code', 'name','id','department_type'])
        return [call_default(x['code'],
                             x['id'],
                             x['department_type'],x['name']) for x in res]

    @staticmethod
    def dept_names(conn = None):
        """
        from shotgun utils
        Returns a list of short names for the Departments, e.g. 'anm' for 
        'Animation' etc.

        return dept_shorts   a list of Department short names. 
        """
        if conn == None:
            conn = connect_to_shotgun()

        res = conn.find('Department', [], ['code'])
        res = [x['code'] for x in res]
        # remove duplicate
        res = list(set(res))
        res.sort()
        return res


    @staticmethod
    def step_list_with_id(conn = None, call_default = step_default):
        """
        departments are not show dependent
        return a list of StepIndfoDb
        """
        if conn == None:
            conn = connect_to_shotgun()

        res = conn.find('Step',
                        [],
                        StepInfoDb.SF)
        # clean when label = is blank or "-"
        res = filter(lambda x:  not x['short_name'] in ['',None,'-'],res)
        res = filter(lambda x:  not x['code'] in ['',None,'-'],res)
        return [call_default(x['code'],x['id'],x) for x in res]

    @staticmethod
    def step_names(conn = None):
        """
        from shotgun utils
        Returns a list of short names for the Step, e.g. 'anm' for
        'Animation' etc.

        return dept_shorts   a list of Step short names.
        """
        if conn == None:
            conn = connect_to_shotgun()

        res = conn.find('Step', [], ['code'])
        res = [x['code'] for x in res]
        # remove duplicate
        res = list(set(res))
        res.sort()
        return res

    @staticmethod
    def user_info_with_id(conn = None, call_default = user_default):
        # Get sg conn
        if conn == None:
            conn = connect_to_shotgun()
        res = conn.find('HumanUser', [], UserInfoDb.UF)
        res = [call_default(x)  for x in res]
        return filter(lambda x: x != None,res)

    @staticmethod
    def pipeline_config_with_id(show_id, call_default = pipeconfig_default,conn = None):
        """query owner task assign
        """
        if conn == None:
            conn = connect_to_shotgun()

        filters = list()
        filters.append(['project','is', {'type':'Project', 'id':show_id}])
        fields = PipeConfigInfoDb.PCF
        res = conn.find("PipelineConfiguration", filters, fields)
        res = [call_default(x)  for x in res]
        return filter(lambda x: x != None,res)

    @classmethod
    def query_settings(cls, project_id, conn = None):
        """Return list of setting info relative to a project
        """
        if conn == None:
            conn = connect_to_shotgun()
        filters = list()
        filters.append(['project','is', {'type':'Project', 'id': project_id}])
        fields = SettingsInfoDb.SF

        res = conn.find(cls._settings["project_settings"],
                                     filters=filters,
                                     fields=fields)
        result = list()
        for x in res:
            result.append(settings_default(x))
        return result

    @classmethod
    def playlist_query_versions(cls,
                                project_id=-1,
                                conn = None):
        """Return list of shotgun playlist info relative to a project

            :param project_id: project id
            :param conn: a shotgun connection, default None
        """
        if conn == None:
            conn = connect_to_shotgun()

        filters = list()
        if project_id != -1:
            filters.append(['project', 'is', {'type':'Project',
                                                'id': project_id}])
        fields = ScreenRoomInfoDb.PLF
        #fields = []
        res = conn.find('Playlist',
                        filters = filters,
                        fields = fields,
                        order   = [{'field_name': 'created_at',
                                    'direction':'desc'}])

        result = list()
        for x in res:
            # lot of playlist are empty so with filter them out here
            vers = x.get('versions',list())
            if len(vers) > 0:
                result.append(screenroom_default(x))
        return result


    @classmethod
    def fpt_by_name(cls, call_default = pft_default, conn=None):
        """Query for PublishedFileType

            :param conn: a shotgun connection, default None

        """
        if conn == None:
            conn = connect_to_shotgun()
        ft = conn.find("PublishedFileType",
                       [
                        ["sg_status_list", "is", "act"]
                        ],
                       PftInfoDb.PFT)
        result = list()
        for f in ft:
            v = call_default(f)
            if v:
                result.append(v)
        return result


    @classmethod
    def filter_fpt_by_name(cls,
                           list_of_short_name,
                           call_default = pft_default,
                           conn=None):
        if conn == None:
            conn = connect_to_shotgun()
        if isinstance(list_of_short_name, basestring):
            list_of_short_name = [list_of_short_name]

        ft = conn.find("PublishedFileType",
                       [
                        ["short_name", "in",list_of_short_name],
                        ["sg_status_list", "is", "act"]
                        ],
                       PftInfoDb.PFT)

        result = list()
        for f in ft:
            v = call_default(f)
            if v:
                result.append(v)
        return result

    @classmethod
    def tasks_by_name(cls,
                      project_id,
                      call_default = task_default,
                      conn=None):
        """Query for Tash

            :param conn: a shotgun connection, default None

        """
        if conn == None:
            conn = connect_to_shotgun()

        filters = list()
        filters.append(['project', 'is', {'type': 'Project', 'id':project_id}])
        fields = list(['code','task_assignees','sg_status_list'])

        res = conn.find("Task",filters=filters,fields=fields)
        result = list()
        for f in res:
            v = call_default(f)
            if v:
                result.append(v)
        return result

    @classmethod
    def entity_asset_query_versions(cls,
                                    project_id,
                                    entity_asset_id,
                                    file_type_list_id = None,
                                    call_default = pf_default,
                                    conn = None):
        """Return a list of publishFiled sorted with version number for asset

            :param project_id: project_id
            :param entity_asset_id:  a asset id
            :param file_type_list_id: a list of file_type_id
            :param conn: a shotgun connection, default None

        """
        if conn == None:
            conn = connect_to_shotgun()


        filters = list()
        if project_id != -1:
            filters.append(['project','is', {'type':'Project', 'id': project_id}])
        if entity_asset_id != -1:
            filters.append(['entity','is', {'type': 'Asset', 'id': entity_asset_id}])

        if len(file_type_list_id) > 0:
            filters.append(["published_file_type.PublishedFileType.id", "in", file_type_list_id])

        query_fields = PfInfoDb.PFS
        res = conn.find('PublishedFile',
                        filters = filters,
                        fields  = query_fields,
                        order   = [{'field_name':'version_number',
                                    'direction':'desc'}]
                        )

        result = list()
        for x in res:
            v = call_default(x)
            if v:
                result.append(v)
        return result

    @classmethod
    def entity_shot_query_versions(cls,
                                   project_id,
                                   entity_shot_id,
                                   file_type_list_id = None,
                                   call_default = pf_default,
                                   conn = None):
        """Return a list of publishFiled sorted with version number for shot

            :param project_id: project_id
            :param entity_shot_id:  a shot id
            :param file_type_list_id: a list of file_type_id
            :param conn: a shotgun connection, default None

        """
        if conn == None:
            conn = connect_to_shotgun()


        filters = list()
        if project_id != -1:
            filters.append(['project','is', {'type':'Project', 'id': project_id}])
        if entity_shot_id != -1:
            filters.append(['entity','is', {'type': 'Shot', 'id': entity_shot_id}])

        if len(file_type_list_id) > 0:
            filters.append(["published_file_type.PublishedFileType.id", "in", file_type_list_id])

        query_fields = PfInfoDb.PFS
        res = conn.find('PublishedFile',
                        filters = filters,
                        fields  = query_fields,
                        order   = [{'field_name':'version_number',
                                    'direction':'desc'}]
                        )

        result = list()
        for x in res:
            v = call_default(x)
            result.append(v)
        return result


    @classmethod
    def published_file_query(cls,
                             project_id,
                             entity_publish_id,
                             query_fields = PfInfoDb.PFS,
                             call_default = pf_default,
                             conn = None):
        """shogun api find PublishedFile

            :param project_id: project_id
            :param entity_publish_id:  entity_publish_id: int, list of id or -1
            :param conn: a shotgun connection, default None

        """
        if conn == None:
            conn = connect_to_shotgun()


        filters = list()
        if project_id != -1:
            filters.append(['project','is', {'type':'Project', 'id': project_id}])
        if isinstance(entity_publish_id,list):
            filters.append(['id','in', entity_publish_id])
        elif entity_publish_id != -1:
            filters.append(['entity','is', {'type': 'PublishedFile',
                                            'id': entity_publish_id}])

        res = conn.find('PublishedFile', filters = filters, fields  = query_fields)

        result = list()
        for x in res:
            v = call_default(x)
            result.append(v)
        return result

    @classmethod
    def published_file_query_one(cls,
                                 project_id,
                                 entity_publish_id,
                                 query_fields = PfInfoDb.PFS,
                                 call_default = pf_default,
                                 conn = None):
        """

            :param project_id: project_id
            :param  entity_publish_id: int or -1
            :param conn: a shotgun connection, default None
        """
        if conn == None:
            conn = connect_to_shotgun()

        filters = list()
        if project_id != -1:
            filters.append(['project','is', {'type':'Project', 'id': project_id}])
        filters.append(['id','is', entity_publish_id])
        res = conn.find_one('PublishedFile',
                            filters = filters,
                            fields  = query_fields)

        if res != None:
            return [call_default(res)]
        return list()


    @staticmethod
    def query_shot_media_versions(project_id,
                                  shot_id,
                                  query_field,
                                  version_type = None,
                                  conn = None):
        """Return list of version info relative to a shot

            :param project_id: a valid project id
            :param shot_id: a valid shot id
            :param query_field: the field to query
            :param version_type: a list of version type
            :param conn: a shotgun connection, default None

        """
        if conn == None:
            conn = connect_to_shotgun()

        filters = [['project','is', {'type':'Project', 'id':project_id}]]
        filters.append(['entity','is', { 'type': 'Shot', 'id': shot_id}])
        if version_type != None:
            filters.append(["sg_version_type", 'in', version_type])

        res = conn.find('Version',
                        filters = filters,
                        fields  = query_field,
                        order   = [{'field_name':'id','direction':'desc'}]
                        )
        result = list()
        for x in res:
            v = version_default(x)
            result.append(v)
        return result


    @classmethod
    def query_shot_media_latest(cls,
                                show_id,
                                shot_id,
                                query_field,
                                version_type,
                                conn = None):
        """Return list of the lasted version for each type for shot

            :param project_id: a valid project id
            :param shot_id: a valid shot id
            :param query_field: the field to query
            :param version_type: a list of version type
            :param conn: a shotgun connection, default None

        """
        if conn == None:
            conn = connect_to_shotgun()

        filters = [['project','is', {'type':'Project', 'id':show_id}]]
        filters.append(['entity','is', { 'type': 'Shot', 'id': shot_id}])
        if version_type:
            filters.append(["sg_version_type", 'in', version_type])
        result = cls._summary_shot_media_version(conn, filters, query_field)
        return result

    @classmethod
    def _summary_shot_media_version(cls, conn, filters, query_field):
        """Call summary to get the lasted, see query_shot_media_latest

            :param conn: a shotgun connection
            :param filters: a filter list
            :param query_field: the field to query

        """
        if conn == None:
            conn = connect_to_shotgun()
        filters.append(['entity', 'type_is', 'Shot'])
        summary = conn.summarize('Version',
                                 filters,
                                 summary_fields=[{'field':'id','type':'maximum'}],
                                 grouping=[{'field':'entity','type':'exact','direction':'asc'},
                                           {'field':'sg_version_type','type':'exact','direction':'asc'}] )

        ver_id_list = []
        if summary.has_key('groups'):
            for shot_summary in summary['groups']:
                if shot_summary.has_key('groups'):
                    for v in shot_summary['groups']:
                        ver_id_list.append( v['summaries']['id'] )
        if len(ver_id_list) == 0:
            return ver_id_list
        res = conn.find('Version', [['id', 'in', ver_id_list]], query_field)

        result = list()
        for x in res:
            v = version_default(x)
            result.append(v)
        return result

    @staticmethod
    def query_asset_media_versions(show_id,
                                   asset_id,
                                   query_field,
                                   version_type = None,
                                   conn = None):
        """Return list of version info relative to a shot

            :param project_id: a valid project id
            :param shot_id: a valid asset id
            :param query_field: the field to query
            :param version_type: a list of version type
            :param conn: a shotgun connection, default None

        """

        if conn == None:
            conn = connect_to_shotgun()

        filters = [['project','is', {'type':'Project', 'id': show_id}]]
        filters.append(['entity','is', { 'type': 'Asset', 'id': asset_id}])

        if version_type:
            filters.append(['sg_version_type','in', version_type])


        res = conn.find('Version',
                        filters = filters,
                        fields  = query_field,
                        order   = [{'field_name':'id','direction':'desc'}]
                        )
        result = list()
        for x in res:
            v = version_default(x)
            result.append(v)
        return result

    @classmethod
    def get_lasted_version_for_show(cls, showid, query_field, limit=10, conn=None):
        """Return a list a limit number of the last version for a show

            :param showid: a show id
            :param query_field: see VersionInfoDb.VC
            :param limit: a number to get how many
            :param conn: a shotgun connection

        """
        if conn is None:
            conn = connect_to_shotgun()
        status_list_except = ['qd','sbmt','fld']
        filters = [['project', 'is', {'type': 'Project', 'id': showid}]]
        filters.append (('sg_status_list', 'not_in', status_list_except))

        order = [{'direction': 'desc', 'field_name': 'id'}]
        res = conn.find('Version',filters,query_field,order,limit=limit)
        result = list()
        for x in res:
            v = version_default(x)
            result.append(v)
        return result


    @classmethod
    def query_asset_media_latest(cls,
                                  show_id,
                                  asset_id,
                                  query_field,
                                  version_type,
                                  conn = None):
        """Return list of the lasted version for each type for asset

            :param project_id: a valid project id
            :param shot_id: a valid shot id
            :param query_field: the field to query
            :param version_type: a list of version type
            :param conn: a shotgun connection, default None

        """

        if conn == None:
            conn = connect_to_shotgun()

        filters = [['project', 'is', {'type': 'Project', 'id': show_id}]]
        filters.append(['entity','is', { 'type': 'Asset', 'id': asset_id}])
        if version_type:
            filters.append(['sg_version_type', 'in', version_type])
        result = cls._summary_asset_version(conn, filters, query_field)
        return result

    @classmethod
    def _summary_asset_version(cls, conn, filters, query_field):
        """Call summary to get the lasted, see query_asset_media_latest

            :param conn: a shotgun connection
            :param filters: a filter list
            :param query_field: the field to query

        """

        if conn == None:
            conn = connect_to_shotgun()

        filters.append(['entity', 'type_is', 'Asset'])
        summary = conn.summarize('Version',
                                 filters,
                                 summary_fields=[{'field':'id',
                                                  'type':'maximum'}],
                                 grouping=[{'field': 'entity',
                                            'type':'exact',
                                            'direction':'asc'}] )

        # now collect all the version ids
        ver_id_list = []
        if summary.has_key('groups'):
            for asset_summary in summary['groups']:
                if asset_summary.has_key('groups'):
                    for v in asset_summary['groups']:
                        ver_id_list.append(v['summaries']['id'] )
        if len(ver_id_list) == 0:
            return ver_id_list
        res = conn.find('Version', [['id', 'in', ver_id_list]], query_field)
        result = list()
        for x in res:
            v = version_default(x)
            if v:
                result.append(v)
        return result

    # ##################################################################
    @staticmethod
    def show_id_by_name(conn, project_name):
        """find one show from tank_name

            :param conn: a shotgun connection, default None
            :param project_name: tank_name for the show
            :return project entity dict:
        """
        if conn == None:
            conn = connect_to_shotgun()
        return conn.find_one("Project",
                             [['tank_name', 'is', project_name]],
                             None)

    @staticmethod
    def shot_id_by_code(conn, project_id, shot_list_code):
        """query a shot list dictionary

            :param conn: a shotgun connection, default None
            :param shot_list_code: list of shot code
            :param project_id: project id
            :return list: list of shot entity dict
        """
        if conn == None:
            conn = connect_to_shotgun()

        list_id = list()
        for s in shot_list_code:
            list_id.append(conn.find_one('Shot',
                                         [['code', 'is', s],
                                         ['project', 'is', project_id]], None))
        return list_id

    @staticmethod
    def asset_id_by_code(conn, project_id, asset_list_code):
        """query a asset list dictionary

            :param conn: a shotgun connection, default None
            :param asset_list_code: list of asset code
            :param project_id: project id
            :return list: list of shot entity dict
        """
        if conn == None:
            conn = connect_to_shotgun()

        list_id = list()
        for s in asset_list_code:
            list_id.append(conn.find_one('Asset',
                                         [['code', 'is', s],
                                         ['project', 'is', project_id]],None))
        return list_id

    @staticmethod
    def search_video_version_query(conn,
                                   project_id,
                                   entity_list,
                                   submit_login_list=None,
                                   status_list=None,
                                   version_type=VersionInfoDb.VC,
                                   fields=VersionInfoDb.VF,
                                   limit=10):
        """Search the version matching a certain criteria (not finish)

            :param project_id: a project id
            :param entity_list: a list of entity id
            :param submit_login_list:
            :param entity_list: can provide directly the entity list,
                    otherwise it will be derived from the entity type and code

        """
        if conn == None:
            conn = connect_to_shotgun()

        filters = [('sg_version_type', 'in', version_type),
                   ('project', 'is', project_id),
                   ('entity', 'is_not', None)]

        filters.append(('entity', 'in', entity_list))

        if submit_login_list:
            filters.append (('sg_login', 'in', submit_login_list))

        if status_list:
            filters.append (('sg_status_list', 'in', status_list))

        res = conn.find('Version',
                        filters = filters,
                        fields = fields,
                        order   = [{'field_name':'created_at',
                                    'direction':'desc'}],
                        limit   = limit)
        return res

    @classmethod
    def search_video_version(cls,
                             conn,
                             project_id,
                             entity_list,
                             dept_list=None,
                             submit_login_list=None,
                             status_list=None,
                             version_type=VersionInfoDb.VC,
                             fields=VersionInfoDb.VF,
                             limit=10):

        res = cls.search_video_version_query(
                                    conn,
                                    project_id,
                                    entity_list,
                                    dept_list=dept_list,
                                    submit_login_list=submit_login_list,
                                    status_list=status_list,
                                    version_type=version_type,
                                    fields=fields,
                                    limit=limit)
        result = list()
        for x in res:
            v = version_default(x)
            if v:
                result.append(v)
        return result

    # ####################################################################
    @staticmethod
    def project_list(conn, tank_names):
        """Return a list of all the projects in the Shotgun database.

        :param conn: the active shotgun connection
        :return list: list  of all project entities in shotgun

        """
        if conn == None:
            return list()
        bad_statuses = ['na', 'omt']

        if tank_names == None:
            return conn.find('Project',
                             [['sg_status', 'not_in', bad_statuses]],
                             ['type', 'name', 'sg_code', 'id',
                              'active', 'tank_name'])
        else:
            if isinstance(tank_names, basestring):
                tank_names = [tank_names]
            return conn.find('Project',
                             [['sg_status', 'not_in', bad_statuses],
                              ['tank_name', 'in', tank_names]],
                             ['type', 'name', 'sg_code', 'id',
                              'active', 'tank_name'])

    @staticmethod
    def db_user(conn = None, fields = ['login','firstname','lastname']):
        """Query user information

            :param conn: the active shotgun connection, default None
            :param fields: a list of field. optional 
                            default=['login','firstname','lastname']
        """
        # Get sg conn
        if conn == None:
            conn = connect_to_shotgun()
        return conn.find('HumanUser', [], fields)

    @staticmethod
    def db_group_user(project_name, group_name, conn=None):
        """Filter through the group

            :param conn: the active shotgun connection, default None
            :param project_name: what show
            :param group_name: name of a shotgun group
            :return : list of users in shotgun group

        """
        # set variables
        user_list = list()
        # Get sg conn
        if conn == None:
            conn = connect_to_shotgun()

        # Get users from group
        groups = conn.find_one('Group', 
                               [['code','is', group_name]], ['users'])
        if groups and 'users' in groups:
            users = groups['users']
        else:
            return user_list

        for user in users:
            # Get user_name
            user_name = user['name']
            # Get sg human user from user_name
            human_user = conn.find_one('HumanUser',
                                        [['name', 'is', user_name]],
                                        ['login'])
            if human_user != []:
                # Get email
                login = human_user['login']
                # Append email to email_list
                user_list.append(login)
        return user_list

    @staticmethod
    def list_version_status(conn = None):
        """List all the possible the version status

            :param conn: the active shotgun connection, default None
            example::

                from dsk.base.db_helper.db_helper_funct import ShotgunQuery
                ShotgunQuery.list_version_status()

        """
        if conn is None:
            conn = connect_to_shotgun()
        X = conn.schema_field_read('Version')
        return X['sg_status_list']['properties']['valid_values']['value']

    @staticmethod
    def download_icon(image_url, dest, conn = None):
        """Download an image from the server to local disk

            :param image_url: a valid address for the image
            :param dest: a fullpath to image on disk. directory needs to exist
            :return : bool, True if success
        """
        from sgtk.util.shotgun import download_url
        if conn is None:
            conn = connect_to_shotgun()
        try:
            download_url(conn, image_url, dest)
        except:
            return False
        return True
