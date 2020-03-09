"""
build up a set of function relative to path to manage resource specific to a tool
"""

import os
from dsk.base.lib.default_path import DefaultPath
from dsk.base.resources import browser_default

class ApplicationPath(DefaultPath):

    def __init__(self, param):
        """
        param (str): a module top tools with a codeInstall key
        """
        super(ApplicationPath, self).__init__()

        codeinstall = ""
        if hasattr(param, "CodeInstall"):
            codeinstall = param.CodeInstall
        assert codeinstall != ""
        self.baseroot = codeinstall

    def get_ui(self, name):
        """Return the correct fullname for the resource

        :param name: (str): root name with extension of a ui resources file
        :return fullname: the full name (project base) of the ui file

        """
        if not name.endswith(".ui"):
            name = name + ".ui"
        pp  = os.path.join(self.baseroot,
                           browser_default.RESOURCES,
                           browser_default.RESOURCES_UI,
                           name)
        return pp

    def get_icons(self, name):
        """Return the correct fullname of the resource

        :args name: (str) root name with extension of an icon file
        :return fullname: the full name (project base) of the icon file

        """
        pp  = os.path.join(self.baseroot,
                           browser_default.RESOURCES,
                           browser_default.RESOURCES_ICONS,
                           name)
        return pp