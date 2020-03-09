import types
from dsk.base.tdata.taskdata.gen_task import GenTask,AttrDescription


from dsk.base.tdata.taskdata.cleaner_variable import clean_quote

class GenIfTask(GenTask):
    _attr_CtlTask = [AttrDescription('condition',types.StringType,
                                     'simpleLineEdit', GenTask.eval_zone, GenTask.set_eval_zone,False)]

    _LockupCtlAttr = dict()
    for i in _attr_CtlTask:
        _LockupCtlAttr[i.name] = i

    def __init__(self):
        super(GenIfTask, self).__init__()
        self.pythonString = "if"

    @classmethod
    def get_lock_up(cls):
        return cls._LockupCtlAttr

    def update_with(self,atask,lockup = None,attribList=None):
        super(GenIfTask, self).update_with(atask,
                                           GenIfTask._LockupCtlAttr,
                                           GenIfTask._attr_CtlTask)

    def to_python(self,stream,acontext):
        super(GenIfTask, self).to_python(stream,acontext)
        # here we have to increment
        tab = acontext['tab']
        incrTab = acontext['tabInc']
        condition = GenIfTask._LockupCtlAttr['condition'].get(self,'condition')

        if condition != None:
            # some condition are getting replace with except:
            if condition.find("hasFailed") != -1:
                stream.write("%sexcept:\n" % (tab))
            else:
                stream.write("%s%s %s:\n" % (tab,self.pythonString, clean_quote(condition)))
        else:
            stream.write("%s%s:\n" % (acontext['tab'],self.pythonString))
        acontext['tab'] += incrTab
        return True

################################################
class GenElseTask(GenIfTask):
    def __init__(self):
        super(GenElseTask, self).__init__()
        self.pythonString = "else"
################################################
class GenElifTask(GenElseTask):
    def __init__(self):
        # same as if
        super(GenElifTask, self).__init__()
        self.pythonString = "elif"
################################################
class GenWhileTask(GenIfTask):
    def __init__(self):
        super(GenWhileTask, self).__init__()
        self.pythonString = "while"

################################################
class GenWaitForTask(GenWhileTask):
    def __init__(self):
        super(GenWaitForTask, self).__init__()
        self.pythonString = "while"

################################################
class GenForEachTask(GenTask):
    _attr_ForTask = [AttrDescription('container',types.StringType, 'simpleLineEdit', GenTask.eval_zone, GenTask.set_eval_zone,True),
                     AttrDescription('output',types.StringType, 'simpleLineEdit', GenTask.eval_zone, GenTask.set_eval_zone,False)
                     ]

    _LockupForAttr = dict()
    for i in _attr_ForTask:
        _LockupForAttr[i.name] = i

    def __init__(self):
        super(GenForEachTask, self).__init__()
        self.pythonString = "for %s in %s"

    def update_with(self,atask,lockup = None,attribList=None):
        super(GenForEachTask, self).update_with(atask,
                                                GenForEachTask._LockupForAttr,
                                                GenForEachTask._attr_ForTask)

    def to_python(self,stream,acontext):
        super(GenForEachTask, self).to_python(stream,acontext)
        # here we have to increment
        tab = acontext['tab']
        incrTab = acontext['tabInc']
        container = GenForEachTask._LockupForAttr['container'].get(self,'container')
        output = GenForEachTask._LockupForAttr['output'].get(self,'output')

        if container != None and container != "":
            out = None
            if output != None and output != "":
                out = clean_quote(output)
            else:
                out = 'item'
            over = clean_quote(container)
            command = self.pythonString % (out,over)
            stream.write("%s%s:\n" % (tab,command))
        acontext['tab'] += incrTab
        return True