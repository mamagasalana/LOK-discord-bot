from peewee import Model, CharField, IntegerField, DateTimeField, BooleanField
from peewee import SqliteDatabase

db = SqliteDatabase('db.db')

class BaseModel(Model):
    class Meta:
        database = db

class Mine(BaseModel):
    _id = CharField(primary_key=True)
    code = IntegerField()  
    world = IntegerField()              
    x = IntegerField()              
    y = IntegerField()              
    level = IntegerField()
    state = IntegerField()
    expiry = DateTimeField()
    date = DateTimeField()
    occupied = BooleanField()

# Create tables
db.connect()
db.create_tables([Mine])