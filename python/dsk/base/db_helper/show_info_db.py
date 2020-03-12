from dsk.base.tdata.gen_tree import GenTree
from dsk.base.db_helper.sequence_info_db import SequenceInfoDb
from dsk.base.db_helper.assetlist_info_db import AssetListInfoDb
from dsk.base.db_helper.pipeconfig_info_db import PipeConfigListInfoDb
from dsk.base.utils.msg_utils import MsgUtils as log


class ShowInfoDb(GenTree):
    def __init__(self):
        super(ShowInfoDb, self).__init__()
        self.reset()

    def reset(self):
        self.id = -1
        self.label = ""
        self._currentsequence = ""
        self._currentasset = ""
        self._current_configpipe = ""
        self['Sequences'] = GenTree()
        self['Assets'] = AssetListInfoDb()
        self['PipelineConfig'] = PipeConfigListInfoDb()
        self['TaskAssign'] = GenTree()
        self.shot_order_dict = None

    def setdata(self, idi, label=""):
        self.id = idi
        self.label = label
        return True

    def get_sequences(self):
        return self['Sequences']

    def get_assets(self):
        return self['Assets']

    def get_configpipe(self):
        return self['PipelineConfig']

    def get_confpipes_list(self):
        return self['PipelineConfig'].getChildren()

    def get_task(self):
        return self['TaskAssigned']

    def get_task_list(self):
        return self['TaskAssigned'].getChildren()

    def reset_sequences_and_assets(self):
        self['Sequences'].resetChildren()
        self['Assets'].resetChildren()
        self['Sequences'] = GenTree()
        self['Assets'] = AssetListInfoDb()
        self.shot_order_dict = dict()

    def set_shot_order_table(self, shot_order_dict=None):
        self.shot_order_dict = shot_order_dict
        self.shot_order_dict = dict()
        for seqo in self['Sequences'].getChildren():
            for shoto in seqo.getChildren():
                if shoto.shot_order != -1:
                    # replace shot order with the object
                    self.shot_order_dict[shoto.shot_order] = shoto

    def get_shot_order_table(self):
        return self.shot_order_dict

    """ shots stuff """
    def init_with_shots(self, shot_list):
        """Take a list of ShotInfoDb and group it by sequence"
        """
        for s in shot_list:
            if s.is_valid_code():
                s.setName(s.short_name())
                seq = s.sequence_name()
                if not self['Sequences'].has(seq):
                    new_seq = SequenceInfoDb()
                    new_seq.setName(seq)
                    self['Sequences'].addChild(new_seq)
                self['Sequences'][seq].addChild(s)

    def set_current_sequence(self, seq_name):
        seqnames = self.get_sequence_names()
        if seq_name in seqnames:
            self._currentsequence = seq_name
            return True
        if len(seqnames) > 0:
            self._currentsequence = seqnames[0]
            return False
        return False

    def get_current_sequencename(self):
        return self._currentsequence

    def get_current_sequence_obj(self):
        if self._currentsequence == "":
            return None
        return self['Sequences'][self._currentsequence]

    def get_current_shotlist_names(self):
        """
        return the shotname in the current sequence
        """
        if self._currentsequence == "":
            return list()
        return self['Sequences'][self._currentsequence].childNames()

    def get_sequence_names(self):
        """ return the list of seq name for current show
        """
        return self['Sequences'].childNames()

    """ asset stuff """
    def init_with_assets(self, asset_list):
        """
        take a list of AssetInfoDb and group it by sequence"
        """
        assets = self.get_assets()
        for s in asset_list:
            assets.addChild(s)

    def get_assetlist_names(self):
        """
        return all assets
        """
        return self['Assets'].childNames()

    def load_asset_if_not(self, db, asset_names):
        """Load none asset loaded into show
            :param:
                   asset_names (list/str): a valid code name for asset
        """
        from dsk.base.db_helper.db_helper_funct import ShotgunQuery as SQ
        if isinstance(asset_names, basestring):
            asset_names = [asset_names]

        assets = self.get_assets()
        in_all_ready = assets.childNames()

        to_query = list()
        all_ready_there = list()
        for s in asset_names:
            if s not in in_all_ready:
                to_query.append(s)
            else:
                ch = assets.getChildByName(s)
                if ch is None:
                    log.error("cannot retrieve asset: %s", s)
                else:
                    all_ready_there.append(ch)

        asset_list = list()
        if len(to_query) > 0:
            asset_list = SQ.assets_with_id(self.id, to_query, db.get_conn())
            self.init_with_assets(asset_list)
        return asset_list + all_ready_there

    def get_asset_obj(self, asset_name):
        if self['Assets'].has(asset_name):
            return self['Assets'][asset_name]
        return None

    def get_current_asset(self):
        if self._currentasset == "":
            ass = self.get_assets()
            if ass.nbOfChildren() > 0:
                cas = ass.getChildren()[0]
                self._currentasset = cas.getName()
        return self._currentasset

    def set_current_asset(self, asset_name):
        if asset_name in self.get_assetlist_names():
            self._currentasset = asset_name
        else:
            self._currentasset = ""

    # Task
    def init_with_Task(self, task_list):
        taskp = self['TaskAssign']
        for pc in task_list:
            taskp.addChild(pc)

    def get_usertask_list(self, db, userlogin):
        from dsk.base.db_helper.db_helper_funct import ShotgunQuery as SQ
        user = db.get_user_dict(userlogin)
        res = list()
        if user:
            ch = self['TaskAssign'].getChildren()
            if len(ch) == 0:
                task_list = SQ.tasks_by_name(self.id, conn=db.get_conn())
                self.init_with_Task(task_list)
            ch = self['TaskAssign'].getChildren()

            idu = int(user['id'])

            for x in ch:
                if idu in x.assigned_ids():
                    res.append("%s" % x.id)

        return list(set(res))

    # config pipe
    def init_with_pipeline_config(self, pc_list):
        confp = self['PipelineConfig']
        for pc in pc_list:
            confp.addChild(pc)

    def get_config_path_noprimary(self, db):
        adefname = self.get_current_confpipe(db)
        for x in self['PipelineConfig'].getChildren():
            if x.getName() != "Primary":
                return self.get_current_config_path(x.getName())
        return self.get_current_config_path(adefname)

    def get_current_confpipe(self, db=None):
        """Set to the first found"""
        if self._current_configpipe == "":
            ass = self.get_configpipe()
            if ass.nbOfChildren() > 0:
                cas = ass.getChildren()[0]
                self._current_configpipe = cas.getName()
            elif db:
                from dsk.base.db_helper.db_helper_funct import ShotgunQuery
                res = ShotgunQuery.pipeline_config_with_id(self.id,
                                                           conn=db.get_conn())
                self.init_with_pipeline_config(res)
                ass = self.get_configpipe()
                if ass.nbOfChildren() > 0:
                    cas = ass.getChildren()[0]
                    self._current_configpipe = cas.getName()
        return self._current_configpipe

    def set_current_configpipe(self, confpipe_name):
        allconfpipename = self['PipelineConfig'].childNames()
        if confpipe_name in allconfpipename:
            self._current_configpipe = confpipe_name
        else:
            self._current_configpipe = ""

    def get_configpipe_obj(self, confpipe_name):
        if self['PipelineConfig'].has(confpipe_name):
            return self['PipelineConfig'][confpipe_name]
        return None

    def get_current_config_path(self, confpipe_name):
        obj = self.get_configpipe_obj(confpipe_name)
        if obj is None:
            return ""
        return obj.get_linux_path()
