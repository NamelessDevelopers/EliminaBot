class BaseDbException(BaseException):
    """Base class for Database Exceptions."""

    pass


class PrimaryKeyViolationError(BaseDbException):
    """Error raised when a primary key constraint is violated"""

    pass


class EntityNotFoundError(BaseDbException):
    """Error raised when an entity is not found upon query."""

    pass
