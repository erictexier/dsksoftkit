_DATA='''from dsk.base.lib.base_app_handler import BaseAppHandler
from dsk.base.resources import browser_constant
from dsk.base.resources import default_toolkit
from %(name_space)s.%(module_name)s.lib.%(file_root_name)s_editor import %(TplToolsClassRoot)sEditor


class %(TplToolsClassRoot)sHandler(BaseAppHandler):
    """Manage initialization stage.
        create needed editor
        Bind app with main widget
    """
    def __init__(self, **argv):

        editor = argv.get('editor',None)
        if editor == None:
            #create the editor for this
            editor = %(TplToolsClassRoot)sEditor(**argv)
            argv.update({'editor':editor})
        super(%(TplToolsClassRoot)sHandler, self).__init__(**argv)

        cfd = argv.get('cfd', None)
        self.options = dict()
        if cfd:
            self.options = cfd.get_as_dict()

    def get_toollist(self):
        return default_toolkit.getDefaultToolsKit()

    def get_application_widget(self, parent):
        """build the ui"""
        from %(name_space)s.%(module_name)s.widgets.%(file_root_name)s_main import %(TplToolsClassRoot)sMain
        central = %(TplToolsClassRoot)sMain(parent,**self.options)
        # connect to global signal
        central.signalsCreate(self.get_editor())
        return central

#     def do_menu(self):
#         return False
'''