import os
import sys
if sys.version_info[0] >= 3:
    from six import string_types as basestring

import traceback
from collections import namedtuple
from pprint import pformat
import sgtk

from dsk.base.utils.msg_utils import MsgUtils as log

class SgHandle(namedtuple('SgHandle', "sg ctx tk")):
    __slots__ = ()
    """
    :param:
        This is comming from TD
        hold an sg (connection), sgtk object and a context from path
    """

class SgstoolsApp(object):
    pass


class SgtkUtils(object):
    """Convenience for tank
       Take an app and provide for simple query
    """
    GROUP_SHOTGUN = ["Supervisor", "Production", "ProductionPlus","Artist"]
    def __init__(self,app=None):
        super(SgtkUtils, self).__init__()
        self._app = None
        self.set_app(app)
        self.start_from_cmds = False

    def set_app(self, app, ashotgun=None):

        if self._app != None:
            self._close_app()

        self._app = app
        # connection
        self._connection = None
        self._tk = None
        if app != None:
            self._app = app
            # connection
            if hasattr(app,"shotgun"):
                self._connection = app.shotgun
                return True
        return False

    def set_external_app(self, an_handle):
        """Experiment not done
        """
        if not isinstance(an_handle, SgHandle):
            print("set_external_app: failed")
            return False
        if self._app != None:
            self._close_app()

    def _close_app(self):
        print("not done, should probably done internally _close_app")
        return False


    def is_valid(self):
        return self._app != None

    def is_dev(self):
        conf = self._app.tank.configuration_name
        return 'dev' in conf

    def get_context(self):
        if self.is_valid():
            return self._app.context
        return ""

    def get_user_context(self):
        if self.is_valid():
            return self._app.context.user
        return ""

    def get_task_name(self):
        if self.is_valid() and self._app.context.task != None:
            return self._app.context.task['name']
        return ""

    def get_task_entity(self):
        if self.is_valid() and self._app.context.task != None:
            return self._app.context.task
        return ""

    def get_step_name(self):
        if self.is_valid() and self._app.context.step != None:
            return self._app.context.step['name']
        return ""

    def get_step_entity(self):
        if self.is_valid() and self._app.context.step != None:
            return self._app.context.step
        return ""


    def get_project_entity(self): #
        anerror =  {'type': 'Project', 'name': 'UNKNOWN', 'id': -1}
        if not self.is_valid():
            return anerror
        if self._app.context.project == None:
            return anerror
        return self._app.context.project


    def print_info(self, debug=False):
        if not self.is_valid() or self.start_from_cmds == True:
            log.error("no app, cannot print anything")
            return


        log.info("project Entity %s" % self.get_project_entity())
        log.info("user_context %s" % self.get_user_context())
        log.info("status %s debug %s" % (self.is_allow('Artist',debug),debug))
        log.info("config name %s" % self._app.tank.configuration_name)
        log.info("config version %s" % self._app.tank.version)
        log.info("project path %s" % self._app.tank.project_path)

    def is_allow(self, agroup, debug=False):
        """INIT get user status
        """
        if debug == True:
            return True
        if self.is_valid():
            return False
        if isinstance(agroup,basestring):
            agroup = [agroup]
        filters = [["name", "is", self.get_user_context()["name"]]]
        fields = ["permission_rule_set"]
        val = self._connection.find_one("HumanUser", filters, fields)
        if str(val["permission_rule_set"]["name"]) in agroup:
            return True
        else :
            return False

    def is_artist(self):
        return self.is_allow('Artist')

    def is_sup(self):
        return self.is_allow('Supervisor')

    def is_crew(self):
        return self.is_allow(['Artist','Supervisor'])

    def get_show_name(self):
        return self.get_project_entity()['name']

    def get_user_name(self):
        return self.get_user_context()['name']

    def list_apps(self):
        project_path_root = os.environ.get('PROJECT_PATH',"")
        if project_path_root == "":
            return ""
        tk = tank.tank_from_path(project_path_root)
        ctx = tk.context_empty()
        engine = tank.platform.current_engine()
        try:
            return engine.apps
        except:
            return list()

    @staticmethod
    def start_engine(engine_name = "tk-shell"):
        """Start the given engine in the given context. If no context is provided, start
        the engine in the project context

        :param engine_name:  Name of the engine to start
        :returns:            The running engine
        """
        import tank

        current_engine = tank.platform.current_engine()
        if current_engine:
            return current_engine

        pc_path = os.environ.get("TANK_CURRENT_PC")
        #---------------------------------------------------------------------------
        try:
            tk = tank.sgtk_from_path(pc_path)
            ctx = tk.context_from_path(tk.project_path)
            current_engine = tank.platform.start_engine(engine_name, tk, ctx)
            return current_engine

        except Exception as e:
            log.error("Failed to start Engine - %s" % str(e))
            traceback.print_exc()
        return None

    def start_an_app(self, engine_name="tk-shell", app_name="mgtk-multi-extract"):
        # THIS IS TO TEST (there is an application development context) needs work
        # it will return an engine instance if it find a current engine
        current_engine = None
        app = None
        try:
            current_engine = self.start_engine(engine_name)
            app = current_engine.apps.get(app_name)
        except Exception as e:
            log.error("couldn't start app %r for engine %r" % (app_name, engine_name))
            log.error(str(e))
            return

        sg = None
        if hasattr(current_engine,"tank"):
            sg = current_engine.tank.shotgun
        if self.set_app(app,sg):
            self.start_from_cmds = True

    def show_app(self):
        if self.start_from_cmds:
            mmodule = self._app.import_module(self._app.name)
            mmodule.show_dialog(self._app)

