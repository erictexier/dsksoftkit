import os
import sys
import stat
import subprocess
import errno
import glob
import fnmatch
import re
import itertools

from tbe_core.utils import path_utils
from tbe_core import dirmap
import show_config
from dsk.base.utils import path_utils
from tbe_core import dirmap
from dsk.base.lib import project_config


class FileUtilsErr(IOError):
    pass


# wrappers for setuid binaries
def clean_path(path):
    # trim trailing slash, multiple slashes
    abspath = os.path.normpath(os.path.abspath(path))
    return dirmap.get_link_remap(abspath).rstrip('/')       # convert /.mounts/ back to /mnt/studio/ links
    
    #path_list = path.split('/')
    #new_path_list = ['']
    #for p in path_list:
    #    if p != '':
    #        new_path_list.append(p)
    #path = '/'.join(new_path_list)
    #return path

def get_mode(path,new_dir=False,lock_prod=False):
    '''
    get mode for LOCKING directories and initial creation of directories (eg making shot dir or making asset dirs)
        
    in prod tree:
        down to $NCO_PROJECT_PATH/prod/shots/<SEQUENCE>/<SHOT>/<DEPT> 0755. these will always be directories
        down to $NCO_PROJECT_PATH/prod/assets/<ASSET_TYPE>/<ASSET_NAME>/<DEPT> 0755. these will always be directories

        initial creation:
            $NCO_PROJECT_PATH/prod/shots/<SEQUENCE>/<SHOT>/<DEPT>/common and below 0775 (directories) and 0664 (files)
            $NCO_PROJECT_PATH/prod/assets/<ASSET_TYPE>/<ASSET_NAME>/<DEPT>/common and below 0775 (directories) and 0664 (files)
        in place publishing:
            $NCO_PROJECT_PATH/prod/shots/<SEQUENCE>/<SHOT>/<DEPT>/common and below 0755 (directories) and 0644 (files)
            $NCO_PROJECT_PATH/prod/assets/<ASSET_TYPE>/<ASSET_NAME>/<DEPT>/common and below 0755 (directories) and 0644 (files)

        except pikit library:
            $NCO_PROJECT_PATH/prod/assets/pikit and below 0755 (directories) and 0644 (files)

    in publish tree:
        down to $NCO_PROJECT_PATH/publish/shots/<SEQUENCE> 0755. these will always be directories
        down to $NCO_PROJECT_PATH/publish/assets/<ASSET_TYPE> 0755. these will always be directories

        from $NCO_PROJECT_PATH/publish/shots/<SEQUENCE>/<SHOT> 1775 (directories) and 0644 (files)
        from $NCO_PROJECT_PATH/publish/assets/<ASSET_TYPE>/<ASSET_NAME> 1775 (directories) and 0644 (files)

    will return -1 if not in prod or publish tree of currently set project
    '''

    path = clean_path(path)

    is_dir = os.path.isdir(path) or new_dir

    publish_root = "%s/publish" %os.environ['NCO_PROJECT_PATH']
    prod_root = "%s/prod" %os.environ['NCO_PROJECT_PATH']
    
    prodlink_root = show_config.get("publish_user:prodlink_root")
    if prodlink_root:
        prodlink_root = os.path.join(prodlink_root, os.environ['NCO_PROJECT'], "prod")
    
    pikit_root = "%s" %show_config.get("pikit:library", expandpath=True)
    if pikit_root[-1:] == '/':
        pikit_root = pikit_root[0:-1]

    if path.find(pikit_root) == 0:
        if is_dir:
            mode = "0755"
        else:
            mode = "0644"
    elif path.find(prod_root) == 0:
        if len(path.split('/')) < 10:
            mode = "0755"
        else:
            if lock_prod:
                if is_dir:
                    mode = "0755"
                else:
                    mode = "0644"
            else:
                if is_dir:
                    mode = "0775"
                else:
                    mode = "0664"
    elif path.find(publish_root) == 0:
        if len(path.split('/')) < 8:
            mode = "0755"
        else:
            if is_dir:
                mode = "1775"
            else:
                mode = "0644"
    elif prodlink_root and path.find(prodlink_root) == 0:
        if len(path.split('/')) < 12:
            mode = "0755"
        else:
            mode = "0775"
    else:
        raise FileUtilsErr(errno.ENOSYS, "can't determine mode because path is outside prod and publish tree", path)
        #sys.stdout.write("ERROR: can't determine mode as path %s not in prod or publish or prodlink tree\n" %path)
        #return "-1"
    return mode

