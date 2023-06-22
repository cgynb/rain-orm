class BasicError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return self.value


class DefineError(BasicError):
    pass


class SqlBuildError(BasicError):
    pass


class UpdateError(BasicError):
    pass
