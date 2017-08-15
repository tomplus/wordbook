
class DictError(Exception):

    def __init__(self, code, message=None):
        super().__init__(message)
        self.code = code


class DictConnectionError(DictError):
    pass


class InvalidDatabase(DictError):
    pass


class InvalidStrategy(DictError):
    pass


class ParseError(DictError):
    pass


