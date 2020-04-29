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
This module will provide basic i/o to read and write session user's credentials
in the site's cache location.

--------------------------------------------------------------------------------
NOTE! This module is part of the authentication library internals and should
not be called directly. Interfaces and implementation of this module may change
at any point.
--------------------------------------------------------------------------------
"""

#from __future__ import with_statement
import os
import socket
import yaml

from shotgun_api3 import Shotgun
from shotgun_api3 import AuthenticationFault
from shotgun_api3 import ProtocolError
from shotgun_api3 import MissingTwoFactorAuthenticationFault
from shotgun_api3.lib import httplib2


from dsk.base.lib.log_manager import LogManager
logger = LogManager.get_logger(__name__)

from dsk.base.conn_helper.shotgun import connection
from dsk.base.utils.filesystem_utils import FileSystemUtils
from dsk.base.utils.platform_utils import LocalFileStorageManager as LFSM
from dsk.base.utils.platform_utils import LocationDefault
from dsk.base.conn_helper.authentication.errors import AuthenticationError

from dsk.base.resources.dsk_constants import SESSION_CACHE_FILE_NAME


class SessionData(object):
    _CURRENT_HOST = "current_host"
    _RECENT_HOSTS = "recent_hosts"

    _CURRENT_USER = "current_user"
    _RECENT_USERS = "recent_users"
    _USERS = "users"
    _LOGIN= "login"

    _SESSION_METADATA = "session_metadata"
    _SESSION_TOKEN = "session_token"


    def __init__(self, alocation):
        assert isinstance(alocation,LocationDefault)
        self.location_base = alocation

    def _get_global_authentication_file_location(self):
        """
        Returns the location of the authentication file on disk. This file
        stores authentication related information for all sites. At this moment,
        the file stores only the current host.
    
        Looks for the latest file naming convention first, if that doesn't exists
        tries to fall back to previous path standards.
    
        :returns: Path to the login information.
        """
        # try current generation path first
        path = os.path.join(self.location_base.cache_dir_def,
                            SESSION_CACHE_FILE_NAME)

        return path

    def _get_site_authentication_file_location(self, base_url):
        """
        Returns the location of the users file on disk for a specific site.
        :param base_url: The site we want the login information for.
        :returns: Path to the login information.
        """
        base_url = LFSM.get_site_root_name(base_url)
        path = os.path.join(self.location_base.cache_dir_def,
                            base_url,
                            SESSION_CACHE_FILE_NAME)
        return path


    @classmethod
    def _is_same_user(cls, user, login):
        """
        Compares the session data's login with a given login name. The comparison
        is not case sensitive.

        :returns: True if the session data is for the given login.
        """
        return user[cls._LOGIN].lower().strip() == login.lower().strip()

    @staticmethod
    def _ensure_folder_for_file(filepath):
        """
        Makes sure the folder exists for a given file.
        :param filepath: Path to the file we want to make sure the parent directory
                         exists.

        :returns: The path to the file.
        """
        folder, _ = os.path.split(filepath)
        FileSystemUtils.ensure_folder_exists(folder, permissions=0o700)
        return filepath

    @staticmethod
    def _try_load_yaml_file(file_path):
        """
        Loads a yaml file.

        :param file_path: The yaml file to load.

        :returns: The dictionary for this yaml file. If the file doesn't exist or is
                  corrupted, returns an empty dictionary.
        """
        logger.debug("Loading '%s'" % file_path)
        if not os.path.exists(file_path):
            logger.debug("Yaml file missing: %s" % file_path)
            return {}
        try:
            config_file = None
            # Open the file and read it.
            config_file = open(file_path, "r")
            result = yaml.load(config_file,Loader=yaml.FullLoader)
            # Make sure we got a dictionary back.
            if not isinstance(result, dict):
                logger.warning("File '%s' didn't have a dictionary, defaulting to an empty one." % file_path)
                result = {}
        except yaml.YAMLError:
            # Return to the beginning
            config_file.seek(0)
            logger.exception("Error reading '%s'" % file_path)

            logger.debug("Here's its content:")
            # And log the complete file for debugging.
            for line in config_file:
                # Log line without \n
                logger.debug(line.rstrip())
            # Create an empty document
            result = {}
        except Exception:
            logger.exception("Unexpected error while opening %s" % file_path)
            result = {}
        finally:
            # If the exception occured when we opened the file, there is no file to close.
            if config_file:
                config_file.close()
        return result

    @classmethod
    def _try_load_site_authentication_file(cls, file_path):
        """
        Returns the site level authentication data.
        This is loaded in from disk if available,
        otherwise an empty data structure is returned.

        :returns: site authentication style dictionary
        """
        content = cls._try_load_yaml_file(file_path)

        # Do not attempt to filter out content that is not understood. This allows
        # the file to be backwards and forward compatible with different versions
        # of core.

        # Make sure any mandatory entry is present.
        content.setdefault(cls._USERS, [])
        content.setdefault(cls._CURRENT_USER, None)
        content.setdefault(cls._RECENT_USERS, [])

        for user in content[cls._USERS]:
            user[cls._LOGIN] = user[cls._LOGIN].strip()

        if content[cls._CURRENT_USER]:
            content[cls._CURRENT_USER] = content[cls._CURRENT_USER].strip()

        return content

    @classmethod
    def _try_load_global_authentication_file(cls, file_path):
        """
        Returns the global authentication data.
        This is loaded in from disk if available,
        otherwise an empty data structure is returned.

        :returns: global authentication style dictionary
        """
        content = cls._try_load_yaml_file(file_path)

        # Do not attempt to filter out content that is not understood. This allows
        # the file to be backwards and forward compatible with different versions
        # of core.

        # Make sure any mandatody entry is present.
        content.setdefault(cls._CURRENT_HOST, None)
        content.setdefault(cls._RECENT_HOSTS, [])

        return content

    @staticmethod
    def _write_yaml_file(file_path, users_data):
        """
        Writes the yaml file at a given location.
    
        :param file_path: Where to write the users data
        :param users_data: Dictionary to write to disk.
        """
        old_umask = os.umask(0o077)
        try:
            with open(file_path, "w") as users_file:
                yaml.safe_dump(users_data, users_file)
        finally:
            os.umask(old_umask)

    @classmethod
    def _insert_or_update_user(cls,
                               users_file,
                               login,
                               session_token,
                               session_metadata):
        """
        Finds or updates an entry in the users file with the given login and
        session token.
    
        :param users_file: Users dictionary to update.
        :param login: Login of the user to update.
        :param session_token: Session token of the user to update.
        :param session_metadata: Information needed for when SSO is used. This is an obscure blob of data.
    
        :returns: True is the users dictionary has been updated, False otherwise.
        """
        # Go through all users

        for user in users_file[cls._USERS]:
            # If we've matched what we are looking for.
            if cls._is_same_user(user, login):
                result = False
                # Update and return True only if something changed.
                if user[cls._SESSION_TOKEN] != session_token:
                    user[cls._SESSION_TOKEN] = session_token
                    result = True
                if user.get(cls._SESSION_METADATA) and user[cls._SESSION_METADATA] != session_metadata:
                    user[cls._SESSION_METADATA] = session_metadata
                    result = True
                return result
        # This is a new user, add it to the list.
        user = {
            cls._LOGIN: login,
            cls._SESSION_TOKEN: session_token
        }
        # We purposely do not save unset session_metadata to avoid de-serialization issues
        # when the data is read by older versions of the tk-core.
        if session_metadata is not None:
            user[cls._SESSION_METADATA] = session_metadata
        users_file[cls._USERS].append(user)
        return True



    def delete_session_data(self, host, login):
        """
        Clears the session cache for the given site and login.
    
        :param host: Site to clear the session cache for.
        :param login: User to clear the session cache for.
        """
        if not host:
            logger.error("Current host not set, nothing to clear.")
            return
        logger.debug("Clearing session cached on disk.")
        try:
            info_path = self._get_site_authentication_file_location(host)
            logger.debug("Session file found.")
            # Read in the file
            users_file = self._try_load_site_authentication_file(info_path)
            # File the users to remove the token
            users_file[self._USERS] = [u for u in users_file[self._USERS] if not self._is_same_user(u, login)]
            # Write back the file.

            self._write_yaml_file(info_path, users_file)
            logger.debug("Session cleared.")
        except Exception:
            logger.exception("Couldn't update the session cache file!")
            raise

    def get_session_data(self, base_url, login):
        """
        Returns the cached login info if found.

        :param base_url: The site to look for the login information.
        :param login: The user we want the login information for.

        :returns: Returns a dictionary with keys login and session_token or None
        """
        # Retrieve the location of the cached info
        info_path = self._get_site_authentication_file_location(base_url)
        try:
            users_file = self._try_load_site_authentication_file(info_path)
            for user in users_file[self._USERS]:
                # Search for the user in the users dictionary.
                if self._is_same_user(user, login):
                    session_data = {
                        self._LOGIN: user[self._LOGIN],
                        self._SESSION_TOKEN: user[self._SESSION_TOKEN]
                    }
                    # We want to keep session_metadata out of the session data if there
                    # is none. This is to ensure backward compatibility for older
                    # version of tk-core reading the authentication.yml
                    if user.get(self._SESSION_METADATA):
                        session_data[self._SESSION_METADATA] = user[self._SESSION_METADATA]
                    return session_data
            logger.debug("No cached user found for %s" % login)
        except Exception:
            logger.exception("Exception thrown while loading cached session info.")
            return None


    def cache_session_data(self, host, login, session_token, session_metadata=None):
        """
        Caches the session data for a site and a user.

        :param host: Site we want to cache a session for.
        :param login: User we want to cache a session for.
        :param session_token: Session token we want to cache.
        :param session_metadata: Session meta data.
        """
        # Retrieve the cached info file location from the host
        file_path = self._get_site_authentication_file_location(host)
        self._ensure_folder_for_file(file_path)

        logger.info("Checking if we need to update cached session data "
                     "for site '%s' and user '%s' in %s..." % (host, login, file_path))

        document = self._try_load_site_authentication_file(file_path)

        if self._insert_or_update_user(document, login, session_token, session_metadata):
            # Write back the file only it a new user was added.
            self._write_yaml_file(file_path, document)
            logger.debug("Updated session cache data.")
        else:
            logger.debug("Session data was already up to date.")


    def get_current_user(self, host):
        """
        Returns the current user for the given host.

        :param host: Host to fetch the current for.

        :returns: The current user for this host or None if not set.
        """
        # Retrieve the cached info file location from the host
        info_path = self._get_site_authentication_file_location(host)
        document = self._try_load_site_authentication_file(info_path)
        user = document[self._CURRENT_USER]
        logger.debug("Current user is '%s'" % user)
        return user.strip() if user else user

    def set_current_user(self, host, login):
        """
        Saves the current user for a given host and updates the recent user list. Only the last 8
        entries are kept.
    
        :param host: Host to save the current user for.
        :param login: The current user login for specified host.
        """
        host = host.strip()
        login = login.strip()

        file_path = self._get_site_authentication_file_location(host)
        self._ensure_folder_for_file(file_path)

        current_user_file = self._try_load_site_authentication_file(file_path)

        self._update_recent_list(current_user_file,
                                 self._CURRENT_USER,
                                 self._RECENT_USERS,
                                 login)
        self._write_yaml_file(file_path, current_user_file)


    def set_current_host(self, host):
        """
        Saves the current host and updates the most recent host list. Only the last 8 entries are kept.

        :param host: The new current host.
        """
        if host:
            host = connection.sanitize_url(host)

        file_path = self._get_global_authentication_file_location()
        self._ensure_folder_for_file(file_path)

        current_host_file = self._try_load_global_authentication_file(file_path)

        self._update_recent_list(current_host_file,
                                 self._CURRENT_HOST,
                                 self._RECENT_HOSTS,
                                 host)
        self._write_yaml_file(file_path, current_host_file)

    @staticmethod
    def _update_recent_list(document, current_key, recent_key, value):
        """
        Updates document's current key with the desired value and it's recent key by inserting the value
        at the front. Only the most recent 8 entries are kept.

        For example, if a document has the current_host (current_key) and recent_hosts (recent_key) key,
        the current_host would be set to the host (value) passed in and the host would be inserted
        at the front of recent_key's array.
        """
        document[current_key] = value
        # Make sure this user is now the most recent one.
        if value in document[recent_key]:
            document[recent_key].remove(value)
        document[recent_key].insert(0, value)
        # Only keep the 8 most recent entries
        document[recent_key] = document[recent_key][:8]

    def get_current_host(self):
        """
        Returns the current host.

        :returns: The current host string, None if undefined
        """
        # Retrieve the cached info file location from the host
        info_path = self._get_global_authentication_file_location()
        document = self._try_load_global_authentication_file(info_path)
        host = document[self._CURRENT_HOST]
        if host:
            host = connection.sanitize_url(host)
        logger.debug("Current host is '%s'" % host)
        return host

    @classmethod
    def _get_recent_items(cls, document, recent_field, current_field, type_name):
        """
        Extract the list of recent items from the document.
    
        If the recent_field is not set, then we'll simply return the current_field's
        value. The recent_field will be empty when upgrading from an older core
        that didn't support the recent users/hosts list.
    
        :param object document: Document to extract information from
        :param recent_field: Field from which we need to retrieve
        """
        # Extract the list of recent items.
        items = document[recent_field]

        # Then check if the current is part of the list. It's not? This is because
        # an older core updated the file, but didn't know about the recent list and
        # didn't update it. This is possible because since day one the authentication.yml
        # has been treated as document with certain fields set and when the document
        # is rewritten it is rewritten as is, except for the bits that were updated.
        if document[current_field]:
            # If the item was present in the list, remove it and move it to the top
            # so it's marked as the most recent.
            if document[current_field] in items:
                items.remove(document[current_field])
            items.insert(0, document[current_field])
        logger.debug("Recent %s are: %s", type_name, items)
        return items


    def get_recent_hosts(self):
        """
        Retrieves the list of recently visited hosts.

        :returns: List of recently visited hosts.
        """
        info_path = self._get_global_authentication_file_location()
        document = self._try_load_global_authentication_file(info_path)
        return self._get_recent_items(document,
                                      self._RECENT_HOSTS,
                                      self._CURRENT_HOST,
                                      "hosts")


    def get_recent_users(self, site):
        """
        Retrieves the list of recently visited hosts.
    
        :returns: List of recently visited hosts.
        """
        info_path = self._get_site_authentication_file_location(site)
        document = self._try_load_site_authentication_file(info_path)
        logger.debug("Recent users are: %s", document[self._RECENT_USERS])
        return self._get_recent_items(document,
                                      self._RECENT_USERS,
                                      self._CURRENT_USER,
                                      "users")

    @staticmethod
    @LogManager.log_timing
    def generate_session_token(hostname,
                               login,
                               password,
                               http_proxy,
                               auth_token=None):
        """
        Generates a session token for a given username/password on a given site.
    
        :param hostname: The host to connect to.
        :param login: The user to get a session for.
        :param password: Password for the user.
        :param http_proxy: Proxy to use. Can be None.
        :param auth_token: Two factor authentication token for the user. Can be None.
    
        :returns: The generated session token for that user/password/auth_token/site combo.
    
        :raises AuthenticationError: Raised when the user information is invalid.
        :raises MissingTwoFactorAuthenticationFault: Raised when missing a two factor authentication
            code or backup code.
        :raises Exception: Raised when a network error occurs.
        """
        try:
            # Create the instance that does not connect right away for speed...
            logger.debug("Connecting to Shotgun to generate session token...")
            sg = Shotgun(hostname,
                         login=login,
                         password=password,
                         http_proxy=http_proxy,
                         connect=False,
                         auth_token=auth_token)
            # .. and generate the session token. If it throws, we have invalid
            # credentials or invalid host/proxy settings.
            return sg.get_session_token()
        except AuthenticationFault:
            raise AuthenticationError("Authentication failed.")
        except (ProtocolError, httplib2.ServerNotFoundError):
            raise AuthenticationError("Server %s was not found." % hostname)
        # In the following handlers, we are not rethrowing an AuthenticationError for
        # a very specific reason. While wrong credentials or host is a user
        # recoverable error, problems with proxy settings or network errors are much
        # more severe errors which can't be fixed by reprompting. Therefore, they have
        # nothing to do with authentication and shouldn't be reported as such.
        except socket.error as e:
            logger.exception("Unexpected connection error.")
            # e.message is always an empty string, so look at the exception's arguments.
            # The arguments are always a string or a number and a string.
            if isinstance(e.args[0], str):
                # if the error is just a string, simply forward the message.
                raise Exception(e.args[0])
            else:
                # We could argue here that we should only display the string portion of the
                # error since the error code is of little relevance to the user, but since
                # Toolkit doesn't properly log everything to a file at the moment, it's probably
                # safer to have the error code a little bit more in the open. Also, the formatting
                # of this exception type is pretty bad so let's reformat it ourselves. By default, it
                # turns a tuple into a string.
                raise Exception("%s (%d)" % (e.args[1], e.args[0]))
        except httplib2.socks.ProxyError as e:
            logger.exception("Unexpected connection error.")
            # Same comment applies here around formatting.
            # Note that e.message is always a tuple in this
            raise Exception("%s (%d)" % (e.message[1], e.message[0]))
        except MissingTwoFactorAuthenticationFault:
            # Silently catch and rethrow to avoid logging.
            raise
        except Exception as e:
            logger.exception("There was a problem logging in.")
            # If the error message is empty, like httplib.HTTPException, convert
            # the class name to a string
            if len(str(e)) == 0:
                raise Exception("Unknown error: %s" % type(e).__name__)
            else:
                raise
