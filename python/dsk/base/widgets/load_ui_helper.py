#--------------------------------------------------------
# HELPER FUNCTION TO LOADUITYPE
#--------------------------------------------------------
import sys

class LoadUi(object):
    '''
       an helper to support loadUiType
    '''
    def __init__(self):
        pass

    @staticmethod
    def loadUiType(uiFile):
        '''
        Pyside lacks the "loadUiType" command, so we have to convert the ui file to py code in-memory first
        and then execute it in a special frame to retrieve the form_class.
        '''

        import pysideuic
        import xml.etree.ElementTree as xml
        from io import StringIO

        import PySide.QtGui

        parsed = xml.parse(uiFile)
        widget_class = parsed.find('widget').get('class')
        form_class = parsed.find('class').text

        with open(uiFile, 'r') as f:
            o = StringIO()
            frame = {}

            pysideuic.compileUi(f, o, indent=0)
            pyc = compile(o.getvalue(), '<string>', 'exec')
            exec(pyc, frame)

            #Fetch the base_class and form class based on their type in the xml from designer
            form_class = frame['Ui_%s'%form_class]


            base_class = eval('PySide.QtGui.%s'%widget_class)

        return form_class, base_class

    @staticmethod
    def loadUi(uiFile,wid, add_layout=True):
        '''
        load a uiFile and wrap its Qt instance under wid
        '''
        from PySide.QtUiTools import QUiLoader
        from PySide import QtGui

        loader = QUiLoader()

        ui = loader.load(uiFile, wid)

        for i in vars(ui):
            try:
                if not i.startswith("_"):
                    exec("wid.%s = ui.%s" % (i,i))
            except:
                pass


        if add_layout:
            layout = QtGui.QVBoxLayout()
            layout.addWidget(ui)
            wid.setLayout(layout)
        return ui

class LoadUiPySide2(object):
    """Helper to support loadUiType
    """
    def __init__(self):
        pass

    @staticmethod
    def loadUiType(uiFile):
        '''
        Pyside lacks the "loadUiType" command, so we have to convert the ui file to py code in-memory first
        and then execute it in a special frame to retrieve the form_class.
        '''

        import pyside2uic
        import xml.etree.ElementTree as xml
        if sys.version_info[0] == 2:
            from cStringIO import StringIO
        else:
            from io import StringIO

        import PySide2.QtWidgets
        parsed = xml.parse(uiFile)
        widget_class = parsed.find('widget').get('class')
        form_class = parsed.find('class').text

        with open(uiFile, 'r') as f:
            o = StringIO()
            frame = {}
            pyside2uic.compileUi(f, o, indent=0)
            pyc = compile(o.getvalue(), '<string>', 'exec')
            exec(pyc, frame)

            #Fetch the base_class and form class based on their type in the xml from designer
            form_class = frame['Ui_%s'%form_class]
            base_class = eval('PySide2.QtWidgets.%s'%widget_class)

        return form_class, base_class

    @staticmethod
    def loadUi(uiFile,wid, add_layout=True):
        '''
        load a uiFile and wrap its Qt instance under wid
        '''

        from PySide2 import QtUiTools
        from PySide2 import QtWidgets,QtCore

        loader = QtUiTools.QUiLoader()
        uifile = QtCore.QFile(uiFile)
        uifile.open(QtCore.QFile.ReadOnly)
        ui = loader.load(uifile, wid)
        uifile.close()

        """
        for i in vars(ui):
            try:
                if not i.startswith("_"):
                    exec("wid.%s = ui.%s" % (i,i))
            except:
                pass
        """
        if add_layout:
            layout = QtWidgets.QVBoxLayout()
            layout.addWidget(ui)
            wid.setLayout(layout)
        return ui


class LoadUiPyQt5(object):
    """Helper to support loadUiType
    """
    def __init__(self):
        pass

    @staticmethod
    def loadUiType(uiFile):
        '''
        Pyside lacks the "loadUiType" command, so we have to convert the ui file to py code in-memory first
        and then execute it in a special frame to retrieve the form_class.
        '''

        from PyQt5 import uic
        import xml.etree.ElementTree as xml
        if sys.version_info[0] == 2:
            from cStringIO import StringIO
        else:
            from io import StringIO

        import PyQt5.QtWidgets
        parsed = xml.parse(uiFile)
        widget_class = parsed.find('widget').get('class')
        form_class = parsed.find('class').text

        with open(uiFile, 'r') as f:
            o = StringIO()
            frame = {}
            uic.compileUi(f, o, indent=0)
            pyc = compile(o.getvalue(), '<string>', 'exec')
            exec(pyc, frame)

            #Fetch the base_class and form class based on their type in the xml from designer
            form_class = frame['Ui_%s'%form_class]
            base_class = eval('PyQt5.QtWidgets.%s'%widget_class)

        return form_class, base_class

    @staticmethod
    def loadUi(uiFile,wid, add_layout=True):
        '''
        load a uiFile and wrap its Qt instance under wid
        '''
        from PyQt5.uic import loadUi
        from PyQt5 import QtWidgets
        ui = loadUi(uiFile,wid)

        if add_layout:
            layout = QtWidgets.QVBoxLayout()
            layout.addWidget(ui)
            wid.setLayout(layout)
        return ui
