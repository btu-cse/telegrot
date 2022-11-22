from peewee import IntegerField, AutoField
from src.common.base_model import BaseModel


class Announcement(BaseModel):
    id = AutoField()
    announcement = IntegerField()
