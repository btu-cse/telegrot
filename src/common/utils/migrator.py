from src.bot_replica.entity.admin import Admin
from src.bot_replica.entity.announcement import Announcement
from src.bot_replica.entity.chat import Chat

from src.common.logger import Logger

logger = Logger.getLogger()


def migrator(db):
    try:
        with db:
            db.create_tables([
                Admin,
                Announcement,
                Chat
            ])
    except Exception as e:
        logger.error("there is an error with migrations", e)
