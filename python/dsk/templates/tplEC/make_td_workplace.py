""" This script to populate dev area """
import os
from dsk.templates.template_envi import td_pack


def build_string(project_name, dev_path):
    return td_pack.DATA_PACK % {'project_name': project_name,
                                'git_clone_area' : dev_path}
