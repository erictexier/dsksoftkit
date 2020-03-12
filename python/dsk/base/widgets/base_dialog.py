from dsk.base.widgets.simpleqt import QtT

class WarningDialog(QtT.QtWidgets.QDialog):
    def __init__(self, parent, title,msg):
        super(WarningDialog, self).__init__(parent)
        self.setWindowTitle(title)
        layout = QtT.QtWidgets.QVBoxLayout()
        self.setLayout(layout)
        label = QtT.QtWidgets.QLabel(msg)
        layout.addWidget(label)


class BaseDialog(QtT.QtWidgets.QDialog):
    def __init__(self, parent, title,msg):
        super(BaseDialog, self).__init__(parent)
        self.setWindowTitle(title)
        layout = QtT.QtWidgets.QVBoxLayout()
        self.setLayout(layout)
        label = QtT.QtWidgets.QLabel(msg)
        layout.addWidget(label)
        buttonBox = QtT.QtWidgets.QDialogButtonBox(
            QtT.QtWidgets.QDialogButtonBox.Ok | QtT.QtWidgets.QDialogButtonBox.Cancel)
        layout.addWidget(buttonBox)
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)