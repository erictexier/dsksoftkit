from dsk.base.widgets.simpleqt import QtT

#from dsk.base.lib.default_path import DefaultPath

#########################################
class ContainerWidget(QtT.QtWidgets.QWidget):
    """Organize a list of widget vertically
       widgets are added to scrollArea that will be resized nicely dependent
       on the visible size of each widget
    """
    def __init__(self,parent = None):

        QtT.QtWidgets.QWidget.__init__(self, parent)
        self.label = QtT.QtWidgets.QLabel('mylabel')
        self._mainLayout = mainLayout = QtT.QtWidgets.QVBoxLayout()
        mainLayout.setAlignment(QtT.QtCore.Qt.AlignTop|QtT.QtCore.Qt.AlignVCenter)
        mainLayout.addWidget(self.label)
        mainLayout.setAlignment(QtT.QtCore.Qt.AlignLeading|QtT.QtCore.Qt.AlignLeft|QtT.QtCore.Qt.AlignTop)

        # define a scroll Area with a frame widget
        scroll = self._scrollArea = QtT.QtWidgets.QScrollArea()
        scroll.setAlignment(QtT.QtCore.Qt.AlignLeading|QtT.QtCore.Qt.AlignLeft|QtT.QtCore.Qt.AlignTop)
        #scroll.setVerticalScrollBarPolicy(QtT.QtCore.Qt.ScrollBarAlwaysOn)
        scroll.setHorizontalScrollBarPolicy(QtT.QtCore.Qt.ScrollBarAlwaysOff)
        scroll.setWidgetResizable(True)

        self._scrollBox = QtT.QtWidgets.QFrame()
        self._VL = QtT.QtWidgets.QVBoxLayout(self)
        self._scrollBox.setLayout(self._VL)

        scroll.setWidget(self._scrollBox)

        # add to the main Layout the scroll
        mainLayout.addWidget(scroll)
        mainLayout.setSpacing(1)
        mainLayout.setContentsMargins(1,1,1,1)
        self._VL.setSpacing(1)
        self._VL.setContentsMargins(1,1,1,1)
        self.setLayout(mainLayout)

    def addCommand(self,awidget):
        assert awidget != None
        # add a widget after the scroll area
        self._mainLayout.addWidget(awidget)

    def setEnabledStretch(self,val):
        self.toAddLayout().setEnabled(val)

    #########################
    def updateLabel(self,name):
        """ set the top level label
        """
        self.label.setText(name)
        if name == "":
            self.label.hide()
        else:
            self.label.show()
        return self.label

    def getLabel(self):
        return self.label

    #########################
    def addListOfWidget(self,alistOfCollapsible,needStretch=True):
        """ Remove any old children widget
           add the new widgets list
           add a stretch to warranty the good layout of the children when they don't extend themself
        """
        self.reset()
        if len(alistOfCollapsible) == 0:
            return
        # add widgets
        for wi in alistOfCollapsible:
            self.toAddLayout().addWidget(wi)

        # add a screcther
        if needStretch:
            self.doneAdding()


    #########################
    def reset(self):
        """Empty everything from the children list + the scretcher
        """
        # clean up the children widgetList
        children = self._scrollBox.children()
        theParent = self.toAddLayout()
        for ch in children:
            if isinstance(ch,QtT.QtWidgets.QWidget):
                theParent.removeWidget(ch)
                ch.deleteLater()

        # remove the scretcher
        child = theParent.takeAt(0)
        while child != None:
            del child;
            child = theParent.takeAt(0)
        QtT.QtCore.QCoreApplication.processEvents()

    def doneAdding(self):
        self._VL.addStretch(1)
        self._VL.setSpacing(1)
        self._VL.setContentsMargins(1,1,1,1)

    ###
    def toAddLayout(self):
        return self._VL

def show(x = False):
    import sys
    from dsk.base.widgets.base_collapsible_widget import BaseCollapsibleWidget
    app = QtT.QtCore.QCoreApplication.instance()
    if app == None:
        app = QtT.QtWidgets.QApplication(sys.argv)

    Form = ContainerWidget()

    widgetList = list()
    for i in range(4):
        widgetList.append(BaseCollapsibleWidget(None,QtT.QtWidgets.QListView(),False))
        a = QtT.QtWidgets.QListView()
        a.setFixedHeight(200)
        widgetList.append(a)

    Form.addListOfWidget(widgetList)
    #Form.updateLabel("basic container widget")
    Form.updateLabel("xxx")
    label = QtT.QtWidgets.QLabel('mylabel')
    Form.addCommand(label)
    Form.setGeometry(500, 300, 300, 400)
    Form.show()
    if x:
        sys.exit(app.exec_())
        return None
    return Form


#########################################
if __name__ == "__main__":
    show(True)
