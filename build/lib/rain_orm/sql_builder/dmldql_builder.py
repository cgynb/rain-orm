from rain_orm.error import SqlBuildError


class DMLDQLBuilder:
    operations = ["select", "insert", "update", "delete"]

    def __init__(self, table, op=None):
        self.__sql_str = None
        self.table = table
        self.op = op
        self.__select_items = list()
        self.__conditions = list()
        self.__set_fields_values = dict()
        self.__orders = list()
        self.__limit_num = None
        self.__offset_num = None

    def __str__(self):
        if self.__sql_str is None:
            return self.sql
        else:
            return self.__sql_str

    def __repr__(self):
        return str(self)

    def set_operation(self, op):
        self.op = op

    def select(self, *args):
        for t in args:
            if not isinstance(t, str):
                raise SqlBuildError("args should be str")
        for t in args:
            self.__select_items.append(t)
        return self

    def where(self, condition, value=None):
        if isinstance(value, str):
            value = f"'{value}'"
        cond_str = condition.replace("?", str(value))
        self.__conditions.append(cond_str)
        return self

    def clear_where(self):
        self.__conditions.clear()

    def set(self, **kwargs):
        self.__set_fields_values = kwargs
        return self

    def clear_set(self):
        self.__set_fields_values.clear()

    def limit(self, num=None):
        if isinstance(num, int):
            self.__limit_num = num
        elif num is not None:
            raise SqlBuildError("limit num should be int or None")
        return self

    def offset(self, num=None):
        if isinstance(num, int):
            self.__offset_num = num
        elif num is not None:
            raise SqlBuildError("limit num should be int or None")
        return self

    def order_by(self, by=None, asc=True):
        if isinstance(by, str) and isinstance(asc, bool):
            self.__orders.append({
                "by": by,
                "asc": asc
            })
        elif by is not None:
            raise SqlBuildError("by should be str or None")
        return self

    @property
    def sql(self):
        if self.op not in self.operations:
            raise SqlBuildError("operation should be in ['select', 'insert', 'update', 'delete']")
        else:
            if self.op == "select":
                self.__sql_str = self.select_sql
            elif self.op == "insert":
                self.__sql_str = self.insert_sql
            elif self.op == "update":
                self.__sql_str = self.update_sql
            elif self.op == "delete":
                self.__sql_str = self.delete_sql
        return self.__sql_str

    @property
    def select_sql(self):
        return f"select {self.__select_str} from {self.table} {self.__condition_str} {self.__order_str} {self.__limit_str} {self.__offset_str};"

    @property
    def insert_sql(self):
        if len(self.__set_fields_values) == 0:
            raise SqlBuildError("insert operation should take fields and values, but there are not defined")
        return f"insert into {self.table} ({self.__field_str}) values ({self.__value_str});"

    @property
    def update_sql(self):
        if len(self.__set_fields_values) != 1:
            raise SqlBuildError("update operation should only set 1 field")
        return f"update {self.table} set {self.__field_str} = {self.__value_str} {self.__condition_str}"

    @property
    def delete_sql(self):
        if len(self.__conditions) == 0:
            raise SqlBuildError("delete operation should take at least 1 condition")
        return f"delete from {self.table} {self.__condition_str}"

    @property
    def __select_str(self):
        if len(self.__select_items) == 0:
            return "*"
        else:
            self.__select_items.sort()
            return f"{', '.join(self.__select_items)}"

    @property
    def __condition_str(self):
        if len(self.__conditions) == 0:
            return ""
        else:
            return f"where {' and '.join(self.__conditions)}"

    @property
    def __order_str(self):
        if len(self.__orders) == 0:
            return ""
        else:
            return "order by " + ' ,'.join([f"{item['by']} {'asc' if item['asc'] else 'desc'}" for item in self.__orders])

    @property
    def __limit_str(self):
        if self.__limit_num is None:
            return ""
        else:
            return f"limit {self.__limit_num}"

    @property
    def __offset_str(self):
        if self.__limit_num is None or self.__offset_num is None:
            return ""
        else:
            return f"offset {self.__offset_num}"

    @property
    def __field_str(self):
        return ', '.join([item for item in self.__set_fields_values.keys() if self.__set_fields_values.get(item) is not None])

    @property
    def __value_str(self):
        return ', '.join(list(
                            map(
                                lambda item: f"'{item}'" if isinstance(item, str) else str(item),
                                [item for item in self.__set_fields_values.values() if item is not None]
                            )))

    @property
    def select_items(self):
        return self.__select_items


if __name__ == "__main__":
    s_select = SqlBuilder(table="table")
    s_select.select("id", "name").where("id < 500").order_by("id", asc=False).limit(2).offset(9)
    print(s_select.select_sql)

    s_insert = SqlBuilder(table="table")
    s_insert.set(id=1, age=18)
    print(s_insert.insert_sql)

    s_update = SqlBuilder(table="table")
    s_update.where("id = ?", 1).set(age=19)
    print(s_update.update_sql)

    s_delete = SqlBuilder(table="table")
    s_delete.where("age < ?", 18)
    print(s_delete.delete_sql)
