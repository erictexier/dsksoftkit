
class DevError(Exception):
    """Top level exception for all core level runtime errors
    """

class DevDescriptorError(DevError):
    """
    Base class for all descriptor related errors.
    """

    pass

class DevUnreadableFileError(DevError):
    """Exception that indicates that a required file can't be read from disk.
    """

class DevFileDoesNotExistError(DevUnreadableFileError):
    """Exception that indicates that a required file does not exist.
    """

class DevNoDefaultValueError(DevError):
    """Exception that can be raised when a default value is required but none is found.
    """

