""" Load of convenience authentication function
"""
from dsk.base.lib.user_settings import UserSettings
from dsk.base.conn_helper.authentication.shotgun_authenticator import ShotgunAuthenticator


def get_user():
    settings = UserSettings()
    sa = ShotgunAuthenticator()
    user = sa.get_user()
    return user

def get_user_connection(user):
    return user.create_sg_connection()

#