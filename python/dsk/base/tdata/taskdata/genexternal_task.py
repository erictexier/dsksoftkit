import types

from dsk.base.tdata.taskdata.gen_task import GenTask,AttrDescription,RequiredFieldError
from dsk.base.tdata.taskdata.cleaner_variable import quote_if_needed

class GenExternalTask(GenTask):

    _attr_ExtTask = [AttrDescription('workingDirectory',types.StringType, 'simpleLineEdit', GenTask.zone,GenTask.set_zone,True),
                     AttrDescription('logdir',types.StringType, 'simpleLineEdit', GenTask.zone,GenTask.set_zone,False),
                     AttrDescription('block',types.BooleanType, 'simpleCheck', GenTask.zone,GenTask.set_zone,True),
                     AttrDescription('daemon',types.BooleanType, 'simpleCheck', GenTask.zone,GenTask.set_zone,True),
                     # more
                     AttrDescription('env_RemoveQVars',types.BooleanType, 'simpleCheck', GenTask.zone,GenTask.set_zone,True),
                     AttrDescription('env_RemoveEnvVars',types.BooleanType, 'simpleCheck', GenTask.zone,GenTask.set_zone,True),
                     AttrDescription('postExec',types.StringType, 'multipleLineEdit', GenTask.eval_zone,GenTask.set_eval_zone,False),
                     AttrDescription('preExec',types.StringType, 'multipleLineEdit', GenTask.eval_zone,GenTask.set_eval_zone,False),
                     # remote execution
                     AttrDescription('host',types.StringType, 'simpleLineEdit', GenTask.zone,GenTask.set_zone,False),
                     AttrDescription('display',types.StringType, 'simpleLineEdit', GenTask.zone,GenTask.set_zone,False),

                     AttrDescription('_command',types.StringType, 'noEdit', GenTask.zone,GenTask.set_zone,True)
                     ]

    _LockupExtAttr = dict()
    for i in _attr_ExtTask:
        _LockupExtAttr[i.name] = i

    def __init__(self):
        super(GenExternalTask, self).__init__()

    @classmethod
    def get_lock_up(cls):
        return cls._LockupExtAttr

    def update_with(self,atask,lockup = None,attribList=None):
        super(GenExternalTask, self).update_with(atask,
                                                 GenExternalTask._LockupExtAttr,
                                                 GenExternalTask._attr_ExtTask)

    def to_python(self,stream,acontext):
        # we build a method to handle the remote code
        # on this stream we only call that method
        super(GenExternalTask, self).to_python(stream,acontext)

        callFunction = self.get_function_name(acontext,self.getName())
        remoteCallFunction = "remote_%s" % callFunction
        tab = saveTab = acontext['tab']

        #if acontext.has_key('packageName'):
        #    packageName = acontext['packageName']


        preExec  = GenExternalTask._LockupExtAttr['preExec'].get(self,'preExec')
        if preExec != None and preExec != "":
            sc = preExec.split("\n")
            for i in sc:
                stream.write("%s%s\n" % (tab,i))

        stream.write("%sself.%s(RTD,CFD,TP)\n" % (acontext['tab'],callFunction))

        # main stream
        # write the call to the method
        postExec  = GenExternalTask._LockupExtAttr['postExec'].get(self,'postExec')
        if postExec != None and postExec != "":
            sc = postExec.split("\n")
            for i in sc:
                stream.write("%s%s\n" % (tab,i))


        workingDirectory  = GenExternalTask._LockupExtAttr['workingDirectory'].get(self,'workingDirectory')
        block = GenExternalTask._LockupExtAttr['block'].get(self,'block')
        daemon = GenExternalTask._LockupExtAttr['daemon'].get(self,'daemon')
        env_RemoveQVars  = GenExternalTask._LockupExtAttr['env_RemoveQVars'].get(self,'env_RemoveQVars')
        env_RemoveEnvVars = GenExternalTask._LockupExtAttr['env_RemoveEnvVars'].get(self,'env_RemoveEnvVars')

        host  = GenExternalTask._LockupExtAttr['host'].get(self,'host')
        display  = GenExternalTask._LockupExtAttr['display'].get(self,'display')


        # start a new stream
        tabInc = acontext['tabInc']
        tab = tabInc # that where method start

        # start a new stream
        stream2 = GenTask.push_stream(acontext,stream,callFunction)
        saveImport = GenTask.copy_reset_import_statement(acontext)
        # write the new method definition definition
        stream2.write("\n")
        stream2.write(tab + "#" * 30 + "\n")
        stream2.write(tabInc + "def %s(self,RTD,CFD,TP):\n" % (callFunction))

        # write the local function definition for the remote client code
        tab = tabInc * 2

        stream2.write("\n")
        stream2.write(tab + "def %s(RTD,CFD,TP):\n" % (remoteCallFunction))

        # remote client code
        acontext['tab'] = tab = tabInc * 3
        self.traverse_with_tab(stream2,"to_python",acontext)

        # manage the subprocess syntax
        tab = tabInc * 2
        
        dumpline = list()
        
        
        dumpline.append(tab)
        dumpline.append(tab + "if TP.is_remote():")
        dumpline.append(tab + tabInc + "TP.set_remote(False)")
        # we are in the remote code
        dumpline.append(tab + tabInc + "return %s(RTD,CFD,TP)" % (remoteCallFunction))
        dumpline.append(tab + "else:")

        dumpline.append(tab + tabInc + "from dsk.base.lib.wrapper_xenvi import WrapperxEnvi")
        dumpline.append(tab)
        stream2.write("\n".join(dumpline))
        '''
        stream2.write(tab + tabInc + "import os\n")
        stream2.write(tab + tabInc + "import subprocess\n")
        stream2.write(tab + tabInc + "TP.set_remote(True)\n")

        # this is where the serialiation can happen
        acmd = "p = subprocess.Popen("
        stream2.write(tab + tabInc + acmd)
        # start args
        stream2.write("['python',__file__,self.__class__.__name__,%r" % callFunction)
        stream2.write(",RTD.serialize(),CFD.serialize(),TP.serialize()]")
        if workingDirectory != None and workingDirectory != "":
            stream2.write(",cwd= %s" %  quote_if_needed(workingDirectory))

        # end function call ( close paranthesis and newline
        stream2.write(")\n")

        stream2.write(tab + tabInc + "TP.set_remote(False)\n")
        if(block != None and block == True):stream2.write(tab + tabInc + "os.waitpid(p.pid, 0)[1]\n")
        else:stream2.write(tab + tabInc + "# no wait\n")
        stream2.write(tab + tabInc + "return\n")

        '''
        # restore the context
        acontext['tab'] = saveTab
        GenTask.reload_import_statement(saveImport,acontext)
        # here we define the function that will be call
        if block != None: stream2.write(tab + "#-->bool(%s)" % block + " wait\n")
        if daemon != None: stream2.write(tab + "#-->bool(%s)" % daemon + " daemon\n")

        if env_RemoveQVars != None: stream2.write(tab + "#-->bool(%s)" %  env_RemoveQVars + " env_RemoveQVars\n")
        if env_RemoveEnvVars != None: stream2.write(tab + "#-->bool(%s)" %  env_RemoveEnvVars + " env_RemoveEnvVars\n")
        if postExec != None: stream2.write(tab + "#-->" +  postExec + " postExec\n")
        if host != None: stream2.write(tab + "#-->" +  host + " host\n")
        if display != None: stream2.write(tab + "#-->" +  display + " display\n")
        stream2.write("\n")
        acontext['tab'] =  tab  # start at the function of the class
        # restore where we left it
        acontext['tab'] = saveTab
        return False # we take care of the traversing


