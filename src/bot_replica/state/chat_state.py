from typing import List

from src.bot_replica.entity.chat import Chat
from src.common.logger import Logger
from src.scraper.scraper import Scraper

logger = Logger.getLogger()


class ChatState:
    __chats: List[Chat] = []

    def __init__(self) -> None:
        self.migrate()
        if len(self.__chats) > 0:
            logger.info("init state: chats => %s", self.__chats)

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

    def remove_chat(self, chat: Chat) -> bool:
        try:
            if not self.__remove_chat_from_db(chat):
                return False

            self.__chats.remove(chat)
            logger.info("removed chat id => {}, name => {}".format(
                chat.telegram_id, chat.name))
        except:
            pass
        
        return True

    def clear_chat(self) -> None:
        self.__chats = []

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
                    self.__chats.append(row)

        except Exception as e:
            logger.error(
                "there is an issue with the DB while migrating chat state", e)

    def __add_chat_to_db(self, chat: Chat) -> bool:
        try:
            count = (Chat
                     .select()
                     .where(Chat.telegram_id == chat.telegram_id)
                     .count()
                     )
            if count == 1:
                logger.info("chat was already inserted")
                return False

            _ = (Chat
                 .create(name=chat.name, telegram_id=chat.telegram_id)
                 )
        except Exception as e:
            logger.error(
                "there is an issue with the DB while adding a new chat", e)
            return False

        return True

    def __remove_chat_from_db(self, chat: Chat) -> bool:
        try:
            _ = (Chat
                     .delete()
                     .where(Chat.telegram_id == chat.telegram_id)
                     .execute()
                     )
        except Exception as e:
            logger.error(
                "there is an issue with the DB while removing a new chat", e)
            return False

        return True

    def migrate(self):
        try:

            self.migrate_chats()

        except Exception as e:
            logger.error(
                "there is an issue with the DB while migrating states", e)
