from dsk.base.widgets.simpleqt import QtT

from dsk.base.resources import browser_signal as confsig
from dsk.base.resources.browser_constant import CASH_SHOW_GEN
from dsk.base.db_helper.db_cache import DbCache
from dsk.base.lib.msg_arg import MsgAssetChange
#from dsk.base.utils.msg_utils import MsgUtils as log


class AssetSelectCombo(QtT.QtWidgets.QComboBox):
    def __init__(self,parent):
        super(AssetSelectCombo,self).__init__(parent)
        self.filtertype = set()
        # a optional filter see set_filtering
        self._hasfiltering = None

    ############### APPLICATION SIGNAL
    def signalsDestroy(self,effectEditor):
        if effectEditor != None:
            self.__actionSignal(effectEditor.request_disconnect)

    def signalsCreate(self,effectEditor):
        if effectEditor != None:
            self.__actionSignal(effectEditor.request_connect)

    def __actionSignal(self,act):
        act(self,confsig.INIT_FIRST_TIME.name, False, self.initFirstTime)
        act(self,confsig.CHANGE_SHOW.name, False, self.refresh_show)
        act(self,confsig.CHANGE_ASSET.name, True, self.refresh_curasset)
        act(self,confsig.CHANGE_ASSET_PREF_TYPE.name, False, self.refresh_type)

    def connectLocalSignal(self):
        self.activated.connect(self.selectassetchange)

    def disconnectLocalSignal(self):
        try:
            self.activated.disconnect(self.selectassetchange)
        except:
            pass
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

    def refresh_type(self, msg):
        if msg.succeed():
            dict_changed = msg.get_assettype_change()
            alist = list()
            for a in dict_changed:
                if dict_changed[a] == True:
                    alist.append(a)
            self.set_filter_type(alist)
            self.init_asset(msg.getGroup())


    def init_asset(self,groupData):
        db = groupData.find(CASH_SHOW_GEN,justChild = True)
        self.disconnectLocalSignal()
        if isinstance(db,DbCache):
            self.clear()
            curshow = db.get_current_show_obj()
            if curshow == None:
                return
            curasset = curshow.get_current_asset()
            allasset = curshow.get_assets().getChildren()
            allassetname = [x.getName() for x in allasset]

            if len(self.filtertype) == 0:
                for i,n  in enumerate(allassetname):
                    self.addItem(self.tr(str(n)))
                    if curasset == n:
                        self.setCurrentIndex(i)
            else:
                allassetype = [x.get_asset_type() for x in allasset]
                index = 0
                for i,n  in enumerate(allassetname):
                    if allassetype[i] in self.filtertype:
                        self.addItem(self.tr(str(n)))
                        if curasset == n:
                            self.setCurrentIndex(index)
                        index += 1

        self.connectLocalSignal()

    def refresh_show(self,msg):
        if msg.succeed():
            self.init_asset(msg.getGroup())

    def refresh_curasset(self,msg):
        if msg.succeed() and msg.widgetFrom() != self:
            self.init_asset(msg.getGroup())

    def selectassetchange(self):
        item = self.currentText()
        if item:
            msg = MsgAssetChange(self,None,str(item))
            self.sig[confsig.CHANGE_ASSET.name].emit(msg)

    # direct query
    def get_data(self):
        return str(self.currentText())