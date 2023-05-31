try:
    from rain_orm.error import DefineError, SqlBuildError, UpdateError
    from rain_orm.sql_builder import DMLDQLBuilder
    from rain_orm.db import DB
except ImportError as e:
    print(e)
    from error import DefineError, SqlBuildError, UpdateError
    from sql_builder import DMLDQLBuilder
    from db import DB
import pymysql
import threading
import copy


class Table(object):
    __db = None
    __lock = threading.Lock()

    @classmethod
    def set_db(cls, db):
        cls.__db = db

    # @classmethod
    # def auto_migrate(cls):
    #     # TODO: DDL
    #     print(cls.__subclasses__())

    def __init__(self, **kwargs):
        if not isinstance(self.__table__, str):
            raise DefineError(f"type(__table__) should be str, but is {type(self.__table__)}")
        if not isinstance(self.__fields__, dict):
            raise DefineError(f"type(__fields__) should be dict, but is {type(self.__fields__)}")

        self.instance = copy.deepcopy(self.__fields__)
        self.__dmldql_builder = DMLDQLBuilder(self.__table__)
        for k, v in kwargs.items():
            self.instance[k] = v

    def __str__(self):
        table = self.__table__
        instance = "{\n"
        for k, v in self.instance.items():
            instance += f"\t\t{k}: {v},\n"
        instance += "\t}"
        return f"\033[0;36m<< {self.__class__.__name__} {id(self)}\033[0m\n" \
               f"\t\033[0;32m.table\033[0m = {table}\n" \
               f"\t\033[0;32m.instance\033[0m = {instance}\n" \
               f"\033[0;36m>>\033[0m\n"

    def __repr__(self):
        return str(self)

    def __getattr__(self, key):
        return self.instance.get(key)

    # update
    def __setattr__(self, key, value):
        if key in ["instance", "_Table__dmldql_builder"]:
            self.__dict__[key] = value
        else:
            self.update(key, value)

    # select condition
    def where(self, condition, value=None):
        self.__dmldql_builder.where(condition, value)
        return self

    # update
    def update(self, key, value):
        if self.instance.get(key) is None:
            raise UpdateError(f"there is no field called '{key}'")
        else:
            self.__dmldql_builder.clear_set()
            self.__dmldql_builder.set(**{key: value})
            self.__dmldql_builder.clear_where()
            for field, val in self.instance.items():
                v = f"'{val}'" if isinstance(val, str) else val
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
                    self.instance[key] = value
                    return True

    # select
    def one(self):
        target = sorted(self.instance.keys()) if len(
            self.__dmldql_builder.select_items) == 0 else self.__dmldql_builder.select_items
        self.__dmldql_builder.select(*sorted(self.instance.keys()))
        with self.__lock:
            try:
                self.__db.cursor.execute(self.__dmldql_builder.select_sql)
                data = self.__db.cursor.fetchone()
            except pymysql.MySQLError as e:
                print(e)
                self.__db.rollback()
        if data is not None:
            for field, key in zip(data, target):
                self.instance[key] = field
            return self
        else:
            return None

    # select
    def all(self):
        new_instances = list()
        target = sorted(self.instance.keys()) if len(
            self.__dmldql_builder.select_items) == 0 else self.__dmldql_builder.select_items
        self.__dmldql_builder.select(*sorted(self.instance.keys()))
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
                new_instance.instance[key] = field
            new_instances.append(new_instance)
        return new_instances

    # insert
    def create(self):
        self.__dmldql_builder.set(**self.instance)
        with self.__lock:
            try:
                self.__db.cursor.execute(self.__dmldql_builder.insert_sql)
                self.instance["id"] = self.__db.insert_id()
                self.__db.commit()
            except pymysql.MySQLError as e:
                print(e)
                self.__db.rollback()
                return False
            else:
                return True

    def delete(self):
        self.__dmldql_builder.clear_where()
        for field, val in self.instance.items():
            if isinstance(val, str):
                self.__dmldql_builder.where(f"{field} = '{val}'")
            elif val is None:
                self.__dmldql_builder.where(f"{field} is null")
            else:
                self.__dmldql_builder.where(f"{field} = {val}")
        with self.__lock:
            try:
                self.__db.cursor.execute(self.__dmldql_builder.delete_sql)
                self.__db.commit()
            except pymysql.MySQLError as e:
                print(e)
                self.__db.rollback()
                return False
            else:
                for key in self.instance.keys():
                    self.instance[key] = None
                return True

