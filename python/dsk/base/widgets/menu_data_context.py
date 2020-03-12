from dsk.base.tdata.gen_tree import GenTree
from dsk.base.utils.msg_utils import MsgUtils as log
from dsk.base.lib.msg_arg import MsgMenuContext

class BaseDataContext(GenTree):
    __widget = None
    @classmethod
    def setWidget(cls,widget):
        cls.__widget = widget
    @classmethod
    def getWidget(cls):
        return cls.__widget
        pass
    def updateFromData(self,data,window,item):
        # call on each action to update the state of
        # the action
        pass

class McSeparator(BaseDataContext):
    @staticmethod
    def isSep():
        return True
    def actionName(self):
        return "noAction"

class McDataContext(BaseDataContext):
    _delimiter = "-@@-"
    _unknown = "unknown"
    _fileList = list()
    _pathsearch = ""

    @staticmethod
    def isSep():
        return False

    @classmethod
    def cleanClassVar(cls):
        cls._fileList = list()
        cls._pathsearch = ""

    @classmethod
    def buildArgSep(cls,str1,str2):
        return "%s%s%s" % (str1,cls._delimiter,str2)

    @classmethod
    def getArgSep(cls,str1):
        return str1.split(cls._delimiter)

    @classmethod
    def unknown(cls):
        return cls._unknown

    def __init__(self,
                 name,
                 aformat="%s",
                 isSub=True,
                 actionName = None,
                 callback=None,
                 checkable=False):

        super(McDataContext, self).__init__()
        self.setName(name)

        self._subActionName = actionName
        self._format = aformat
        self._isSub = isSub

        self._callback = callback
        self._actionList = []
        self._unused = GenTree()

        # action supported
        self._checkAble = checkable
        self._check = True

    # checkability
    def ckeckable(self):
        return self._checkAble

    def setCheckable(self,val):
        self._checkAble = val

    def isChecked(self):
        return self._check

    def setCheck(self,val):
        self._check = val

    def buildDefaultKid(self):
        for mode in self._listMode:
            for tt in self._listType:
                k = "%s_%s" % (mode, tt)
                n = McDataContext(k, k, False,actionName=self.getSubActionName())
                self._unused.addChild(n)

    def actionName(self):
        return self.getName()

    def getSubActionName(self):
        if self._subActionName != None:
            return self._subActionName
        return self.getName()

    def setSubActionName(self,an):
        self._subActionName = an.replace(" ","")

    def actionTitle(self, aname):
        if self._format.find("%s") != -1:
            return self._format % aname
        return self._format

    def isSubmenu(self):
        return self._isSub

    def subAction(self):
        return self.getChildren()

    # to be overloaded
    def hasAction(self):
        if len(self._actionList) > 0:
            return True
        for c in self.subAction():
            if c.hasAction():
                return True
        return False

    def getActions(self):
        return self._actionList

    def setActionList(self, alist):
        self._actionList = alist

    def addActionList(self, alist):
        self._actionList.append(alist)

    def resetAction(self):
        self._actionList = []

    def _initialize(self):
        self.resetAction()
        for i in self.subAction():
            i._initialize()
        for chn in self.getChildren()[:]:
            self._unused.addChild(chn)
        #self.resetChildren()
        self.resetCache()

    # to be overload
    def initialize(self,assetName=None, apathname=None):
        if apathname == None:
            return list()
        self._initialize() # reset the child and the local action
        return McDataContext.updateSearch(apathname,self._listResolution, self._filterListExt)

    def execute(self,subAction, arg):
        msg = self.doIt(subAction,arg)
        if msg != None:
            if self._callback != None:
                self._callback(self,self.getName(),subAction, msg.getFilename())
        return msg

    def getAppSignal(self,signalName):
        return "%s(PyQt_PyObject)" % signalName

    # to be overload
    def doIt(self,subAction,arg):
        log.warning("in doit %s %s" % (subAction,arg))
        log.warning("doIt has to be overloaded for context %s" % self.getName())
        return None

##############################################################
class SimpleContext(McDataContext):
    def __init__(self,name,actionName=""):
        super(SimpleContext, self).__init__(name=name,
                                            aformat=name,
                                            isSub=False,
                                            actionName = actionName,
                                            callback=None)

    def initialize(self,aName=None, someExtra=None):
        aName = aName if aName != None else ""
        someExtra = someExtra if someExtra != None else ""
        self.setActionList([["%s" % (self.actionTitle(aName)),self.buildArgSep(aName,someExtra),True]])

    def doIt(self,subAction,arg):
        s = self.getArgSep(arg)
        assert len(s) == 2
        return MsgMenuContext(None,
                              apath=s[1],
                              applicationSignal=self.getAppSignal(self.getSubActionName()),
                              emitter=self,
                              abstractOption=s[0])

