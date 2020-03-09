import os
import sys
import re
import tempfile
import uuid
from collections import namedtuple

from dsk.base.utils.git_utils import GitUtils
from dsk.base.utils.msg_utils import MsgUtils as log
from dskenv.pack_info import PackInfo
from dsk.base.lib.base_fileproc import BaseFileProc
from dsk.base.lib.base_fileproc import ResultFileProc
from dskenv.versioned_dir import DirVersioned
from dskenv.version_helper import VersionHelper
from dsk.base.utils.filesystem_utils import FileSystemUtils


class ResultRepoInstall(namedtuple('repoinst', "success errors log tagname")):
    __slots__ = ()

class RepoApi(object):
    __pat_release = re.compile("base_release\s*=")
    __pat_version = re.compile("version\s*=")
    __pat_version_repo = re.compile("version_repo\s*=")

    def __init__(self, src_repo):
        self.src_repo = src_repo

    def install(self,
                release_top_location,
                branch="",
                do_version = False,
                new_version = False):
        """Clone an accessible remote git address to a top location by using
            name and tag to build the install area

            :param    release_top_location: (str existing branch)  a place to install
            :param    branch: (str)  an optional existing branch
            :param do_version: add a tag
            :param new_version: when do_version is incremental try to incremenent
            :returns ResultRepoInstall: success errors log atag

        """

        if not os.path.isdir(release_top_location):
            log.error("release area needs to exist, %s doen't" % release_top_location)
            return False

        tempdir = GitUtils.get_temp_git_clone_place_dir()
        x = GitUtils(tempdir)
        tempdest = x.get_temp_zone("REPO")

        res = ""
        try:
            #The repo gets clone in this function
            res = x.clone_repo(self.src_repo, tempdest, branch)
        except Exception as e:
            log.error(str(e))
            return ResultRepoInstall(False,[str(e)],None)

        if isinstance(res,str):
            res = [res]

        for r in res:
            if 'fatal' in r: # most likely to belong to the output in case of failure
                return ResultRepoInstall(False,res,"")

        if new_version == True and do_version == True and branch == "":
            # query tag, increment pach tag, push tag
            self._push_new_version(tempdest)

        # copy the temp repo contain in the release area
        res = self._copy_versionned_to_area(tempdest, release_top_location, branch,do_version)
        return res

    def _push_new_version(self, gitrepo):
        """ Query, increment tag and push to remote repo
        """
        x = GitUtils(gitrepo)
        ver = x.get_git_version()
        if ver in ["","NONE"]:
            ver = "v0.0.0"
        else:
            verob = DirVersioned(ver)
            if verob.is_valid():
                verob.inc_patch()   # need an argument for minor
                ver = verob.format()
        glog = x.get_git_log(20)
        # we only push if head is not tagged
        do_tag = True

        for l in glog:
            log.info("log check for HEAD %s" % l)
            if l[-1] == True:
                log.warning("HEAD is already tag, will not create new tag")
                do_tag = False
                break
        if do_tag:
            x.create_tag(ver)
            x.push_tag(ver)
            log.info("new tag will be created: %r" % x.get_git_version())

    def _copy_versionned_to_area(self, source, dest_release, branch, do_version):
        """Source is a repo clone area
           dest_release is an existing direct to which the name of the repo name and the
           version will be copied under   dest_release/tools_name/v?.?.?

            :paramsource: a valid git place (with a .git directory)
            :param dest_release
            :return ResultRepoInstall:

        """

        # Check that source has all the criteria
        x = GitUtils(source)
        if not x.is_valid():
            errors = ["Not a valid git:{}".format(source)]
            return ResultRepoInstall(False, errors,['copy_versionned_to_area.source'],None)
        name = x.get_git_name()
        if name == "":
            errors = ["Not a valid name:{}".format(name)]
            return ResultRepoInstall(False, errors,['copy_versionned_to_area.name'],None)

        atag = ""
        if do_version:
            atag = branch
            if branch == "":
                atag = x.get_git_version()
                if atag == "":
                    errors = ["Not a valid tag:{}".format(atag)]
                    return ResultRepoInstall(False, errors,['copy_versionned_to_area.tag'],None)

        elif branch != "": # branch willbe in subdirectory
            atag = branch

        todolist = BaseFileProc()
        todolist.copy_folder_release(source, dest_release, name, atag)
        res = todolist.execute_stop_first_failed()
        if res.success == False:
            return ResultRepoInstall(False, res.errors,res.log, None)
        return ResultRepoInstall(True, res.errors, res.log, atag)

    def lastest_install(self,
                        release_top_location,
                        repo,
                        doversion):
        errors = log = list()
        apath = os.path.join(release_top_location,repo)
        if doversion == False:
            return ResultRepoInstall(False, errors, log, None)

        all_vers = list()
        try:
            all_vers = os.listdir(apath)
        except:
            pass
        all_vers = [DirVersioned(x) for x in all_vers]
        all_vers = [x for x in all_vers if x.is_versioned()]
        all_vers = sorted(all_vers,DirVersioned.compare_version)

        if len(all_vers) > 0:
            return ResultRepoInstall(True, errors, log, all_vers[-1].format())
        return ResultRepoInstall(False, errors, log, None)


    def simple_clone(self,
                     release_top_location,
                     branch=""):

        """Clone an accessible remote git address to a top location

            :param release_top_location: (str existing branch)  a place to install
            :param branch: (str)  an optional existing branch
            :return ResultRepoInstall: success errors log atag
        """

        if not os.path.isdir(release_top_location):
            log.error("release area needs to exist, %s doen't" % release_top_location)
            return False

        x = GitUtils(release_top_location)

        try:
            #The repo gets clone in this function
            x.clone_repo(self.src_repo, "", branch)
        except Exception as e:
            log.error(str(e))
            return ResultRepoInstall(False,[str(e)],['failed simple_clone'],None)


        return ResultRepoInstall(True,["no error"],['done simple_clone'],None)


    def pack_commit(self,
                    fromdir,
                    todir,
                    packname,
                    top_release_path,
                    repo_name,
                    version,
                    with_version=True):

        """

        :param fromdir: (str path) an envi user_place ex: BaseEnv.user_home('eric')
        :param todir: (str path)  an envi release place ex: BaseEnv.base()
        :param packname: (str) the name of the pack
        :param top_release_path: (str path) the release area of all repo:
                              ex: /mnt/dev/${USER}/packages
        :param repo_name: (str)  dir name of the repo. ex: mgtk-multi-setuptools
        :param version:   (str)  version ex: v0.0.8
        :param with_version=True  NOT DONE
        :return ResultFileProc:

        """

        if not os.path.isdir(todir):
            return ResultFileProc(False, ["Doesn't exist %s" % todir],[], None)


        searchPath1 = [todir]
        if not isinstance(fromdir,list):
            searchPath2 = [fromdir]
        else:
            searchPath2 = fromdir

        fromFile = toFile = ""

        pi = PackInfo(packname)
        rcHome = pi.real_version_file(PackInfo,searchPath2)
        if rcHome != None:
            fromFile = rcHome.get_fullname()
        else:
            rcRelease = pi.real_version_file(PackInfo,searchPath1)
            if rcRelease == None:
                err = "Cannot find a valid pack {}".format(packname)
                log.error(err)
                return ResultFileProc(False, [err],[], None)
            fromFile = rcRelease.get_fullname()

        # build up the new pack file
        release_path = ""
        tmp = os.path.join(tempfile.gettempdir(), "pack_%s" % uuid.uuid4().hex)
        foundR = foundV = False
        with open(fromFile, "rt") as fin:
            with open(tmp, "wt") as fout:
                for line in fin:
                    if foundR and foundV:
                        fout.write(line)
                        continue
                    m = self.__pat_release.search(line)
                    if m and m.start() == 0:
                        release_path = os.path.join(top_release_path,repo_name)
                        fout.write('base_release = "%s"\n' % release_path)
                        foundR = True
                    else:
                        m = self.__pat_version.search(line)
                        if m and m.start() == 0:
                            fout.write('version = "%s"\n' % version)
                            foundV = True
                        else:
                            m = self.__pat_version_repo.search(line)
                            if m and m.start() == 0:
                                fout.write('version_repo = "%s"\n' % version)
                                foundV = True
                            else:
                                fout.write(line)


        todolist = BaseFileProc()
        rcRelease = pi.real_version_file(PackInfo,searchPath1)
        if rcRelease == None:
            rcHome.version_up_minor()
            toFile = rcHome.get_fullname()
            # repath
            toFile = toFile.replace(searchPath2[0],searchPath1[0])
            if not with_version:
                x = VersionHelper(toFile)
                x.unversioned()
                toFile = x.format()
            todolist.copy_envifile(tmp, toFile)

        else:
            rcRelease.version_up_minor()
            toFile = rcRelease.get_fullname()
            if not with_version:
                x = VersionHelper(toFile)
                x.unversioned()
                toFile = x.format()
            todolist.copy_envifile(tmp, toFile)

        log.info("Creating new pack from: {} to: {}".format(fromFile,toFile))

        todolist.delete_file(tmp)
        res_copy = todolist.execute_stop_first_failed(run_dry=False,
                                                      with_log = True)
        return res_copy

    def pack_checkout(self,
                      fromdir,
                      todir,
                      packname,
                      dev_path,
                      repo_name):
        """Create a packname in user area

        :param    fromdir: (str path)  an envi release place ex: BaseEnv.base()
        :param    todir: (str path) an envi user_place ex: BaseEnv.user_home('eric')
        :param    packname: (str) the name of the pack
        :param    dev_path: (str path) top dev user git area
                              ex: /mnt/dev/${USER}/packages
                              (see: $DSKENV/configs_and_packs/envi_info.yml)
        :param    repo_name: (str) dir name of the repo. ex: mgtk-multi-setuptools
        :returns ResultFileProc:

        """
        if not os.path.isdir(todir):
            new_user_pack_area = os.path.join(todir,PackInfo.get_label())

            FileSystemUtils.ensure_folder_exists(os.path.dirname(new_user_pack_area),
                                                 permissions=0o775)

            log.info("create a user pack area in {}".format(new_user_pack_area))

        if not os.path.isdir(todir):
            return ResultFileProc(False, ["Doesn't exist %s" % todir],[], None)

        searchPath1 = [fromdir]
        searchPath2 = [todir]


        pi = PackInfo(packname)
        tmp = os.path.join(tempfile.gettempdir(), "pack_%s" % uuid.uuid4().hex)

        todolist = BaseFileProc()
        # build up the new pack file
        rcRelease = pi.real_version_file(PackInfo,searchPath1)
        if rcRelease != None:
            toFile = os.path.join(searchPath2[0],pi.get_label(),packname+".py")
            fromFile = rcRelease.get_fullname()

            foundR = foundV = False

            with open(fromFile, "rt") as fin:
                with open(tmp, "wt") as fout:
                    for line in fin:
                        if foundR and foundV:
                            fout.write(line)
                            continue
                        m = self.__pat_release.search(line)
                        if m:
                            x = line.split("=")[1]
                            x = x.strip()
                            x = x.split(os.sep)[-1]
                            x = x.replace("'","")
                            x = x.replace('"',"")
                            source_dev_path = os.path.join(dev_path,x)
                            fout.write("base_release = %r\n" % source_dev_path)
                            foundR = True
                        else:
                            m = self.__pat_version.search(line)
                            if m:
                                fout.write('version = ""\n')
                                foundV = True
                            else:
                                m = self.__pat_version_repo.search(line)
                                if m:
                                    fout.write('version_repo = ""\n')
                                    foundV = True
                                else:
                                    fout.write(line)

            todolist.copy_envifile(tmp, toFile)
            todolist.delete_file(tmp)
        else:
            # make a blank
            from dsk.templates.template_envi import repo_pack
            toFile = os.path.join(searchPath2[0],pi.get_label(),packname+".py")

            data = repo_pack.DATA_PACK % {'rootname': os.path.join(dev_path,repo_name)}
            with open(tmp, "wt") as fout:
                fout.write(data)
            todolist.copy_envifile(tmp, toFile)
            todolist.delete_file(tmp)

        res_copy = todolist.execute_stop_first_failed(run_dry=False, with_log = True)
        return res_copy


    @classmethod
    def get_version_path(cls, afile):
        """Some utils to get version when properly formatted

            :param afile: a config or pack file
            :returns: "" if not found, the version otherwise (ex: v0.0.10)
        """

        with open(afile, "rt") as fin:
            for line in fin:
                m = RepoApi.__pat_version.search(line)
                if m and m.start() == 0:
                    return line[m.end():].strip()
                    break
                m = RepoApi.__pat_version_repo.search(line)
                if m and m.start() == 0:
                    return line[m.end():].strip()
                    break

        return ""

    @classmethod
    def get_release_path(cls, afile):
        """Some utils to get release path when properly formatted

            :param afile: a config or pack file
            :returns: "" if not found, the release path otherwise /u/release...

        """
        with open(afile, "rt") as fin:
            for line in fin:
                m = RepoApi.__pat_release.search(line)
                if m and m.start() == 0:
                    return line[m.end():].strip()
                    break
        return ""

    @classmethod
    def get_description_path(cls, afile):
        """Some utils to get release path and version when properly formatted

            :param afile: a config or pack file
            :returns: "","" if not found, the release path, version otherwise
                      ex: ('/u/beta/newEnv/released/reponame', 'v0.0.20')

        """
        rel = ver = ""
        with open(afile, "rt") as fin:
            for line in fin:
                m = RepoApi.__pat_release.search(line)
                if m and m.start()==0:
                    rel = line[m.end():].strip()
                else:
                    m = RepoApi.__pat_version.search(line)
                    if m and m.start()==0:
                        ver = line[m.end():].strip()
                    else:
                        m = RepoApi.__pat_version_repo.search(line)
                        if m and m.start()== 0:
                            ver = line[m.end():].strip()

                if rel != "" and ver != "":
                    return rel.replace("'","").replace('"',""), ver.replace("'","").replace('"',"")
        return rel,ver
