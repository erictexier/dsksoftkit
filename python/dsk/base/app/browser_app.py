import types
from dsk.base.widgets.simpleqt import QtT

SIGNAL = QtT.QtCore.SIGNAL

from dsk.base.resources import browser_default
from dsk.base.resources import browser_signal as confsig
from dsk.base.lib.default_path import DefaultPath
from dsk.base.lib.base_app_handler import BaseAppHandler
from dsk.base.lib.msg_arg import MsgFirstTime
### function to be share across mainwindow
import dsk.base.app.main_window_helper as MWH




class BrowserApp(QtT.QtWidgets.QMainWindow):
    """
    top class main window:

    a wrapper for application providing basic functionality.

    main argument are option handler and initModule
        - the handler define the functionality
        - initModule define local data, like appName, version etc...

    """
    def __init__(self, parent, **argv):

        super(BrowserApp, self).__init__(parent)

        self.setDockNestingEnabled(True)
        windowName = argv.get('objectName',"browserApp")

        self.setObjectName(windowName)

        # keep track of the different dock
        self._docksWidget = {}
        # An editor: must be a subclass of BaseEditor
        self._browserEditor = None
        # see toolKit in the resources folder
        self._toolList = dict()
        handler = argv.get('handler',None)

        if handler == None:
            import dsk.base
            argv.update({'initModule':dsk.base})
            hinstance = BaseAppHandler(**argv)

        else:
            # check api
            #assert type(handler) == types.TypeType
            assert BaseAppHandler == handler.mro()[-2]
            hinstance = handler(**argv)

        ######################
        # query/set the editor
        self.set_editor(hinstance.get_editor())
        # query the tool List
        self._toolList = hinstance.get_toollist()
        # window tile
        self.setWindowTitle(self.tr(self.window_title()))

        # build the optional document and the preference
        self.get_editor().create_document_data()

        #####################


        # preference
        self.get_editor().load_preference(self)

        if browser_default.DO_LOG and self.get_editor().do_log():
            self.get_editor().start_log()

        ##############
        # init the different actor
        ##############
        ui_path = argv.get('ui_path',None)
        if ui_path != None:
            self.ui = QtT.uic.loadUi(ui_path,self)
            if hasattr(self,'setup_interface') == True:
                self.setup_interface()

        else:

            if hinstance.do_menu():
                self.makeMenu(hinstance.need_quit())
            else:
                self.menuBar().hide()
            self.statusBar().hide()

        # this sequence of initialization may be different with the app has
        # a central widget so we break here to let subclass with application widgets
        # do their own stuff

        apl = hinstance.get_application_widget(self)
        if apl:
            self.editorDataAndSignal()

            self.loadLayout(self.get_editor().get_layout_file())
            self.setCentralWidget(apl)

        else:
            self.editorDataAndSignal()
            self.loadLayout(self.get_editor().get_layout_file())


        hinstance.register_option(self)

        msg = MsgFirstTime(apl,first=True)
        self.sig[confsig.INIT_FIRST_TIME.name].emit(msg)
    ## END INIT

    def get_editor(self):
        return self._browserEditor
    def set_editor(self,editor):
        self._browserEditor = editor
    ################
    # editor stuff
    #################
    def editorDataAndSignal(self):
        self.get_editor().request_connect(self, confsig.INIT_FIRST_TIME.name, True)
        self.get_editor().request_connect(self, confsig.OPTION_CHANGE.name, True)
        self.get_editor().request_connect(self, confsig.RICH_COLOR_CHANGE.name, True)
        self.get_editor().request_connect(self, confsig.COMMAND_SIGNAL.name, True)

    #######################
    def get_interest_file(self):
        return self.get_editor().get_shot_interest()

    #######################
    # MENU
    #######################
    #######################
    # MENU FILE
    def makeFileMenu(self,needQuit=False):

        ##############
        # file Menu
        ##############
        if not needQuit:
            return None

        fileMenu = QtT.QtQtWidgets.QMenu(self.tr("&File"), self)
        quitAction = fileMenu.addAction(self.tr("&Quit"))
        quitAction.setShortcut(QtT.QtGui.QKeySequence(self.tr("Ctrl+Q")))
        self._qAct = quitAction
        return fileMenu


    #######################
    # MENU TOOL
    def makeToolMenu(self):
        if len(self._toolList) == 0:
            return None

        toolMenu = QtT.QtWidgets.QMenu(self.tr("&Tools"), self)
        nameToolList = map(lambda x: self._toolList[x].name,self._toolList.keys())
        for widgetName in nameToolList:
            toolMenu.addAction(self.tr(widgetName))

        toolMenu.triggered.connect(self.toolInstanciate)
        return toolMenu

    #######################
    # MENU OPTION
    def makeOptionMenu(self):
        self._optionMenu = QtT.QtWidgets.QMenu(self.tr("Option"), self)
        self._optionMenu.triggered.connect(self.optionCallback)
        return self._optionMenu

    def clearMenuOption(self):
        if hasattr(self,'_optionMenu'):
            self._optionMenu.clear()

    def addSubOptionMenu(self,aname,dd):
        if hasattr(self,'_optionMenu'):
            MWH.H_addSubOptionMenu(self,self._optionMenu,aname,dd)

    def removeSubOptionMenu(self,aname):
        if hasattr(self,'_optionMenu'):
            MWH.H_removeSubOptionMenu(self._optionMenu,aname)

    def optionCallback(self,action):
        MWH.H_optionCallback(self,action)

    ###############################################
    # MENU
    def makeMenu(self,needFileMenu=False):

        fileMenu = self.makeFileMenu(needFileMenu)
        toolMenu = self.makeToolMenu()
        if toolMenu != None:
            optionMenu = self.makeOptionMenu()
        else:
            optionMenu = None

        ##############
        # layout menu
        #############
        self._layoutMenu = QtT.QtWidgets.QMenu(self.tr("&Layout"), self)
        self.updateLayout()
        self._layoutMenu.triggered.connect(self.layoutAction)
        ##############
        # preference menu
        #############
        prefMenu = MWH.H_prefMenu(self)
        if browser_default.DO_LOG:
            prefMenu.addAction(self.tr("startLog"))
            prefMenu.addAction(self.tr("endLog"))
        prefMenu.triggered.connect(self.prefAction)

        ##############
        # help Menu
        ##############
        helpMenu = QtT.QtWidgets.QMenu(self.tr("&Help"), self)
        aAct = helpMenu.addAction(self.tr("Quick Start"))
        #SIGNAL
        aAct.triggered.connect(self.quick_start)

        aAct = helpMenu.addAction(self.tr("Documentation"))
        aAct.triggered.connect(self.app_doc)

        if  browser_default.DO_LOG:
            aAct = helpMenu.addAction(self.tr("Send bug"))
            aAct.triggered.connect(self.get_editor().send_report)


        aAct = helpMenu.addAction(self.tr("About"))
        aAct.triggered.connect(self.about)

        self._editPlace = self._layoutMenu # hook to add an edit menu

        if fileMenu != None:
            self.menuBar().addMenu(fileMenu)
        if toolMenu != None:
            self.menuBar().addMenu(toolMenu)
            self._editPlace = toolMenu
        if optionMenu != None:
            self.menuBar().addMenu(optionMenu)

        self.menuBar().addMenu(self._layoutMenu)
        self.menuBar().addMenu(prefMenu)
        self.menuBar().addSeparator()
        self.menuBar().addMenu(helpMenu)


    ##############################################
    # DOCK STUFF
    ##############################################
    def toolInstanciate(self,widgetNameAction,aname=""):
        MWH.H_toolInstanciate(self,self.get_editor(),widgetNameAction,aname="")
    ###
    def removeDock(self, name):
        """ call from the dock widget """
        MWH.H_removeDock(self, self.get_editor(),name)
    ###
    def clearAllDocks(self):
        MWH.H_clearAllDocks(self)

    ### title menu
    def window_title(self):
        about = self.get_editor().get_about()
        if about:
            return "%s -- %s -- %s" % (about.app_name,
                                       about.version,
                                       about.repo_version)
        return "no app"
    #######################
    # menu callBack
    #######################
    def about(self):

        message =  "<h2>%s %s</h2>"
        message += "<h2><p>Copyright: %s</p></h2>"
        message += "<h2>%s</h2>"
        about = self.get_editor().get_about()
        if about:
            msg = message % (about.app_name,
                             about.version,
                             browser_default.ANAPP_YEAR,
                             about.company)

            QtT.QtWidgets.QMessageBox.about(self,self.tr("About this App"),self.tr(msg))


    #######################
    def app_doc(self):
        sup = self.get_editor().get_support()
        if sup:
            MWH.H_documentation(self, sup.doc)

    #######################
    def quick_start(self):
        sup = self.get_editor().get_support()
        if sup:
            MWH.H_webpagequickstart(self, sup.quickstart)

    #######################
    def closeEvent(self,event):
        self.get_editor().save_pref_at_closing()
        if event != None:
            event.accept()
            pass

    #######################
    def doQuit(self):
        self.get_editor().save_pref_at_closing()
        #self.disconnect(self._qAct,
        #                QtT.QtCore.SIGNAL("triggered()"),
        #                QtT.QtGui.qApp,
        #                QtT.QtCore.SLOT("quit()"))
        #self.disconnect(self._qAct, QtT.QtCore.SIGNAL("triggered()"),self.doQuit)
        try:
            self._qAct.triggered.disconnect(self.doQuit)
        except:
            print("No Quit")
        QtT.QtGui.qApp.quit()

    ######################
    def prefAction(self,action):
        MWH.H_prefAction(self,self.get_editor(),action)

    #######################
    # layout management
    #######################
    def updateLayout(self):
        MWH.H_updateLayout(self,self.get_editor())
    #######################
    def layoutAction(self,action):
        MWH.H_layoutAction(self,self.get_editor(),action)
    #######################
    def saveLayout(self,nameLayout):
        MWH.H_saveLayout(self,self.get_editor(),nameLayout)
    #######################
    def loadLayout(self,nameLayout):
        MWH.H_loadLayout(self,self.get_editor(), DefaultPath, nameLayout)

class BrowserAppTest(QtT.QtWidgets.QMainWindow):
    def __init__(self, parent, **argv):
        super(BrowserAppTest, self).__init__(parent)


