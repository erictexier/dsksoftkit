from dskenv import dskenv_constants

ROOT_NAME = "Dsk"

#  KEY TO query alternative main location in ENVIRONMENT
ROOT_NAME_ENV = "DSK_ENV"

# root logger for all of tk. This needs to match the top level
ROOT_LOGGER_NAME = "dsk"

## Envi config top node for configuration ROOT_CONFIG/NAME_CONFIG
ROOT_CONFIG_DIR = dskenv_constants.DSK_CONFIGURATION_FOLDER# KEY FOR MAIN APP
NAME_CONFIG_DIR = dskenv_constants.DSK_ENVI_FOLDER
NAME_PROJECT_CONFIG_DIR = 'projects'
TEMPLATE_NAME_FOR_PROJECT = '%s_info.yml'
NAME_DEFAULT_PROJECT = 'dev_show'

# subdirectory 
ENVI_TEMPLATE_NAME = "pconfig"
ENVI_NAMING_CORE = "core"

# the storage name that is treated to be the primary storage for dsk
PRIMARY_STORAGE_NAME = "primary"

# hook that is executed before a publish is registered in sg.
PUBLISH_HOOK_NAME = "before_register_publish"

# valid characters for a template key name
TEMPLATE_KEY_NAME_REGEX = r"[a-zA-Z_ 0-9\.]+"

# a human readable explanation of the above. For error messages.
VALID_TEMPLATE_KEY_NAME_DESC = "letters, numbers, underscore, space and period"

# the key sections in a template file
TEMPLATE_SECTIONS = ["keys", "paths", "strings"]

# the path section in a templates file
TEMPLATE_PATH_SECTION = "paths"

# the string section in a templates file
TEMPLATE_STRING_SECTION = "strings"

# the file that defines which storages a configuration requires
STORAGE_ROOTS_FILE = "roots.yml"

# the name of the file that holds the templates.yml config
CONTENT_TEMPLATES_FILE = "templates.yml"

# for multiple root support (need to integrated more)
ENVI_DIRMAP_NAME = "dirmap.yml"

# the name of the include section in env and template files
SINGLE_INCLUDE_SECTION = "include"

# the name of the includes section in env and template files
MULTI_INCLUDE_SECTION = "includes"

# the name of the primary pipeline configuration
PRIMARY_PIPELINE_CONFIG_NAME = "Primary"

# hook that is executed whenever a cache location should be determined
CACHE_LOCATION_HOOK_NAME = "cache_location"

# log channel to used for function timings
PROFILING_LOG_CHANNEL = "dsk.stopwatch"

# environment variable that if set, enables debug logging in the engine
DEBUG_LOGGING_ENV_VAR = "DSK_DEBUG"

# studio level core hook file name for computing the default name of a project
STUDIO_HOOK_PROJECT_NAME = "project_name.py"

# tk instance cache of the shotgun schema
SHOTGUN_SCHEMA_CACHE_KEY = "shotgun_schema"

# tk instance cache of sg local storages
SHOTGUN_LOCAL_STORAGES_CACHE_KEY = "shotgun_local_storages"

# hook to get current login
CURRENT_LOGIN_HOOK_NAME = "get_current_login"

# dsk authentification file
SESSION_CACHE_FILE_NAME = "authentication.yml"
