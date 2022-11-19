import logging
import os
import random
import sys
import requests
import urllib.parse as urlparse

from datetime import datetime
from emoji import emojize
from bs4 import BeautifulSoup
from time import sleep
from threading import Thread, Event

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler

#%% variables
TOKEN = os.getenv("REPLICA_TOKEN")
url = "https://api.telegram.org/bot" + TOKEN

#%% initialization

#Enabling logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger()

# Getting mode, so we could define run function for local and Heroku setup
mode = os.getenv("MODE")

if mode == "dev":
    def run(updater):
        updater.start_polling()
elif mode == "prod":
    def run(updater):
        PORT = int(os.environ.get("PORT", "8443"))
        HEROKU_APP_NAME = "btubmtanitimbot"
        updater.start_webhook(listen="0.0.0.0",
                              port=PORT,
                              url_path=TOKEN)
        updater.bot.set_webhook("https://{}.herokuapp.com/{}".format(HEROKU_APP_NAME, TOKEN))
else:
    logger.error("No MODE specified!")
    sys.exit(1)

#GLOBAL VARIABLES
announcement_thread_dictionary = {}

class myThread(Thread):
    def __init__(self, update, context, *args, **kwarg):
        super().__init__(*args, **kwarg)
        self.running_event = Event()
        self.update = update;
        self.context = context;

    def getAnnouncement(self, announcement, control = True):
        params = {'page':'duyuru'}
        if not control :
            params = {'page':'duyuru','id':announcement}
        SITEURL = 'http://bilgisayar.btu.edu.tr/index.php'

        page = requests.get(SITEURL, params=params)
        soup = BeautifulSoup(page.content, 'html.parser')
        container = soup.find_all("div", {"class" : "container"})[2]
        row = container.find_all("div", {"class" : "row"})[0]
        column = row.find_all("div", {"class" : "col-md-9"})[0]

        if control:
            i = 0
            table = ''
            for val in column.find_all('table'):
                if i == announcement:
                    return val.find_all('a')[0]
                i += 1
        else:
            panel = column.find_all("div", {"class":"panel"})[0]
            panel_body = panel.find_all('div')[1].get_text()
            panel_body += '\nİncelemek için: ' + str(SITEURL) + '?'
            for val in params.keys():
                panel_body += str(val) + '=' + str(params[val]) + '&'
            return panel_body.rstrip('&')

    def run(self):
        while not self.running_event.isSet():
            try:
                last = self.getAnnouncement(0).get('href')
                context = self.context
                update = self.update
                while not self.running_event.isSet():
                    newLast = self.getAnnouncement(0).get('href')
                    i = 0
                    list = []
                    while last != newLast:
                        id_query = newLast.split('&')[1].split('=')[1]
                        list.append(id_query)
                        i += 1
                        newLast = self.getAnnouncement(i).get('href')
                    list.reverse()

                    for value in list:
                        message_text = '\nDUYURU: \n'
                        message_text += self.getAnnouncement(value, False)
                        context.bot.send_message(chat_id=update.message.chat_id, text=message_text)

                    list.clear()
                    last = self.getAnnouncement(0).get('href')
                    sleep(600)
            except:
                print("Siteye şu anda ulaşılamıyor...")

    def stop_thread(self):
        self.running_event.set()

#%% Creating handler-functions for /* commands
def help(update, context):
    """Send a message when the command /help is issued."""

    help_message = "Mevcut komutları aşağıdaki listeden görebilirsin. \n"
    help_message += "Komut çalıştırmak için \"/\" karakteri ile gerekli komutu yazmalısın.\n"
    help_message += "Mevcut komutlar; \n"
    help_message += "/dict Çalışan betikleri konsola yansıtır::YALNIZCA SAHİP ve YÖNETİCİ\n"
    help_message += "/hakkinda - Geliştirici ekibi\n"
    help_message += "/help - Tüm komutları görmek istiyorum\n"
    help_message += "/start Duyuru botunu çalıştırır::YALNIZCA SAHİP ve YÖNETİCİ\n"
    help_message += "/stop Duyuru botunu durdurur::YALNIZCA SAHİP ve YÖNETİCİ\n"
    help_message += "/web_sayfasi - BTÜ BM Web sayfası\n"
    update.message.reply_text(help_message)

