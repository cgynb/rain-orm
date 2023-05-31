import threading
import pymysql


class DB:
    __instance = None
    __lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if cls.__instance:
            return cls.__instance
        else:
            with cls.__lock:
                cls.__instance = super().__new__(cls)
                return cls.__instance

    def __init__(self, host, port, user, password, database):
        self.db = pymysql.connect(host=host, user=user, password=password, database=database, port=port)
        self.cursor = self.db.cursor()

    def insert_id(self):
        return self.db.insert_id()

    def commit(self):
        self.db.commit()

    def rollback(self):
        self.db.rollback()

    def __del__(self):
        self.db.close()

