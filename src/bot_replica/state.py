from typing import List
from src.bot_replica.entity.chat import Chat
from src.bot_replica.entity.announcement import Announcement
from src.common.logger import Logger

logger = Logger.getLogger()

class ReplicaState:
    __last_announcement: int
    __chats: List[Chat]

    def __init__(self) -> None:
        self.migrate()

    def set_last_announcement(self, last_announcement: int) -> None:
        self.__last_announcement = last_announcement

    def get_last_announcement(self) -> int:
        return self.__last_announcement

    def set_chats(self, chats: List[Chat]) -> None:
        self.__chats = chats

    def get_chats(self) -> List[Chat]:
        return self.__chats

    def append_chat(self, chat: Chat) -> None:
        self.__chats.append(chat)

    def remove_chat(self, chat: Chat) -> None:
        try:
            self.__chats.remove(chat)
        except:
            pass

    def migrate(self):
        try:
            query = (Announcement
                     .select()
                     .order_by(Announcement.id.desc())
                     .limit(1)
                     )
            logger.info(query)
        except Exception as e:
            print("hata var. \n ", e)
