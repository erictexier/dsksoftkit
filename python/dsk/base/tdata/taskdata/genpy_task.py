import types
import re
import sys
if sys.version_info[0] >= 3:
    from six import string_types as basestring


from dsk.base.utils.msg_utils import MsgUtils as log
from dsk.base.tdata.taskdata.gen_task import GenTask,AttrDescription


from dsk.base.tdata.taskdata.cleaner_variable import clean_quote
from dsk.base.tdata.taskdata.cleaner_variable import do_clean_command

from dsk.base.tdata.taskdata.cleaner_variable import remove_extern_quote
from dsk.base.tdata.taskdata.cleaner_variable import remove_extern_bracket
from dsk.base.tdata.taskdata.cleaner_variable import remove_extern_cbracket
from dsk.base.tdata.taskdata.cleaner_variable import remove_over_quoted


################################################
class GenPyTask(GenTask):
    _attr_PyTask = [AttrDescription('module',types.StringType, 'simpleLineEdit', GenTask.zone, GenTask.set_zone,False),
                    AttrDescription('command',types.StringType, 'multipleLineEdit', GenTask.eval_zone,GenTask.set_eval_zone,True),
                    AttrDescription('output',types.StringType, 'simpleLineEdit', GenTask.eval_zone,GenTask.set_eval_zone,False),
                    AttrDescription('args',types.StringType, 'argLineEdit', GenTask.eval_zone,GenTask.set_eval_zone,False),
                    AttrDescription('kwargs',types.StringType, 'argLineEdit', GenTask.eval_zone,GenTask.set_eval_zone,False),
                    AttrDescription('handler',types.StringType, 'simpleLineEdit', GenTask.zone, GenTask.set_zone,False),
                    ]
    _LockupPyAttr = dict()
    for i in _attr_PyTask:
        _LockupPyAttr[i.name] = i

    def __init__(self):
        super(GenPyTask, self).__init__()

    @classmethod
    def get_lock_up(cls):
        return cls._LockupPyAttr

    def update_with(self,atask,lockup = None,attribList=None):
        super(GenPyTask, self).update_with(atask,GenPyTask._LockupPyAttr,GenPyTask._attr_PyTask)
        if hasattr(atask,'resolveArgValues'):
            self.resolveArgValues = atask.resolveArgValues
            if hasattr(atask,'resolveKwArgValues'):
                self.resolveKwArgValues  = atask.resolveKwArgValues
                if atask.resolveArgValues == False or atask.resolveKwArgValues == False:
                    log.warning("resolve argument set to false is not supported for now")

    def _build_clean_argument_list(self):
        # add the args and the kwargs
        # exception
        # if cmd is found in args and kwargs is a tuple or string don't add the kwargs argument

        lcmd = list()
        val = GenPyTask._LockupPyAttr['args'].get(self,'args')

        if val != None and val != "":
            assert isinstance(val,basestring)
            val = remove_extern_bracket(val)
            val = clean_quote(val)
            # now we have to deal with the funny syntax %()s
            sval = val.split(",")
            for s in sval:
                s = s.strip()
                s = remove_over_quoted(s)
                res = do_clean_command(s)
                if res.success:
                    lcmd.append("%s%s\n" % (res.newCommand,res.addOn))
                else:
                    lcmd.append(s)

        val = GenPyTask._LockupPyAttr['kwargs'].get(self,'kwargs')
        if val != None and val != "":
            # we canno't eval here
            # first see it's a path
            pe = ""
            if val.startswith("{'"):
                pe = re.compile(r"'[\w]*':")
                val = remove_extern_cbracket(val)
            elif val.startswith('{"'):
                pe = re.compile(r'"[\w]*":')
                val = remove_extern_cbracket(val)
            else: # it's a path
                if len(lcmd) != 0: # when 2 path are define the dict one is ignore
                    return lcmd
                val = clean_quote(val)
                sval = val.split(",")
                for s in sval:
                    s = s.strip()
                    s = remove_over_quoted(s)
                    res = do_clean_command(s)
                    if res.success:
                        lcmd.append("%s%s" % (res.newCommand,res.addOn))
                    else:
                        lcmd.append(s)
                return lcmd
            # I know it's ugly and it much be an other way but I cannot come up with
            # the right patern is insulate key,value, knowing that everything here can be escape
            allKey = re.findall(pe,val)
            allKey.reverse()
            dlist = list()
            # we start by the end, by splitting we should be able to build a list of tuple
            for k in allKey:
                sval=val.split(k)
                val = sval[0]
                # clean the key:
                akey = remove_extern_quote(k.replace(":","").strip())
                # clean the value
                aval = sval[1].strip()
                if len(aval) > 0 and aval[-1] == ",":aval = aval[:-1]
                aval = clean_quote(aval)
                dlist.append((akey,remove_over_quoted(aval)))
            dlist.reverse()
            for i in dlist: # put it back in order
                res = do_clean_command(i[1])
                if res.success:
                    if len(res.newCommand) > 0 and not res.newCommand[0] in ['"',"'"]:
                        lcmd.append("%s = '%s' %s" % (i[0],res.newCommand,res.addOn))
                    else:
                        lcmd.append("%s = %s%s" % (i[0],res.newCommand,res.addOn))
                else:
                    lcmd.append("%s = %s" % (i[0],i[1]))

        return lcmd

    def get_argument_string(self):
        argList = self._build_clean_argument_list()
        return ",".join(argList)

    def set_argument_string(self,args):
        arg = list()
        karg = list()
        argList = args.split(",")
        for i in argList:
            if i.find("=") != -1:
                karg.append(i)
            else:
                arg.append(i)

        self.set('args',",".join(arg))
        self.set('kwargs',",".join(karg))



    def is_script(self):
        handler = GenPyTask._LockupPyAttr['handler'].get(self,'handler')
        return not handler in [None,'','eval']


    def to_python(self,stream,acontext):
        # there is 2 case here, one (when module is present, it only about importing the
        # module and excuting the function. The other one is to define a local function
        # and execute it, return value are optional

        super(GenPyTask, self).to_python(stream,acontext)

        tab = acontext['tab']
        #tabInc = acontext['tabInc']
        # command
        command = GenPyTask._LockupPyAttr['command'].get(self,'command')
        if command == None or command.strip() == "":
            log.error("'command' is required for a py task %r" % self.getName())
            return False

        # output
        output = GenPyTask._LockupPyAttr['output'].get(self,'output')
        if output == "":
            output = None

        handler = GenPyTask._LockupPyAttr['handler'].get(self,'handler')
        if handler == "":
            handler = None

        argumentList = self._build_clean_argument_list()


        if handler == None or handler == 'eval':
            # something the argument string is already in the command
            # module
            module = GenPyTask._LockupPyAttr['module'].get(self,'module')
            doModule = (module != None and module != "")
            if doModule:
                # module
                GenTask.do_python_module(stream,acontext,tab,module)

            m = GenTask._argumentFunction.search(command)

            # having argument syntax in the function take precedence
            startLine = tab
            if output != None:
                startLine += "%s = " % output
            if m:
                if doModule == True:
                    stream.write("%s%s.%s\n" % (startLine,module,clean_quote(command)))
                else:
                    stream.write("%s%s\n" % (startLine,clean_quote(command)))
            else:
                import traceback
                nbOfArgument = len(argumentList)

                if nbOfArgument == 0 and doModule:
                    # some argument like RTD,CFD can be added let check if it's need
                    # inspect
                    import inspect
                    funcstring = "%s.%s" % (module,command)
                    inspectSuccess = True
                    readArg = None

                    try:
                        exec("import %s" % module)
                    except:
                        #traceback.print_exc()
                        inspectSuccess = False
                        log.warning("couldn't import the module('%s')" % module)

                    try:
                        readArg = inspect.getargspec(eval(funcstring))
                    except:
                        inspectSuccess = False
                        #log.warning("couldn't get the function('%s') argument in %s" % (funcstring,self.label))

                    if inspectSuccess==False:
                        if doModule:
                            stream.write("%s%s.%s()\n" % (startLine,module,command))
                        else:
                            stream.write("%s%s()\n" % (startLine,command))
                    else:
                        # very simple for now
                        #defa = readArg.defaults

                        argu = ""
                        for i in readArg.args:
                            m = GenTask._checkStringEval.match(i)
                            if m:
                                if argu == "":
                                    argu = i
                                else:
                                    argu = argu + "," + i

                        if argu == "":
                            if doModule:
                                stream.write("%s%s.%s()\n" % (startLine,module,command))
                            else:
                                stream.write("%s%s()\n" % (startLine,command))
                        else:
                            if doModule:
                                stream.write("%s%s.%s(%s)\n" % (startLine,module,command,argu))
                            else:
                                stream.write("%s%s.%s(%s)\n" % (startLine,command,argu))
                else:
                    maxLen = 0
                    for ea in argumentList:
                        maxLen += len(ea)

                    endValue = ")"
                    if nbOfArgument > 1:
                        endValue = ","
                    startCmd = ""
                    alen = 0
                    if doModule:
                        startCmd = "%s%s.%s(" % (startLine,module,command)
                    else:
                        startCmd = "%s%s(" % (startLine,command)
                    alen = len(startCmd)
                    if maxLen > 80 and nbOfArgument > 1: # maximum line length to display
                        stream.write("%s%s%s\n" % (startCmd,argumentList[0],endValue))
                        for ar in argumentList[1:-1]:
                            stream.write("%s%s,\n" % (' ' * alen,ar))
                        # we need the ) with the last element
                        stream.write("%s%s)\n" % (' ' * alen,argumentList[-1]))
                    else:
                        stream.write("%s%s)\n" % (startCmd,", ".join(argumentList)))
        else:
            sc = command.split("\n")
            for i in sc:
                stream.write("%s%s\n" % (tab,i))

        return True
