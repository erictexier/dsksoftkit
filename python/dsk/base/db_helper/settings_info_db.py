from dsk.base.tdata.gen_tree import GenTree


class SettingsInfoDb(GenTree):
    SF = ["code", "sg_mg_value"]

    def __init__(self):
        super(SettingsInfoDb, self).__init__()
        self.reset()

    def reset(self):
        self.id = -1

    def setdata(self, data):
        n = data.get('code', "unknown")
        self.setName(n)
        self.val = data.get('sg_mg_value', "")
        return True

    def __repr__(self):
        return "name: {}: val: {}".format(self.getName(), self.val)
