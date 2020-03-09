''' generic app doc '''

import os
import re
import dsk
Base = dsk.__file__.split("python")[0][:-1]

pp = os.path.realpath(__file__.replace(".pyc",".py"))
revision = os.path.split(pp)[0]
CodeInstall = revision
BinInstall = os.path.join(Base,"bin")
#print(BinInstall)
#print(CodeInstall)
assert os.path.exists(CodeInstall) and os.path.exists(BinInstall)

appName = "browse"
Version = "0.1"
VersionRelease = "beta"
__url__ = 'http://mediawiki/wiki/Utilisateur:Etexier'


keyused = '''
initModule
autor
appName
subType
userBase # directory somewhere
toollist
aliasname
CodeInstall
BinInstall
Version
VersionRelease
supportList # list of email address
__url__
'''