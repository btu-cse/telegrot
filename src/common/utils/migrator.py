from src.bot_replica.entity.admin import Admin
from src.bot_replica.entity.announcement import Announcement
from src.bot_replica.entity.chat import Chat

def migrator(db):
    with db:
        db.create_tables([
            Admin,
            Announcement,
            Chat
        ])