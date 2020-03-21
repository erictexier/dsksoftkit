# -*- coding: utf-8 -*-
"""Package message into object to avoid multiplication of argument
"""

import pprint
import types

class MsgArg(object):
    def __init__(self, widgetFrom, group):
        """Base Msg

            :param widfrom:  widget that initial the msg, can be None
            :param grp:  the current group, can be None

        """
        super(MsgArg,self).__init__()
        self._widgetFrom = widgetFrom
        self._currentGroup = group
        self._success = False
        self._editor = None
    def setGroup(self, group):
        self._currentGroup = group
    def getGroup(self):
        return self._currentGroup
    def widgetFrom(self):
        return self._widgetFrom
    def setWidgetFrom(self, wid):
        self._widgetFrom = wid
    def setSuccess(self, val):
        self._success = val
    def getEditor(self):
        return self._editor
    def setEditor(self, editor):
        self._editor = editor
    def succeed(self):
        return self._success
    def __repr__(self):
        return pprint.pformat(self.__dict__, indent=1) +
                  "\nmsg type: " + self.__class__.__name__

class MsgFirstTime(MsgArg):
    def __init__(self,widgetFrom,group=None,first=False):
        super(MsgFirstTime,self).__init__(widgetFrom, group)
        self._pref = None
        self._isAppLevel = first
    def isAppLevel(self):
        return self._isAppLevel
    def setPref(self,pref):
        self._pref = pref
    def getPref(self):
        return self._pref

class MsgCommand(MsgArg):
    def __init__(self, widgetFrom, cmd, data, extra="", group=None):
        super(MsgCommand,self).__init__(widgetFrom, group)
        self._cmd = cmd
        self._data = data
        self._extra = extra
        self._itemslist = None
        self._destinationPath = ""
        self._reselect = None
    def getCommand(self):
        return self._cmd
    def getData(self):
        return self._data
    def setData(self,data):
        self._data = data
    def get_extra(self):
        return self._extra
    def setItems(self,il):
        self._itemslist = il
    def getItems(self):
        return self._itemslist
    def getWhere(self):
        return self._destinationPath
    def setWhere(self,apath):
        self._destinationPath = apath

    def set_reselect(self,apath):
        # a path to reselect
        self._reselect = apath
    def reselect(self):
        return self._reselect

class MsgShowChange(MsgArg):
    def __init__(self, widgetFrom, group, showname):
        super(MsgShowChange,self).__init__(widgetFrom, group)
        self.showname = showname
    def getShowName(self):
        return self.showname

class MsgSeqChange(MsgArg):
    def __init__(self,widgetFrom,group,seqname):
        super(MsgSeqChange,self).__init__(widgetFrom, group)
        self.seqname = seqname
    def getSeqName(self):
        return self.seqname

class MsgShotChange(MsgArg):
    def __init__(self, widgetFrom, group, shotname):
        super(MsgShotChange,self).__init__(widgetFrom, group)
        self.shotname = shotname
    def getShotName(self):
        return self.shotname

class MsgAssetChange(MsgArg):
    def __init__(self, widgetFrom, group, assetname):
        super(MsgAssetChange,self).__init__(widgetFrom, group)
        self.assetname = assetname
    def getAssetName(self):
        return self.shotname

class MsgAssetTypeChange(MsgArg):
    def __init__(self, widgetFrom, group, dict_changed):
        super(MsgAssetTypeChange,self).__init__(widgetFrom, group)
        self.dict_changed = dict_changed
    def get_assettype_change(self):
        return self.dict_changed

class MsgStepChange(MsgArg):
    def __init__(self, widgetFrom, group, stepname):
        super(MsgStepChange,self).__init__(widgetFrom, group)
        self.stepname = stepname
    def getStepName(self):
        return self.stepname

class MsgStepFilterChange(MsgArg):
    def __init__(self, widgetFrom, group, dict_changed):
        super(MsgStepFilterChange,self).__init__(widgetFrom, group)
        self.dict_changed = dict_changed
    def get_stepfilter_change(self):
        return self.dict_changed

class MsgConfigpipeChange(MsgArg):
    def __init__(self, widgetFrom, group, configpipe, configpath=None):
        super(MsgConfigpipeChange,self).__init__(widgetFrom, group)
        self.configpipe = configpipe
        self.configpath = configpath
    def getConfigpipeName(self):
        return self.configpipe
    def getConfigpipePath(self):
        return self.configpath
    def setConfigpipePath(self, configpath):
        self.configpath = configpath


class MsgConfigpipeFilterChange(MsgArg):
    def __init__(self, widgetFrom, group, dict_changed):
        super(MsgConfigpipeFilterChange,self).__init__(widgetFrom, group)
        self.dict_changed = dict_changed
    def get_configpipefilter_change(self):
        return self.dict_changed


class MsgSelectChange(MsgArg):
    def __init__(self, widgetFrom=None, currentPath=None, emitter=None):
        super(MsgSelectChange,self).__init__(widgetFrom, None)
        self._currentPath =  currentPath
        self._emitter = emitter  # an optional emitter
        self._currentNode = None
        self._hasMaya = False
    def getCurrentPath(self):
        return self._currentPath
    def setCurrentPath(self, pathlist):
        self._currentPath = pathlist
    def setCurrentNode(self,node):
        self._currentNode = node
    def getCurrentNode(self):
        return self._currentNode
    def hasMaya(self):
        return self._hasMaya
    def setHasMaya(self, value):
        self._hasMaya = value

