import sys
import getpass

from dskenv.api.envi_api import EnviApi
from dsk.base.utils.log_utils import MsgUtils as log

class EnviInfoHelper(object):
    """This class helps to write update envi_file with new user and new repo
       It also provide with an api to control write/read permission



        :note : yaml write will cause an reformating and lost of comment that
                we want to avoid for clarity
    """
    @staticmethod
    def add_user(file_location, afile, newu):
        """Insert a new user in envi_info file

            :param file_location: file to copy from
            :param afile: new created file
            :param newu:  a DevUser object

            :return True:
        """
        with open(afile, "w") as fout:
            with open(file_location, "rt") as fin:
                for line in fin.readlines():
                    if line.strip() == "dev_user:":
                        fout.write(line)
                        newu.write(fout)
                        fout.write("\n")
                    else:
                        fout.write(line)
        return True

    @staticmethod
    def add_repo(file_location, afile, newrepo):
        """Insert a new user in envi_info file

            :param file_location: file to copy from
            :param afile: new created file
            :param newu:  a RepoInstall object
            :return True:

        """
        with open(afile, "w") as fout:
            with open(file_location, "rt") as fin:
                for line in fin.readlines():
                    if line.strip() == "repo_info:":
                        fout.write(line)
                        newrepo.write(fout)
                        fout.write("\n")
                    else:
                        fout.write(line)
        return True

    @staticmethod
    def is_write_permitted(a_top_root):
        api = EnviApi()
        api.reset(a_top_root)
        log.info("Loading %s as user %s" % (a_top_root,getpass.getuser()))
        api.load_data()
        if not api.is_valid():
            log.error("This is not a valid config %s" % a_top_root)
            return False
        varea = api.get_userdev_config_path(getpass.getuser())
        log.info("is_write_permitted: Checking if %s in %s\n" % (a_top_root," ".join(varea)))
        if a_top_root in varea:
            return True
        return False
