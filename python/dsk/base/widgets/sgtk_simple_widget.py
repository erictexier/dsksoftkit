import string
from dsk.base.widgets.simpleqt import QtT
from dsk.base.lib.default_path import DefaultPath


class SgtkSimpleWidget(QtT.QtWidgets.QWidget):
    def __init__(self,parent, **argv):
        super(SgtkSimpleWidget, self).__init__(parent)
        self.ui = QtT.uic.loadUi(DefaultPath.getUiFile("sgtk_simple_widget"), self)

    def update_widget(self, tu = None):
        if tu == None:
            self.ui.label_showname.setText("")
            self.ui.label_username.setText("")
            self.ui.label_taskname.setText("")
            self.ui.label_stepname.setText("")
        else:
            self.ui.label_showname.setText(tu.get_show_name())
            self.ui.label_username.setText(tu.get_user_name())
            self.ui.label_taskname.setText(tu.get_task_name())
            self.ui.label_stepname.setText(tu.get_step_name())
