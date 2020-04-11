_DATA='''import os

from dsk.base.lib.base_editor import BaseEditor
from %(name_space)s.%(module_name)s.resources import %(file_root_name)s_signal as lconfsg
# in case you need to over write signal
from dsk.base.resources import browser_signal as confsg
from dsk.base.utils.msg_utils import MsgUtils as log

class %(TplToolsClassRoot)sEditor(BaseEditor):
    """Editor to support %(name_space)s.%(module_name)s
    """
    def __init__(self, **args):
        super(%(TplToolsClassRoot)sEditor, self).__init__(**args)

    def init_signal(self):
        super(%(TplToolsClassRoot)sEditor, self).init_signal()
        self.declare_signal(lconfsg.%(tool_signal_name)s,
                            self.callback,
                            confsg.SINGLE_ARG)

    def callback(self, msg):
        log.info(msg)
        msg.setGroup(self._currentGroup)
        msg.setSuccess(True)
        self.reemit(self._signalAssign[lconfsg.%(tool_signal_name)s.name],msg)

'''