from dsk.base.widgets.simpleqt import QtT

from dsk.base.lib.default_path import DefaultPath
from dsk.base.resources import browser_signal as confsig
from dsk.base.resources.browser_constant import CASH_SHOW_GEN
from dsk.base.db_helper.db_cache import DbCache
from dsk.base.lib.msg_arg import MsgAssetChange
#from dsk.base.utils.msg_utils import MsgUtils as log

class itemEdit(QtT.QtWidgets.QListWidgetItem):
    def __init__(self,parent = None):
        QtT.QtWidgets.QListWidgetItem.__init__(self,parent)
        #self.setFlags(QtT.QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable )
        self.setFlags( QtT.QtCore.Qt.ItemIsEnabled | QtT.QtCore.Qt.ItemIsSelectable)

class AssetSelectWidget(QtT.QtWidgets.QWidget):
    def __init__(self,parent):
        super(AssetSelectWidget,self).__init__(parent)
        self.ui = QtT.uic.loadUi(DefaultPath.getUiFile("asset_select"), self)
        self._hasfiltering = None
        self.filtertype = set()
    ############### APPLICATION SIGNAL
    def signalsDestroy(self,effectEditor):
        if effectEditor != None:
            self.__actionSignal(effectEditor.request_disconnect)

    def signalsCreate(self,effectEditor):
        if effectEditor != None:
            self.__actionSignal(effectEditor.request_connect)

    def __actionSignal(self,act):
        act(self,confsig.INIT_FIRST_TIME.name,False,self.initFirstTime)
        act(self,confsig.CHANGE_SHOW.name,True,self.refresh_show)
        act(self,confsig.CHANGE_ASSET.name, True, self.refresh_curasset)
        act(self,confsig.CHANGE_ASSET_PREF_TYPE.name, False, self.refresh_type)

    def connectLocalSignal(self):
        self.connect(self.ui.assetListWidget,
                     QtT.QtCore.SIGNAL("itemSelectionChanged()"),
                     self.selectassetchange)

    def disconnectLocalSignal(self):
        self.disconnect(self.ui.assetListWidget,
                        QtT.QtCore.SIGNAL("itemSelectionChanged()"),
                        self.selectassetchange)

    ###############
    def initFirstTime(self, msg):
        if self != msg.widgetFrom() and msg.isAppLevel() == False:
            return

        if self._hasfiltering != None:
            self.set_filter_type(self._hasfiltering.get_filter_list())

        self.init_asset(msg.getGroup())

    def set_filter_type(self,filterlist):
        if isinstance(filterlist,str):
            filterlist = [filterlist]
        self.filtertype = set(filterlist)

    def set_filtering(self, filterobject):
        self._hasfiltering = filterobject

    def init_asset(self,groupData):

        db = groupData.find(CASH_SHOW_GEN,justChild = True)
        self.disconnectLocalSignal()
        if isinstance(db,DbCache):
            self.ui.assetListWidget.clear()
            curshow = db.get_current_show_obj()
            if curshow == None:
                return
            allasset = curshow.get_assets().getChildren()
            allassetname = [x.getName() for x in allasset]
            curasset = curshow.get_current_asset()

            if len(self.filtertype) == 0:
                for i in allassetname:
                    item = itemEdit(self.ui.assetListWidget)
                    item.setText(self.tr(str(i)))
                    if curasset == i:
                        self.ui.assetListWidget.setCurrentItem(item)
            else:
                allassetype = [x.get_asset_type() for x in allasset]
                for i,n  in enumerate(allassetname):
                    if allassetype[i] in self.filtertype:
                        item = itemEdit(self.ui.assetListWidget)
                        item.setText(self.tr(str(n)))
                        if curasset == n:
                            self.ui.assetListWidget.setCurrentItem(item)
        self.connectLocalSignal()

    def refresh_show(self,msg):
        if msg.succeed():
            self.init_asset(msg.getGroup())

    def refresh_curasset(self,msg):
        if msg.succeed() and msg.widgetFrom() != self:
            self.init_asset(msg.getGroup())

    def refresh_type(self, msg):
        if msg.succeed():
            dict_changed = msg.get_assettype_change()
            alist = list()
            for a in dict_changed:
                if dict_changed[a] == True:
                    alist.append(a)
            self.set_filter_type(alist)
            self.init_asset(msg.getGroup())

    def selectassetchange(self):
        item = self.ui.assetListWidget.currentItem()
        if item:
            msg = MsgAssetChange(self,None,str(item.text()))
            self.sig[confsig.CHANGE_ASSET.name].emit(msg)

    def get_data(self):
        item = self.ui.assetListWidget.currentItem()
        if item:
            return item.text()
        return ""