# Copyright (c) 2015 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.
"""
Defines the supported types of authentication methods with Shotgun. You can
either authenticate with a session token with the SessionUser class or with an
api key with the ScriptUser class. This module is meant to be used internally.

--------------------------------------------------------------------------------
NOTE! This module is part of the authentication library internals and should
not be called directly. Interfaces and implementation of this module may change
at any point.
--------------------------------------------------------------------------------
"""

import cPickle
import httplib
from dsk.base.conn_helper.authentication.shotgun_wrapper import ShotgunWrapper
from shotgun_api3 import Shotgun, AuthenticationFault, ProtocolError

from dsk.base.conn_helper.authentication.session_cache import SessionData
from dsk.base.conn_helper.authentication.errors import IncompleteCredentials

# Indirection to create ShotgunWrapper instances. Great for unit testing.
_shotgun_instance_factory = ShotgunWrapper
from dsk.base.lib.log_manager import LogManager
logger = LogManager.get_logger(__name__)
#logger = LogManager.get_logger("toto")
#from dsk.base.utils.msg_utils import MsgUtils as logger

class ShotgunUserImpl(object):
    """
    Abstract base class for a Shotgun user. It tracks the user's host and proxy.
    """

    def __init__(self, host, http_proxy):
        """
        Constructor.

        :param host: Host for this Shotgun user.
        :param http_proxy: HTTP proxy to use with this host.
        """
        if not host:
            raise IncompleteCredentials("missing host")

        # We need to ensure that we are always storing utf-8 so that
        # we don't end up infecting API instances with unicode strings
        # that would then cause some string data to be unicoded during
        # concatenation operations.
        if http_proxy:
            self._http_proxy = http_proxy.encode("utf-8")
        else:
            self._http_proxy = ""
        self._host = host.encode("utf-8")
        logger.info(self._host)

    def get_host(self):
        """
        Returns the host for this user.

        :returns: The host string.
        """
        return self._host

    def get_http_proxy(self):
        """
        Returns the HTTP proxy for this user.

        :returns: The HTTP proxy string.
        """
        return self._http_proxy

    def create_sg_connection(self):
        """
        Creates a Shotgun connection using the credentials for this user.

        :raises NotImplementedError: If not overridden in the derived class,
                                     this method will raise a
                                     NotImplementedError.
        """
        self.__class__._not_implemented("create_sg_connection")

    def are_credentials_expired(self):
        """
        Checks if the credentials for the user are valid.

        :returns: True if the credentials are valid, False otherwise.
        """
        self.__class__._not_implemented("are_credentials_expired")

    def get_login(self):
        """
        Returns the login name for this user.

        :returns: The login name string.
        """
        self.__class__._not_implemented("get_login")

    def get_session_metadata(self):
        """
        Returns the session metadata for this user.

        :returns: An obscure blob of data.
        """
        self.__class__._not_implemented("get_session_metadata")

    def to_dict(self):
        """
        Converts the user into a dictionary object.

        :returns: A dictionary with all the attributes of the user.

        :raises NotImplementedError: If not overridden in the derived class,
                                     this method will raise a
                                     NotImplementedError.
        """
        return {"http_proxy": self._http_proxy,
                "host": self._host
                }

    @classmethod
    def from_dict(cls, payload):
        """
        Creates a user from a dictionary.

        :param payload: Dictionary with the user information.

        :returns: A ShotgunUser derived instance.

        :raises NotImplementedError: If not overridden in the derived class,
                                     this method will raise a
                                     NotImplementedError.

        """
        cls._not_implemented("from_dict")

    @classmethod
    def _not_implemented(cls, method):
        """
        Raise a properly formatted error message when a method is not implemented.

        :param method: Name of the method not implemented.

        :raises NotImplementedError: Thrown with the message "<class-name>.<method-name>
                                     is not implemented."
        """
        raise NotImplementedError(
            "%s.%s is not implemented." % (cls.__name__, method)
        )


