# -*- coding:utf-8 -*-
from datetime import datetime
import json

from src.common.utils.json import json_dumper
from src.common.telegram_bot import TelegramBot
from src.common.logger import Logger
from src.scraper.scraper import Scraper
from src.bot_replica.state.state import ReplicaState
from src.common import constants
from src.bot_replica.entity.chat import Chat
from src.bot_replica.entity.admin import Admin
from src.common.utils.migrator import migrator
from src.common.db import DB

from telegram.ext import CommandHandler, CallbackQueryHandler, CallbackContext


class ReplicaTelegramBot(TelegramBot):
    __control_key: str = ""
    __replica_state: ReplicaState

    def __init__(self, token: str, mode: str, control_key: str = "", web_hook_url: str = "", port: int = 80) -> None:
        super().__init__(
            token=token,
            mode=mode,
            web_hook_url=web_hook_url,
            port=port
        )

        self.__control_key = control_key
        migrator(DB().get_default_db())

        Logger.init("replica_bot")
        self.__replica_state = ReplicaState()
        self.run()

    # sends new announcements to the telegram chats: developed for the announcing to students/teachers/everybody about news
    def send_announcements_to_chats(self, context):
        try:

            lastAnnouncement = Scraper.get_last_announcement_id()
            if lastAnnouncement == -1:
                pass
            last = lastAnnouncement
            if self.__replica_state.announcement.get_last_announcement_as_id() != -1:
                last = self.__replica_state.announcement.get_last_announcement_as_id()

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
                if self.__control_key != "" and self.__control_key in message_text:
                    Logger.info(
                        'announcement {} is contains CONTROL_KEY, this will not sent to the chats'.format(value))
                    continue

                for chat in self.__replica_state.chat.get_chats():
                    try:
                        context.bot.send_message(
                            chat_id=chat.telegram_id, text=message_text)
                        Logger.info(
                            'new announcement {} sent to the chat {}'.format(value, chat))

                    except:
                        Logger.error(
                            'cannot send the announcement to the chat id = {}, name = {} '.format(chat.telegram_id, chat.name))

            self.__replica_state.announcement.set_last_announcement(
                lastAnnouncement)

        except Exception as e:
            print(e)
            Logger.error(
                "there is an error while sending announcements to the chats %s", e)

    def help_command(self, update, context):
        """Send a message when the command /help is issued."""

        help_message = "Mevcut komutları aşağıdaki listeden görebilirsin. \n"
        help_message += "Komut çalıştırmak için \"/\" karakteri ile gerekli komutu yazmalısın.\n"
        help_message += "Mevcut komutlar; \n\n"
        help_message += "/yaz - Sözlükte bulunan grupları konsola yazar::YALNIZCA SAHİP ve YÖNETİCİ\n"
        help_message += "/hakkinda - Geliştirici ekibi hakkında bilgi verir\n"
        help_message += "/yardim - Tüm komutları görmek istiyorum\n"
        help_message += "/ekle - Grubu duyurucuya ekler::YALNIZCA SAHİP ve YÖNETİCİ\n"
        help_message += "/cikar - Grubu duyurucudan çıkarır::YALNIZCA SAHİP ve YÖNETİCİ\n"
        help_message += "/web - BTÜ BM Web sayfası\n"

        update.message.reply_text(help_message)

    def about_command(self, update, context):
        update.message.reply_text("Duyuru botumuz, bölüm mezunumuz Fatih Ateş ve Arş. Gör. Ahmet Kaşif tarafından geliştirilmiştir. Öneri ve istekleriniz için : @ahmetkasif {}".format(
            str(ReplicaTelegramBot.new_question_message())), reply_markup=ReplicaTelegramBot.new_question_keyboard())

    def web_command(self, update, context):
        update.message.reply_text("Bölüm Web sayfamıza https://mdbf.btu.edu.tr/bilgisayar adresinden erişebilirsiniz. {}".format(
            str(ReplicaTelegramBot.new_question_message())), reply_markup=ReplicaTelegramBot.new_question_keyboard())

    def add_command(self, update, context):
        user = context.bot.getChatMember(
            update.message.chat.id, update.message.from_user['id'])

        if user.status == "creator" or user.status == "administrator":
            try:
                _ = self.__replica_state.chat.get_chats().index(
                    Chat(telegram_id=update.message.chat.id))
                update.message.reply_text(
                    "Şu an bu sohbet duyurucuya zaten kayıtlı.")
            except ValueError:
                if self.__replica_state.chat.append_chat(Chat(telegram_id=update.message.chat.id, name=update.message.chat.title)):
                    update.message.reply_text("Komut başarıyla çalıştırıldı.")
                    Logger.info("manager added chat. chat {}, user => {}".format(update.message.chat,
                                                                                 update.message.from_user))
                else:
                    Logger.info("someone tried to add chat but it failed. chat {}, user => {}".format(update.message.chat,
                                                                                                      update.message.from_user))
                    update.message.reply_text(
                        "Komut çalıştırılırken bilinmeyen bir hata oluştu.")

            except Exception as e:
                Logger.error("there is an error while adding a new group %s", e)
                update.message.reply_text(
                    "Komut çalıştırma başarısız oldu.")

        else:
            Logger.info("someone who is not manager on the chat tried to add chat {}, user => {}".format(update.message.chat,
                                                                                                         update.message.from_user))
            update.message.reply_text(
                "Yalnızca admin ve yöneticiler komutları kullanabilir.")

    def remove_command(self, update, context):
        user = context.bot.getChatMember(
            update.message.chat.id, update.message.from_user['id'])

        if user.status == "creator" or user.status == "administrator":
            try:
                _ = self.__replica_state.chat.get_chats().index(
                    Chat(telegram_id=update.message.chat.id))

                if not self.__replica_state.chat.remove_chat(
                        Chat(telegram_id=update.message.chat.id, name=update.message.chat.title)):
                    raise Exception("this chat cannot be removed")
                update.message.reply_text(
                    "Grup duyurucudan başarıyla çıkartıldı.")
                Logger.info("chat removed from the list. chat => {}, user => {}".format(update.message.chat,
                                                                                        update.message.from_user))
            except ValueError:
                update.message.reply_text(
                    "Bu sohbet zaten listede değil.")

            except Exception as e:
                Logger.error("there is an error while removing a chat. chat => {}, user => {} %s".format(update.message.chat,
                                                                                                      update.message.from_user), e)
                update.message.reply_text(
                    "Komut çalıştırma başarısız oldu.")

        else:
            Logger.info("someone tried remove chat. chat => {}, user => {}".format(update.message.chat,
                                                                                   update.message.from_user))
            update.message.reply_text(
                "Yalnızca admin ve yöneticiler komutları kullanabilir.")

    def get_all_chats_command(self, update, context):
        self.__replica_state.admin.migrate_admins()
        member = context.bot.getChatMember(
            update.message.chat.id, update.message.from_user['id'])
        json_data = json.dumps(
            self.__replica_state.chat.get_chats(), indent=4, ensure_ascii=False, default=json_dumper)

        if member.status == "creator" or member.status == "administrator":
            message = "#### VERİ BAŞLANGIÇ - TARİH: " + \
                str(datetime.now()) + " \n" + \
                str(json_data) + " \n#### VERİ SON"

            try:
                _ = self.__replica_state.admin.get_admins().index(
                    Admin(telegram_id=update.message.from_user['id']))
                update.message.reply_text(message)
                Logger.info("admin dumped chats, user => {}".format(
                    update.message.from_user))
            except ValueError:
                Logger.info("chat manager tried to dump chats, but it failed, user => {}".format(
                    update.message.from_user))
                update.message.reply_text(
                    "Yalnızca veritabanında kayıtlı adminler bu komutu kullanabilir.")

        else:
            Logger.info("someone tried to dump chats, user => {}".format(
                update.message.from_user))
            update.message.reply_text(
                "Yalnızca admin ve yöneticiler komutları kullanabilir.")

    def run(self):

        # Telegramdan gönderilen komutlar için algılayıcılar oluşturuluyor
        self.add_handler(CommandHandler(
            "yaz", TelegramBot.Command(self.get_all_chats_command)))
        self.add_handler(CommandHandler(
            "hakkinda", TelegramBot.Command(self.about_command)))
        self.add_handler(CommandHandler(
            "yardim", TelegramBot.Command(self.help_command)))
        self.add_handler(CommandHandler(
            "ekle", TelegramBot.Command(self.add_command)))
        self.add_handler(CommandHandler(
            "cikar", TelegramBot.Command(self.remove_command)))
        self.add_handler(CommandHandler(
            "web", TelegramBot.Command(self.web_command)))
        self.add_handler(CallbackQueryHandler(
            self.new_question_callback, pattern='new_question_yes'))
        self.add_handler(CallbackQueryHandler(
            self.new_question_callback, pattern='new_question_no'))

        self.send_announcements_to_chats(CallbackContext(self._updater.dispatcher))

        super().run()
