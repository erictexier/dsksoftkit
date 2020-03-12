from dsk.base.widgets.simpleqt import QtT

from dsk.base.widgets.base_tree_widget.base_tw import BaseTW
from dsk.base.widgets.menu_context_action import MenuContextAction,Da
from dsk.base.widgets.menu_data_context import McDataContext
from dsk.base.utils.msg_utils import MsgUtils as log

#################################################################
class BaseContextTW(BaseTW):
    #######################
    def __init__(self, parent,parameter):
        super(BaseContextTW, self).__init__(parent,parameter)
        self._savePos = None # to avoid double
        self._popupMenuTree = None
        self._popupMenuItem = None
        self._contextMenuTree = list()
        self._contextMenuItem = list()

    def setContextMenuTree(self,alist):
        self._contextMenuTree = alist

    def setContextMenuItem(self,alist):
        self._contextMenuItem = alist

    def callbackTreeContext(self, action):
        what, subAction, arg = str(action.whatsThis()).split(Da)

        McDataContext.setWidget(self)
        for i in self._contextMenuTree:
            if what == i.actionName():
                i.setCheck(action.isChecked())
                msg = i.execute(subAction,arg)
                if msg != None:
                    try:
                        msg.setWidgetFrom(self)
                    except:
                        log.error("wrong globalInfoMsgReturn1")
                        return
                    appSignature = msg.getApplicationSignal()
                    #print("APP SIG",appSignature,self.sig)
                    if appSignature != "":
                        #self.emit(QtT.QtCore.SIGNAL(appSignature),msg)
                        self.sig['appSignature'].emit(msg)
                    #self.emit(QtT.QtCore.SIGNAL('contextMenuAction(PyQt_PyObject)'), msg)
                    self.sig['contextMenuAction'].emit(msg)
                break

    def callbackItemContext(self,action):
        what,subAction,arg = str(action.whatsThis()).split(Da)

        McDataContext.setWidget(self)
        for i in self._contextMenuItem:
            if what == i.actionName():
                i.setCheck(action.isChecked())
                msg = i.execute(subAction,arg)
                if msg != None:
                    try:
                        msg.setWidgetFrom(self)
                    except:
                        log.error("wrong globalInfoMsgReturn2")
                        return
                    appSignature = msg.getApplicationSignal()
                    print("APP SIG2",appSignature,self.sig)
                    if appSignature != "":
                        self.sig['appSignature'].emit(msg)
                        #self.emit(QtT.QtCore.SIGNAL(appSignature),msg)
                    #self.emit(QtT.QtCore.SIGNAL('contextMenuAction(PyQt_PyObject)'),msg)
                    self.sig['contextMenuAction'].emit(msg)
                break


    def contextMenuEvent(self,event):
        # qt overwrite

        pos = event.pos()
        if self._savePos == pos:
            return
        self._savePos = pos
        item = self.itemAt(pos)

        if not item:
            if self._popupMenuTree == None:
                if len(self._contextMenuTree) > 0:
                    self._popupMenuTree = MenuContextAction(self,
                                                            self._contextMenuTree)
                    self.connect(self._popupMenuTree,
                                 QtCore.SIGNAL("triggered(QAction *)"),
                                 self.callbackTreeContext)
                else:
                    return
            McDataContext.cleanClassVar()
            self._popupMenuTree.updateTextAction(self.objectName(),
                                                 McDataContext.unknown(),
                                                 self._contextMenuTree)
            self._popupMenuTree.popup(QtT.QtGui.QCursor.pos())
            for m in self._contextMenuTree:
                m.updateFromData(None,self,None)
        else:
            if self._popupMenuItem == None:
                if len(self._contextMenuItem) > 0:
                    self._popupMenuItem = MenuContextAction(self,
                                                            self._contextMenuItem)
                    self.connect(self._popupMenuItem,
                                 QtCore.SIGNAL("triggered(QAction *)"),
                                 self.callbackItemContext)
                else:
                    return

            data = item.getContain()
            for m in self._contextMenuItem:
                m.updateFromData(data,self,item)
            p = data.getPath()
            McDataContext.cleanClassVar()
            self._popupMenuItem.updateTextAction(self.objectName(),
                                                 p,
                                                 self._contextMenuItem)
            self._popupMenuItem.popup(QtT.QtGui.QCursor.pos())
