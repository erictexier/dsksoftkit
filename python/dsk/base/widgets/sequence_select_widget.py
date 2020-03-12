from dsk.base.widgets.simpleqt import QtT


from dsk.base.lib.default_path import DefaultPath
from dsk.base.resources import browser_signal as confsig
from dsk.base.resources.browser_constant import CASH_SHOW_GEN
from dsk.base.lib.msg_arg import MsgSeqChange
from dsk.base.db_helper.db_cache import DbCache


class itemEdit(QtT.QtWidgets.QListWidgetItem):
    def __init__(self,parent = None):
        QtT.QtWidgets.QListWidgetItem.__init__(self,parent)
        #self.setFlags(QtT.QtCore.Qt.ItemIsEditable | QtT.QtCore.Qt.ItemIsEnabled | QtT.QtCore.Qt.ItemIsSelectable )
        self.setFlags( QtT.QtCore.Qt.ItemIsEnabled | QtT.QtCore.Qt.ItemIsSelectable)

class SequenceSelectWidget(QtT.QtWidgets.QWidget):
    def __init__(self,parent):
        super(SequenceSelectWidget,self).__init__(parent)
        self.ui = QtT.uic.loadUi(DefaultPath.getUiFile("sequence_select"), self)
        self.ui.filterLabel.hide()
        self.ui.filterLineEdit.hide()
        self.connectLocalSignal()

    def connectLocalSignal(self):
        self.ui.sequenceListWidget.itemSelectionChanged.connect(self.selectseqchange)

    def disconnectLocalSignal(self):
        self.ui.sequenceListWidget.itemSelectionChanged.disconnect(self.selectseqchange)

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
        item = self.ui.sequenceListWidget.currentItem()
        if item:
            msg = MsgSeqChange(self,None,str(item.text()))
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
            self.ui.sequenceListWidget.clear()
            if curshow == None:
                return
            seq = curshow.get_current_sequencename()
            allseq = curshow.get_sequence_names()
            for i in sorted(allseq):
                item = itemEdit(self.ui.sequenceListWidget)
                item.setText(self.tr(str(i)))
                if seq == i:
                    self.ui.sequenceListWidget.setCurrentItem(item)

        self.connectLocalSignal()

    def refresh_show(self,msg):
        if msg.succeed() and msg.widgetFrom() != self:
            self.init_sequence(msg.getGroup())