def hakkinda(update, context):
    update.message.reply_text("Duyuru botumuz, bölüm öğrencimiz Fatih Ateş ve Arş. Gör. Ahmet Kaşif tarafından geliştirilmiştir. Öneri ve isteklerinizi için : @ahmetkasif"
    + str(new_question_message()), reply_markup=new_question_keyboard())

def web_sayfasi(update, context):
    update.message.reply_text("Bölüm Web sayfamıza http://bilgisayar.btu.edu.tr adresinden erişebilirsiniz."
    + str(new_question_message()), reply_markup=new_question_keyboard())

def replica_start(update, context):
    user = context.bot.getChatMember(update.message.chat_id,update.message.from_user['id'])
    global announcement_thread_dictionary

    if user.status == "creator" or user.status == "administrator":
        if announcement_thread_dictionary.get(str(update.message.chat_id)) != None:
            update.message.reply_text("Şu an da bir betik çalışıyor yeni bir betik başlatmak için deneyin: \n /stop ve ardından /start.")
        else:
            announcement_thread_dictionary[str(update.message.chat_id)] = myThread(update, context)
            announcement_thread_dictionary[str(update.message.chat_id)].start()
            print("### İŞLEM BAŞLANGIÇ - TARİH: " + str(datetime.now()) + " \nYeni bir betik başlatıldı - Chat: " + str(update.message.chat) + " \n### İŞLEM SON")
            update.message.reply_text("Duyuru botu aktif hale getirildi.")
    else:
        update.message.reply_text("Yalnızca admin ve yöneticiler komutları kullanabilir.")

# Creating a handler-function for /start command
def replica_stop(update, context):
    user = context.bot.getChatMember(update.message.chat_id,update.message.from_user['id'])
    global announcement_thread_dictionary
    if user.status == "creator" or user.status == "administrator":
        if announcement_thread_dictionary.get(str(update.message.chat_id)) != None:
            announcement_thread_dictionary[str(update.message.chat_id)].stop_thread()
            announcement_thread_dictionary.pop(str(update.message.chat_id), None)
            print("### İŞLEM BAŞLANGIÇ -  TARİH: " + str(datetime.now()) + " \nBir bir betik sonlandırıldı - Chat: " + str(update.message.chat) + " \n### İŞLEM SON")
            update.message.reply_text("Komut başarıyla çalıştırıldı.")
        else:
            update.message.reply_text("Şu anda çalışan bir betik bulunamadı. Yeni betik oluşturmak için deneyin: /start")
    else:
        update.message.reply_text("Yalnızca admin ve yöneticiler komutları kullanabilir.")

def replica_dictionary(update, context):
    user = context.bot.getChatMember(update.message.chat_id,update.message.from_user['id'])
    global announcement_thread_dictionary
    if user.status == "creator" or user.status == "administrator":
        print("#### BETİKLER BAŞLANGIÇ - TARİH: " + str(datetime.now()) + " \n" + str(announcement_thread_dictionary) + " \n#### BETİKLER SON")
        update.message.reply_text("Komut başarıyla çalıştırıldı.")
    else:
        update.message.reply_text("Yalnızca admin ve yöneticiler komutları kullanabilir.")

def new_question_callback(update, context):
  query = update.callback_query

  if query.data == 'new_question_yes':
      help(query, context)
  elif query.data == 'new_question_no':
      query.message.reply_text("İyi günler. Her zaman hizmetinizdeyim...")
  else:
      query.message.reply_text("Bir sorun var! Error Code:208.")

############################ Keyboards #########################################
def new_question_keyboard():
  keyboard = [[
      InlineKeyboardButton('Evet', callback_data='new_question_yes'),
      InlineKeyboardButton('Hayır', callback_data='new_question_no'),
  ]]
  return InlineKeyboardMarkup(keyboard)

############################# Messages #########################################
def new_question_message():
  return '\n\nBaşka bir sorunuz var mı ?'

def main():
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater(TOKEN, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("dict", replica_dictionary))
    dp.add_handler(CommandHandler("hakkinda", hakkinda))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("start", replica_start))
    dp.add_handler(CommandHandler("stop", replica_stop))
    dp.add_handler(CommandHandler("web_sayfasi", web_sayfasi))
    dp.add_handler(CallbackQueryHandler(new_question_callback, pattern='new_question_yes'))
    dp.add_handler(CallbackQueryHandler(new_question_callback, pattern='new_question_no'))

    # Start the Bot
    updater.start_polling()
    updater.idle()
    
if __name__ == '__main__':
    main()