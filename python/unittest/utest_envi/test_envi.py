import os
import sys
import pytest

# this is part of the test
try:
    from dskenv.envi import Envi
except ImportError:
    print("needed: envi -p base_envi")
    sys.exit(0)

"""This unitest is environment sensitive
it's meant to be run from a clean shell with no prior envi call
for now, and since where the code is we do need to be sure that the right pack
is include, so  -p base_envi may be required
"""



def test_info_from_environment():
    Env = Envi()
    # see if we can read the content of the environmement
    assert Env.info_from_environment()

@pytest.mark.xfail(strict=False)
def test_possible_run_config():
    # only base should be run when running this test
    Env = Envi()
    Env.info_from_environment()
    cmd = Env.get_commands()
    assert cmd == "-p base_envi" or cmd == []

def test_init_with_cmd():
    Env = Envi()
    Env.info_from_environment()
    b = Envi()
    b.init_with_cmd(Env.get_commands())
    assert Env.get_commands()==b.get_commands()

def test_get_cmd():
    Env = Envi()
    Env.info_from_environment()
    b = Envi()
    b.init_with_cmd(Env.get_commands())
    Env.do_eval_pack()
    b.do_eval_pack()

    assert Env.get_environ(withRemoveCmd=False) == b.get_environ(withRemoveCmd=False)

@pytest.mark.xfail(strict=False)
def test_compare_os_env():

    from dskenv import base_env
    Env = Envi()
    Env.info_from_environment()
    Env.do_eval_pack()
    Env.build_history_variable()
    d = Env.get_environ(withRemoveCmd=True)
    Env.expand_vars(d)
    dos = dict()
    dos.update(os.environ)

    exp = base_env.keyEnvi -1 # hack for now, since we remove a key
    if len(d) != len(dos):
        assert len(d)- len(exp) == len(dos)
        # copy the missing key
        for i in exp:
            if i in d and not i in dos:
                dos[i] = d[i]
    assert sorted(dos.keys()) == sorted(d.keys())
    # 2 of the key _BASE_CURRENT_PACKAGES and _BASE_CURRENT_CONFIGS
    # we just remove the leading : of those 2 key
    #for e in exp:
    #    while dos[e].startswith(os.pathsep):
    #        dos[e] = dos[e][1:]
    # compare the final
    assert dos == d

def test_dirversion():
    from dskenv.versioned_dir import DirVersioned
    d = DirVersioned("v1.2.3")
    assert d.is_versioned()
    d.inc_patch()
    assert d.patch == 4
    assert d.inc_minor()
    assert d.inc_major()
    assert d.version_string() == "2.3.4"

def test_pack_commit():
    from dskenv.base_env import BaseEnv
    from dskenv.pack_info import PackInfo
    from dsk.base.lib.base_fileproc import BaseFileProc
    run_dry = True

    packname = "dsk"
    repo_name = "devsoftkit"
    top_release_path = "/mnt/dev/install"
    version = "v0.0.8"

    searchPath1 = [BaseEnv.base()]
    searchPath2 = [BaseEnv.user_home('eric')]

    print("SEARCHPATH",searchPath1,searchPath2)

    pi = PackInfo(packname)
    rcHome = pi.real_version_file(PackInfo,searchPath2)
    fromFile = rcHome.get_fullname()
    rcRelease = pi.real_version_file(PackInfo,searchPath1)
    assert rcHome.is_versioned() == False

    import tempfile
    import uuid
    import re
    pat1 = re.compile("base_release\s*=")
    pat2 = re.compile("version\s*=")

    tmp = os.path.join(tempfile.gettempdir(), "pack_%s" % uuid.uuid4().hex)
    with open(fromFile, "rt") as fin:
        with open(tmp, "wt") as fout:
            for line in fin:
                m = pat1.search(line)
                if m:
                    release_path = os.path.join(top_release_path,repo_name)
                    fout.write('base_release = "%s"\n' % release_path)
                else:
                    m = pat2.search(line)
                    if m:
                        fout.write('version = "%s"\n' % version)
                    else:
                        fout.write(line)
    print(tmp)

    todolist = BaseFileProc()

    if rcRelease == None:
        print("first creation")
        rcHome.version_up_minor()
        toFile = rcHome.get_fullname()
        # repath
        toFile = toFile.replace(searchPath2[0],searchPath1[0])
        print("from %s to %s" % (tmp,toFile))
        todolist.copy_envifile(tmp, toFile)

    else:
        print(rcRelease.get_fullname())
        rcRelease.version_up_minor()
        toFile = rcRelease.get_fullname()
        todolist.copy_envifile(tmp, toFile)

    todolist.delete_file(tmp)
    #todolist.delete_file(fromFile)
    res_copy = todolist.execute_stop_first_failed(run_dry=run_dry, with_log = True)
    print(res_copy.success,res_copy.log)


