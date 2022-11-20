from peewee import Model, IntegerField, AutoField
from src.utils.db import DB


class Announcement(Model):
    id = AutoField()
    announcement = IntegerField()

    class Meta:
        database = DB.get_default_db()
