import os


from dsk.base.resources import dsk_constants
from dsk.base.path_helper import sgre as re
from dsk.base.path_helper.errors import DevDescriptorError

import yaml
from six.moves import urllib

class IODescriptorBase(object):
    """
    An I/O descriptor describes a particular version of an app, engine or core component.
    It also knows how to access metadata such as documentation, descriptions etc.

    Several Descriptor classes exists, all deriving from this base class, and the
    factory method create_descriptor() manufactures the correct descriptor object
    based on a descriptor dict, that is found inside of the environment config.

    Different App Descriptor implementations typically handle different source control
    systems: There may be an app descriptor which knows how to communicate with the
    Tank App store and one which knows how to handle the local file system.
    """

    _factory = {}

    @classmethod
    def register_descriptor_factory(cls, descriptor_type, subclass):
        """
        Registers a descriptor subclass with the :meth:`create` factory. This is
        necessary to remove local imports from IODescriptorBase subclasses to prevent
        problems during core swapping.

        :param descriptor_type: String type name of the descriptor, as will
            appear in the app location configuration.
        :param subclass: Class deriving from IODescriptorBase to associate.
        """
        cls._factory[descriptor_type] = subclass

    @classmethod
    def create(cls, bundle_type, descriptor_dict, sg_connection):
        """
        Factory method used by :meth:`create_descriptor`. This complex factory
        pattern is necessary to remove local imports from IODescriptorBase subclasses
        to prevent problems during core swapping.

        :param bundle_type: Either AppDescriptor.APP, CORE, ENGINE or FRAMEWORK.
        :param descriptor_dict: Descriptor dictionary describing the bundle.
        :param sg_connection: Shotgun connection to associated site.
        :returns: Instance of class deriving from :class:`IODescriptorBase`
        :raises: DevDescriptorError
        """
        descriptor_type = descriptor_dict.get("type")
        if descriptor_type not in cls._factory:
            raise DevDescriptorError(
                "Unknown descriptor type for '%s'" % descriptor_dict
            )
        class_obj = cls._factory[descriptor_type]
        return class_obj(descriptor_dict, sg_connection, bundle_type)

    def __init__(self, descriptor_dict, sg_connection, bundle_type):
        """
        Constructor

        :param descriptor_dict: Dictionary describing what
                                the descriptor is pointing at.
        :param sg_connection: Shotgun connection to associated site.
        :param bundle_type: Either AppDescriptor.APP, CORE, ENGINE or FRAMEWORK.
        """
        self._bundle_cache_root = None
        self._fallback_roots = []
        self._descriptor_dict = descriptor_dict
        self.__manifest_data = None
        self._is_copiable = True

    def set_cache_roots(self, primary_root, fallback_roots):
        """
        Specify where to go look for cached versions of the app.
        The primary root is where new data is always written to
        if something is downloaded and cached. The fallback_roots
        parameter is a list of paths where the descriptor system
        will look in case a cached entry is not found in the
        primary root. If you specify several fallback roots, they
        will be traversed in order.

        This is an internal method that is part of the construction
        of the descriptor instances. Do not call directly.

        :param primary_root: Path for reading and writing cached apps
        :param fallback_roots: Paths to attempt to read cached apps from
                               in case it's not found in the primary root.
                               Paths will be traversed in the order they are
                               specified.

        """
        self._bundle_cache_root = primary_root
        self._fallback_roots = fallback_roots

    def __str__(self):
        """
        Human readable representation
        """
        # fall back onto uri which is semi-human-readable
        # it is recommended that each class implements its own
        # operator in order to better customize the ux.
        return self.get_uri()

    def __repr__(self):
        """
        Low level representation
        """
        class_name = self.__class__.__name__
        return "<%s %s>" % (class_name, self.get_uri())

    @classmethod
    def _validate_descriptor(cls, descriptor_dict, required, optional):
        """
        Validate that the descriptor dictionary has got the necessary keys.

        Raises DevDescriptorError if required parameters are missing.
        Logs warnings if parameters outside the required/optional range are specified.

        :param descriptor_dict: descriptor dict
        :param required: List of required parameters
        :param optional: List of optionally supported parameters
        :raises: DevDescriptorError if the descriptor dict does not include all parameters.
        """
        desc_keys_set = set(descriptor_dict.keys())
        required_set = set(required)
        # Add deny_platforms and disabled to the list of optional parameters as these are globally supported across
        # all descriptors and are used by the environment code to check if an item is disabled.
        optional_set = set(optional + ["deny_platforms", "disabled"])

        if not required_set.issubset(desc_keys_set):
            missing_keys = required_set.difference(desc_keys_set)
            raise DevDescriptorError(
                "%s are missing required keys %s" % (descriptor_dict, missing_keys)
            )

        all_keys = required_set.union(optional_set)

        if desc_keys_set.difference(all_keys):
            log.warning(
                "Found unsupported parameters %s in %s. "
                "These will be ignored."
                % (desc_keys_set.difference(all_keys), descriptor_dict)
            )
    @classmethod
    def dict_from_uri(cls, uri):
        """
        Convert a uri string into a descriptor dictionary.

        Example:

        - uri:           sgtk:descriptor:app_store?name=hello&version=v123
        - expected_type: app_store
        - returns:   {'type': 'app_store',
                      'name': 'hello',
                      'version': 'v123'}

        :param uri: uri string
        :return: dictionary with keys type and all keys specified
                 in the item_keys parameter matched up by items in the
                 uri string.
        """
        parsed_uri = urllib.parse.urlparse(uri)

        # example:
        #
        # >>> urlparse.urlparse("sgtk:descriptor:app_store?foo=bar&baz=buz")
        #
        # ParseResult(scheme='sgtk', netloc='', path='descriptor:app_store',
        #             params='', query='foo=bar&baz=buz', fragment='')
        #
        #
        # NOTE - it seems on some versions of python the result is different.
        #        this includes python2.5 but seems to affect other SKUs as well.
        #
        # uri: sgtk:descriptor:app_store?version=v0.1.2&name=tk-bundle
        #
        # python 2.6+ expected: ParseResult(
        # scheme='sgtk',
        # netloc='',
        # path='descriptor:app_store',
        # params='',
        # query='version=v0.1.2&name=tk-bundle',
        # fragment='')
        #
        # python 2.5 and others: (
        # 'sgtk',
        # '',
        # 'descriptor:app_store?version=v0.1.2&name=tk-bundle',
        # '',
        # '',
        # '')

        if parsed_uri.scheme != constants.DESCRIPTOR_URI_PATH_SCHEME:
            raise DevDescriptorError("Invalid uri '%s' - must begin with 'sgtk'" % uri)

        if parsed_uri.query == "":
            # in python 2.5 and others, the querystring is part of the path (see above)
            (path, query) = parsed_uri.path.split("?")
        else:
            path = parsed_uri.path
            query = parsed_uri.query

        split_path = path.split(constants.DESCRIPTOR_URI_SEPARATOR)
        # e.g. 'descriptor:app_store' -> ('descriptor', 'app_store')
        if (
            len(split_path) != 2
            or split_path[0] != constants.DESCRIPTOR_URI_PATH_PREFIX
        ):
            raise DevDescriptorError(
                "Invalid uri '%s' - must begin with sgtk:descriptor" % uri
            )

        descriptor_dict = {}

        descriptor_dict["type"] = split_path[1]

        # now pop remaining keys into a dict and key by item_keys
        for (param, value) in urllib.parse.parse_qs(query).items():
            if len(value) > 1:
                raise DevDescriptorError(
                    "Invalid uri '%s' - duplicate parameters" % uri
                )
            descriptor_dict[param] = value[0]

        return descriptor_dict

    def get_dict(self):
        """
        Returns the dictionary associated with this descriptor
        """
        return self._descriptor_dict

    @classmethod
    def uri_from_dict(cls, descriptor_dict):
        """
        Create a descriptor uri given some data

        {'type': 'app_store', 'bar':'baz'} --> 'sgtk:descriptor:app_store?bar=baz'

        :param descriptor_dict: descriptor dictionary
        :return: descriptor uri
        """
        if "type" not in descriptor_dict:
            raise DevDescriptorError(
                "Cannot create uri from %s - missing type field" % descriptor_dict
            )

        uri_chunks = [
            constants.DESCRIPTOR_URI_PATH_SCHEME,
            constants.DESCRIPTOR_URI_PATH_PREFIX,
            descriptor_dict["type"],
        ]
        uri = constants.DESCRIPTOR_URI_SEPARATOR.join(uri_chunks)

        qs_chunks = []
        # Sort keys so that the uri is the same across invocations. This is very important
        # because tests may start failing with different implementations of Python (like pypy)
        # or code using this value as a key in a dict.
        for param in sorted(descriptor_dict):
            if param == "type":
                continue

            # note: for readability of windows and git paths, do not convert '/@:\'
            quoted_value = urllib.parse.quote(str(descriptor_dict[param]), safe="@/:\\")
            qs_chunks.append("%s=%s" % (param, quoted_value))

        qs = "&".join(qs_chunks)

        return "%s?%s" % (uri, qs)




def descriptor_uri_to_dict(uri):
    """
    Translates a descriptor uri into a dictionary.

    :param uri: descriptor string uri
    :returns: descriptor dictionary
    """
    return IODescriptorBase.dict_from_uri(uri)


def descriptor_dict_to_uri(ddict):
    """
    Translates a descriptor dictionary into a uri.

    :param ddict: descriptor dictionary
    :returns: descriptor uri
    """
    return IODescriptorBase.uri_from_dict(ddict)