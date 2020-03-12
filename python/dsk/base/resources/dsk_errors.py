"""
All custom exceptions that Dsk emits are defined here.
"""


class DskError(Exception):
    """
    Top level exception for all toolkit-core level runtime errors
    """

class DskErrorPython2or3Only(DskError):
    """
    Exception indicating that this is version of python is not supported
    """

class DskInitError(DskError):
    """
    Exception indicating initialization failure.
    """


class DskUnreadableFileError(DskError):
    """
    Exception that indicates that a required file can't be read from disk.
    """


class DskFileDoesNotExistError(DskUnreadableFileError):
    """
    Exception that indicates that a required file does not exist.
    """

class DskFileErr(DskUnreadableFileError):
    pass

class DskNoDefaultValueError(DskError):
    """
    Exception that can be raised when a default value is required but none is found.
    """


class DskHookMethodDoesNotExistError(DskError):
    """
    Exception that indicates that a called method does not exist in the hook.
    """


class DskInvalidCoreLocationError(DskError):
    """
    Exception that indicates the core location file contained an invalid path.
    """


class DskLaunchError(DskError):
    """
    Exception that indicates that Some trouble launching
    """





class DskNotPipelineConfigurationError(DskError):
    """
    Exception that indicates that a folder doesn't contain a pipeline configuration.
    """

class DirmapError(DskError):
    """
    mapping between platform not supported
    """


class DskErrorProjectIsSetup(DskError):
    """
    Exception that indicates that a project already has a toolkit name but no pipeline configuration.
    """

    def __init__(self):
        """
        Include error message
        """
        super(DskErrorProjectIsSetup, self).__init__(
            "You are trying to set up a project which has already been set up. "
            "If you want to do this, make sure to set the force parameter."
        )


class DskContextDeserializationError(DskError):
    """
    Exception that indicates that something went wrong while deserializating a context.
    """


class DskMultipleMatchingTemplatesError(DskError):
    """
    Exception that indicates that a path matches multiple templates.
    """

class EnvironmentVariableFileLookupError(DskError):
    """
    Raised when an environment variable specifying a location points to configuration
    file that doesn't exist.
    """

    def __init__(self, var_name, path):
        """
        :param str var_name: Name of the environment variable used.
        :param str path: Path to the configuration file that doesn't exist.
        """
        super(EnvironmentVariableFileLookupError,self).__init__(
                    "The env variable '%s' refers to a configuration file on disk at '%s' that doesn't exist." 
                    % ( var_name, path))


class ShotgunAttachmentDownloadError(DskError):
    """
    Raised when a Shotgun attachment could not be downloaded
    """

class DskMultipleMatchingTemplatesError(DskError):
    """
    Exception that indicates that a path matches multiple templates.
    """

class UnresolvableCoreConfigurationError(DskError):
    """
    Raises when Toolkit is not able to resolve the path
    """

    def __init__(self, full_path_to_file):
        """
        :param str full_path_to_file: Path to the folder where shotgun.yml was expected.
        """
        DskError.__init__(
            self,
            "Cannot resolve the core configuration from the location of the Sgtk Code! "
            "This can happen if you try to move or symlink the Sgtk API. The "
            "Sgtk API is currently picked up from %s which is an "
            "invalid location." % full_path_to_file
         )
