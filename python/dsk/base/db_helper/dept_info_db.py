from dsk.base.tdata.gen_tree import GenTree


class DeptInfoDb(GenTree):

    @staticmethod
    def compare(a, b):
        return cmp(a.id, b.id)

    def __init__(self):
        super(DeptInfoDb, self).__init__()
        self.reset()

    def reset(self):
        self.id = -1
        self.dept_type = ""
        self.label = ""
        self.active = True

    def copy(self):
        a = DeptInfoDb()
        a.setName(self.getName())
        a.__dict__.update(self.__dict__)
        return a

    def setdata(self, idi, dept_type, label):
        self.id = idi
        self.dept_type = dept_type
        self.label = label
        return True

    def is_shot(self):
        return self.dept_type == 'shot'

    def is_asset(self):
        return self.dept_type == 'asset'
