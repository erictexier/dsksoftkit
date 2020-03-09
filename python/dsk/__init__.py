global APP
import os
#defin the main bin area
pp = os.path.realpath(__file__.replace(".pyc",".py"))
revision = os.path.split(pp)[0]
ModuleBin = os.path.join(os.path.dirname(revision),"bin")
del pp
del revision
def initialize(app):
    # just for now to query from interpreter
    global APP
    APP = app