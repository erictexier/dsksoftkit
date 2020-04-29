from collections import OrderedDict
from collections import namedtuple

class dynamic_map(object):
    #def __init__(self):
    #    self.active = False
    def is_active(self):
        if hasattr("active",self): return self.active
        return False

class MappingTank(namedtuple('msgtk', "short_name label upstream downstream"),dynamic_map):
    __slots__ = ()


globalType = OrderedDict()

typeListShot = OrderedDict()
typeListShot['M_ANIM-SRC_SF'] = MappingTank('maya_anim_src_file','Anim src',[],[])
typeListShot['M_ANIM_F'] = MappingTank('maya_anim_file','Anim',[],[])
typeListShot['G_ALEMBIC_C'] = MappingTank('alembic_cache','Alembic',[],[])
typeListShot['M_CAMERA_SF'] = MappingTank('maya_camera_src_file','camera',[],[])
typeListShot['M_TRACK-ABC_F'] = MappingTank('maya_track_abc','Abc track',[],[])
typeListShot['M_TRACK-SRC_SF'] = MappingTank('maya_track_src_file','Maya track',[],[])
typeListShot['M_PLAYBLAST_MV'] = MappingTank('maya_playblast_movie','Maya playblast',[],[])

typeListAsset = OrderedDict()
typeListAsset['M_SHADER_SF'] = MappingTank('maya_shader_src_file','Shader src',[],[])
typeListAsset['M_RIG_SF'] = MappingTank('maya_rig_src_file','Rig src',[],[])
typeListAsset['M_MODEL_SF'] = MappingTank('maya_model_src_file','Model src',[],[])
typeListAsset['M_CFX-SRC_SF'] = MappingTank('maya_cfx_src_file','Cfx src',[],[])


typeListShotVersion = OrderedDict()
typeListAssetVersion = OrderedDict()
typeListShotVersion['PLAYBLAST_MEDIA'] = MappingTank('playblast','Playblast version',[],[])
typeListShotVersion['M_DEADLINE_RENDER_MEDIA'] = MappingTank('deadlineMayaRender','Farm deadLine maya',[],[])
typeListShotVersion['N_DEADLINE_RENDER_MEDIA'] = MappingTank('deadlineNukeRender','Farm deadLine Nuke',[],[])
typeListShotVersion['M_PUBLISHED_RENDER_MEDIA'] = MappingTank('publishedMayaRender','Published render maya',[],[])
typeListShotVersion['N_PUBLISHED_RENDER_MEDIA'] = MappingTank('publishedNukeRender','Published render Nuke',[],[])
typeListShotVersion['DELIVERY'] = MappingTank('delivery','Delivery',[],[])
##### publish type
typeList = dict()
typeList['Shot'] = typeListShot
typeList['Asset'] = typeListAsset

GlobalMap = dict()
GlobalMap['dev_show'] = typeList

###### version
typeListVersion = dict()
typeListVersion['Shot'] = typeListShotVersion
typeListVersion['Asset'] = typeListAssetVersion

GlobalMapVersion = dict()
GlobalMapVersion['dev_show'] = typeListVersion

def getAssetMapping(showname):
    if showname in GlobalMap:
        return GlobalMap[showname]['Asset']
    return typeList['Asset']

def getShotMapping(showname):
    if showname in GlobalMap:
        return GlobalMap[showname]['Shot']
    return typeList['Shot']

def getShotVersionMapping(showname):
    if showname in GlobalMapVersion:
        return GlobalMapVersion[showname]['Shot']
    return typeListVersion['Shot']

def getAssetVersionMapping(showname):
    if showname in GlobalMapVersion:
        return GlobalMapVersion[showname]['Asset']
    return typeListVersion['Asset']

