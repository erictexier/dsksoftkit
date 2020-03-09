from dsk.base.tdata.taskdata.gen_task import GenTask

################################################
# UI task
################################################
class GenUiTask(GenTask):
    def __init__(self):
        super(GenUiTask, self).__init__()

    def update_with(self,atask,lockup = None,attribList=None):
        super(GenUiTask, self).update_with(atask)

    def to_python(self,stream,acontext):
        # we build a method to handle the remote code
        # on this stream we only call that method
        super(GenUiTask, self).to_python(stream,acontext)
        stream.write("%sTP.Ui(%r)\n" % (acontext['tab'],self.getName()))