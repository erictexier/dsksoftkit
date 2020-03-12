
from dsk.base.lib.signal_info import signalInfo
from dsk.base.widgets.simpleqt import QtT

if QtT.which == "PyQt5":
    SINGLE_ARG = 'PyQt_PyObject'
    DOUBLE_ARG = 'PyQt_PyObject,PyQt_PyObject'
    TRIPLE_ARG = 'PyQt_PyObject,PyQt_PyObject,PyQt_PyObject'
    QUATRE_ARG = 'PyQt_PyObject,PyQt_PyObject,PyQt_PyObject,PyQt_PyObject'
    CINQ_ARG = 'PyQt_PyObject,PyQt_PyObject,PyQt_PyObject,PyQt_PyObject,PyQt_PyObject'

elif QtT.which == "PySide2":
    SINGLE_ARG = 'object'
    DOUBLE_ARG = 'object,object'
    TRIPLE_ARG = 'object,object,object'
    QUATRE_ARG = 'object,object,object,object'
    CINQ_ARG = 'object,object,object,object,object'
else:
    raise ("Only implemented for PySide2 and PyQt5")
"""
if DO_PYSIDE2:
    SINGLE_ARG = 'QObject*'
    DOUBLE_ARG = 'QObject*,QObject*'
    TRIPLE_ARG = 'QObject*,QObject*,QObject*'
    QUATRE_ARG = 'QObject*,QObject*,QObject*,QObject*'
    CINQ_ARG = 'QObject*,QObject*,QObject*,QObject*,QObject*'
"""

INIT_FIRST_TIME = signalInfo('initFirstTime',SINGLE_ARG)
LOG_WRITE = signalInfo("logwrite",SINGLE_ARG)
OPTION_CHANGE = signalInfo('optionChange',SINGLE_ARG)
RICH_COLOR_CHANGE = signalInfo('richColor',SINGLE_ARG)

CHANGE_CURPATH = signalInfo('changeCurrentPath',SINGLE_ARG)
CHANGE_USERPROFILE = signalInfo('changeUserProfile',SINGLE_ARG)
CHANGE_CONTEXT_MENU = signalInfo('contextMenuAction',SINGLE_ARG)

CURRENTTASK_SIGNAL = signalInfo('selectMain',SINGLE_ARG)


CHANGE_SHOT = signalInfo('shotChange',SINGLE_ARG)
CHANGE_ASSET = signalInfo('assetChange',SINGLE_ARG)
CHANGE_SEQUENCE = signalInfo('sequenceChange',SINGLE_ARG)
CHANGE_SHOW = signalInfo('showChange',SINGLE_ARG)


CHANGE_STEP = signalInfo('stepChange',SINGLE_ARG)
CHANGE_PREF_STEP = signalInfo('prefStepChange',SINGLE_ARG)
CHANGE_ASSET_PREF_TYPE = signalInfo('assetTypePrefChange',SINGLE_ARG)

CHANGE_CONFIGPIPE  = signalInfo('configpipeChange',SINGLE_ARG)
CHANGE_PREF_CONFIGPIPE  = signalInfo('prefConfigpipeChange',SINGLE_ARG)

L_ATTR_LOCAL_SIGNAL =  signalInfo('attributeLocalChange',SINGLE_ARG)

COMMAND_SIGNAL = signalInfo('command',SINGLE_ARG)

######################### SIMPLE
# editing
ENABLE_SIGNAL = signalInfo('enableTask',SINGLE_ARG)
COPY_SIGNAL = signalInfo('copySubTree',SINGLE_ARG)
CUT_SIGNAL = signalInfo('deleteSubTree',SINGLE_ARG)
PASTE_SIGNAL = signalInfo('pasteSubTree',SINGLE_ARG)
CELLTREE_CHANGE = signalInfo('cellchangeTree',SINGLE_ARG)
XML_DROP_LIST = signalInfo('dropXmlList',SINGLE_ARG)
SELECTION_ITEM_CHANGE = signalInfo('aselectchange',SINGLE_ARG)
# drag and drop
DROP_SIGNAL = signalInfo('dropMain',SINGLE_ARG)
RENAME_SIGNAL = signalInfo('renameMain',SINGLE_ARG)

CHECKED_ALL_SIGNAL = signalInfo('selectAllTest',SINGLE_ARG)
# new task
ADDNEWTASK_SIGNAL = signalInfo('addNewTask',SINGLE_ARG)
