from dsk.base.widgets.simpleqt import QtT


def setupUi(self, Form):

        Form.setObjectName("Form")
        #Form.resize(QtT.QtCore.QSize(QtT.QtCore.QRect(0,0,438,40).size()).expandedTo(Form.minimumSizeHint()))
        #Form.resize(QtT.QtCore.QSize(QtT.QtCore.QRect(0,0,438,40).size()).expandedTo(Form.minimumSizeHint()))
        self.vboxlayout = QtT.QtWidgets.QVBoxLayout(Form)
        self.vboxlayout.setSpacing(0)
        #self.vboxlayout.setMargin(0)
        self.vboxlayout.setObjectName("vboxlayout")

        self.hboxlayout = QtT.QtWidgets.QHBoxLayout()
        self.hboxlayout.setObjectName("hboxlayout")

        self.EnvVis = QtT.QtWidgets.QCheckBox(Form)
        self.EnvVis.setMinimumSize(QtT.QtCore.QSize(20,0))
        self.EnvVis.setMaximumSize(QtT.QtCore.QSize(20,16777215))
        self.EnvVis.setIconSize(QtT.QtCore.QSize(5,5))
        self.EnvVis.setObjectName("EnvVis")
        self.hboxlayout.addWidget(self.EnvVis)

        self.label = QtT.QtWidgets.QTextEdit(Form)

        sizePolicy = QtT.QtWidgets.QSizePolicy(QtT.QtWidgets.QSizePolicy.Expanding,QtT.QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        self.label.setMaximumSize(QtT.QtCore.QSize(16777215,20))
        self.label.setFocusPolicy(QtT.QtCore.Qt.NoFocus)
        self.label.setFrameShape(QtT.QtWidgets.QFrame.NoFrame)
        self.label.setVerticalScrollBarPolicy(QtT.QtCore.Qt.ScrollBarAlwaysOff)
        self.label.setHorizontalScrollBarPolicy(QtT.QtCore.Qt.ScrollBarAlwaysOff)
        self.label.setUndoRedoEnabled(False)
        self.label.setLineWrapMode(QtT.QtWidgets.QTextEdit.NoWrap)
        self.label.setReadOnly(True)
        self.label.setObjectName("label")
        self.hboxlayout.addWidget(self.label)
        self.vboxlayout.addLayout(self.hboxlayout)


        #Form.setWindowTitle(QtT.QtWidgets.QApplication.translate("Form", "Form", None, QtT.QtWidgets.QApplication.UnicodeUTF8))
        QtT.QtCore.QMetaObject.connectSlotsByName(Form)


#########################################
class BaseCollapsibleWidget(QtT.QtWidgets.QWidget):
    """ manage the visibility of a widget
    """
    def __init__(self,parent,awidget,isCollapsed=False):

        super(BaseCollapsibleWidget, self).__init__(parent)
        self.doRichLabel = False
        layout = awidget.layout()
        agroup = None
        if layout != None:

            nbOfItem = layout.count()
            #this is looking if the widget is group it wil use it label to toggle
            for i in  range(nbOfItem):
                item = layout.itemAt(i)
                wi = item.widget()

                if isinstance(wi,QtT.QtWidgets.QGroupBox):
                    agroup = wi
                    break

        if agroup != None:
            agroup.setCheckable(True)
            agroup.setChecked(isCollapsed)
            if not hasattr(awidget,"doCollapse"):
                # we don't want to hide the entier group since the group hold the check box"
                self._managedWidget = []
                for ch in agroup.children():
                    if isinstance(ch,QtT.QtWidgets.QWidget):
                        self._managedWidget.append(ch)

            else:
                self._managedWidget = [awidget]

            vboxlayout = QtT.QtWidgets.QVBoxLayout()
            vboxlayout.addWidget(awidget)
            self.setLayout(vboxlayout)
            self.group = agroup

            self.label = None
            agroup.toggled.connect(self.isToggled)


        else:
            # use text edit
            setupUi(self,self)

            self._managedWidget = [awidget]
            self.vboxlayout.addWidget(awidget)
            self.EnvVis.setChecked(isCollapsed)
            self.EnvVis.toggled.connect(self.isToggled)
        if(isCollapsed):
            self.doCollapse()
        else:
            self.doExtend()

    def setDoRichLabel(self,val):
        self.doRichLabel = val
        return

    def doCollapse(self):
        """ hide all the managed widget
        """
        for w in self._managedWidget:
            if hasattr(w,"doCollapse"):
                w.doCollapse()
            else:
                w.hide()

    def doExtend(self):
        """ show all the managed widget
        """
        for w in self._managedWidget:
            if hasattr(w,"doExtend"):
                w.doExtend()
            else:
                w.show()
                w.setEnabled(True)

    def setLabel(self,lab,acolor="black"):
        """ Set the top level label.
        When a group is found, use the tilte of the group instead
        """

        if self.label != None:
            if self.doRichLabel == True:
                acol = str("<b><font color=%s>%s</color>" % (acolor,lab))
                if QtT.which in ['PySide2','PyQt5']:
                    self.label.setText(QtT.QtWidgets.QApplication.translate("baseCollapsibleWidget",
                                                                            acol,""))
                else:
                    self.label.setText(QtT.QtWidgets.QApplication.translate("baseCollapsibleWidget",
                                                                acol,"",QtT.QtWidgets.QApplication.UnicodeUTF8))
            else:
                self.label.setText(lab)
        else:
            # it's a group
            self.group.setTitle(lab)


    def isToggled(self,v):
        """ change the visible status of managed widgets
        """
        if v == True:
            self.doCollapse()
        else:
            self.doExtend()


    def resetContent(self):
        children = self.children()[:]
        theParent = self.vboxlayout
        for ch in children:
            if isinstance(ch,QtT.QtWidgets.QWidget):
                theParent.removeWidget(ch)
                ch.deleteLater()