import os
import sys
from collections import OrderedDict

from dskenv import dskenv_constants

from dsk.base.tdata.gen_tree import GenTree
from dsk.base.db_helper.shotgun_script import connect_to_shotgun_time_out as connect_to_shotgun

from dsk.base.db_helper.steplist_info_db import StepListInfoDb
from dsk.base.db_helper.shot_info_db import ShotInfoDb
from dsk.base.db_helper.asset_info_db import AssetInfoDb
from dsk.base.db_helper.dept_info_db import DeptInfoDb
from dsk.base.db_helper.version_info_db import VersionInfoDb
from dsk.base.db_helper.user_info_db import UserListInfoDb
from dsk.base.db_helper.user_info_db import UserInfoDb
from dsk.base.db_helper.db_helper_funct import ShotgunQuery as SQ
from dsk.base.utils.msg_utils import MsgUtils as log
from dsk.base.conn_helper.sgtk_mapping import getAssetMapping,getShotMapping
from dsk.base.utils.time_utils import StopWatch

if sys.version_info[0] >= 3:
    from six import string_types as basestring

AllAssetType = AssetInfoDb.AllAssetType
AllGroups = UserInfoDb.All_Groups

class Assettype(GenTree):
    def __init__(self):
        super(Assettype,self).__init__()
        self.active = True
    @property
    def label(self):
        return self.getName()

class GroupPerm(GenTree):
    def __init__(self):
        super(GroupPerm,self).__init__()
        self.active = True
    @property
    def label(self):
        return self.getName()

SW = StopWatch()

