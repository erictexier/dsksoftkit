from dsk.base.tdata.gen_tree import GenTree
from pprint import pformat


class PftInfoDb(GenTree):
    """helper published file type
    """
    PFT = ["id", "code", "short_name"]

    def __init__(self):
        super(PftInfoDb, self).__init__()
        self.reset()

    def reset(self):
        self.code = ""
        self.id = -1

    def setdata(self, arg):
        n = arg.get('short_name', None)
        if n:
            self.setName(n.replace(" ", "_"))
            arg.pop('short_name')
        arg.pop('type')
        self.__dict__.update(arg)
        return True

    def __repr__(self):
        return pformat(self.__dict__)
