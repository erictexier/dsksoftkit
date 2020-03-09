from dsk.base.tdata.gen_tree import GenTree

#########################################
class GlobalAppPref(GenTree):
    """ a place holder for global user preference
    """
    _colorRich = ['Label','Value','Valid','Hilite','Error']
    def __init__(self):
        from dsk.base.resources import browser_default as initDefault 
        super(GlobalAppPref,self).__init__()
        self.Info = ""
        self.reset_pref()
        self.LayoutFile = initDefault.DEFAULT_LAYOUT_ROOT
        self.MaxRecentFile = 10
        self.ShotInterest = ""
        self.DoLog = False

        # will save the preference always, even when user doesn't go to
        # the menu
        self.SavePreferenceOnExit = True
        self.ShowMenu = True

    def reset_pref(self):
        self.GlobalFontSize = 12
        self.BgColor = "#444444"
        self.TextColor = "#c6c6c6"
        self.SelectColor = "#ffffff"
        self.SelectBgColor = "#44a8ea"
        self.RichColor = {"Label":"#FFFFFF",
                          "Value":"#01D1FF",
                          "Valid": "#00FF00",
                          "Hilite": "#FF5500",
                          "Error":"#FF0000"}

    def set_rich_color(self,d):
        self.RichColor.update(d)

    def get_rich_color(self):
        return self.RichColor

    def set_global_font_size(self,size):
        self.GlobalFontSize = size

    def get_global_font_size(self):
        return self.GlobalFontSize

#########################################
class GlobalState(GenTree):
    """ a place holder for variable share across widget
    """
    def __init__(self):
        super(GlobalState, self).__init__()
        self.CurrentPath = ""

#########################################
class DockState(GenTree):
    def __init__(self):
        super(DockState,self).__init__()

#########################################
class AppPrefData(GenTree):
    def __init__(self):
        super(AppPrefData,self).__init__()
        self['globalPreference'] = GlobalAppPref()
        self['globalState'] = GlobalState()

    def global_preference(self):
        if self.has('globalPreference'):
            return self['globalPreference']
        self['globalPreference'] = GlobalAppPref()
        return self['globalPreference']

    def reset_pref(self):

        self['globalPreference'].reset_pref()
        self['globalState'] = GlobalState()

    def global_state(self):
        if self.has('globalState'):
            return self['globalState']
        self['globalState'] = GlobalState()
        return self['globalState']

    def dock_state(self):
        if self.has('dockState'):
            return self['dockState']
        self['dockState'] = DockState()
        return self['dockState']
