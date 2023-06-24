from rain_orm import Table, connect
from rain_orm.column import Int, VarChar


class ClassModel(Table):
    __table__ = "classes"
    __fields__ = {
        "id": Int(primary_key=True, auto_increment=True),
        "name": VarChar(30)
    }


class StudentModel(Table):
    __table__ = "students"
    __fields__ = {
        "id": Int(primary_key=True, auto_increment=True),
        "name": VarChar(30, not_null=True),
        "class_id": Int(foreign_key=ClassModel.id)
    }


if __name__ == "__main__":
    connect(host="localhost", port=3306, user="root", password="123456", database="t")
    Table.auto_migrate()
    ClassModel(name="人工智能1班").create()
    StudentModel(name="cgy", class_id=1).create()
    sts = StudentModel().all()
    print(sts)

