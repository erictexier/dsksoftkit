""" icons """
import os

from dsk.base.widgets.base_tree_widget.base_tw import AttrUiDescription
from dsk.base.lib.default_path import DefaultPath
from dsk.base.widgets.simpleqt import QtT

QIcon = QtT.QtGui.QIcon
defaultIcon = dict()

def init_default_icon(t,v):
    global defaultIcons
    defaultIcon[t] = AttrUiDescription(QIcon(v))
    return defaultIcon

def init_default_pixmap(t,px):
    global defaultIcons
    defaultIcon[t] = AttrUiDescription(QIcon(px))
    return defaultIcon

def update(t,apath=None):
    v = apath
    if apath == None:
        v = DefaultPath.getIconFile(t)
    if os.path.isfile(v):
        return init_default_icon(t,v)
    return defaultIcon

def getDefaultIconTask():
    return defaultIcon