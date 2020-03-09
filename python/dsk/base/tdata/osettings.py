import types

from dsk.base.tdata.tdata import Tdata
from dsk.base.tdata.tdata import SepPath
from dsk.base.utils.msg_utils import MsgUtils

class OSettings(Tdata):
    __slots__ =  [  "_OSettings__Group",
             ]
    def __init__(self):
        super(OSettings,self).__init__()
        self.reset()

    def reset(self):
        """ reset the group pointer
        """
        self.__Group = []

    ##################
    def setValue(self,val,key=""):
        current = self.group()
        if current:
            current.setValue(val,key)
        else:
            Tdata.setValue(self,val,key)

    def getValue(self,key = ""):
        current = self.group()
        if current:
            return current.getValue(key)
        else:
            return Tdata.getValue(self,key)

    value = property(getValue,setValue,doc = "overload value access")

    ############################
    def getPath(self,sep="/"):
        """ getPath(self) 
            return the path from the root
        """
        MsgUtils.error("child none insulated, see addChid")
        raise


    ##################
    def addChild(self,ch,withRename = False):
        super(OSettings,self).addChild(ch,withRename)
        ch.insulate()


    ##################
    def beginGroup(self,prefix):
        """ 
        beginGroup(self,prefix) return False
        if the relativeprefix in not found
        """
        if len(prefix) == 0:
            return False

        key = self.group()
        obj = None
        if key != None:
            obj = key.find(prefix,True)
        else:
            obj = self.find(prefix,True)
        if obj != None:
            self.__Group.append(obj)
            return True

        return False

    ##################
    def endGroup(self):
        """ pop out one level up in the group
        """
        if len(self.__Group) > 0:
            self.__Group.pop(-1)

    ##################
    def group(self):
        if len(self.__Group) > 0:
            return self.__Group[-1]
        return None

    ##################
    def childGroups(self):
        key = self.group()
        if key != None:
            return key.childNames()

        return self.childNames()

    def open(self,apath):
        route = apath.split(SepPath)
        self.reset()
        return self.openAt(route)

    def close(self):
        self.reset()

    def openAt(self,route):
        if len(route) == 0:
            return True
        f = route[0]
        res = False
        for group in self.childGroups():
            if group == f:
                self.beginGroup(group)
                res = self.openAt(route[1:])
                return res
        return res

    ##################
    def dictKeys(self):
        key = self.group()
        dd = {}
        if key != None:
            key.getVariableMember(dd)
        else:
            self.getVariableMember(dd)
        return list(dd.keys())

    ##################
    def allKeys(self):
        key = self.group()
        dd = {}
        chName = []
        if key != None:
            key.getVariableMember(dd)
            chName = key.childNames()
        else:
            self.getVariableMember(dd)
            chName = self.childNames()

        return list(dd.keys()) + chName

    ##################
    def contains(self,key):
        print("contains not Done")
        return False

 
    ####
    def __getitem__(self, item):
        assert type(item) == bytes
        if len(item) > 0 and item[0] == SepPath: 
            return self.getValue(item[1:])
        else:
            return self.getValue(item)

        ####
    def __setitem__(self, item,val):
        assert type(item) == bytes
        if len(item) > 0 and item[0] == SepPath: 
            self.setValue(val,item[1:])
        else:
            self.setValue(val,item)


#################################################################
#################################################################
# for testing only
def createADummySetting():
    import random
    random.seed(0)

    s = OSettings()
    s.setName("ROOT")

    #########################
    # build on the fly
    #########################
    from dsk.base.tdata.tdata import container
    a = container()
    a.setName("Main")
    s.addChild(a)

    for i in range(4):
        b = container()
        b.setName("CHI_%s" % i)
        rr = int(random.random() * 10)
        for j in range(rr):
            c = container()
            c.setName("rand_%s" % j)
            c.setTypeValue("float")
            c.setValue(rr)
            b.addChild(c)
        a.addChild(b)
    cg = s.childGroups()

    for i in cg:
        s.beginGroup(i)
        chg = s.childGroups()
        for j in chg:
            s.beginGroup(j)
            chg2 = s.childGroups()
            coo = 0
            for k in chg2:
                if coo % 2:
                    s.setValue(s.getValue(k) * 2,k)
                coo += 1
            s.endGroup()
        s.endGroup()

    s.setValue(10000.,"Main/CHI_2/rand_3")
    return s

if __name__ == "__main__":
    s = createADummySetting()
    s.setModuleName("dsk.base.tdata.osettings")
    s.SaveAsXml("forFun.xml")
    print(s['/Main/CHI_2/rand_3'])
    s['/Main/CHI_2/rand_3'] = s['/Main/CHI_2/rand_3']/10
    print(s['/Main/CHI_2/rand_3'])
    print(s.ReadAsXml("forFun2.xml")) 
