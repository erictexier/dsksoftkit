import os
import sys

from dsk.base.resources.dsk_errors import DskLaunchError
from dsk.base.resources.browser_signal import COMMAND_SIGNAL
styleName = ['cleanlooks','windows','motif','CDE','Plastique']

## Hold instance to avoid none widget hold to be clean by gc (garbage collector)
INSTANCE_KEEPER = dict()


###############################################################################
def qt_launch(mainInstance, **argv):
    from dsk.base.widgets.simpleqt import QtT

    app = QtT.QtCore.QCoreApplication.instance()

    if app == None:
        app = QtT.QtWidgets.QApplication(sys.argv)
    indexStyle = argv.get('indexStyle',0)

    # set the style
    if indexStyle >= 0 and indexStyle < len(styleName):
        style = QtT.QtWidgets.QStyleFactory.create(styleName[indexStyle])
        QtT.QtWidgets.QApplication.setStyle(style)


    # launch the ui
    window = mainInstance(None,**argv)
    if window.size().width() <= 0 or window.size().height() <= 0:
        window.resize(500,500)
        window.move(100,100)

    QtT.QtWidgets.QApplication.processEvents()


    window.show()
    window.raise_()

    try:
        sys.exit(app.exec_())
    except:
        pass
    return window

###############################################################################
def qt_launch_maya(mainInstance,**argv):

    """The multi Threading is not support in regular mode """
    from dsk.base.widgets.simpleqt import QtT
        #sip.wrapinstance = sip.wrapInstance
    from maya import OpenMayaUI as omui


    app = QtT.QtCore.QCoreApplication.instance()
    if app == None:
        app = QtT.Qwidgets.QApplication(sys.argv)

    ptr = omui.MQtUtil.mainWindow()

    parent = None
    if ptr != None:
        if QtT.which == "PySide2":
            try:
                import shiboken2
            except:
                from PySide2 import shiboken2
            parent = shiboken2.wrapInstance(int(ptr), QtT.QtWidgets.QMainWindow)
        else:
            try:
                import sip
                parent = sip.wrapinstance(int(ptr), QtT.QtCore.QObject)
            except Exception as e:
                raise DskLaunchError("Couldn't instance wrapper for qt %s" % str(e))
    else:
        return None
    window = mainInstance(parent, **argv)

    if window.size().width() <= 0 or window.size().height() <= 0:
        window.resize(700,500)
        window.move(100,100)

    QtT.QtWidgets.QApplication.processEvents()
    window.show()
    window.raise_()

    return window

###############################################################################
def qt_launch_mayapy(mainInstance,**argv):
    from dsk.base.widgets.simpleqt import QtT

    """ important to keep the QApplication creation before importing standalone
    to get a valid Gui QtCore app
    """
    app = QtT.QtCore.QCoreApplication.instance()
    if app == None:
        app = QtT.QtWidgets.QApplication(sys.argv)
    #app.setQuitOnLastWindowClosed(True)
    import maya.standalone as standalone
    standalone.initialize(os.path.basename(sys.argv[0]))
    import maya.cmds as cmds
    cmds.undoInfo(state=False)        # Turn off undo
    cmds.autoSave(enable=False)       # Turn off autosave

    window = mainInstance(None, **argv)

    if window.size().width() <= 0 or window.size().height() <= 0:
        window.resize(500,500)
        window.move(100,100)

    QtT.QtWidgets.QApplication.processEvents()
    window.show()
    window.raise_()
    try:
        sys.exit(app.exec_())
    except:
        pass
    return window

###############################################################################
def delete_window(windowName):
    global INSTANCE_KEEPER
    if windowName != "" and windowName in INSTANCE_KEEPER:
        INSTANCE_KEEPER[windowName].close()
        INSTANCE_KEEPER[windowName] = None
        return True
    return False

##############################
def is_window_loaded(windowName):
    global INSTANCE_KEEPER
    return windowName in INSTANCE_KEEPER

##############################
def get_window(windowName):
    global INSTANCE_KEEPER
    if is_window_loaded(windowName):
        return INSTANCE_KEEPER[windowName]
    return None

################################################################################
# LAUNCH AND LAUNCHMAYAPY
################################################################################
def launch(mainInstance,windowName, **argv):
    from dsk.base.widgets.simpleqt import QtT


    cfd = argv.get("cfd",None)
    if hasattr(cfd,'logger'):
        cfd.logger.info("using %s" % QtT.which)

    global INSTANCE_KEEPER
    assert windowName != ""
    if windowName in INSTANCE_KEEPER and INSTANCE_KEEPER[windowName] != None:
        INSTANCE_KEEPER[windowName].sig[COMMAND_SIGNAL.name].emit(argv)
        INSTANCE_KEEPER[windowName].show()
        INSTANCE_KEEPER[windowName].raise_()
        return INSTANCE_KEEPER[windowName]

    doMaya = False
    try:
        import maya.utils as utils
        doMaya=True
    except:
        pass
    argv.update({'objectName':windowName})
    if doMaya:
        INSTANCE_KEEPER[windowName] = qt_launch_maya(mainInstance, **argv)
    else:
        INSTANCE_KEEPER[windowName] = qt_launch(mainInstance, **argv)
    return INSTANCE_KEEPER[windowName]

##############################
def launchmayapy(mainInstance,windowName, **argv):
    """Special launch of qt for mayapy.
    The QtApp needs to be instantiate before the import standalone
    """
    #from dsk.base.widgets.simpleqt import QtT

    global INSTANCE_KEEPER
    assert windowName != ""
    if windowName in INSTANCE_KEEPER:
        INSTANCE_KEEPER[windowName].sig[COMMAND_SIGNAL.name].emit(argv)
        INSTANCE_KEEPER[windowName].show()
        INSTANCE_KEEPER[windowName].raise_()
        return INSTANCE_KEEPER[windowName]
    INSTANCE_KEEPER[windowName] = qt_launch_mayapy(mainInstance, **argv)
    return INSTANCE_KEEPER[windowName]


