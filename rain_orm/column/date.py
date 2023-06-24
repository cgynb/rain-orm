try:
    from rain_orm.column.base import Date
except ImportError:
    from base import Date


class Time(Date):
    pass


class Year(Date):
    pass


class DateTime(Date):
    pass


class TimeStamp(Date):
    pass
