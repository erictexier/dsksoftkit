from pprint import pformat
from dsk.base.tdata.gen_tree import GenTree


class PipeConfigListInfoDb(GenTree):

    def __init__(self):
        super(PipeConfigListInfoDb, self).__init__()


class PipeConfigInfoDb(GenTree):
    PCF = ["code", "linux_path", "windows_path", "mac_path", "users"]

    def __init__(self):
        super(PipeConfigInfoDb, self).__init__()
        self.reset()

    def reset(self):
        self.id = -1
        self.users_id = list()

    def setdata(self, arg):

        # we pop the image ref for readability
        code = arg.get('code', "")
        if code != "":
            self.setName(code)
            arg.pop('code')
            if 'type' in arg:
                arg.pop('type')
            if 'users' in arg:
                users = arg.pop('users')
                # users = arg['users']
                self.users_id = list()
                for u in users:
                    self.users_id.append(u['id'])
            self.__dict__.update(arg)
            return True
        return False

    def useridlist(self):
        return self.users_id

    def __repr__(self):
        return pformat(self.__dict__)

    def get_linux_path(self):
        return self.linux_path
