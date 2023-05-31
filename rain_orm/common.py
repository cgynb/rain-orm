try:
    from rain_orm.db import DB
    from rain_orm.table import Table
except ImportError:
    from db import DB
    from table import Table


def connect(host, port, user, password, database):
    db = DB(host=host, user=user, password=password, database=database, port=port)
    Table.set_db(db)
