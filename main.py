import logging
import os
import random
import sys
import requests

from telegram.ext import Updater, CommandHandler

#%% variables
TOKEN = os.getenv("TOKEN")
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

#%% Creating handler-functions for /* commands
def start(update, context):
    """Send a message when the command /help is issued."""
    
    help_message = "Merhaba, BTÜ ve Bilgisayar Mühendisliği Bölümü hakkında sorularınızı cevaplandırmak üzere buradayım."
    help_message += "Mevcut komutları görmek için /yardim komutunu kullanabilirsin. \n"
    update.message.reply_text(help_message)

def yardim(update, context):
    """Send a message when the command /help is issued."""
    
    help_message = "Mevcut komutları aşağıdaki listeden görebilirsin. \n"
    help_message += "Komut çalıştırmak için \"/\" karakteri ile gerekli komutu yazmalısın.\n\n"
    help_message += "Mevcut komutlar; \n\n"
    help_message += "/yardim -> Tüm komutları görmek istiyorum\n"
    help_message += "/hakkinda BMTanıtımBOT Geliştirici ekibi hakkında bilgi almak istiyorum\n"
    help_message += "/web_sayfasi BTÜ BM Web sayfasına erişmek istiyorum\n"
    help_message += "/akademik_tanitim Bölüm başkanlığı tanıtım videosunu görüntülemek istiyorum\n"
    help_message += "/ogrenci_tanitim Bölüm öğrencilerinin tanıtım videosunu görüntülemek istiyorum\n"
    help_message += "/mezun_tanitim Bölüm mezunlarının tanıtım videosunu görüntülemek istiyorum\n"
    help_message += "/akademik_personel Akademik personel hakkında bilgi almak istiyorum\n"
    help_message += "/bolum_tarihi Bölümün tarihi hakkında bilgi almak istiyorum\n"
    help_message += "/yok_atlas Bölüm YÖK Atlas sayfasına erişmek istiyorum\n"
    help_message += "/sep_bilgi BTÜ Sektörel Eğitim Programı hakkında bilgi almak istiyorum\n"
    help_message += "/sep_anlasmali_sirketler BTÜ-SEP kapsamında bölümün anlaşmalı olduğu şirketlerin listesini incelemek istiyorum\n"
    help_message += "/yazılım_kütüphanesi Bölümün anlaşmalı olduğu yazılım programlarının listesini verir.\n"
    help_message += "/lisans_program Bilgisayar Mühendisliği Lisans eğitim müfredatını görüntülemek istiyorum\n"
    help_message += "/bm_yl_program Bilgisayar Mühendisliği Yüksek Lisans eğitim müfredatını görüntülemek istiyorum\n"
    help_message += "/asm_yl_program Akıllı Sistemler Mühendisliği Yüksek Lisans eğitim müfredatını görüntülemek istiyorum\n"
    help_message += "/bm_yl_akademik_personel Bilgisayar Mühendisliği Yüksek Lisans Akademik Personeli hakkında bilgi almak istiyorum\n"
    help_message += "/asm_yl_akademik_personel Akıllı Sistemler Mühendisliği Yüksek Lisans Akademik Personeli hakkında bilgi almak istiyorum\n"
    help_message += "/erasmus Erasmus kontenjanları, anlaşmalı ülkelerin listesi, başvurmak için gerekli kısıtlar ve başvuru süreci hakkında bilgi almak istiyorum\n"
    help_message += "/farabi Farabi kontenjanları, anlaşmalı ülkelerin listesi, başvurmak için gerekli kısıtlar ve başvuru süreci hakkında bilgi almak istiyorum\n"
    help_message += "/mevlana Mevlana kontenjanları, anlaşmalı ülkelerin listesi, başvurmak için gerekli kısıtlar ve başvuru süreci hakkında bilgi almak istiyorum\n"
    help_message += "/cap ÇAP programı için koşullar ve başvuru süreci hakkında bilgi almak istiyorum\n"
    help_message += "/yandal Yandal programı için koşullar ve başvuru süreci hakkında bilgi almak istiyorum\n"
    help_message += "/laboratuvarlar Bölüm laboratuvarları hakkında bilgi almak istiyorum\n"
    help_message += "/staj Staj süreçlerini ve şartlarını öğrenmek istiyorum\n"
    help_message += "/anabilim_dallari Anabilim dallarını incelemek istiyorum\n"
    help_message += "/arastirma_gruplari_projeler Bölümdeki aktif araştırma grupları ve projeleri incelemek istiyorum\n"
    help_message += "/yayinlar Bölüm akademik kadrosu tarafından yapılan akademik yayınları incelemek istiyorum\n"
    update.message.reply_text(help_message)
    
