import pytest
import os
from dsk.base.db_helper.shotgun_script import connect_to_shotgun
from dsk.base.db_helper.db_cache import DbCache
from dsk.base.db_helper.db_helper_funct import ShotgunQuery as SQ
from dsk.base.resources.get_pix_version import get_pixmap
from dsk.shot_info.resources.icon_gen_mt import IconGenQueue
from dsk.base.db_helper.version_info_db import VersionInfoDb
from dsk.shot_info.resources.shotinfo_constant import TEMP_ICON_DIRECTORY,BASE_RES

from dsk.base.utils.time_utils import StopWatch

conn = connect_to_shotgun()

@pytest.mark.skipif(True, reason="too long")
def test_media():
    dbc = DbCache(shot_only=True, asset_only=False)

    showobj =  dbc.get_showobj('dev_show')
    VER_TYPE = None
    shot_list = dbc.load_shot('dev_show',['125_3600',
                                        '007_0300','036_0200',
                                        '110_0500','036_1100',
                                        '125-4500'])
    for shotobj in shot_list:
        res = dbc.update_media_version_shot_info(showobj,
                                                 shotobj,
                                                 VER_TYPE,
                                                 force = True)

        for x in res:
            for y in x.getChildren():
                print(y.getName(), y.version_type,y.id)
                if(y.path_to_frame != "":print "\t", y.path_to_frame,y.creation_date)
                if(y.path_to_movie != "":print "\t", y.path_to_movie,y.creation_date)


@pytest.mark.skipif(True, reason="too long")
def test_latest_version():
    dbc = DbCache(shot_only=True, asset_only=False)
    showobj =  dbc.get_showobj('dev_show')
    SW = StopWatch()
    SW.start()
    res = dbc.get_lasted_version_for_show(showobj, limit=10)
    count = 0
    for x in res:
        if x.iconfile == "":
            count += 1
            x.get_iconfile(dbc, TEMP_ICON_DIRECTORY,conn,BASE_RES)

    SW.stop()
    print "download %d icon in %f" % (count,SW.elapsed())


@pytest.mark.skipif(True, reason="too long")
def test_make_icon_mt():
    dbc = DbCache(shot_only=True, asset_only=False)
    showobj =  dbc.get_showobj('dev_show')
    SW = StopWatch()
    res = dbc.get_lasted_version_for_show(showobj, limit=10)
    SW.start()
    SW.stop()
    print "download %d icon in %f" % (len(res),SW.elapsed())
