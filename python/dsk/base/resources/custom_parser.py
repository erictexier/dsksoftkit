import sys
import string

from argparse import  ArgumentParser


class BaseCustomParser(object):
    HELP = "no help"
    def __init__(self, helpi, usage, desc):
        BaseCustomParser.HELP = helpi
        self.parser = ArgumentParser(description=desc, usage= usage)

    def add_default_options(self, optionsList=["help","verbose","debug"]):
        # help
        #if 'help' in optionsList:
        #    self.parser.add_argument("-h", "--help",help=BaseCustomParser.HELP)
        if 'verbose' in optionsList:
            self.parser.add_argument("-v","--ver", 
                            dest="doVerbose",
                            action="store_true",
                            default=False,
                            help="turn verbose on")
        if 'debug' in optionsList:
            self.parser.add_argument("-d","--debug", 
                            dest="doDebug",
                            action="store_true",
                            default=False,
                            help="turn debug on")

class QtMayaParse(BaseCustomParser):

    def __init__(self,helpi,usage,desc):
        super(BaseCustomParser,self).__init__(helpi, usage, desc)

    def addDefaultOptions(self,optionsList=["ui","maya","MayaUI"]):
        BaseCustomParser.add_default_options(self)

        if 'ui' in optionsList:
            self.parser.add_argument("-u","--ui", 
                            dest="gui",
                            action="store_true",
                            default=False,
                            help="load the ui")

        if 'maya' in optionsList:
            self.parser.add_argument("-m","--maya", 
                            dest="doMaya",
                            action="store_true",
                            default=False,
                            help="run mayapy")

        if 'MayaUI' in optionsList:
            self.parser.add_argument("-M","--mayaUI", 
                            dest="doMayaUI",
                            action="store_true",
                            default=False,
                            help="run maya")


class QtCommonParse(BaseCustomParser):
    def __init__(self, helpi, usage, desc):
        super(QtCommonParse, self).__init__(helpi, usage, desc)

    def addDefaultOptions(self):
        BaseCustomParser.add_default_options(self)
        ## style
        from dsk.base.lib.qt_launch import styleName
        helpStyle = "%s" % string.join(map(lambda x: "%s" % styleName.index(x) + "=%s" % x ,styleName))
        self.parser.add_argument("-s", "--style",
                        action="store",
                        dest="style",
                        default="-1",
                        help=helpStyle)

    def getStyle(self,opt):
        from dsk.base.lib.qt_launch import styleName
        # style
        styleIndex = 0
        if opt.style == "-1":
            return -1
        try:
            styleIndex = string.atoi(opt.style)
        except:
                pass
        if styleIndex < 0 or styleIndex >= len(styleName):
            styleIndex = 0
        return styleIndex

