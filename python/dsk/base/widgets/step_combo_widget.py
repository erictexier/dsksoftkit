from dsk.base.widgets.simpleqt import QtT

from dsk.base.resources import browser_signal as confsig
from dsk.base.resources.browser_constant import CASH_SHOW_GEN
from dsk.base.db_helper.db_cache import DbCache
from dsk.base.lib.msg_arg import MsgStepChange
#from dsk.base.utils.msg_utils import MsgUtils as log


class StepSelectCombo(QtT.QtWidgets.QComboBox):
    def __init__(self,parent):
        super(StepSelectCombo,self).__init__(parent)
        self.filtertype = set()
        # a optional filter see set_filtering
        self._hasfiltering = None
        self.active_step = None
    ############### APPLICATION SIGNAL
    def signalsDestroy(self,effectEditor):
        if effectEditor != None:
            self.__actionSignal(effectEditor.request_disconnect)

    def signalsCreate(self,effectEditor):
        if effectEditor != None:
            self.__actionSignal(effectEditor.request_connect)

    def __actionSignal(self,act):
        act(self,confsig.INIT_FIRST_TIME.name, False, self.initFirstTime)
        act(self,confsig.CHANGE_STEP.name, True, self.refresh_curstep)
        act(self,confsig.CHANGE_PREF_STEP.name, False, self.refresh_from_filter)

    def connectLocalSignal(self):
        self.activated.connect(self.selectstepchange)

    def disconnectLocalSignal(self):
        try:
            self.activated.disconnect(self.selectstepchange)
        except:
            pass

    ###############
    def initFirstTime(self, msg):
        if self != msg.widgetFrom() and msg.isAppLevel() == False:
            return

        if self._hasfiltering != None:
            self.set_filter_type(self._hasfiltering.get_filter_list())
        self.init_step(msg.getGroup())

    def set_filter_type(self,filterlist):
        if isinstance(filterlist,str):
            filterlist = [filterlist]
        self.filtertype = set(filterlist)

    def set_filtering(self, filterobject):
        self._hasfiltering = filterobject

    def init_step(self,groupData):
        db = groupData.find(CASH_SHOW_GEN,justChild = True)
        self.disconnectLocalSignal()
        if isinstance(db,DbCache):
            self.clear()

            showsteps = db.get_steps()
            allstepname = [x.getName() for x in showsteps]
            active_step = self.active_step

            allstepname = sorted(set(allstepname))

            if len(self.filtertype) == 0:
                for i,n  in enumerate(allstepname):
                    self.addItem(self.tr(str(n)))
                    if active_step == n:
                        self.setCurrentIndex(i) # because of the blank

            else:
                index = 0
                for i,n  in enumerate(allstepname):
                    if n in self.filtertype:
                        self.addItem(self.tr(str(n)))
                        if active_step== n:
                            self.setCurrentIndex(index) # because of the blank
                        index += 1

        self.connectLocalSignal()

    def refresh_from_filter(self,msg):
        if msg.succeed():
            dict_changed = msg.get_stepfilter_change()
            alist = list()
            for a in dict_changed:
                if dict_changed[a] == True:
                    alist.append(a)
            self.set_filter_type(alist)
            self.init_step(msg.getGroup())


    def refresh_curstep(self,msg):
        if msg.succeed() and msg.widgetFrom() != self:
            self.active_step = msg.getStepName()
            self.init_step(msg.getGroup())

    def selectstepchange(self):
        item = self.currentText()
        if item:
            msg = MsgStepChange(self,None,str(item))
            self.sig[confsig.CHANGE_STEP.name].emit(msg)

    # direct query
    def get_data(self):
        return str(self.currentText())