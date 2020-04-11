import os
import pytest
from dskenv.envi import Envi

APP = "maya"

##### SHOW CONTEXT
shows = ["dev_show"]

#@pytest.fixture
def launch():
    pass

def test_rawlaunch():
    a = Envi()
    configs = ['envipython1'] # the name of the application here is not relevant
    configs.append("-c dev_show")  # version

    try:
        a.execute(configs,True)
    except Exception,e:
        print(str(e))

    configs = ['envipython2']
    configs.append("-p sgtkstudio_maya") # repo dev

    try:
        a.execute(configs,True)
    except Exception,e:
        print(str(e))

    configs = ['envipython3']
    configs.append("-p base_maya -d") # get basic maya env
    #configs.extend(modedev) # include the 'rnd' environment
    configs.append("-p clean_prepath") # collapse pre_path

    configs.append("-p studio_sgtk")
    configs.append("-p sgtk_test_dev_show")

    # launch mayapy
    configs.append("-a %s" % APP)

    try:
        a.execute(configs,True)
    except Exception,e:
        print(str(e))
