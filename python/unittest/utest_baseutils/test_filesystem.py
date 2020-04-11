import os
import sys

try:
    from dsk.base.utils.filesystem_utils import FileSystemUtils
except ImportError:
    print("needed: envi -p base_envi")
    sys.exit(0)


def test_ensure_dir():
    """Test ensure_folder_exists, touch, safe_delete_file
    """
    x = FileSystemUtils  # only class instance
    apath = "/tmp/toto/blah"
    x.ensure_folder_exists(apath)
    assert os.path.isdir(apath)

    afile = os.path.join(apath,"too")
    x.touch_file(afile)

    x.safe_delete_file(afile)
    assert not os.path.exists(afile)
    os.rmdir(apath)
    assert  os.path.isdir(apath) == False

def test_valid_file_name():
    x = FileSystemUtils
    res = x.create_valid_filename("1   2 3 *4 5--[")
    print(res)
    assert res == "1___2_3__4_5--_"