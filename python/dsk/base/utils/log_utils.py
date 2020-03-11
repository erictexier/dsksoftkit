import os, sys
import logging

from dsk.base.utils.disk_utils import DiskUtils
from dsk.base.utils.msg_utils import MsgUtils


# some useful handler not needed python >= 2.7
class NullHandler(logging.Handler):
    def emit(self, record):
        pass


class TESTlogstream(object): 
    def __init__(self, filepath, aneditor, mode='w+'):
        self._file = open(filepath, mode=mode)

        if aneditor != None:
            assert hasattr(aneditor, "logwrite")
            assert callable(aneditor.logwrite)
        self._aneditor =  aneditor

    def write(self, line):

        if(self._aneditor != None):
            #This is an broadcast to the someone that be need it
            self._aneditor.logwrite(str(line))
        self._file.write(line)

    def close(self):
        if self._file != None:
            self._file.close()
        self._file = None
    def flush(self):
        if self._file != None:
            self._file.flush()

    def readlines(self):
        if self._file != None:
            return self._file.readlines()
        return list()

################################################
class LogUtils(object):
    _defaultFormat = "[%(levelname)-7s] - %(asctime)s - %(name)s  - %(message)s"
    #_saveFormat = "[%(levelname)s %(name)s] %(message)s"

    # keep the last tag ti restore from before mute
    # see startMute
    _saveLoggerTag =  "" 

    def __init__(self):
        self._lock = False
        self._logger = None


        # keep the current hander
        self._handlerObject = None
        self._handlerObjecthand = None
        self._handlerObjectList = []

        # default logging mode        
        self._loglevel = logging.DEBUG
 
        self._logFormat = None

    ##########################
    def getLogger(self):
        return self._logger

    ##########################
    def setLogLevel(self, level):
        """
        Set log level on the current log
        """
        if self._handlerObjecthand != None:
            self._handlerObjecthand.setLevel(level)
        elif self._logger != None:
            self._logger.setLevel(level)

        self._loglevel = level

    ##########################
    def setDebugMode(self,b):
        if b == True:
            self.setLogLevel(logging.DEBUG)
        else:
            self.setLogLevel(logging.INFO)

    ##########################
    def isDebugOn(self):
        return self._loglevel == logging.DEBUG

    ##########################
    def toggleDebugMode(self):
        self.setDebugMode(not self.isDebugOn())

    ##########################
    def setFormat(self, formate = ""):
        if self._logFormat == None:
            if formate == "":
                formate = LogUtils._defaultFormat
            self._logFormat = logging.Formatter(formate)

        if self._handlerObjecthand != None:
            self._handlerObjecthand.setFormatter(self._logFormat)

    ##########################
    def pushHandlerStack(self):
        if self._handlerObjecthand != None:
            if not self._handlerObjecthand in self._handlerObjectList:
                self._handlerObjectList.append(self._handlerObjecthand)

    ##########################
    def removeLastHandler(self):

        if len(self._handlerObjectList) > 0:
            hand = self._handlerObjectList.pop(-1)

            hand.flush()
            hand.close()
            self._logger.removeHandler(hand) # get the last one

            if len(self._handlerObjectList) > 0:
                    if len(self._handlerObjectList) > 0:
                        self._handlerObjecthand = self._handlerObjectList[-1]
                    else:
                        self._handlerObjecthand = None

    ##########################
    def addHandlerStream(self,ooo = None):
        self.pushHandlerStack()
        self._handlerObjecthand = logging.StreamHandler(ooo)
        self._logger.addHandler(self._handlerObjecthand)

    def addHandlerFile(self,fileName):
        self.pushHandlerStack()
        self._handlerObjecthand = logging.FileHandler(fileName)
        self._logger.addHandler(self._handlerObjecthand)
        self._logFileName = fileName

    def addHandlerFileRotate(self,fileName,astream = None,nbLog=6):
        afile = self.pushLogs(fileName,nbLog)
        if(astream == None):
            self.addHandlerFile(afile)
        else:
            self._handlerObject  = TESTlogstream(afile,astream)
            self.addHandlerStream(self._handlerObject)

    def regularHandlerFile(self,fileName,astream = None):
        ### in python2.7
        #self._handlerObjecthand = logging.handlers.RotatingFileHandler(fileName)
        # for now:
        if(astream == None):
            self.addHandlerFile(fileName)
        else:
            self._handlerObject  = TESTlogstream(fileName,astream)
            self.addHandlerStream(self._handlerObject)

    ##########################
    def getLogFilename(self):
        return self._logFileName 

    def addHandlerMute(self):
        self.pushHandlerStack()
        self._handlerObjecthand = NullHandler()
        self._logger.addHandler(self._handlerObjecthand)

    def clean(self):
        if self._handlerObject != None:
            self._handlerObject.flush()
            self._handlerObject.close()
        if self._logger != None:

            for h in self._handlerObjectList:
                self._logger.removeHandler(h)

        # logging.shutdown(self._handlerObjectList)
        self._handlerObjectList = list()
        self._handlerObjecthand = None
        self._handlerObject = None
        self._logger = None

    def end_log(self):
        MsgUtils.set_logger("")
        self.clean()

    def _startLog(self,logTag):

        self._logger = logging.getLogger(logTag)
        self.setFormat()
        self.setLogLevel(self._loglevel)
        MsgUtils.set_logger(logTag)

    def startLogConsole(self,logTag):

        """ this is a basic log not using logging to redirect
            the output to a file
        """
        self.clean()
        self._startLog(logTag)
        self.addHandlerStream()
        self.setFormat()

    def startLogFile(self,logTag,logFile,astream=None):
        #########
        self.clean()
        self._startLog(logTag)
        self.regularHandlerFile(logFile,astream)
        self.setFormat()
        ## Start New

    def startLogFileRotate(self,logTag,logFile,nbRotation,astream = None):
        self.clean()
        self._startLog(logTag)
        self.addHandlerFileRotate(logFile,astream,nbRotation)
        self.setFormat()

    def startMute(self,logTag):
        #########
        if self._logger != None:
            self._saveLoggerTag = self._logger.name 
        self.clean()
        self._startLog(logTag)
        self.addHandlerMute()

    def endMute(self):
        self.end_log()
        if self._saveLoggerTag != "":
            MsgUtils.set_logger(self._saveLoggerTag)
            self._saveLoggerTag = ""

    def startLogBatch(self,logTag,logFileName):
        self.startLogFile(logTag,logFileName)

    def info(self,someText):
        # use the MsgUtils module instead
        self._logger.info(someText)

    @staticmethod
    def pushLogs(filename,maxLogFile):
        adir,basefile = os.path.split(filename)
        if not DiskUtils.is_dir_exist(adir):
            if not DiskUtils.create_path(adir):
                MsgUtils.error("Cannot create dir %r" % adir)
                sys.exit(1)

        if not os.path.exists(filename):
            return filename

        for i in range(maxLogFile,0,-1):
            tofile = os.path.join(adir,"%s.%d" % (basefile, i+1))
            fromfile = os.path.join(adir,"%s.%d" % (basefile, i))
            if os.path.exists(tofile) and os.path.exists(fromfile):
                DiskUtils.remove_file(tofile)
            if os.path.exists(fromfile):
                DiskUtils.rename_file(fromfile, tofile)

        DiskUtils.rename_file(
                            os.path.join(adir, basefile),
                            os.path.join(adir,'%s.1' % basefile))
        return os.path.join(adir, basefile)

    ##########################
    def lockLog(self,lfile):
        # mainly to catch up with print statement
        from dsk.base.utils import platform_utils
        self._lock = True

        flags = os.O_CREAT | os.O_APPEND | os.O_WRONLY

        # lock the lockFile
        whichOs = platform_utils.platform.system()
        if( whichOs == 'Linux' or 
            whichOs == 'Darwin' or 
            whichOs == 'Unix'):
                import fcntl
                # replace the input
                os.close(0)
                os.open("/dev/null", os.O_RDONLY)

                # replace the output
                os.close(1)
                os.open(lfile,flags)


                fcntl.flock(1, fcntl.LOCK_EX|fcntl.LOCK_NB)

                # redirect the std error
                os.close(2)
                os.open(lfile, flags)

        elif whichOs == 'Windows':
            # need some work
            # close the output
            print("window not supported")
            """
            os.close(1)
            os.open(lfile,flags)

            import msvcrt
            msvcrt.locking(1,msvcrt.LK_NBLCK, os.path.getsize(lfile))
            os.close(2)
            os.open(lfile,flags)
            """
            pass


