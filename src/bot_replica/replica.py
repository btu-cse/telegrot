# -*- coding:utf-8 -*-
import os
import sys
import requests
import json
import mysql.connector

from datetime import datetime
from bs4 import BeautifulSoup

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext

from src.lib.telegram_bot import TelegramBot
from src.utils import logger

STATE = initialState


def getData():
    global STATE
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

# Uzak sunucuda bulunan son gönderilen duyuru kolonu ve aktif chatlerin bulunduğu kolonu günceller


def updateData():
    try:
        data = STATE.copy()
        data['chatIDs'] = data['chatIDs']
        mycursor = mydb.cursor()

        query = "UPDATE data SET lastAnnouncement=\"{0}\", chatIDs=\"{1}\" WHERE id=1".format(
            data['lastAnnouncement'], str(data['chatIDs']))
        mycursor.execute(query)
        mydb.commit()
        print(mycursor.rowcount, "satır(lar) güncellendi")
        getData()
        mycursor.close()

    except Exception as e:
        print("Uzak sunucuya veri gönderilemiyor. \n " + e)


# Betik çalıştırıldığında bir kere çalışır ve yeni duyuru varsa gruplara iletir.



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
    user = context.bot.getChatMember(
        update.message.chat.id, update.message.from_user['id'])
    global STATE
    chat_id_dictionary = STATE["chatIDs"]

    if user.status == "creator" or user.status == "administrator":
        if chat_id_dictionary.get(str(update.message.chat.id)) != None:
            update.message.reply_text(
                "Şu an da bu grup duyurucuya kayıtlı yeniden başlatmak için deneyin: \n /cikar ve ardından /ekle.")
        else:
            chat_id_dictionary[str(update.message.chat.id)
                               ] = update.message.chat.title
            print("### İŞLEM BAŞLANGIÇ - TARİH: " + str(datetime.now()) +
                  " \nDuyurucuya yeni bir grup eklendi - Chat: " + str(update.message.chat) + " \n### İŞLEM SON")
            update.message.reply_text("Komut başarıyla çalıştırıldı.")
            if mydb != None:
                updateData()
    else:
        update.message.reply_text(
            "Yalnızca admin ve yöneticiler komutları kullanabilir.")

# /cikar komutu geldiğinde gerçekleştirilecek işlemler


def remove(update, context):
    user = context.bot.getChatMember(
        update.message.chat.id, update.message.from_user['id'])
    global STATE
    chat_id_dictionary = STATE["chatIDs"]

    if user.status == "creator" or user.status == "administrator":
        if chat_id_dictionary.get(str(update.message.chat.id)) != None:
            chat_id_dictionary.pop(str(update.message.chat.id), None)
            print("### İŞLEM BAŞLANGIÇ -  TARİH: " + str(datetime.now()) +
                  " \nDuyurucudan bir grup çıkarıldı - Chat: " + str(update.message.chat) + " \n### İŞLEM SON")
            update.message.reply_text("Komut başarıyla çalıştırıldı.")
            if mydb != None:
                updateData()
        else:
            update.message.reply_text(
                "Şu anda bu grup duyurucuda bulunmuyor. Grubu duyurucuya dahil etmek için: /add")
    else:
        update.message.reply_text(
            "Yalnızca admin ve yöneticiler komutları kullanabilir.")

# /yaz komutu geldiğinde gerçekleştirilecek işlemler


def getDictionary(update, context):
    member = context.bot.getChatMember(
        update.message.chat.id, update.message.from_user['id'])
    json_data = json.dumps(STATE, indent=4, ensure_ascii=False)

    if member.status == "creator" or member.status == "administrator":
        message = "#### VERİ BAŞLANGIÇ - TARİH: " + \
            str(datetime.now()) + " \n" + str(json_data) + " \n#### VERİ SON"
        update.message.reply_text("Komut başarıyla çalıştırıldı.")
        for key in USER_ID.keys():
            if update.message.from_user['id'] == USER_ID[key]:
                update.message.reply_text(message)
    else:
        update.message.reply_text(
            "Yalnızca admin ve yöneticiler komutları kullanabilir.")

# Gönderilen komut işlemleri gerçekleştirildiğinde, döndürülen 'Başka bir sorunuz var mı ?' fonksiyonu




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
    dp.add_handler(CallbackQueryHandler(
        new_question_callback, pattern='new_question_yes'))
    dp.add_handler(CallbackQueryHandler(
        new_question_callback, pattern='new_question_no'))

    # Bot başlatılıyor.
    run(updater)


if __name__ == '__main__':
    main()
