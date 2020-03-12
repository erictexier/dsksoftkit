from dsk.base.widgets.simpleqt import QtT

class DockWidget(QtT.QtWidgets.QDockWidget):
    def __init__(self, parent, thename, widgetclass, isFloating=False):
        QtT.QtWidgets.QDockWidget.__init__(self,parent)

        self.setWindowTitle(thename)
        self._customWidget = None
        self._myName = thename

        if widgetclass != None:

            self._customWidget = widgetclass(self)
            self._customWidget.setObjectName(thename)
            self.setWidget(self._customWidget)
        self.setFloating(isFloating)
        self.setAttribute(QtT.QtCore.Qt.WA_DeleteOnClose)

    def closeEvent(self, event):
        if hasattr(self.parent(), 'removeDock'):
            self.parent().removeDock(self._myName)
        self.widget().close()
        event.accept()

    def getCustomWidget(self):
        return self._customWidget

    def deregisterWidget(self,effectEditor):
        assert self._customWidget != None
        self._customWidget.signalsDestroy(effectEditor)

    def registerWidget(self,effectEditor):
        assert self._customWidget != None
        self._customWidget.signalsCreate(effectEditor)