def hakkinda(update, context):
    update.message.reply_text("Fatih Ateş, Furkan Portakal, Alperen Orhan ve Arş. Gör. Ahmet Kaşif tarafından BTÜ Bilgisayar Mühendisliği adına geliştirilmiştir.")

def web_sayfasi(update, context):
    update.message.reply_text("http://bilgisayar.btu.edu.tr adresinden erişebilirsiniz.")
    
def akademik_kadro(update, context):
    update.message.reply_text("Bölüm akademik kadrosuna http://bilgisayar.btu.edu.tr/index.php?page=akademikkadro&sid=6700 adresinden erişebilirsiniz")
    
def akademik_tanitim(update, context):
    update.message.reply_text("Bölüm başkanımızın tanıtım videosuna https://youtu.be/s0CPmkIeVLc adresinden erişebilirsiniz.")
    
def ogrenci_tanitim(update, context):
    update.message.reply_text("Güncellenmektedir.")
    
# Creating a handler-function for /start command 
def mezun_tanitim(update, context):
    update.message.reply_text("Bölüm başkanımız ve mezun öğrencimizin Youtube yayın kaydına https://youtu.be/aCWweagVyK8 adresinden erişebilirsiniz.")
    
# Creating a handler-function for /start command 
def bolum_tarihi(update, context):
    update.message.reply_text("Bursa Teknik Üniversitesi, Mühendislik ve Mimarlık Fakültesi içerisinde yer alan Bilgisayar Mühendisliği Bölümü 2015 yılında kurulmuştur. 2016 yılında KHK ile kapatılan Bursa Orhangazi Üniversitesi'nin Bilgisayar Mühendisliği (İngilizce) bölümü öğrencilerinin eğitimlerini sürdürebilmesi amacıyla YÖK tarafından bölümümüz İngilizce olarak eğitime başlamıştır. Şu an bölümümüzde 667 Karar Sayılı KHK Kapsamındaki Özel Öğrenciler ve Yabancı Öğrenciler öğrenimlerine %100 ingilizce olarak devam etmektedirler. Bu program, 'Özel ve Yabancı öğrenciler' mezun olduğunda kapanacaktır ve ÖSYM puanıyla öğrenci almamaktadır. Bilgisayar Mühendisliği (Türkçe) programı ise 2018 yılında isteğe bağlı İngilizce hazırlık sınıfı seçeneğiyle kurulmuş olup ilk öğrencilerini 2018 Üniversite Giriş sınavı sonuçlarıyla almıştır.")
    
# Creating a handler-function for /start command 
def yok_atlas(update, context):
    update.message.reply_text("Bölüm YÖK Atlas sayfasına https://yokatlas.yok.gov.tr/lisans.php?y=102410190 adresinden erişebilirsiniz.")

# Creating a handler-function for /start command 
def sep_bilgi(update, context):
    update.message.reply_text("http://sep.btu.edu.tr adresinden detaylı bilgi edinebilirsiniz.")
    
# Creating a handler-function for /start command 
def yazilim_kutuphanesi(update, context):
    update.message.reply_text("Bölümümüzün OnTheHub, Oracle Academy, Red Hat Linux ve Microsoft Azure programları ile anlaşması bulunmaktadır. Detaylar için web sayfamızı ziyaret ediniz.")
    
# Creating a handler-function for /start command 
def bm_yl_program(update, context):
    update.message.reply_text("Lisans Ders Planı için http://bilgisayar.btu.edu.tr/index.php?sid=6790 adresini ziyaret ediniz.")
    
# Creating a handler-function for /start command 
def asm_yl_program(update, context):
    update.message.reply_text("Güncellenmektedir.")
    
# Creating a handler-function for /start command 
def bm_yl_akademik_personel(update, context):
    update.message.reply_text("Güncellenmektedir.")
    
# Creating a handler-function for /start command 
def asm_yl_akademik_personel(update, context):
    update.message.reply_text("Güncellenmektedir.")
    
# Creating a handler-function for /start command 
def erasmus(update, context):
    update.message.reply_text("Bölümümüzün Almanya, İtalya, İspanya ve Kosova'da bulunan çeşitli üniversiteler ile Erasmus anlaşmaları bulunmaktadır.")
    
# Creating a handler-function for /start command 
def farabi(update, context):
    update.message.reply_text("Güncellenmektedir.")
    
# Creating a handler-function for /start command 
def mevlana(update, context):
    update.message.reply_text("Güncellenmektedir.")
    
