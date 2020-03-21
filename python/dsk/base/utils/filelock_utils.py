import os
import sys
import stat
import subprocess
import logging
import stat


from dsk.base.utils import platform_utils as path_utils
from dsk.base.utils import file_utils
from dsk.base.utils.log_utils import MsgUtils as log
from dsk.base.resources.dsk_errors import DskFileErr

try:
    import pwd
    import grp
except ImportError:
    pwd = grp = None     # Modules not on windows


class FilePermissionsProvider(object):
    def __init__(self):
        pass


def is_locked(path):
    if os.path.isfile(path):
        return str(os.stat(path).st_uid) == show_config.get('publish_user:uid')
    else:
        if str(os.stat(path).st_uid) != show_config.get('publish_user:uid'):
            return False
        else:
            contents = os.listdir(path)
            for file_path in contents:
                content_path = os.path.join(path, file_path)
                if not is_locked(content_path):
                    return False
            return True


def lock_file(path, preserveTime=True):
    sys.stdout.write(">>>>>>>>>>file_utils lock_file %s\n" % path)
    sys.stdout.flush()

    if is_locked(path):
        sys.stdout.write(">>>>>>>>>>file_utils %s already locked\n" % path)
        sys.stdout.flush()
        return 0
    # Files created by tempfile.mkstemp() will be read/write only by the user,
    # which will make wm_cp unable to read the file. watchman should be in
    # the same group as users, so attempt to make files
    # u+rw,g+r using the current user, otherwise assume watchman can already
    # read it.
    try:
        # NOT wm_chmod
        info = os.stat(path)
        mode = (stat.S_IMODE(info.st_mode) |
                stat.S_IRUSR | stat.S_IWUSR |
                stat.S_IRGRP)
        os.chmod(path, mode)
    except:
        pass
        # If it's still not readable by the publish user (watchman),
        # then cp_file below will fail

    tmpPath = "%s.tmp" % path
    try:
        file_utils.cp_file(path, tmpPath, preserveTime=preserveTime)
        file_utils.rm_file(path)
        file_utils.mv(tmpPath, path, isforce=True)
        file_utils.chmod_file(path)
    except subprocess.CalledProcessError as exc:
        try:
            file_utils.rm_file(tmpPath)
        except:
            pass
        raise DskFileErr(
            exc.returncode,
            "lock failed: could not %s" % os.path.basename(exc.cmd[0]), path)
    return 0


def lock_dir_recursive(path, preserveTime=True):
    sys.stdout.write(">>>>>>>>>>file_utils lock_dir_recursive %s\n" % path)
    sys.stdout.flush()

    if is_locked(path):
        sys.stdout.write(">>>>>>>>>>file_utils %s already locked\n" % path)
        sys.stdout.flush()
        return 0

    # Files or dirs created by tempfile.mkstemp() will be read/write only by
    # the user, which will make wm_cp unable to read the file. watchman
    # should be in the same group as users, so attempt to make all files
    # u+rw,g+r using the current user, otherwise assume watchman can already
    # read it.
    # Suppress errors, ignore result, and continue (as long as there is not a
    # traceback from launching the process NOT wm_chmod
    cmd = ["/bin/chmod", "-R", "--silent", "u+rw,g+r", path]
    result = subprocess.call(cmd)
    # If it's still not readable by the publish user (watchman), then
    # cp_recursive below will fail

    tmpPath = "%s.tmp" % path
    try:
        file_utils.cp_recursive(path, tmpPath, preserveTime=preserveTime)
        file_utils.rm_recursive(path)
        file_utils.mv(tmpPath, path, isforce=True)
        file_utils.chmod_recursive(path)
    except subprocess.CalledProcessError as exc:
        try:
            file_utils.rm_recursive(tmpPath)
        except:
            pass
        raise FileUtilsErr(
                exc.returncode,
                "lock failed: could not %s: %s" % (os.path.basename(
                                                    exc.cmd[0]), exc),
                path)
    return 0


class FilePermissions(object):
    def __init__(self, permissions_provider):
        self.permissions = permissions_provider

    def _curstat(self, path):
        info = os.lstat(path)
        uid = info.st_uid
        gid = info.st_gid
        try:
            uname = pwd.getpwuid(uid).pw_name
        except:
            uname = "?"

        try:
            gname = grp.getgrgid(gid).gr_name
        except:
            gname = "?"

        fkind = '?'
        if stat.S_ISDIR(info.st_mode):
            fkind = 'D'
        elif stat.S_ISREG(info.st_mode):
            fkind = 'F'
        elif stat.S_ISLNK(info.st_mode):
            fkind = 'L'
        return (fkind,
                stat.S_IMODE(info.st_mode),
                uname, gname, uid, gid, path)

    def lock_file(self, path, chowned_set=None, utime=False):
        log.debug("Locking %s" % path)
        wm_path = path_utils.conform_path(path, os_name="linux")
        log.debug("stat [%c %#o] %s:%s (%d:%d): %s" % self._curstat(path))

        lock_file(wm_path, preserveTime=not utime)

        # The shared set from the current session should be passed in,
        # to keep track of which files
        # have been chown'd to in watchman case of a rollback.
        # This is a keyword argument to stay compatible
        # with spk.
        if chowned_set is not None:
            chowned_set.add(path)

    def lock_dir(self, path, chowned_set=None, utime=False):
        self.lock_dir_recursive(path, chowned_set=chowned_set, utime=utime)

    def lock_dir_recursive(self, path, chowned_set=None, utime=False):
        log.debug("Locking recursively %s" % path)
        # wm_path = path_utils.conform_path(path, os_name="linux")
        log.debug("stat [%c %#o] %s:%s (%d:%d): %s" % self._curstat(path))

        file_utils.lock_dir_recursive(path, preserveTime=not utime)

        for root, dirs, files in os.walk(path):
            for d in dirs:
                this_dir = os.path.join(root, d)
                if chowned_set is not None:
                    chowned_set.add(this_dir)
            for f in files:
                this_file = os.path.join(root, f)
                if chowned_set is not None:
                    chowned_set.add(this_file)

    def lock_items(self, items, chowned_set=None, utime=False):
        dirs = []
        files = []
        for path in items:
            if os.path.isdir(path):
                dirs.append(path)
            else:
                files.append(path)

        dirs.sort()
        files.sort()

        # ## !!! Not efficient anymore because it does 1 file at a time
        for path in dirs:
            self.lock_dir(path, chowned_set=chowned_set, utime=utime)
        for path in files:
            self.lock_file(path, chowned_set=chowned_set, utime=utime)