class MsgMenuContext(MsgArg):
    def __init__(self,
                 widgetFrom=None,
                 apath=None,
                 applicationSignal="",
                 package=None,
                 emitter=None,
                 abstractOption=None):

        super(MsgMenuContext,self).__init__(widgetFrom, None)
        self._fileOrPath = apath
        self._applicationSignal = applicationSignal
        self._userInfo = None
        self._package = package  # an optionalPackage
        self._emitter = emitter  # an optional emitter
        self._ABoptions = abstractOption
        self._serialisedData = None

    def setFilename(self, afile):
        self._fileOrPath = afile
    def getFilename(self):
        return self._fileOrPath
    def getPath(self):
        return self._fileOrPath
    def getPathList(self):
        if type(self._fileOrPath) == types.ListType:
            return self._fileOrPath
        else:
            return [self._fileOrPath]

    def getApplicationSignal(self):
        return self._applicationSignal
    def setUserInfo(self, userinfoObjet):
        self._userInfo = userinfoObjet
    def getUserInfo(self):
        return self._userInfo
    def getPackageName(self):
        return self._package
    def setPackageName(self, package):
        self._package = package
    def getOptions(self):
        return self._ABoptions
    def setOptions(self,oo):
        self._ABoptions = oo
    def setSerialized(self,data):
        self._serialisedData = data
    def getSerialized(self):
        return self._serialisedData
        # warning: the type of this is arbitrary
    def pathToRemove(self):
        return self._pathToRemove
    def setPathToRemove(self, listOfPath):
        self._pathToRemove = listOfPath


class MsgNameChange(MsgArg):
    def __init__(self,
                 widgetFrom=None,
                 item=None, path=None, newName=None, which=0):
        super(MsgNameChange,self).__init__(widgetFrom,None)
        self._item = item
        self._path = path
        self._proposedName = newName
        self._which = which
    def getPath(self):
        return self._path
    def getProposedName(self):
        return self._proposedName
    def setProposedName(self, aname):
        self._proposedName = aname
    def getWhich(self):
        return self._which
    def getItem(self):
        return self._item


class MsgDragDrop(MsgArg):
    def __init__(self,
                 widgetFrom=None,
                 actionType="MOVE",
                 listOfSerializeData=None,
                 destinationPath=None,
                 pos=-1,
                 widgetSourceName=""):
        super(MsgDragDrop,self).__init__(widgetFrom, None)
        self._actionType = actionType
        self._serialisedData = listOfSerializeData
        self._destinationPath = destinationPath
        self._pos = pos
        self._widgetSourceName = widgetSourceName
        self._pathToRemove = None
    def getAction(self):
        return self._actionType
    def getSerialized(self):
        return self._serialisedData
    def getPos(self):
        return self._pos
    def setPos(self,pos):
        self._pos = pos
    def getWhere(self):
        return self._destinationPath
    def setWhere(self,apath):
        self._destinationPath = apath
    def getWidgetName(self):
        return self._widgetSourceName
    def pathToRemove(self):
        return self._pathToRemove
    def setPathToRemove(self,listOfPath):
        self._pathToRemove = listOfPath


class MsgArgTimeChange(MsgArg):
    def __init__(self,
                 widgetFrom,
                 group,
                 nodeTime,
                 time, doEvaluate, doAllDirty):
        super(MsgArgTimeChange,self).__init__(widgetFrom,group)
        self.nodeTime = nodeTime
        self.time = time
        self.doEvaluate = doEvaluate
        self.doAllDirty = doAllDirty


class MsgArgAttributeChange(MsgArg):
    def __init__(self, widgetFrom, group, currentNode, objAttr):
        super(MsgArgAttributeChange,self).__init__(widgetFrom, group)
        self.currentNode = currentNode
        self.attrib = objAttr


class MsgArgConnection(MsgArg):
    def __init__(self,
                 widgetFrom,
                 group,
                 fromName,
                 toName,
                 fromOutput,
                 toInput):
        super(MsgArgConnection,self).__init__(widgetFrom, group)
        self.fromName = fromName
        self.toName = toName
        self.fromOutput = fromOutput
        self.toInput = toInput


class MsgArgGrid(MsgArg):
    def __init__(self,
                 widgetFrom,
                 group,
                 xmin, ymin, xsize, ysize, xunit, yunit):
        super(MsgArgGrid,self).__init__(widgetFrom,group)
        self.xmin = xmin
        self.ymin = ymin
        self.xsize = xsize
        self.ysize= ysize
        self.xunit = xunit
        self.yunit = yunit


class MsgArgDirty(MsgArg):
    def __init__(self, widgetFrom, group, doEvaluate, doChangeTime):
        super(MsgArgDirty,self).__init__(widgetFrom, group)
        self.doEvaluate = doEvaluate
        self.doChangeTime = doChangeTime


class MsgArgPlugRename(MsgArg):
    def __init__(self, widgetFrom, group, fromName, isIn, nbPlug, oldName):
        super(MsgArgPlugRename,self).__init__(widgetFrom, group)
        self.fromName = fromName
        self.isIn = isIn
        self.nbPlug = nbPlug
        self.oldName = oldName
        self.theNewName = ""


class MsgArgCreateNode(MsgArg):
    def __init__(self,
                 widgetFrom,
                 group,
                 nodeModule,
                 nodeName,
                 nodeType):
        super(MsgArgCreateNode,self).__init__(widgetFrom, group)
        self.nodeModule = nodeModule
        self.nodeName = nodeName
        self.nodeType = nodeType


