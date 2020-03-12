from dsk.base.widgets.simpleqt import QtT

from dsk.base.lib.default_path import DefaultPath
from dsk.base.resources import browser_signal as confsig
from dsk.base.resources.browser_constant import CASH_SHOW_GEN
from dsk.base.lib.msg_arg import MsgShowChange
from dsk.base.db_helper.db_cache import DbCache


class ShowSelectWidget(QtT.QtWidgets.QWidget):
    def __init__(self,parent):
        super(ShowSelectWidget,self).__init__(parent)
        self.ui = QtT.uic.loadUi(DefaultPath.getUiFile("show_select"), self)

    ############### APPLICATION SIGNAL
    def signalsDestroy(self,effectEditor):
        if effectEditor != None:
            self.__actionSignal(effectEditor.request_disconnect)

    def signalsCreate(self,effectEditor):
        if effectEditor != None:
            self.__actionSignal(effectEditor.request_connect)

    def __actionSignal(self,act):
        act(self,confsig.INIT_FIRST_TIME.name,False, self.initFirstTime)
        act(self,confsig.CHANGE_SHOW.name,True,self.refresh_show)

    def connectLocalSignal(self):
        self.ui.allShowCombo.activated.connect(self.selectshowchange)

    def disconnectLocalSignal(self):
        try:
            self.ui.allShowCombo.activated.disconnect(self.selectshowchange)
        except:
            pass
    def selectshowchange(self,index):
        showname = str(self.ui.allShowCombo.currentText())
        msg = MsgShowChange(self,None,showname)
        self.sig[confsig.CHANGE_SHOW.name].emit(msg)

    ###############
    def initFirstTime(self, msg):
        if self != msg.widgetFrom() and msg.isAppLevel() == False:
            return
        self.init_show(msg.getGroup())

    ###############
    def init_show(self,groupData):
        self.disconnectLocalSignal()
        db = groupData.find(CASH_SHOW_GEN,justChild = True)
        self.ui.allShowCombo.clear()
        if isinstance(db,DbCache):
            show_list = db.get_show_names()
            index = 0
            curshow = db.get_current_show_obj()
            for v in show_list:
                self.ui.allShowCombo.addItem(str(v))
                if curshow and v == curshow.getName():
                    self.ui.allShowCombo.setCurrentIndex(index)
                index += 1
        self.connectLocalSignal()

    ###############
    def refresh_show(self,msg):
        if msg.widgetFrom() == self:
            return
        if msg.succeed():
            self.init_show(msg.getGroup())

    def get_data(self):
        return str(self.ui.allShowCombo.currentText())
