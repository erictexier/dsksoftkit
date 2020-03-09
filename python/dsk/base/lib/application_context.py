"""
Serie for namedtuple to store information relative to the user environment
    - AboutInfo
    - ResourcesInfo
    - UserDataInfo
    - SupportInfo
"""


import os
import sys
if sys.version_info[0] >= 3:
    from six import string_types as basestring

from collections import namedtuple, Iterable
from dsk.base.resources import browser_default as initDefault

################################################################################
# About Info
class AboutInfo(namedtuple('aboutInfo', "company year app_name version repo_version doc")):
    __slots__ = ()

def get_about(appName, appModuleInfo):
    about = None
    if appModuleInfo != None:
        repoversion = version = ""
        if hasattr(appModuleInfo,"Version"):
            version = appModuleInfo.Version
        if hasattr(appModuleInfo,"VersionRelease"):
            repoversion = appModuleInfo.VersionRelease

        about = AboutInfo(initDefault.COMPAGNY,
                          initDefault.ANAPP_YEAR,
                          appName,
                          version,
                          repoversion,
                          appModuleInfo.__doc__)
    else:
        about = AboutInfo(initDefault.COMPAGNY,
                          initDefault.ANAPP_YEAR,
                          appName,
                          "unknown_version",
                          "unknown_releaseversion",
                          "no_doc")

    return about

################################################################################
# Resources Info
class ResourcesInfo(namedtuple('resourcesInfo', 'resource_path ui_path icons_path')):
    __slots__ = ()

def get_resources_locations(appModuleInfo = None):
    """ application resource icons and ui file
    """
    if appModuleInfo == None:
        return ResourcesInfo(initDefault.RESOURCEDATA_PATH,
                             initDefault.UIC_PATH,
                             initDefault.ICON_PATH)
    codeinstall = ""
    if hasattr(appModuleInfo, "CodeInstall"):
        codeinstall = appModuleInfo.CodeInstall
    elif hasattr(appModuleInfo, "CODE_INSTALL"):
        codeinstall = appModuleInfo.CODE_INSTALL
    else: # return default browser
        return ResourcesInfo(initDefault.RESOURCEDATA_PATH,
                             initDefault.UIC_PATH,
                             initDefault.ICON_PATH)
    return ResourcesInfo(os.path.join(codeinstall, initDefault.RESOURCES),
                         os.path.join(codeinstall, initDefault.RESOURCES,
                                      initDefault.RESOURCES_UI),
                         os.path.join(codeinstall, initDefault.RESOURCES,
                                      initDefault.RESOURCES_ICONS))

################################################################################
# User Data Info
class UserDataInfo(namedtuple('userfileInfo', 'local_area pref_file log_dir email')):
    __slots__ = ()

def get_user_info(appName,
                  appSubType,
                  baseUserDir,
                  appModuleInfo):
    from dsk.base.utils.userid import UserId

    pref_file = ""
    if appName == "":
        if baseUserDir == "":
            import tempfile
            baseUserDir = tempfile.gettempdir()
    else:
        baseUserDir = os.path.join(baseUserDir,".%s" % appName)

    if appSubType == "":
        pref_file = os.path.join(baseUserDir,initDefault.PREF_FILE)
    else:
        pref_file = os.path.join(baseUserDir,initDefault.PREF_FILE_APP % appSubType)

    log_dir = os.path.join(baseUserDir,"log")
    useremail = "%s@%s" % (UserId.current_user(), initDefault.EMAIL_SUFFIX)
    if appModuleInfo != None and hasattr(appModuleInfo,'aliasname'):
        useremail = "%s@%s" % (appModuleInfo, initDefault.EMAIL_SUFFIX)
    return UserDataInfo(baseUserDir, pref_file, log_dir, useremail)


################################################################################
# Support Info
class SupportInfo(namedtuple('supportInfo', 'quickstart doc email_list bug hostname')):
    __slots__ = ()

def get_support(appName,
                appSubType,
                appModuleInfo):

    from dsk.base.utils.platform_utils import uname

    autoremail = [initDefault.EMAIL_BUG]
    if appModuleInfo != None and hasattr(appModuleInfo,"autor"):
        x = appModuleInfo.autor
        autoremail = ["%s@%s" % (x,initDefault.EMAIL_SUFFIX)]
    if appModuleInfo != None and hasattr(appModuleInfo,"supportList"):
        alist = appModuleInfo.supportList
        if isinstance(alist, basestring):
            if alist.endswith(initDefault.EMAIL_SUFFIX):
                autoremail.append(alist)
            else:
                autoremail.append("%s@%s" % (alist, initDefault.EMAIL_SUFFIX))
        elif isinstance(alist, Iterable):
            for i in alist:
                if isinstance(i, basestring):
                    if i.endswith(initDefault.EMAIL_SUFFIX):
                        autoremail.append(i)
                    else:
                        autoremail.append("%s@%s" % (i, initDefault.EMAIL_SUFFIX))
    quickStart = initDefault.QUICKSTART
    adoc = initDefault.URLDOC

    if appModuleInfo != None:
        quickStart = appModuleInfo.__doc__
        adoc = appModuleInfo.__url__
    bugfile = initDefault.BUG_REPORT
    return SupportInfo(quickStart, adoc, autoremail, bugfile, uname)

