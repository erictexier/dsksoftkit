from dsk.base.widgets.simpleqt import QtT

from dsk.base.resources import browser_signal as confsig
from dsk.base.resources.browser_constant import CASH_SHOW_GEN
from dsk.base.db_helper.db_cache import DbCache
from dsk.base.lib.msg_arg import MsgConfigpipeChange
#from dsk.base.utils.msg_utils import MsgUtils as log


class ConfigpipeSelectCombo(QtT.QtWidgets.QComboBox):
    def __init__(self,parent):
        super(ConfigpipeSelectCombo,self).__init__(parent)
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
        act(self,confsig.CHANGE_SHOW.name, True, self.refresh_curconfpipe)
        act(self,confsig.CHANGE_CONFIGPIPE.name, True, self.refresh_curconfpipe)
        act(self,confsig.CHANGE_PREF_CONFIGPIPE.name, False, self.refresh_from_filter)

    def connectLocalSignal(self):
        self.activated.connect(self.selectconfpipechange)

    def disconnectLocalSignal(self):
        try:
            self.activated.disconnect(self.selectconfpipechange)
        except:
            pass
    ###############
    def initFirstTime(self, msg):
        if self != msg.widgetFrom() and msg.isAppLevel() == False:
            return

        if self._hasfiltering != None:
            self.set_filter_type(self._hasfiltering.get_filter_list())
        self.init_configpipe(msg.getGroup())

    def set_filter_type(self,filterlist):
        if isinstance(filterlist,str):
            filterlist = [filterlist]
        self.filtertype = set(filterlist)

    def set_filtering(self, filterobject):
        self._hasfiltering = filterobject

    def init_configpipe(self, groupData):
        db = groupData.find(CASH_SHOW_GEN,justChild = True)
        self.disconnectLocalSignal()
        if isinstance(db,DbCache):
            self.clear()

            curshow = db.get_current_show_obj()
            if curshow == None:
                return

            curconfpipename = db.get_current_confpipe(curshow)
            allconfpipe = curshow.get_confpipes_list()
            if allconfpipe == None:
                return

            if len(self.filtertype) == 0:
                allconfpipename = [x.getName() for x in allconfpipe]
            else:
                allconfpipename = db.get_filtered_confpipesname(allconfpipe, self.filtertype)

            #if len(self.filtertype) == 0:

            for i,n  in enumerate(allconfpipename):
                self.addItem(self.tr(str(n)))
                if curconfpipename == n:
                    self.setCurrentIndex(i)

        self.connectLocalSignal()

    def refresh_from_filter(self,msg):
        if msg.succeed():
            dict_changed = msg.get_configpipefilter_change()
            alist = list()
            for a in dict_changed:
                if dict_changed[a] == True:
                    alist.append(a)
            self.set_filter_type(alist)
            self.init_configpipe(msg.getGroup())


    def refresh_curconfpipe(self,msg):
        if msg.succeed() and msg.widgetFrom() != self:
            self.init_configpipe(msg.getGroup())

    def selectconfpipechange(self):
        item = self.currentText()
        if item:
            msg = MsgConfigpipeChange(self,None,str(item))
            self.sig[confsig.CHANGE_CONFIGPIPE.name].emit(msg)

    # direct query
    def get_data(self):
        return str(self.currentText())