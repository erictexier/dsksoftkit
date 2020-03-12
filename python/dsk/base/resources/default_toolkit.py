from collections import OrderedDict

from dsk.base.lib.add_on import AddOn

from dsk.base.resources import browser_constant as BK
simpleVis = OrderedDict()
simpleVis[BK.ST_VISIBLE] = [False,"Toggle Visibility",False]


# some utils function to load specific tool
def addLog(mm,objectName="logger"): # an Ordered dict and a name
    b = AddOn(objectName,"LogWidget", "widgets" , "log_widget", "B", True, simpleVis, None, None)
    mm[b.wid_class] = b
def addTumbnail(mm,objectName="thumbnail"): # an Ordered dict and a name
    b = AddOn(objectName,"ThumbnailWidget", "widgets" , "thumbnail_widget", "R", True, simpleVis, None, None)
    mm[b.wid_class] = b


def addSequenceSelect(mm,objectName="sequence_select"): # an Ordered dict and a name
    b = AddOn(objectName,"SequenceSeclectWidget", "widgets" , "sequence_select_widget", "R", True, simpleVis, None, None)
    mm[b.wid_class] = b

def addEnvDisplay(mm,objectName="env_display"): # an Ordered dict and a name
    b = AddOn(objectName,"EnvVariableWidget", "widgets" , "env_variable_widget", "R", True, simpleVis, None, None)
    mm[b.wid_class] = b


def getDefaultToolsKit():
    mm = OrderedDict()
    addTumbnail(mm,"thumbnail")
    addEnvDisplay(mm,"envdisplay")

    addLog(mm,'logger')
    return mm