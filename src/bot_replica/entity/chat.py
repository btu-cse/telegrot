from peewee import Model, IntegerField, CharField, AutoField
from src.utils.db import DB


class Chat(Model):
    id = AutoField()
    name = CharField(255)
    telegram_id = IntegerField()

    class Meta:
        database = DB.get_default_db()

    def __eq__(self, other):
        return self.id == other.id