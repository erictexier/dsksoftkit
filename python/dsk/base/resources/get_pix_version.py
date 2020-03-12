import os

from dsk.base.widgets.simpleqt import QtT

from dsk.base.lib.default_path import DefaultPath
from dsk.base.resources.icon_cache import init_default_pixmap

Icon_NF = 'icon_not_found'
Iconfile_default = DefaultPath.getIconFile('noeye_orange.png')

CashPix = dict()

def get_pixmap(iconfile, versionobject, force=False):
    global CashPix
    if iconfile in ["",None]:
        n = versionobject.getTypeName()
        if n in CashPix:
            return CashPix[n]
    else:
        n = versionobject.getTypeName()


    if n in CashPix and force == False:
        return CashPix[n]

    pix = None
    if os.path.isfile(iconfile):
        pix = QtT.QtGui.QPixmap(iconfile)
        CashPix[iconfile] = CashPix[n] = pix
        init_default_pixmap(n,pix)
        return pix


    if Icon_NF  in CashPix:
        return CashPix[Icon_NF]
    else:
        pix = QtT.QtGui.QPixmap(Iconfile_default)
        CashPix[Icon_NF] = CashPix[n] = pix
        init_default_pixmap(n,pix)
        return pix
    return pix

