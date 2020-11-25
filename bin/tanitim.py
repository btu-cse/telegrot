import logging
import os
import sys

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler

#%% variables
TOKEN = os.getenv("TANITIM_TOKEN")
url = "https://api.telegram.org/bot" + TOKEN

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
        HEROKU_APP_NAME = os.environ.get("HEROKU_APP_NAME")
        updater.start_webhook(listen="0.0.0.1",
                              port=PORT,
                              url_path=TOKEN)
        updater.bot.set_webhook("https://{}.herokuapp.com/{}".format(HEROKU_APP_NAME, TOKEN))
        updater.idle()
else:
    logger.error("No MODE specified!")
    sys.exit(1)

#%% Creating handler-functions for /* commands
def start(update, context):
    """Send a message when the command /help is issued."""

    help_message = "Merhaba, BTÜ ve Bilgisayar Mühendisliği Bölümü hakkında sorularınızı cevaplandırmak üzere buradayım."
    help_message = "Bu grup sadece Bilgisayar Mühendisliği öğrenci adayları için oluşturulmuş olup, diğer bölüm personelleri ile iletişime geçmeniz gerekmektedir. Bununla birlikte bildiğimiz kadarıyla Elektrik-Elektronik bölümünün de bir Telegram grubu bulunmaktadır."
    help_message += "Mevcut komutları görmek için /help komutunu kullanabilirsin.\n"
    update.message.reply_text(help_message)

def help(update, context):
    """Send a message when the command /help is issued."""

    help_message = "Mevcut komutları aşağıdaki listeden görebilirsin. \n"
    help_message += "Komut çalıştırmak için \"/\" karakteri ile gerekli komutu yazmalısın.\n"
    help_message += "Grupta bulunduğunuz süre içerisinde diğer adaylar ve bölüm personeli ile saygı ve iyi niyet çerçevesinde iletişim kurmaya ve grubun amacı dışında herhangi bir söylemde bulunmamaya özen gösteriniz.\n"
    help_message += "Mevcut komutlar; \n"
    help_message += "/help - Tüm komutları görmek istiyorum\n"
    help_message += "/hakkinda - Geliştirici ekibi\n"
    help_message += "/web_sayfasi - BTÜ BM Web sayfası\n"
    help_message += "/akademik_tanitim - Bölüm başkanlığı tanıtım videosu\n"
    help_message += "/youtube_tanitim - Youtube'da BTÜ BM tanıtım videosu\n"
    help_message += "/akademik_kadro - Akademik kadro\n"
    help_message += "/bolum_tarihi - Bölümün tarihi\n"
    help_message += "/yok_atlas - YÖK Atlas sayfasına\n"
    help_message += "/sep_bilgi - BTÜ Sektörel Eğitim Programı\n"
    help_message += "/sep_anlasmali_sirketler BTÜ-SEP anlaşmalı şirketler\n"
    help_message += "/yazilim_kutuphanesi Bölüm ile anlaşmalı yazılımlar\n"
    help_message += "/ogrencimiz_gozunden Bölümümüzü bir de öğrencimizden dinleyin\n\n"
    help_message += "/ogrenci_klupleri BTÜ öğrenci klüpleri\n"
    help_message += "/lisans_programi Lisans eğitim planı\n"
    help_message += "/erasmus Erasmus\n\n"
    help_message += "/farabi Farabi \n"
    help_message += "/mevlana Mevlana\n"
    help_message += "/cap ÇAP \n"
    help_message += "/yandal Yandal\n"
    help_message += "/laboratuvarlar Bölüm laboratuvarları \n"
    help_message += "/staj Staj süreçleri\n"
    help_message += "/anabilim_dallari Anabilim dalları\n"
    help_message += "/arastirma_gruplari_projeler Bölümdeki aktif araştırma grupları ve projeler\n"
    help_message += "/yayinlar Akademik kadrosu tarafından yapılan yayınlar\n"
    help_message += "/yurt Yurt olanakları\n"
    help_message += "/mudek MÜDEK Akreditasyonunuz var mı ?\n"
    help_message += "/mezun_yl Yurt dışında Yüksek Lisans olanakları neler ?\n"
    help_message += "/prog_dilleri Bölümünüzdeki derslerde hangi programlama dilleri verilmektedir ?\n"
    help_message += "/btubm_sosyal Sosyal medya hesaplarımız\n"
    update.message.reply_text(help_message)

