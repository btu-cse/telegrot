import sys

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler
from src.common import constants
from src.common.logger import Logger

logger = Logger.getLogger()


class TelegramBot:
    _token: str
    _mode: str
    _port: int
    _heroku_app_name: str
    _updater: Updater
    _handlers: list

    def __init__(self, token: str, mode: str, heroku_app_name: str = "", port: int = 8443) -> None:
        if token == "":
            logger.error("'token' cannot be empty")
            sys.exit(1)

        if mode == "":
            logger.error("'mode' cannot be empty")
            sys.exit(1)

        if not mode in constants.MODES:
            logger.error("mode {} is not supported. supported modes are => {}".format(
                mode, ",".join("'%s'" % el for el in constants.MODES)))
            sys.exit(1)

        if mode == constants.MODE_PROD_HEROKU and heroku_app_name == "":
            logger.error(
                "when program working on the 'prod_heroku' mode it needs to 'heroku_app_name' parameter")
            sys.exit(1)

        self.__token = token
        self.__mode = mode
        self.__handlers = [
            CommandHandler("start", self.start_command),
            CommandHandler("help", self.help_command)
        ]
        self.__heroku_app_name = heroku_app_name
        self.__port = port

    def add_handler(self, handler):
        self.__handlers.append(handler)

    def run(self):
        self.call()

        if self.__mode == constants.MODE_DEV:
            self.run_dev()
        elif self.__mode == constants.MODE_PROD_HEROKU:
            self.run_heroku_webhook()
        elif self.__mode == constants.MODE_PROD:
            self.run_prod()

    def run_dev(self) -> None:
        self._updater.start_polling()

    def run_prod(self) -> None:
        # elf.__updater.start_polling()
        self._updater.start_webhook(listen="0.0.0.0",
                                    port=self.__port,
                                    url_path=self.__token)

    def run_heroku_webhook(self) -> None:
        self._updater.start_webhook(listen="0.0.0.0",
                                    port=self.__port,
                                    url_path=self.__token)
        self._updater.bot.set_webhook(
            "https://{}.herokuapp.com/{}".format(self.__heroku_app_name, self.__token))

    def call(self):
        self._updater = Updater(self.__token, use_context=True)

        dp = self._updater.dispatcher

        for handler in self.__handlers:
            dp.add_handler(handler)

    def help_command(self, update, context):

        help_message = "Bu örnek bir yardım mesajıdır. \n"
        help_message += "Komut çalıştırmak için \"/\" karakteri ile gerekli komutu yazmalısın.\n"
        help_message += "Mevcut komutlar; \n\n"
        help_message += "/start - botu başlatır\n"
        help_message += "/help - yardım ekranını açar\n"

        update.message.reply_text(help_message)

    def start_command(self, update, context):
        self.help_command(update, context)

    def new_question_callback(self, update, context):
        query = update.callback_query

        if query.data == 'new_question_yes':
            self.help_command(query, context)
        elif query.data == 'new_question_no':
            query.message.reply_text(
                "İyi günler. Her zaman hizmetinizdeyim...")
        else:
            query.message.reply_text("Bir sorun var! Error Code:208.")

    @staticmethod
    def new_question_keyboard():
        keyboard = [[
            InlineKeyboardButton('Evet', callback_data='new_question_yes'),
            InlineKeyboardButton('Hayır', callback_data='new_question_no'),
        ]]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def new_question_message():
        return '\n\nBaşka bir sorunuz var mı ?'
