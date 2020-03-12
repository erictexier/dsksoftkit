import types
from dsk.base.widgets.simpleqt import QtT

Qt = QtT.QtCore.Qt
QByteArray = QtT.QtCore.QByteArray

#from dsk.base.utils.msg_utils import MsgUtils as log

from collections import namedtuple
class beforeDragInfo(namedtuple('beforeDragInfo', "data,mimeType,topItems,serialized")):
    __slots__ = ()


TYPEMIME = 'text/jsondict-listXml'

##################################################
class DragAndDropHelper(object):

    def __init__(self,baseClass):
        assert baseClass != None
        self.__BASECLASS__ = baseClass

    ########################################
    def getMimeDataToDrag(self):
        # to be overwritten
        return beforeDragInfo(None,"",[],"")

    ########################################
    def startDrag(self,mode):

        toDrag = self.getMimeDataToDrag()
        if toDrag.data == None:
            return
        drag = Qt.QtGui.QDrag(self)
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



class DragAndDropTableHelper(DragAndDropHelper):
    def __init__(self,baseClass):
        super(DragAndDropTableHelper, self).__init__(baseClass)
    ########################################

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
            iconHeight = 80 * scale
            iconData = item.icon()

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



