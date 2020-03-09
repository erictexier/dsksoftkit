import os
import sys
if sys.version_info[0] >= 3:
    from six import string_types as basestring

from dsk.base.tdata.taskdata.gen_task import GenTask
from dsk.base.utils.msg_utils import MsgUtils as log


class TaskDataApi(object):
    ############
    @staticmethod
    def open_tp(tpZipFile):
        x = GenTask.ReadAsXml(tpZipFile)
        if x and len(x) == 1 and isinstance(x[0],GenTask):
            return x[0]
        return None

    @staticmethod
    ############
    def save_tp(taskpro):
        taskpro.SaveAsXml(taskpro.getName()+".tpp.gz",recursive=True)

    ############
    @classmethod
    def load_tp_file(cls, tpZipFile, searchPath=None, group=True):
        # init tp
        fileToLoad = tpZipFile
        doSearch = False
        # if there is a searchPath and the file doesn't have a path
        if searchPath != None and fileToLoad.find(os.sep) == -1:
            doSearch = True
            if isinstance(searchPath, basestring):
                searchPath = [searchPath]
            for i in searchPath:
                p = os.path.join(i,tpZipFile)
                if os.path.isfile(p) == True:
                    fileToLoad = p
                    break
        if doSearch and fileToLoad == tpZipFile:
            log.warning("couln't find the package %r at this location, maybe a new package" % tpZipFile)
        log.info("loading %r" % fileToLoad)

        return cls.open_tp(fileToLoad)


    ############
    @staticmethod
    def get_class_name_from_package(tpZipFile):
        name = os.path.split(tpZipFile)[1]
        # no real basefile formathere so let hardcoded it
        for ext in [".tpp",".tpp.gz"]:
            name = name.replace(ext,"")
        # dot are not valid in class name
        name = name.replace(".","")
        return name[0].capitalize() + name[1:]
        #return name.capitalize()

    ############
    @classmethod
    def to_python_out(cls,
                      atask,
                      className,
                      skipComment,
                      doTaskPackage,
                      outputs,
                      packageAllReadyLoaded,
                      packageName,
                      doTrace,
                      searchPath,
                      mainType):

        out,otherPackage = GenTask.to_python_one_package(atask,
                                                         className,
                                                         skipComment,
                                                         doTaskPackage,
                                                         packageAllReadyLoaded,
                                                         packageName)
        for i in out:
            outputs.append(i)
        if doTrace:
            import StringIO
            astream = StringIO.StringIO()
            astream.write("%s = logtrace.logclass(%s)\n" % (className,className))
            #astream.write("%s = logtrace.logtrace_class(%s)\n" % (className,className))
            outputs.append(astream)

        for other in otherPackage:
            nt = cls.load_tp_file(other,searchPath,mainType)
            if nt != None:
                cls.to_python_out(nt,
                                  cls.get_class_name_from_package(other),
                                  skipComment,
                                  doTaskPackage,
                                  outputs,
                                  packageAllReadyLoaded,
                                  packageName,
                                  doTrace,
                                  searchPath,
                                  mainType)

    @staticmethod
    def get_executable_main_string(className):
        CODE = """#########################
if __name__ == "__main__":
    import sys
    from dsk.base.tdata.taskdata import tp_variable
    objectProc = %s()
    if len(sys.argv) == 1:
        objectProc.doIt()
    else:
        print(sys.argv)
        assert len(sys.argv) == 5
        arg = sys.argv
        funcToCall = getattr(objectProc,arg[1])
        rtd = tp_variable.TpVariable()
        rtd.deserialize(arg[2])
        cfd = tp_variable.TpVariable()
        cfd.deserialize(arg[3])
        tp = tp_variable.ProcessVar()
        tp.deserialize(arg[4])
        funcToCall(rtd,cfd,tp)
        """ % className
        return CODE

    @staticmethod
    def get_instance_string(className):
        CODE = """#########################
objectProc = %s()
objectProc.doIt()
        """ % className
        return CODE


    ############
    @classmethod
    def make_python_file(cls,
                         loadedTp=None,
                         className="",
                         skipComment=True,
                         doTaskPackage=False,
                         doTrace=False,
                         searchPath="",
                         mainType="main",
                         outFile=""):
        if outFile == "":
            return cls.dumps_to_python(loadedTp=loadedTp,
                                       className=className,
                                       skipComment=skipComment,
                                       doTaskPackage=doTaskPackage,
                                       doTrace=doTrace,
                                       searchPath=searchPath,
                                       mainType)

        packageAllReadyLoaded = list()
        outputs = list()
        packName = os.path.split(outFile)[1]
        cls.to_python_out(loadedTp,
                          className=className,
                          skipComment=skipComment,
                          doTaskPackage=doTaskPackage,
                          outputs=[],
                          packageAllReadyLoaded=packageAllReadyLoaded,
                          packName=packName,
                          doTrace=False,
                          searchPath=searchPath,
                          mainType="main")

        f = open(outFile,"w")
        for out in outputs:
            f.write(out.getvalue())
            f.write("\n") # write a blank line between stream
        if mainType == "main":
            maincode = cls.get_executable_main_string(className)
            f.write(maincode)
        elif mainType == "instance":
            maincode = cls.get_instance_string(className)
            f.write(maincode)
        f.close()
        return True

    ############
    @classmethod
    def dumps_to_python(cls,
                        loadedTp = None,
                        className = "",
                        skipComment = True,
                        doTaskPackage = False,
                        doTrace=False,
                        searchPath="",
                        mainType = "main"):

        import StringIO
        packageAllReadyLoaded = list()
        outputs = list()
        cls.to_python_out(loadedTp,
                          className,
                          skipComment,
                          doTaskPackage,
                          outputs,
                          packageAllReadyLoaded,
                          "", # pack name
                          doTrace,
                          searchPath,
                          mainType)

        astream = StringIO.StringIO()
        if doTrace:
            astream.write("from dsk.base.utils import logtrace\n")
        for out in outputs:
            astream.write(out.getvalue())
            astream.write("\n") # write a blank line between stream
        if mainType == "main":
            maincode = cls.get_executable_main_string(className)
            astream.write(maincode)
        elif mainType == "instance":
            maincode = cls.get_instance_string(className)
            astream.write(maincode)

        return astream.getvalue()