def hakkinda(update, context):
    update.message.reply_text("Tanıtım destek botumuz, bölüm öğrencilerimiz Fatih Ateş, Furkan Portakal, Alperen Orhan ve Arş. Gör. Ahmet Kaşif tarafından geliştirilmiştir. Öneri ve isteklerinizi için : @ahmetkasif"
    + str(new_question_message()), reply_markup=new_question_keyboard())

def web_sayfasi(update, context):
    update.message.reply_text("Bölüm Web sayfamıza http://bilgisayar.btu.edu.tr adresinden erişebilirsiniz."
    + str(new_question_message()), reply_markup=new_question_keyboard())

def akademik_tanitim(update, context):
    update.message.reply_text("Bölüm başkanımızın tanıtım videosuna https://youtu.be/s0CPmkIeVLc adresinden erişebilirsiniz."
    + str(new_question_message()), reply_markup=new_question_keyboard())

def youtube_tanitim(update, context):
    update.message.reply_text("Bölüm başkanımız ve mezun öğrencimizin Youtube yayın kaydına https://youtu.be/aCWweagVyK8 adresinden erişebilirsiniz."
    + str(new_question_message()), reply_markup=new_question_keyboard())

def akademik_kadro(update, context):
    update.message.reply_text("Bölümümüzde 1 Profesör, 1 Doçent, 6 Doktor Öğretim Üyesi ve 5 Araştırma Görevlisi görev yapmaktadır. Akademik Personel Yapay Zeka, Veri Madenciliği, Siber Güvenlik, Bioinformatik gibi alanlarda uzmanlıklara sahiptir. Detaylara http://bilgisayar.btu.edu.tr/index.php?page=akademikkadro&sid=6700 adresinden erişebilirsiniz"
    + str(new_question_message()), reply_markup=new_question_keyboard())

def bolum_tarihi(update, context):
    update.message.reply_text("Bursa Teknik Üniversitesi, Mühendislik ve Mimarlık Fakültesi içerisinde yer alan Bilgisayar Mühendisliği Bölümü 2015 yılında kurulmuştur. 2016 yılında KHK ile kapatılan Bursa Orhangazi Üniversitesi'nin Bilgisayar Mühendisliği (İngilizce) bölümü öğrencilerinin eğitimlerini sürdürebilmesi amacıyla YÖK tarafından bölümümüz İngilizce olarak eğitime başlamıştır. Şu an bölümümüzde 667 Karar Sayılı KHK Kapsamındaki Özel Öğrenciler ve Yabancı Öğrenciler öğrenimlerine %100 ingilizce olarak devam etmektedirler. Bu program, 'Özel ve Yabancı öğrenciler' mezun olduğunda kapanacaktır ve ÖSYM puanıyla öğrenci almamaktadır. Bilgisayar Mühendisliği (Türkçe) programı ise 2018 yılında isteğe bağlı İngilizce hazırlık sınıfı seçeneğiyle kurulmuş olup ilk öğrencilerini 2018 Üniversite Giriş sınavı sonuçlarıyla almıştır."
    + str(new_question_message()), reply_markup=new_question_keyboard())

def yok_atlas(update, context):
    update.message.reply_text("Bölüm YÖK Atlas sayfasına https://yokatlas.yok.gov.tr/lisans.php?y=102410190 adresinden erişebilirsiniz."
    + str(new_question_message()), reply_markup=new_question_keyboard())

def sep_bilgi(update, context):
    update.message.reply_text("SEP programı ÖSYM kılavuzunda özel koşul olarak yer almaktadır, bütün öğrencilerimiz dahildir. 7 dönem ders ve 1 dönem proje bazlı işyeri eğitimi vardır. İşyeri eğitimi süresince devlet tarafından SGK nız ödenir ve asgari ücretin 1/3 ü kadar maaş alırsınız. İşyeri eğitimi yaptığınız işveren sizi işe aldığında işverene de devlet teşviği vardır. Daha fazlası için http://sep.btu.edu.tr adresinden detaylı bilgi edinebilirsiniz."
    + str(new_question_message()), reply_markup=new_question_keyboard())

def sep_anlasmali_sirketler(update, context):
    update.message.reply_text("SEP anlaşmalı şirketler listesine http://sep.btu.edu.tr adresinden erişebilirsiniz."
    + str(new_question_message()), reply_markup=new_question_keyboard())

