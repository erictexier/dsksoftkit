import types
import re
from dsk.base.utils.msg_utils import MsgUtils as log
from dsk.base.tdata.taskdata.gen_task import GenTask,AttrDescription
from dsk.base.tdata.taskdata.cleaner_variable import do_clean_command

class GenMelTask(GenTask):
    _attr_MelTask = [AttrDescription('source',types.StringType, 'simpleLineEdit', GenTask.zone, GenTask.set_zone,False),
                     AttrDescription('command',types.StringType, 'multipleLineEdit', GenTask.eval_zone,GenTask.set_eval_zone,True),
                     AttrDescription('output',types.BooleanType, 'simpleLineEdit', GenTask.eval_zone,GenTask.set_eval_zone,False),
                     AttrDescription('evalEcho',types.BooleanType, 'simpleCheck', GenTask.zone,GenTask.set_zone,False)
                     ]
    _LockupMelAttr = dict()
    for i in _attr_MelTask:
        _LockupMelAttr[i.name] = i

    def __init__(self):
        super(GenMelTask, self).__init__()

    @classmethod
    def get_lock_up(cls):
        return cls._LockupMelAttr

    def update_with(self,atask,lockup = None,attribList=None):
        super(GenMelTask, self).update_with(atask,GenMelTask._LockupMelAttr,GenMelTask._attr_MelTask)

    def to_python(self,stream,acontext):
        super(GenMelTask, self).to_python(stream,acontext)

        # command
        command = GenMelTask._LockupMelAttr['command'].get(self,'command')
        if command == None:
            log.error("'command' is required for a mel task")
            return

        # output
        output = GenMelTask._LockupMelAttr['output'].get(self,'output')

        # source
        source = GenMelTask._LockupMelAttr['source'].get(self,'source')

        module = "maya.mel"
        tab = acontext['tab']

        GenTask.do_python_module(stream,acontext,tab,module)

        if source != None:
            stream.write(("%smaya.mel.eval('" % tab) + ('source "%s"' % source) + "')\n")

        res = do_clean_command(command)
        final = ""
        if res.success:
            if output == None:
                final = ("%smaya.mel.eval('" % tab) + res.newCommand + "'" + res.addOn + ")"
            else:
                final = ("%s%s = maya.mel.eval('" % (tab,output)) + res.newCommand +  "'" + res.addOn + ")"
        else:
            if output == None:
                final = ("%smaya.mel.eval('" % tab) + command + "')"
            else:
                final = ("%s%s = maya.mel.eval('" % (tab,output)) + command + "')"

        evalEcho = GenMelTask._LockupMelAttr['evalEcho'].get(self,'evalEcho')
        if evalEcho == True:
            p = re.compile("\(.*\)",re.DOTALL)
            m = p.search(final)
            if m:
                stream.write("%sprint%s\n" % (tab,m.group()))
            stream.write(final + "\n")
            if output != None: stream.write("%sprint 'return value " % tab + "%s' % "  + output + "\n")
        else:
            stream.write(final + "\n")
        return True
