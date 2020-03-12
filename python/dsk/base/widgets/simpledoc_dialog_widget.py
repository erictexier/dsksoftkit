from dsk.base.widgets.simpleqt import QtT
from dsk.base.lib.default_path import DefaultPath


class SimpleDocDialogWidget(QtT.QtWidgets.QDialog):

    def __init__(self, parent,text):

        super(SimpleDocDialogWidget, self).__init__(None)
        self.ui = QtT.uic.loadUi(DefaultPath.getUiFile("simple_doc"), self)
        stext = text.split("\n")
        clean = list()
        for tt in stext:
            if tt.strip() == "":
                clean.append("<br>")
                clean.append("</br>")
            else:
                clean.append(tt.replace("<br>","").replace("<p>","").replace("</p>","").replace("<b>",""))

        result = list()
        for tt in clean:
            result.append("<div>")
            result.append(tt)
            result.append("</div>")
        self.ui.text_edit.setText("\n".join(result))
