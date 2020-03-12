from dsk.base.tdata.gen_tree import GenTree


class UncachedVersion(GenTree):

    def __init__(self):
        super(UncachedVersion, self).__init__()
        self.reset()

    def reset(self):
        self.sid = -1

    def setdata_shotgun(self, arg):
        n = arg.get('name', None)
        if n:
            self.setName(n.replace("/", ":"))
        self.sid = arg.get('id', -1)


class ScreenRoomInfoDb(GenTree):
    PLF = ["code",
           "id",
           "locked",
           "project",
           "sg_mg_delivery_date",
           "sg_mg_type",
           "versions",
           "created_at"]

    @staticmethod
    def compare_date(a, b):
        return cmp(a.creation_date, b.creation_date)

    def __init__(self):
        super(ScreenRoomInfoDb, self).__init__()
        self.reset()

    def reset(self):
        self.sid = -1
        self.realname = ""
        self.creation_date = ""
        self.created_by = ""

    def is_later_than(self, dt):
        # dt is a qtdate
        from datetime import datetime
        clip = datetime(dt.year(), dt.month(), dt.day(), 0, 0)
        return self.creation_date.replace(tzinfo=None) >= clip

    def setdata_shotgun(self, arg):
        n = arg.get('code', None)
        if n:
            self.setName(n.replace("/", ":"))
            self.realname = n
        self.sid = arg.get('id', -1)
        self.creation_date = arg.get('created_at', "")

        vers = arg.get('versions', None)
        for v in vers:
            un = UncachedVersion()
            un.setdata_shotgun(v)
            self.addChild(un)
        dd = arg.get('created_by', None)
        if dd:
            self.created_by = dd['name']
        return True