class GenSysTask(GenExternalTask):
    def __init__(self):
        super(GenSysTask, self).__init__()

    def update_with(self,atask,lockup = None,attribList=None):
        super(GenSysTask, self).update_with(atask)
        '''
        if hasattr(atask,'failOnSTDERR'): self.failOnSTDERR = atask.failOnSTDERR
        if hasattr(atask,'stderrToStdout'): self.stderrToStdout = atask.stderrToStdout
        if hasattr(atask,'env_RemoveQVars'): self.env_RemoveQVars = atask.env_RemoveQVars
        if hasattr(atask,'env_RemoveEnvVars'): self.env_RemoveEnvVars = atask.env_RemoveEnvVars
        # string
        if hasattr(atask,'command'): self.shell = atask.command
        if hasattr(atask,'shell'): self.shell = atask.shell
        if hasattr(atask,'output') and atask.output != None: self.output = atask.output
        if hasattr(atask,'preExec') and atask.preExec != None: self.preExec = atask.preExec
        if hasattr(atask,'postExec') and atask.postExec != None: self.postExec = atask.postExec
        if hasattr(atask,'workingDirectory') and atask.workingDirectory != None: self.workingDirectory = atask.workingDirectory
        '''


################################################
# qtask
################################################
class GenQTask(GenExternalTask):
    def __init__(self):
        super(GenQTask, self).__init__()

class GenQSubmitTask(GenExternalTask):
    def __init__(self):
        super(GenQSubmitTask, self).__init__()

################################################
# external task: new process space
################################################
class GenQProcessTask(GenExternalTask):
    def __init__(self):
        super(GenQProcessTask, self).__init__()

################################################
# maya
################################################
class GenMayaTask(GenExternalTask):
    def __init__(self):
        super(GenMayaTask, self).__init__()

################################################
class GenQMayaTask(GenQProcessTask):
    def __init__(self):
        super(GenQMayaTask, self).__init__()
