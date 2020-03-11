import os
import re
import dsk
v = re.search(r'%sv[\d\.]*%s' % (os.sep, os.sep), dsk.__file__)
if v:
    version = v.group()[1:-1]
else:
    version = "local"
