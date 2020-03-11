import os
import getpass


####################################
class UserId(object):
    """ note: get_user_* are kept separated since I don't assume group are
        properly managed
    """
    _unknown = "unknownUser"
    _USER_CACHE = dict()

    @classmethod
    def get_user_dev(cls):
        result = list()
        try:
            import grp
            groups = grp.getgrnam('dev')
            return groups.gr_mem
        except:
            return result

    @classmethod
    def get_user_sys(cls):
        result = list()
        try:
            import grp
            groups = grp.getgrnam('system')
            return groups.gr_mem
        except:
            return result

    @classmethod
    def get_user_td(cls):
        result = list()
        try:
            import grp
            groups = grp.getgrnam('td')
            return groups.gr_mem
        except:
            return result

    @staticmethod
    def is_valid_user(username):
        # check if the username belong to the group
        if UserId.current_user() != UserId._unknown:
            UserId._USER_CACHE[username] = UserId.current_user()
        return username in UserId._USER_CACHE

    #####################
    @staticmethod
    def current_user():
        userName = getpass.getuser()

        return userName

    #####################
    @classmethod
    def get_cache(cls):
        return cls._USER_CACHE
