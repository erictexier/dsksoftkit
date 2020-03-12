import sys
import string
from optparse import OptionParser

HELP = "some quick info on how to run it"
DESC = "describe here"

#############
def printHelp(option, opt_str, value, parser, *args, **kwargs):
    # OptionParser assist routine to print more than default OptionParser help
    sys.stderr.write(HELP+ "\n")
    sys.stderr.write(parser.format_help() + "\n")
    sys.stderr.write(DESC)
    sys.exit(0)

class BaseCustomParser(OptionParser):

    def __init__(self, helpi, usage, desc):
        global HELP
        global DESC
        HELP = helpi
        DESC = desc
        OptionParser.__init__(self,usage=usage, add_help_option=False)

    def add_default_options(self, optionsList=["help","verbose","debug"]):
        # help
        if 'help' in optionsList:
            self.add_option("-h", "--help",
                            action="callback",
                            callback=printHelp,
                            help="Print this help info and exit")
        if 'verbose' in optionsList:
            self.add_option("-v","--ver", 
                            dest="doVerbose",
                            action="store_true",
                            default=False,
                            help="turn verbose on")
        if 'debug' in optionsList:
            self.add_option("-d","--debug", 
                            dest="doDebug",
                            action="store_true",
                            default=False,
                            help="turn debug on")

class QtMayaParse(BaseCustomParser):

    def __init__(self,helpi,usage,desc):
        BaseCustomParser.__init__(self,helpi, usage, desc)

    def addDefaultOptions(self,optionsList=["ui","maya","MayaUI"]):
        BaseCustomParser.add_default_options(self)

        if 'ui' in optionsList:
            self.add_option("-u","--ui", 
                            dest="gui",
                            action="store_true",
                            default=False,
                            help="load the ui")

        if 'maya' in optionsList:
            self.add_option("-m","--maya", 
                            dest="doMaya",
                            action="store_true",
                            default=False,
                            help="run mayapy")

        if 'MayaUI' in optionsList:
            self.add_option("-M","--mayaUI", 
                            dest="doMayaUI",
                            action="store_true",
                            default=False,
                            help="run maya")


class QtCommonParse(BaseCustomParser):
    def __init__(self, helpi, usage, desc):
        BaseCustomParser.__init__(self, helpi, usage, desc)

    def addDefaultOptions(self):
        BaseCustomParser.add_default_options(self)
        ## style
        from dsk.base.lib.qt_launch import styleName
        helpStyle = "%s" % string.join(map(lambda x: "%s" % styleName.index(x) + "=%s" % x ,styleName))
        self.add_option("-s", "--style",
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

