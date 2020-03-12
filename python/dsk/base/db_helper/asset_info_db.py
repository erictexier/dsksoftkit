
from dsk.base.db_helper.basemedia_info_db import BaseMediaInfoDb


class AssetInfoDb(BaseMediaInfoDb):
    """ helper for asset query db
    """

    AllAssetType = ['Creature','Character','Prop','Setup','Environment']

    @staticmethod
    def compare(a,b):
        return cmp(a.getName(), b.getName())
    def __init__(self):
        super(AssetInfoDb, self).__init__()
        self.reset()

    def reset(self):
        super(AssetInfoDb, self).reset()
        self.id = -1
        self.asset_type = ""
        self.status  = 'na'

    def get_asset_type(self):
        return self.asset_type

    def get_code(self):
        return "%s_%s" % (self.asset_type, self.getName())

    def setdata(self,idi,asset_type="Asset",status='wtg'):
        "Asset type can be generic as Asset, or more specific as Prop, Creature"
        self.id = idi
        self.asset_type = asset_type
        self.status = status
        if status == "":
            self.status = 'wtg'
        return True

    def __repr__(self):
        return "asset: %s " % self.getName() + "id = %(id)d, type = %(asset_type)s, %(status)s" % self.__dict__

