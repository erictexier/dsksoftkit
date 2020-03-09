import os
import sys
import string
import shutil
import stat
import time

from dsk.base.utils.msg_utils import MsgUtils
######
readwrite=0o777
####################################
class DiskUtils:
    # need some work for error

    ##################
    @staticmethod
    def is_file_exist(fullName):
        return os.path.isfile(fullName)

    ##################
    @staticmethod
    def is_link(fullName):
        return os.path.islink(fullName)

    ##################
    @staticmethod
    def is_dir_exist(fullName):
        return os.path.isdir(fullName)

    ##################
    # a way to extract the prefix from a directory name
    # find the global ROOT
    @staticmethod
    def get_directory_in_common(pathNameList):
        """ return a string representing the common path
        to all files'
        """

        if len(pathNameList) == 1:
            if DiskUtils.is_file_exist(pathNameList[0]):
                return os.path.dirname(pathNameList[0])
            else:
                return pathNameList[0]
        cleanList = []
        for i in pathNameList:
            if len(i) > 0:
                if i[-1] != os.sep:
                    cleanList.append(i+os.sep)
                else:
                    cleanList.append(i)

        root = os.path.commonprefix(cleanList)
        if len(root) > 0 and root[-1] != os.sep:
            # we need to back track one level
            index = root.rfind(os.sep)
            if index != -1:
                root = root[:index] + os.sep
        return root

    ##################
    @staticmethod
    def remove_file(fullName):
        return os.remove(fullName)

    ##################
    @staticmethod
    def remove_dir(fullName):
        return os.rmdir(fullName)

    ##################
    @staticmethod
    def move_file(fromFile, toFile):
        return shutil.move(fromFile,toFile)

    ##################
    @staticmethod
    def rename_file(fromFile, toFile):
        return os.rename(fromFile,toFile)

    ##################
    @staticmethod
    def copy_file(fromFile, toFile):
        return shutil.copyfile(fromFile,toFile)

    ##################
    @staticmethod
    def make_path_name(path, fileName):
        tempName = os.path.join(path,fileName)
        return os.path.normcase(tempName)

    ##################
    @staticmethod
    def get_right_sep(fullPath):
        return string.replace(fullPath,"\\",os.sep)

    ##################
    # create the physical Path
    @staticmethod
    def create_path(fullPath):
        try:
            os.mkdir(fullPath,0o775)
            return True
        except:
            MsgUtils.msg("Cannot create %r" % fullPath)
            return False

    ##################
    # create the physical Path recursively
    @staticmethod
    def create_path_rec(fullPath):
        """Create all the needed directory
        if an extension exist will not considered the last field as a dir but as a filename
        """
        if DiskUtils.is_dir_exist(fullPath):
            return True
        p,ext = os.path.splitext(fullPath)
        toCreate = ""
        if ext != "":
            # the last field is file we will not create it as a directory
            toCreate = os.path.split(p)[0]
        else:
            toCreate = p

        # build the parent directory
        par = os.path.split(toCreate)[0]
        if DiskUtils.create_path_rec(par):
            if not DiskUtils.is_dir_exist(toCreate):
                DiskUtils.create_path(toCreate)
        return True

    ##################
    @staticmethod
    def get_file_size(fullPath):
        file_stats = ""
        try:
            file_stats = os.stat(fullPath)
        except:
            return ""
        return "%0.3fM"% (file_stats [stat.ST_SIZE]/1000000.)

    ##################
    @staticmethod
    def get_file_owner(fullPath):
        file_stats = ""
        userinfo = None
        try:
            import pwd
            file_stats = os.stat(fullPath)
            userinfo = pwd.getpwuid(file_stats[stat.ST_UID])
        except:
            return ""
        if userinfo:
            return userinfo[0]
        return ""


    ##################
    @staticmethod
    def compare_time_file(f1,f2):
        # need for sure more work
        """ return a tuple (success= bool, timediff = time(f1) - time(f2))
        """
        try:
            # check if they exist for sanity
            os.stat(f1)[stat.ST_MODE]
            os.stat(f2)[stat.ST_MODE]
        except:
            # file do not exist
            return (False,0)

        f1 = os.stat(f1)[stat.ST_MTIME]
        f2 = os.stat(f2)[stat.ST_MTIME]
        return (True,f1 - f2)

    ##################
    @staticmethod
    def sort_files(listOfFile,mostRecentFirst=True):
        """ list of for file on disk, if file or directory do not exist they will be dropped
        """
        from operator import itemgetter
        a = [(DiskUtils.get_time(x),x) for x in listOfFile]
        return list(map(itemgetter(1),sorted(a,reverse=mostRecentFirst)))

    ##################
    @staticmethod
    def clip_time_files(listOfFile,atime):
        """ list of for file on disk, if file or directory do not exist they will be dropped
        """
        return [x for x in listOfFile if DiskUtils.get_time(x) < atime]

    ##################
    @staticmethod
    def clip_time_files_sorted(listOfFile, atime):
        """ list of for file on disk, if file or directory do not exist they will be dropped
        """
        a = [(DiskUtils.get_time(x),x) for x in listOfFile]
        b = sorted(a,reverse=False)
        res = list()
        for i in b:
            if i[0] <= atime:
                res.append(i[1])
            else:
                break
        return res

    ##################
    @staticmethod
    def get_time(aFile):
        try:
            return os.stat(aFile)[stat.ST_MTIME]
        except:
            return -sys.maxsize

    ##################
    @staticmethod
    def get_file_time(aFile):
        """ last change
        """
        try:
            return time.ctime(os.path.getctime(aFile))
        except:
            pass
        return ""

    ##################
    @staticmethod
    def get_file_last_access(aFile):
        """ last access
        """
        try:
            return time.ctime(os.path.getatime(aFile))
        except:
            pass
        return ""

    ##################
    @staticmethod
    def get_file_last_modification(aFile):
        """ last modification
        """
        try:
            return time.ctime(os.path.getmtime(aFile))
        except:
            pass
        return ""

    ##################
    @staticmethod
    def cleanpath(apath):
        # not done
        return apath.replace("\\", "/")

    ##################
    @staticmethod
    def get_sub_dir_content(parentdir):
        """ return the content of a directory with full name
        """
        ch = list()
        if os.path.isdir(parentdir):
            ch = os.listdir(parentdir)
        return [os.path.join(parentdir,x) for x in ch]

    ##################
    @staticmethod
    def get_sub_dir(parentdir):
        content = DiskUtils.get_sub_dir_content(parentdir)
        result = list()
        for x in content:
            if os.path.isdir(x):
                result.append(x)
        return result

    ##################
    @staticmethod
    def get_empty_sub_dir(parentdir):
        content = DiskUtils.get_sub_dir_content(parentdir)
        result = list()
        for x in content:
            cc = DiskUtils.get_sub_dir_content(x)
            if len(cc) == 0:
                result.append(x)
        return result