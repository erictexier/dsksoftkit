"""helper user and application local data
"""

import os
import time
import json
import traceback
from dsk.base.utils.disk_utils import DiskUtils
from dsk.base.utils.msg_utils import MsgUtils
from dsk.base.resources import browser_default as initDefault

from dsk.base.lib.app_pref_data import AppPrefData

from dsk.base.lib.application_context import get_about, get_resources_locations
from dsk.base.lib.application_context import get_user_info, get_support


class UserProfile(object):
    """User preferences and resource
    """
    __LOGCOUNT  = 0

    def __init__(self,**options):
        super(UserProfile,self).__init__()

        self.reset()

        # check for cfd as to see if this is a debug mode
        configdata = options.get('cfd',None) if options else None
        if configdata:
            self.debug = configdata.debug
        self._sgtkutils = None
        '''
        if configdata != None:
            try:
                self._sgtkutils = configdata.sgtkutil
            except:
                pass
        if self._sgtkutils and self.debug == True:
            self._sgtkutils.print_info(self.debug)
        '''
        self.appName = options.get('appName', '')
        self.subType = options.get('subType', '')
        rootpath = options.get('userBase', initDefault.HOME_PREF)
        initmodule = options.get("initModule",None)

        self.options = options
        # check if initmodule carry the missing key
        if self.appName == "":
            if hasattr(initmodule,'appName'):
                self.appName = initmodule.appName

        if self.subType == "":
            if hasattr(initmodule,'subType'):
                self.subType = initmodule.subType
        if rootpath == "":
            if hasattr(initmodule,'userBase'):
                rootpath = initmodule.userBase

        assert isinstance(self.appName, str)
        assert isinstance(self.subType, str)
        assert isinstance(rootpath, str) and os.path.isdir(rootpath)

        #MsgUtils.info("init homeUser %r" % self.appName)

        self._about = get_about(self.appName, initmodule)
        self._resource = get_resources_locations(initmodule)
        self._userInfo = get_user_info(self.appName,
                                       self.subType,
                                       rootpath,
                                       initmodule)
        self.rootpath = self._userInfo.local_area

        self._support = get_support(self.appName,
                                    self.subType,
                                    initmodule)

        if self.appName == "":
            MsgUtils.info("no pref are saved")
            return

        # build the user are if possible
        self._init_root_path()

    def get_sgtk(self):
        return self._sgtkutils

    def get_about(self):
        return self._about

    def get_support(self):
        return self._support

    def reset(self):
        self.appName = ""
        self.subType = ""
        self._about = None
        self._resource = None
        self._userInfo = None
        self._support = None

        self.valid_to_save = False
        self.rootpath = ""
        self._prefs = None
        self._logF = ""
        self._logger = None

    def _init_root_path(self):
        if self._userInfo == None:
            return False
        toCheck = [self._userInfo.local_area,
                   self._userInfo.log_dir]
        checkLayout = False
        for d in toCheck:
            if not DiskUtils.is_dir_exist(d):
                checkLayout = True
                MsgUtils.warning("%r is needed, create..." % d)
                if DiskUtils.create_path_rec(d) == False:
                    MsgUtils.error("can't create %r" % d)
                else:
                    MsgUtils.info("%r created" % d)

                #only on creation,copy if exist the defaultLayoutFile from
                # from the module
        if checkLayout:
            import shutil
            fromlayout = os.path.join(self._resource.resource_path,
                                      initDefault.DEFAULT_LAYOUT_ROOT)
            tolayout = os.path.join(self._userInfo.local_area,
                                    initDefault.DEFAULT_LAYOUT_ROOT)
            fromlayout += ".lyt"
            tolayout += ".lyt"
            if os.path.exists(fromlayout) and not os.path.exists(tolayout):
                shutil.copyfile(fromlayout, tolayout)
                MsgUtils.info("found a defaut layout file %s" % fromlayout)
        self.valid_to_save = self.is_persistant()


    def get_root_path(self):
        if self.valid_to_save:
            return self.rootpath
        return ""

    def is_persistant(self):
        return DiskUtils.is_dir_exist(self.rootpath) and self.appName != ""


    ##################
    def get_pref_file(self):
        import tempfile
        if self.valid_to_save:
            return self._userInfo.pref_file
        aname = "defaultpref.txt"
        return os.path.join(tempfile.gettempdir(),aname)

    # base preference management
    def make_preference(self):
        #MsgUtils.info("in make preference %s " % (self.appName))
        self._prefs = AppPrefData()
        self._prefs.setName(self.appName if self.appName != "" else "default")
        return self._prefs

    def get_preference(self):
        return self._prefs

    def save_preference(self):
        from dsk.base.utils import platform_utils
        if self._prefs == None:
            self.make_preference()
        filePref = self.get_pref_file()
        if  filePref == "":
            return False

        self._prefs['globalPreference'].Info = "%s:%s" % (platform_utils.getOs(),
                                                          time.ctime())
        self._prefs.SaveAsXml(filePref)
        return True

    def load_preference(self):
        if self._prefs == None:
            self.make_preference()
        filePref = self.get_pref_file()
        if filePref == "":
            return self._prefs
        if DiskUtils.is_file_exist(filePref):
            #print "loading preferences",filePref
            self._prefs = self._prefs.ReadAsXml(filePref)[0]
        return self._prefs


    #############  keep the most recent file
    def get_recent_file(self):
        if self.valid_to_save:
            return os.path.join(self.rootpath,initDefault.RECENT_FILE_SAVE)
        return ""

    #############  layout dir
    def get_layout_dir(self):
        if self.valid_to_save:
            return self.rootpath
        return ""

    def get_layout_names(self):
        """ return all layout file found in rootpath """
        import glob
        adir = self.get_layout_dir()
        if adir == "":
            return []
        ally = glob.glob(os.path.join(adir,"*.lyt"))
        return [os.path.split(x)[1][:-4] for x in ally]

    def layout_file(self,name):
        adir = self.get_layout_dir()
        if adir == "":
            return ""
        return os.path.join(self.get_layout_dir(),"%s.lyt" % name)

    def send_report(self,**args):
        import socket
        if self._support == None:
            MsgUtils.error("no technical support for this app")
            return
        email_list = self._support.email_list
        from dsk.base.utils.userid import UserId
        from dsk.base.utils import email_utils

        emailAs = UserId.current_user()

        subject = "%s version:%s repo_version%s\n" % (self.appName,
                                                      self._about.version,
                                                      self._about.repo_version)

        args.update(self.options)
        # collect some known key
        rtd = args.get("rtd",None)
        cfd = args.get("cfd",None)
        #currentGroup = args.get('currentGroup',None )

        body = list()
        hostname = socket.gethostname()
        body.append("hostname %s" % hostname)
        #         log_term = "/tmp/%s_desktop.log" % hostname
        #         try:
        #             body.extend(open(log_term,"r").readlines())
        #         except Exception,e:
        #             MsgUtils.error(log_term + ":" + str(e))
        #             pass
        try:
            body.append(traceback.format_exc())
            if rtd != None:
                d = rtd.get_as_dict()
                body.append("RTD:")
                body.append(json.dumps(d, indent=4))
            if cfd != None:
                d = cfd.get_as_dict()
                body.append("CFD:")
                body.append(json.dumps(d,indent=4))
        except:
            body.append("couldn't serialized cfd and rtd")

        document = args.get("document",list())
        for d in document:
            body.append(d)

        body.append("Environment:")
        envir = dict()
        envir.update(os.environ)

        body.append(json.dumps(envir, indent=4))


        logFile = self.get_log_file()
        if not os.path.isfile(logFile):
            logFile = ""
        body = "\n".join(body)
        try:
            email_utils.send_mail(emailAs,
                                 email_list,
                                 subject,
                                 body,
                                 [logFile])
            return True
        except: # worst let try to save it in the log
            MsgUtils.error(body)
        return False
    #######################
    # the log view
    #######################
    def get_log_file(self):
        return self._logF

    def start_log(self,editor):

        from dsk.base.utils.log_utils import LogUtils as LogBase

        if self._logger != None:
            MsgUtils.msg("doLog is on")
            return
        MsgUtils.msg("doLog is on, print statement after this")
        MsgUtils.msg("will be redirect to the log area")

        logfile = os.path.join(self._userInfo.log_dir,self.appName)
        MsgUtils.msg("log location %r" % logfile)
        self._logger = LogBase()

        self._logF = "%s_%s.log" % (logfile,os.getpid())
        logTag = self.appName + str(self.__LOGCOUNT)
        #self._logger.startLogFileRotate(logTag,self._logF,5,self)
        self._logger.startLogFile(logTag,self._logF,editor)
        self._logger.info("STARTING LOG %r AT: %s" % (self._logF,time.ctime()))
        self.__LOGCOUNT += 1

        self._prefs['globalPreference']['DoLog'] = True

    #######################
    def end_log(self):
        if self._logger != None:
            self._logger.info("ENDLOG LOG AT: %s" % time.ctime())
            self._logger.end_log()
        self._logger = None
        self._logF = ""
        MsgUtils.msg("doLog is off, print statement after this should be in the console")
        self._prefs['globalPreference']['DoLog'] = False

if __name__ == "__main__":
    atest = ['testapp',""]
    for t in atest:
        a = UserProfile(appName=t)
        print("prefile defaut %r" % a.get_pref_file())
    a = UserProfile(appName="zzz",subapp="tile")
    print("prefile defaut %r" % a.get_pref_file())
    print("recentfile %r" % a.get_recent_file())
    print(a.save_preference())