def test_pack_checkout():
    from dskenv.base_env import BaseEnv
    from dskenv.pack_info import PackInfo
    from dsk.base.lib.base_fileproc import BaseFileProc

    run_dry = True
    dev_path = "/mnt/dev/eric/packages"
    packname = "dsk"

    repo_name = "devsoftkit"


    searchPath1 = [BaseEnv.base()]
    searchPath2 = [BaseEnv.user_home('eric')]

    print "SEARCHPATH",searchPath1,searchPath2
    pi = PackInfo(packname)

    import tempfile
    import uuid
    tmp = os.path.join(tempfile.gettempdir(), "pack_%s" % uuid.uuid4().hex)

    todolist = BaseFileProc()

    rcRelease = pi.real_version_file(PackInfo,searchPath1)
    if rcRelease != None:
        toFile = os.path.join(searchPath2[0],pi.get_label(),packname+".py")
        fromFile = rcRelease.get_fullname()
        import re
        pat1 = re.compile("base_release\s*=")
        pat2 = re.compile("version\s*=")


        with open(fromFile, "rt") as fin:
            with open(tmp, "wt") as fout:
                for line in fin:
                    m = pat1.search(line)
                    if m:
                        x = line.split("=")[1]
                        x = x.strip()
                        x = x.split(os.sep)[-1]
                        x = x.replace("'","")
                        x = x.replace('"',"")
                        source_dev_path = os.path.join(dev_path,x)
                        fout.write("base_release = %r\n" % source_dev_path)
                    else:
                        m = pat2.search(line)
                        if m:
                            fout.write('version = ""\n')
                        else:
                            fout.write(line)
        print(tmp)
        print("TOHOME",toFile)

        todolist.copy_envifile(tmp, toFile)
        todolist.delete_file(tmp)
    else:
        # make a blank
        from dsk.templates.template_envi import repo_pack
        toFile = os.path.join(searchPath2[0],pi.get_label(),packname+".py")
        print(tmp)
        print("TOHOME",toFile)

        data = repo_pack.DATA_PACK % {'rootname': os.path.join(dev_path,repo_name)}
        with open(tmp, "wt") as fout:
            fout.write(data)
        todolist.copy_envifile(tmp, toFile)
        todolist.delete_file(tmp)

    res_copy = todolist.execute_stop_first_failed(run_dry=run_dry, with_log = True)
    print(res_copy.success,res_copy.log)

@pytest.mark.skipif(False, reason="user base and too long")
def test_version_when_tag_from_temp():
    pytest.skip("test not multi-user friendly")
    RELEASE_LOCATION_DISK = '/mnt/dev/eric/packages'
    SRC_REPO = 'https://gitlab.com/erictexier/devsoftkit.git'
    try:
        from dsk.base.utils.git_utils import GitUtils
    except ImportError:
        print("needed: envi -p base_envi")
        sys.exit(0)

    tempdir = GitUtils.get_temp_git_clone_place_dir()
    x = GitUtils(tempdir)
    tempdest = x.get_temp_zone("REPO")
    res = x.clone_repo(SRC_REPO, tempdest)
    if res and len(res) > 0:
        if res[0] != "failed":# check
            x = GitUtils(tempdest)
            assert x.is_valid()
            print(x.get_git_version())
            assert x.get_git_name() in SRC_REPO
            assert x.get_git_version().startswith("v")
            res = x.copy_versionned_to_area(tempdest, RELEASE_LOCATION_DISK)
            print(res)
            assert res.success == True










