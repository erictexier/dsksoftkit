from dsk.base.db_helper.basemedia_info_db import BaseMediaInfoDb

SHOT_FIELDS = ['code', 'sg_sequence', 'assets']
FRAME_RANGE_SHOT = ['sg_cut_order',
                    'sg_cut_in',
                    'sg_cut_out',
                    'sg_cut_duration']


class ShotInfoDb(BaseMediaInfoDb):
    """ helper shot info db query
    """
    SF = SHOT_FIELDS + FRAME_RANGE_SHOT

    @staticmethod
    def compare(a, b):
        if a.shot_order == -1 and b.shot_order == -1:
            return cmp(a.code, b.code)
        return cmp(a.shot_order, b.shot_order)

    def __repr__(self):
        return ("shot: %s " % self.getName() +
                "id = %(id)d, order = %(shot_order)s" % self.__dict__)

    def __init__(self):
        super(ShotInfoDb, self).__init__()
        self.reset()

    def reset(self):
        super(ShotInfoDb, self).reset()
        self.code = ""
        self.id = -1
        self.shot_order = -1
        self.assets = list()

    def setdata(self,
                code, idi=-1, cut_order=-1, assets=None, status='wtg'):
        self.code = code
        self.id = idi
        self.assets = assets
        self.shot_order = cut_order
        if self.shot_order is None:
            self.shot_order = -1
        if status == "":
            self.status = 'wtg'
        return True

    def is_valid_code(self):
        sp = self.code.split("_")
        if len(sp) == 2:
            return True
        else:
            return False

    def sequence_name(self):
        sp = self.code.split("_")
        if len(sp) > 1:
            return sp[0]
        else:
            return self.code

    def get_code(self):
        return self.code

    def short_name(self):
        """
        return the code name without the show
        """
        sp = self.code.split("_")
        if len(sp) > 1:
            return "_".join(sp[1:])
        else:
            return self.code

    def shot_number(self):
        """
        return the code name without the show and seq as a string
        """
        sp = self.code.split("_")
        if len(sp) > 1:
            return "_".join(sp[1:])
        else:
            return self.code

    def get_asset_names(self):
        return [x['name'] for x in self.assets]

    def get_asset_ids(self):
        return [x['id'] for x in self.assets]

    def get_fields(self, conn, field_names=FRAME_RANGE_SHOT):
        sg_filters = [['code', 'is', self.code]]
        return conn.find('Shot', sg_filters, field_names)
