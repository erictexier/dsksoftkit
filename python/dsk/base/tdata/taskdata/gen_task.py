import string
import types
import re
import base64
import json
from collections import namedtuple


# base class

from dsk.base.tdata.gen_tree import GenTree
from dsk.base.utils.msg_utils import MsgUtils as log


# exception
class RequiredFieldError(Exception):
    """Something cannot process with out it"""
    pass


class AttrDescription(namedtuple('attrDescription', 'name type uitype get set required')):
    __slots__ = ()


typeArgWidget = ['argLineEdit','simpleLineEdit','multipleLineEdit','simpleCheck','noEdit']

def customStream():
    try:
        import cStringIO
        return cStringIO.StringIO()
    except:
        import StringIO
        return StringIO.StringIO()

################################################
class GenTask(GenTree):

    _checkStringEval = re.compile(u"^CFD|RTD|TASK|TP")
    _argumentFunction = re.compile(u"\(\s*[\w\d\s.\[\]\'\",=]*\)")

    def __init__(self):
        super(GenTask, self).__init__()

    #### RTD, CFD, overloaded function
    def setVariable(self,rtd,cfd):
        d = rtd.get_as_dict() if rtd != None else {'name':'RunTimeData'}
        try:
            self.RTD = json.dumps(d)
        except:
            print("Failed json dump")
            self.RTD  = json.dumps({'name':'RunTimeData'})

        if cfd == None:
            adict = {'name':'ConfigData'}
        else:
            adict = cfd.get_as_dict()
            # clean up the layout for now
            if adict.has_key('layout'):
                adict.pop('layout')
        try:
            self.CFD = json.dumps(adict)
        except:
            self.CFD = json.dumps( {'name':'ConfigData'})

    def getCFD(self):
        if self.has("CFD"):
            return json.loads(self.CFD)
        return dict()

    def getRTD(self):
        if self.has("RTD"):
            return json.loads(self.RTD)
        return dict()

    #### END RTD, CFD
    # setenable

    #### THIS is INterface base.... need to be implemented
    #################
    def getVariableMember(self, dd):
        """ the is a call back to control what to save
        per nature from doesn't need to be serialize to we remove all the
        private variable
        """
        super(GenTask,self).getVariableMember(dd)

        for key in ["_interfaceFactory"]:
            if key in dd:
                dd.pop(key)

    def setEnable(self,val):
        self.enable = val
    # inherit
    def isEnable(self):
        if self.has('enable'):
            return self.enable
        return True

    def get_comment(self):
        if hasattr(self,'comment'):
            return self.comment
        return ""

    def set_comment(self,comment):
        self.comment = comment

    @classmethod
    def get_lock_up(cls):
        return None

    def get_interface_factory(self):
        if self._interfaceFactory != None:
            return self._interfaceFactory
        return self._interfaceFactory

    ### overwrite/inherit
    def update_with(self,atask,lockup = None,attribList=None):
        # name
        if hasattr(atask,'name'):
            from dsk.base.tdata import tdata
            cleanName = atask.name.replace(tdata.SepPath,"_")
            self.setName(cleanName)
        else:
            self.setName("unknown")

        #comment
        if hasattr(atask,'comment'):
            self.comment = atask.comment

        # enable or not
        if hasattr(atask,'enable'):
            self.enable = atask.enable

        # label
        lab =  atask.getLabel()
        # label is only when different of name + we remove the preceding the last dot
        if lab != atask.name:
            if lab.find(".") != -1:
                lab = lab.split(".")[-1]
            if lab != atask.name:
                self.label = lab

        # for debug we keep the label
        self.label = atask.getLabel()

        if lockup != None and attribList != None and self.isEnable()==True:
            for attr in attribList:
                if hasattr(atask,attr.name):
                    if lockup[attr.name].set(self,attr.name,getattr(atask,attr.name)) == False and lockup[attr.name].required:
                        log.error("attribute %r is required for %r in %r" % (attr.name,
                                                                             self.__class__.__name__,
                                                                             self.getName()))



    # zone is where value are code or not: to avoid confusion in the parsing some
    # of the argument are converted into base64 encoding
    ###
    def set_zone(self,key,value):
        if value != None:
            setattr(self,key,value)
            return True
        return False

    def zone(self,prop):
        if hasattr(self,prop) == True:
            return getattr(self,prop)
        return None

    def set_eval_zone(self,key,value):
        # for basic parameter value, since some of them have quote

        if value != None:
            setattr(self,key,base64.encodestring("%s" % value))
            return True
        return False

    def eval_zone(self,prop):
        # for basic parameter value, since some of them have quote
        if hasattr(self,prop) == True:
            return base64.decodestring(getattr(self,prop))
        return None

    ###
    def has(self,akey):
        return hasattr(self,akey)

    # python generating code
    def header(self,stream,tab):
        stream.write(tab + "#" * 50 + "\n")
        stream.write(tab + "#  new class\n")

    ###
    def to_python_class_def(self,stream,className,baseClass,rtdDict,cfdDict,tab,incTab):
        """ we print here the RTD and CFD and TP (no done) initial setup, config first
        """
        stream.write(tab + "# class definition\n")
        stream.write(tab + "class %s(%s):\n" % (className,baseClass))
        tab += incTab
        stream.write(tab + "def __init__(self):\n")
        tab += incTab
        stream.write(tab + "super(%s, self).__init__()\n" % className)
        stream.write(tab + "from dsk.base.tdata.taskdata.tp_variable import TpVariable,ProcessVar\n")
        stream.write("\n")
        stream.write(tab + "# instance\n")
        stream.write(tab + "self.CFD = TpVariable()\n")
        stream.write(tab + "self.CFD.set_with_dict(" + str(cfdDict) + ")\n")
        stream.write(tab + "self.RTD = TpVariable()\n")
        stream.write(tab + "self.RTD.set_with_dict(" + str(rtdDict) + ")\n")
        stream.write(tab + "self.TP = ProcessVar()\n")
        stream.write(tab + "#" * 10 + "end init\n\n")

    ###
    def to_python_main_function(self,stream,tab,incTab):
        """ we print here the RTD and CFD and TP (no done) initial setup, config first
        """

        stream.write(tab + "def %s(self,RTD=None,CFD=None,TP=None):\n" % self.getName())
        tab += incTab
        stream.write(tab + "CFD = self.CFD.overwrite(CFD)\n")
        stream.write(tab + "RTD = self.RTD.overwrite(RTD)\n")
        stream.write(tab + "TP = self.TP.overwrite(TP)\n")
        stream.write("\n")

    ###
    def to_python(self,stream,acontext):
        """ the context can be
        --> tab: current tab    (string)
        --> tabInc: indentation(string)
        --> importStatement:   dynamic list to keep module name already imported
        --> skipComment: don't write comment argument (bool)
        """
        if acontext.has_key('skipComment'):
            if acontext['skipComment'] == True:
                return
        tab = acontext['tab']
        # we ignore the tab here, it's only comment
        stream.write("\n\n")
        stream.write(tab + "#\n")
        if self.has('comment'):
            stream.write(tab + "# %s -- %s\n" % (self.getName(),self.comment.strip()))
        else:
            if hasattr(self,'label'):
                stream.write(tab + "# %s\n" % (self.label))
            else:
                stream.write(tab + "# %s\n" % (self.getName()))
        stream.write(tab + "#" + "\n")
        return True


    @staticmethod
    def get_function_name(context,funcName):
        if not context.has_key("newFunctionName"):
            context["newFunctionName"] = list()
            context["newFunctionName"].append(funcName)
            return funcName
        if not funcName in context['newFunctionName']:
            context["newFunctionName"].append(funcName)
            return funcName
        number = 0
        if not context.has_key('nbNewFunction'):
            context['nbNewFunction'] = number
        else:
            context['nbNewFunction'] += 1

        return "%s_%d" % (funcName,context['nbNewFunction'])

    ### some module simplification code to avoid multiple import statement
    @staticmethod
    def do_python_module(stream,acontext,tab,module):
        """In a list of task, module import statement get writen only one
        """
        assert module != "" and module != None

        if acontext.has_key("importStatement"):
            modInThere = acontext['importStatement']
            if not modInThere.has_key(module):
                stream.write("%simport %s\n" % (tab,module))
                acontext['importStatement'][module]=True
        else:
            stream.write("%simport %s\n" % (tab,module))
            acontext['importStatement'] = dict()
            acontext['importStatement'][module]=True
    ###
    @staticmethod
    def copy_reset_import_statement(acontext):
        d= dict()
        if not acontext.has_key("importStatement"):
            return d
        d.update(acontext['importStatement'])
        acontext.pop('importStatement')
        return d
    ###
    @staticmethod
    def reload_import_statement(d,acontext):
        if acontext.has_key("importStatement"):
            acontext.pop('importStatement')
        acontext['importStatement'] = dict()
        acontext['importStatement'].update(d)

    # and object main need multiple stream
    # mainly for method management
    @staticmethod
    def push_stream(context,stream,callFunction):
        assert callFunction != ""
        from collections import OrderedDict
        if not context.has_key('streamQueue'):
            context['streamQueue'] = OrderedDict()
            context['streamQueue']['mainStream'] = stream
        assert not callFunction in context['streamQueue']
        newStream = customStream()

        context['streamQueue'][callFunction] = newStream
        return newStream

    ###
    def traverse_with_tab(self,stream,func,kwarg):
        """ traverse_with_tab minimum kwarg --> 'tab'
        """

        if not self.isEnable():
            # i'm not sure about this, some time the main task list is turn off
            if self.getName() != "TaskList":
                return
        for i in self.getChildren():
            saveTab = None
            if kwarg.has_key('tab'):
                saveTab = kwarg['tab']
            traverse = True

            if i.hasInterface(func) and i.isEnable():
                afunc = eval("i.%s" % func)
                traverse = afunc(stream,kwarg)

            if traverse: i.traverse_with_tab(stream,func,kwarg)

            if saveTab != None:
                kwarg['tab'] = saveTab

    ## attribute
    def get(self,attributeName,default=None):
        d = self.get_lock_up()
        if d == None:
            return default
        if attributeName in d:
            return d[attributeName].get(self,attributeName)
        return default

    def set(self,attributeName,avalue):
        d = self.get_lock_up()
        if d == None:
            return False
        if attributeName in d:
            d[attributeName].set(self,attributeName,avalue)
            return True
        return False

    def get_attribute_names(self):
        d = self.get_lock_up()
        if d == None:
            return list()
        return d.keys()

    def get_attribute_name_and_type(self):
        d = self.get_lock_up()
        if d == None:
            return list()
        return map(lambda a: (a,d[a].type.__name__),d)

    def get_attribute_name_and_typeUI(self):
        d = self.get_lock_up()
        if d == None:
            return list()
        return map(lambda a: (a,d[a].uitype),d)


    @staticmethod
    def to_python_one_package(atask,
                              className,
                              skipComment=False,
                              doTaskPackage=False,
                              packageAllReadyLoaded = None,
                              packName=""):
        assert className != ""
        assert atask != None

        tab=""
        tabInc=" "*4
        output = customStream()
        atask.header(output,tab)
        atask.to_python_class_def(output,
                                  className,
                                  "object",
                                  atask.getRTD(),
                                  atask.getCFD(),
                                  tab,
                                  tabInc)

        atask.to_python_main_function(output,tab+tabInc,tabInc)
        tab = tabInc * 2
        acontext = dict()
        acontext['tab'] = tab
        acontext['tabInc'] = tabInc
        acontext['skipComment'] = skipComment
        acontext['doTaskPackage'] = doTaskPackage
        acontext['packageClass'] = className
        if packName == "":
            acontext['packageName'] = className
        else:
            acontext['packageName'] = packName
        acontext['taskPackage'] = list()
        if packageAllReadyLoaded == None:
            acontext['taskPackageLoaded'] = []
        else:
            acontext['taskPackageLoaded'] = packageAllReadyLoaded
        atask.setEnable(True)
        atask.traverse_with_tab(output,"to_python",acontext)

        # merge the stream
        listOfOutput = list()
        if acontext.has_key('streamQueue'):
            #it's an old ordered dict so it's safer this way
            for s in acontext['streamQueue']:
                listOfOutput.append(acontext['streamQueue'][s])

        else:
            listOfOutput.append(output)
        return listOfOutput,acontext['taskPackage']



