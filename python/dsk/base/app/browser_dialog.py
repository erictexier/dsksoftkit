import types
from dsk.base.widgets.simpleqt import QtT
SIGNAL = QtT.QtCore.SIGNAL

from dsk.base.resources import browser_default
from dsk.base.resources import browser_signal as confsig
from dsk.base.lib.default_path import DefaultPath
from dsk.base.lib.base_app_handler import BaseAppHandler
from dsk.base.lib.msg_arg import MsgFirstTime
import dsk.base.app.main_window_helper as MWH

class BrowserDialog(QtT.QtWidgets.QDialog):
    """
    top class main window:

    a wrapper for application providing basic functionality.

    main argument are option handler and initModule
        - the handler define the functionality
        - initModule define local data, like appName, version etc...


    Default menu:
        - preferences
        - layout
        - tools and option (docks)
        - files
        - help

    """
    def __init__(self, parent, **argv):

        super(BrowserDialog, self).__init__(parent)

        windowName = argv.get('objectName',"DialogApp")

        self.setObjectName(windowName)

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
            self.ui = uic.loadUi(ui_path,self)
            if hasattr(self,'setup_interface') == True:
                self.setup_interface()
        ''''
        else:

            if hinstance.do_menu():
                self.makeMenu(hinstance.need_quit())
            else:
                self.menuBar().hide()
            self.statusBar().hide()
        '''
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
        #self.get_editor().request_connect(self, confsig.OPTION_CHANGE.name, True)
        #self.get_editor().request_connect(self, confsig.RICH_COLOR_CHANGE.name, True)
        self.get_editor().request_connect(self, confsig.COMMAND_SIGNAL.name, True)

    #######################
    def get_interest_file(self):
        return self.get_editor().get_shot_interest()

    ### title menu
    def window_title(self):
        about = self.get_editor().get_about()
        if about:
            return "%s -- %s -- %s" % (about.app_name,
                                       about.version,
                                       about.repo_version)
        return "no app"
    #######################
    def saveLayout(self,nameLayout):
        MWH.H_saveLayout(self,self.get_editor(),nameLayout)
    #######################
    def loadLayout(self,nameLayout):
        MWH.H_loadLayout(self,self.get_editor(), DefaultPath, nameLayout)

