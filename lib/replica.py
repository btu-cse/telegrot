# -*- coding:utf-8 -*-

import logging
import os
import random
import sys
import requests
import json
import urllib3
import urllib.parse as urlparse
import mysql.connector

from datetime import datetime
from emoji import emojize
from bs4 import BeautifulSoup
from time import sleep
from threading import Thread, Event

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext

# İstek hatalarının çıktılarını bozmasını engeller
urllib3.disable_warnings()

# Heroku'dan REPLICA_TOKEN değişkenini getirir
TOKEN = os.getenv("REPLICA_TOKEN")
url = "https://api.telegram.org/bot" + TOKEN

# Heroku'dan USER_ID değişkenini getirir
USER_ID = eval(os.getenv("USER_ID"))

# Loglama başlatılıyor
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger()

# Heroku'dan MODE değişkenini çeker
mode = os.getenv("MODE")

# Mod'a uyarlı, updater başlatma fonksiyonu belirler
if mode == "dev":
    def run(updater):
        updater.start_polling()
        start(CallbackContext(updater.dispatcher))
elif mode == "prod":
    def run(updater):
        PORT = int(os.environ.get("PORT", 8443))
        HEROKU_APP_NAME = os.environ.get("HEROKU_APP_NAME")
        updater.start_webhook(listen="0.0.0.0",
                              port=PORT,
                              url_path=TOKEN)
        updater.bot.set_webhook("https://{}.herokuapp.com/{}".format(HEROKU_APP_NAME, TOKEN))
        start(CallbackContext(updater.dispatcher))
        updater.idle()
        if mydb != None:
            mydb.close()
else:
    logger.error("No MODE specified!")
    sys.exit(1)

# GLOBAL DEĞİŞKENLER

initialState = {
    "lastAnnouncement": "0",
    "chatIDs": eval(os.getenv('CHAT_ID'))
}
STATE = initialState
mydb = None


def mysqlConnect():
    global mydb
    try:
        db = mysql.connector.connect(
          host=os.getenv("REMOTE_SQL_SERVER"),
          port="3306",
          user=os.getenv("REMOTE_SQL_USER"),
          password=os.getenv("REMOTE_SQL_PWD"),
          database=os.getenv("REMOTE_SQL_DB"),
          charset='utf8',
        )
        mydb = db
    except Exception as e:
            print("Uzak sunucuya bağlanılamıyor. \n " + e)

# Uzak sunucudan son gönderilen duyuruyu ve aktif olduğu chatleri getirir
def getData():
    global STATE
    try:

        mycursor = mydb.cursor()
        mycursor.execute("SELECT lastAnnouncement, chatIDs FROM data WHERE id=1 ")
        result = mycursor.fetchall()
        STATE["chatIDs"] = eval(result[0][1])
        STATE["lastAnnouncement"] = result[0][0]
        mycursor.close()

    except Exception as e:
        if STATE['lastAnnouncement'] == "0":
            STATE['lastAnnouncement'] = getAnnouncement(0).get('href').split('&')[1].split('=')[1]
        print("Uzak sunucudan veri getirilemedi. \n " + e)

# Uzak sunucuda bulunan son gönderilen duyuru kolonu ve aktif chatlerin bulunduğu kolonu günceller
def updateData():
    try:
        data = STATE.copy()
        data['chatIDs'] = data['chatIDs']
        mycursor = mydb.cursor()

        query ="UPDATE data SET lastAnnouncement=\"{0}\", chatIDs=\"{1}\" WHERE id=1".format(data['lastAnnouncement'], str(data['chatIDs']))
        mycursor.execute(query)
        mydb.commit()
        print(mycursor.rowcount, "satır(lar) güncellendi")
        getData()
        mycursor.close()

    except Exception as e:
        print("Uzak sunucuya veri gönderilemiyor. \n " + e)


# Duyuru ile ilgili veri döndürür
def getAnnouncement(announcement, control = True):
    try:
        params = {'page':'duyuru'}
        if not control :
            params = {'page':'duyuru','id':announcement}
        SITEURL = 'http://bilgisayar.btu.edu.tr/index.php'

        # Siteden gelen dönütü düzenler
        page = requests.get(SITEURL, params=params, verify=False)
        soup = BeautifulSoup(page.content, 'html.parser')
        container = soup.find_all("div", {"class" : "container"})[1]
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
    except Exception as e:
        print("Siteden duyuru getirilemedi, DUYURU NO: {0} \n {1}".format(announcement, e))

