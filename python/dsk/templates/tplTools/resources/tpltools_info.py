_DATA='''import os
appName = "%(name_space)s_%(module_name)s"
Version = "v0.0.0"
VersionRelease = "beta"

pp = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
CodeInstall = pp
__doc__ = """%(module_name)s -h
usage: %(module_name)s [-h] [-d]

optional arguments:
  -h, --help   show this help message and exit
  -d, --debug  print out debug info
"""
__url__ = 'http://mediawiki/wiki/Utilisateur:Etexier'
'''