from dsk.base.widgets.simpleqt import QtT
from dsk.base.widgets.drag_and_drop_helper import beforeDragInfo,TYPEMIME
#from dsk.base.widgets.drag_and_drop_helper import DragAndDropTableHelper


class EmptyItem(QtT.QtWidgets.QTableWidgetItem):
    def __init__(self,parent,raw,col):
        super(EmptyItem, self).__init__()
        self.setSizeHint(QtT.QtCore.QSize(parent.icon_w,parent.icon_h))
        parent.setItem(raw, col, self)

    def getContain(self):
        return None



class SimpleItem(QtT.QtWidgets.QTableWidgetItem):

    def __init__(self, parent, raw, col, aname):
        super(SimpleItem, self).__init__()
        #self._containt = None
        self.setText(str(aname))
        parent.setItem(raw, col, self)

    def getContain(self):
        return self._containt

##############################################################################
class DragHeaderView(QtT.QtWidgets.QHeaderView):

    def __init__(self,atype,callback):
        super(DragHeaderView, self).__init__(atype)
        self.sectionMoved.connect(self.OnSectionMoved)
        self._alist = list()
        self._curcol = ""
        self._callback = callback


    def set_col(self,alist):
        self._alist = alist

    def get_col_list(self):
        return self._alist


    def get_current_col(self):
        return self._curcol

    def OnSectionMoved(self, logicalIndex, oldVisualIndex, newVisualIndex):
        # edit the department order
        for i,ll in enumerate(self._alist):
            ll.id = self.visualIndex(i)

class BaseTableWidgetDD(QtT.QtWidgets.QTableWidget):
    def __init__(self,parent, parameter):
        #assert baseClass != None
        self.__BASECLASS__ = QtT.QtWidgets.QTableWidget
        super(BaseTableWidgetDD,self).__init__(parent)
    ########################################
    def getMimeDataToDrag(self):
        # to be overwritten
        return beforeDragInfo(None,"",[],"")

    ########################################
    def startDrag(self,mode):

        toDrag = self.getMimeDataToDrag()
        if toDrag.data == None:
            return
        drag = QtGui.QDrag(self)
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

###############################################################################
#class BaseTableWidget(QtGui.QTableWidget, DragAndDropTableHelper):
class BaseTableWidget(BaseTableWidgetDD):
    #######################
    def __init__(self, parent, **parameter):
        super(BaseTableWidget, self).__init__(parent,parameter)
        #DragAndDropTableHelper.__init__(self,QtGui.QTableWidget)
        self.setDragEnabled(True)
        try:
            # to go over some windows stuff
            self.setDefaultDropAction(QtT.QtCore.Qt.CopyAction)
        except:
            pass
