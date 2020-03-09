import os
import sys
from collections import namedtuple

from dsk.base.utils.filesystem_utils import FileSystemUtils
from dskenv.proxy_env import ProxyEnv
from dsk.base.utils.msg_utils import MsgUtils as log

class ResultFileProc(namedtuple('fpinfo', "success errors log result")):
    __slots__ = ()

#####################
class mxinfocopy(object):
    def run(self, with_log, run_dry):
        log_info = ['mxinfocopy']
        if with_log:
            log_info.append("Copy File {} {}".format(self.parm1,self.parm2))
        try:
            if run_dry == False:
                FileSystemUtils.copy_file(self.parm1, self.parm2, self.mode)
            success = True
            errors = []
        except Exception as e:
            log.error(str(e))
            success = False
            errors = [str(e)]
        return ResultFileProc(success, errors, log_info, None)

class pinfocopyfile(namedtuple('cfinfo', "parm1 parm2 mode"),mxinfocopy):
    __slots__ = ()

#####################
class mxinfocreatedir(object):
    def run(self, with_log, run_dry):
        log_info = ['mxinfocreatedir']
        if with_log:
            log_info.append("ensure_folder_exists {}".format(self.parm1))
        try:
            if run_dry == False:
                FileSystemUtils.ensure_folder_exists(self.parm1, self.mode)
            success = True
            errors = []
        except Exception as e:
            log.error(str(e))
            success = False
            errors = [str(e)]
        return ResultFileProc(success, errors, log_info, None)

class pinfocreatedir(namedtuple('crdirinfo', "parm1 mode"),mxinfocreatedir):
    __slots__ = ()

#####################
class mxinfocreate_userdev(object):
    def run(self, with_log, run_dry):
        log_info = ['mxinfocreate_userdev']
        x = None
        if with_log:
            log_info.append("ProxyEnv({})".format(self.parm1))
        try:
            if run_dry == False:
                x = ProxyEnv(self.parm1)
            success = True
            errors = []
        except Exception as e:
            log.error(str(e))
            success = False
            errors = [str(e)]
        return ResultFileProc(success, errors, log_info, x)

class pinfocreate_userdev(namedtuple('cudinfo', "parm1"),
                          mxinfocreate_userdev):
    __slots__ = ()



#####################
class mxinfocopy_folder_release(object):
    def run(self, with_log, run_dry):
        log_info = ['copy_folder_release']
        x = None
        if with_log:
            log_info.append("copy_folder_release: {} {}".format(self.parm1,self.parm2))
        try:
            if run_dry == False:
                FileSystemUtils.copy_folder(self.parm1,
                                            self.parm2,
                                            folder_permissions=self.mode,
                                            skip_list=None)
            success = True
            errors = []
        except Exception as e:
            log.error(str(e))
            success = False
            errors = [str(e)]
        return ResultFileProc(success, errors, log_info, x)

class pinfocopy_folder_release(namedtuple('cpyfldinfo', "parm1 parm2 mode"),
                               mxinfocopy_folder_release):
    __slots__ = ()


#####################
class mxinfosafe_delete_file(object):
    def run(self, with_log, run_dry):
        log_info = ['safe_delete_file']
        x = None
        if with_log:
            log_info.append("safe_delete_file: {}".format(self.parm1))
        try:
            if run_dry == False:
                FileSystemUtils.safe_delete_file(self.parm1)
            success = True
            errors = []
        except Exception as e:
            log.error(str(e))
            success = False
            errors = [str(e)]
        return ResultFileProc(success, errors, log_info, x)

class pinfosafe_delete_file(namedtuple('sdelfileinfo', "parm1"),
                            mxinfosafe_delete_file):
    __slots__ = ()


readwritesafe = 0o664
readwrite = 0o666
readwritedir = 0o775

#####################

class BaseFileProc(object):
    """A list of 'things' to do in a list to execute them later """
    def __init__(self):
        self._exec = list()

    def copy_envifile(self, parm1, parm2, mode=readwrite):
        self._exec.append(pinfocopyfile(parm1, parm2, mode))

    def delete_file(self, parm1):
        self._exec.append(pinfosafe_delete_file(parm1))

    def create_dir(self, parm1, mode=readwritedir):
        self._exec.append(pinfocreatedir(parm1, mode))

    def create_userdev(self, parm1):
        """A possible config_pack"""
        self._exec.append(pinfocreate_userdev(parm1))

    def copy_files_from_config_pack(self, parm1, parm2, mode=readwritesafe):
        """Assume parm1 and parm2 exists as dir and have config and pack"""

        apath_from = os.path.join(parm1, ProxyEnv.config_tag())
        apath_to   = os.path.join(parm2, ProxyEnv.config_tag())
        try:
            allconfig = os.listdir(apath_from)
            for x in allconfig:
                self.copy_envifile(os.path.join(apath_from,x),
                                   os.path.join(apath_to,x),
                                   mode=0o664)
        except:
            pass
        apath_from = os.path.join(parm1,ProxyEnv.pack_tag())
        apath_to = os.path.join(parm2,ProxyEnv.pack_tag())
        try:
            allpack = os.listdir(apath_from)
            for x in allpack:
                self.copy_envifile(os.path.join(apath_from,x),
                                   os.path.join(apath_to,x),
                                   mode=0o664)
        except:
            pass

    def copy_folder_release(self, source, dest_release, name, atag, mode=readwritedir):
        """Build release/gitprojectname/atag as a destination to copy the project
            :return:
               the path of the directory where the will be copied
        """
        root_proj = os.path.join(dest_release,name)
        self.create_dir(root_proj)
        if atag != "":
            root_proj = os.path.join(root_proj,atag)
            self.create_dir(root_proj)
        self._exec.append(pinfocopy_folder_release(source, root_proj, mode))
        return root_proj

    #########
    def execute_stop_first_failed(self, with_log=False, run_dry=False):
        result = list()
        if len(self._exec) == 0:
            return ResultFileProc(True,[],['nothing to do'],[])
        for an_exec in self._exec:
            res = an_exec.run(with_log, run_dry)
            result.append(res)
            if res.success == False:
                break

        return ResultFileProc(self._is_all_success(result),  # bool
                              result[-1].errors if len(result) > 0 else [],
                              self._get_log(result),
                              [x.result for x in result])

    def _get_log(self,result):
        a = ['execute_stop_first_failed']
        for x in result:
            a.append(x.log)
        return a

    def _is_all_success(self, result):
        if len(result) != len(self._exec) or len(result) == 0:
            return False
        return result[-1].success
