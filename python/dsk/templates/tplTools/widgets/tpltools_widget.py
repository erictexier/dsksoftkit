_DATA='''try:
from dsk.base.widgets.simpleqt import QtT
from dsk.base.lib.application_path import ApplicationPath
from dsk.base.resources import browser_signal as confsig
from %(name_space)s.%(module_name)s.resources import %(file_root_name)s_signal as lconfsg
from %(name_space)s.%(module_name)s.resources import %(file_root_name)s_info

# a message is needed
from %(name_space)s.%(module_name)s.resources.%(file_root_name)s_msgarg import Msg%(TplToolsClassRoot)s

ap = ApplicationPath(%(file_root_name)s_info)
ui_path = ap.get_ui("example_widget.ui")

class %(TplToolsClassRoot)sWidget(QtT.QtWidgets.QWidget):

    def __init__(self,parent, **argv):
        super(%(TplToolsClassRoot)sWidget, self).__init__(parent)
        self.ui = QtT.uic.loadUi(ui_path, self)

        # local signal example
        self.ui.pushButton.clicked.connect(self.emitexample)

    def emitexample(self):
        """Emit a global signal with a type message"""
        msg = Msg%(TplToolsClassRoot)s(self,None)
        self.sig[lconfsg.%(tool_signal_name)s.name].emit(msg)

    ############### APPLICATION SIGNAL
    def signalsDestroy(self,effectEditor):
        if effectEditor != None:
            self.__actionSignal(effectEditor.request_disconnect)

    def signalsCreate(self,effectEditor):
        if effectEditor != None:
            self.__actionSignal(effectEditor.request_connect)

    def __actionSignal(self,act):
        act(self, confsig.INIT_FIRST_TIME.name,False,self.initFirstTime)
        act(self, lconfsg.%(tool_signal_name)s.name,True,self.refresh_me)

    def initFirstTime(self, msg):
        if self != msg.widgetFrom() and msg.isAppLevel() == False:
            return
        self.display_me(msg.getGroup())

    def refresh_me(self,msg):
        if msg.succeed():
            self.display_me(msg.getGroup())

    def display_me(self, group):
        print("in display me",group)
'''