import string
from dsk.base.widgets.simpleqt import QtT
from dsk.base.lib.default_path import DefaultPath

class LogWidget(QtT.QtWidgets.QWidget):
    def __init__(self,parent, **argv):
        super(LogWidget, self).__init__(parent)
        self.ui = QtT.uic.loadUi(DefaultPath.getUiFile("log_widget"), self)

        self.ui.comboBox.hide()  # level selection (not implemented)
        self.ui.lineEdit.hide()  # a filter(not implemented)
        self.grabLog()

    ############### APPLICATION SIGNAL
    def signalsDestroy(self,effectEditor):
        if effectEditor != None:
            self.__actionSignal(effectEditor.request_disconnect)
    def signalsCreate(self,effectEditor):
        # application signal
        # connect with the view
        if effectEditor != None:
            self.__actionSignal(effectEditor.request_connect)

    def __actionSignal(self,act):
        act(self,"logwrite",False,self.updateText)

    def grabLog(self):
        self.ui.textEdit.clear()

    def updateText(self, text):
        #if self.filterLine(text):
        stripped = string.strip(str(text), '\n')
        self.ui.textEdit.append(str(stripped))