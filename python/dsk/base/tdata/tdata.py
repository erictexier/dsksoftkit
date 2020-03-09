import types
import sys

from dsk.base.utils.msg_utils import MsgUtils
from dsk.base.tdata.type_helper import CashType
Name_Sep = ":"
SepPath = "/"

class Tdata(object):
    """ the task base definition """
    __slots__ = ["_Tdata__Name",
            "_Tdata__ModuleName",
            "_Tdata__Children",
            "_Tdata__Parent",
            "_Tdata__Value",
            "_Tdata__TypeValue"
            ]
    ##################
    def __init__(self):
        super(Tdata,self).__init__()
        self.__Name = "unknown"
        self.__ModuleName = self.__module__
        self.__Children = []
        self.__Parent = None
        self.__TypeValue = 'str'
        self.__Value = None

    #################
    @staticmethod
    def getSep():
        return SepPath

    ##################
    # identification stuff
    ##################
    def setName(self,name):
        # SepPath
        if name.find(SepPath) != -1:
            raise ValueError("cannot support %s in name " % SepPath) 
        self.__Name = str(name)

    def getName(self):
        return self.__Name

    def isNameSet(self):
        return self.__Name != "unknown"

    def rename(self,newName,findUnique=True):
        parent = self.getParent()
        if parent == None:
            self.setName(newName)
            return True
        # check if newName is a possible candidate
        for ch in parent.getChildren():
            if ch != self:
                if ch.getName() == newName:
                    if findUnique == False:
                        return False
                    chName = parent.findUniqueChildName(newName)
                    self.setName(chName)
                    return True
        self.setName(newName)
        return True

    # we want to allow user attribute to use name as a member
    #name = property(getName,setName,doc = "object name")

    ##################
    def getModuleName(self):
        return self.__ModuleName

    def setModuleName(self,modu):
        MsgUtils.warning("forcing module name %r to %r" % (self.__ModuleName,modu))
        self.__ModuleName = modu

    moduleName = property(getModuleName,setModuleName,doc="module to import")

    ##################
    def setValue(self,val,key=""):
        if type(key) == list:
            if len(key) > 0:
                kk = key[0]
                if hasattr(self,"__dict__"): 
                    if kk in self.__dict__:
                        self.__dict__[kk] = val
                        return 
                for ch in self.getChildren():
                    if kk == ch.getName():
                        ch.setValue(val,key[1:])
                        return
                MsgUtils.error("unknown key %r" % key)
            else:
                self.setValue(val)

        elif key != "":
            if hasattr(self,"__dict__"): 
                if key in self.__dict__:
                    self.__dict__[key] = val
                    return 
            path = Tdata.splitPath(key)
            if len(path) > 0:
                for ch in self.getChildren():
                    if path[0] == ch.getName():
                        ch.setValue(val,path[1:])
                        return
                MsgUtils.error("unknown key %r" % key)
            else:
                self.setValue(val)
        else:
            # temp code need works
            mvaltype = self.__TypeValue
            #ivaltype = type(val).__name__
            # need to be clean up before hack for now
            if isinstance(val,str):
                if val.find("'")!=-1:
                    val = val.replace("'","\"")
            if mvaltype in CashType:
                self.__Value = CashType[mvaltype](val)
            else:
                self.__Value = val # temporary

    def getValue(self,key = ""):
        if key != "":
            if hasattr(self,"__dict__"):
                if key in self.__dict__:
                    return self.__dict__[key]
            ch = self.find(key,True)
            if ch:
                return ch.getValue()
            else:
                pass

        return self.__Value

    # we want to allow user attribute to use value as a member
    ####value = property(getValue,setValue,doc = "default access value")

    ##################
    def hasValue(self):
        return self.__Value != None

    ##################
    def setTypeValue(self,val,key=""):
        self.__TypeValue = str(val)

    def getTypeValue(self,key = ""):
        return self.__TypeValue

    typevalue = property(getTypeValue,
            setTypeValue,doc = "default access mode of the value")

    ##################
    # parent/children stuff
    ##################
    def setParent(self,pparent):
        if self.getParent() != None:
            # tell the parent that we don't belong to him
            self.__Parent.removeChildFromList(self)
        self.__Parent = pparent

    def insulate(self):
        self.__Parent = None

    ##################
    def forceParent(self,pparent):
        self.__Parent = pparent

    ##################
    def getParent(self):
        return self.__Parent

    ##################
    def getChildren(self):
        return self.__Children
    ##################
    def getChildrenUi(self):
        return self.__Children
    ##################
    def getChildrenForXml(self):
        return self.__Children

    ##################
    def addChild(self,ch,withRename = False):
        # be sure that that it's valid child
        import traceback
        if isinstance(ch,Tdata):
            if ch in self.getChildren():
                return
            chname = self.findUniqueChildName(ch.getName())
            if withRename == True:
                # be sure that the child name is unique
                ch.setName(chname)
                self.__Children.append(ch)
            else:
                if chname != ch.getName():
                    # an object of the same name
                    # exist an need to be replace
                    childN = self.childNames()
                    try:
                        index = childN.index(ch.getName())
                        self.__Children.pop(index)
                        self.__Children.insert(index,ch)

                    except:
                        traceback.print_exc()
                        self.error("addChild","big Trouble in addChild")
                        sys.exit(1)
                else:
                    self.__Children.append(ch)

            ch.setParent(self)
        else:
            MsgUtils.warning("addChild","Can't add %s to my children List" % ch)

    ##################
    def insert(self, newChild, where):
        if not isinstance(newChild,Tdata):
            return False
        chname = newChild.getName()
        if not newChild in self.__Children:
            chname = self.findUniqueChildName(newChild.getName())
        else:
            # the where need to be adjusted if the kid get inserted after where it was
            index = self.__Children.index(newChild)
            if index == where:
                return True
            if index < where:
                where = where - 1
        newChild.setName(chname)
        newChild.setParent(self)
        self.__Children.insert(where,newChild)
        return True
    ################
    def resetChildren(self):
        # give a chance to do something at detach time
        while len(self.getChildren())> 0:
            ch = self.__Children[0]
            ch.remove()

    #################
    def removeChildFromList(self,ch):
        if ch in self.getChildren():
            self.__Children.remove(ch)

    #################
    def remove(self):
        if self.getParent() != None:
            self.getParent().removeChildFromList(self)
        del self

    ##################
    def nbOfChildren(self):
        return len(self.getChildren())

    ##################
    def childNames(self):
        """ return a list with all the children name
        """
        return [ch.getName() for ch in self.getChildren()]
        """
        childName = []
        for ch in self.getChildren():
            childName.append(ch.getName())
        return childName
        """
    ##################
    def findUniqueChildNameOLD(self,oldName):
        """ before adding a  child, be sure the name
        is unique or create a unique name
        """
        import string
        import traceback
        newName = oldName
        alist = self.getChildren()
        for i in alist:
            a = i.getName()
            if a  == oldName:
                b = a.split(Name_Sep)
                l = len(b)
                if l == 1:
                    # there is not : so just add :1
                    # 
                    newName = oldName + Name_Sep + "1"
                elif l >= 2:
                    try:
                        # try to increase :$ to :$+1
                        d = int(b[l-1])
                        d = d + 1
                        b[l-1] = str(d)
                        newName = string.joinfields(b,Name_Sep)
                    except: 
                        traceback.print_exc()
                        newName = oldName + Name_Sep + "1"
                # check again in case the new name was already there
                return  self.findUniqueChildName(newName)
        return newName
    ##################
    def findUniqueChildName(self,oldName,allNames = [],ref = 1):
        import random
        if allNames == []:
            allNames = self.childNames()
            ref = len(allNames)

        if oldName in allNames:
            newName = oldName + str(ref)
            if newName in allNames:
                return self.findUniqueChildName(oldName,allNames,ref*(1+int(random.random()*1000)))
            return newName
        else:
            return oldName

    ############################
    @staticmethod
    def splitPath(pathu):
        if type(pathu) in (str,):
            path =  pathu.split(SepPath)
        else:
            path = pathu

        assert type(path) == list
        return path

    ############################
    def find(self,pathu,justChild = False):
        """
        find(self,pathu,justChild)
        return an object with the right exact path
        pathu can be a string with sep or a list
        if justChild == True, skip the self test
        and pass it on to the kids
        """

        path = Tdata.splitPath(pathu)

        if len(path) > 0:
            if path[0] == "..":
                p = self.getParent()
                if p!= None:
                    return p.find(path[1:],justChild)
                return None

        if justChild == True:
            found = None
            for ch in self.getChildren():
                found = ch.find(path,False)
                if found != None:
                    break
            return found
        else:
            if len(path) == 1 and path[0] == self.getName():
                return self
            elif len(path) > 1 and path[0] == self.getName():
                found = None
                for ch in self.getChildren():
                    found = ch.find(path[1:],False)
                    if found != None:
                        break
                return found
        return None

    #############################
    def findAll(self,name,p = True):
        """
        findAll(self,name,p = True)
        find all node with this name
            
        if p = True, the path is added to the list
        else it s the object itself
        """
        localPath = []
        if self.getName() == name:
            if p:
                localPath.append(self.getPath())
            else:
                localPath.append(self)

        for ch in self.getChildren():
            path = ch.findAll(name,p)
            if path != []:
                localPath += path
        return localPath

    def findByRegex(self,reg,found):
        if reg.match(self.getName()):
            found.append(self)
        for ch in self.getChildren():
            ch.findByRegex(reg,found)

    ############################
    def getPath(self,sep=SepPath):
        """
        getPath(self) 
        return the path from the root
        """

        parent = self.getParent()
        if parent == None:
            return self.getName()
        pp = parent.getPath(sep)
        if pp != "":
            return  pp + SepPath + self.getName()
        else:
            return self.getName()

    ############################
    def getTop(self):
        """
        getTop(self) 
        return the last parent != None
        """
        parent = self.getParent()
        if parent == None:
            return self
        saveParent = parent
        while(parent != None):
            saveParent = parent
            parent = parent.getParent()
        return saveParent


    ##########################################
    ######### JSON
    ##########################
    @staticmethod
    def ReadAsJson(filename):
        from dsk.base.tdata import json_helper
        importer = json_helper.JsonHelper()
        d = importer.loads(filename)
        return importer.instanciate(d)
 
    ##########################
    def SaveAsJson(self,filename,basic = True,recursive=False,indent=1):
        # for now we have a limited suport the file generat
        from dsk.base.tdata import json_helper
        exporter = json_helper.JsonHelper()
        d = exporter.dumps(self,basic,recursive,indent=indent)
        return exporter.SaveJson(filename,d)

    def makePretty(self,basic=True,recursive=True,indent=4):
        from dsk.base.tdata import json_helper
        exporter = json_helper.JsonHelper()
        return exporter.dumps(self,basic,recursive,indent)


    ##########################################
    ######### XML
    ##################
    def buildDomDoc(self,rec):
        from dsk.base.tdata import container_xml
        exporter = container_xml.ContainerXml()
        exporter.startDomTree()
        exporter.constructDomTree(self,None,rec)
        return exporter

    ##################
    @staticmethod
    def ReadAsXml(filename,maxLevel = -1):
        from dsk.base.tdata import container_xml
        importer = container_xml.ContainerXml()
        return importer.importFromFile(filename,maxLevel)

    ##################
    def SaveAsXml(self,filename,recursive=True):
        """
        exports all the task as xml returns True on success, False otherwise; 
        optionally compresses with gzip
        """
        exporter = self.buildDomDoc(recursive)
        res = exporter.exportToFile(filename,True)
        return res

    ##################
    def Serialize(self,rec):
        exporter = self.buildDomDoc(rec)
        return exporter.serialize()

    ##################
    def Deserialize(self, astr):
        """
        return a xmlContainer
        """
        from dsk.base.tdata import container_xml
        importer = container_xml.ContainerXml()
        importer.deserialize(astr)
        return importer


    def toString(self,rec,atype="gc"):
        if atype == "gc":
            return self.Serialize(rec)
        return self.makePretty(basic=True,recursive=rec,indent=1)

    def fromString(self,astring,atype="gc"):
        if atype == "gc":
            top = self.Deserialize(astring)
            objList = top.load(-1)
            if len(objList) > 0:
                return objList[0]
            return None
        else:
            from dsk.base.tdata.json_helper import JsonHelper
            return JsonHelper.asDict(astring)

    ##################
    ## some xml support
    def getClassName(self):
        return self.__class__.__name__
    def getTypeName(self):
        """ a way to override """
        return self.__class__.__name__

    ##################
    ## some overload possible for xml
    ##
    ##################
    ## to use the attribute field, you can overload this function
    ## to get
    ## the attribute are save as 'key'='value', it's up to you to convert
    ## them
    ##################
    def loadStringAttribute(self,d):
        d['name'] = self.getName()
        if self.hasValue():
            d['typevalue'] = self.typevalue
            d['value'] = self.getValue()

    ##################
    def updateStringAttribute(self,d):
        if 'name' in d:
            self.setName(d['name'])
        if 'typevalue' in d:
            self.typevalue = d['typevalue']
        if 'value' in d:
            self.setValue(d['value'])

    ##################
    def getVariableMember(self,dd):
        if hasattr(self,"__dict__"):
            dd.update(self.__dict__)
    ##################
    def setVariableMember(self,dd):
        if hasattr(self,"__dict__"):
            self.__dict__.update(dd)


    ##################
    def hasInterface(self,nameFunc):
        if nameFunc in dir(self):
            b = eval("self.%s" % nameFunc)
            if type(b) == types.MethodType:
                return True
        return False

    ##################
    def getInterface(self,all = False):
        """ return all the method of an object """
        f = Tdata()
        d = []
        for foo in dir(self):
            b = eval("self.%s" % foo)
            if type(b) == types.MethodType:
                if all == True:
                    d.append({foo:b.__doc__})
                else:
                    if not f.hasInterface(foo):
                        d.append({foo:b.__doc__})

        return d

    ##################
    def printOutName(self,tt = ""):
        print((tt,self.getName()))
        newTab = tt + (" " * 5)
        for ch  in self.getChildren():
            ch.printOutName(newTab)




#### for default instanciation
### this class let you add any member
class container(Tdata):
    def __init__(self):
        super(container,self).__init__()

###########################################################
###########################################################
### this class let you add any member
class delegateValue(Tdata):
    __slots__ = "_delegateValue__Helper"
    def __init__(self):
        super(delegateValue,self).__init__()

################# default container ###################
class defaultContainer(Tdata):
    """ helper when an object is found multilple time in an
        xml document.
    """
    __slots__ = ["_defaultContainer__PathName"]
    def __init__(self):
        super(defaultContainer,self).__init__()

    def setPathName(self,name):
        self.__PathName = str(name)

    def getPathName(self):
        return self.__PathName

    pathname = property(getPathName,setPathName,doc = "needs a path")

    ##################
    def loadStringAttribute(self,d):
        Tdata.loadStringAttribute(self,d)
        d['pathname'] = self.pathname
        Tdata.loadStringAttribute(self,d)
    ##################
    def updateStringAttribute(self,d):
        Tdata.updateStringAttribute(self,d)
        if 'pathname' in d:
            self.pathname = d['pathname']