class SessionUser(ShotgunUserImpl):
    """
    A user that authenticates to the Shotgun server using a session token.
    """

    def __init__(self, 
                 host,
                 login, 
                 session_token,
                 http_proxy,
                 password=None,
                 session_metadata=None,
                 session = None):
        """
        Constructor.

        :param host: Host for this Shotgun user.
        :param login: Login name for the user.
        :param session_token: Session token for the user. If session token is None
            the session token will be looked for in the users file.
        :param http_proxy: HTTP proxy to use with this host. Defaults to None.
        :param password: Password for the user. Defaults to None.
        :param session_metadata: Data structure needed when SSO is used. This is an obscure blob of data. Defaults to
            None.

        :raises IncompleteCredentials: If there is not enough values
            provided to initialize the user, this exception will be thrown.
        """
        if(session == None):
            logger.error("Create session data, with no session")
        super(SessionUser, self).__init__(host, http_proxy)
        self.session = session
        if not login:
            raise IncompleteCredentials("missing login.")

        # If we only have a password, generate a session token.
        if password and not session_token:
            session_token = SessionData.generate_session_token(host,
                                                               login, 
                                                               password,
                                                               http_proxy)

        # If we still don't have a session token, look in the session cache
        # to see if this user was already authenticated in the past.
        if not session_token and self.session:
            session_data = self.session.get_session_data(host,
                                                        login)
            # If session data was cached, load it.
            if session_data:
                session_token = session_data["session_token"]

        # We've exhausted our avenues to get a valid session token, throw.
        if not session_token:
            raise IncompleteCredentials("missing session_token")

        self._login = login
        self._session_token = session_token
        self._session_metadata = session_metadata

        self._try_save()

    def refresh_credentials(self):
        """
        Refreshes the credentials of this user so that they don't expire.
        If they are expired, you will be prompted for the user's password.
        """
        # Make a very simple authenticated request that returns as little information as possible.
        # If the session token was expired, the ShotgunWrapper returned by create_sg_connection
        # will take care of the session renewal.
        self.create_sg_connection().find_one("HumanUser", [])

    def get_login(self):
        """
        Returns the login name for this user.

        :returns: The login name string.
        """
        return self._login

    def get_session_token(self):
        """
        Returns the session token for this user.

        :returns: The session token string.
        """
        return self._session_token

    def set_session_token(self, session_token, cache=True):
        """
        Updates the session token for this user.

        :param session_token: The new session token for this user.
        :param cache: Set to False if you don't want the token to be written back
            to the session cache. Defaults to True.
        """
        self._session_token = session_token
        if cache:
            self._try_save()

    def get_session_metadata(self):
        """
        Returns the session_metadata string for this user.

        :returns: The session data, an obscure blob.
        """
        return self._session_metadata

    def set_session_metadata(self, session_metadata):
        """
        Update the user's session_metadata.

        :param session_metadata: SSO session information.
        """
        self._session_metadata = session_metadata

    def create_sg_connection(self):
        """
        Creates a Shotgun instance using the script user's credentials.

        The Shotgun instance will connect upon its first request.

        :returns: A Shotgun instance.
        """
        print('create a connection')
        return _shotgun_instance_factory(self.get_host(), 
                                         session_token=self.get_session_token(),
                                         http_proxy=self.get_http_proxy(),
                                         sg_auth_user=self,
                                         connect=False)

    @LogManager.log_timing
    def are_credentials_expired(self):
        """
        Checks if the credentials for the user are expired.

        This check is done solely on the Shotgun side. If SSO is being used,
        we do not attempt to contact the IdP to validate the session.

        :returns: True if the credentials are expired, False otherwise.
        """
        print('creation expired')
        logger.debug("Connecting to shotgun to determine if credentials have expired...")
        sg = Shotgun(self.get_host(),
                     session_token=self.get_session_token(),
                     http_proxy=self.get_http_proxy())
        try:
            sg.find_one("HumanUser", [])
            return False
        except ProtocolError as e:
            # One potential source of the error is that our SAML claims have
            # expired. We check if we were given a 302 and the
            # saml_login_request URL.
            # But if we get there, it means our session_token is still valid
            # as far as Shotgun is concerned.
            if (
                e.errcode == httplib.FOUND and
                "location" in e.headers and
                e.headers["location"].endswith("/saml/saml_login_request")
            ):
                # If we get here, the session_token is still valid.
                logger.debug("The SAML claims have expired. But the session_token is still valid")
                return False
            else:
                logger.error("Unexpected exception while validating credentials: %s" % e)
            return True
        except AuthenticationFault:
            return True

    def __repr__(self):
        """
        Returns a string reprensentation of the user.

        :returns: A string containing login and site.
        """
        return "<SessionUser %s @ %s>" % (self._login, self._host)

    def __str__(self):
        """
        Returns the name of the user.

        :returns: A string.
        """
        return self._login

    @staticmethod
    def from_dict(payload):
        """
        Creates a user from a dictionary.

        :param payload: Dictionary with the user information.

        :returns: A SessionUser instance.
        """
        return SessionUser(host=payload.get("host"),
                           login=payload.get("login"),
                           session_token=payload.get("session_token"),
                           http_proxy=payload.get("http_proxy"),
                           session_metadata=payload.get("session_metadata")
                           )

    def to_dict(self):
        """
        Converts the user into a dictionary object.

        :returns: A dictionary with all the attributes of the user.
        """
        data = super(SessionUser, self).to_dict()
        data["login"] = self.get_login()
        data["session_token"] = self.get_session_token()
        # To preserve backward compatibility with older cores, we avoid
        # serializing the session_metadata if there are not any.
        if self.get_session_metadata() is not None:
            data["session_metadata"] = self.get_session_metadata()
        return data

    def _try_save(self):
        """
        Try saving the credentials for this user, but do not raise an exception
        if it failed.
        """
        try:
            self.session.cache_session_data(self.get_host(),
                                            self.get_login(),
                                            self.get_session_token(),
                                            self.get_session_metadata())
        except Exception:
            # Do not break execution because somehow we couldn't
            # cache the credentials. We'll simply be asking them again
            # next time.
            logger.exception("Couldn't log the credentials to disk:")


