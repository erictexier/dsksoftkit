_DATA='''try:
#from dsk.base.widgets.simpleqt import QtT
from dsk.base.lib.application_path import ApplicationPath
from dsk.base.resources import browser_signal as confsig
from %(name_space)s.%(module_name)s.resources import %(file_root_name)s_info
ap = ApplicationPath(%(file_root_name)s_info)

from dsk.base.widgets.container_widget import ContainerWidget

from %(name_space)s.%(module_name)s.widgets.%(file_root_name)s_widget import %(TplToolsClassRoot)sWidget

################################################
# ui file
ui_path = ap.get_ui("%(file_root_name)s_main.ui")
ui_object, ui_baseClass = QtT.uic.loadUiType(ui_path)

class %(TplToolsClassRoot)sMain(ui_baseClass, ui_object):
    """Main window for %(module_name)s
    """

    def __init__(self, parent,**argv):
        """init the %(module_name)s main menu
        """
        super(%(TplToolsClassRoot)sMain, self).__init__(parent)
        self.setupUi(self)

        awid = %(TplToolsClassRoot)sWidget(None)
        container = ContainerWidget()
        container.updateLabel("")
        self._widgetList = list()
        self._widgetList.append(awid)
        container.addListOfWidget(self._widgetList, needStretch=True)

        self.task_browser_tabs.addTab(container,"Tasks")
        #self.launch_browser_tabs.addTab(container,"App")

    ############### APPLICATION SIGNAL
    def signalsDestroy(self,effectEditor):
        if effectEditor != None:
            self._actionSignal(effectEditor.request_disconnect)
            for w in self._widgetList:
                w.signalsDestroy(effectEditor)

    ###############
    def signalsCreate(self,effectEditor):
        if effectEditor != None:
            self._actionSignal(effectEditor.request_connect)
            for w in self._widgetList:
                w.signalsCreate(effectEditor)

    ###############
    def _actionSignal(self,act):
        act(self,confsig.INIT_FIRST_TIME.name,False,self.initFirstTime)

    ###############
    def initFirstTime(self, msg):
        if msg.isAppLevel() == True:
            # nothing special, each child widget will get its initFirstTime
            return

        if self != msg.widgetFrom():
            return
        for w in self._widgetList:
            msg.setWidgetFrom(w)
            w.initFirstTime(msg)
        msg.setWidgetFrom(self)

'''