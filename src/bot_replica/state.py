from typing import List
from src.bot_replica.entity.chat import Chat
from src.utils.db import DB


class ReplicaState:
    __last_announcement: int
    __chats: List[Chat]
    __db: DB

    def __init__(self, db: DB) -> None:
        self.__db = db
        self.migrate(self.__db)

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

    def migrate(self, db: DB):
        try:
            mycursor = mydb.cursor()
            mycursor.execute(
                "SELECT lastAnnouncement, chatIDs FROM data WHERE id=1 ")
            result = mycursor.fetchall()
            STATE["chatIDs"] = eval(result[0][1])
            STATE["lastAnnouncement"] = result[0][0]
            mycursor.close()

        except Exception as e:
            if STATE['lastAnnouncement'] == "0":
                STATE['lastAnnouncement'] = getAnnouncement(
                    0).get('href').split('&')[1].split('=')[1]
            print("Uzak sunucudan veri getirilemedi. \n " + e)