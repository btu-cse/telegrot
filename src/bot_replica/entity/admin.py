from peewee import IntegerField, CharField, AutoField
from src.common.base_model import BaseModel

class Admin(BaseModel):
    id = AutoField()
    name = CharField(255)
    telegram_id = IntegerField(unique=True)

    def __eq__(self, other):
        return self.telegram_id == other.telegram_id

    def __str__(self):
        return str(self.name)

    def __repr__(self):
        return str(self.name)