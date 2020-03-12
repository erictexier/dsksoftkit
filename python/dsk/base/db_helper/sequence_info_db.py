from dsk.base.tdata.gen_tree import GenTree


class SequenceInfoDb(GenTree):

    def __init__(self):
        super(SequenceInfoDb, self).__init__()
        self.reset()

    def reset(self):
        self._currentshot = ""
        self.id = -1

    def set_current_shot(self, shot_name):
        if shot_name in self.get_shot_names():
            self._currentshot = shot_name
            return True
        return False

    def get_current_shotname(self):
        if self._currentshot == "":
            chs = self.getChildren()
            if len(chs) > 0:
                self._currentshot = chs[0].getName()
        return self._currentshot

    def get_shot_names(self):
        """ return the list of the current shot name
        """
        return self.childNames()

    def get_shot(self, shot_name):
        for ch in self.getChildren():
            if ch.getName() == shot_name:
                return ch
        return None