def mkdir(path):
    sys.stdout.write(">>>>>>>>>>file_utils mkdir path %s\n" %path)
    sys.stdout.flush()

    mode = get_mode(path,new_dir=True)
    sys.stdout.write(">>>>>>>>>>file_utils mkdir mode %s path %s\n" %(mode,path))
    sys.stdout.flush()
    cmd = [os.path.join(show_config.get("publish_user:bin", "/bin"),'wm_mkdir'),'-m',mode,'-p',path]
    return subprocess.check_call(cmd)

def rmdir(path, *paths):
    sys.stdout.write(">>>>>>>>>>file_utils rmdir path %s\n" %path)
    sys.stdout.flush()

    cmd = [os.path.join(show_config.get("publish_user:bin", "/bin"),'wm_rmdir'),path] + list(paths)
    return subprocess.check_call(cmd)

def rm_file(path, *paths):
    sys.stdout.write(">>>>>>>>>>file_utils rm_file paths %s\n" %str([path] + list(paths)))
    sys.stdout.flush()

    cmd = [os.path.join(show_config.get("publish_user:bin", "/bin"),'wm_rm'),'-f', path] + list(paths)
    return subprocess.check_call(cmd)

def rm_recursive(path, *paths):
    sys.stdout.write(">>>>>>>>>>file_utils rm_recursive paths %s\n" %str([path] + list(paths)))
    sys.stdout.flush()

    cmd = [os.path.join(show_config.get("publish_user:bin", "/bin"),'wm_rm'),'-rf', path] + list(paths)
    return subprocess.check_call(cmd)

def cp_recursive(source,destination, preserveTime=False):
    sys.stdout.write(">>>>>>>>>>file_utils cp_recursive source=%s destination=%s\n" %(source,destination))
    sys.stdout.flush()

    cmd = [os.path.join(show_config.get("publish_user:bin", "/bin"),'wm_cp'),'-R']
    if preserveTime: cmd.append("--preserve=timestamps")
    cmd += [source,destination]
    return subprocess.check_call(cmd)

def cp_file(sources, destination, preserveTime=False):
    sys.stdout.write(">>>>>>>>>>file_utils cp_file source %s destination %s\n" %(sources,destination))
    sys.stdout.flush()

    cmd = [os.path.join(show_config.get("publish_user:bin", "/bin"),'wm_cp')]
    if preserveTime: cmd.append("--preserve=timestamps")
    if isinstance(sources, (str,unicode)): sources = [sources]
    cmd += list(sources)
    cmd.append(destination)
    return subprocess.check_call(cmd)


