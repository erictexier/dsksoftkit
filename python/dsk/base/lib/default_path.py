import os
import sys


from dsk.base.resources import browser_default
from dsk.base.utils.disk_utils import DiskUtils
from dsk.base.utils.msg_utils import MsgUtils

class DefaultPath(object):
    """ utility to manage the needed path
    """
    __slots__ = ()

    __REQUIRED__ =  [ browser_default.CODE_INSTALL,
                      browser_default.UIC_PATH,
                      browser_default.ICON_PATH]

    __SELF_CREATED__ =  []

    __ADMIN_CREATED__ = []

    _browserIconPath = ""

    ##################
    @classmethod
    def add_required(cls, apath):
        if apath not in cls.__REQUIRED__:
            cls.__REQUIRED__.append(apath)

    ##################
    @classmethod
    def add_selfcreated(cls, apath):
        if apath not in cls.__SELF_CREATED__:
            cls.__SELF_CREATE__.append(apath)
    ##################
    @classmethod
    def add_admin(cls, apath):
        if apath not in cls.__ADMIN_CREATED__:
            cls.__ADMIN_CREATE__.append(apath)

    ##################
    @staticmethod
    def getDataBasePath():
        """ where the database is
        """
        if DiskUtils.is_dir_exist(browser_default.DATABASE_PATH):
            return browser_default.DATABASE_PATH
        return None

    ##################
    @staticmethod
    def getBaseInstallPath():
        """ where the code py file resided
        """
        if DiskUtils.is_dir_exist(browser_default.CODE_INSTALL):
            return browser_default.CODE_INSTALL
        return None

    ##################
    @staticmethod
    def checkBasicPath():
        # required will exist if not found
        for path in DefaultPath.__REQUIRED__:
            if not DiskUtils.is_dir_exist(path):
                MsgUtils.error("%r (REQUIRED)" % path)
                sys.exit(1)

        for path in DefaultPath.__SELF_CREATED__:
            if not DiskUtils.is_dir_exist(path):
                MsgUtils.warning("%r needed, creating..." % path)
                if DiskUtils.create_path_rec(path) == False:
                    MsgUtils.error("can't create %r" % path)
                    sys.exit(1)
        return True

    ###################
    @staticmethod    
    def checkAdminPath():
        for path in DefaultPath.__ADMIN_CREATED__:
            if not DiskUtils.is_dir_exist(path):
                MsgUtils.warning("%r needed, creating" % path)
                if DiskUtils.create_path(path) == False:
                    MsgUtils.error("can't create %r" % path)
                    sys.exit(1)
        return True


    @staticmethod
    def getDefaultLayoutFile():
        return browser_default.DEFAULT_LAYOUT_FILE


    ###############
    @staticmethod
    def getUicPath():
        return browser_default.UIC_PATH

    @staticmethod
    def getUiFile(name):
        return os.path.join(DefaultPath.getUicPath(),"%s.ui" % name)
    ###############
    ##############
    @staticmethod
    def getIconPath():
        return browser_default.ICON_PATH

    ##############
    @staticmethod
    def getIconFile(name):
        return os.path.join(DefaultPath.getIconPath(),"%s" % name)


    @staticmethod
    def getBrowserIconPath():
        if DefaultPath._browserIconPath == "":
            DefaultPath._browserIconPath = os.path.join(browser_default.RESOURCEDATA_PATH,"Icons")
        return DefaultPath._browserIconPath

    ###############
    @staticmethod
    def getBrowserIconFile(aname):
        return os.path.join(DefaultPath.getBrowserIconPath(),aname)






#END
