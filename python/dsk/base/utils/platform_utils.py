import os
import sys
import platform
import re
from datetime import datetime
from dsk.base.lib.log_manager import LogManager
from dsk.base.utils.filesystem_utils import FileSystemUtils

from dsk.base.resources.dsk_errors import DskError, DirmapError
from dsk.base.resources.dsk_errors import DskErrorPython2or3Only

from dsk.base.path_helper import template
from dsk.base.resources.dsk_constants import ROOT_CONFIG_DIR
from dsk.base.resources.dsk_constants import NAME_CONFIG_DIR
from dsk.base.resources.dsk_constants import ENVI_TEMPLATE_NAME
from dsk.base.resources.dsk_constants import ENVI_DIRMAP_NAME
from dskenv.dskenv_constants import DSK_MOUNTED_ROOT,DSK_DEV_AREA

DEFAULT_DIRMAP_FILE = os.path.join(os.sep,
                                   DSK_MOUNTED_ROOT,
                                   DSK_DEV_AREA,
                                   ROOT_CONFIG_DIR,
                                   NAME_CONFIG_DIR,
                                   ENVI_TEMPLATE_NAME,
                                   ENVI_DIRMAP_NAME)


# python3 support
if sys.version_info[0] == 2:
    from urlparse import urlparse
elif sys.version_info[0] == 3:
    # python3
    from urllib.parse import urlparse
else:
    raise DskErrorPython2or3Only("Need Python 2 or 3")

from collections import namedtuple
class LocationDefault(namedtuple('locationDefault', 
                                 "cache_dir_def, log_file_def, pref_dir_def,  data_dir_def,"
                                 "platform, namespace, is_user")):
    __slots__ = ()


class LocationWithUrl(namedtuple('location_with_Url', 
                                 "locationdefault, authenfile, baseUrl")):
    __slots__ = ()



log = LogManager.get_logger(__name__)

from os.path import expanduser

def get_home_user():
    ex = expanduser("~")
    return ex

def uname():
    return platform.uname()

def getOs():

    pos = platform.system()
    if pos == 'Microsoft':
        if sys.platform == 'win32':
            return 'Windows'
    # Linux Mac default
    return pos

