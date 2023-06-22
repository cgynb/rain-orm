class DDLBuilder:
    def __init__(self, table):
        self.table = table
        self.__sql_str = None
        self.__fields = []

    def add_field(self, field_name, field_type, *, primary_key=False, unique=False, not_null=False,
                  auto_increment=False):
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
