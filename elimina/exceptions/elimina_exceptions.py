class BaseEliminaException(Exception):
    """
    Base Class for Elimina Exceptions.
    """

    pass


class TimeValueError(BaseEliminaException):
    """
    Exception thrown when the `time` for the `timer` command is not in the 1-300s range
    """

    def __init__(self, time: int) -> None:
        self.time = time
