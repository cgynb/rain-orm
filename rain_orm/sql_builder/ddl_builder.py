class DDLBuilder:
    def __init__(self, table):
        self.table = table
        self.__sql_str = None
        self.__fields = []
        self.__foreign_keys = []

    def add_field(self, field_name, field_type, *, primary_key=False, unique=False, not_null=False,
                  auto_increment=False, foreign_key=None):
        self.__fields.append({
            "field_name": field_name,
            "field_type": field_type,
            "constraint": {
                "primary key": primary_key,
                "unique": unique,
                "not null": not_null,
                "auto_increment": auto_increment
            }
        })
        if foreign_key is not None:
            self.__foreign_keys.append({
                "field_name": field_name,
                "reference": foreign_key
            })

    @property
    def create_sql(self):
        sql = f"create table if not exists {self.table}"
        sql += "("
        for field in self.__fields:
            sql += f"{field['field_name']} {field['field_type']}"
            for k, v in field['constraint'].items():
                if v is not False:
                    sql += f" {k}"
            sql += ","
        for i, fk in enumerate(self.__foreign_keys, start=1):
            fk_name = f"{self.table}_{fk.get('reference').get('ref_table')}_{i}"
            sql += f"constraint {fk_name} foreign key ({fk.get('field_name')}) " \
                   f"references {fk.get('reference').get('ref_table')} ({fk.get('reference').get('ref_field')})"
            sql += ","
        sql = sql[:-1]
        sql += ")"
        return sql

    @property
    def drop_sql(self):
        sql = f"drop table if exists {self.table}"
        return sql

    @property
    def alter_sql(self):
        # TODO: alter sql
        sql = ""
        return sql
