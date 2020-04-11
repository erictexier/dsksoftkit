import pytest
from pprint import pformat
import getpass
from dsk.base.db_helper.shotgun_script import connect_to_shotgun_time_out
from dsk.base.db_helper.shotgun_script import connect_to_shotgun
from dsk.base.db_helper.db_helper_funct import ShotgunQuery
from dsk.base.db_helper.db_cache import DbCache
from dsk.base.db_helper.version_info_db import VersionInfoDb
from dsk.base.db_helper.asset_info_db import AssetInfoDb
from dsk.base.db_helper.db_helper_funct import ShotgunQuery as SQ

from dsk.base.utils.time_utils import StopWatch
#def test_connection():
#    assert connect_to_shotgun()

#def test_connection_time_out():
#    assert connect_to_shotgun_time_out()

conn = connect_to_shotgun()
def test_all_show():
    a = ShotgunQuery.get_current_projects(conn)
    print([(x.getName(),x.id) for x in a])
    assert len(a) > 0
    #for x in a:
    #    print x
def test_get_devshow():
    a = ShotgunQuery.show_id_by_name(conn,'dev_show')
    assert 'id' in a
    shotlist = ShotgunQuery.shot_list_with_id(a['id'], conn)
    assert len(shotlist) > 0

    assetList = ShotgunQuery.asset_list_with_id(a['id'], conn)
    assert len(assetList) > 0


def test_get_setting():
    a = ShotgunQuery.show_id_by_name(conn,'dev_show')
    assert 'id' in a
    settinglist = ShotgunQuery.query_settings(a['id'], conn)
    for s in settinglist:
        print(s)

@pytest.mark.skipif(True, reason="too long")
def test_file_type():
    dbc = DbCache()
    name = dbc.get_ft_from_short_name('maya_shader_maf_file')
    print("NNNNN",name)
    assert name == "Maya Shader Assignation File"

@pytest.mark.skipif(False, reason="too long")
def test_file_type_filter():
    ft = SQ.filter_fpt_by_name('maya_model_file',conn=conn)

    for f in ft:
        print("--------->",f.getName(),pformat(f))
    dbc = DbCache()
    print(pformat(dbc.get_file_type_names()))
    #print pformat(ft)

@pytest.mark.skipif(True, reason="too long to wait")
def test_db_cache():
    dbc = DbCache()
    dbc.init_with_current_shows()
    dbc.set_show("dev_show")
    showobj =  dbc.get_current_show_obj()
    seqs = showobj.get_sequences()
    for seq in seqs.getChildren():

        for shotobj in seq.getChildren():
            print(shotobj.getName(),shotobj.assets)

@pytest.mark.skipif(True, reason="too long to wait")
def test_db_asset_for_build_shot():
    dbc = DbCache(shot_only=False, asset_only=True)

    showobj =  dbc.get_showobj('dev_show')
    assert showobj != None
    M_SHADER_SF = 'maya_shader_src_file'
    M_RIG_SF = 'maya_rig_src_file'
    file_type_list = [M_SHADER_SF,M_RIG_SF] #,'maya_model_file']
    #file_type_list = ['maya_rig_src_file'] #,'maya_model_file']
    #pft_list = dbc.asset_maya_build_query(showobj, assetobj, file_type_list)

    fts = SQ.filter_fpt_by_name(file_type_list,conn=dbc.get_conn())

    shd_src_pub_type = None
    rig_src_pub_type = None

    for f in fts:
        if f.getName() == M_RIG_SF:
            rig_src_pub_type = f
        elif f.getName() == M_SHADER_SF:
            shd_src_pub_type = f

    assert shd_src_pub_type != None
    assert rig_src_pub_type != None

    shot_list = dbc.load_shot('dev_show',['007_0200','051_0200'])
    assert len(shot_list) > 0
    for shotobj in shot_list:
        print("SHOT",shotobj.code,shotobj.assets)
        assets_id = shotobj.get_asset_ids()
        assets_name = shotobj.get_asset_names()
        for as_id,as_name in zip(assets_id,assets_name):
            print("asset name:",as_name)
            ass = AssetInfoDb()
            ass.setName(as_name)
            ass.setdata(as_id)
            SW = StopWatch()
            SW.start()
            #pf_list = dbc.assetid_filepub_query(showobj, as_id, file_type_list)
            pf_list = dbc.assetid_filepubobj_query(showobj,
                                                   ass,
                                                   [rig_src_pub_type,shd_src_pub_type])
            rig_srcs = pf_list[0]
            shd_srcs = pf_list[1]
            SW.stop()
            print("assetid_filepub_query in %f" % SW.elapsed())

            """ much slower
            SW.start()
            a = dbc.assetid_filepub_query(showobj, as_id, [file_type_list[0]])
            SW.stop()
            print("assetid_filepub_query1 in %f" % SW.elapsed())
            SW.start()
            b = dbc.assetid_filepub_query(showobj, as_id, [file_type_list[1]])
            SW.stop()
            print("assetid_filepub_query2 in %f" % SW.elapsed())
            """
            rig_mod_ids = []
            rig_rig_ids = []
            printinfo = True
            for pf in rig_srcs:

                if printinfo: print("VERSION RIG",pf.version_number)

                x = pf.get_upstream_model()
                if x != None:
                    if printinfo: print("\tRIG model version",pf.get_upstream_model_version(),x['id'])
                    rig_mod_ids.append(x['id'])

                x = pf.get_downstream_rig()
                if x:
                    if printinfo: print("\tRIG rig version",pf.get_downstream_rig_version(),x['id'])
                    rig_rig_ids.append(x['id'])

            shd_mod_ids = []
            shd_cfx_ids = []
            shd_shd_ids = []


            for pf in shd_srcs:

                if printinfo: print("VERSION SHADER",pf.version_number)

                x = pf.get_upstream_model()
                if x != None:
                    if printinfo: print("\tshader model version",pf.get_upstream_model_version(),x['id'])
                    shd_mod_ids.append(x['id'])
                x = pf.get_upstream_cfx()
                if x != None:
                    if printinfo: print("\tshader cfx version",pf.get_upstream_cfx_version(),x['id'])
                    shd_cfx_ids.append(x['id'])
                x = pf.get_downstream_shader()
                if x != None:
                    if printinfo: print("\tshader shader version", pf.get_downstream_shader_version(),x['id'])
                    shd_shd_ids.append(x['id'])

            #print "shader model", shd_mod_ids
            #print "shader cfx", shd_cfx_ids
            #print "shader shader",shd_shd_ids

            #entity_publish_id = rig_mod_ids + rig_rig_ids + shd_mod_ids + shd_cfx_ids + shd_shd_ids
            # check cfx model version
            """
            entity_publish_id = shd_cfx_ids
            if len(entity_publish_id) > 0:
                print("Q" * 100, entity_publish_id)
                res = ShotgunQuery.published_file_query(showobj.id, entity_publish_id , conn = dbc.get_conn())
                print ("return res",res)
                for pf in res:
                    x =  pf.get_upstream_model()
                    if x:
                        print(x)
                        print("\t\t\tfound model on cfx at version" % pf.get_upstream_model_version())
                #print(pf.getName(),r.get_file_local_path())
            """
            """
            for i in entity_publish_id:
                res = ShotgunQuery.published_file_query_one(showobj.id, i , conn = dbc.get_conn())
                if res: print(res)
            """


