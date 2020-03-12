from dsk.base.widgets.simpleqt import QtT


from dsk.base.resources import browser_signal as confsig
from dsk.base.resources.browser_constant import CASH_SHOW_GEN
from dsk.base.lib.msg_arg import MsgSeqChange

from dsk.base.db_helper.db_cache import DbCache


class SequenceSelectCombo(QtT.QtWidgets.QComboBox):
    def __init__(self,parent):
        super(SequenceSelectCombo,self).__init__(parent)
        self.connectLocalSignal()

    def connectLocalSignal(self):
        self.activated.connect(self.selectseqchange)

    def disconnectLocalSignal(self):
        self.activated.connect(self.selectseqchange)

    ############### APPLICATION SIGNAL
    def signalsDestroy(self,effectEditor):
        if effectEditor != None:
            self.__actionSignal(effectEditor.request_disconnect)

    def signalsCreate(self,effectEditor):
        if effectEditor != None:
            self.__actionSignal(effectEditor.request_connect)

    def __actionSignal(self,act):
        act(self,confsig.INIT_FIRST_TIME.name,False, self.initFirstTime)
        act(self,confsig.CHANGE_SHOW.name,True, self.refresh_show)
        act(self,confsig.CHANGE_SEQUENCE.name,True, self.refresh_show)

    def selectseqchange(self):
        item = self.currentText()
        if item:
            msg = MsgSeqChange(self,None,str(item))
            self.sig[confsig.CHANGE_SEQUENCE.name].emit(msg)

    ###############
    def initFirstTime(self, msg):
        if self != msg.widgetFrom() and msg.isAppLevel() == False:
            return
        self.init_sequence(msg.getGroup())

    def init_sequence(self,groupData):
        db = groupData.find(CASH_SHOW_GEN,justChild = True)
        self.disconnectLocalSignal()
        if isinstance(db,DbCache):
            curshow = db.get_current_show_obj()
            self.clear()
            if curshow == None:
                return
            seq = curshow.get_current_sequencename()
            allseq = curshow.get_sequence_names()
            for i,n in enumerate(sorted(allseq)):
                self.addItem(self.tr(n))
                if seq == n:
                    self.setCurrentIndex(i)

        self.connectLocalSignal()

    def refresh_show(self,msg):
        if msg.succeed():
            self.init_sequence(msg.getGroup())

    def get_data(self):
        return str(self.currentText())
