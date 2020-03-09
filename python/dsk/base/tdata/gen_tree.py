import types

from dsk.base.tdata.tdata import Tdata
from dsk.base.utils.msg_utils import MsgUtils as log

class GenTree(Tdata):
    __slots__ = ["_GenTree__Cache"]
    def __init__(self):
        super(GenTree,self).__init__()
        self.__Cache = {}

    def has(self,aname):
        if len(self.__Cache) != self.nbOfChildren():
            self.cache()
        return aname in self.__Cache

    def slowhas(self,aname):
        return aname in self.childNames()

    #################
    def getVariableMember(self,dd):
        super(GenTree,self).getVariableMember(dd)
        if "__Cache" in dd:
            dd.pop("__Cache")

    #################
    def resetCache(self):
        self.__Cache = dict()

    #################
    def cache(self):
        """ build a dictionary childrenName,address
        """
        self.__Cache = {}
        for ch in self.getChildren():
            self.__Cache[ch.getName()] = ch

    ###################
    def getChildByName(self,key):
        """ from a name find a node in the task node ... the result is cache for futher query
        """
        if key in self.__Cache:
            return self.__Cache[key]

        for cn in self.getChildren():
            if cn.getName() == key:
                self.__Cache[key] = cn
                return cn
        log.debug("getChildByName: node %r not found" % key)
        return  None

    ###################
    def insert(self, newChild, where):
        res = super(GenTree,self).insert(newChild,where)
        if res == False:
            return False
        self.__Cache[newChild.getName()] = newChild
        return True

    #################
    def remove(self):
        p = self.getParent()
        if p != None:
            if not hasattr(p,"__Cache"):
                return super(GenTree,self).remove()
            p.removeChildFromList(self)
            if self.getName() in p.__Cache:
                p.__Cache.pop(self.getName())
        del self

    ###################
    def rename(self,newName,findUnique=True):
        parent = self.getParent()
        if parent == None:
            self.setName(newName)
            return True
        # check if newName is a possible candidate
        if not hasattr(parent,"__Cache"):
            return super(GenTree, self).rename(newName,findUnique)
        for ch in parent.getChildren():
            if ch != self:
                if ch.getName() == newName:
                    if findUnique == False:
                        return False
                    chName = parent.findUniqueChildName(newName)
                    if self.getName() in parent.__Cache:
                        parent.__Cache.pop(self.getName())
                    self.setName(chName)
                    parent.__Cache[chName] = self
                    return True
        if self.getName() in parent.__Cache:
            parent.__Cache.pop(self.getName())
        self.setName(newName)
        parent.__Cache[newName] = self
        return True

    ###################
    def __getitem__(self, item):
        if not item in self.childNames():
            if  item in list(self.__dict__.keys()):
                return self.__dict__[item]
            log.error("in genTree, we should throw an exception KeyError or use variable use before set... to do %s %r %r" % (self,self.getName(),item))
            return GenTree()
        ch = self.getChildByName(item)
        if ch == None:
            log.error("in genTree, we should throw an exception KeyError  or use variable use before set... to do %s %r %r" % (self,self.getName().item))
            return GenTree()
        return ch
    ###################
    def __setitem__(self, item,val):

        if item in self.__dict__:
            self.__dict__[item] = val
        else:
            if not type(item) in (str,):
                log.error("key Type error")
                return
            if isinstance(val, Tdata):
                # in cache use hashing so it's faster, if no cache then use fallback
                if item in self.__Cache or item in self.childNames():
                    pass
                else:
                    val.setName(item)
                    self.addChild(val,False)
            else:
                ##### IN TESTING (not sure If it's a desirable Base. it makes the delete easier
                # but it's break
                if val == None:
                    if item in self.__Cache:
                        ch = self.__Cache[item]
                        self.removeChildFromList(ch)
                        self.__Cache.pop(item)
                    elif item in self.childNames():
                        for ch in self.getChildren():
                            if item == ch.getName():
                                self.removeChildFromList(ch)
                                break
                    else:
                        log.error("setitem as not kid of that name %r" % item)

                else:
                    log.error("support only genTree interface or None")

    def isEnable(self):
        return True

if __name__ == '__main__':
    a = GenTree()
    '''
    class bg(GenTree):
        pass
    b = bg()
    c = b.ReadAsXml("foo.xml")
    print(c)

    b.setName("Top")
    c = bg()
    c.setName("tptp")
    b.addChild(c)

    b.SaveAsXml("foo.xml")
    b.SaveAsJson("foo.json",True,True)
    '''



