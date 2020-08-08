import logging
import os
import random
import sys
import requests
import urllib.parse as urlparse

from bs4 import BeautifulSoup
from time import sleep
from threading import Thread, Event

from telegram.ext import Updater, CommandHandler

#%% variables
TOKEN = os.getenv("TOKEN_REPLICA")
url = "https://api.telegram.org/bot" + TOKEN

#%% initialization
announcement_thread = None

#Enabling logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger()


# Getting mode, so we could define run function for local and Heroku setup
mode = os.getenv("MODE", "dev")

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

# Special thread class
class myThread(Thread):
    def __init__(self, update, *args, **kwarg):
        super().__init__(*args, **kwarg)
        self.running_event = Event()
        self.update = update;

    def getAnnouncement(self, announcement):
        SITEURL = 'http://www.btu.edu.tr/index.php?dyr=' + str(announcement)

        page = requests.get(SITEURL)
        return page

        soup = BeautifulSoup(page.content, 'html.parser')

        container = soup.find_all("div", {"class" : "container"})[1]
        row = container.find_all("div", {"class" : "row"})[0]
        panel_body = row.find_all("div", {"class" : "panel-body"})[0]

        if announcement == 0:
            href_link = panel_body.find_all('a')[0]
            return href_link.get('href')
        else:
            return panel_body

    def run(self):
        while not self.running_event.isSet():
            try:
                last = self.getAnnouncement(0)
                print(last.status)
                update = self.update
                while not self.running_event.isSet():
                    sleep(2)
                    newLast = self.getAnnouncement(0)
                    if last != newLast:
                        last = newLast
                        parsedUrl = urlparse.urlparse(last)
                        dyr_query = urlparse.parse_qs(parsed.query)['dyr']
                        update.message.reply_text(self.getAnnouncement(dyr_query))
                break;
            except:
                print("Siteye şu anda ulaşılamıyor...")

    def stop_thread(self):
        self.running_event.set()

# Creating a handler-function for /start command
def replica_start(update, context):
    user = context.bot.getChatMember(update.message.chat_id,update.message.from_user['id'])
    global announcement_thread
    if user.status == "creator" or user.status == "administrator":
        update.message.reply_text("Komut başarıyla çalıştırıldı.")
        announcement_thread = myThread(update)
        announcement_thread.start()
    else:
        update.message.reply_text("Yalnızca admin ve yöneticiler komutları kullanabilir.")

# Creating a handler-function for /start command
def replica_stop(update, context):
    user = context.bot.getChatMember(update.message.chat_id,update.message.from_user['id'])
    global announcement_thread
    if user.status == "creator" or user.status == "administrator":
        update.message.reply_text("Komut başarıyla çalıştırıldı.")
        if announcement_thread != None:
            announcement_thread.stop_thread()
    else:
        update.message.reply_text("Yalnızca admin ve yöneticiler komutları kullanabilir.")

def main():
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater(TOKEN, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("rstart", replica_start))
    dp.add_handler(CommandHandler("rstop", replica_stop))


    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()

if __name__ == '__main__':
    main()
