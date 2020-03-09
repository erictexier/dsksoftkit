"""Base class to centralize the app behavior.
Tag as 'editor' for the BaseAppHandler.
BaseAppHandler Will instantiate a default if not define or the app itself
"""
from dsk.base.widgets.simpleqt import QtT

from dsk.base.tdata.tdata import Tdata
from dsk.base.utils.msg_utils import MsgUtils as log
from dsk.base.lib.user_profile import UserProfile
from dsk.base.resources import browser_signal as confsig

from dsk.base.lib.signal_info import make_signal_instance

################################################
class BaseEditor(QtT.QtCore.QObject):

    def __init__(self,**args):
        """ instantiate a user profile (optionally define with a userProfile key
        """
        super(BaseEditor,self).__init__()
        self._currentGroup = None
        self._copyBuffer  = None
        self._prefs = None
        hu = args.get('userProfile',UserProfile)
        self._homeUser = hu(**args)
        self.init_signal()
        self._window = None

    #######################
    def get_pref(self):
        return self._prefs
    #######################
    def get_document(self):
        return self._currentGroup

    #######################
    def set_document(self,group):
        self._currentGroup = group

    #######################
    def get_document_top(self):
        # support for children parent interface
        if self._currentGroup == None:
            return None
        if hasattr(self._currentGroup,"getTop"):
            return self._currentGroup.getTop()
        return self._currentGroup

    #######################
    def create_document_data(self):
        # we create a Tdata here but it can be overwrite later
        self._currentGroup = Tdata()
        self._currentGroup.setName("TOP")
        self.make_preference()
        return self._currentGroup

    ###########################
    def get_user_profile(self):
        return self._homeUser

    ###########################
    def get_sgtk_utils(self):
        return self._homeUser.get_sgtk()

    def get_about(self):
        if self._homeUser != None:
            return self._homeUser.get_about()
        return None

    def get_support(self):
        if self._homeUser != None:
            return self._homeUser.get_support()
        return None


    def get_pref_file(self):
        r = ""
        if self._homeUser != None:
            r = self._homeUser.get_pref_file()
        return r

    def get_pref_root(self):
        r = ""
        if self._homeUser != None:
            r = self._homeUser.get_root_path()
        return r


    def make_preference(self):
        if self._homeUser != None:
            self._prefs = self._homeUser.make_preference()
            self._prefs.setName("appPreference")
        return self._prefs
    # END OVERLOAD
    ##############################################
    # preference: each user as single preference file
    def load_preference(self, wi):
        #pref = None

        if self._homeUser != None:
            self._prefs = self._homeUser.load_preference()
        try:
            self.set_style(wi)
        except:
            pass

    ######################
    # color and font
    def set_style(self, wi):
        self.windowapp = wi # this is usefull to pass parent widget to dialog
        from dsk.base.resources import default_style
        dd = {}
        # capital key have to be matching the default_style.py
        dd["TEXTCOLOR"] = self._prefs['globalPreference']['TextColor']
        dd["BGCOLOR"] = self._prefs['globalPreference']['BgColor']
        dd["SELECTCOLOR"] = self._prefs['globalPreference']['SelectColor']
        dd["SELECTBGCOLOR"] = self._prefs['globalPreference']['SelectBgColor']
        dd['HANDLE'] = dd["TEXTCOLOR"]
        dd['SCROLLBG']= self._prefs['globalPreference']['BgColor']
        dd['FONTSIZE'] = self._prefs['globalPreference'].get_global_font_size()
        if hasattr(default_style,'shotgunStyle'):
            wi.setStyleSheet(default_style.shotgunStyle % dd)
        else:
            wi.setStyleSheet(default_style.styleUser % dd)
        return dd

    def get_global_preference(self):
        return self._prefs['globalPreference']

    # basic preference handling
    # font
    def reset_font_preference(self, wi):
        self.set_font_size(10, wi)

    def set_font_size(self,fsize, wi):
        self._prefs['globalPreference'].set_global_font_size(fsize)
        self.set_style(wi)

    def get_global_font_size(self):
        return self._prefs['globalPreference']['GlobalFontSize']

    def set_text_color(self,color, wi):
        self._prefs['globalPreference']['TextColor'] = str(color.name())
        self.set_style(wi)

    def get_text_color(self):
        return self._prefs['globalPreference']['TextColor']

    def set_bg_color(self,color, wi):
        self._prefs['globalPreference']['BgColor'] = str(color.name())
        self.set_style(wi)

    def get_bg_color(self):
        return self._prefs['globalPreference']['BgColor']

    def set_select_color(self,color, wi):
        self._prefs['globalPreference']['SelectColor'] = str(color.name())
        self.set_style(wi)

    def get_select_color(self):
        return self._prefs['globalPreference']['SelectColor']

    def set_select_bg_color(self,color, wi):
        self._prefs['globalPreference']['SelectBgColor'] = str(color.name())
        self.set_style(wi)

    def get_select_bg_color(self):
        return self._prefs['globalPreference']['SelectBgColor']

    def reset_style_preference(self, wi):
        if self._prefs != None:
            self._prefs.reset_pref()
        self.set_style(wi)

    # rich color
    def set_rich_color(self,d):
        self._prefs['globalPreference'].set_rich_color(d)

    def get_rich_color(self):
        d = dict()
        d.update(self._prefs['globalPreference'].get_rich_color())
        return d

    # recent file
    def get_max_recent_file(self):
        return self._prefs['globalPreference']['MaxRecentFile']

    # log
    def do_log(self):
        return self._prefs['globalPreference']['DoLog']

    # shot interest
    def get_shot_interest(self):
        return self._prefs['globalPreference']['ShotInterest']

    def set_shot_interest(self,a):
        self._prefs['globalPreference']['ShotInterest'] = a

    # layout file
    def set_layout_file(self,ff):
        self._prefs['globalPreference']['LayoutFile'] = ff

    def get_layout_file(self):
        return self._prefs['globalPreference']['LayoutFile']

    def get_layout_names(self):
        r = ""
        if self._homeUser != None:
            r = self._homeUser.get_layout_names()
        return r

    def layout_file(self,name):
        r = ""
        if self._homeUser != None:
            r = self._homeUser.layout_file(name)
        return r


    #######################
    # save
    def save_pref_at_closing(self):
        if self._homeUser != None and self.save_on_exit():
            return self._homeUser.save_preference()
        return False

    def save_on_exit(self):
        return self._prefs['globalPreference']['SavePreferenceOnExit']

    def set_save_on_exit(self,val):
        self._prefs['globalPreference']['SavePreferenceOnExit'] = val

    def show_menu(self):
        return self._prefs['globalPreference']['ShowMenu']

    def get_recent_file(self):
        if self._homeUser != "":
            return self._homeUser.get_recent_file()
        log.info("no recentfile path defined")
        return ""

    #######################
    # the log view
    #######################
    def get_log_file(self):
        if self._homeUser != "":
            return self._homeUser.get_log_file()
        log.info("noLogFile")
        return ""

    def start_log(self):
        if self._homeUser != "":
            self._homeUser.start_log(self)


    def end_log(self):

        if self._homeUser != "":
            self._homeUser.end_log()

    # send report
    def send_report(self,**extra):
        if self._homeUser != "":
            self._homeUser.send_report(currentGroup=self.get_document_top(),**extra)

    ############################################################################################
    # signal handling
    ############################################################################################
    def declare_signal(self, xsignal, callback = None, argswhendone = None):
        """ Create signal instance and store them
        """
        from dsk.base.lib.signal_info import signalInfo
        signalname = xsignal.name

        if signalname in self._signalAssign:
            raise Exception("signal %s already declare" % signalname)

        # check the Done signal is not already in the dictionary
        if signalname[:-4] in self._signalAssign:
            raise Exception("signal %s used for %s" % (signalname,signalname[:-4]))

        # create the 2 signals
        self._signalAssign[signalname] = make_signal_instance(xsignal)
                # add suffix Done to the signal name
        dsignal = signalInfo(self._signalAssign[signalname].doneName,argswhendone)

        self._signalAssign[dsignal.name] = make_signal_instance(dsignal)

        # connect the callback
        if callback != None:
            self._signalAssign[signalname].sig.connect(callback)


    ##############################################
    def dump(self):
        from pprint import pprint
        pprint(self._signalAssign)
    ##############################################
    def init_signal(self):

        # initial _signalAssign
        self._signalAssign = {}

        # the first argument of the call back in the widget that is involve, the userPrefs, the third is the currentgroup
        self.declare_signal(confsig.INIT_FIRST_TIME, self.initFirstTime, confsig.SINGLE_ARG)

        # logging
        self.declare_signal(confsig.LOG_WRITE, self.logwrite, confsig.SINGLE_ARG)

        # for dockwidget
        # option change argument is a list of option starting with the name of the dock as first argument
        self.declare_signal(confsig.OPTION_CHANGE, self.optionChange,confsig.SINGLE_ARG)

        self.declare_signal(confsig.RICH_COLOR_CHANGE,self.richColorChange,confsig.SINGLE_ARG)

        # just a path name
        self.declare_signal(confsig.CHANGE_CURPATH, self.changeCurrentPath,confsig.SINGLE_ARG)

        self.declare_signal(confsig.CHANGE_USERPROFILE, self.changeUserProfile,confsig.SINGLE_ARG)

        # menuContext
        self.declare_signal(confsig.CHANGE_CONTEXT_MENU, self.contextMenuAction,confsig.SINGLE_ARG)

        # selection change
        self.declare_signal(confsig.CURRENTTASK_SIGNAL, self.selectionChanged,confsig.SINGLE_ARG)

        # command
        self.declare_signal(confsig.COMMAND_SIGNAL, self.command_input,confsig.SINGLE_ARG)

    ###
    def request_connect(self,emitter,signalName,canEmit,callerCallback = None):
        """ the main method to register signal"""
        if emitter in [None,""]: return
        assert type(canEmit) == bool
        if not signalName in self._signalAssign:
            raise BaseException("unknown signal Name %s" % signalName)
        if canEmit:
            if not hasattr(emitter,'sig'):
                emitter.sig = dict()

            emitter.sig[signalName] = self._signalAssign[signalName].sig


        if callerCallback != None:
            self._signalAssign[self._signalAssign[signalName].doneName].sig.connect(callerCallback)

        #self.dump()
        return self._signalAssign[signalName].sig
    ###
    def request_disconnect(self,emitter,signalName,canEmit,callerCallback = None):
        if emitter in [None,""]: return
        if not signalName in self._signalAssign:
            raise BaseException("unknown signal Name %s" % signalName)
        if canEmit:
            if not hasattr(emitter,'sig'):
                emitter.sig = dict()

            emitter.sig[signalName] = self._signalAssign[signalName].sig
            #self._signalAssign[signalName].sig.disconnect()
            '''self.disconnect(emitter,
                            self._signalAssign[signalName]["signal"],
                            self._signalAssign[signalName]["methodReceiving"])
            '''

        if callerCallback != None:
            self._signalAssign[self._signalAssign[signalName].doneName].sig.disconnect(callerCallback)

        return self._signalAssign[signalName].sig

    ############ 
    def reemit(self, sigx, args = None):
        signame = sigx.doneName
        self._signalAssign[signame].sig.emit(args)

    ############    
    def initFirstTime(self,msg):
        """ This is function is call to build or rebuild the gui
        """
        msg.setPref(self._prefs)
        msg.setGroup(self._currentGroup)
        msg.setEditor(self)
        self.reemit(self._signalAssign[confsig.INIT_FIRST_TIME.name], msg)

    ############################################################################################
    def optionChange(self,val):
        self.reemit(self._signalAssign[confsig.OPTION_CHANGE.name], val)

    #######################
    def clean(self):
        top = self.get_document_top()
        if top != None:
            self._currentGroup = top
            if hasattr(self._currentGroup,"resetChildren"):
                self._currentGroup.resetChildren()
            if hasattr(self._currentGroup,"resetCache"):
                self._currentGroup.resetCache()

    ###################
    # LOGGING
    ###################
    def logwrite(self,line):

        self.reemit(self._signalAssign[confsig.LOG_WRITE.name],line)

    ##########################
    # base
    def changeCurrentPath(self,apath):
        pref = self._prefs.global_state()
        pref.CurrentPath = apath
        self.reemit(self._signalAssign[confsig.CHANGE_CURPATH.name],apath)

    def contextMenuAction(self,args):
        self.reemit(self._signalAssign[confsig.CHANGE_CONTEXT_MENU.name], args)

    #######################
    def selectionChanged(self,msg):
        msg.setGroup(self._currentGroup)
        ch =  self._currentGroup.getTop().find(msg.getCurrentPath())
        msg.setCurrentNode(ch)
        self.reemit(self._signalAssign[confsig.CURRENTTASK_SIGNAL.name],msg)

    # user
    def changeUserProfile(self,msg):
        self.reemit(self._signalAssign[confsig.CHANGE_USERPROFILE.name],msg)

    # preference
    def richColorChange(self,d):
        self.set_rich_color(d)
        self.reemit(self._signalAssign[confsig.RICH_COLOR_CHANGE.name],d)

    def command_input(self,msg):
        self.reemit(self._signalAssign[confsig.COMMAND_SIGNAL.name],msg)

