import os
from dskenv.base_env import BaseEnv

raise "NO DONE"

class ProxyShow(object):
    ''' helper to find out couple area not necessary the current show
    '''
    __realbase = os.path.realpath(BaseEnv.studio_root())

    @classmethod
    def usep(cls,apath):
        return apath.replace(r'\\\\','/').replace('\\','/')

    def __init__(self,showname):
        self.show_name = showname
        self.project_path = ProxyShow.usep(os.path.join(BaseEnv.studio_root(), self.show_name))

    def get_project_path(self):
        return self.project_path

    def get_normal_path(self, apath):
        '''
        to convert from real to normalized path

        returns:
            norm path
        '''
        apath = apath.replace(ProxyShow.__realbase,BaseEnv.studio_root())
        return apath

    def get_prod_area(self):
        return ProxyShow.usep(os.path.join(self.project_path,BaseEnv.MAIN_PROD))

    def get_publish_area(self):
        return ProxyShow.usep(os.path.join(self.project_path, BaseEnv.MAIN_PUBLISH))

    def get_asset_prod_area(self,atype = ""):
        if atype == "":
            return ProxyShow.usep(os.path.join(self.get_prod_area(), BaseEnv.MAIN_ASSET))
        assert atype in BaseEnv.get_asset_type()
        return ProxyShow.usep(os.path.join(os.path.join(self.get_prod_area(),BaseEnv.MAIN_ASSET,atype)))

    def get_asset_publish_area(self,atype = ""):
        if atype == "":
            return ProxyShow.usep(os.path.join(self.get_publish_area(), BaseEnv.MAIN_ASSET))
        assert atype in BaseEnv.get_asset_publish_type()
        return ProxyShow.usep(os.path.join(self.get_publish_area(), BaseEnv.MAIN_ASSET, atype))

    def get_shot_prod_area(self, sequence = ""):
        if sequence == "":
            return os.path.join(self.get_prod_area(), BaseEnv.MAIN_SHOT)
        return os.path.join(self.get_prod_area(), BaseEnv.MAIN_SHOT, sequence)

    def get_shot_publish_area(self,sequence = ""):
        if sequence == "":
            return ProxyShow.usep(os.path.join(self.get_publish_area(), BaseEnv.MAIN_SHOT))
        return ProxyShow.usep(os.path.join(self.get_publish_area(), BaseEnv.MAIN_SHOT,sequence))

    def get_shot_publish_thumbcache_area(self):
        return ProxyShow.usep(os.path.join(self.get_publish_area(), BaseEnv.THUMBCACH,BaseEnv.THUMB_SHOT))

    def get_asset_publish_thumbcache_area(self):
        return ProxyShow.usep(os.path.join(self.get_publish_area(), BaseEnv.THUMBCACH,BaseEnv.THUMB_ASSET))