class ScriptUser(ShotgunUserImpl):
    """
    User that authenticates to the Shotgun server using a api name and api key.
    """

    def __init__(self, host, api_script, api_key, http_proxy):
        """
        Constructor.

        :param host: Host for this Shotgun user.
        :param api_script: API script name.
        :param api_key: API script key.
        :param http_proxy: HTTP proxy to use with this host. Defaults to None.
        """
        super(ScriptUser, self).__init__(host, http_proxy)

        if not api_script or not api_key:
            raise IncompleteCredentials("missing api_script and/or api_key")

        self._api_script = api_script
        self._api_key = api_key

    def create_sg_connection(self):
        """
        Creates a Shotgun instance using the script user's credentials.

        The Shotgun instance will connect upon its first request.

        :returns: A Shotgun instance.
        """
        # No need to instantiate the ShotgunWrapper because we're not using
        # session-based authentication.
        return Shotgun(self._host,
                       script_name=self._api_script,
                       api_key=self._api_key,
                       http_proxy=self._http_proxy,
                       connect=False)

    def refresh_credentials(self):
        """
        This method does nothing, as script user's credentials don't expire.
        """

    def are_credentials_expired(self):
        """
        Checks if the credentials for the user are expired. Script user
        credentials can never be expired, so this method always returns False.

        :returns: False
        """
        return False

    def get_script(self):
        """
        Returns the script user name.

        :returns: The script user name.
        """
        return self._api_script

    def get_key(self):
        """
        Returns the script user key.

        :returns: The script user key.
        """
        return self._api_key

    def get_login(self):
        """
        Returns the login name for this user.

        :returns: The login name string.
        """
        # Script user has no login.
        return None

    def get_session_metadata(self):
        """
        Returns the session_metadata for this user.

        :returns: The metadata for the SSO session.
        """
        # Script user has no session_metadata.
        return None

    def to_dict(self):
        """
        Converts the user into a dictionary object.

        :returns: A dictionary with all the attributes of the user.
        """
        data = super(ScriptUser, self).to_dict()
        data["api_script"] = self.get_script()
        data["api_key"] = self.get_key()
        return data

    def __repr__(self):
        """
        Returns a string reprensentation of the user.

        :returns: A string containing script name and site.
        """
        return "<ScriptUser %s @ %s>" % (self._api_script, self._host)

    def __str__(self):
        """
        Returns the name of the user.

        :returns: A string.
        """
        return self._api_script

    @staticmethod
    def from_dict(payload):
        """
        Creates a user from a dictionary.

        :param payload: Dictionary with the user information.

        :returns: A ScriptUser instance.
        """
        return ScriptUser(
            host=payload.get("host"),
            api_script=payload.get("api_script"),
            api_key=payload.get("api_key"),
            http_proxy=payload.get("http_proxy")
        )


__factories = {
    # LoginPassword-like-User should go here in we ever implement it.
    SessionUser.__name__: SessionUser.from_dict,
    ScriptUser.__name__: ScriptUser.from_dict
}


def serialize_user(user):
    """
    Serializes a user. Meant to be consumed by deserialize.

    :param user: User object that needs to be serialized.

    :returns: The payload representing the user.
    """
    # Pickle the dictionary and inject the user type in the payload so we know
    # how to unpickle the user.
    return cPickle.dumps({
        "type": user.__class__.__name__,
        "data": user.to_dict()
    })


def deserialize_user(payload):
    """
    Converts a payload produced by serialize into any of the ShotgunUser
    derived instance.

    :params payload: Pickled dictionary of values

    :returns: A ShotgunUser derived instance.
    """
    # Unpickle the dictionary
    user_dict = cPickle.loads(payload)

    # Find which user type we have
    global __factories
    factory = __factories.get(user_dict.get("type"))
    # Unknown type, something is wrong. Maybe backward compatible code broke?
    if not factory:
        raise Exception("Could not deserialize Shotgun user. Invalid user type: %s" % user_dict)
    # Instantiate the user object.
    return factory(user_dict["data"])