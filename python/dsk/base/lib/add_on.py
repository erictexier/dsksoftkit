"""
to generate widget from a formated string

"""

import traceback
from collections import namedtuple

class ToolImportBrowser(object):
    """ convenience to instantiate widget from browser
    """

    def str_instance(self):
        return "xxx = %s" % (self.wid_class)

    def str_import(self):
        """ when locate to dsk.base
        """
        if self.strfactory == None:
            return "from dsk.base.%s.%s import %s" % (self.wid_module, self.wid_loc, self.wid_class)
        else:
            return self.strfactory % (self.wid_module, self.wid_loc, self.wid_class)

    def get_factory(self):
        """
        :return:
            a factory to the widget
        """

        if self.factory == None:
            try:
                exec(self.str_import())
            except:
                traceback.print_exc()
                return None
            cmd_ins = self.str_instance()
            xxx = None # don't change name
            try:
                exec(cmd_ins)
                return xxx
            except:
                traceback.print_exc()
                return None

        else:
            return self.factory

class AddOn(namedtuple('addOn', "name wid_class wid_module wid_loc pref_place unique optmenu strfactory factory"), ToolImportBrowser):
    __slots__ = ()
    """

    :param name: tagname  (str)
    :param wid_class: widget class name  (str)
    :param wid_module : module path  (str)
    :param wid_loc: file name where the class definition is in  (str)
    :param pref_place: dock can be added with preference to L(elf), R(ight),T(op)or B(ottom) of your app window (str)
    :param unique: define if it's unique or notl (bool)
    :param optmenu: an ordered dict to populate options (str)
    :param strfactory: a format to import the widget (can be none if factory defined) (str)
    :param factory: a widget class (can be none if strfactory is not None)

    """

class ToolDesc(object):
    def __init__(self, addon, menudesc):
        """ Combine an addon and a menu description
        """
        self.addon = addon
        self.menudesc = menudesc
