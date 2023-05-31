# rain-orm

a tiny orm frame

# Install

it's easy to install via pip

```cmd
pip install rain-orm
```

# Simple Example

assume you have "students" table in "student_management" database

students

| id  | name | password | class_id |
|-----|------|----------|----------|
|     |      |          |          |

```python
import rain_orm

rain_orm.connect(host="you host", port=3306, user="root", password="your password", database="student_management")


class StudentModel(rain_orm.Table):
    __table__ = "students"
    __instance__ = {
        "id": None,
        "name": None,
        "password": None,
        "class_id": None
    }

if __name__ == "__main__":
    stu = StudentModel().where("id=?", 1).one()
    print(stu)
```
result

```cmd
<<StudentModel 2109293369984
    .table = students
    .instance = {
        id: 1,
        name: cgy,
        password: None,
        class_id: 1,
    }
>>
```

# Basic Usage

it's easy to use rain-orm

1. import rain_orm
2. connect to database
3. define model class that inherits class rain_orm.Table
4. define two attribute "\_\_table__" and "\_\_instance__"
5. use rain-orm API

## Import
```python
import rain_orm
```

## Connect
```python
rain_orm.connect(host="you host", port=3306, user="root", password="your password", database="student_management")
```

## Define Model

each data must have a unique "id"
```python
class StudentModel(RainORM):
    __table__ = "students"
    __fields__ = {
        "id": None,
        "name": None,
        "password": None,
        "class_id": None
    }
```

## CRUD Example

### Read

```python
# student list
stu_lst = StudentModel().all()
# student whose id equals 1 with all fields
stu1 = StudentModel().where("id = ?", 1).one()
# student whose id equals 1 with all fields
stu2 = StudentModel().where("id = 1").one()
```

### Create

```python
stu = StudentModel(name="name", password="123", class_id=1234)  # set student
ok = stu.create()
print("ok:", ok)
print(stu)
```
result:
```
ok: True
<< StudentModel 2449383681440
	.table = students
	.fields = ['id', 'name', 'password', 'class_id']
	.instance = {
		id: 30,
		name: jack,
		password: 123456,
		class_id: 1,
	}
>>
```

### Update

there 2 ways to update data

```python
StudentModel().where("id = ?", 22).one()  # get student instance first
# 1. set attribute (recommend)
stu.name = "your name"
# 2. call update methods
ok = stu.update("name", "your name")
```

### Delete

```python
StudentModel().where("id = ?", 22).one()  # get student instance first
ok = stu.delete()  # call delete method
```