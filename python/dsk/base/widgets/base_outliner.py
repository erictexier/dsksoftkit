#!/usr/bin/env python
import os
import types
import sys
import json
from collections import OrderedDict
from dsk.base.widgets.simpleqt import QtT

Qt = QtT.QtCore.Qt
QByteArray = QtT.QtCore.QByteArray
QFont = QtT.QtGui.QFont

from dsk.base.tdata.osettings import OSettings
from dsk.base.utils.msg_utils import MsgUtils as log

#from dsk.base.widgets.drag_and_drop_helper import DragAndDropHelper
from dsk.base.widgets.drag_and_drop_helper import beforeDragInfo,TYPEMIME
from dsk.base.tdata.tdata import SepPath
from dsk.base.lib.msg_arg import MsgNameChange
from dsk.base.widgets.base_tree_widget.base_context_tw import BaseContextTW
from dsk.base.resources import browser_signal as confsig



class ContainerTreeWItem(QtT.QtWidgets.QTreeWidgetItem):
    _font = QFont()
    def __init__(self,parent,index,container):
        super(ContainerTreeWItem,self).__init__(parent, index)
        self.updateItem(container)

    def updateItem(self,container):
        self._containt = container
        if container != None:# and hasattr(container,"comment"):
            try:
                self.setText(1,container.comment)
            except:
                pass
        self.updateEnable()

    def updateEnable(self):
        if self._containt:
            if self._containt.isEnable():
                self.checkState(QtT.QtCore.Qt.Checked)
                self._font.setBold(False)
                self._font.setItalic(False)
                self._font.setStrikeOut(False)
            else:
                self.checkState(QtT.QtCore.Qt.Unchecked)
                self._font.setBold(True)
                self._font.setItalic(True)
                self._font.setStrikeOut(True)
                self._font.setWeight(QFont.Light)
            self.setFont(0,self._font)

    def getContain(self):
        return self._containt

class BaseOutlinerDD(BaseContextTW):
    def __init__(self,parent, parameter):
        #assert baseClass != None
        self.__BASECLASS__ = QtT.QtWidgets.QTreeWidget
        super(BaseOutlinerDD,self).__init__(parent, parameter)
    ########################################
    def getMimeDataToDrag(self):
        # to be overwritten
        return beforeDragInfo(None,"",[],"")

    ########################################
    def startDrag(self,mode):

        toDrag = self.getMimeDataToDrag()
        if toDrag.data == None:
            return
        drag = QtT.QtGui.QDrag(self)
        md = toDrag.data
        md.setData(toDrag.mimeType,QByteArray(toDrag.serialized))
        md.setText(toDrag.mimeType)

        drag.setHotSpot(QtT.QtCore.QPoint(5,5))
        pixm = self._renderToPixmap(toDrag.topItems)
        if pixm != None:
            drag.setPixmap(pixm)
        drag.setMimeData(md)
        mode = drag.start(mode)

    def _dropActionFromEvent(self, event):
        action = None
        if event.source() != self:
            action = event.proposedAction()
            return action
        elif event.keyboardModifiers() == Qt.ShiftModifier:
            return Qt.CopyAction
        return Qt.MoveAction

    def dragMoveEvent(self, event):
        self.__BASECLASS__.dragMoveEvent(self,event)
        action = self._dropActionFromEvent(event)
        if action is None:
            event.ignore()
            return
        event.setDropAction(action)
        event.accept()

    def dropEvent(self, event):

        action = self._dropActionFromEvent(event)
        if action is None:
            event.ignore()
            return

        eventPos = event.pos()
        ip = self.dropIndicatorPosition()

        pos = -1
        if ip == self.OnItem:
            item = self.itemAt(eventPos)
            pos = item.childCount()
        elif ip == self.OnViewport:
            pos = self.topLevelItemCount()
            item = None
        elif ip == self.AboveItem:
            item = self.itemAt(eventPos)
            parent = item.parent()
            pos = self.getIndex(parent,item)
            item = parent
        elif ip == self.BelowItem:
            item = self.itemAt(eventPos)
            parent = item.parent()
            pos = self.getIndex(parent,item) + 1
            item = parent
        src = event.source()

        widgetSourceName= ""
        if src:
            widgetSourceName = src.objectName()
        else:
            widgetSourceName = "foreign"

        accept = self.dropReceive(actionType=action,
                                  widgetSourceName = widgetSourceName,
                                  destItem=item,
                                  pos=pos,
                                  mimeType=event.mimeData().text(),
                                  mimeData=event.mimeData())
        if accept == False:
            event.ignore()
            return
        event.setDropAction(action)
        event.accept()
        return self.__BASECLASS__.dropEvent(self,event)


    def _renderToPixmap(self,itemList):
        # return None if one or more item don't have icon
        fade = False
        scale = 1.
        rect = QtT.QtCore.QRect(0,0,0,0)
        yOffset = 0
        paintStack = []
        opacity = [1.,.9,.86,.75,.68,.59,.54]

        if len(itemList)>len(opacity):
            itemList = itemList[:len(opacity)]
            fade      = True
            scale = .8
        for item in itemList:
            iconHeight = 50
            iconData = item.icon(0)
            sizes = iconData.availableSizes()
            if sizes and len(sizes) > 0:
                iconHeight = sizes[0].height()*scale
            else:
                return None
            iconRect = QtT.QtCore.QRect(rect.x(),rect.y()+yOffset,iconHeight,iconHeight)
            paintStack.append((iconData,iconRect))
            rect = rect.united(iconRect)
            yOffset = yOffset + iconHeight

        resultImage = QtT.QtGui.QPixmap(rect.size())
        resultImage.fill(Qt.transparent)
        painter = QtT.QtGui.QPainter(resultImage)
        painter.setOpacity(1.)
        for icon,iconRect in paintStack:
            if not fade:
                icon.paint(painter,iconRect,Qt.AlignJustify)
                continue
            if len(opacity)> 0:
                alpha = opacity.pop(0)
            painter.setOpacity(alpha)
            icon.paint(painter,iconRect,Qt.AlignJustify)

        painter.end()
        return resultImage


