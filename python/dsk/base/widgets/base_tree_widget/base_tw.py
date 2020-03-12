import os
from dsk.base.widgets.simpleqt import QtT

is_qt5 = QtT.which in ['PyQt5','PySide2']
QIcon = QtT.QtGui.QIcon

from dsk.base.utils.msg_utils import MsgUtils as log

from collections import namedtuple
class AttrUiDescription(namedtuple('attrUiDescription', 'icon')):
    __slots__ = ()


labelTree = ["Setting"]
winSize = [400,400]
prefSize =  [200,100]
dictParm  = {"Label":labelTree,
             "Size" : winSize,
             #"SizeColumn": prefSize,
             "AltColor": True,       # alternate color in row
             "Icons"   : True,
             "Editable": True,
             "IconsData": dict()
             }

#################################################################
class BaseTW(QtT.QtWidgets.QTreeWidget):
    #######################
    def __init__(self, parent, parameter):
        super(BaseTW, self).__init__(parent)
        self.setRootIsDecorated(True)

        if "AltColor" in parameter:
            self.setAlternatingRowColors(parameter['AltColor'])

        self.setSelectionMode(QtT.QtWidgets.QAbstractItemView.SingleSelection)
        self._editable = parameter["Editable"] if "Editable" in parameter else False

        # size
        if "Size" in parameter:
            self._hintSizex = parameter['Size'][0]
            self._hintSizey = parameter['Size'][1]
        else:
            self._hintSizex = 100
            self._hintSizey = 20

        #label
        if "Label" in parameter:
            if len(parameter['Label']) == 0:
                self.header().setVisible(False)
                pass
            else:
                if is_qt5==True:
                    labels = list()
                    for l in parameter['Label']:
                        labels.append(l)
                    self.setHeaderLabels(labels)
                else:
                    labels = QtT.QtCore.QStringList()
                    for l in parameter['Label']:
                        labels << self.tr(l)
                    self.setHeaderLabels(labels)


        else:
            self.header().setVisible(False)

        # column size
        if 'SizeColumn' in parameter:
            # set their pref size
            count = 0
            for s in parameter['SizeColumn']:
                self.header().resizeSection(count,s)
                count += 1
        else:
            try:
                if is_qt5==True:
                    self.header().setSectionResizeMode(QtT.QtWidgets.QHeaderView.Stretch)
                else:
                    #self.header().setResizeMode(QtT.QtWidgets.QHeaderView.ResizeToContents)
                    self.header().setResizeMode(QtT.QtWidgets.QHeaderView.Stretch)
            except Exception as e:
                print(str(e))

        # SETTING
        self._settings = None

        # icon stuff
        self._defaultIcon = None
        self._iconData = dict()

        if "Icons" in parameter and parameter['Icons']:
            self._defaultIcon = QIcon()
            self._defaultIcon.addPixmap(self.style().standardPixmap(QtT.QtWidgets.QStyle.SP_DirClosedIcon),
                                        QIcon.Normal, QIcon.Off)
            self._defaultIcon.addPixmap(self.style().standardPixmap(QtT.QtWidgets.QStyle.SP_DirOpenIcon),
                                        QIcon.Normal, QIcon.On)
        if "IconsData" in parameter and parameter['IconsData'] != None:
            self._iconData = parameter['IconsData']


    #######################
    def sizeHint(self):
        return QtT.QtCore.QSize(self._hintSizex,self._hintSizey)

    #######################
    def updateChildItems(self, parent):
        #log.info("%s %s" % ("updateChildItems",parent))
        dividerIndex = 0
        for group in self._settings.childGroups():
            m = self._settings.group()

            if m != None:
                m = m.find(group,True)
            else:
                m = self._settings.getChildren()
                if len(m)>0:
                    m = m[0]
            childIndex = self.findChild(parent, group, dividerIndex)
            if childIndex != -1:
                child = self.childAt(parent, childIndex)
                self.moveItemForward(parent, childIndex, dividerIndex)
                self.updateItem(child,group,m)
            else:

                child = self.createItem(group, parent, dividerIndex,m)

            dividerIndex += 1

            self._settings.beginGroup(group)
            self.updateChildItems(child)
            self._settings.endGroup()

        while dividerIndex < self.childCount(parent):
            self.deleteItem(parent, dividerIndex)


    #######################
    def iconSet(self,item,extraData):
        if extraData:
            cn = extraData.getTypeName()

            if cn in self._iconData:
                item.setIcon(0,self._iconData[cn].icon)
            elif self._defaultIcon != None:
                item.setIcon(0, self._defaultIcon)
        elif self._defaultIcon != None:
            item.setIcon(0, self._defaultIcon)

    #######################
    def createItem(self, text, parent, index,extraData=None):
        log.info("CreateItem %s %s %s" % (text,parent,index))
        after = None
        if index != 0:
            after = self.childAt(parent, index - 1)
        if parent is not None:
            item = QtT.QtWidgets.QTreeWidgetItem(parent, after)
        else:
            item = QtT.QtWidgets.QTreeWidgetItem(self, after)

        item.setText(0,text)
        self.iconSet(item,extraData)
        if self._editable:
            item.setFlags(item.flags() | QtT.QtCore.Qt.ItemIsEditable)
        return item

    #######################
    def updateItem(self, item,text,extraData=None):
        item.setText(0,text)
        self.iconSet(item,extraData)

    #######################
    def expand(self,anItem,rec = True,exp=False):
        if anItem is None:
            return
        anItem.setExpanded(exp)
        anItem.setHidden(False)
        if rec == False:
            return
        for index in range(anItem.childCount()):
            ch = anItem.child(index)
            self.expand(ch,rec,exp)


    def set_hidden(self,parent,val):
        if parent is None:
            count = self.topLevelItemCount()
            for t in range(count):
                parent = self.topLevelItem(t)
                self.set_hidden(parent,val)
            return

        parent.setHidden(val)
        parent.setExpanded(val)
        for index in range(parent.childCount()):
            ch = parent.child(index)
            self.set_hidden(ch,val)

    def turnOn(self,parent,direction):
        if parent is None:
            return
        if len(direction) == 0:
            # we expand the rest of the children
            self.expand(parent,True,True)
            return
        parent.setHidden(False)
        for i in range(self.childCount(parent)):
            item = self.childAt(parent, i)

            if item is not None:
                if item.text(0) == direction[0]:
                    self.turnOn(item,direction[1:])
        return

    def revealOnly(self,listOfPath, offset = 0, sep=os.sep):
        for t in range(self.topLevelItemCount()):
            top = self.topLevelItem(t)
            self.set_hidden(top,True) # hidden all
            for i in listOfPath:
                si = i.split(sep)
                if len(si) > offset:
                    si = si[offset:]
                    if len(si) > 0:
                        if top.text(0) == si[0]:
                            self.turnOn(top,si[1:])

    #######################
    def connectLocalSignal(self):
        pass
    def disconnectLocalSignal(self):
        pass

    def getHidenRoot(self,clip):
        if self._settings == None:
            return None
        chs = self._settings.getChildren()
        for i in range(clip-1):
            if chs != None and len(chs) > 0:
                chs = chs[0]
                chs = chs.getChildren()
            else:
                return None
        return chs[0]
    #######################
    def refresh(self, parent, clip = 0):
        self.disconnectLocalSignal()
        for i in range(clip):
            children = self._settings.childGroups()
            if len(children) > 0:
                self._settings.beginGroup(children[0])
            else:
                break
        self.updateChildItems(parent)
        for i in range(clip):
            self._settings.endGroup()
        self.connectLocalSignal()

    def setSettingsObject(self, settings, clip=0):
        self._settings = settings
        self.clear()
        self.refresh(None, clip)

    def __resetting(self,clip=0):
        self.clear()
        self.refresh(None, clip)

    #######################
    def deleteItem(self, parent, index):
        if parent is not None:
            item = parent.takeChild(index)
        else:
            item = self.takeTopLevelItem(index)
        del item

    #######################
    def deleteSubTree(self,item=None):
        # I don't know if we need to go recursively about it?
        if not item:
            item = self.currentItem()
        if not item:
            return None

        try:
            i = self.findChild(item.parent(), item.text(0), 0)
            if i != -1:
                self.deleteItem(item.parent(),i)
            else:
                #log.error("cannot delete this item")
                return None
        except:
            pass
        return item

    #######################
    def childAt(self, parent, index):
        if parent is not None:
            return parent.child(index)
        else:
            return self.topLevelItem(index)

    #######################
    def childCount(self, parent):
        if parent is not None:
            return parent.childCount()
        else:
            return self.topLevelItemCount()

    #######################
    def getIndex(self,parent,item):
        for i in range(self.childCount(parent)):
            if self.childAt(parent, i) is item:
                return i
        return -1

    #######################
    def findChild(self, parent, text, startIndex=0):
        childCount = self.childCount(parent)
        if startIndex < childCount:
            for i in range(startIndex,childCount):
                if self.childAt(parent, i).text(0) == text:
                    return i
        return -1

    #######################
    def findChildRec(self, parent, aPathAsList):
        if len(aPathAsList) == 0:
            return parent
        for i in range(self.childCount(parent)):
            item = self.childAt(parent, i)
            if not item:
                log.error("in base_tw: findChildRec")
                return None
            if item.text(0) == aPathAsList[0]:
                if len(aPathAsList) <= 1:
                    return item
                return self.findChildRec(item,aPathAsList[1:])
        return None

    #######################
    def moveItemForward(self, parent, oldIndex, newIndex):
        for i in range(oldIndex - newIndex):
            self.deleteItem(parent, newIndex)

