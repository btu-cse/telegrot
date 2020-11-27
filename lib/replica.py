# -*- coding:utf-8 -*-

import logging
import os
import random
import sys
import requests
import json
import urllib.parse as urlparse

from datetime import datetime
from emoji import emojize
from bs4 import BeautifulSoup
from time import sleep
from threading import Thread, Event

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext

# Heroku'dan REPLICA_TOKEN değişkenini getirir
TOKEN = "1403524326:AAG9QDOsVFCwB50Z-xnWtWuqoJf9AhXuLx0"#os.getenv("REPLICA_TOKEN")
url = "https://api.telegram.org/bot" + TOKEN

# Loglama başlatılıyor
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger()

# Heroku'dan MODE değişkenini çekiyor
mode = "dev"#os.getenv("MODE")

# Mod'a uyarlı, updater başlatma fonksiyonu belirler
if mode == "dev":
    def run(updater):
        updater.start_polling()
        start(CallbackContext(updater.dispatcher))
elif mode == "prod":
    def run(updater):
        PORT = int(os.environ.get("REPLICA_PORT", 8443))
        HEROKU_APP_NAME = os.environ.get("HEROKU_APP_NAME")
        updater.start_webhook(listen="0.0.0.0",
                              port=PORT,
                              url_path=TOKEN)
        updater.bot.set_webhook("https://{}.herokuapp.com/{}".format(HEROKU_APP_NAME, TOKEN))
        start(CallbackContext(updater.dispatcher))
        updater.idle()
else:
    logger.error("No MODE specified!")
    sys.exit(1)

# Global değişkenler
DOC_JSON = "./doc/data.json"
announcement_json_data = { "lastAnnouncement": "0", "chatIDs": {'-3': 'Bilg. Müh. Destek', '-466883632': 'TEST GRUP'} } # DESTEK: 1001285487723, TEST: '-466883632'


# ../doc/data.json dosyasından son gönderilen duyuruyu ve aktif olduğu chatleri getirir
def getData():
    global announcement_json_data
    try:
        f = open(DOC_JSON, "r")
        data = json.loads(f.read())

        announcement_json_data["chatIDs"] = data['chatIDs']
        announcement_json_data["lastAnnouncement"] = data["lastAnnouncement"]
    except Exception as e:
        print("'data.json' üzerinden veri çekilemedi. \n " + e)

def updateData():
    global announcement_json_data
    try:
        data = announcement_json_data.copy()
        data['chatIDs'] = data['chatIDs']

        json_object = json.dumps(data, indent = 4, ensure_ascii = False)
        with open(DOC_JSON, "w", encoding='utf8') as outfile:
            outfile.write(json_object)

        getData()
        return json_object
    except Exception as e:
        print("'data.json' dosyası güncellenemedi. \n " + e)


# Duyuru ile ilgili veri döndürür
def getAnnouncement(announcement, control = True):
    params = {'page':'duyuru'}
    if not control :
        params = {'page':'duyuru','id':announcement}
    SITEURL = 'http://bilgisayar.btu.edu.tr/index.php'

    # Siteden gelen dönütü düzenler
    page = requests.get(SITEURL, params=params)
    soup = BeautifulSoup(page.content, 'html.parser')
    container = soup.find_all("div", {"class" : "container"})[2]
    row = container.find_all("div", {"class" : "row"})[0]
    column = row.find_all("div", {"class" : "col-md-9"})[0]

    # Eğer control=True ise duyurunun query verisinden id'yi döndürür. Eğer control=False ise duyuruyu döndürür
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

# Belirlenen(chat_id_dictionary) yerlere duyuruyu gönderir.
def sendAnnouncement(ctx):
    global announcement_json_data
    try:
        lastAnnouncement = getAnnouncement(0).get('href')
        isEmptyLastAnnouncement = announcement_json_data["lastAnnouncement"].split('&')[1].split('=')[1]

        if isEmptyLastAnnouncement != "0" and isEmptyLastAnnouncement != "":
            last = announcement_json_data["lastAnnouncement"]
        else:
            last = lastAnnouncement
        context = ctx
        newLast = lastAnnouncement
        i = 0
        list = []
        while last != newLast:
            id_query = newLast.split('&')[1].split('=')[1]
            list.append(id_query)
            i += 1
            newLast = getAnnouncement(i).get('href')
        list.reverse()

        for value in list:
            message_text = '\nDUYURU: \n'
            message_text += getAnnouncement(value, False)
            for key in announcement_json_data["chatIDs"]:
                try:
                    context.bot.send_message(chat_id=key, text=message_text)
                except:
                    print('{0} Chat id\'sine sahip sohbete duyuru gönderilemedi.'.format(key))

        announcement_json_data["lastAnnouncement"] = lastAnnouncement

    except Exception as e:
        print("Siteden veri getirilemedi... \n" + e)

# Betik çalıştırıldığında bir kere çalışır ve yeni duyuru varsa gruplara iletir.
def start(ctx):
    getData()
    sendAnnouncement(ctx)
    updateData()

# /help komutu geldiğinde gerçekleştirilecek işlemler
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
    help_message += "/web - BTÜ BM Web sayfası\n"
    update.message.reply_text(help_message)

