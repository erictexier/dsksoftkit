from dsk.base.widgets.simpleqt import QtT

from dsk.base.lib.default_path import DefaultPath
from dsk.base.resources import browser_signal as confsig

from dsk.base.resources.browser_constant import CASH_SHOW_GEN
from dsk.base.db_helper.db_cache import DbCache
from dsk.base.lib.msg_arg import MsgShotChange
#from dsk.base.utils.msg_utils import MsgUtils as log

class itemEdit(QtT.QtWidgets.QListWidgetItem):
    def __init__(self,parent = None):
        QtT.QtWidgets.QListWidgetItem.__init__(self,parent)
        self.setFlags( QtT.QtCore.Qt.ItemIsEnabled | QtT.QtCore.Qt.ItemIsSelectable)

class ShotSelectWidget(QtT.QtWidgets.QWidget):
    def __init__(self,parent):
        super(ShotSelectWidget,self).__init__(parent)
        self.ui = QtT.uic.loadUi(DefaultPath.getUiFile("shot_select"), self)
        self.ui.shotListWidget.itemSelectionChanged.connect(self.selectshotchange)
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
        act(self,confsig.CHANGE_SHOT.name,True, self.refresh_curshot)

    def connectLocalSignal(self):
        #self.ui.shotListWidget.itemSelectionChanged.connect(self.selectshotchange)
        self.ui.shotListWidget.blockSignals(False)

    def disconnectLocalSignal(self):
        #self.ui.shotListWidget.itemSelectionChanged.disconnect(self.selectshotchange)
        self.ui.shotListWidget.blockSignals(True)


    ###############
    def initFirstTime(self, msg):
        if self != msg.widgetFrom() and msg.isAppLevel() == False:
            return
        self.init_shot(msg.getGroup())

    def init_shot(self, groupData):

        db = groupData.find(CASH_SHOW_GEN,justChild = True)
        self.disconnectLocalSignal()
        if isinstance(db,DbCache):
            self.ui.shotListWidget.clear()
            curshow = db.get_current_show_obj()
            if curshow == None:
                return
            allshot = curshow.get_current_shotlist_names()
            seqobj = curshow.get_current_sequence_obj()

            if seqobj:
                curshot = seqobj.get_current_shotname()
            for i in allshot:
                item = itemEdit(self.ui.shotListWidget)
                item.setText(self.tr(str(i)))
                if curshot == i:
                    self.ui.shotListWidget.setCurrentItem(item)
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

        item = self.ui.shotListWidget.currentItem()
        if item:
            msg = MsgShotChange(self,None,str(item.text()))
            self.sig[confsig.CHANGE_SHOT.name].emit(msg)
