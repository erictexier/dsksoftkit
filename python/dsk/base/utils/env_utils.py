import os

####################################
class EnvUtils(object):
    ##################
    _OSKEY = frozenset(["OS",
                        "OSV",
                        "OSTYPE",
                        "BETAOSV",
                        "SHELL",
                        "MACHTYPE",
                        "HOST",
                        "HOSTTYPE",
                        "HOSTNAME",
                        "LOCALPATH",
                        "LOCALPREPATH",
                        "SESSION_MANAGER",
                        "VENDOR",
                        "GDMSESSION",
                        "WINDOWID",
                        "XAUTHORITY",
                        "LS_COLORS"])

    @staticmethod
    def remove_machine_dependent_env(adict):
        for i in EnvUtils._OSKEY():
            if i in adict:
                adict.pop(i)

    @staticmethod
    def split_env(anEnv):
        if anEnv in os.environ:
            allPath = os.environ[anEnv]
            return allPath.split(os.pathsep)
        return list()

    @staticmethod
    def build_set_env_cmd(asExport = True, clean=False):
        """ serialize the cmd to setenv or export
        """
        cd = dict()
        if clean == True:
            for i in os.environ:
                if not i.startswith("_"):
                    cd[i] = os.environ[i]
        else:
            cd = os.environ
        if asExport:
            return '\n'.join(['export %s=%s'%(key,value) for key,value in list(cd.items())])+'\n'
        else:
            return '\n'.join(['setenv %s %r'%(key,value) for key,value in list(cd.items())])+'\n'
    '''
    def init_file_system(self, try_install_config = False):
        """Deal with resources not done
        for now, just deal with the debug as the config are local
        """
        global DEBUG_INIT
        if DEBUG_INIT or try_install_config:
            EnviUtils.create_path_rec(self.base_pack())
            EnviUtils.create_path_rec(self.base_config())
            print ("created",self.base_config())
    '''