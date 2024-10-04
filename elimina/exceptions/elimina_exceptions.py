class BaseEliminaException(Exception):
    pass


class TimeValueError(BaseEliminaException):
    def __init__(self, time: int) -> None:
        self.time = time
