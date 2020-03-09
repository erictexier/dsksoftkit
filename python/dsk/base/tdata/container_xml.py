import types
import traceback


from dsk.base.tdata import tdata
from dsk.base.tdata import xml_helper
from dsk.base.tdata import type_helper
from dsk.base.utils.msg_utils import MsgUtils


#### for debug
VERB = True

############ FILE XML CONSTANT ######
VERSION = 1.0
APPSTRUCTYPE  = "simpletree"
APPVERSION = ("version", VERSION)
APPSERVERID = ("server", "https://dsk")
DOCTYPE = "shotfile.dtd"
def noneTypeCast(t):
    return t
##################
##################
##################

class ContainerXml(xml_helper.XmlHelper):
    PROPID_OLD = "property"
    PROPID = "p"
    CHILDID = "children"
    FILEID = "containerFile"
    REFID = "reference"
    NoName = "noName"
    ##################
    def __init__(self,enc=False):
        super(ContainerXml,self).__init__(enc)
        self.reset()
        # allowRef: not completely implemented
        self._allowRef = True

    ##################
    def reset(self):
        super(ContainerXml,self).reset()
        self._top = []
        self._ref = []

    #################
    def addRef(self,obj,elmt):
        """     keep a dynamic list at writing time
            of all the container object. when an occurence
            come again make a special element with the path
            instead of dumping the object
        """
        assert self.isContainerClass(obj)
        if self._allowRef:
            if obj in self._ref:
                self.elementUnder(elmt,self.REFID,list({"path":obj.getPath()}.items()))
                # no need to do more
                return True
            else:
                self._ref.append(obj)
                # still need to be serialize once
                # by returning false

        return False

    #################
    def refRead(self,obj,parentTask):
        """
        this function is mean to try to solve reference
            as we go. return the referenced obj,when possible
            else None
        """
        if not self._allowRef:
            return None

        assert isinstance(obj,tdata.defaultContainer)

        path = obj.pathname

        for aL in self._ref:
            if aL.getPath() == path:
                return aL

        if parentTask:
            ro = parentTask.find(path)
            if ro:
                return ro
        return None

    #################
    def addRead(self,obj):
        """ object get store for potentential reference
            later
        """
        if self._allowRef:
            if not obj in self._ref:
                self._ref.append(obj)

    #################
    def isContainerClass(self,ob):
        return isinstance(ob,tdata.Tdata)

    ##################
    def startDomTree(self):
        """constructs the  dom from all containers"""
        if self._doc == None:
            # for now, we leave the doctype 'dtd' out.
            self.createDom(None, None, APPSTRUCTYPE)
            self._top = [self.elementUnder(self._doc,APPSTRUCTYPE,
                                           attributes=(APPVERSION,APPSERVERID))]
        else:
            self._top += [self.elementUnder(self._doc,APPSTRUCTYPE,
                                            attributes=(APPVERSION,APPSERVERID))]


    ##################
    def constructDomTree(self,myTask,elmt,rec = True):
        if myTask == None:
            return self._doc
        if elmt == None:
            if len(self._top) > 0:
                elmt = self._top[-1]
            if elmt == None:
                return self._doc

        if self.isContainerClass(myTask):
            if self.addRef(myTask,elmt):
                pass
            else:
                d = {"class":myTask.getClassName()}
                myTask.loadStringAttribute(d)

                # query header to be the task to be store
                # has key/value attribute

                chdom = self.elementUnder(elmt, myTask.getModuleName(),list(d.items()))

                if rec:
                    chN = None
                    for ch in myTask.getChildrenForXml():

                        if chN == None:
                            chN = self.elementUnder(chdom,self.CHILDID)
                        self.constructDomTree(ch,chN,rec)
                else:
                    # when recursion is 0 we only save
                    # ref to the children
                    pass
                # query the dictionary of the task
                dd = {}
                myTask.getVariableMember(dd)
                # start the recursion
                self.recursionDict(dd,chdom)


        elif hasattr(myTask,"__dict__"):
            # for simple dict class
            chdom = self.elementUnder( elmt,myTask.__class__.__module__,list({"class":myTask.__class__.__name__}.items()))
            dd = {}
            dd.update(myTask.__dict__)
            # start the recursion
            self.recursionDict(dd,chdom)
        else:
            # let try sets
            aclass = None
            amodule = None
            try:
                aclass = myTask.__class__.__name__
                amodule = myTask.__class__.__module__
            except:
                traceback.print_exc()
                MsgUtils.warning('OTHER OBJECT NOT SUPPORTED YET')

            if (amodule != None and aclass in type_helper.SOMEOTHERTYPE):

                if aclass == "Set":
                    chdom = self.elementUnder(elmt,amodule,list({"class":aclass}.items()))

                    for e in myTask:
                        attr = self.elementUnder(chdom,type(e).__name__)
                        self.textNodeUnder(attr,str(e))

                elif aclass == "xrange":
                    chdom = self.elementUnder(elmt,amodule,list({"class":aclass,"construct":str(myTask)}.items()))
                elif aclass == "complex":
                    chdom = self.elementUnder(elmt,amodule,list({"class":aclass,"construct":'complex%s' % myTask}.items()))

                else:
                    MsgUtils.warning("not supported yet module %r class %r" % (amodule,aclass))
            else:
                MsgUtils.warning('not supported xx %s' % aclass)

        return self._doc

    ##################
    def recursionList(self,ll,elmt):
        for l in ll:
            if type(l) in type_helper.BASICTYPE:
                attr = self.elementUnder(elmt,type(l).__name__)
                if str(l).strip() == "":
                    self.textNodeUnder(attr,'""')
                else:
                    self.textNodeUnder(attr,str(l))

            elif l == None:
                attr = self.elementUnder(elmt,type(l).__name__)
                self.textNodeUnder(attr,'"None"')

            elif type(l) in type_helper.LISTTYPE:
                propName = self.elementUnder(elmt,self.PROPID,
                    list({"type":type(l).__name__}.items()))
                self.recursionList(l,propName)

            elif type(l) == dict:
                propName = self.elementUnder(elmt,self.PROPID,
                    list({"type":type(l).__name__}.items()))
                self.storeDict(l,propName)

            else:
                self.constructDomTree(l,elmt)

    ##################
    def storeDict(self,dd,elmt):
        # key can be int,float,long or string
        for i in dd:
            # first the key
            if type(i) in type_helper.BASICTYPE:
                keyName = self.elementUnder(elmt,type(i).__name__)
                self.textNodeUnder(keyName,str(i))
                # then the value
                if type(dd[i]) in type_helper.BASICTYPE:
                    keyVal = self.elementUnder(elmt,type(dd[i]).__name__)
                    if dd[i] != "":
                        self.textNodeUnder(keyVal,str(dd[i]))
                    else:
                        self.textNodeUnder(keyVal,str('""'))
                elif dd[i] == None:
                    keyVal = self.elementUnder(elmt,type(dd[i]).__name__)
                    self.textNodeUnder(keyVal,str('"None"'))
                elif type(dd[i]) in type_helper.LISTTYPE:
                    propName = self.elementUnder(elmt,self.PROPID,list({"type":type(dd[i]).__name__}.items()))
                    self.recursionList(dd[i],propName)
                elif type(dd[i]) == dict:
                    propName = self.elementUnder(elmt,self.PROPID,list({"type":type(dd[i]).__name__}.items()))
                    self.storeDict(dd[i],propName)

                else:
                    self.constructDomTree(dd[i],elmt)

    ##################
    def recursionDict(self,dd,elmt):

        for i in dd:
            # name of the member and type

            propName = self.elementUnder(elmt,self.PROPID,list({"name":i,"type":type(dd[i]).__name__}.items()))

            if type(dd[i]) in type_helper.BASICTYPE:
                if dd[i] != "":
                    self.textNodeUnder(propName,str(dd[i]))
                else:
                    self.textNodeUnder(propName,str('""'))

            elif dd[i] == None:
                self.textNodeUnder(propName,str('"None"'))

            elif type(dd[i]) in type_helper.LISTTYPE:
                self.recursionList(dd[i],propName)


            elif type(dd[i]) == dict:
                self.storeDict(dd[i],propName)

            # check if it's an 'valid' object
            elif self.isContainerClass(dd[i]):
                self.constructDomTree(dd[i],propName)

            else:
                self.constructDomTree(dd[i],propName)

    ##################
    def importFromFile(self,fileName,maxLevel = -1):
        res = super(ContainerXml,self).importFromFile(fileName)
        if res:
            return self.load(maxLevel)
        return None

    ##################
    def load(self,maxLevel):
        if self._doc == None:
            return None
        # here we track the odd file
        self._top = []
        TopCreated = []

        for n1 in self._doc.childNodes:
            if n1.nodeName == APPSTRUCTYPE:
                self._top.append(n1)
                TopCreated += self.LoadRecurElement(n1.firstChild,None,maxLevel)

            else:
                self._top.append(n1)
                parentTask = tdata.container()
                parentTask.setName(n1.nodeName)
                adict = {}
                if self.getXmlAttr(n1,adict):
                    parentTask.__dict__.update(adict)
                TopCreated.append([n1.nodeName,parentTask,self.NoName])
                self.loadRaw(n1.firstChild,parentTask,maxLevel)

        result = []
        for i in TopCreated:
            assert len(i) == 3
            result.append(i[1])
        return result

    #################
    def getKidsRaw(self,elmt,parentTask,maxLevel):
        ch = elmt.firstChild
        if ch != None:
            return self.loadRaw(ch,parentTask,maxLevel)
        return []

    def loadRaw(self,elmt,pTask,maxLevel):
        # foreign xml
        creationList = []
        nb = "n%d:"
        index = 0

        while elmt != None:

            if elmt.nodeType == elmt.ELEMENT_NODE:
                if maxLevel == 0:
                    return []
                if maxLevel != -1:
                    maxLevel -= 1

                if elmt.nodeName != "#text":
                    atask = tdata.container()
                    atask.setName(nb % index + elmt.nodeName)

                    pTask.addChild(atask)

                    index += 1
                    adict = {}
                    if self.getXmlAttr(elmt,adict):
                        atask.__dict__.update(adict)
                    result = self.getKidsRaw(elmt,atask,maxLevel)
                    for r in result:
                        if r[0] == "TexType":
                            atask.setValue(r[1])
                        else:
                            MsgUtils.error("not done  %r %r t=%s v=%s n=%s" % (pTask.getName(),atask.getName(),r[0],r[1],r[2]))
            elif elmt.nodeType == elmt.TEXT_NODE:
                edata = self.getTextValue(elmt).strip()
                if edata != "":
                    creationList.append(["TextType",edata,elmt.nodeName])
            elif elmt.nodeType == elmt.COMMENT_NODE:
                edata = self.getTextValue(elmt).strip()
                if edata != "":
                    creationList.append(["CommentType",edata,elmt.nodeName])

            elif elmt.nodeType == elmt.CDATA_SECTION_NODE:
                data = self.getcData(elmt)
                if data != "" and len(data.strip()) > 0:
                    creationList.append(["CdType",data,elmt.nodeName])
            else:
                MsgUtils.warning("NOT YETXX %r %r" % (elmt.nodeName,elmt.nodeType))

            elmt = elmt.nextSibling
        return creationList

    #################
    def getKids(self,elmt,parentTask,maxLevel):
        ch = elmt.firstChild
        if ch != None:
            return self.LoadRecurElement(ch,parentTask,maxLevel)
        return []


    ##################
    def LoadRecurElement(self,elmt,parentTask,maxLevel):

        creationList = []

        while elmt != None:
            if elmt.nodeType == elmt.ELEMENT_NODE:
                # get Attr in a dict
                adict = {}
                self.getXmlAttr(elmt,adict)
                assert not(elmt.nodeName in type_helper.LIST_TYPE_NAME)
                assert not(elmt.nodeName=='dict')

                if elmt.nodeName in type_helper.SIMPLE_TYPE_NAME:
                    result = self.getKids(elmt,parentTask,maxLevel)

                    #assert len(result) == 1
                    if len(result) == 1:
                        res = result[0]
                        assert len(res) == 3
                        if elmt.nodeName in type_helper.STRING_TYPE_NAME:
                            if res[1] == '""' or res[1] == '""':
                                v = ""   # TESTING
                            else:
                                v = "%r" % res[1]
                            creationList.append([elmt.nodeName ,v,self.NoName])
                        else:

                            val = res[1].strip()
                            creationList.append([elmt.nodeName,val,self.NoName])

                # property
                elif elmt.nodeName == self.PROPID or elmt.nodeName == self.PROPID_OLD:
                    # must have type, name optional
                    assert 'type' in adict
                    # property belong to a
                    # 'valid parent' list, dict..
                    name = self.NoName
                    if 'name' in adict:
                        name = adict['name']

                    if  adict['type'] in type_helper.SIMPLE_TYPE_NAME:
                        #those are suppose to have 1
                        # child only holding the value
                        result = self.getKids(elmt,parentTask,maxLevel)
                        if len(result) == 0:
                            break
                        assert len(result) == 1
                        #if len(result) == 1
                        res = result[0]
                        assert len(res) == 3
                        if adict['type'] in type_helper.STRING_TYPE_NAME:
                            if res == '""' or res[1] == '""':
                                v = ""  # TESTING
                            else:
                                v = "%s" % res[1]
                            creationList.append([adict['type'],v,name])
                        else:
                            val = res[1].strip()
                            creationList.append([adict['type'],val,name])

                    elif adict['type'] in type_helper.LIST_TYPE_NAME:
                        result = self.getKids(elmt,parentTask,maxLevel)
                        if adict['type'] == type_helper.LIST_TYPE_NAME[0]:
                            newone = []
                        elif adict['type'] == type_helper.LIST_TYPE_NAME[1]:
                            newone = ()
                        else:
                            MsgUtils.warning("trouble with the list type")

                        for res in result:

                            assert len(res) == 3
                            if res[0] in type_helper.SIMPLE_TYPE_NAME:
                                val = None
                                val = eval('%s(%s)' % (res[0],res[1]))

                                if adict['type'] == type_helper.LIST_TYPE_NAME[0]:
                                    newone.append(val)
                                elif adict['type'] == type_helper.LIST_TYPE_NAME[1]:
                                    newone += (val,)
                            else:
                                if res[0] == self.REFID:
                                    nref = self.refRead(res[1],parentTask)
                                    if nref != None:
                                        res[1] = nref
                                    else:
                                        MsgUtils.warning("can't resolve dependance yet")

                                if adict['type'] == type_helper.LIST_TYPE_NAME[0]:
                                    newone.append(res[1])
                                elif adict['type'] == type_helper.LIST_TYPE_NAME[1]:
                                    newone += (res[1],)

                        creationList.append(["%s"%adict['type'],newone,name])

                    elif adict['type'] == 'dict':
                        newone = {}
                        result = self.getKids(elmt,parentTask,maxLevel)
                        # the result must be key value,... an even number
                        assert not len(result) % 2
                        for index in range(0,len(result),2):
                            key = result[index]
                            val = result[index+1]
                            assert len(key) == 3
                            assert len(val) == 3
                            kk = None
                            vv = None

                            if key[0] in type_helper.SIMPLE_TYPE_NAME:
                                kk = eval('%s(%s)' % (key[0],key[1]))

                            else:
                                if key[0] == self.REFID:
                                    nref = self.refRead(key[1],parentTask)
                                    if nref != None:
                                        key[1] = nref
                                    else:
                                        MsgUtils.warning("can't resolve dependance yet")

                                kk = key[1]

                            if val[0] in type_helper.SIMPLE_TYPE_NAME:
                                #if len(val[1]) > 2 and val[1][0] = "'"
                                #if val[0] in type_helper.STRING_TYPE_NAME:
                                #    vv = val[1]
                                #else:
                                vv = eval('%s(%s)' % (val[0],val[1]))

                            else:
                                vv = val[1]
                                if val[0] == self.REFID:
                                    nref = self.refRead(vv,parentTask)
                                    if nref != None:
                                        vv = nref
                                    else:
                                        MsgUtils.warning("can't resolve dependance yet")

                            newone[kk] = vv

                        creationList.append(["dict",newone,name])

                    elif adict['type'] == types.NoneType.__name__:
                        creationList.append([adict['type'],None,name])
                    else:
                        #if nothing else it must be an object
                        result = self.getKids(elmt,parentTask,maxLevel)

                        assert len(result) == 1
                        res = result[0]
                        assert len(res) == 3
                        if res[0] == self.REFID:
                            nref = self.refRead(res[1],parentTask)
                            if nref != None:
                                res[1] = nref
                            else:
                                MsgUtils.warning("can't resolve dependance yet")

                        creationList.append(["unknownType",res[1],name])

                elif elmt.nodeName == self.CHILDID:
                    assert parentTask != None
                    if maxLevel == 0:
                        break
                    if maxLevel != -1:
                        maxLevel -= 1
                    result = self.getKids(elmt,parentTask,maxLevel)
                    for res in result:
                        assert len(res) == 3
                        assert res[0] != self.REFID
                        parentTask.addChild(res[1])

                elif elmt.nodeName == self.FILEID:
                    assert 'path' in adict
                    path = adict['path']
                    insts = tdata.Tdata.ReadAsXml(path)
                    for ist in insts:
                        creationList.append(["unknowType",ist,self.NoName])

                elif elmt.nodeName == self.REFID:
                    assert 'path' in adict
                    instance = tdata.defaultContainer()
                    instance.pathname = adict['path']
                    nref = self.refRead(instance,parentTask)
                    if nref != None:
                        creationList.append(["unknownType",nref,self.NoName])
                    else:
                        creationList.append([self.REFID,instance,self.NoName])

                elif elmt.nodeName == 'NoneType':
                    creationList.append([noneTypeCast,None,self.NoName])


                else:
                    # It's an object that need to be instanciate

                    assert 'class' in adict
                    amodule = elmt.nodeName
                    aclass = adict['class']
                    if (amodule != 'Tdata' and
                            amodule != '__builtin__'):
                        cmd = "import %s" % amodule

                        try:
                            exec(cmd)
                        except:
                            traceback.print_exc()
                            MsgUtils.warning("cannot import %s" % elmt.nodeName)
                            MsgUtils.msg("Creating a generic class container")
                            amodule = "Tdata"
                            aclass = "container"
                    if 'construct' in adict:
                        #cmd = "newInstance = %s" % adict['construct']
                        cmd = "%s" % adict['construct']
                    else:
                        #cmd = "newInstance = %s.%s()" % (amodule,aclass)
                        cmd = "%s.%s()" % (amodule,aclass)

                    newInstance = None

                    try:
                        #exec(cmd,globals(), locals())
                        newInstance = eval(cmd)

                    except:
                        traceback.print_exc()
                        MsgUtils.error("COMMAND %s" % cmd)
                        MsgUtils.msg("class definition %s not found in %s" % (aclass,amodule))

                    assert newInstance != None

                    if self.isContainerClass(newInstance):
                        newInstance.updateStringAttribute(adict)
                        self.addRead(newInstance)

                    result = self.getKids(elmt,newInstance,maxLevel)
                    if not aclass in type_helper.SOMEOTHERTYPE:
                        for res in result:
                            assert len(res) == 3
                            assert not res[2] == self.NoName
                            if res[0] == self.REFID:
                                nref = self.refRead(res[1],parentTask)
                                if nref != None:
                                    res[1] = nref
                                else:
                                    MsgUtils.warning("can't resolve dependance yet")

                            if res[0] == "bool":
                                if res[1] == "False":
                                    cmd = "newInstance.%s = False" % res[2]
                                else:
                                    cmd = "newInstance.%s = True" % res[2]

                            elif res[0] in type_helper.SIMPLE_TYPE_NAME:
                                cmd = "newInstance.%s = %s(res[1])" % (res[2],res[0])
                            else:
                                cmd = "newInstance.%s = res[1]" % res[2]

                            exec (cmd)

                    else:
                        if aclass == "Set":
                            for res in result:
                                assert len(res) == 3
                                val = eval('%s(%s)'%(res[0],res[1]))
                                newInstance.add(val)

                    creationList.append(['object',newInstance,self.NoName])


            elif elmt.nodeType == elmt.TEXT_NODE:
                data = self.getTextValue(elmt)
                if data != "":
                    sdata = data.strip()
                    if len(sdata) > 0:
                        creationList.append(["dType",sdata,self.NoName])
                else:
                    raise


            elif elmt.nodeType == elmt.CDATA_SECTION_NODE:
                data = self.getcData(elmt)
                if data != "":
                    sdata = data.strip()
                    if len(sdata) > 0:
                        creationList.append(["CdType",data,self.NoName])
                    else:
                        pass

            elmt = elmt.nextSibling
        return creationList


#################### for example #################
class foo:
    def __init__(self):
        self.zoo = "zoo"
        self.fl = 10.
        self.int = 4
        self.empty = ""

if __name__ == "__main__":
    from dsk.base.tdata import container_xml
    x = container_xml.ContainerXml()

    a = foo()
    a.fl = 100000.
    a.empty = "not so empty"
    a.zoo = "zaa"
    x.startDomTree()
    x.constructDomTree(a,None,0)
    x.exportToFile("zoo.xml",True)
    importer = container_xml.ContainerXml()
    b = importer.importFromFile("zoo.xml")
    if b != None and len(b) > 0:
        y = container_xml.ContainerXml()
        y.startDomTree()
        y.constructDomTree(b[0],None,0)
        y.exportToFile("zoo2.xml",True)

