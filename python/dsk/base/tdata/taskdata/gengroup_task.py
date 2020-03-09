
from dsk.base.tdata.taskdata.gen_task import GenTask

class GenGroupTask(GenTask):

    def __init__(self):
        super(GenGroupTask, self).__init__()

    def to_python(self,stream,acontext):
        # we build a method to handle the remote code
        # on this stream we only call that method
        super(GenGroupTask, self).to_python(stream,acontext)
        callFunction = self.get_function_name(acontext,self.getName())
        tab = saveTab = acontext['tab']
        stream.write("%sself.%s(RTD,CFD,TP)\n" % (tab,callFunction))
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
        acontext['tab'] = tab + tabInc
        self.traverse_with_tab(stream2,"to_python",acontext)
        stream2.write(tab + tabInc + "return\n")
        # restore the context
        acontext['tab'] = saveTab
        GenTask.reload_import_statement(saveImport,acontext)