#################################################################
#class BaseOutliner(BaseContextTW, DragAndDropHelper2):
class BaseOutliner(BaseOutlinerDD):
    #######################
    def __init__(self, parent,parameter):
        #BaseContextTW.__init__(self,parent, parameter)
        super(BaseOutliner,self).__init__(parent, parameter)
        self._levelProtect = 0

        # drag and drop
        if "itemGenerator" in parameter:
            self._itemCreate = parameter['itemGenerator']
        else:
            self._itemCreate = ContainerTreeWItem

        self.setSelectionMode(QtT.QtWidgets.QAbstractItemView.ContiguousSelection)
        if self._editable == True:
            self.setDragEnabled(True)
            self.setAcceptDrops(True)

        self.connectLocalSignal()



    def getProtectLevel(self):
        return self._levelProtect

    def setProtectLevel(self,level):
        self._levelProtect = level

    def getRootObject(self):
        # last
        return self.getHidenRoot(self._levelProtect)

    #######################
    def createItem(self, text, parent, index,extraData=None):
        after = None
        #log.info("%s %s %s %s" % ("x" * 30,text,parent,index))

        if index != 0:
            after = self.childAt(parent, index - 1)
        if parent is not None:
            item = self._itemCreate(parent, after,extraData)
        else:
            item = self._itemCreate(self, after,extraData)

        item.setText(0,text)
        self.iconSet(item,extraData)
        if self._editable:
            item.setFlags(item.flags() | QtT.QtCore.Qt.ItemIsEditable) # | QtCore.Qt.ItemIsEnabled |
            #QtCore.Qt.ItemIsSelectable |  QtCore.Qt.ItemIsDragEnabled | QtCore.Qt.ItemIsDropEnabled)
        return item

    #######################
    def updateItem(self, item,text,extraData=None):
        item.setText(0,text)
        self.iconSet(item,extraData)
        item.updateItem(extraData)

    #######################
    def connectLocalSignal(self):
        self.connect(self, QtT.QtCore.SIGNAL("itemPressed(QTreeWidgetItem*, int)"),self.updateCurrent)
        self.connect(self, QtT.QtCore.SIGNAL("itemChanged(QTreeWidgetItem *, int)"),self.editTreeText)

    #######################
    def disconnectLocalSignal(self):
        self.disconnect(self, QtT.QtCore.SIGNAL("itemPressed(QTreeWidgetItem*, int)"),self.updateCurrent)
        self.disconnect(self, QtT.QtCore.SIGNAL("itemChanged(QTreeWidgetItem *, int)"),self.editTreeText)

    ########################
    # overwrite dragAndDropHelper
    def getMimeDataToDrag(self,doSerialize=True):
        from operator import itemgetter

        selectPath = dict()

        # find what the set of data that need to be serialize
        currentSelection = self.selectedItems()

        for item in currentSelection:
            m = item.getContain()
            if m:
                selectPath[m.getPath()] = item
            else:
                item.setSelected(False)
                index = currentSelection.index(item)
                currentSelection.pop(index)

        # sorted from closer to the root
        dpath = dict() # assume sorted since keys are int
        for p in selectPath:
            n = len(p.split(SepPath))
            if not n in dpath:
                dpath[n] = list()
            dpath[n].append(p)

        # order the item, selectedItems return a unsorted list
        # we need to sorted the items
        sdpath = dict()  # sort in sdpath item
        for i in dpath:
            level = dpath[i]
            sdpath[i] = list()
            itemList = [selectPath[p] for p in level]
            grPar = dict()
            for it in itemList:
                p = it.parent()
                if not p in grPar:
                    grPar[p] = list()
                grPar[p].append(it)
            for parent in grPar:
                indexList = [self.getIndex(parent,it) for it in grPar[parent]]
                b = zip(indexList,grPar[parent])
                b = map(itemgetter(1),sorted(b))
                res = [ch.getContain().getPath() for ch in b]
                sdpath[i] += res
        # define if we need to save recursive serialization
        # recursive if all the children are in selection or none

        toSerialize = dict()
        topItemSelect = list()
        for i in sdpath:
            level = sdpath[i]
            for p in level:
                if p in selectPath:
                    item = selectPath[p]
                    topItemSelect.append(item)

                    if doSerialize == True:
                        countSelect = 0
                        child = list()
                        childSelect = list()
                        for chi in range(item.childCount()):
                            ch = item.child(chi)
                            if ch in currentSelection:
                                countSelect += 1
                                childSelect.append(ch.getContain())
                            child.append(ch)

                        gc =  item.getContain()
                        if countSelect == 0 or countSelect == gc.nbOfChildren():
                            toSerialize[p] = gc.toString(True)

                        else:
                            # selective serialize
                            ser = gc.toString(False)
                            top = gc.fromString(ser)
                            for ch in childSelect:
                                ser = ch.toString(True)
                                ch = gc.fromString(ser)
                                if ch:
                                    top.addChild(ch)
                            toSerialize[p] = top.toString(True)


                    # clean up the task already serialize by parenting
                    for i in selectPath.keys():
                        if i.startswith(p):
                            selectPath.pop(i)

        if len(currentSelection) > 0 and len(topItemSelect) > 0:
            md = self.mimeData(topItemSelect)
            return beforeDragInfo(md,TYPEMIME, currentSelection, json.dumps(toSerialize))
        else:
            return beforeDragInfo(None,"",[],"")

    def getPathList(self,itemList):
        res = list()
        for i in itemList:
            res.append(i.getContain().getPath())
        return res

    ######################################################
    def dropReceive(self,
                    actionType,
                    widgetSourceName,
                    destItem,
                    pos,
                    mimeType,
                    mimeData):

        from dsk.base.lib.msg_arg import MsgDragDrop

        action = "MOVE" if actionType & Qt.MoveAction else "COPY"
        pathDest = ""
        if destItem: # != None:
            pathDest = destItem.getContain().getPath()
        else:
            if self.topLevelItemCount()>0:
                topItem = self.topLevelItem(0)
                parent = topItem.parent()
                if parent != None:
                    pathDest = parent.getContain().getPath()

        msg = MsgDragDrop(widgetFrom=self,
                          actionType = action,
                          listOfSerializeData=str(mimeData.data(mimeType)),
                          destinationPath = pathDest,
                          pos = pos,
                          widgetSourceName=str(widgetSourceName))
        if hasattr(self,'sig') and confsig.XML_DROP_LIST.name in self.sig:
            self.sig[confsig.XML_DROP_LIST.name].emit(msg)
        return True

    #######################
    def updateCurrent(self,item,c):
        path = item.getContain().getPath()
        if hasattr(self,'sig') and confsig.SELECTION_ITEM_CHANGE.name in self.sig:
            self.sig[confsig.SELECTION_ITEM_CHANGE.name].emit(path)

    #########################
    def editTreeText(self, item,count):
        key = str(item.text(count))
        try:
            path = item.getContain().getPath()
            msg = MsgNameChange(widgetFrom=self,item=item,path=path,newName=key,which=count)
            if hasattr(self,'sig') and confsig.CELLTREE_CHANGE.name in self.sig:
                self.sig[confsig.CELLTREE_CHANGE.name].emit(msg)
        except:
            pass
    #########################
    # in response to editTreeText validation
    def treeTextUpdate(self,msg):
        if msg.widgetFrom() != self:
            log.error("treeTextUpdate,should be not getting this update")
            return

        i = msg.getItem()
        if i:
            self.disconnectLocalSignal() # to avoid bouncing
            i.setText(msg.getWhich(),msg.getProposedName())
            self.connectLocalSignal()

    #########################
    def updateEnable(self,msg):
        if msg.widgetFrom() != self:
            log.error("updateEnable,should be not getting this update")
            return
        if msg.succeed():
            for item in msg.getOptions():
                item.updateEnable()

    def updateCut(self,msg):
        if msg.widgetFrom() != self:
            #log.error("updateCut,should be not getting this update")
            return False
        if msg.succeed():
            for item in msg.getOptions():
                self.deleteSubTree(item)
        return True

    def select_item(self,apath,parent=None,r=0):
        if len(apath) == 0:
            return
        tofind = apath[0]
        for i in range(self.childCount(parent)):
            item = self.childAt(parent, i)
            if tofind == str(item.text(0)):
                if len(apath) == 1:
                    index = self.indexFromItem(item,r)
                    for r in range(self.childCount(item)):
                        index = self.indexFromItem(item,r)
                        break
                    self.selectionModel().select(index,QtT.QtGui.QItemSelectionModel.Select)
                else:
                    self.select_item(apath[1:],item)
        return

    def updateSubTreeAdded(self,msg):
        #log.info("in updateSubTreeAdded")

        start = msg.getGroup()
        assert start != None
        self.disconnectLocalSignal()
        pTop = start.getPath()
        self._settings.open(pTop)
        pp = pTop.split("/")
        a = self.getProtectLevel()
        if a > 0:
            pp = pp[a:]
        parent = self.findChildRec(None,pp)
        self.updateChildItems(parent)
        self._settings.close()
        self.expand(parent,False,True)
        self.connectLocalSignal()

    def pathTreeDelete(self,apath):
        pp = apath.split("/")
        a = self.getProtectLevel()
        if a > 0:
            pp = pp[a:]
        parent = self.findChildRec(None,pp)
        if parent:
            self.deleteSubTree(parent)

    def updateSubTreeDeleted(self,msg):
        start = msg.getGroup()
        assert start != None
        pTop = start.getPath()
        self.pathTreeDelete(pTop)
    #######################
    # expand
    def __expandRec(self,anItem,alist,create=False):
        assert type(alist) == types.ListType
        if len(alist) == 0:
            anItem.setSelected(True)
            return True
        aname = alist[0]
        for index in range(anItem.childCount()):
            ch = anItem.child(index)
            if ch.text(0) == aname:
                ch.setExpanded(True)
                return self.__expandRec(ch, alist[1:],create)
        if create == True:
            p = anItem
            for i in alist:
                if i != "":
                    p = self.createItem(i,p,0)
                    p.setExpanded(True)
            return True
        return False

    #######################
    def expandWithPath(self,parent,apath,create=False):
        assert type(apath) in types.StringTypes
        if parent is None:
            for t in range(self.topLevelItemCount()):
                parent = self.topLevelItem(t)
                self.expandWithPath(parent,apath,create)
            return
        spath = apath.split(os.sep)
        if len(spath) == 0:
            return False

        if parent.text(0) == spath[0]:
            parent.setExpanded(True)
            return self.__expandRec(parent, spath[1:],create)
        elif create == True and parent != None:
            p = parent
            for i in spath:
                if i != "":
                    p = self.createItem(i,p,0)
            return self.expandWithPath(parent,apath,False)
        return False

