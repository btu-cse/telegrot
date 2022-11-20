from peewee import Model, IntegerField, CharField, AutoField
from src.utils.db import DB


class Admin(Model):
    id = AutoField()
    name = CharField(255)
    telegram_id = IntegerField()

    class Meta:
        database = DB.get_default_db()
