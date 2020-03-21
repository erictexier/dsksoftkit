# ########### INFO DEVELOPMENT ######
ANAPP_YEAR = "2016-2???"
COMPAGNY = "Eclectic Studio Net"
COPYRIGHT = "Copyright (c) %s" % ANAPP_YEAR
APPNAME = "Eclectic"
ANAPP_VERSION = "0.0.0"
ANAPP_SVN = "beta"
AUTOR = "erictexier"

import os
import tempfile
#from os.path import expanduser
from dsk.base.utils.platform_utils import get_home_user
import dsk.base
CODE_INSTALL = dsk.base.CodeInstall
# for my mac
if CODE_INSTALL.find('eric') != -1:
    AUTOR = "eric"

# ######################## LOG
DO_LOG = True

# ######################## SPLASH
DO_SPLASH = False

# ######################### Source code level
RESOURCES = "resources"
RESOURCES_UI = "ui"
RESOURCES_ICONS = "icons"
RESOURCEDATA_PATH = os.path.join(CODE_INSTALL, RESOURCES)
ICON_PATH = os.path.join(CODE_INSTALL, RESOURCES, RESOURCES_ICONS)

# where the ui file are
UIC_PATH = os.path.join(CODE_INSTALL, RESOURCES, RESOURCES_UI)

DEFAULT_LAYOUT_ROOT = "defaultLayout"
DEFAULT_LAYOUT_FILE = os.path.join(RESOURCEDATA_PATH,
                                   DEFAULT_LAYOUT_ROOT+".lyt")

# ######################## Email

SERVER_EMAIL_NAME = 'smtp.mail.yahoo.com'
EMAIL_SUFFIX = "@%s" % "eclecticstudionet.com"
if AUTOR == 'eric':
    EMAIL_BUG = "erictexier@eclecticstudionet.com"
else:
    EMAIL_BUG = "%s%s" % (AUTOR,EMAIL_SUFFIX)

########################## Bug Report ( file to save stuff....)
home = get_home_user() #expanduser("~")
users = os.sep.join(os.path.split(home)[:-1])
autordir = os.path.join(users,AUTOR)

if not os.path.isdir(autordir):
    autordir = tempfile.gettempdir()
BUG_REPORT = os.path.join(autordir,"bug%s.txt" % APPNAME)
assert os.path.isdir(autordir)

# ######################### WEB PAGE HELP
QUICKSTART = dsk.base.__doc__


""" for now it's a global doc under show_tools/python """
#topDoc = os.path.join(os.path.split(CODE_INSTALL)[:-1])
URLDOC = "file://%s/doc/src/_build/html/index.html" % dsk.base.Base

# ######################### USER LOCAL AREA
DB_NAME = "." + APPNAME
HOME_PREF = home
# Define some user dir to save preference and log
## a place to save the preference
DATABASE_PATH = os.path.join(HOME_PREF,DB_NAME)
## a place to save the layout
PREF_LAYOUTDIR = DATABASE_PATH
## a place to save the log
LOG_PATH = os.path.join(DATABASE_PATH,'logs')

# ######################### NAME TOOLS ACCESS
TOOLS_LIST = ["logWidget"]
MAXCUR = 4000

# ######################## PATH NAME CONVENTION
PREF_FILE = "preferences.xml"
PREF_FILE_APP = "%spreference.xml"
RECENT_FILE_SAVE = "recentFileSave.txt"












