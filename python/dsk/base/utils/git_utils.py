"""Base on Location git repo"""
import os
import subprocess
import re

from dsk.base.utils.filesystem_utils import FileSystemUtils
from dsk.base.utils.msg_utils import MsgUtils as log

class GitUtils(object):
    """Class helper to query/clone gitlocation information
    """
    __markertag = re.compile("\(.*\)")

    def __init__(self,repo_location=""):
        super(GitUtils, self).__init__()
        self._repolocation = repo_location

    def is_valid(self):
        if self._repolocation == "":
            return False
        return os.path.isdir(os.path.join(self._repolocation,".git"))

    @staticmethod
    def _get_datetime(astr):
        import datetime
        return datetime.datetime.strptime(astr,'%Y-%m-%d %H:%M:%S')

    @staticmethod
    def _callsubprocess(cmd, git_location):
        """Take command as a list and a git valid git location.. (place with a .git)
        :return:
            a subprocess descriptor
        """
        return subprocess.Popen(cmd,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT,
                                cwd=git_location,
                                close_fds=True)

    @staticmethod
    def _getresult(p, cmd):
        """
            :return:
                empty string if failed,
        """
        if p.wait() != 0:
            print(["ERROR: %s" % " ".join(cmd)])
            return [""]
        result = p.stdout.readlines()
        p.stdout.close()
        return [x.rstrip() for x in result] # remove the character return

    @staticmethod
    def _clean_tab(result):
        """clean return format with no tab
        """
        return [x.replace("\t"," ") for x in result]

    def get_git_version(self):
        """Helper to extract tag version
        """
        if not self.is_valid():
            return list()
        cmd = list()
        cmd.extend(['git', 'describe','--abbrev=0','--tags'])
        p = self._callsubprocess(cmd, self._repolocation)
        result = self._getresult(p, cmd)
        res = result[0].rstrip()
        if res.startswith('fatal'):
            return "NONE"
        return res

    def create_tag(self, tag):
        """Helper to extract tag version
        """
        if not self.is_valid():
            return list()
        cmd = list()
        cmd.extend(['git', 'tag', tag])
        p = self._callsubprocess(cmd, self._repolocation)
        result = self._getresult(p, cmd)
        return result

    def push_tag(self, tag):
        """Helper to extract tag version
        """
        if not self.is_valid():
            return list()
        cmd = list()
        cmd.extend(['git', 'push','origin',tag])
        p = self._callsubprocess(cmd, self._repolocation)
        return self._getresult(p, cmd)

    def get_git_name(self):
        """Helper to extract root repo name
        """
        if not self.is_valid():
            return list()
        cmd = list()
        cmd.extend(['git','remote','-v'])
        p = self._callsubprocess(cmd, self._repolocation)
        result = self._getresult(p, cmd)
        result = self._clean_tab(result)
        result = result[0].rstrip().split(" ")
        result = result[1].split("/")
        for i in result:
            if '.git' in i:
                return i.replace(".git","")
        return "no-git-name-founded"

    def get_git_date(self, max_log):
        """Helper to extract history date from log
        :return:
            alist of date up to max log:  format each list YYYY-MM-DD hh:mm:ss
        """
        if not self.is_valid():
            return list()
        cmd = list()
        cmd.extend(['git','log',"-%d" % max_log ,'--format=%ci','--date=local'])
        p = self._callsubprocess(cmd, self._repolocation)
        return self._getresult(p, cmd)

    def get_git_log_raw(self, max_log):
        """Helper to retrieve tag version
            :return:
                Return a list of list with 3 elmts: sha dateobj and tags
        """
        if not self.is_valid():
            return list()
        cmd = list()
        cmd.extend(['git', 'log','-%d' % max_log,'--pretty=format:"%h %ci %an %d"'])
        p = self._callsubprocess(cmd, self._repolocation)
        return self._getresult(p, cmd)

    def get_git_log(self, max_log):
        """Helper to retrieve tag version
            :return:
                Return a list of list with 4 elmts: sha dateobj tags is_head
        """
        if not self.is_valid():
            return list()
        cmd = list()
        cmd.extend(['git', 'log','-%d' % max_log,'--pretty=format:"%h %ci %an %d"'])
        p = self._callsubprocess(cmd, self._repolocation)
        result = self._getresult(p, cmd)
        final = list()
        for r in result:
            ttag = None
            m = self.__markertag.search(r)
            if m:
                ttag = m.group()[1:-1].split()
                ttag = [x.replace(",","") for x in ttag]
                if len(ttag) == 2:
                    ttag = ttag[1]
                    rs = r.split()
                    rt = rs[1:3]
                    objdt = self._get_datetime(" ".join(rt))
                    final.append([ttag, objdt, rs[0][1:], False]) # false for head
                elif len(ttag) > 3:
                    is_head = False
                    for i,x in enumerate(ttag):
                        if x == 'HEAD':
                            is_head = True
                        if x == 'tag:':
                            ntag = ttag[i+1]
                            rs = r.split()
                            rt = rs[1:3]
                            objdt = self._get_datetime(" ".join(rt))
                            final.append([ntag, objdt, rs[0][1:], is_head])
                            break

        return final


    def install_repo_from_bash(self, src_repo, release_place, rootname, tag):
        """Run a git bash script
        """
        if not self.is_valid():
            return list()
        from dsk import ModuleBin
        cmd = list()
        cmd.append("%s/update_repo_app_local.bsh" % ModuleBin)
        cmd.append(src_repo)
        cmd.append(release_place)
        cmd.append(rootname)
        cmd.append(tag)
        p = self._callsubprocess(cmd, self._repolocation)
        result = self._getresult(p, cmd)
        return result

    @staticmethod
    def get_temp_git_clone_place_dir():
        """Return a unique temp clone area
        :return:
            a valid unique tmp dir
        """
        import tempfile
        import uuid
        clone_tmp = os.path.join(tempfile.gettempdir(),
                                 "repo_clone_%s" % uuid.uuid4().hex)
        FileSystemUtils.ensure_folder_exists(clone_tmp)
        return clone_tmp

    def get_temp_zone(self, relative_destination):
        """A convenient location to retrieve root repo
        """
        return os.path.join(self._repolocation, relative_destination)


    def clone_repo(self, repo_name, dest, branch=""):
        """This function is not checking the validity of self

            :param repo_name: (str) a valid git address
                              relative_destination: (str) folder under _repolocation
            :param dest: where to clone the repo
            :param branch: optional branch name
            :return: return log of the git call

        """

        cmd = ['git']
        if branch != "":
            cmd.append("-b %s" % branch)
        cmd.extend(["clone", repo_name])
        if dest != "":
            cmd.append(dest)
        log.info("Cloning: %s" % " ".join(cmd))
        p = self._callsubprocess(cmd, self._repolocation)
        result = self._getresult(p, cmd)
        return result

    def fetch_repo(self, repo_name, dest, branch=""):
        """This function is not checking the validity of self

            :param repo_name: (str) a valid git address
                              relative_destination: (str) folder under _repolocation
            :param branch: optional branch name
            :return: return log of the git call

        """

        cmd = ['git']
        if branch != "":
            cmd.append("-b %s" % branch)
        cmd.extend(["fetch", repo_name])
        log.info("fetch: %s" % " ".join(cmd))
        p = self._callsubprocess(cmd, self._repolocation)
        result = self._getresult(p, cmd)
        return result

    def pull_repo(self, repo_name, dest, branch=""):
        """This function is not checking the validity of self

            :param repo_name: (str) a valid git address
                              relative_destination: (str) folder under _repolocation
            :param branch: optional branch name
            :return: return log of the git call

        """

        cmd = ['git']
        if branch != "":
            cmd.append("-b %s" % branch)
        cmd.extend(["pull", repo_name])
        log.info("fetch: %s" % " ".join(cmd))
        p = self._callsubprocess(cmd, self._repolocation)
        result = self._getresult(p, cmd)
        return result

