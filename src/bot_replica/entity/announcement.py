from peewee import IntegerField, AutoField
from src.common.base_model import BaseModel


class Announcement(BaseModel):
    id = AutoField()
    announcement = IntegerField()

    def __str__(self):
        return str(self.announcement)

    def __repr__(self):
        return str(self.announcement)

    def toJson(self):
        yield {
            "id": self.id,
            "announcement": self.announcement,
        }.items()
