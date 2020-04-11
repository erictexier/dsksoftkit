import os
from dsk.templates.template_envi import repo_pack


def build_string(release_path, repo_name):
    return repo_pack.DATA_PACK % {'rootname': os.path.join(release_path,repo_name)}
