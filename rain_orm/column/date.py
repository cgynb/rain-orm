try:
    from rain_orm.column.base import Type
except ImportError:
    from base import Type


class Date(Type):
    pass


class Time(Type):
    pass


class Year(Type):
    pass


class DateTime(Type):
    pass


class TimeStamp(Type):
    pass
