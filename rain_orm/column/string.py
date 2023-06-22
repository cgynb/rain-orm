try:
    from rain_orm.column.base import String
except ImportError:
    from base import String


class Char(String):
    pass


class VarChar(String):
    def __init__(self, length=255, **kwargs):
        super().__init__(**kwargs)
        self.length = length
        self.type_name = f"{self.type_name}({self.length})"


class TinyText(String):
    pass


class Text(String):
    pass


class MediumText(String):

    pass


class LongText(String):
    pass


# class TinyBlob(String):
#
#        pass


# class Blob(String):
#
#        pass


# class MediumBlob(String):
#
#        pass


# class LongBlob(String):
#
#        pass
