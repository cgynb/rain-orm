import warnings


class Type(object):
    type_name = None

    def __new__(cls, *args, **kwargs):
        cls.type_name = cls.__name__.casefold()
        return object.__new__(cls)

    def __init__(self, primary_key=False, unique=False, not_null=False, auto_increment=False, foreign_key=None,  default=None):
        self.__value = None
        self.default = default
        self.constraint = {
            "primary_key": primary_key,
            "auto_increment": auto_increment,
            "unique": unique,
            "not_null": not_null,
            "foreign_key": foreign_key
        }

    def __str__(self):
        return str(self.__value)

    def __repr__(self):
        return str(self)

    def check(self, val) -> bool:
        raise NotImplementedError

    @property
    def detail(self):
        return f"<<{self.type_name.upper()} value: {self.__value} constraint: {self.constraint}>>"

    @property
    def value(self):
        if self.__value is None:
            if callable(self.default):
                self.__value = self.default()
            else:
                self.__value = self.default
        return self.__value

    @value.setter
    def value(self, value):
        if not self.check(value):
            warnings.warn(f"data type is different from definition \"{self.type_name}\"")
        self.__value = value


class Number(Type):
    def check(self, val) -> bool:
        return isinstance(val, int) or isinstance(val, float) or val is None


class String(Type):
    def check(self, val):
        return isinstance(val, str) or val is None

# class Date()
