"""
All pytoeba exceptions used by views and the api live here
"""


class PytoebaError(Exception):
    """
    Base class for all pytoeba exceptions. Inherit
    from this to create new exceptions.
    """
    pass


class UnknownUserError(PytoebaError):
    """
    Raised when a function that requires a User object
    isn't wrapped in a 'with work_as(User):' context
    manager that provides it.
    """
    pass


class NotEditableError(PytoebaError):
    """
    Raised when an edit operation is attempted on
    a locked object. Usually denoted by the
    is_editable attribute/field being set to false.
    """
    pass