def yazilim_kutuphanesi(update, context):
    update.message.reply_text("Bölümümüzün OnTheHub, Oracle Academy, Red Hat Linux ve Microsoft Azure programları ile anlaşması bulunmaktadır. Detaylar için web sayfamızı ziyaret ediniz."
    + str(new_question_message()), reply_markup=new_question_keyboard())

def ogrencimiz_gozunden(update, context):
    update.message.reply_text("Bölüm öğrencimiz Furkan Portakal'ın medium makalesine https://medium.com/@furkanportakal/neden-bursa-teknik-ed101c4a78f3 adresinden erişebilirsiniz."
    + str(new_question_message()), reply_markup=new_question_keyboard())

def ogrenci_klupleri(update, context):
    update.message.reply_text("BTÜ Öğrenci klüpleri listesine http://www.btu.edu.tr/index.php?sid=48 adresinden erişebilirsiniz."
    + str(new_question_message()), reply_markup=new_question_keyboard())

def lisans_programi(update, context):
    update.message.reply_text("Ders içeriklerine http://bilgisayar.btu.edu.tr/index.php?sid=6790 adresinden erişebilirsiniz."
    + str(new_question_message()), reply_markup=new_question_keyboard())

def erasmus(update, context):
    update.message.reply_text("Bölümümüzün Almanya, İtalya, İspanya ve Kosova'da bulunan çeşitli üniversiteler ile Erasmus anlaşmaları bulunmaktadır. Geçtiğimiz yıl 2 öğrenci Erasmus ile yurtdışında eğitim görme hakkı elde etmiştir."
    + str(new_question_message()), reply_markup=new_question_keyboard())

def farabi(update, context):
    update.message.reply_text("BTÜ Farabi koordinatörlük sayfasına http://farabi.btu.edu.tr/ adresinden erişebilirsiniz."
    + str(new_question_message()), reply_markup=new_question_keyboard())

def mevlana(update, context):
    update.message.reply_text("Güncellenmektedir." + str(new_question_message()), reply_markup=new_question_keyboard())

def cap(update, context):
    update.message.reply_text("Bilgisayar Mühendisliği öğrencilerinin BTÜ'deki diğer tüm bölümler ile ÇAP yapma imkanı bulunmaktadır"
    + str(new_question_message()), reply_markup=new_question_keyboard())

def yandal(update, context):
    update.message.reply_text("Güncellenmektedir." + str(new_question_message()), reply_markup=new_question_keyboard())

def laboratuvarlar(update, context):
    update.message.reply_text("Bölümümüzde 2 adet 55+1 pc kapasiteli ders laboratuvarı ve 1 adet 20+1 pc kapasiteli özel çalışma laboratuvarı bulunmaktadır. Tüm bilgisayarlarda Linux + Windows işletim sistemleri dual-boot modunda çalıştırılabilmektedir. Cihazların tamamı All-in-One cihazlardır. Ders laboratuvarındaki bilgisayarlar 16 GB Ram ve SSD disk özelliklerine sahiptir."
    + str(new_question_message()), reply_markup=new_question_keyboard())

def staj(update, context):
    update.message.reply_text("Bölümümüzde mezuniyet için 2 adet zorunlu staj yükümlülüğü bulunmaktadır."
    + str(new_question_message()), reply_markup=new_question_keyboard())

def anabilim_dallari(update, context):
    update.message.reply_text("Bölümümüzde Bilgisayar Yazılımı, Bilgisayar Bilimleri ve Bilgisayar Donanımı olmak üzere 3 anabilim dalı bulunmaktadır."
    + str(new_question_message()), reply_markup=new_question_keyboard())

def arastirma_gruplari_projeler(update, context):
    update.message.reply_text("Güncellenmektedir." + str(new_question_message()), reply_markup=new_question_keyboard())

def yayinlar(update, context):
    update.message.reply_text("Güncellenmektedir." + str(new_question_message()), reply_markup=new_question_keyboard())

def yurt(update, context):
    update.message.reply_text("Özel yurt olanakları hem kız hem erkek öğrenciler için Üniversite kampüsleri yakınında bulunmaktadır. Erkek öğrenciler için Mimar Sinan kampüsünün yanı başında KYK yurdu bulunmakta, kız öğrenciler için ise henüz bir devlet yurdu imkanı bulunmamaktadır. Bununla birlikte inşaatı ve projelendirmesi devam eden 2 kız yurdu projesi bulunmaktadır. Bunlardan Mimar Sinan kampüsü içerisindekinin 2021 bahar yarıyılı sonuna kadar tamamlanması hedeflenmektedir."
    + str(new_question_message()), reply_markup=new_question_keyboard())

