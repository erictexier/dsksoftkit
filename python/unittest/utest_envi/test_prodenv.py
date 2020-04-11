import os
from dskenv.proxy_env import ProdEnv
from dsk.envi_commit.lib.c_and_p_tools import CandPTools
from dskenv import dskenv_constants

def test_prodenv():
    ax = os.path.join(os.sep,
                      dskenv_constants.DSK_MOUNTED_ROOT,
                      dskenv_constants.DSK_DEV_AREA,
                      dskenv_constants.DSK_CONFIGURATION_FOLDER,
                      dskenv_constants.DSK_ENVI_FOLDER)

    x = ProdEnv(ax)
    xx = x.get_all_valid_config_and_packs()
    for u in xx:
        print(1,u)


    ay = os.path.join(os.sep,
                      dskenv_constants.DSK_MOUNTED_ROOT,
                      dskenv_constants.DSK_DEV_AREA,
                      'eric',
                      dskenv_constants.DSK_CONFIGURATION_FOLDER,
                      dskenv_constants.DSK_ENVI_FOLDER)
    y = ProdEnv(ay)
    yy = y.get_all_valid_config_and_packs()
    for u in yy:
        print(2,u)
    xx = CandPTools.translate_for_gui(xx)
    res = CandPTools.store_in_dict_gui(xx)
    assert len(res) <= len(xx)


