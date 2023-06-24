import datetime

try:
    from rain_orm.error import DefineError, SqlBuildError, UpdateError
    from rain_orm.sql_builder import DMLDQLBuilder, DDLBuilder
    from rain_orm.column import Type
    from rain_orm.db import DB
    from rain_orm.metatable import MetaTable
except ImportError as e:
    print(e)
    from error import DefineError, SqlBuildError, UpdateError
    from sql_builder import DMLDQLBuilder, DDLBuilder
    from column import Type
    from db import DB
    from metatable import MetaTable
import pymysql
import threading
import copy


class Table(metaclass=MetaTable):
    __db = None
    __lock = threading.Lock()
    __table__ = ""
    __fields__ = {}

    @classmethod
    def set_db(cls, db):
        cls.__db = db

    @classmethod
    def auto_migrate(cls, *classes):
        class_lst = classes if len(classes) > 0 else cls.__subclasses__()
        ddls = []
        for subcls in class_lst:
            ddl_builder = DDLBuilder(subcls.__table__)
            for k, v in subcls.__fields__.items():
                ddl_builder.add_field(field_name=k, field_type=v.type_name, **v.constraint)
            ddls.append(ddl_builder.create_sql)
        with cls.__lock:
            for ddl in ddls:
                cls.__db.cursor.execute(ddl)
            cls.__db.commit()

    def __init__(self, **kwargs):
        self.__instance = copy.deepcopy(self.__fields__)
        self.__dmldql_builder = DMLDQLBuilder(self.__table__)
        for k, v in kwargs.items():
            self.__instance[k].value = v
        self.is_none = False

    def __str__(self):
        if self.is_none is True:
            return "None"
        table = self.__table__
        fields = list(self.__fields__.keys())
        instance = "{\n"
        for k, v in self.__instance.items():
            if isinstance(v.value, (str, datetime.datetime)):
                v = f"'{v.value}'"
            instance += f"\t\t{k}: {v},\n"
        instance += "\t}"
        return f"\033[0;36m<< {self.__class__.__name__} {id(self)}\033[0m\n" \
               f"\t\033[0;32m.table\033[0m = {table}\n" \
               f"\t\033[0;32m.fields\033[0m = {fields}\n" \
               f"\t\033[0;32m.instance\033[0m = {instance}\n" \
               f"\033[0;36m>>\033[0m\n"

    def __repr__(self):
        return str(self)

    def __getattr__(self, key):
        return self.__instance.get(key).value

    # update
    def __setattr__(self, key, value):
        if key in ["_Table__instance", "_Table__dmldql_builder", "is_none"]:
            self.__dict__[key] = value
        else:
            self.update(key, value)

    @property
    def instance(self):
        ins = dict()
        for k, v in self.__instance.items():
            ins[k] = v.value
        return ins

    # select condition
    def where(self, condition, value=None):
        self.__dmldql_builder.where(condition, value)
        return self

    # select
    def one(self):
        target = sorted(self.__instance.keys()) if len(
            self.__dmldql_builder.select_items) == 0 else self.__dmldql_builder.select_items
        self.__dmldql_builder.select(*sorted(self.__instance.keys()))
        data = None
        with self.__lock:
            try:
                self.__db.cursor.execute(self.__dmldql_builder.select_sql)
                data = self.__db.cursor.fetchone()
            except pymysql.MySQLError as e:
                print(e)
                self.__db.rollback()
        if data is not None:
            for field, key in zip(data, target):
                self.__instance[key].value = field
            return self
        else:
            return None

    # select
    def all(self):
        new_instances = list()
        target = sorted(self.__instance.keys()) if len(
            self.__dmldql_builder.select_items) == 0 else self.__dmldql_builder.select_items
        self.__dmldql_builder.select(*sorted(self.__instance.keys()))
        with self.__lock:
            try:
                self.__db.cursor.execute(self.__dmldql_builder.select_sql)
                datas = self.__db.cursor.fetchall()
            except pymysql.MySQLError as e:
                print(e)
                self.__db.rollback()
        for data in datas:
            new_instance = self.__class__()
            for field, key in zip(data, target):
                new_instance.__instance[key].value = field
            new_instances.append(new_instance)
        return new_instances

    # insert
    def create(self):
        raw_instance = dict()
        for k, v in self.__instance.items():
            raw_instance[k] = v.value
        self.__dmldql_builder.set(**raw_instance)
        with self.__lock:
            try:
                self.__db.cursor.execute(self.__dmldql_builder.insert_sql)
                self.__instance["id"].value = self.__db.insert_id()
                self.__db.commit()
            except pymysql.MySQLError as e:
                print(e)
                self.__db.rollback()
                return False
            else:
                return True

    # update
    def update(self, key, value):
        if self.__instance.get(key) is None:
            raise UpdateError(f"there is no field called '{key}'")
        else:
            self.__dmldql_builder.clear_set()
            self.__dmldql_builder.set(**{key: value})
            self.__dmldql_builder.clear_where()
            for field, val in self.__instance.items():
                v = f"'{val.value}'" if isinstance(val.value, (str, datetime.datetime)) else val
                self.__dmldql_builder.where(f"{field} = {v}")
            with self.__lock:
                try:
                    self.__db.cursor.execute(self.__dmldql_builder.update_sql)
                    self.__db.commit()
                except pymysql.MySQLError as e:
                    print(e)
                    self.__db.rollback()
                    return False
                else:
                    self.__instance[key].value = value
                    return True

    # delete
    def delete(self):
        self.__dmldql_builder.clear_where()
        for field, val in self.__instance.items():
            if isinstance(val.value, (str, datetime.datetime)):
                self.__dmldql_builder.where(f"{field} = '{val.value}'")
            elif val.value is None:
                self.__dmldql_builder.where(f"{field} is null")
            else:
                self.__dmldql_builder.where(f"{field} = {val.value}")
        with self.__lock:
            try:
                self.__db.cursor.execute(self.__dmldql_builder.delete_sql)
                self.__db.commit()
            except pymysql.MySQLError as e:
                print(e)
                self.__db.rollback()
                return False
            else:
                self.is_none = True
                return True

