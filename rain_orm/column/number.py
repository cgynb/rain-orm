try:
    from rain_orm.column.base import Number
except ImportError:
    from base import Number


class TinyInt(Number):
    pass


class SmallInt(Number):
    pass


class MediumInt(Number):
    pass


class Int(Number):
    pass


class BigInt(Number):
    pass


class Float(Number):
    pass


class Double(Number):
    pass


class Decimal(Number):
    pass