# Belirlenen(chat_id_dictionary) yerlere duyuruyu gönderir.
def sendAnnouncement(ctx):
    global STATE
    try:
        lastAnnouncement = getAnnouncement(0).get('href').split('&')[1].split('=')[1]

        if STATE["lastAnnouncement"] != "0" and STATE["lastAnnouncement"] != "":
            last = STATE["lastAnnouncement"]
        else:
            last = lastAnnouncement
        context = ctx
        newLast = lastAnnouncement
        i = 0
        list = []
        while last != newLast:
            list.append(newLast)
            i += 1
            if i > 3:
                list.clear()
                break
            newLast = getAnnouncement(i).get('href').split('&')[1].split('=')[1]
        list.reverse()
        for value in list:
            message_text = '\nDUYURU: \n'
            message_text += getAnnouncement(value, False)
            for key in STATE["chatIDs"]:
                try:
                    context.bot.send_message(chat_id=key, text=message_text)
                except:
                    print('{0} Chat id\'sine sahip sohbete duyuru gönderilemedi.'.format(key))

        STATE["lastAnnouncement"] = lastAnnouncement

    except Exception as e:
        print("Siteden veri getirilemedi... \n" + e)

# Betik çalıştırıldığında bir kere çalışır ve yeni duyuru varsa gruplara iletir.
def start(ctx):
    mysqlConnect()
    if(mydb != None):
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
    global STATE
    chat_id_dictionary = STATE["chatIDs"]

    if user.status == "creator" or user.status == "administrator":
        if chat_id_dictionary.get(str(update.message.chat.id)) != None:
            update.message.reply_text("Şu an da bu grup duyurucuya kayıtlı yeniden başlatmak için deneyin: \n /cikar ve ardından /ekle.")
        else:
            chat_id_dictionary[str(update.message.chat.id)] = update.message.chat.title
            print("### İŞLEM BAŞLANGIÇ - TARİH: " + str(datetime.now()) + " \nDuyurucuya yeni bir grup eklendi - Chat: " + str(update.message.chat) + " \n### İŞLEM SON")
            update.message.reply_text("Komut başarıyla çalıştırıldı.")
            if mydb != None:
                updateData()
    else:
        update.message.reply_text("Yalnızca admin ve yöneticiler komutları kullanabilir.")

# /cikar komutu geldiğinde gerçekleştirilecek işlemler
def remove(update, context):
    user = context.bot.getChatMember(update.message.chat.id,update.message.from_user['id'])
    global STATE
    chat_id_dictionary = STATE["chatIDs"]

    if user.status == "creator" or user.status == "administrator":
        if chat_id_dictionary.get(str(update.message.chat.id)) != None:
            chat_id_dictionary.pop(str(update.message.chat.id), None)
            print("### İŞLEM BAŞLANGIÇ -  TARİH: " + str(datetime.now()) + " \nDuyurucudan bir grup çıkarıldı - Chat: " + str(update.message.chat) + " \n### İŞLEM SON")
            update.message.reply_text("Komut başarıyla çalıştırıldı.")
            if mydb != None:
                updateData()
        else:
            update.message.reply_text("Şu anda bu grup duyurucuda bulunmuyor. Grubu duyurucuya dahil etmek için: /add")
    else:
        update.message.reply_text("Yalnızca admin ve yöneticiler komutları kullanabilir.")

# /yaz komutu geldiğinde gerçekleştirilecek işlemler
def getDictionary(update, context):
    member = context.bot.getChatMember(update.message.chat.id,update.message.from_user['id'])
    json_data = json.dumps(STATE, indent = 4, ensure_ascii = False)

    if member.status == "creator" or member.status == "administrator":
        message = "#### VERİ BAŞLANGIÇ - TARİH: " + str(datetime.now()) + " \n" + str(json_data) + " \n#### VERİ SON"
        update.message.reply_text("Komut başarıyla çalıştırıldı.")
        print(message)
        for key in USER_ID.keys():
            if update.message.from_user['id'] == USER_ID[key]:
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
