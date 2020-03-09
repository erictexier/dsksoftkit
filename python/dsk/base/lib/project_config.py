'''
Module to parse the show settings stored in a yaml files
The yaml filenames match the DSK_PROJECT under:
$ config_folder/projects/DSK_PROJECT/site_info.yml

Usage:
import project_config
project_config.get('film:fps') # Note: 'DSK_PROJECT' need to be set.
project_config.show('ashowname').get('film:fps') # else you can specify explicitly
project_config.get('RV:?platform') # for platform specific can use wild card, ?platform,
'''

import os
import copy
import re
import yaml

from dsk.base.lib.log_manager import LogManager
log = LogManager.get_logger(__name__)

from dskenv import dskenv_constants as DK
from dsk.base.resources import dsk_constants as DSK
DSK_PROJECT_CONF_BASE = os.path.join(os.sep,
                                     DK.DSK_MOUNTED_ROOT,
                                     DK.DSK_DEV_AREA,
                                     DK.DSK_CONFIGURATION_FOLDER,
                                     DSK.NAME_PROJECT_CONFIG_DIR)


_cache_show_config = {}

def current_show():
    show = os.environ.get('DSK_PROJECT', DSK.NAME_DEFAULT_PROJECT)
    if not show:
        raise KeyError, "The project has not been set"
    return show

def current_site():
    studio = os.environ.get('DSK_LOCATION','current')
    if not studio:
        raise KeyError, "The site has not been set"
    return studio

def show(show_name=None, site=None):
    '''
    Retrieve the show config session
    '''
    if show_name == None:
        show_name = current_show()
    if site == None:
        site = current_site()

    global _cache_show_config

    
    yaml_path = '%s/show_yaml/%s_%s.yml' %(os.path.split(os.path.split(__file__)[0])[0], show_name, studio)
    yaml_path = os.path.join(DSK_PROJECT_CONF_BASE,
                             show_name,
                             DSK.TEMPLATE_NAME_FOR_PROJECT % show_name)
    # parse and cache the show settings into a config session
    cachekey = (show_name, studio)
    if cachekey not in _cache_show_config: # config not yet cached.
        if os.path.isfile(yaml_path):
            log.debug('Parsing config for show "%s" from yaml path %r' % (show_name, yaml_path))
            _cache_show_config[cachekey] = ProjectConfig(yaml_path)

    # return the config session
    if cachekey in _cache_show_config:
        return _cache_show_config[cachekey]

    raise KeyError, "There are no show configuration for project %s at %s. Expected %s" % (show_name, studio, yaml_path)

def get(setting_name, default=None, expandpath=False, studio=None):
    '''
    Retreive the a particular settings, ex: the fps.
    @param setting_name name of a single setting
    @param expandpath bool expands environment variables if true
    @return the setting value
    '''
    return show(current_show(), studio).get(setting_name, default=default, expandpath=expandpath)

def get_container(key,
                  default=None,
                  expandpath=False,
                  studio=None):
    return show(current_show(), studio).get_container(key, default=default)

def resolve_show_dir_branch(branch_tag, resolve_branch_hash):
    '''
    Given the branch tag, and resolve path token hash return the resolved directory path
    '''
    if 'project' not in resolve_branch_hash: resolve_branch_hash['project'] = current_show()
    if 'prod_dir_type' not in resolve_branch_hash: resolve_branch_hash['prod_dir_type'] = 'publish'
    if 'artist' not in resolve_branch_hash: resolve_branch_hash['artist'] = 'common'
    from tbe_core.utils.shot_dir_setup import _resolve_path_from_template

    branch_template = show(current_show()).get_show_dir_branch(branch_tag)
    branch_tokens = branch_template.split(':')

    # if it's publish, then no need for artist:
    resolve_tokens =  _resolve_path_from_template( branch_tokens, resolve_branch_hash )
    return get_show_dir_root() + '/' + ( '/'.join (resolve_tokens))

def get_show_dir_branch(branch_tag, create_branch=False, resolve_branch_hash=None):
    '''
    Convenience wrapper around _Config.get_show_dir_branch

    ex:     get_show_dir_branch(branch_tag="branch_asset_root")
            > '?project:?prod_dir_type:assets'
    '''
    if resolve_branch_hash is None:
        resolve_branch_hash = {}

    return show(current_show()).get_show_dir_branch(branch_tag,create_branch,resolve_branch_hash)


def tokenize_shot_code(shot_code):
    # get show_pattern match from show.yaml
    re_pattern_match = re.compile(show(current_show()).get('sequence_code_pattern'))
    
    # pattern match shot code
    pattern_match = re_pattern_match.findall(shot_code)
    
    # if pattern match not empty list return shot
    if pattern_match != []:
        token_list = pattern_match[0]
    else:
        token_list = None

    return token_list

def tokenize_clip_name(clip_name):
    # get show_pattern match from show.yaml
    re_pattern_match = re.compile(show(current_show()).get('clip_name_pattern'))
    
    # pattern match shot code
    pattern_match = re_pattern_match.findall(clip_name)
    
    # if pattern match not empty list return shot
    if pattern_match != []:
        token_list = pattern_match[0]
    else:
        token_list = None
    return token_list    

def get_sequence(shot_code):
    token_list = tokenize_shot_code(shot_code)
    if token_list != None:
         sequence = token_list[1]
    else:
        sequence = None
    return sequence
    
def get_shot(shot_code):
    token_list = tokenize_shot_code(shot_code)
    if token_list != None:
        shot = token_list[-1]
    else:
        shot = None
    return shot