def chmod_recursive(path):
    prod_root = "%s/prod" %os.environ['NCO_PROJECT_PATH']
    if path.find(prod_root) == 0:
        lock_prod = True
    else:
        lock_prod = False

    prog = os.path.join(show_config.get("publish_user:bin", "/bin"),'wm_chmod')
    mode = get_mode(path,lock_prod=lock_prod)
    if os.path.isdir(path):
        sys.stdout.write(">>>>>>>>>>file_utils chmod_recursive dir %s mode %s\n" %(path,mode))
        sys.stdout.flush()

        cmd = [prog,mode,path]
        result = subprocess.check_call(cmd)
        for root,dirs,files in os.walk(path):
            for d in dirs:
                this_dir = os.path.join(root,d)
                mode = get_mode(this_dir,lock_prod=lock_prod)
                sys.stdout.write(">>>>>>>>>>file_utils chmod_recursive dir %s mode %s\n" %(this_dir,mode))
                sys.stdout.flush()
                cmd = [prog,mode,this_dir]
                subprocess.check_call(cmd)
            for f in files:
                this_file = os.path.join(root,f)
                if os.path.islink(this_file):
                    continue
                mode = get_mode(this_file,lock_prod=lock_prod)
                sys.stdout.write(">>>>>>>>>>file_utils chmod_recursive file %s mode %s\n" %(this_file,mode))
                sys.stdout.flush()
                cmd = [prog,mode,this_file]
                subprocess.check_call(cmd)
    else:
        sys.stdout.write(">>>>>>>>>>file_utils chmod_recursive file %s mode %s\n" %(path,mode))
        sys.stdout.flush()
        cmd = [prog,mode,path]
        result = subprocess.check_call(cmd)
    return 0

def _grouper(n, iterable):
    "_grouper(3, 'ABCDEFG') --> ABC DEF G"
    iterable = iter(iterable)
    while True:
       chunk = tuple(itertools.islice(iterable, n))
       if not chunk:
           return
       yield chunk
       
def chmod_file(path, *paths):
    sys.stdout.write(">>>>>>>>>>file_utils chmod_file path %s\n" %path)
    sys.stdout.flush()
    #mode = get_mode(path)
    #sys.stdout.write(">>>>>>>>>>file_utils chmod_file path %s mode %s\n" %(path,mode))
    #sys.stdout.flush()
    
    # Get mode of each path and group them by each different mode
    assert not isinstance(path, (tuple,list))
    prog = os.path.join(show_config.get("publish_user:bin", "/bin"),'wm_chmod')
    modes = [(get_mode(p), p) for p in [path]+list(paths)]
    modes.sort()
    for mode,pathgrp in itertools.groupby(modes, key=lambda x: x[0]):
        # Make groups of 20 paths at a time, so we don't hit the command line character maximum
        for chunk in _grouper(20, pathgrp):
            cmd = [prog,mode] + sorted([x[1] for x in chunk])
            subprocess.check_call(cmd)
    return 0

def mv(source,destination, isforce=True, noclobber=False):
    sys.stdout.write(">>>>>>>>>>file_utils mv source %s destination %s\n" %(source,destination))
    sys.stdout.flush()

    cmd = [os.path.join(show_config.get("publish_user:bin", "/bin"),'wm_mv')]
    if isforce: cmd.append("-f")
    if noclobber: cmd.append("-n")
    cmd += [source,destination]
    return subprocess.check_call(cmd)

def ln(target,linkname):
    sys.stdout.write(">>>>>>>>>>file_utils ln target %s linkname %s\n" %(target,linkname))
    sys.stdout.flush()

    cmd = [os.path.join(show_config.get("publish_user:bin", "/bin"),'wm_ln'),'-sfn',target,linkname]
    return subprocess.check_call(cmd)

def is_locked(path):
    if os.path.isfile(path):
        return str(os.stat(path).st_uid) == show_config.get('publish_user:uid')
    else:
        if str(os.stat(path).st_uid) != show_config.get('publish_user:uid'):
            return False
        else:
            contents = os.listdir(path)
            for file_path in contents:
                content_path = os.path.join(path,file_path)
                if not is_locked(content_path):
                    return False
            return True

