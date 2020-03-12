from collections import OrderedDict
from dsk.base.widgets.simpleqt import QtT


Da = "-!-"

class BaseAction(QtT.QtWidgets.QAction):
    def __init__(self,aname,parent = None):
        super(BaseAction, self).__init__(aname,parent)
        self._actionName = aname

    def cleanAction(self):
        return

    def updateData(self,o,aName,someExtra):
        if o.ckeckable():
            self.setCheckable(True)
            self.setChecked(o.isChecked())

        enable = False
        o.initialize(aName,someExtra)
        actionList = o.getActions()
        if len(actionList) == 1:
            label,path,en = actionList[0]
            if en == True:
                enable = True
            self.setWhatsThis(Da.join([self._actionName,o.getSubActionName(),path]))
            self.setText(o.actionTitle(aName))
        else:
            self.setText(o.actionTitle(aName))
        return enable

class SubMenuContext(QtT.QtWidgets.QMenu):
    def __init__(self,actionName,label,parent):
        super(SubMenuContext,self).__init__(label,parent)
        self._actionName = actionName

    def cleanAction(self):
        for ssm in self.children()[1:]:
            if hasattr(ssm,'cleanAction'):
                ssm.cleanAction()
            ssm.deleteLater()

    def updateData(self,o,aName,someExtra):
        currentMenu = self
        enable = False
        if someExtra != None:
            o.initialize(aName,someExtra)
        actionList = o.getActions()

        for u in actionList:
            label,path,en = u
            ad = self.addAction(label)
            ad.setWhatsThis(Da.join([self._actionName,o.getSubActionName(),path]))
            ad.setEnabled(en)
            if en == True:
                enable = True
        if o.hasAction():
            for san in o.subAction():
                if san.hasAction():
                    if san.isSubmenu() == True:
                        currentMenu = SubMenuContext(self._actionName,san.getName(),self)
                        self.addMenu(currentMenu)
                        en = currentMenu.updateData(san,aName,None)
                        if en == True:
                            enable = True
                    else:
                        actionList = san.getActions()
                        for u in actionList:
                            label,path,en = u
                            ad = self.addAction(label)
                            ad.setWhatsThis(Da.join([self._actionName,
                                                     o.getSubActionName(),
                                                     path]))
                            ad.setEnabled(en)
                            if en == True:
                                enable = True
        self.setTitle(o.actionTitle(aName))
        return enable

class MenuContextAction(QtT.QtWidgets.QMenu):
    def __init__(self,parent,menuAss):
        self._needTextUpdate = OrderedDict()
        super(MenuContextAction, self).__init__(parent)

        for subData in menuAss:
            if subData.isSep():
                self.addSeparator()
            else:
                if subData.isSubmenu() == True:
                    subMenu = SubMenuContext(subData.actionName(),subData.actionName(), self)
                    self.addMenu(subMenu)
                    self._needTextUpdate[subData.actionName()] = subMenu
                else:
                    anAction = BaseAction(subData.actionName(), self)
                    self._needTextUpdate[subData.actionName()] = anAction
                    self.addAction(anAction)

    def updateTextAction(self,aName,someExtra,menuAss):
        for m in self._needTextUpdate.values():
            m.cleanAction()
            m.setEnabled(False)
        for o in menuAss:
            if o.actionName() in self._needTextUpdate:
                m = self._needTextUpdate[o.actionName()]
                res = m.updateData(o,aName,someExtra)
                if res == True:
                    #m.setVisible(True)
                    m.setEnabled(True)
                else:
                    m.setEnabled(False)
                    #m.setVisible(False)