# Creating a handler-function for /start command 
def laboratuvarlar(update, context):
    update.message.reply_text("Bölümümüzde 2 adet 55+1 pc kapasiteli ders laboratuvarı ve 1 adet 20+1 pc kapasiteli özel çalışma laboratuvarı bulunmaktadır. Tüm bilgisayarlarda Linux + Windows işletim sistemleri dual-boot modunda çalıştırılabilmektedir. Cihazların tamamı All-in-One cihazlardır. Ders laboratuvarındaki bilgisayarlar 16 GB Ram ve SSD disk özelliklerine sahiptir.")

# Creating a handler-function for /start command 
def staj(update, context):
    update.message.reply_text("Bölümümüzde mezuniyet için 2 adet zorunlu staj yükümlülüğü bulunmaktadır.")
    
# Creating a handler-function for /start command 
def anabilim_dallari(update, context):
    update.message.reply_text("Bölümümüzde Bilgisayar Yazılımı, Bilgisayar Bilimleri ve Bilgisayar Donanımı olmak üzere 3 anabilim dalı bulunmaktadır.")
    
# Creating a handler-function for /start command 
def arastirma_gruplari_projeler(update, context):
    update.message.reply_text("Güncellenmektedir.")
    
# Creating a handler-function for /start command 
def yayinlar(update, context):
    update.message.reply_text("Güncellenmektedir.")
    
# Creating a handler-function for /start command 
def sss(update, context):
    help_message = "Soru: BTÜ'de telegram hizmeti veren diğer bölümlere nasıl ulaşabilirim ?\nCevap: Bu grup sadece Bilgisayar Mühendisliği öğrenci adayları için oluşturulmuş olup, diğer bölüm personelleri ile iletişime geçmeniz gerekmektedir. Bununla birlikte bildiğimiz kadarıyla Elektrik-Elektronik bölümünün de bir Telegram grubu bulunmaktadır.\n\n"
    help_message += "Soru: BTÜ yurt olanakları nelerdir ?\nCevap: Özel yurt olanakları hem kız hem erkek öğrenciler için Üniversite kampüsleri yakınında bulunmaktadır. Erkek öğrenciler için Mimar Sinan kampüsünün yanı başında KYK yurdu bulunmakta, kız öğrenciler için ise henüz bir devlet yurdu imkanı bulunmamaktadır. Bununla birlikte inşaatı ve projelendirmesi devam eden 2 kız yurdu projesi bulunmaktadır. Bunlardan Mimar Sinan kampüsü içerisindekinin 2021 bahar yarıyılı sonuna kadar tamamlanması hedeflenmektedir.\n"
    update.message.reply_text(help_message)

def main():
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater(TOKEN, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("yardim", yardim))
    dp.add_handler(CommandHandler("hakkinda", hakkinda))
    dp.add_handler(CommandHandler("web_sayfasi", web_sayfasi))
    dp.add_handler(CommandHandler("akademik_tanitim", akademik_tanitim))
    dp.add_handler(CommandHandler("ogrenci_tanitim", ogrenci_tanitim))
    dp.add_handler(CommandHandler("mezun_tanitim", mezun_tanitim))
    dp.add_handler(CommandHandler("bolum_tarihi", bolum_tarihi))
    dp.add_handler(CommandHandler("yok_atlas", yok_atlas))
    dp.add_handler(CommandHandler("sep_bilgi", sep_bilgi))
    dp.add_handler(CommandHandler("yazilim_kutuphanesi", yazilim_kutuphanesi))
    dp.add_handler(CommandHandler("bm_yl_program", bm_yl_program))
    dp.add_handler(CommandHandler("asm_yl_program", asm_yl_program))
    dp.add_handler(CommandHandler("bm_yl_akademik_personel", bm_yl_akademik_personel))
    dp.add_handler(CommandHandler("asm_yl_akademik_personel", asm_yl_akademik_personel))
    dp.add_handler(CommandHandler("erasmus", erasmus))
    dp.add_handler(CommandHandler("farabi", farabi))
    dp.add_handler(CommandHandler("mevlana", mevlana))
    dp.add_handler(CommandHandler("laboratuvarlar", laboratuvarlar))
    dp.add_handler(CommandHandler("staj", staj))
    dp.add_handler(CommandHandler("anabilim_dallari", anabilim_dallari))
    dp.add_handler(CommandHandler("arastirma_gruplari_projeler", arastirma_gruplari_projeler))
    dp.add_handler(CommandHandler("yayinlar", yayinlar))
    
    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()

if __name__ == '__main__':
    main()