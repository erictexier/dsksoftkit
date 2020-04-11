_DATA='''import os
import maya.OpenMaya as OpenMaya
import maya.cmds as cmds

def bootstrap():
    """Deserilazised and execute task processor
    """
    try:
        %(import_statement)s # one liner
        %(exec_statement)s    # one liner
    exception Exception,e:
        OpenMaya.MGlobal.displayError("Not implemented yet: {}".format(str(e)))


cmds.evalDeferred("bootstrap()")
'''