def mudek(update, context):
    update.message.reply_text("Bir bölüm ilk mezununu verdikten sonra akreditasyon için başvurabiliyor. Bilgisayar Müh. Türkçe programı 2018'den beri öğrenci alıyor, mezun verildiğinde akreditasyon başvurusu yapılacaktır"
    + str(new_question_message()), reply_markup=new_question_keyboard())

def mezun_yl(update, context):
    update.message.reply_text("Bölümümüz 2017 den beri mezun vermektedir, bu mezunların büyük bir kısmı yabancı kökenli öğrenciler olduğu için çoğu yurt dışındadır. Bu yıl mezun olan öğrencilerilerimizden bir öğrencimiz de bu gruptadır, diplomasını aldığı gün Bursa'da Nestle Ar-Ge merkezinde işe başladı"
    + str(new_question_message()), reply_markup=new_question_keyboard())

def prog_dilleri(update, context):
    update.message.reply_text("Bölümümüzde eğitim gören öğrenciler, 4 yıllık eğitimleri boyunca C, C++, C#, Python, Java, Html, Javascript, CSS, XML, PHP dilleri ile aşina olmakta, SEP programı ile entegre sektörde kodlama tecrübelerini pekiştirmektedirler."
    + str(new_question_message()), reply_markup=new_question_keyboard())

def btubm_sosyal(update, context):
    update.message.reply_text("Instagram hesabımıza @btu.bm adı üzerinden erişebilirsiniz. Hesap, bölümümüz öğrencileri tarafından yönetilmektedir."
    + str(new_question_message()), reply_markup=new_question_keyboard())

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
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("hakkinda", hakkinda))
    dp.add_handler(CommandHandler("web_sayfasi", web_sayfasi))
    dp.add_handler(CommandHandler("akademik_tanitim", akademik_tanitim))
    dp.add_handler(CommandHandler("youtube_tanitim", youtube_tanitim))
    dp.add_handler(CommandHandler("akademik_kadro", akademik_kadro))
    dp.add_handler(CommandHandler("bolum_tarihi", bolum_tarihi))
    dp.add_handler(CommandHandler("yok_atlas", yok_atlas))
    dp.add_handler(CommandHandler("sep_bilgi", sep_bilgi))
    dp.add_handler(CommandHandler("sep_anlasmali_sirketler", sep_anlasmali_sirketler))
    dp.add_handler(CommandHandler("yazilim_kutuphanesi", yazilim_kutuphanesi))
    dp.add_handler(CommandHandler("ogrencimiz_gozunden", ogrencimiz_gozunden))
    dp.add_handler(CommandHandler("ogrenci_klupleri", ogrenci_klupleri))
    dp.add_handler(CommandHandler("lisans_programi", lisans_programi))
    dp.add_handler(CommandHandler("erasmus", erasmus))
    dp.add_handler(CommandHandler("farabi", farabi))
    dp.add_handler(CommandHandler("mevlana", mevlana))
    dp.add_handler(CommandHandler("cap", cap))
    dp.add_handler(CommandHandler("yandal", yandal))
    dp.add_handler(CommandHandler("laboratuvarlar", laboratuvarlar))
    dp.add_handler(CommandHandler("staj", staj))
    dp.add_handler(CommandHandler("anabilim_dallari", anabilim_dallari))
    dp.add_handler(CommandHandler("arastirma_gruplari_projeler", arastirma_gruplari_projeler))
    dp.add_handler(CommandHandler("yayinlar", yayinlar))
    dp.add_handler(CommandHandler("yurt", yurt))
    dp.add_handler(CommandHandler("mudek", mudek))
    dp.add_handler(CommandHandler("mezun_yl", mezun_yl))
    dp.add_handler(CommandHandler("prog_dilleri", prog_dilleri))
    dp.add_handler(CommandHandler("btubm_sosyal", btubm_sosyal))
    dp.add_handler(CallbackQueryHandler(new_question_callback, pattern='new_question_yes'))
    dp.add_handler(CallbackQueryHandler(new_question_callback, pattern='new_question_no'))

    run(updater)

if __name__ == '__main__':
    main()
