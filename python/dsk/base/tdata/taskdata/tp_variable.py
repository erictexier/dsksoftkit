import types
import json

from dsk.base.tdata.gen_tree import GenTree

class TpVariable(GenTree):

    def __init__(self,**args):
        super(TpVariable,self).__init__()

    def overwrite(self,atpvariable):
        # it's not done but it will try to match the argument
        # name  recursively and ignoring the "_"
        # not done
        if atpvariable == None:
            return self
        for v in vars(atpvariable):
            if not v.startswith("_"):
                if hasattr(self,v):
                    setattr(self,v,getattr(atpvariable,v))
        return self

    def serialize(self):
        d = self.get_as_dict()
        return json.dumps(d)

    def deserialize(self,data):
        o = json.loads(data)
        self.set_with_dict(o)

    def get_as_dict(self):
        # "get_as_dict not done"
        d = dict()
        d.update(self.__dict__)
        return d

    def set_with_dict(self, d):
        self.__dict__.update(d)

class ProcessVar(TpVariable):
    def __init__(self):
        super(ProcessVar,self).__init__()
        self.isremote = False
    def is_remote(self):
        return self.isremote
    def set_remote(self,val):
        assert type(val) == types.BooleanType
        self.isremote = val
    def getUI(self,awindowName):
        return False

    def external(self,
                 executable = "",
                 pythonModule = "",
                 function="",
                 className="",
                 RTD=None,
                 CFD=None,
                 workingDirectory = "",
                 logDir = "",
                 daemonize=False,
                 block = False,              # waitForCompletion
                 host = "",
                 display=""
                 ):
        pass