# /hakkinda komutu geldiğinde gerçekleştirilecek işlemler
def about(update, context):
    update.message.reply_text("Duyuru botumuz, bölüm öğrencimiz Fatih Ateş ve Arş. Gör. Ahmet Kaşif tarafından geliştirilmiştir. Öneri ve isteklerinizi için : @ahmetkasif"
    + str(new_question_message()), reply_markup=new_question_keyboard())

# /web komutu geldiğinde gerçekleştirilecek işlemler
def web(update, context):
    update.message.reply_text("Bölüm Web sayfamıza http://bilgisayar.btu.edu.tr adresinden erişebilirsiniz."
    + str(new_question_message()), reply_markup=new_question_keyboard())

# /ekle komutu geldiğinde gerçekleştirilecek işlemler
def add(update, context):
    user = context.bot.getChatMember(update.message.chat.id,update.message.from_user['id'])
    global announcement_json_data
    chat_id_dictionary = announcement_json_data["chatIDs"]

    if user.status == "creator" or user.status == "administrator":
        if chat_id_dictionary.get(str(update.message.chat.id)) != None:
            update.message.reply_text("Şu an da bu grup duyurucuya kayıtlı yeniden başlatmak için deneyin: \n /cikar ve ardından /ekle.")
        else:
            chat_id_dictionary[str(update.message.chat.id)] = update.message.chat.title
            print("### İŞLEM BAŞLANGIÇ - TARİH: " + str(datetime.now()) + " \nDuyurucuya yeni bir grup eklendi - Chat: " + str(update.message.chat) + " \n### İŞLEM SON")
            update.message.reply_text("Komut başarıyla çalıştırıldı.")
            updateData()
    else:
        update.message.reply_text("Yalnızca admin ve yöneticiler komutları kullanabilir.")

# /cikar komutu geldiğinde gerçekleştirilecek işlemler
def remove(update, context):
    user = context.bot.getChatMember(update.message.chat.id,update.message.from_user['id'])
    global announcement_json_data
    chat_id_dictionary = announcement_json_data["chatIDs"]

    if user.status == "creator" or user.status == "administrator":
        if chat_id_dictionary.get(str(update.message.chat.id)) != None:
            chat_id_dictionary.pop(str(update.message.chat.id), None)
            print("### İŞLEM BAŞLANGIÇ -  TARİH: " + str(datetime.now()) + " \nDuyurucudan bir grup çıkarıldı - Chat: " + str(update.message.chat) + " \n### İŞLEM SON")
            update.message.reply_text("Komut başarıyla çalıştırıldı.")
            updateData()
        else:
            update.message.reply_text("Şu anda bu grup duyurucuda bulunmuyor. Grubu duyurucuya dahil etmek için: /add")
    else:
        update.message.reply_text("Yalnızca admin ve yöneticiler komutları kullanabilir.")

# /yaz komutu geldiğinde gerçekleştirilecek işlemler
def getDictionary(update, context):
    member = context.bot.getChatMember(update.message.chat.id,update.message.from_user['id'])
    json_data = updateData()
    if member.status == "creator" or member.status == "administrator":
        message = "#### VERİ BAŞLANGIÇ - TARİH: " + str(datetime.now()) + " \n" + str(json_data) + " \n#### VERİ SON"
        update.message.reply_text("Komut başarıyla çalıştırıldı.")
        if update.message.from_user['id'] == 690194302: # 690194302 = fatiiates hesabına ait user id
            update.message.reply_text(message)
    else:
        update.message.reply_text("Yalnızca admin ve yöneticiler komutları kullanabilir.")

# Gönderilen komut işlemleri gerçekleştirildiğinde, döndürülen 'Başka bir sorunuz var mı ?' fonksiyonu
def new_question_callback(update, context):
  query = update.callback_query

  if query.data == 'new_question_yes':
      help(query, context)
  elif query.data == 'new_question_no':
      query.message.reply_text("İyi günler. Her zaman hizmetinizdeyim...")
  else:
      query.message.reply_text("Bir sorun var! Error Code:208.")

############################ Klavyeler #########################################
def new_question_keyboard():
  keyboard = [[
      InlineKeyboardButton('Evet', callback_data='new_question_yes'),
      InlineKeyboardButton('Hayır', callback_data='new_question_no'),
  ]]
  return InlineKeyboardMarkup(keyboard)

############################# Mesajlar #########################################
def new_question_message():
  return '\n\nBaşka bir sorunuz var mı ?'

def main():
    # Updater oluşturur
    updater = Updater(TOKEN, use_context=True)

    # Dispatcher'ı erişilebilir bir değişkene atar
    dp = updater.dispatcher



    # Telegramdan gönderilen komutlar için algılayıcılar oluşturuluyor
    dp.add_handler(CommandHandler("yaz", getDictionary))
    dp.add_handler(CommandHandler("hakkinda", about))
    dp.add_handler(CommandHandler("yardim", help))
    dp.add_handler(CommandHandler("ekle", add))
    dp.add_handler(CommandHandler("cikar", remove))
    dp.add_handler(CommandHandler("web", web))
    dp.add_handler(CallbackQueryHandler(new_question_callback, pattern='new_question_yes'))
    dp.add_handler(CallbackQueryHandler(new_question_callback, pattern='new_question_no'))

    # Bot başlatılıyor.
    run(updater)

if __name__ == '__main__':
    main()