def lock_file(path, preserveTime=True):
    sys.stdout.write(">>>>>>>>>>file_utils lock_file %s\n" %path)
    sys.stdout.flush()
    
    if is_locked(path):
        sys.stdout.write(">>>>>>>>>>file_utils %s already locked\n" %path)
        sys.stdout.flush()
        return 0        
    # Files created by tempfile.mkstemp() will be read/write only by the user, which will make wm_cp
    # unable to read the file. watchman should be in the same group as users, so attempt to make files
    #   u+rw,g+r using the current user, otherwise assume watchman can already read it.
    try:
        # NOT wm_chmod
        info = os.stat(path)
        mode = stat.S_IMODE(info.st_mode)|stat.S_IRUSR|stat.S_IWUSR|stat.S_IRGRP
        os.chmod(path, mode)
    except:
        pass    # If it's still not readable by the publish user (watchman), then cp_file below will fail
        
    tmpPath = "%s.tmp" %path
    try:
        cp_file(path,tmpPath, preserveTime=preserveTime)
        rm_file(path)
        mv(tmpPath,path, isforce=True)
        chmod_file(path)
    except subprocess.CalledProcessError as exc:
        try: rm_file(tmpPath)
        except: pass
        raise FileUtilsErr(exc.returncode, "lock failed: could not %s" %os.path.basename(exc.cmd[0]), path)
    return 0

def lock_dir_recursive(path, preserveTime=True):
    sys.stdout.write(">>>>>>>>>>file_utils lock_dir_recursive %s\n" %path)
    sys.stdout.flush()
    
    if is_locked(path):
        sys.stdout.write(">>>>>>>>>>file_utils %s already locked\n" %path)
        sys.stdout.flush()
        return 0        

    # Files or dirs created by tempfile.mkstemp() will be read/write only by the user, which will make wm_cp
    # unable to read the file. watchman should be in the same group as users, so attempt to make all files
    #   u+rw,g+r using the current user, otherwise assume watchman can already read it.
    #
    # Suppress errors, ignore result, and continue (as long as there is not a traceback from launching the process
    # NOT wm_chmod
    cmd = ["/bin/chmod", "-R", "--silent", "u+rw,g+r", path]
    result = subprocess.call(cmd)
    # If it's still not readable by the publish user (watchman), then cp_recursive below will fail
    
    tmpPath = "%s.tmp" %path
    try:
        cp_recursive(path,tmpPath, preserveTime=preserveTime)
        rm_recursive(path)
        mv(tmpPath,path, isforce=True)
        chmod_recursive(path)
    except subprocess.CalledProcessError as exc:
        try: rm_recursive(tmpPath)
        except: pass
        raise FileUtilsErr(exc.returncode, "lock failed: could not %s: %s" %(os.path.basename(exc.cmd[0]), exc), path)
    return 0

def listdir(path, pattern=None, fullpath=True):
    """
    List the contents of a directory
    @param path The full path to the directory to list.
    @param pattern Optional shell-pattern to apply to listed files.
    @param fullpath If False, only return the basename, as returned by os.path.basename, of each listed item.
    """
    files = glob.glob(path_utils.join(path, "*"))
    if pattern:
        files = fnmatch.filter(files, pattern)

    if not fullpath:
        return [ os.path.basename(x) for x in files ]
    return files

def get_file_versions(filepath_pattern, version_pattern=None, dirs=None):
    """
    Get a list of all versions of a file.
    @param filepath_pattern A path pattern used to search for versions. This should be a glob
    friendly full path.
    For Example if looking for files like below:
    "T:/publish/nut_job/flo/prod/q998/s0030/wip/tnj_q998_s0030_flo_wip_v025.ma"
    Use the pattern:
    "T:/publish/nut_job/flo/prod/q998/s0030/wip/tnj_q998_s0030_flo_wip_*.ma"
    @param version_pattern A version pattern used to extract the version information
    from the filename. This must include a regex group for the version number. The
    default is "v(\d{3})" will find the version pattern "v###"
    @returns a list of version numbers in ascending order.
    """
    version_pattern = version_pattern or "v(\d{3})"
    pattern = re.compile(version_pattern)

    versions = []

    latest_version = None

    files = glob.glob(filepath_pattern)
    for f in files:
        if dirs and not os.path.isdir(f):
            continue

        match = pattern.search(f)
        if match:
            version_number = int(match.groups()[0])
            versions.append((int(match.groups()[0]), f))

    versions.sort(key=lambda x: x[0])

    return versions

