import os
import sys
import getpass
from dsk.base.utils.yaml_utils import YamlUtils
from dsk.base.tdata.gen_tree import GenTree
from dsk.base.utils.yaml_utils import OrderedDictYamlDumper
from dsk.base.utils.yaml_utils import OrderedDictYamlLoader
from collections import OrderedDict

class foo(GenTree):
    def __init__(self):
        super(foo, self).__init__()

rootdir = os.path.dirname(__file__)

def test_save_load():
    afile = os.path.join(rootdir,"data.yml")
    afilenew = os.path.join(rootdir,"newdata.yml")
    afilenew2 = os.path.join(rootdir,"new2data.yml")
    for i in [afilenew,afilenew2]:
        if os.path.exists(i):
            os.remove(i)

    data = YamlUtils.load_data(afile)
    # make it user only: maybe user
    YamlUtils.save_data(afilenew,data)
    data2 = YamlUtils.load_data(afilenew)
    assert sorted(data.keys()) == sorted(data2.keys())
    YamlUtils.save_data(afilenew2,data2)

    for i in [afilenew,afilenew2]:
        if os.path.exists(i):
            os.remove(i)

    includes = list()
    if 'includes' in data2:
        # multi include section
        includes.extend( data2['includes'])

    for include in includes:
        resolved = YamlUtils.resolve_include(afilenew, include)
        assert resolved != None

        data3 = YamlUtils.load_data(resolved)
        assert data3["description"] == "The strings section"


def compare_two(data,data2):
    assert len(data) == len(data2)
    for x in data:
        assert x in data2
        assert data[x] == data2[x]
        if isinstance(data[x],OrderedDict):
            assert len(data[x]) == len(data2[x])
            assert data[x] == data2[x]
            for y in data[x]:
                assert y in data2[x]
                assert data[x][y] == data2[x][y]
                print x,data[x][y], data2[x][y]
        if isinstance(data[x],list):
            for ii in range(len(data[x])):

                assert data[x][ii] == data2[x][ii]
                assert len(data[x][ii]) == len(data2[x][ii])
                if isinstance(data[x][ii],OrderedDict):
                    for y in data[x][ii]:
                        assert y in data2[x][ii]
                        assert data[x][ii][y] == data2[x][ii][y]
                        print x,data[x][ii][y], data2[x][ii][y]


    for x in data2:
        assert x in data
        assert data2[x] == data[x]
        if isinstance(data2[x],OrderedDict):
            for y in data2[x]:
                assert y in data[x]
                assert data2[x][y] == data[x][y]
                print x,data2[x][y], data[x][y]

def test_ordered_envi_info():
    afile = os.path.join(rootdir,"envi_info.yml")
    afile1 = os.path.join(rootdir,"envi_info_1.yml")
    afile2 = os.path.join(rootdir,"envi_info_2.yml")
    data = YamlUtils.load_data(afile, OrderedDictYamlLoader)
    YamlUtils.save_data(afile1, data, OrderedDictYamlDumper)
    data2 = YamlUtils.load_data(afile1, OrderedDictYamlLoader)
    YamlUtils.save_data(afile2, data2, OrderedDictYamlDumper)
    #print "data2",data2,len(data2)
    compare_two(data,data2)

def test_ordered_envi_info2():
    afile = os.path.join(rootdir,"envi_info.yml")
    afile1 = os.path.join(rootdir,"envi_info_3.yml")
    afile2 = os.path.join(rootdir,"envi_info_4.yml")
    afile3 = os.path.join(rootdir,"data.yml")
    afile4 = os.path.join(rootdir,"xxdata.yml")
    datao = YamlUtils.load_data(afile)

    data = YamlUtils.load_data(afile, OrderedDictYamlLoader)
    YamlUtils.save_data(afile1, data, OrderedDictYamlDumper)
    compare_two(datao,data)
    #print "data2",data2,len(data2)
    data2 = YamlUtils.load_data(afile)
    compare_two(datao,data2)

    data = YamlUtils.load_data(afile3)
    YamlUtils.save_data(afile4,data)
    #print "data2",data2,len(data2)

def test_envi_info():
    afile = os.path.join(rootdir,"envi_info.yml")
    data = YamlUtils.load_data(afile)
    assert data["site"]
    assert "Paris" in data["site"]["name"]

def test_envi_file():
    from dskenv.base_env import BaseEnv
    assert os.path.isfile(BaseEnv.envi_info_location())

def test_envi_file_save_local():
    from dskenv.base_env import BaseEnv
    assert os.path.isfile(BaseEnv.envi_info_location())

    data = YamlUtils.load_data(BaseEnv.envi_info_location())
    # make it user only: maybe user
    afileout = os.path.join(rootdir,"envi_saved.yml")
    YamlUtils.save_data(afileout,data)


def test_dsk_release():
    from dskenv.api.dsk_release_lib import DskReleaseLib
    x = DskReleaseLib()
    assert x.is_valid() == False
    x.load_data()
    assert x.is_valid() == True
