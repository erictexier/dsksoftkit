import pytest
import os


from dsk.base.path_helper.pathconfig import PathConfig
from dsk.base.path_helper import template
from dsk.base.resources.dsk_constants import ROOT_CONFIG_DIR, NAME_CONFIG_DIR
from dskenv.dskenv_constants import DSK_MOUNTED_ROOT, DSK_DEV_AREA
from dskenv.base_env import BaseEnv
root_envi = os.path.join(os.sep,
                         DSK_MOUNTED_ROOT,
                         DSK_DEV_AREA,
                         ROOT_CONFIG_DIR,
                         NAME_CONFIG_DIR)

# this is a dev user config
root_envi_user = os.path.join(os.environ.get("DSK_ENV_ROOT"),
                              'eric',
                              ROOT_CONFIG_DIR,
                              NAME_CONFIG_DIR)

project_file = os.path.join(os.sep,
                            DSK_MOUNTED_ROOT,
                            "shotgun",
                            "git",
                            "tk-config-default2",
                            "env",
                            "project.yml")

assert os.path.exists(root_envi)

@pytest.mark.skipif(False, reason="too long to wait")
def test_config():
    pc = PathConfig(root_envi, ROOT_CONFIG_DIR)
    x = pc.get_all_platform_data_roots()
    assert pc.is_site_configuration()
    assert 'primary' in x
    assert 'secondary' in x
    x = template.read_templates(pc)

    assert x

    apackdir = os.path.join(root_envi,BaseEnv.envi_iddir(),BaseEnv.pack_tag())
    aconfdir = os.path.join(root_envi,BaseEnv.envi_iddir(),BaseEnv.config_tag())
    envi_info = os.path.join(os.environ.get('DSKENVPATH'), 'configs_and_packs/envi_info.yml')
    bad_envi_info = '/mnt1/dev/dsk_configuration/envi/configs_and_packs/envi_info.yml'
    #d = {'Config': root_envi}
    d = {'Config': ('envi'),'name' : ('info')}
    a = x["envi_info"].apply_fields(d)
    assert a == envi_info
    a = x["envi_info"].missing_keys({}) 

    assert set(a) == set(d.keys())
    assert aconfdir ==  x["config_path"].apply_fields(d)

    assert apackdir ==  x["pack_path"].apply_fields(d)

    assert x['envi_info'].validate_and_get_fields(bad_envi_info)  == None


@pytest.mark.skipif(True, reason="too long to wait")
def test_add_config():
    pc = PathConfig(root_envi, ROOT_CONFIG_DIR)

@pytest.mark.skipif(True, reason="just display")
def test_project_config():
    from dsk.base.app.custom_menu import get_templates_config
    data = get_templates_config(project_file)
    for i in data:
        print(i,data[i])

@pytest.mark.skipif(True, reason="Not Done Yet")
def test_version_reg():
    """The version classication seems to be convoluted, this is to see if
    that can be hack until it's done probably
    """

    a1 = "Lighting_rs_beauty_CAM_021_2600_cam_track_CAM_021_2600_v01_v001_021_2600" # {'type': 'Shot', 'id': 11167, 'name': '021_2600'}
    a2 = "Compo_Jpeg_v003_079_0400" # {'type': 'Shot', 'id': 11421, 'name': '079_0400'}
    a3 = "Compo_EXR_v003_079_0400" # {'type': 'Shot', 'id': 11421, 'name': '079_0400'}
    a4 = "MG_058_0300_v006" # {'type': 'Shot', 'id': 11044, 'name': '058_0300'}

    a5 = "021_2400_Anim_playblast.v037.mov" # {'type': 'Shot', 'id': 11165, 'name': '021_2400'}


@pytest.mark.skipif(False, reason="Not Done Yet")
def test_base_template():
    pc = PathConfig(root_envi,'newshot')
    x = template.read_templates(pc)
    # pc.get_all_platform_data_roots()
    print(x["project_reference_file"].missing_keys({}))
    d = {'Project': 'toto', 'name': 'bgref', 'version' : 3, 'img_ext' : 'jpg'}
    # d = {'Episode': 'cpi', 'name': 'pidsa', 'Step': 'adsdf', 'version': '003', 'Asset': 'sgfd', 'sg_asset_type': 'gdfdfg'}
    print (x["project_reference_file"].apply_fields(d,platform="linux"))
    # print ("VALIDATE",x['project_reference_file'].validate_and_get_fields('/mnt/cpi/assets/gdfdfg/sgfd/adsdf/publish/files/houdini/pidsa.v003.hip'))
    





