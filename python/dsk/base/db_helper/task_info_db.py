from pprint import pformat
from dsk.base.tdata.gen_tree import GenTree


class TaskInfoDb(GenTree):
    def __init__(self):
        super(TaskInfoDb, self).__init__()
        self.reset()

    def reset(self):
        self.id = -1
        self.task_assign = list()

    def setdata(self, arg):

        self.task_assign = arg.get('task_assignees')
        if len(self.task_assign) == 0:
            return False

        slim = []
        for x in self.task_assign:
            slim.append(x['id'])
        self.task_assign = slim

        self.id = arg.get('id')
        self.setName("%s" % self.id)
        self.status = arg.get('sg_status_list', "")
        return True

    def assigned_ids(self):
        return self.task_assign

    def __repr__(self):
        return pformat(self.__dict__)