@pytest.mark.skipif(True, reason="too long to wait: media function")
def test_db_cache_shot_devshow():
    dbc = DbCache(shot_only=False, asset_only=False)
    dbc.init_with_current_shows()

    dbc.set_show("dev_show")

    showobj =  dbc.get_current_show_obj()
    assert showobj
    assert len(showobj.get_assetlist_names()) != 0


    # sequence
    ids = list()

    seqs = showobj.get_sequences()
    pformat(dbc.get_file_type_names())
    VER_TYPE = None #['deadlineNukeRender', 'deadlineMayaRender']
    #fts = SQ.filter_fpt_by_name(VER_TYPE,conn=dbc.get_conn())
    for seq in seqs.getChildren():
        #print(seq.getName(),seq.get_shot_names())
        for shotobj in seq.getChildren():

            #print("shotname",shotobj.getName(),"show id", showobj.id, "shot id", shotobj.id)
            #ids.append(shotobj)
            res = dbc.update_media_version_shot_info(showobj, shotobj, VER_TYPE, force = True)
            print("nb of shot version", len(res))
            ver_type = [x.getName() for x in res]
            ver_type = filter(lambda x: x != "No_Type", ver_type)

            #if ver_type:
            if 0:
                print(ver_type)
                res2 = ShotgunQuery.query_shot_media_latest(showobj.id,
                                                            shotobj.id,
                                                            VersionInfoDb.VF,
                                                            ver_type)


    # asset
    #print "xxxx"
    assets =  showobj.get_assets()
    #print "xxxx",assets
    for assetobj in assets.getChildren():
        #print assetobj
        #print "assetname",assetobj.getName(),"show id", showobj.id, "asset id", assetobj.id
        ids.append(assetobj)
        res = dbc.update_media_version_asset_info(showobj, assetobj, VER_TYPE)
        print "nb of asset version", len(res)
        ver_type = [x.getName() for x  in res]
        ver_type = filter(lambda x: x != "No_Type", ver_type)
        print ver_type
        """
        if ver_type:
            print ver_type
            res2 = ShotgunQuery.query_asset_media_latest(showobj.id,
                                                         assetobj.id,
                                                         VersionInfoDb.VF,
                                                         ver_type)
        """



@pytest.mark.skipif(True, reason="too long to wait: media function")
def test_serialize_step():
    dbc = DbCache(shot_only=True, asset_only=True)
    steps = dbc.get_steps()
    for step in steps:

        print(pformat(step))
    print("saved as %s" % "foo.xml")
    dbc.SaveAsXml("foo.xml")
    # play list
    #dsply_list = SQ.playlist_query_versions(showobj.id,conn=conn)
    #print("Display list",dsply_list)

    #steps = ShotgunQuery.step_list_with_id(conn)
    #print(steps)

    #step_names = ShotgunQuery.step_names(conn)
    #print(step_names)


#@pytest.mark.skipif(True, reason="too long to wait")
def test_db_current_user_as_dict():
    dbc = DbCache(shot_only=False, asset_only=True)
    print(dbc.get_user_dict(getpass.getuser()))
    assert dbc.get_user_dict(getpass.getuser()) != None