class DbCache(GenTree):
    """Handle query to shotgun and allow for memory storage (cache) to avoid
        multiple access to shotgun

        Organize the shot and asset in a tree structure
            shows/show/assets
            shows/show/sequences/sequence/shot/version/versiontype for media
            shows/show/sequences/sequence/shot/filepublishedtype for files
            shows/filetypes

        - Hold a list of showobj (see ShowInfoDb)
        - Hold a list of FPT (published file type) Query to showgun, not show specific
        - Hold a list of Steps (global entity Step, not show specific) needs to be cleanup
        - Hold a list of User (global entity HumanUser)

        Query/Keep global (not show specific) information

        Keep track of current show

    """
    __Conn = None

    def __init__(self, shot_only=False, asset_only=False, verbose = False):
        """Create an instance, (simple fast nothing important

            :param shot_only: if True will not load asset
            :param asset_only: if True will not load shot
            :param verbose: display query timing information to database

        """

        if shot_only == True:
            log.info("*" * 20 + " running query for shot only " + "*" * 20)
        if asset_only == True:
            log.info("*" * 20 + " running query for asset only " + "*" * 20)
        super(DbCache, self).__init__()

        self._shot_only = shot_only
        self._asset_only = asset_only
        self.verbose = verbose
        self.reset()

        self._asset_type = list()
        self._group_perm = list()

        self._cache_group = dict() # to build temporary cache for pipeline config

    def getVariableMember(self, dd):
        """The is a callback to control what to save or not
            per nature from doesn't need to be serialize to we remove all the
            private variable
        """
        super(DbCache,self).getVariableMember(dd)

        for key in ["_step_shot","_step_asset","_asset_type"]:
            try:
                dd.pop(key)
            except:
                pass

    @classmethod
    def get_conn(cls):
        """Create and store a shotgun api connection
        """
        if cls.__Conn == None:
            try:
                cls.__Conn = connect_to_shotgun()
            except:
                cls.__Conn = None
        return cls.__Conn

    def reset(self):
        """reset all caches
        """
        self.resetCache()
        self['Shows'] = GenTree()
        self['FPT'] = GenTree()
        self['Steps'] = StepListInfoDb()
        self['Users'] = UserListInfoDb()

        self._currentshow = ""

    def get_assettype(self):
        """asset type are not a query """
        if len(self._asset_type) > 0:
            return self._asset_type
        for at in AllAssetType:
            ato = Assettype()
            ato.setName(at)
            self._asset_type.append(ato)
        return self._asset_type

    def get_configpipefilter(self):
        """Query to config pipe filter
            :return list: a list of GroupPerm
        """
        if len(self._group_perm) > 0:
            return self._group_perm
        for at in AllGroups:
            ato = GroupPerm()
            ato.setName(at)
            self._group_perm.append(ato)
        return self._group_perm

    # STEPS
    def _do_steps(self):
        """Query and cache step info
        """

        conn = self.get_conn()
        if conn == None:
            return
        SW.start()
        if self.verbose:
            log.warning("login to shotgun, to get default step settings")
        steps = SQ.step_list_with_id(conn)
        parent = self['Steps']
        steps_name = dict()
        for s in steps:
            if not s.getName() in steps_name:
                steps_name[s.getName()] = s
        for s in steps_name:
            parent.addChild(steps_name[s], withRename = False)
        SW.stop()
        if self.verbose:
            log.info("step_query in {}".format(SW.elapsed()))

    def get_steps(self):
        if self['Steps'].nbOfChildren()== 0:
            self._do_steps()
        return self['Steps'].getChildren()

    def get_step_by_name(self, step_name = ""):
        steps = self.get_steps()
        for s in steps:
            if s.getName() == step_name:
                return s
        # return the first one if possible
        if len(steps) > 0:
            return steps[0]
        return None
    def get_departments(self):
        """ query and cache department info
        """
        if len(self._dept_shot) + len(self._dept_asset) > 0:
            return self._dept_shot + self._dept_asset

        #if not self._use_coffer:
        conn = self.get_conn()
        log.warning("login to shotgun, to get default department settings")
        dept = SQ.dept_list_with_id(conn)


        for i in dept:
            #print i.getName(),i.__dict__
            if i.is_shot():
                self._dept_shot.append(i)
            elif i.is_asset():
                self._dept_asset.append(i)
            else:
                pass # we ignore production (prod) for now
                #log.warning('unknown department type %r' % i.dept_type)
        self._dept_shot = sorted(self._dept_shot, DeptInfoDb.compare)
        self._dept_asset = sorted(self._dept_asset, DeptInfoDb.compare)
        return self._dept_shot + self._dept_asset

    def set_shot_departments(self,shot_dep):
        self._dept_shot = list()
        for i in shot_dep.getChildren():
            self._dept_shot.append(i)
        self._dept_shot = sorted(self._dept_shot, DeptInfoDb.compare)

    def add_extra_shot_department(self,dept):
        self._dept_shot.append(dept)

    def set_asset_departments(self,asset_dep):
        self._dept_asset = list()
        for i in asset_dep.getChildren():
            self._dept_asset.append(i)
        self._dept_asset = sorted(self._dept_asset, DeptInfoDb.compare)

    def get_asset_departments(self):
        if len(self._dept_asset) == 0:
            self.get_departments()
        return self._dept_asset

    def get_shot_departments(self):
        if len(self._dept_shot) == 0:
            self.get_departments()
        return self._dept_shot

    # USERS
    def _do_users(self):
        """ query and cache step info
        """
        SW.start()
        conn = self.get_conn()
        if self.verbose:
            log.warning("login to shotgun, to get user")
        step = SQ.user_info_with_id(conn=conn)
        parent = self['Users']
        for s in step:
            parent.addChild(s, withRename = False)
        SW.stop()
        if self.verbose:
            log.info("user_query in {}".format(SW.elapsed()))

    def get_users(self):
        if self['Users'].nbOfChildren()== 0:
            self._do_users()
        return self['Users'].getChildren()

    def get_user_dict(self, loginname):
        if self['Users'].nbOfChildren()== 0:
            self._do_users()
        if self['Users'].has(loginname):
            return self['Users'][loginname].get_user_dict()
        return None

    def set_show(self, show_name ,seq_name = ""):
        """Set show: load all the assets and/or shots"""

        if show_name in self.get_show_names():
            showobj = self['Shows'][show_name]
            if showobj.get_sequences().nbOfChildren() == 0 and self._asset_only == False:
                showobj.init_with_shots(sorted(SQ.shot_list_with_id(showobj.id,
                                                                    self.get_conn()),
                                               ShotInfoDb.compare))
            if seq_name != None:
                showobj.set_current_sequence(seq_name)
            else:
                showobj.set_current_sequence("")
            if showobj.get_assets().nbOfChildren() == 0 and self._shot_only == False:
                showobj.init_with_assets(sorted(SQ.asset_list_with_id(showobj.id,
                                                                      self.get_conn()),
                                                AssetInfoDb.compare))
            self._currentshow = show_name
            return True
        return False

    def load_shot(self, show_name, shot_names):
        """Load a list of shots into db under showname

            :param show_name: (str), valid sgtk name
            :param shot_names: (list or str): a valid code name for shot

        """

        showobj = None
        if show_name in self.get_show_names():
            showobj = self['Shows'][show_name]
        if showobj == None:
            return []
        if isinstance(shot_names, basestring):
            shot_names = [shot_names]
        shot_list = SQ.shots_with_id(showobj.id, shot_names, self.get_conn())
        showobj.init_with_shots(shot_list)
        self._currentshow = show_name
        return shot_list

    def load_asset(self, show_name, asset_names):
        """Load a single asset into db under showname

            :param show_name: (str), valid sgtk name
            :param asset_names: (list/str): a valid code name for asset
        """

        showobj = None
        if show_name in self.get_show_names():
            showobj = self['Shows'][show_name]

        if showobj == None:
            return list()
        if isinstance(asset_names, basestring):
            asset_names = [asset_names]

        asset_list = SQ.assets_with_id(showobj.id, asset_names, self.get_conn())
        showobj.init_with_assets(asset_list)
        self._currentshow = show_name
        return asset_list

    def init_with_current_shows(self, with_shotgun = True):
        """Initialisation of shows

            :param with_shotgun: default True, will load all the show in shotgun
                   (minus an exception list)  if False load the show define in envi_info instead
            :note: only show header are read... id, sgtk_name, no other data

        """
        s = self['Shows']
        if with_shotgun == True:
            conn = self.get_conn()
            cpl = SQ.get_current_projects(conn = conn)
            for cp in cpl:
                s.addChild(cp)
        else:
            conn = self.get_conn()
            from dskenv.api.dsk_studio import DskStudio
            envi_info = DskStudio()
            envi_info.reset(os.environ.get(dskenv_constants.DSK_ENV_PATH_KEY))
            envi_info.load_data()
            sgtks_names = envi_info.get_projects()
            cpl = SQ.get_current_projects(conn=conn, sgtk_names= sgtks_names)
            for cp in cpl:
                s.addChild(cp)

    def get_current_show_obj(self):
        """Return the current show object
        """
        if self._currentshow == "":
            return None
        return self['Shows'][self._currentshow]


    def get_showobj(self, show_default=""):
        """Return the current show object, but try to set it if not
        """
        if show_default == "" and self._currentshow != None:
            return self._currentshow

        shownames = self.get_show_names()
        if len(shownames) == 0:
            self.init_with_current_shows()
        if not show_default in self.get_show_names():
            return None
        else:
            self._currentshow = self['Shows'][show_default]

        return self._currentshow


    def get_current_show_sequence_obj(self):
        """Return the current sequence object for the current show
        """
        res = list()
        if self._currentshow == "":
            return res
        return self['Shows'][self._currentshow].get_sequences()

    def get_current_sequencename(self):
        """Return the current sequence name for the current show
        """
        if self._currentshow == "":
            return ""
        return self['Shows'][self._currentshow].get_current_sequencename()


    def get_current_showname(self):
        s = self.get_current_show_obj()
        if s == None:
            return "no current show"
        return s.getName()

    def get_show_names(self):
        """Return the list of current show names
        """
        return self['Shows'].childNames()


    def cache_file_type(self):
        """Build a dico to map short_name filetype to name
        """
        ft = SQ.fpt_by_name(conn = self.get_conn())
        fpt = self['FPT']
        for f in ft:
            fpt.addChild(f)
        fpt.cache()

    def get_all_fpt(self):
        """Return as a list all publishFileType (global to all show)
        """
        if self['FPT'].nbOfChildren() == 0:
            self.cache_file_type()
        return self['FPT'].getChildren()

    def get_file_type_names(self):
        """Return as a list all publishFileType 'name' (global to all show)
        """
        if self['FPT'].nbOfChildren() == 0:
            self.cache_file_type()
        return self['FPT'].childNames()

    def get_ft_from_short_name(self, short_name):
        """Return publishFileType code of short name (global to all show)

            :param short_name: short name of the publish file type
            :return list of ids:

        """
        if self['FPT'].nbOfChildren() == 0:
            self.cache_file_type()
        if self['FPT'].has(short_name):
            return self['FPT'][short_name].code
        return ""

    def get_ftid_from_short_name(self, short_name):
        """Return publishFileType 'id' (global to all show)

            :param short_name: short name of the publish file type
            :return list of ids:

        """
        if self['FPT'].nbOfChildren() == 0:
            self.cache_file_type()
        if self['FPT'].has(short_name):
            return self['FPT'][short_name].id
        return ""


    def update_media_version_shot_info(self,
                                       showobj,
                                       shotobj,
                                       version_type = None,
                                       force = True):
        """Version stuff for asset

            :param showobj: ShowInfoDb object
            :param shotobj: ShotInfoDb object
            :param version_type: default None, a list of version type
                   example: ['deadlineNukeRender', 'publishedNukeRender']
            :param force: bool force the query

        """

        if force == False and shotobj.is_version_set():
            return shotobj.get_media_version()

        #steplist = map(lambda x: x ,filter(lambda x: x.active == True,steplist))
        res = list()
        if showobj.id != -1 and  shotobj.id != -1:
            res = SQ.query_shot_media_versions(showobj.id,
                                               shotobj.id,
                                               VersionInfoDb.VF,
                                               version_type = version_type,
                                               conn = self.get_conn())


        versions = shotobj.set_media_version(res)
        return versions


    def update_media_version_asset_info(self,
                                        showobj,
                                        assetobj,
                                        version_type = None,
                                        force = False):
        """Version stuff for asset

            :param showobj: ShowInfoDb object
            :param assetobj: AssetInfoDb object
            :param version_type: default None, a list of version type
                   example: ['deadlineNukeRender', 'publishedNukeRender']
            :param force: bool force the query
        """
        if force == False and assetobj.is_version_set():
            return assetobj.get_media_version()

        res = list()
        if showobj.id != -1 and  assetobj.id != -1:
            res = SQ.query_asset_media_versions(showobj.id,
                                                assetobj.id,
                                                VersionInfoDb.VF,
                                                version_type = version_type,
                                                conn = self.get_conn())
        versions = assetobj.set_media_version(res)
        return versions

    def get_lasted_version_for_show(self, showobj, limit=10):
        """Return a list a limit number of the last version for a show
            No cache for now
        """
        res = SQ.get_lasted_version_for_show(showobj.id,
                                             VersionInfoDb.VF,
                                             limit=limit,
                                             conn=self.get_conn())
        return res

    def assetid_filepubobj_query(self,
                                 showobj,
                                 assetobj,
                                 file_type_object_list):
        """Return a list of publishedFile

            :param showobj:
            :param assetobj:
            :param file_type_list: (list) pft Short name interface
            :return list: list of list of PfInfoDb sorted as file_type_object_list

        """

        file_type_list_id = [x.id for x in file_type_object_list]
        file_type_list_id = filter(lambda x: x != '', file_type_list_id)
        pf_list = SQ.entity_asset_query_versions(showobj.id,
                                                 assetobj.id,
                                                 file_type_list_id=file_type_list_id,
                                                 conn=self.get_conn())
        res = list()
        for ftol in file_type_object_list:
            res.append([x for x in pf_list if x.published_file_type["id"] == ftol.id])
        return res

    def assetid_filepub_query(self,
                               showobj,
                               assetid,
                               file_type_list):
        """
            :param showobj:
            :param assetid:
            :param file_type_list: (list) pft Short name interface
            :return list: list of PfInfoDb
         """

        file_type_list_id = [self.get_ftid_from_short_name(x) for x in file_type_list]
        file_type_list_id = filter(lambda x: x != '', file_type_list_id)
        pft_list = SQ.entity_asset_query_versions(showobj.id,
                                                  assetid,
                                                  file_type_list_id=file_type_list_id,
                                                  conn=self.get_conn())

        return pft_list

    def shotid_filepubobj_query(self,
                                showobj,
                                shotobj,
                                file_type_object_list):
        """
            :param showobj:
            :param shotobj:
            :param file_type_list: (list) pft Short name interface
            :return list: list of PfInfoDb

         """
        file_type_list_id = [x.id for x in file_type_object_list]
        file_type_list_id = filter(lambda x: x != '', file_type_list_id)
        pf_list = SQ.entity_shot_query_versions(showobj.id,
                                                 shotobj.id,
                                                 file_type_list_id=file_type_list_id,
                                                 conn=self.get_conn())
        res = list()
        for ftol in file_type_object_list:
            res.append([x for x in pf_list if x.published_file_type["id"] == ftol.id])
        return res

        return pf_list

    def shotid_filepub_query(self,
                             showobj,
                             shotid,
                             file_type_list):
        """
            :param showobj:
            :param   shotid:
            :param file_type_list: (list) pft Short name interface
            :return list: list of PfInfoDb
         """

        file_type_list_id = [self.get_ftid_from_short_name(x) for x in file_type_list]
        file_type_list_id = filter(lambda x: x != '', file_type_list_id)

        pft_list = SQ.entity_shot_query_versions(showobj.id,
                                                 shotid,
                                                 file_type_list_id=file_type_list_id,
                                                 conn=self.get_conn())

        return pft_list


    def _get_ft(self, adict):
        fts = self.get_all_fpt()
        all_names = [x.getName()for x in fts]
        file_type_obj_list = list()
        for x in adict.values():
            try:
                index = all_names.index(x)
                file_type_obj_list.append(fts[index])
            except:
                pass
        return file_type_obj_list



    def inspect_shot_depend(self, showobj, shotobj):
        """Load the needed filepublish

            :param showobj: a ShowInfoDb object
            :param shotobj: a ShotInfoDb object

        """
        SW.start()
        # this needs to isolated
        typeList = getShotMapping(showobj.getName())

        allready = shotobj.get_publishedType()
        allready = [x.getName() for x in allready]

        typeListMissing = OrderedDict()
        for i in typeList:
            if not typeList[i].short_name in allready:
                typeListMissing[i] = typeList[i].short_name
        if len(typeListMissing) > 0:

            file_type_obj_list = self._get_ft(typeListMissing)
            pf_list = self.shotid_filepubobj_query(showobj,
                                                   shotobj,
                                                   file_type_obj_list)

            for k,pf in zip(typeListMissing.keys(),pf_list):
                shotobj.set_plublished_type(typeListMissing[k],pf)

        SW.stop()
        if self.verbose:
            log.info("shotid_filepub_query in {}".format(SW.elapsed()))

    def inspect_shot_asset_depend(self, showobj, assetobj):
        """Load the needed filepublish

            :param showobj: a ShowInfoDb object
            :param assetobj: a AssetInfoDb object

        """
        typeList = getAssetMapping(showobj.getName())

        assets_name = assetobj.get_asset_names()
        asset_obj_list = showobj.load_asset_if_not(self, assets_name)

        SW.start()
        for assobj in asset_obj_list:
            allready = assobj.get_publishedType()
            allready = [x.getName() for x in allready]
            typeListMissing = OrderedDict()
            for i in typeList:
                if not typeList[i].short_name in allready:
                    typeListMissing[i] = typeList[i].short_name
            if len(typeListMissing) == 0:
                continue
            file_type_obj_list = self._get_ft(typeListMissing)

            pf_list = self.assetid_filepubobj_query(showobj,
                                                    assobj,
                                                    file_type_obj_list)

            for k,pf in zip(typeListMissing.keys(),pf_list):
                # update data list
                assobj.set_plublished_type(typeListMissing[k],pf)
        SW.stop()
        if self.verbose:
            log.info("assetid_filepub_query in {}".format(SW.elapsed()))

    def inspect_asset_depend(self, showobj, assobj):
        typeList = getAssetMapping(showobj.getName())
        SW.start()

        allready = assobj.get_publishedType()
        allready = [x.getName() for x in allready]
        typeListMissing = OrderedDict()
        for i in typeList:
            if not typeList[i].short_name in allready:
                typeListMissing[i] = typeList[i].short_name
        if len(typeListMissing) == 0:
            SW.stop()
            if self.verbose:
                log.info("assetid_filepub_query in {}".format(SW.elapsed()))
            return
        file_type_obj_list = self._get_ft(typeListMissing)


        pf_list = self.assetid_filepubobj_query(showobj,
                                                assobj,
                                                file_type_obj_list)

        for k,pf in zip(typeListMissing.keys(),pf_list):
            # update data list
            assobj.set_plublished_type(typeListMissing[k], pf)
        SW.stop()
        if self.verbose:
            log.info("assetid_filepub_query in {}".format(SW.elapsed()))


    def get_current_confpipe(self,showobj):
        SW.start()
        res = showobj.get_current_confpipe(self)
        SW.stop()
        if self.verbose:
            log.info("get_current_confpipe in {}".format(SW.elapsed()))
        return res


    def mapping_user_ids(self):
        if len(self._cache_group) > 0:
            return
        users = self.get_users()
        for u in users:
            self._cache_group[u.id] = u.get_permission_group()
        return self._cache_group

    def get_filtered_confpipesname(self, allconfpipe, filtergroupname, with_primary = True):
        #allconfpipename = db.get_filtered_confpipesname(self.filtertype)
        result = list()
        self.mapping_user_ids()
        for ch in allconfpipe:
            for x in ch.useridlist():
                if x in self._cache_group and self._cache_group[x] in filtergroupname:
                    result.append(ch.getName())
        result = list(set(result))
        if with_primary == True and not 'Primary' in result:
            result.insert(0, "Primary")
        return result

    def download_icon(self,image_url, dest):
        SW.start()
        SQ.download_icon(image_url, dest, self.get_conn())
        SW.stop()
        if self.verbose:
            log.info("download icon in {}".format(SW.elapsed()))
