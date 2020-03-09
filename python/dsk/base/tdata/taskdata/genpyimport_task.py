import types

from dsk.base.utils.msg_utils import MsgUtils as log
from dsk.base.tdata.taskdata.gen_task import GenTask,AttrDescription

class GenPyImportTask(GenTask):
    _attr_ImportTask = [AttrDescription('command',
                                        types.StringType,
                                        'multipleLineEdit',
                                        GenTask.eval_zone,
                                        GenTask.set_eval_zone,True)]
    _LockupImportAttr = dict()
    for i in _attr_ImportTask:
        _LockupImportAttr[i.name] = i

    def __init__(self):
        super(GenPyImportTask, self).__init__()

    @classmethod
    def get_lock_up(cls):
        return cls._LockupImportAttr

    def update_with(self,atask,lockup = None,attribList=None):
        super(GenPyImportTask, self).update_with(atask,GenPyImportTask._LockupImportAttr,GenPyImportTask._attr_ImportTask)

    def to_python(self,stream,acontext):
        super(GenPyImportTask, self).to_python(stream,acontext)
        # command
        command = GenPyImportTask._LockupImportAttr['command'].get(self,'command')
        if command == None:
            log.error("'import contents' is required for an import task")
            return False

        scommand = command.split("\n")
        for c in scommand:
            stream.write("%s%s\n" % (acontext['tab'],c))
        return True
