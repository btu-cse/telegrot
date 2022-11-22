from peewee import Model
from src.common.db import DB


class BaseModel(Model):
    class Meta:
        database = DB().get_default_db()