def get_latest_file_version(filepath_pattern, version_pattern=None, dirs=None):
    """
    Get the latest version of a file.
    @param filepath_pattern A path pattern used to search for versions. This should be a glob
    friendly full path.
    For Example if looking for files like below:
    "T:/publish/nut_job/flo/prod/q998/s0030/wip/tnj_q998_s0030_flo_wip_v025.ma"
    Use the pattern:
    "T:/publish/nut_job/flo/prod/q998/s0030/wip/tnj_q998_s0030_flo_wip_*.ma"
    @param version_pattern A version pattern used to extract the version information
    from the filename. This must include a regex group for the version number. The
    default is "v(\d{3})" will find the version pattern "v###"
    @returns a list of version numbers in ascending order.
    """
    versions = get_file_versions(filepath_pattern, version_pattern=version_pattern, dirs=dirs)
    if versions:
        return versions[-1]
    return None

def split_versioned_file(filepath, version_pattern=None):
    """
    Split a versioned file into three parts: the prefix leading up to the version,
    the version itself, and the suffix which is everything after the version.
    For Example, given the filepath:
    "T:/publish/nut_job/flo/prod/q998/s0030/wip/tnj_q998_s0030_flo_wip_v025.ma"
    this method would split it into:
    "T:/publish/nut_job/flo/prod/q998/s0030/wip/tnj_q998_s0030_flo_wip", "v025", ".ma"
    @param filepath The full filepath to the file to split.
    @param version_pattern The regex pattern used to split the filepath. It must include
    groups for prefix, version and suffix. If set to None, the routine defaults to "(.*)(v\d{3})(.*)".
    @returns a dictionary containing the keys "prefix", "version" and "suffix". If unable to split
    the filepath, None is returned.
    """
    version_pattern = version_pattern or "(.*)(v\d{3})(.*)"
    match = re.match(version_pattern, filepath)
    if match:
        prefix, version, suffix = match.groups()
        return {"prefix":prefix, "version":version, "suffix":suffix}
    return None

def get_abs_symlinked_file(file_path):
    '''
    Given a file path to a file, return the absolute symlinked target path of the file (i.e. the absolute path to the
    file that the link points to).  If it is not a symlinked file, just return the absolute path to the file.
    @param filepath The full file path to the file
    (e.g. "/mnt/studio/tnj2/publish/assets/chr/andie/sur/palette/chr_andie_sur_palette_default_v000.mtl")
    @return The real path to the given file
    (e.g. /mnt/studio/tnj2/publish/assets/chr/andie/sur/palette/chr_andie_sur_palette_default_v037.mtl)
    '''
    if os.path.islink(file_path):
        file_path = os.path.join(os.path.dirname(os.path.abspath(file_path)), os.path.basename(os.readlink(file_path)))
    else:
        file_path = os.path.join(os.path.dirname(os.path.abspath(file_path)), os.path.basename(file_path))
    return file_path


def is_gzip(filepath):
    """
    Test if a file is gzip compressed or not. Reads the first two byte of the file and
    see if they contain they gzip magic number '\x1f\x8b'.
    """
    with open(filepath, "r") as f:
        if f.read(2) == b'\x1f\x8b':
            gzipped = True
        else:
            gzipped = False
    return gzipped

# more generic search for version whether it is directory or file
def get_any_latest_version(filepath):
#-----------------------------------------------------------------------------------------------------------------------
# Descr: get the list of files sorted to return highest version
# Example root_path: 'C:/tmp/camera/tnj_q287_s0030_showcam_alembicCamera-stereoCameraRight_*.abc'
# or mnt/studio/tnj2/prod/assets/chr/buddy/sur/common/render/images/tt_buddy_*/... for directory

     results = glob.glob(filepath)
     order = sorted(results)
     if len(order)<1:
        return None
     return order[-1]
