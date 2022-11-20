# -*- coding:utf-8 -*-

from src.lib.telegram_bot import TelegramBot
from src.utils.logger import Logger
from src.scraper.scraper import Scraper
from bot_replica.state import ReplicaState
from src.utils import constants

logger = Logger.getLogger()


class ReplicaTelegramBot(TelegramBot):
    __control_key: str = ""
    __replica_state: ReplicaState

    def __init__(self, token: str, mode: str, control_key: str = "", heroku_app_name: str = "", port: int = 8443) -> None:
        super().__init__(
            token=token,
            mode=mode,
            heroku_app_name=heroku_app_name,
            port=port
        )

        self.__control_key = control_key
        self.__replica_state = ReplicaState()

    # sends new announcements to the telegram chats: developed for the announcing to students/teachers/everybody about news
    def send_announcements_to_chats(self, context):
        try:
            lastAnnouncement = Scraper.get_announcement_id(0)
            if lastAnnouncement == -1:
                pass

            last = lastAnnouncement
            if self.__replica_state.get_last_announcement() > 0:
                last = self.__replica_state.get_last_announcement()

            newLast = lastAnnouncement
            i = 0
            list = []
            while last != newLast:
                list.append(newLast)
                i += 1
                if i > constants.MAX_ANNOUNCEMENT_NUMBER_PER_CHECK:
                    list.clear()
                    break
                newLast = Scraper.get_announcement_id(i)

            list.reverse()
            for value in list:
                message_text = '\nDUYURU: \n'
                message_text += Scraper.get_announcement_content_by_id(value)
                if self.__control_key in message_text:
                    logger.error(
                        '{0} id\'sine sahip duyuru kontrol keyini içeriyor, gruplara gönderilmedi.'.format(value))
                    continue

                for key in self.__replica_state.get_chats():
                    try:
                        context.bot.send_message(
                            chat_id=key, text=message_text)
                    except:
                        logger.error(
                            '{0} Chat id\'sine sahip sohbete duyuru gönderilemedi.'.format(key))

            self.__replica_state.set_last_announcement(lastAnnouncement)

        except Exception as e:
            logger.error("Siteden veri getirilemedi... \n {}".format(e))
