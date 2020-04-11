_DATA='''"""Main App Template"""
from dsk.base.app.browser_app import BrowserApp

class %(TplToolsClassRoot)sApp(BrowserApp):
    def __init__(self, parent, **argv):
        modu = argv.get('initModule',None)
        if modu == None:
            from %(name_space)s.%(module_name)s.resources import %(file_root_name)s_info
            argv.update({'initModule': %(file_root_name)s_info})
        handler =  argv.get('handler',None)
        if handler == None:
            from %(name_space)s.%(module_name)s.lib.%(file_root_name)s_handler import %(TplToolsClassRoot)sHandler
            argv.update({'handler': %(TplToolsClassRoot)sHandler})
        super(%(TplToolsClassRoot)sApp, self).__init__(parent,**argv)

    #################
    def editorDataAndSignal(self):
        super(%(TplToolsClassRoot)sApp, self).editorDataAndSignal()
'''