class LocalFileStorageManager(object):
    """
    Class that encapsulates logic for resolving local storage paths.

    Toolkit needs to store cache data, logs and other items at runtime.
    Some of this data is global, other is per site or per configuration.

    This class provides a consistent and centralized interface for resolving
    such paths and also handles compatibility across generations of path
    standards if and when these change between releases.

    .. note:: All paths returned by this class are local to the currently running
              user and typically private or with limited access settings for other users.

              If the current user's home directory is not an appropriate location to store
              your user files, you can use the ``DSK_HOME`` environment variable to
              override the root location of the files. In that case, the location for the
              user files on each platform will be:

              - Logging:     ``$DSK_HOME/logs``
              - Cache:       ``$DSK_HOME``
              - Persistent:  ``$DSK_HOME/data``
              - Preferences: ``$DSK_HOME/preferences``


    :constant LOGGING:     Indicates a path suitable for storing logs, useful for debugging
    :constant CACHE:       Indicates a path suitable for storing cache data that can be deleted
                           without any loss of functionality or state.
    :constant PERSISTENT:  Indicates a path suitable for storing data that needs
                           to be retained between sessions.
    :constant PREFERENCES: Indicates a path that suitable for storing settings files and preferences.
    """

    # supported types of paths
    (LOGGING, CACHE, PERSISTENT, PREFERENCES) = range(4)

    PSITE = re.compile(r"\.[\d\w]*\.com")

    @classmethod
    def base_application_location(cls,
                                  namespace,
                                  logfile = "",
                                  alternative=None,
                                  is_user=True):
        """
        Returns the platform specific location for CacheDir/Logging Name/Preferences/Persistent
        name tag
        :returns: LocationDefault
        """
        assert namespace != ""
        log_file_def = pref_dir_def = cache_dir_def = data_dir_def = ""

        alt_name = ""
        if alternative and alternative in os.environ:
            alt_name = os.path.expandvars(os.environ.get(alternative,""))
            if alt_name in None:
                alt_name = ""
            alt_name = alt_name.strip()
        if logfile == '':
            logfile = datetime.now().strftime("%Y%m%d-%H%M%S")
        logext = '.log'
        logfilename = logfile.replace(logext,'')
        logfilename = logfilename+logext
        platform = sys.platform 
        if is_user or alt_name == '':
            alt_name = os.path.expanduser("~")
            if platform == "darwin":
                cache_dir_def = os.path.join(alt_name,"Library", "Caches", namespace)
                log_file_def = os.path.join(alt_name, "Library", "Logs", namespace, logfilename)
                pref_dir_def = os.path.join(alt_name, "Library", "Preferences", namespace)
                data_dir_def = os.path.join(alt_name, "Library", "Application Support",namespace)

            elif platform == "win32":
                app_data = os.environ.get("APPDATA", "APPDATA_NOT_SET")
                cache_dir_def = os.path.join(app_data, namespace)
                log_file_def = os.path.join(app_data, namespace, "Logs",logfilename)
                pref_dir_def = os.path.join(app_data, namespace, "Preferences")
                data_dir_def = os.path.join(app_data, namespace, "Data")

            elif platform == 'linux':
                cache_dir_def = os.path.join(alt_name, ".%s" %  namespace)
                log_file_def = os.path.join(alt_name, ".%s" % namespace, "logs",logfilename)
                pref_dir_def = os.path.join(alt_name, ".%s" % namespace, "preferences")
                data_dir_def = os.path.join(alt_name, ".%s" % namespace, "data")
            else:
                raise ValueError("Unknown platform: %s" % platform)

        elif alt_name != "":
            cache_dir_def = alt_name
            log_file_def = os.path.join(alt_name, "logs", namespace, logfilename)
            pref_dir_def = os.path.join(alt_name, "preferences")
            data_dir_def = os.path.join(alt_name, "data")
        else:
            raise ValueError("you should set is_user to true or a alternative variable name with path content")

        return LocationDefault(cache_dir_def,
                               log_file_def,
                               pref_dir_def,
                               data_dir_def,
                               platform,
                               namespace,
                               is_user)


    @classmethod
    def ensure_exist(cls, location_def, which):
        assert isinstance(location_def, LocationDefault)
        try:
            if which == cls.CACHE:
                FileSystemUtils.ensure_folder_exists(location_def.cache_dir_def)
                return True
            elif which == cls.PREFERENCES:
                FileSystemUtils.ensure_folder_exists(location_def.pref_dir_def)
                return True
            elif which == cls.PERSISTENT:
                FileSystemUtils.ensure_folder_exists(location_def.data_dir_def)
                return True
            elif which == cls.LOGGING:
                return os.path.exists(location_def.log_file_def)
        except:
            return False

    @classmethod
    def get_global_root(cls, path_type, generation):
        raise("not valid function get_global_root")


    @classmethod
    def get_site_root_name(cls, hostname):
        """
        Returns root name of site

        :param hostname:  hostname as string, e.g. 'https://foo.blah.com'
        :param path_type: Type of path to return. One of ``LocalFileStorageManager.LOGGING``,
                          ``LocalFileStorageManager.CACHE``, ``LocalFileStorageManager.PERSISTENT``, where
                          logging is a path where log- and debug related data should be stored,
                          cache is a location intended for cache data, e.g. data that can be deleted
                          without affecting the state of execution, and persistent is a location intended
                          for data that is meant to be persist. This includes things like settings and
                          preferences.

        :return: Path as string
        """
        if hostname is None:
            raise DskError("Cannot compute path"
                           " for local site specific storage - no dsk hostname specified!")

        # get site only; https://www.FOO.com:8080 -> www.foo.com
        base_url = urlparse(hostname).netloc.split(":")[0].lower()
        res = cls.PSITE.search(base_url)
        if res:
            base_url = base_url.replace(res.group(0), "")
        return base_url

    @classmethod
    def get_cache_site_root(cls, location, base_url):
        return LocationWithUrl(location,
                               os.path.join(location.cache_dir_def),
                               base_url)
    @classmethod
    def get_preferences_site_root(cls, location, base_url):
        return os.path.join(location.preference_dir_def, base_url)