def printSample(label):
    log.error("%s" % label, d=1)
    log.info("%s" % label, d=2)
    log.error("%s" % label)
    log.debug("%s" % label, d=4)
    log.warning("%s" % label)
    log.msg("%s" % label)
    print("regular print %s" % label)        # regular print
    log.write("%s" % label * 12, 'debug')    # older syntax

###############################################
if __name__ == '__main__':
    # from os.path import expanduser
    from dsk.base.utils.platform_utils import get_home_user
    from dsk.base.utils.msg_utils import MsgUtils as log
    # the directory needs to exist

    # logFile = "%s/TEMPLOG/test_logs" % expanduser("~")
    logFile = "%s/TEMPLOG/test_logs" % get_home_user()
    print("LOG FILE",logFile)
    alog = LogUtils()

    printSample("NOT STARTED ")

    # "START THE LOGGING"
    # alog.startLogConsole("Console")

    # alog.startLogFile("Console",logFile)
    # alog.addHandlerStream() # if run will keep print during logging to file

    alog.startLogFileRotate("ROTATE",logFile,3)
    printSample("STARTED")

    alog.addHandlerStream() # if run will keep print during the logging to file
    # for i in range(2):printSample("STARTED AFTER STREAM")
    alog.removeLastHandler()
    for i in range(5):
        printSample("AFTERREMOVE")

    # TODO: this is not working for
    # alog.removeLastHandler()
    # alog.removeLastHandler()
    # end the logging
    alog.end_log()
    printSample("ENDED")

