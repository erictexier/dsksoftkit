from dsk.base.tdata.gen_tree import GenTree


class PfList(GenTree):
    def __init__(self):
        super(PfList, self).__init__()
        self._currentname = ""

    def set_current_pf_name(self, name):
        if name in self.childNames():
            self._currentname = name

    def get_current_pf_name(self):
        if self._currentname == "":
            chs = self.getChildren()
            if len(chs) > 0:
                self._currentname = chs[0].getName()
        return self._currentname


class BaseMediaInfoDb(GenTree):
    """ base class for shot_info_db and asset_info_db
    """
    def __init__(self):
        super(BaseMediaInfoDb, self).__init__()
        self.reset()

    def reset(self):
        self.resetCache()
        self.version_set = False
        self['Version'] = GenTree()

        self.pub_set = False
        self['PublishedType'] = GenTree()

    # version media
    def is_version_set(self):
        return self.version_set

    def reset_version_set(self):
        self.version_set = False

    def set_media_version(self, versions):
        self.version_set = True
        if len(versions) == 0:
            return list()
        type_names = self['Version'].childNames()

        # should maybe be sorted later when in step
        for obj in versions:
            if obj.version_type not in type_names:
                g = GenTree()
                g.setName(obj.version_type)
                self['Version'].addChild(g)
                type_names = self['Version'].childNames()
            self['Version'][obj.version_type].addChild(obj)
        return self.get_media_version()

    def set_media_version2(self, versions, with_belong=True):
        self.version_set = True
        if len(versions) == 0:
            return list()
        type_names = self['Version'].childNames()

        # should maybe be sorted later when in step
        for obj in versions:
            if with_belong:
                key = obj.get_belong_to()
            else:
                key = obj.version_type
            if key not in type_names:
                g = GenTree()
                g.setName(key)
                self['Version'].addChild(g)
                type_names = self['Version'].childNames()
            self['Version'][key].addChild(obj)
        return self.get_media_version()

    def get_media_version(self):
        res = list()
        for obj in self['Version'].getChildren():
            res.append(obj)
            # this is a test to see if it was a ever query before
        return res

    # pub type
    def is_pub_set(self):
        return self.pub_set

    def get_publishedType(self):
        res = list()
        for obj in self['PublishedType'].getChildren():
            res.append(obj)
            # this is a test to see if it was a ever query before
        return res

    def set_plublished_type(self, fpt, published_type_list):
        # not done: need to bind the short_name of the file type
        if fpt in ["", None]:
            return
        type_names = self['PublishedType'].childNames()
        if fpt not in type_names:
            g = PfList()
            g.setName(fpt)
            self['PublishedType'].addChild(g)
            # type_names.append(fpt)
        if len(published_type_list) == 0:
            return list()
        for obj in published_type_list:
            self['PublishedType'][fpt].addChild(obj)
        return self.get_publishedType()
