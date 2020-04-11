import pytest
import os
import sys
import dsk

DEV_ENV = os.path.dirname(os.path.dirname(dsk.__path__[0]))

# this is part of the test
try:
    from dsk.base.utils.git_utils import GitUtils
except ImportError:
    print("needed: envi -p dev_tools")
    sys.exit(0)

def test_repo_exist():
    x = GitUtils(DEV_ENV)
    assert x.is_valid() == True

def test_version():
    x = GitUtils(DEV_ENV)
    assert x.get_git_version() != ""

def test_git_name():
    x = GitUtils(DEV_ENV)
    assert x.get_git_name() != ""

def test_list_date():
    x = GitUtils(DEV_ENV)
    assert len(x.get_git_date(1)) == 1

def test_log_git():
    x = GitUtils(DEV_ENV)
    assert len(x.get_git_log_raw(30)) > 1

def test_version_when_tag():
    x = GitUtils(DEV_ENV)
    tag = x.get_git_version()
    rootname = x.get_git_name()
    assert rootname != ""
    assert tag != ""
    ### example de generation de repo over write
    #res=x.install_repo_from_bash(SRC_REPO, RELEASE_LOCATION_DISK, rootname, tag)
    #print("\n".join(res))

