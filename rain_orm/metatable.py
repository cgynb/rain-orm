try:
    from rain_orm.error import DefineError, SqlBuildError, UpdateError
    from rain_orm.sql_builder import DMLDQLBuilder, DDLBuilder
    from rain_orm.column import Type
    from rain_orm.db import DB
except ImportError as e:
    print(e)
    from error import DefineError, SqlBuildError, UpdateError
    from sql_builder import DMLDQLBuilder, DDLBuilder
    from column import Type
    from db import DB


class MetaTable(type):
    def __new__(mcs, name, bases, namespace):
        if not isinstance(namespace.get('__table__'), str):
            raise ValueError(f"type(__table__) should be str, but is {type(namespace.get('__table__'))}")
        if not isinstance(namespace.get("__fields__"), dict):
            raise ValueError(f"type(__fields__) should be dict, but is {type(namespace.get('__fields__'))}")
        if not all([isinstance(item, Type) for _, item in namespace.get('__fields__').items()]):
            raise ValueError(f"items of __fields__ should be instance of rain_orm.column.Type")
        return type.__new__(mcs, name, bases, namespace)

    def __getattr__(cls, item):
        if item not in cls.__fields__.keys():
            raise ValueError(f"there's no field <{item}> in table {cls.__table__}")
        return {
            "ref_table": cls.__table__,
            "ref_field": item
        }


