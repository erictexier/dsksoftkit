import os

from dsk.base.path_helper import yaml_cache
from dsk.base.path_helper.shotgun_path import ShotgunPath
from dsk.base.resources import dsk_constants

from dsk.base.path_helper import template_includes
from dsk.base.path_helper.errors import DevError,DevUnreadableFileError

def get_templates_config(templates_file):
    """
    Returns the templates configuration as an object
    """

    try:
        data = yaml_cache.g_yaml_cache.get(templates_file, deepcopy_data=False) or {}
        data = template_includes.process_includes(templates_file, data)
    except DevUnreadableFileError as e:
        print(e)
        data = dict()

    return data
