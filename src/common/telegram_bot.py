import os
import sys
from typing import Callable

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler
from src.common import constants
from src.common.logger import Logger
 
class TelegramBot:
    _token: str
    _mode: str
    _port: int
    _web_hook_url: str
    _updater: Updater
    _handlers: list

    def __init__(self, token: str, mode: str, web_hook_url: str = "", port: int = constants.DEFAULT_PORT) -> None:
        if token == "":
            Logger.fatal("'token' cannot be empty")

        if mode == "":
            Logger.fatal("'mode' cannot be empty")

        if not mode in constants.MODES:
            Logger.fatal("mode {} is not supported. supported modes are => {}".format(
                mode, ",".join("'%s'" % el for el in constants.MODES)))

        if mode == constants.MODE_PROD and web_hook_url == "":
            Logger.fatal(
                "when program working on the 'prod' mode it needs to 'web_hook_url' parameter")

        self._token = token
        self._mode = mode
        self._handlers = [
            CommandHandler("start", self.start_command),
            CommandHandler("help", self.help_command)
        ]
        self._web_hook_url = web_hook_url
        self._port = port

        self._updater = Updater(self._token, use_context=True)

    def add_handler(self, handler):
        self._handlers.append(handler)

    def run(self):
        self.call()

        if self._mode == constants.MODE_DEV:
            self.run_dev()
        elif self._mode == constants.MODE_PROD:
            self.run_prod()

    def run_dev(self) -> None:
        self._updater.start_polling()

    def run_prod(self) -> None:
        self._updater.start_webhook(listen="0.0.0.0",
                                    port=self._port,
                                    url_path=self._token,
                                    webhook_url="https://{}:{}/{}".format(self._web_hook_url, self._port, self._token),
                                    cert=os.path.join(sys.path[0], 'certs/server.pem'),
                                    key=os.path.join(sys.path[0], 'certs/server.key'))

    def call(self):

        dp = self._updater.dispatcher

        for handler in self._handlers:
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

    @staticmethod
    def Command(command: Callable) -> Callable:
        def new_command(update, context):
            try:
                command(update, context)
            except Exception as e:
                Logger.error("there is an unexpected error on '{}' %s".format(command.__name__), e)
                update.message.reply_text(
                    "Bilinmeyen bir hata oluştu, bu komut şu an kullanılamıyor.")

        return new_command

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
