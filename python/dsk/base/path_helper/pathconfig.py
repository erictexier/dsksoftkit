import os

from dsk.base.path_helper import yaml_cache
from dsk.base.path_helper.shotgun_path import ShotgunPath
from dsk.base.resources import dsk_constants
from dsk.base.path_helper.storage_roots import StorageRoots
from dsk.base.path_helper import template_includes
from dsk.base.path_helper.errors import DevError
from dsk.base.path_helper.errors import DevUnreadableFileError

def get_roots_metadata(pipeline_config_path):
    """
    Loads and validates the roots metadata file.

    The roots.yml file is a reflection of the local storages setup in Shotgun
    at project setup time and may contain anomalies in the path layout structure.

    The roots data will be prepended to paths and used for comparison so it is 
    critical that the paths are on a correct normalized form once they have been 
    loaded into the system.

    :param pipeline_config_path: Path to the root of a pipeline configuration,
                                 (excluding the "config" folder).  

    :returns: A dictionary structure with an entry for each storage defined. Each
              storage will have three keys mac_path, windows_path and linux_path, 
              for example
              { "primary"  : <ShotgunPath>,
                "textures" : <ShotgunPath>
              }
    """
    # now read in the roots.yml file
    # this will contain something like
    # {'primary': {'mac_path': '/studio', 'windows_path': None, 'linux_path': '/studio'}}
    roots_yml = os.path.join(pipeline_config_path,
                             dsk_constants.ENVI_TEMPLATE_NAME,
                             dsk_constants.ENVI_NAMING_CORE,
                             dsk_constants.STORAGE_ROOTS_FILE)

    try:
        # if file is empty, initialize with empty dict...
        data = yaml_cache.g_yaml_cache.get(roots_yml, deepcopy_data=False) or {}
    except Exception as e:
        raise DevError("Looks like the roots file is corrupt. Please contact "
                       "support! File: '%s' Error: %s" % (roots_yml, e))

    # if there are more than zero storages defined, ensure one of them is the primary storage
    if len(data) > 0 and dsk_constants.PRIMARY_STORAGE_NAME not in data:
        raise DevError("Could not find a primary storage in roots file "
                        "for configuration %s!" % pipeline_config_path)

    # sanitize path data by passing it through the ShotgunPath
    shotgun_paths = {}
    for storage_name in data:
        shotgun_paths[storage_name] = ShotgunPath.from_shotgun_dict(data[storage_name])

    return shotgun_paths


class PathConfig(object):
    """Represents a pipeline configuration.

    Use the factory methods in pipelineconfig_factory
    to construct this object, do not create directly via the constructor.
    """

    def __init__(self, pipeline_configuration_path, project_name, descriptor=None):
        """
        Constructor. Do not call this directly, use the factory methods
        in pipelineconfig_factory.

        NOTE ABOUT SYMLINKS!

        The pipeline_configuration_path is always populated by the paths
        that were registered in shotgun, regardless of how the symlink setup
        is handled on the OS level.

        :param str pipeline_configuration_path: Path to the pipeline configuration on disk.
        :param descriptor: Descriptor that was used to create this pipeline configuration. 
            Defaults to ``None`` for backwards compatibility with Bootstrapper that only
            pass down one argument. Also this argument was passed down by cores from
            v0.18.72 to 0.18.94. The descriptor is now read from the disk inside
            pipeline_configuration.yml.
        :type descriptor: :class:`sgtk.descriptor.ConfigDescriptor`
        """
        self._project_name = project_name
        self._pc_root = pipeline_configuration_path
        self._roots = get_roots_metadata(self._pc_root)

        # keep a storage roots object interface instance in order to query roots
        # info as needed
        config_folder = os.path.join(
                                    self._pc_root,
                                    dsk_constants.ENVI_TEMPLATE_NAME)
        self._storage_roots = StorageRoots.from_config(config_folder)
        if self._storage_roots.required_roots and not self._storage_roots.default_path:
            raise DevError(
                "Could not identify a default storage root for this pipeline "
                "configuration! File: '%s'" % (self._storage_roots.roots_file,)
            )

    def get_all_platform_data_roots(self):
        """
        Similar to get_data_roots but instead of returning the data roots for a single 
        operating system, the data roots for all operating systems are returned.
        
        The return structure is a nested dictionary structure, for example:

        {
         "primary": {"win32":  "z:\studio\my_project", 
                     "linux2": "/studio/my_project",
                     "darwin": "/studio/my_project"},
                     
         "textures": {"win32":  "z:\studio\my_project", 
                      "linux2": None,
                      "darwin": "/studio/my_project"},
        }
         
        The operating system keys are returned on sys.platform-style notation.
        If a data root has not been defined on a particular platform, None is 
        returned (see example above).

        @todo - refactor to use ShotgunPath

        :returns: dictionary of dictionaries. See above.
        """
        proj_roots = {}
        for storage_name in self._roots:
            # join the project name to the storage ShotgunPath
            project_path = self._roots[storage_name].join(self._project_name)
            # break out the ShotgunPath object in sys.platform style dict
            proj_roots[storage_name] = project_path.as_system_dict()

        return proj_roots

    def get_templates_config(self):
        """
        Returns the templates configuration as an object
        """
        templates_file = os.path.join(self._pc_root,
                                      dsk_constants.ENVI_TEMPLATE_NAME,
                                      dsk_constants.ENVI_NAMING_CORE,
                                      dsk_constants.CONTENT_TEMPLATES_FILE)

        try:
            data = yaml_cache.g_yaml_cache.get(templates_file, deepcopy_data=False) or {}
            data = template_includes.process_includes(templates_file, data)
        except DevUnreadableFileError:
            data = dict()

        return data

    def get_primary_data_root_name(self):
        """
        Returns the default root name as defined by the required roots for this
        configuration.

        :returns: str name of a storage root
        """
        # return self._roots
        return self._storage_roots.default