def get_shot_code(shot_code):
    token_list = tokenize_shot_code(shot_code)
    if token_list != None:
        return '%s_%s_%s' % (token_list[0], token_list[1], token_list[-1])
    else:
        return None

def get_clip_name(clip_name):
    token_list = tokenize_clip_name(clip_name)
    if token_list != None:
        clip_name = '%s_%s' % (token_list[0], token_list[-1])
    else:
        clip_name = None
    return clip_name

class ProjectConfig(object):
    '''
    parse the data from the yaml
    '''
    def __init__(self, config_yaml_path ):
        super(ProjectConfig,self).__init__()
        log.debug("Parsing config from yaml file: %s" % config_yaml_path)

        self._config_yaml_path  = config_yaml_path  # path to the show config yaml
        self._config_hash       = None              # dictionary of all the show config values.
        self._show_dir_branch   = None              # cache all the branches for show directory config.

        if os.path.isfile(config_yaml_path):
            content = open(config_yaml_path).read()
            self._config_hash = yaml.load( content )
        else:
            raise KeyError, "Warning: There are no configuration found under '%s'." % config_yaml_path

    def get(self, setting_key, default=None, expandpath=False):
        '''
        @param setting_key contain multiple levels separated by colon, ex: show:fps, or shotgun:url etc.
        @param resolve if this is False, then a whole level may be returned instead of the default
        @return the value for the key
        '''
        if ":?platform" in setting_key:
            setting_key = setting_key.replace("?platform", "%s" % "linux" if os.name=='posix' else "windows")

        setting_key_token = setting_key.split(':')

        if self._config_hash == None:
            raise IOError, "The configuration was not parsed properly."

        _resolved = self._config_hash
        _resolve_index = 0

        # resolve down the hierarchy until the value is reached.
        while _resolve_index < len(setting_key_token) and setting_key_token[_resolve_index] in _resolved.keys():
            _resolved = _resolved[ setting_key_token[_resolve_index] ]
            _resolve_index += 1

        # value not fully resolved, return default value.
        if type(_resolved)==dict:
            _resolved = default

        if isinstance(_resolved, (str,unicode)) and expandpath:
            _resolved = os.path.expanduser(os.path.expandvars(_resolved))

        return _resolved

    def get_container(self, key, default=None):
        ctr = self._config_hash
        try:
            for p in key.split(':'):
                ctr = ctr.__getitem__(p)
        except KeyError:
            ctr = default or {}
        return ctr

    def get_show_dir_hier(self):
        '''
        This function return as a dictionary the show directory hierarchy information.
        '''
        return self._config_hash.get('show_dir_config', {})

    def get_show_dir_branch(self, branch_tag, create_branch=False, resolve_branch_hash=None):
        '''
        Parse the show_dir_config block from the show yaml, and build a list of tagged branches.

        @param branch_tag specify the tag name of the particular branch, this tag is in the show_yaml.
        @param create_branch create the branch if doesn't already exist
        @param resovle_branch_hash any branch tokens that needs to be resolved.
        @return a list representing the hierarchy path of the branch.

        ex:     get_show_dir_branch( branch_tag="branch_asset_root" )
                > '?project:?prod_dir_type:assets'
        '''

        if resolve_branch_hash is None:
            resolve_branch_hash = {}

        if self._show_dir_branch==None:
            f = file(self._config_yaml_path, 'r')

            # use to walk the show dir stack.  If this is None, it means it has yet encounter the show_dir_config block
            self._show_dir_branch   = {}
            dir_walk_stack          = None

            for t in yaml.scan(f):
                if type(t) == yaml.tokens.ScalarToken and t.value=='show_dir_config':
                    dir_walk_stack = []

                if dir_walk_stack==None:
                    continue

                if type(t) == yaml.tokens.BlockMappingStartToken:
                    dir_walk_stack.append(None)

                if type(t) == yaml.tokens.ScalarToken and len(dir_walk_stack):
                    dir_walk_stack[-1] = t.value

                if type(t) == yaml.tokens.BlockEndToken:
                    dir_walk_stack.pop(-1)

                    if len(dir_walk_stack)==0: # complete parsing
                        break

                if type(t) == yaml.tokens.AnchorToken:
                    self._show_dir_branch[t.value] = copy.copy(dir_walk_stack)

        if branch_tag in self._show_dir_branch:
            # some defaults
            if 'project' not in resolve_branch_hash: resolve_branch_hash['project'] = current_show()
            #if 'prod_dir_type' not in resolve_branch_hash: resolve_branch_hash['prod_dir_type'] = 'publish'
            if 'artist' not in resolve_branch_hash: resolve_branch_hash['artist'] = 'common'

            # if publish then don't need artist in path
            branch_string =  ':'.join( self._show_dir_branch[branch_tag] )

            if resolve_branch_hash.get('prod_dir_type') == 'publish' and '?artist' in branch_string:
                branch_string =  branch_string.replace(':?artist:', ':')

            # create the branch if necessary
            if create_branch:
                from tbe_core.utils import shot_dir_setup
                return get_show_dir_root() + '/' + shot_dir_setup.create_branch(
                        get_show_dir_root(),
                        branch_string,
                        resolve_branch_hash
                        )

            else:
                return branch_string

        else:
            log.warning("Warning: Failed to find the branch tag '%s' from the show directory config in '%s'. Available: \n%s" % (
                                                            branch_tag, self._config_yaml_path, self._show_dir_branch.keys() ))
            return None
