#!/usr/bin/env python

import os
import sys
import types
from dsk.base.widgets.simpleqt import QtT

from dsk.base.utils.msg_utils import MsgUtils as log
from dsk.base.widgets.base_tree_widget.base_tw import BaseTW
from dsk.base.resources import browser_signal as confsig

labelTree = ["Setting"]
winSize = [400,400]
prefSize =  [200]
dictParm  = {"Label":labelTree,
             "Size" : winSize,
             "AltColor": True,       # alternate color in row
             "Icons"   : True,
             }

#################################################################
class SimpleTreeEdit(BaseTW):
    #######################
    def __init__(self, parameter,parent=None):
        super(SimpleTreeEdit, self).__init__(parent,parameter)
        self.connectLocalSignal()

    #######################
    def connectLocalSignal(self):
        self.itemPressed.connect(self.updateCurrent)
    #######################
    def disconnectLocalSignal(self):
        self.itemPressed.disconnect(self.updateCurrent)
    #######################
    def getPath(self,item):
        if item == None:
            return ""
        key = item.text(0)
        ancestor = item.parent()
        while ancestor:
            key.prepend(ancestor.text(0) + os.sep)
            ancestor = ancestor.parent()
        return str(key)

    #######################
    def updateCurrent(self,item,c):
        key = self.getPath(item)
        self.sig[confsig.SELECTION_ITEM_CHANGE].emit(key)
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
