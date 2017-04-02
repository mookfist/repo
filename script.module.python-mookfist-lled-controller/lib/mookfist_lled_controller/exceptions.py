"""Exceptions"""

class NoBridgeFound(Exception):
    """Thrown when no bridge can found"""
    pass


class UnsupportedVersion(Exception):
    """Throw when an unsuppoted version is used"""
    pass


class InvalidGroup(Exception):
    """Thrown when using an invalid group"""
    pass
