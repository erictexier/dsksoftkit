from dsk.base.widgets.simpleqt import QtT

#from dsk.base.lib.default_path import DefaultPath
from dsk.base.resources import browser_signal as confsig

from dsk.base.resources.browser_constant import CASH_SHOW_GEN
from dsk.base.db_helper.db_cache import DbCache
from dsk.base.lib.msg_arg import MsgShotChange

class ShotSelectCombo(QtT.QtWidgets.QComboBox):
    def __init__(self,parent):
        super(ShotSelectCombo,self).__init__(parent)
    ############### APPLICATION SIGNAL
    def signalsDestroy(self,effectEditor):
        if effectEditor != None:
            self.__actionSignal(effectEditor.request_disconnect)

    def signalsCreate(self,effectEditor):
        if effectEditor != None:
            self.__actionSignal(effectEditor.request_connect)

    def __actionSignal(self,act):
        act(self,confsig.INIT_FIRST_TIME.name,False,self.initFirstTime)
        act(self,confsig.CHANGE_SHOW.name,False,self.refresh_show)
        act(self,confsig.CHANGE_SEQUENCE.name,False,self.refresh_seq)
        act(self,confsig.CHANGE_SHOT.name,True,self.refresh_curshot)

    def connectLocalSignal(self):
        self.activated.connect(self.selectshotchange)

    def disconnectLocalSignal(self):
        try:
            self.activated.disconnect(self.selectshotchange)
        except:
            pass
    ###############
    def initFirstTime(self, msg):
        if self != msg.widgetFrom() and msg.isAppLevel() == False:
            return
        self.init_shot(msg.getGroup())

    def init_shot(self,group_data):
        db = group_data.find(CASH_SHOW_GEN,justChild = True)
        self.disconnectLocalSignal()
        if isinstance(db,DbCache):
            self.clear()
            curshow = db.get_current_show_obj()
            if curshow == None:
                return
            allshot = curshow.get_current_shotlist_names()
            seqobj = curshow.get_current_sequence_obj()
            curshot = ""
            if seqobj:
                curshot = seqobj.get_current_shotname()
            for i,n in enumerate(allshot):
                self.addItem(self.tr(n))
                if curshot == n:
                    self.setCurrentIndex(i)
        self.connectLocalSignal()

    def refresh_show(self,msg):
        if msg.succeed():
            self.init_shot(msg.getGroup())

    def refresh_seq(self,msg):
        if msg.succeed():
            self.init_shot(msg.getGroup())

    def refresh_curshot(self,msg):
        if msg.succeed() and msg.widgetFrom() != self:
            self.init_shot(msg.getGroup())

    def selectshotchange(self):
        item = self.currentText()
        if item:
            msg = MsgShotChange(self,None,str(item))
            self.sig[confsig.CHANGE_SHOT.name].emit(msg)

    # direct query
    def get_data(self):
        return str(self.currentText())
