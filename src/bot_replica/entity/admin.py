from peewee import IntegerField, CharField, AutoField
from src.common.base_model import BaseModel

class Admin(BaseModel):
    id = AutoField()
    name = CharField(255)
    telegram_id = IntegerField(unique=True)
