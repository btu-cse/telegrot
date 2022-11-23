from peewee import IntegerField, CharField, AutoField
from src.common.base_model import BaseModel


class Chat(BaseModel):
    id = AutoField()
    name = CharField(255)
    telegram_id = IntegerField(unique=True)

    def __eq__(self, other):
        return self.id == other.id
