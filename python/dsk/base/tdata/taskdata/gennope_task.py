from dsk.base.tdata.taskdata.gen_task import GenTask

class GenNopeTask(GenTask):
    def __init__(self):
        super(GenNopeTask, self).__init__()
    def to_python(self,stream,acontext):
        return True