class TextEditorPlatform(object):
    editors = []
    diffscmd = []

    env_editor = os.environ.get('EDITOR','')

    # get the setting
    system = sys.platform

    # build the commands for opening the folder on the various OS's
    if system.startswith("linux"):
        if env_editor == '':
            editors = ["xdg-open"]
        else:
            editors = [env_editor]
        diffscmd = ['xdiff','meld']
    elif system == "darwin":
        if env_editor == '':
            editors = ["open"]
        else:
            editors = [env_editor]
        diffscmd = ['opendiff','meld']
    elif system == "win32":
        if env_editor == '':
            editors = ["cmd.exe", "/C", "start"]
        else:
            editors = [env_editor]
        diffscmd = ['opendiff','meld']


def _read_dirmap():
    """
    Load the dirmap from the dirmap file.
    """
    import yaml
    dirmap_file = os.environ.get("DSK_DIRMAP_FILE", False)

    if not dirmap_file:
        dirmap_file = DEFAULT_DIRMAP_FILE

    if not os.path.exists(dirmap_file):
        raise DirmapError("Unable to find dirmap file: '%s'" % dirmap_file)

    with open(dirmap_file, "r") as dirmap_file:
        dirmaps_data = yaml.load(dirmap_file.read())

    dirmaps = dirmaps_data["dirmaps"]
    return dirmaps

def get_dirmaps():
    """
    """
    return _read_dirmap()

def get_link_remap(path):
    """
    the opposite of dereferencing a symlink
    @param path the dereferenced path
    @return the un-dereferenced path
    """
    if os.name != 'posix':
        return path

    link_dict = {}
    root_dir = os.environ['NCO_STUDIO_PATH']
    links = os.listdir(root_dir)
    for link in links:
        if not os.path.islink(os.path.join(root_dir,link)):
            continue

        target = os.readlink(os.path.join(root_dir,link))
        link_dict[target] = os.path.join(root_dir,link)

    for key in link_dict.keys():
        if path.startswith(key+'/'):
            return link_dict[key] + path[len(key):]

    return path

def dirmap(path, os_name=None):
    """
    Find the mapping for a path. This will run through all directory mappings
    looking for a path match. If found, returns the remapped path.
    @param path The path to remap
    @param os_name If specified, remap the path to the specified OS. If None, the
    current OS is used. Valid values are "linux" and "windows"
    @return Remapped path string.
    """
    curr_platform = platform.system().lower()

    isexists = os.path.exists(path)
    if (os_name is None or os_name == curr_platform ) and isexists:
        return path

    if os_name is None:
        os_name = curr_platform

    dirmaps = _read_dirmap()

    for dirmap in dirmaps:
        for dirmap_platform in dirmap:
            if path.startswith(dirmap[dirmap_platform]):
                repl = dirmap[os_name]
                return path.replace(dirmap[dirmap_platform], repl)

    raise DirmapError("Unable to find dirmap for %spath: '%s'" %(("non-existant ","")[isexists], path))





def conform_slashes(path):
    """
    """
    conformed_path = re.sub(r"[\\|/]+", "/", os.path.normpath(path))
    return conformed_path

def conform_path(path, os_name=None):
    """
    Replace all occurrences of backslashes with a forward slash. This will also normalize the
    path, and collapses redundant separatores.
    @param path The path to conform
    """

    #legacy support of os.name being used instead of platform
    if os_name == "nt":
        os_name = "windows"

    elif os_name == "posix":
        os_name = "linux"

    conformed_path = conform_slashes(path)
    conformed_path = os.path.expandvars(conformed_path)
    conformed_path = dirmap.dirmap(conformed_path, os_name=os_name)
    return conformed_path


