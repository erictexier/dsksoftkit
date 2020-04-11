import os
import sys
import pytest
from dskenv.base_env import BaseEnv
from dskenv.api.envi_api import DevUser
from dskenv.api import dsk_release_lib
from dskenv.api.dsk_release_lib import RepoInstall

from dsk.base.lib.envi_info_helper import EnviInfoHelper

rootdir = os.path.dirname(__file__)
afile = os.path.join(rootdir,"newenvi.yml")
afile2 = os.path.join(rootdir,"newenvi2.yml")
def test_add_user():

    x = dsk_release_lib.DskReleaseLib()
    x.load_data()
    user="fakeuser"

    newu = DevUser()
    newu.setdata(**{
                  'login':user,
                  'email' : 'fakeuser@gmail.com',
                  'shotgun_name':'fakeuser blah',
                  'dev_path' : '/asdjad/asdjkasd',
                  'dev_path_configs':  ['fooo','fsdf'],
                  'projects' : ['dev_show']
                  })
    assert  not user in x.get_all_user_login()
    file_location =  BaseEnv.envi_info_location()

    ei = EnviInfoHelper()
    assert ei.add_user(file_location, afile,newu)

def test_add_repo():

    x = dsk_release_lib.DskReleaseLib()
    x.load_data()
    reponame="fakerepo"

    newrepo = RepoInstall()
    newrepo.setdata(**{
                  'name': reponame,
                  'new_version': 'true',
                  'do_version' : 'true',
                  'pack_update': 'true',
                  'shortname': 'shortfake',
                  'path': 'git@gfake.git',
                  'type': 'git',
                  'branch': ''
                  })
    assert  "" ==  x.name_repo(reponame)
    file_location =  BaseEnv.envi_info_location()
    print(file_location,afile2)
    ei = EnviInfoHelper()
    assert ei.add_repo(file_location, afile2,newrepo)
