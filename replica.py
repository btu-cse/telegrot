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
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext

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
        PORT = int(os.environ.get("PORT", 8443))
        HEROKU_APP_NAME = os.environ.get("HEROKU_APP_NAME", 8443)
        updater.start_webhook(listen="0.0.0.0",
                              port=PORT,
                              url_path=TOKEN)
        updater.bot.set_webhook("https://{}.herokuapp.com/{}".format(HEROKU_APP_NAME, TOKEN))
else:
    logger.error("No MODE specified!")
    sys.exit(1)

#GLOBAL VARIABLES
chat_id_dictionary = { '-1001285487723': True, '-466883632':True } # DESTEK: , TEST: '-466883632'

class myThread(Thread):
    def __init__(self, context, *args, **kwarg):
        super().__init__(*args, **kwarg)
        self.running_event = Event()
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
        global chat_id_dictionary
        while not self.running_event.isSet():
            try:
                last = self.getAnnouncement(0).get('href')
                context = self.context
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
                        for key in chat_id_dictionary:
                            context.bot.send_message(chat_id=key, text=message_text)

                    list.clear()
                    last = self.getAnnouncement(0).get('href')
                    sleep(1800)# 30 minutes
            except:
                print("Siteye şu anda ulaşılamıyor...")

    def stop_thread(self):
        self.running_event.set()

#%% Creating handler-functions for /* commands
def help(update, context):
    """Send a message when the command /help is issued."""

    help_message = "Mevcut komutları aşağıdaki listeden görebilirsin. \n"
    help_message += "Komut çalıştırmak için \"/\" karakteri ile gerekli komutu yazmalısın.\n"
    help_message += "Mevcut komutlar; \n\n"
    help_message += "/yaz - Sözlükte bulunan grupları konsola yazar::YALNIZCA SAHİP ve YÖNETİCİ\n"
    help_message += "/hakkinda - Geliştirici ekibi hakkında bilgi verir\n"
    help_message += "/yardim - Tüm komutları görmek istiyorum\n"
    help_message += "/ekle - Grubu duyurucuya ekler::YALNIZCA SAHİP ve YÖNETİCİ\n"
    help_message += "/cikar - Grubu duyurucudan çıkarır::YALNIZCA SAHİP ve YÖNETİCİ\n"
    help_message += "/web_sayfasi - BTÜ BM Web sayfası\n"
    update.message.reply_text(help_message)

def about(update, context):
    update.message.reply_text("Duyuru botumuz, bölüm öğrencimiz Fatih Ateş ve Arş. Gör. Ahmet Kaşif tarafından geliştirilmiştir. Öneri ve isteklerinizi için : @ahmetkasif"
    + str(new_question_message()), reply_markup=new_question_keyboard())

def web_site(update, context):
    update.message.reply_text("Bölüm Web sayfamıza http://bilgisayar.btu.edu.tr adresinden erişebilirsiniz."
    + str(new_question_message()), reply_markup=new_question_keyboard())

def add(update, context):
    user = context.bot.getChatMember(update.message.chat_id,update.message.from_user['id'])
    global chat_id_dictionary

    if user.status == "creator" or user.status == "administrator":
        if chat_id_dictionary.get(str(update.message.chat_id)) != None:
            update.message.reply_text("Şu an da bu grup duyurucuya kayıtlı yeniden başlatmak için deneyin: \n /cikar ve ardından /ekle.")
        else:
            chat_id_dictionary[str(update.message.chat_id)] = True
            print("### İŞLEM BAŞLANGIÇ - TARİH: " + str(datetime.now()) + " \nDuyurucuya yeni bir grup eklendi - Chat: " + str(update.message.chat) + " \n### İŞLEM SON")
            update.message.reply_text("Komut başarıyla çalıştırıldı.")
    else:
        update.message.reply_text("Yalnızca admin ve yöneticiler komutları kullanabilir.")

# Creating a handler-function for /start command
def remove(update, context):
    user = context.bot.getChatMember(update.message.chat_id,update.message.from_user['id'])
    global chat_id_dictionary
    if user.status == "creator" or user.status == "administrator":
        if chat_id_dictionary.get(str(update.message.chat_id)) != None:
            chat_id_dictionary.pop(str(update.message.chat_id), None)
            print("### İŞLEM BAŞLANGIÇ -  TARİH: " + str(datetime.now()) + " \nDuyurucudan bir grup çıkarıldı - Chat: " + str(update.message.chat) + " \n### İŞLEM SON")
            update.message.reply_text("Komut başarıyla çalıştırıldı.")
        else:
            update.message.reply_text("Şu anda bu grup duyurucuda bulunmuyor. Grubu duyurucuya dahil etmek için: /add")
    else:
        update.message.reply_text("Yalnızca admin ve yöneticiler komutları kullanabilir.")

def dictionary(update, context):
    user = context.bot.getChatMember(update.message.chat_id,update.message.from_user['id'])
    global chat_id_dictionary
    if user.status == "creator" or user.status == "administrator":
        print("#### GRUPLAR BAŞLANGIÇ - TARİH: " + str(datetime.now()) + " \n" + str(chat_id_dictionary) + " \n#### GRUPLAR SON")
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

    # Create and start thread
    announcement_thread = myThread(CallbackContext(dp))
    announcement_thread.start()

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("yaz", dictionary))
    dp.add_handler(CommandHandler("hakkinda", about))
    dp.add_handler(CommandHandler("yardim", help))
    dp.add_handler(CommandHandler("ekle", add))
    dp.add_handler(CommandHandler("cikar", remove))
    dp.add_handler(CommandHandler("web_sayfasi", web_site))
    dp.add_handler(CallbackQueryHandler(new_question_callback, pattern='new_question_yes'))
    dp.add_handler(CallbackQueryHandler(new_question_callback, pattern='new_question_no'))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()

if __name__ == '__main__':
    main()
