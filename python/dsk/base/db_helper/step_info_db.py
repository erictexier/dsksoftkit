from dsk.base.tdata.gen_tree import GenTree


class StepInfoDb(GenTree):
    SF = ['code', 'id', 'short_name']

    @staticmethod
    def compare(a, b):
        return cmp(a.id, b.id)

    def __init__(self):
        super(StepInfoDb, self).__init__()
        self.reset()

    def __repr__(self):

        return (
            "step: %s " % self.getName() +
            ",id = %(id)d, type = %(step_type)s, label =" +
            "%(label)s" % self.__dict__)

    def reset(self):
        self.id = -1
        self.step_type = ""
        self.label = ""
        self.active = True

    def copy(self):
        a = StepInfoDb()
        a.setName(self.getName())
        a.__dict__.update(self.__dict__)
        return a

    def setdata(self, arg):
        self.label = arg.get("short_name", "no_label")
        self.id = arg.get("id", -1)
        return True

    def get_step_dict(self):
        return {'name': self.getName(),
                'type': 'Step',
                'id': self.id}

    def is_shot(self):
        return self.step_type == 'shot'

    def is_asset(self):
        return self.step_type == 'asset'
