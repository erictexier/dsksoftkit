import os
import traceback
import types
import gzip
from dsk.base.utils.msg_utils import MsgUtils
from dsk.base.utils.disk_utils import DiskUtils
from dsk.base.tdata import tdata

JSON = ""

import json as JSON


if JSON == "":
    print("CANNOT FIND JSON MODULE")

class JsonHelper(object):
    _KEY = "+"
    _CHKEY = _KEY + 'ch'
    _CLASSKEY = _KEY  + "c"
    _MODULEKEY = _KEY  + "m"
    _PROPKEY = _KEY  + "p"
    _NAMEKEY = _KEY  + "n"
    _VALKEY = _KEY  + "v"
    _VALTYPEKEY = _KEY  + "t"

    #################
    def isGz(self,filename):
        return os.path.splitext(filename)[1] == ".gz" 

    ##################
    def OpenFileGz(self, afile, mode = "r"):
        fFile = None
        if mode == "r":
            try:
                fFile = gzip.open(afile, "rb")
            except IOError:
                    # can't read the file
                    MsgUtils.error("Can't read %r" % afile)
                    fFile = None
        else: ## for write
                try:
                    fFile = gzip.open(afile, "wb")
                except IOError:
                    MsgUtils.error("Can't read %r" % afile)
                    fFile = None
        return fFile

    ##################
    def OpenFile(self, afile,mode = "r"):
        try:
            fFile = open(afile,mode)
        except:
            MsgUtils.error("Can't open %r" % afile)
            fFile = None

        return fFile

    ##################
    def SaveJson(self, fileName, d):
        f = None
        if self.isGz(fileName) == True:
            f = self.OpenFileGz(fileName,"w")
        else:
            f = self.OpenFile(fileName,"w")
        if f != 0:
            f.write(d)
            f.close()
        return True
 
    ##################
    def loads(self, fileName):
        d = {}
        if self.isGz(fileName) == True:
            f = self.OpenFileGz(fileName,"r")
            if f != 0:
                astr = f.read()
                d = JSON.loads(astr)
                f.close()
                return d
        else:
            if DiskUtils.is_file_exist(fileName):
                try:
                    f = self.OpenFile(fileName,'r')
                    astr = f.read()
                    f.close()
                    d = JSON.loads(astr)
                except:
                    return d
            else:
                return d
            return d
        return d

    @staticmethod
    def asDict(astr):
        return JSON.loads(astr)

    ##########
    def instanciate(self,d):
        if (JsonHelper._CLASSKEY not in d or 
            JsonHelper._MODULEKEY not in d):
            # this is a basic dict
            return d

        # create an instance
        aclass = d[JsonHelper._CLASSKEY]
        amodule = d[JsonHelper._MODULEKEY]

        if (amodule != '__builtin__'):
            cmd = "import %s" % amodule
            try:
                exec(cmd)
            except:
                traceback.print_exc()
                MsgUtils.warning("cannot import %r" % amodule)
                MsgUtils.msg("Creating a generic class container")
                amodule = "tdata"
                aclass = "container"

        cmd = "%s.%s()" % (amodule,aclass)
        newInstance = None
        try:
            newInstance = eval(cmd)
        except:
            traceback.print_exc()
            MsgUtils.error("COMMAND %r" % cmd)
            MsgUtils.msg("class definition %r not found in %r" % (aclass,amodule))
            assert newInstance != None

        # name value and typevalue
        if JsonHelper._NAMEKEY in d:
            newInstance.setName(d[JsonHelper._NAMEKEY])

        if JsonHelper._VALTYPEKEY in d:
            newInstance.setTypeValue(d[JsonHelper._VALTYPEKEY])

        if JsonHelper._VALKEY in d:
            newInstance.setValue(d[JsonHelper._VALKEY])
        if JsonHelper._PROPKEY in d:
            newInstance.setVariableMember(d[JsonHelper._PROPKEY])


        if JsonHelper._CHKEY in d:
            assert type(d[JsonHelper._CHKEY]) == dict
            for k,vn in list(d[JsonHelper._CHKEY].items()):
                chInstance = self.instanciate(vn)
                if JsonHelper.isContainerClass(chInstance):
                    chInstance.setName(str(k))
                    newInstance.addChild(chInstance,False)
                else:
                    MsgUtils.error("trouble reading %r" % type(chInstance))
        return newInstance

    #################
    @staticmethod
    def isContainerClass(ob):
        return isinstance(ob,tdata.Tdata)

    ##################
    @staticmethod
    def buildChildrenDict(myTask,theDict):
        if JsonHelper.isContainerClass(myTask):
            d = {JsonHelper._CLASSKEY:myTask.getClassName(),
                 JsonHelper._MODULEKEY:myTask.getModuleName()}
            simpleD = dict()
            myTask.loadStringAttribute(simpleD)
            for key,value in list(simpleD.items()):
                # here we don't save the key name since it's a child and
                # the parent know the name already
                if key !=  'name':
                    d[JsonHelper._KEY + key[0]] = value

            for ch in myTask.getChildrenForXml():
                if not (JsonHelper._CHKEY) in d:
                    d[JsonHelper._CHKEY] = dict()
                d[JsonHelper._CHKEY][ch.getName()] = dict()
                JsonHelper.buildChildrenDict(ch,d[JsonHelper._CHKEY][ch.getName()])
            theDict.update(d)
            dd = dict()
            myTask.getVariableMember(dd) # ask the class for what it need to save
            theDict[JsonHelper._PROPKEY] = dd

    ##################
    @staticmethod
    def buildDict(myTask,theDict):
        if JsonHelper.isContainerClass(myTask):
            dd = dict()
            myTask.getVariableMember(dd) # ask the class for what it need to save
            for ch in myTask.getChildrenForXml():
                JsonHelper.buildDict(ch,dd)
            theDict[myTask.getName()] = dd
        else:
            MsgUtils.error("canno't builddict on this object")

    ##################
    @staticmethod
    def dumps(myTask,basic,rec,indent=1):
        if JsonHelper.isContainerClass(myTask):
            if basic==True:
                dd = dict()
                myTask.getVariableMember(dd) # ask the class for what it need to save

                if rec == True:
                    for ch in myTask.getChildrenForXml():
                        JsonHelper.buildDict(ch,dd)

                return JSON.dumps(dd,indent=indent)

            else:
                d = {JsonHelper._CLASSKEY:myTask.getClassName(),
                     JsonHelper._MODULEKEY:myTask.getModuleName()}

                simpleD = dict()
                myTask.loadStringAttribute(simpleD)

                # rename the key to be consistance to the + convention

                for key,value in list(simpleD.items()):
                    d[JsonHelper._KEY + key[0]] = value

                dd = dict()
                myTask.getVariableMember(dd) # ask the class for what it need to save
                d[JsonHelper._PROPKEY] = dd
                if rec == True:
                    for ch in myTask.getChildrenForXml():
                        if not (JsonHelper._CHKEY) in d:
                            d[JsonHelper._CHKEY] = dict()
                        d[JsonHelper._CHKEY][ch.getName()] = dict()
                        JsonHelper.buildChildrenDict(ch,d[JsonHelper._CHKEY][ch.getName()])

                return JSON.dumps(d,indent=indent)

        else:
            if hasattr(myTask,"__dict__"):
                return JSON.dumps(myTask.__dict__,indent=4)
        return JSON.dumps(dict())

