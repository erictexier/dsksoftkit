"""Base class to specialize the app behavior.
Tag as 'handler' for the browserApp.
BrowserApp Will instantiate one of those at initialization
"""

from dsk.base.lib.base_editor import BaseEditor
from dsk.base.tdata.taskdata.tp_variable import TpVariable


class BaseAppHandler(object):

    def __init__(self,**arg):
        """
        :param:
            editor (BaseEditor): optional
            toollist (dict): list of tool to be instanciated
            rtd (runtime data)
            cfd (config data)
            tkd (task data)
        """
        super(BaseAppHandler,self).__init__()

        self._toolList = arg.get('toollist',dict()) if arg else None

        self._editor = arg.get('editor',None)
        if self._editor == None:
            self._editor = BaseEditor(**arg)

        self._runtimedata = arg.get('rtd',None) if arg else None
        self._configdata = arg.get('cfd',None) if arg else None
        self._taskdata = arg.get('tkd',None) if arg else None

        if self._runtimedata == None:
            self._runtimedata = TpVariable()

        if self._configdata == None:
            self._configdata = TpVariable()
            self._configdata.debug = False

        if self._taskdata == None:
            self._taskdata = TpVariable()

        logger = None
        if hasattr(self._configdata, 'do_log') and self._configdata.do_splash:
            from dsk.base.lib.log_manager import LogManager
            l = LogManager()
            l.initialize_custom_handler()
            l.global_debug = True
            logger = l.get_logger(__name__)

        if hasattr(self._configdata, 'do_splash') and self._configdata.do_splash:
            try:
                from dsk.base.utils import qt_utils
                if self._configdata.do_splash == True:
                    self._configdata.splash = qt_utils.get_splash()
                    self._configdata.splash.hide()
            except Exception as e:
                if logger:
                    logger.warning("%s" % str(e))


        if hasattr(self._configdata, 'do_auth') and self._configdata.do_auth:
            from dsk.base.conn_helper import shotgun_startup as SGS
            if self._configdata.do_auth == True:
                #get_user_credential
                user = SGS.get_user()
                self._runtimedata.connection = SGS.get_user_connection(user)


    def get_editor(self):
        """Returns the editor """
        return self._editor
    def get_toollist(self):
        """Return the toollist """
        return self._toolList
    def get_config_data(self):
        return self._configdata
    def get_runtime_data(self):
        return self._runtimedata
    def get_task_data(self):
        return self._taskdata

    def get_application_widget(self,parent):
        """ return the main application widget """
        return None
    def register_option(self, widgetapp):
        """ call back after main window initialization is done """
        pass

    def do_menu(self):
        """ to build menu or not .... in progress """
        return self._configdata.debug

    def need_quit(self):
        # when for maya you don't want the file/quit
        return False

    @staticmethod
    def hasMaya():
        try:
            import maya.utils as utils
        except:
            return False
        return True
    @staticmethod
    def hasNuke():
        return False
    @staticmethod
    def hasRv():
        return False
