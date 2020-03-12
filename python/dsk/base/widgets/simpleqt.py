from collections import namedtuple

class qtt(namedtuple('Qtt',"QtCore QtGui QtWidgets uic which")):
    __slots__ = ()

class qte(namedtuple('Qte',"QtNetwork QWebPage QWebView which")):
    __slots__ = ()

class qtall(namedtuple('Qtall',"QtCore QtGui QtWidgets QtNetwork QWebPage QWebView uic which")):
    __slots__ = ()


###### Base Qt Model
QtCore = None
QtGui = None
QtWidgets = None
uic = None
QtNetwork  = None
QWebPage = None
QWebView = None

vers = ""
try:
    from PySide2 import QtCore, QtGui, QtWidgets
    from dsk.base.widgets.load_ui_helper import LoadUiPySide2 as uic
    vers = "PySide2"
    QtCore.SIGNAL = QtCore.Signal
    QtCore.SLOT = QtCore.Slot

except:
    try:
        from PyQt5 import QtCore, QtGui, QtWidgets
        from dsk.base.widgets.load_ui_helper import LoadUiPyQt5 as uic
        QtCore.SIGNAL = QtCore.pyqtSignal
        QtCore.SLOT = QtCore.pyqtSlot
        vers = "PyQt5"
    except:
        try:
            from PyQt4 import QtCore, QtGui, uic
            QtWidgets = QtGui
            QtCore.SIGNAL = QtCore.pyqtSignal
            QtCore.SLOT = QtCore.pyqtSlot
            vers = "PyQt4"
        except:
            from PySide import QtCore, QtGui
            QtWidgets = QtGui
            from dsk.base.widgets.load_ui_helper import LoadUi as uic
            QtCore.SIGNAL = QtCore.Signal
            QtCore.SLOT = QtCore.Slot

            vers = "PySide"

QtT = qtt(QtCore,QtGui,QtWidgets,uic,vers)

###### LOAD EXTRA Network and Web
try:
    from PySide2 import QtNetwork
    from PySide2.QtWebEngineWidgets import QWebEngineView as QWebView,QWebEnginePage as QWebPage
    from PySide2.QtWebEngineWidgets import QWebEngineSettings as QWebSettings
    #from PySide2.QtWebKitWidgets import QWebView
    #from PySide2.QtWebKitWidgets import QWebPage
    vers = "PySide2"
except:
    try:
        from PyQt5 import QtNetwork
        from PyQt5.QtWebEngineWidgets import QWebEngineView as QWebView,QWebEnginePage as QWebPage
        from PyQt5.QtWebEngineWidgets import QWebEngineSettings as QWebSettings
        #from PyQt5.QtWebKitWidgets import QWebView
        #from PyQt5.QtWebKitWidgets import QWebPage

        vers = "PyQt5"
    except:
        from PyQt4 import QtNetwork
        from PyQt4.QtWebKit import QWebView
        from PyQt4.QtWebKit import QWebPage
        vers = "PyQt4"

QtE = qte(QtNetwork, QWebPage, QWebView,vers)
QtAll = qtall(QtCore,QtGui,QtWidgets,QtNetwork, QWebPage, QWebView,uic,vers)