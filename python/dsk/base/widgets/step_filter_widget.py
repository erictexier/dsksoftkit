from dsk.base.widgets.simpleqt import QtT

from dsk.base.tdata.gen_tree import GenTree
from dsk.base.widgets.container_widget import ContainerWidget
from dsk.base.db_helper.db_cache import DbCache
from dsk.base.resources.browser_constant import CASH_SHOW_GEN
from dsk.base.resources import browser_signal as confsig
from dsk.base.lib.msg_arg import MsgStepFilterChange

from dsk.base.resources.browser_constant import  WINDOW_NAME_STEPFILTER


class StepFilterWidgetPref(GenTree):
    def __init__(self):
        super(StepFilterWidgetPref,self).__init__()
        self.stepfilterOnOff = dict()

    def set_stepfilter(self,assetype,value = True):
        self.stepfilterOnOff[assetype] = value

    def get_stepfilter(self, stepname):
        if stepname in self.stepfilterOnOff:
            return self.stepfilterOnOff[stepname]
        return False

    def get_filter_dict(self):
        return self.stepfilterOnOff

    def update_data(self,d):
        self.stepfilterOnOff.update(d)


class StepFilterWidget(QtT.QtWidgets.QWidget):
    #######################
    def __init__(self, parent, **parameter):
        super(StepFilterWidget, self).__init__(parent)
        widgetname = parameter.get('object_name', WINDOW_NAME_STEPFILTER)
        self._isradio = False
        if parameter.get('do_radio', False):
            self._button_factory = QtT.QtWidgets.QRadioButton
            self._isradio = True
        else:
            self._button_factory = QtT.QtWidgets.QCheckBox

        self.setObjectName(widgetname)
        self.verticalLayout = QtT.QtWidgets.QVBoxLayout(self)
        #self.verticalLayout.setMargin(0)
        self._myPref = None
        self._togglewidget = list()

    def __actionSignal(self,act):
        act(self,confsig.INIT_FIRST_TIME.name, False, self.initFirstTime)
        act(self,confsig.CHANGE_PREF_STEP.name, True, self.refresh)

    ############### APPLICATION SIGNAL
    def signalsDestroy(self,effectEditor):
        if effectEditor != None:
            self.__actionSignal(effectEditor.request_disconnect)

    def signalsCreate(self,effectEditor):
        if effectEditor != None:
            self.__actionSignal(effectEditor.request_connect)

    ###############
    def set_header(self,headerlabel,textbase):
        self._headerlabel = headerlabel
        self._headertextbase = textbase

    def update_header(self):
        res = list()
        for c in self._togglewidget: # display the first
            if c.isChecked():
                res.append(str(c.text()))
        self._headerlabel.setLabel("%s: <b>%s</b>" % (self._headertextbase,"/".join(res)))

    ###############
    def initFirstTime(self, msg):
        if self != msg.widgetFrom() and msg.isAppLevel() == False:
            return
        myName = str(self.objectName())
        self._myPref = None
        globState = msg.getPref().global_state()
        is_new = True

        if globState.has(myName):
            is_new = False
            self._myPref = globState[myName]
        else:
            # add myPref
            self._myPref = globState[myName] = StepFilterWidgetPref()

        db = msg.getGroup().find(CASH_SHOW_GEN,justChild = True)

        container = ContainerWidget()
        container.updateLabel("")

        steps = list()
        if isinstance(db,DbCache):
            steps = db.get_steps()

        widgetList = list()
        firstfound = False
        for x in steps:
            c = self._button_factory(x.getName())
            if is_new == True:
                vv = False
                if x.active == True and firstfound == False:
                    vv = True
                    firstfound = True
                self._myPref.set_stepfilter(x.getName(), vv)
                x.active = vv
            else:
                x.active = self._myPref.get_stepfilter(x.getName())

            c.setChecked(x.active)
            self._togglewidget.append(c)
            #QtT.QtCore.QObject.connect(c,
            #                       QtT.QtCore.SIGNAL("toggled(bool)"),
            #                       self.toggle_value_astype)
            c.toggled.connect(self.toggle_value_astype)
            widgetList.append(c)

        container.addListOfWidget(widgetList,needStretch=True)
        self.verticalLayout.addWidget(container)

        self.update_header()

    def get_filter_list(self):
        if self._myPref != None:
            d = self._myPref.get_filter_dict()
            res = list()
            for i in d:
                if d[i]:
                    res.append(i)
            return res
        return list()

    def refresh(self,msg):
        if msg.succeed():
            self._myPref.update_data(msg.get_stepfilter_change())
            self.update_header()

    def toggle_value_astype(self,val):
        # to do need some work, it's called twice on to turn on one to turn off
        if self._isradio and val == False:
            return
        res = dict()
        for c in self._togglewidget:
            res[str(c.text())] = c.isChecked()

        msg = MsgStepFilterChange(self,None,res)
        self.sig[confsig.CHANGE_PREF_STEP.name].emit(msg)

    def get_data(self):
        res = list()
        for c in self._togglewidget:
            if c.isChecked():
                res.append(str(c.text()))
        return res