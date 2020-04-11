"""Test the current sgtk core configuration
"""
import pytest
import os
import sys
import getpass
from pprint import pprint

print "WithPython version \"%s\"" % (".".join(str(i) for i in sys.version_info[0:3]),)

#import sgtk.platform
root_tk = os.environ.get("TANK_CURRENT_PC","")
if root_tk in [None,""]:
    root_tk = "/u/sgtk/dev/eric/devshow"  # this should be removed
    print "testing in a dev environment init to %s for now" % root_tk
    print "set your TANK_CURRENT_PC environment to your config to be tested"

if root_tk == "/u/sgtk/studio":
    raise Exception("For dev or td nothing should point to this config/ studio config")

try:
    import sgtk

except:
    python_path = os.path.abspath(os.path.join(root_tk, "install","core","python"))
    print "Adding sgtk location to python_path: %s" % python_path
    sys.path.insert(0,python_path)


from sgtk import constants
from sgtk.pipelineconfig import PipelineConfiguration

# a config file
cf = PipelineConfiguration(root_tk)

@pytest.fixture
def sgwi():
    """ Shotgun with authentification"""
    import sgtk
    from tank_vendor.shotgun_authentication import ShotgunAuthenticator
    cdm = sgtk.util.CoreDefaultsManager()
    authenticator = ShotgunAuthenticator(cdm)
    user = authenticator.create_script_user(api_script="Toolkit",api_key="cdeb3545052b2afeec449c43deda7c857558a067658b52033ce489d0789d6aff")
    sgtk.set_authenticated_user(user)
    return sgtk.sgtk_from_path(cf.get_primary_data_root())

def test_configpipeline():
    """Mostly to informs not really a test,  use py.test -s"""
    print "is localized", cf.is_localized()
    print "shotgun id", cf.get_shotgun_id()
    print "is_auto_path", cf.is_auto_path()
    print "project id", cf.get_project_id()
    print "is_site config", cf.is_site_configuration()
    print "project disk name",cf.get_project_disk_name()
    print "published_file_entity_type",cf.get_published_file_entity_type()
    print "shotgun_path_cache_enabled",cf.get_shotgun_path_cache_enabled()
    print "local_storage_roots",cf.get_local_storage_roots()
    print "all_platform_data_roots",cf.get_all_platform_data_roots()
    print "get_data_roots",cf.get_data_roots()
    print "has_associated_data_roots",cf.has_associated_data_roots()
    print "primary_data_root",cf.get_primary_data_root()
    print "associated_core_version",cf.get_associated_core_version()
    print "get_install_location",cf.get_install_location()
    print "bundles_location",cf.get_bundles_location()
    print "config name",cf.get_name()
    print "config path",cf.get_path()
    print "config location",cf.get_config_location()
    print "schema location",cf.get_schema_config_location()
    print "environment",cf.get_environments()

    try:
        # 'writable is new'
        print cf.get_environment("asset",context=None,writeable=False)
    except Exception,e:
        print "No writable key for this version of ",str(e)

    print "get_environment_path",cf.get_environment_path("asset")
    print "get_environment_path",cf.get_environment_path("shot")
    print "core_hooks_location",cf.get_core_hooks_location()



    '''
    engine = cf.get_engines()
    fw = cf.get_frameworks()
    print "engine",engine
    print "framework",fw
    for i in engine:
        print "get_apps",cf.get_apps(i)
    '''

    #def execute_core_hook_internal(self, hook_name, parent, **kwargs)
    #def execute_core_hook_method_internal(self, hook_name, method_name, parent, **kwargs)

# config
def test_file_exist():
    """ check if all the xml file for definition exists """
    x = cf.get_environments()
    for xx in x:
        print cf.get_environment_path(xx)
        assert os.path.exists(cf.get_environment_path(xx))

def test_config_template():
    x = cf.get_templates_config()
    assert sorted(x.keys()) == sorted(['keys', 'paths', 'strings'])
    assert isinstance(x,dict)

def test_config_location():
        assert os.path.exists(cf.get_path())
# shotgun
def test_type_file_publish():
    assert cf.get_published_file_entity_type() == "PublishedFile"

"""require authentification
"""
#@pytest.mark.skip(reason="will failed on project with name as label")

#@pytest.mark.xfail
def test_project_name_sg(sgwi):
    sg = sgwi.shotgun
    infoname = sg.find_one("Project",[['id','is',cf.get_project_id()]],["name"])
    print "Query project by name",infoname
    assert infoname['name'].lower() == cf.get_project_disk_name()

#@pytest.mark.xfail
def test_task_id_list(sgwi):
    """query owner task assign
    """
    import sgtk
    sg = sgwi.shotgun
    atk = sgtk.sgtk_from_entity("Project",cf.get_project_id())
    user = sgtk.util.get_current_user(atk)
    filters = list()
    #["step.Step.code", "is", "Shading"]
    filters.append(['project', 'is', {'type': 'Project', 'id':cf.get_project_id() }])
    #filters.append(["sg_status_list", "is", "ip"])
    #filters.append(["task_assignees", 'is', {"type": "HumanUser", "id": 660, "name": "Texier Eric"}])
    filters.append(["task_assignees", 'is', user])

    fields = list(['code','task_assignees','sg_status_list'])
    sg_task = sg.find("Task",filters=filters,fields=fields)
    print len(sg_task)
    pprint(sg_task)
    for x in sg_task:
        if 'task_assignees' in x:
            for y in x['task_assignees']:
                print "INFO user", y['name'],y['id']

def test_pipeline_config(sgwi):
    """query owner task assign
    """
    import sgtk
    sg = sgwi.shotgun
    #atk = sgtk.sgtk_from_entity("Project",cf.get_project_id())
    #user = sgtk.util.get_current_user(atk)
    filters = list()

    filters.append(['project', 'is', {'type': 'Project', 'id':cf.get_project_id() }])
    #filters.append(["id", "is", cf.get_shotgun_id()])
    fields = ["id", "code", "project","linux_path", "windows_path", "mac_path","users"]
    sg_pc = sg.find(constants.PIPELINE_CONFIGURATION_ENTITY,
                    filters,
                    fields)
    pprint(sg_pc)

@pytest.mark.xfail
def test_download(sgwi):
    sg = sgwi.shotgun
    from sgtk.util.shotgun import download_url
    data = 'https://sg-media-ireland.s3-accelerate.amazonaws.com/4560419c21a1fdaf53582bf90b33f66b1f56882d/5590499cb4790870a16627f24344b80850115476/642f1c2499b137b0_Anim.v002_t.jpg?AWSAccessKeyId=AKIAI52SI43FHJUKTP5Q&Expires=1499158152&Signature=sEu%2BtahB6UwYV%2B2ImjcUFmyqW8Q%3D&response-content-disposition=filename%3D%22642f1c2499b137b0_Anim.v002_t.jpg%22&x-amz-meta-user-id=293&x-amz-meta-user-type=ApiUser'
    #data = "https://sg-media-ireland.s3-accelerate.amazonaws.com/4560419c21a1fdaf53582bf90b33f66b1f56882d/371d51c00be53e66bec3cd2e680102f710fb9c15/tmpYhQYCO_t.jpg?AWSAccessKeyId=AKIAI52SI43FHJUKTP5Q&Expires=1499158151&Signature=sCn1xmFgyACmZnkUYVhdDGt2uqI%3D&response-content-disposition=filename%3D%22tmpYhQYCO_t.jpg%22&x-amz-meta-user-id=293&x-amz-meta-user-type=ApiUser"
    a = download_url(sg,data,"downloadimage.jpg")