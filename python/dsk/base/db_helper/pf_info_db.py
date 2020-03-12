import os
import re
from pprint import pformat

from dsk.base.tdata.gen_tree import GenTree

class PfInfoDb(GenTree):
    """Helper published file
    """
    PF = ["id",
          "image",
          "code",
          "entity",
          "task",
          "name",
          "published_file_type",
          "version",
          "downstream_published_files",
          "upstream_published_files",
          "path",
          "project",
          "version_number",
          "description",
          "sg_mg_asset",
          "sg_mg_sites",
          "sg_mg_is_latest",
          "sg_mg_source_path",
          "sg_status_list"]
    PFS = ["code",
           "name",
           "entity",
           "published_file_type",
           "downstream_published_files",
           "upstream_published_files",
           "version_number",
           "path",
           "description",
           "sg_status_list","created_at","image","task"]

    # to get version without full query of the depend (upstream and downstream)
    _pat_version = re.compile("\.v[\d]*\.")

    def __init__(self):
        super(PfInfoDb, self).__init__()
        self.reset()

    def reset(self):
        self.code = ""
        self.id = -1
        self.version_number = -1
        self.upstream_published_files = []
        self.downstream_published_files = []

    def setdata(self, arg):
        # we pop the image ref for readability
        #print arg
        if 'image' in arg:
            arg.pop('image')
        if 'version' in arg:
            arg.pop('version')
        if 'sg_mg_asset' in arg:
            arg.pop('sg_mg_asset')

        n = arg.get('code',None)
        if n != None:
            self.setName(n.replace(" ","_"))

        self.__dict__.update(arg)

        self.version_number = arg.get('version_number',"NoVersion")
        if self.version_number == None:
            self.version_number = "NoVersion"

        self.description = arg.get('description',"")
        if self.description == None:
            self.description = ""

        self.status = arg.get("sg_status_list","na")
        if self.status == None:
            self.status = 'na'
        return True

    def get_date_string(self):
        if 'created_at' in self.__dict__:
            return self.created_at.strftime("%Y-%m-%d %Hh%Mm%S")
        return ""

    def get_version(self):
        return self.version_number

    def get_all_versions(self):
        p_ver = self.getParent()
        if p_ver != None:
            return p_ver.getChildren()
        return list()

    def get_status(self):
        return self.status

    def set_status(self,sta):
        self.status = sta


    def get_file_local_path(self):
        return self.path['local_path']

    def get_file_name(self):
        return os.path.basename(self.get_file_local_path())

    def get_upstream_ids(self):
        return [x['id'] for x in self.upstream_published_files]

    def get_upstream_model(self):
        for x in self.upstream_published_files:
            if x['name'].startswith("model"):
                return x
        return None

    def _get_version_depend(self, filename):
            m = self._pat_version.search(filename)
            if m:
                return m.group()[2:-1]
            return None

    def get_upstream_model_version(self):
        for x in self.upstream_published_files:
            if x['name'].startswith("model"):
                return self._get_version_depend(x['name'])
        return None

    def get_upstream_cfx(self):
        for x in self.upstream_published_files:
            if x['name'].startswith("cfx"):
                return x
        return None

    def get_upstream_cfx_version(self):
        for x in self.upstream_published_files:
            if x['name'].startswith("cfx"):
                return self._get_version_depend(x['name'])
        return None

    def get_downstream_rig(self):
        for x in self.downstream_published_files:
            if x['name'].startswith("rig"):
                return x
        return None

    def get_downstream_rig_version(self):
        for x in self.downstream_published_files:
            if x['name'].startswith("rig"):
                return self._get_version_depend(x['name'])
        return None

    def get_downstream_shader(self):
        for x in self.downstream_published_files:
            if x['name'].startswith("shader"):
                return x
        return None

    def get_downstream_shader_version(self):
        for x in self.downstream_published_files:
            if x['name'].startswith("shader"):
                return self._get_version_depend(x['name'])
        return None

    def query_depend_fp(self, db, showobj, file_selected):
        from dsk.base.db_helper.db_helper_funct import ShotgunQuery as SQ

        result = None
        if db == None or showobj == None:
            return result

        for x in self.downstream_published_files:

            if x['name'] == file_selected:
                entity_publish_id = x['id']
                result = SQ.published_file_query_one(showobj.id,
                                                     entity_publish_id,
                                                     conn = db.get_conn())
                if len(result) == 1:
                    return result[0]
                return None

        for x in self.upstream_published_files:

            if x['name'] == file_selected:
                entity_publish_id = x['id']
                result = SQ.published_file_query_one(showobj.id,
                                                  entity_publish_id,
                                                  conn = db.get_conn())
                if len(result) == 1:
                    return result[0]
                return None

        return result

    def __repr__(self):
        #return "pft: %s " % self.getName() + "id = %(id)d, depends_on = %(depends_on)s, version_number = %(version_number)s" % self.__dict__
        #return "pft: %s " % self.getName() + "version_number = %(version_number)s" % self.__dict__
        return pformat(self.__dict__)
