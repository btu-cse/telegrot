from typing import List

from src.bot_replica.entity.chat import Chat
from src.bot_replica.entity.announcement import Announcement
from src.bot_replica.entity.admin import Admin
from src.common.logger import Logger
from src.scraper.scraper import Scraper

logger = Logger.getLogger()


class ReplicaState:
    __last_announcement: int = -1
    __chats: List[Chat] = []
    __admin: List[Admin] = []

    def __init__(self) -> None:
        self.migrate()

    def set_last_announcement(self, last_announcement: int) -> bool:
        if not self.__set_announcement_to_db(last_announcement):
            return False

        self.__last_announcement = last_announcement
        return True

    def get_last_announcement(self) -> int:
        return self.__last_announcement

    def set_chats(self, chats: List[Chat]) -> None:
        self.__chats = chats

    def get_chats(self) -> List[Chat]:
        return self.__chats

    def append_chat(self, chat: Chat) -> bool:
        if not self.__add_chat_to_db(chat):
            return False

        self.__chats.append(chat)
        logger.info("added new chat id => {}, name => {}".format(
            chat.telegram_id, chat.name))

        return True

    def remove_chat(self, chat: Chat) -> None:
        try:
            self.__chats.remove(chat)
        except:
            pass

    def clear_chat(self) -> None:
        self.__chats = []

    def migrate_last_announcement(self):
        try:
            row = (Announcement
                   .select()
                   .order_by(Announcement.id.desc())
                   .limit(1)
                   )

            if len(row) == 0:
                last_announcement = Scraper.get_last_announcement_id()
                if last_announcement == -1:
                    pass

                if self.__set_announcement_to_db(last_announcement):
                    self.__last_announcement = last_announcement
                else:
                    self.__last_announcement = -1
            else:
                self.__last_announcement = row[0]

        except Exception as e:
            logger.error(
                "there is an issue with the DB while migrating announcement state \n ", e)

    def migrate_chats(self):
        try:
            rows = (Chat
                    .select()
                    )

            if len(rows) == 0:
                logger.info("There is no Telegram chat in the DB")
            else:
                self.clear_chat()
                for row in rows:
                    self.append_chat(row)

        except Exception as e:
            logger.error(
                "there is an issue with the DB while migrating announcement state \n ", e)

    def migrate(self):
        try:

            self.migrate_last_announcement()
            self.migrate_chats()

        except Exception as e:
            logger.error(
                "there is an issue with the DB while migrating states \n ", e)

    def __add_chat_to_db(self, chat: Chat) -> bool:
        try:
            count = (Chat
                     .select()
                     .where(Chat.telegram_id == chat.telegram_id)
                     .count()
                     )
            if count == 0:
                logger.info("chat was already inserted \n ")
                return False

            _ = (Chat
                 .create(name=chat.name, telegram_id=chat.telegram_id)
                 )
        except Exception as e:
            logger.error(
                "there is an issue with the DB while adding a new chat \n ", e)
            return False

        return True

    def __set_announcement_to_db(self, last_announcement: int) -> bool:
        try:
            count = (Announcement
                     .select()
                     .count()
                     )
            if count == 0:
                id = (Announcement
                      .create(announcement=last_announcement)
                      )
            else:
                test = (Announcement
                        .update(announcement=last_announcement)
                        .order_by(Announcement.id.desc())
                        .limit(1)
                        .execute()
                        )
                logger.info(test)

        except Exception as e:
            logger.error(
                "there is an issue with the DB while setting new announcement \n ", e)
            return False

        return True
