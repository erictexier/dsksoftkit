from dsk.base.widgets.simpleqt import QtT
from dsk.base.widgets.splash_dialog import DskSplash


def get_splash():
    splash = DskSplash()
    splash.show()
    QtT.QtWidgets.QApplication.processEvents()
    return splash
