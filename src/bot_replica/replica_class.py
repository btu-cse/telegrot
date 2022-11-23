# -*- coding:utf-8 -*-
from datetime import datetime
import json

from src.common.telegram_bot import TelegramBot
from src.common.logger import Logger
from src.scraper.scraper import Scraper
from src.bot_replica.state import ReplicaState
from src.common import constants
from src.bot_replica.entity.chat import Chat

from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext

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
        update.message.reply_text("Duyuru botumuz, bölüm öğrencimiz Fatih Ateş ve Arş. Gör. Ahmet Kaşif tarafından geliştirilmiştir. Öneri ve istekleriniz için : @ahmetkasif {}".format(
            str(ReplicaTelegramBot.new_question_message())), reply_markup=ReplicaTelegramBot.new_question_keyboard())

    def web_command(self, update, context):
        update.message.reply_text("Bölüm Web sayfamıza http://bilgisayar.btu.edu.tr adresinden erişebilirsiniz. {}".format(
            str(ReplicaTelegramBot.new_question_message())), reply_markup=ReplicaTelegramBot.new_question_keyboard())

    def add_command(self, update, context):
        user = context.bot.getChatMember(
            update.message.chat.id, update.message.from_user['id'])

        if user.status == "creator" or user.status == "administrator":
            try:
                _ = self.__replica_state.get_chats().index(
                    Chat(telegram_id=update.message.chat.id))
                update.message.reply_text(
                    "Şu an da bu grup duyurucuya zaten kayıtlı.")
            except ValueError:
                if self.__replica_state.append_chat(Chat(telegram_id=update.message.chat.id, name=update.message.chat.title)):
                    update.message.reply_text("Komut başarıyla çalıştırıldı.")
                else:
                    update.message.reply_text(
                        "Komut çalıştırılırken bilinmeyen bir hata oluştu.")

            except Exception as e:
                logger.error("there is an error while adding a new group", e)
                update.message.reply_text(
                    "Komut çalıştırma başarısız oldu.")

        else:
            update.message.reply_text(
                "Yalnızca admin ve yöneticiler komutları kullanabilir.")

    def remove_command(self, update, context):
        user = context.bot.getChatMember(
            update.message.chat.id, update.message.from_user['id'])

        if user.status == "creator" or user.status == "administrator":
            try:
                _ = self.__replica_state.get_chats().index(
                    Chat(telegram_id=update.message.chat.id))
                self.__replica_state.remove_chat(
                    Chat(telegram_id=update.message.chat.id))

                update.message.reply_text(
                    "Grup duyurucudan başarıyla çıkartıldı.")
            except ValueError:
                if self.__replica_state.append_chat(Chat(telegram_id=update.message.chat.id, name=update.message.chat.title)):
                    update.message.reply_text("Komut başarıyla çalıştırıldı.")
                else:
                    update.message.reply_text(
                        "Komut çalıştırılırken bilinmeyen bir hata oluştu. Lütfen yöneticilere bildiriniz.")
            except Exception as e:
                logger.error("there is an error while removing a new group", e)
                update.message.reply_text(
                    "Komut çalıştırma başarısız oldu.")

        else:
            update.message.reply_text(
                "Yalnızca admin ve yöneticiler komutları kullanabilir.")

    def get_all_chats_command(self, update, context):
        member = context.bot.getChatMember(
            update.message.chat.id, update.message.from_user['id'])
        json_data = json.dumps(
            self.__replica_state.get_chats(), indent=4, ensure_ascii=False)

        if member.status == "creator" or member.status == "administrator":
            message = "#### VERİ BAŞLANGIÇ - TARİH: " + \
                str(datetime.now()) + " \n" + \
                str(json_data) + " \n#### VERİ SON"
            update.message.reply_text("Komut başarıyla çalıştırıldı.")

            for key in USER_ID.keys():
                if update.message.from_user['id'] == USER_ID[key]:
                    update.message.reply_text(message)
        else:
            update.message.reply_text(
                "Yalnızca admin ve yöneticiler komutları kullanabilir.")

    def run(self):

        # Dispatcher'ı erişilebilir bir değişkene atar
        dp = self._updater.dispatcher

        # Telegramdan gönderilen komutlar için algılayıcılar oluşturuluyor
        self.add_handler(CommandHandler("yaz", self.get_all_chats_command))
        self.add_handler(CommandHandler("hakkinda", self.about_command))
        self.add_handler(CommandHandler("yardim", self.help_command))
        self.add_handler(CommandHandler("ekle", self.add_command))
        self.add_handler(CommandHandler("cikar", self.remove_command))
        self.add_handler(CommandHandler("web", self.web_command))
        self.add_handler(CallbackQueryHandler(
            self.new_question_callback, pattern='new_question_yes'))
        self.add_handler(CallbackQueryHandler(
            self.new_question_callback, pattern='new_question_no'))

        # Bot başlatılıyor.
        super().run()
