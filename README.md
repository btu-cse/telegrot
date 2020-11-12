# KURULUM
Bu depodaki kodlar Python3 aracığıyla yazılmıştır. Python3'ün en son versiyonunu bilgisayarınıza kurmak için;
> Python3: https://www.python.org/downloads/

Programın çalışması için gerekli paketleri pip3 aracılığıyla paketleri kurmak için deponun indirildiği dizine gelin ve çalıştırın;
> pip3 install requirements.txt

### API BİLGİSİ
Bu depoda iki ayrı bot bulunmaktadır. Her telegram botunun kendine özel API-TOKEN bilgisi vardır. Buradaki depo Heroku tarafıyla otomatik etkileşimli olduğu için 
TOKEN bilgisi güvenlik nedeniyle Heroku üzerinde saklanmaktadır. 

## NASIL ÇALIŞTIRILIR ?
### Tanıtım Botu
Gerekli kurulumları yaptıktan sonra tanıtım botunun bir kopyasını çalıştırmak için öncelikle "tanitim.py" içerisinde 9. satırdaki "TOKEN" değişkenini kendi
botunuzun TOKEN bilgisi ile değiştirmelisiniz ve ardından 17. satırdaki "mode" değişkenini "dev" olarak güncellemelisiniz. Ardıdan tanıtım botunuzu aşağıdaki komutla başlatabilirsiniz:
> python3 tanitim.py

!Bir bot aynı anda iki farklı betik üzerinden çalıştırılamaz. Çalıştırılması halinde çatışma(Conflict) hatası alınacaktır ve her iki betikte çalışma zamanında zarar
görecektir.

### Duyuru Replica Bot

Gerekli kurulumları yaptıktan sonra tanıtım botunun bir kopyasını çalıştırmak için öncelikle "tanitim.py" içerisinde 18. satırdaki "TOKEN" değişkenini kendi
botunuzun TOKEN bilgisi ile değiştirmelisiniz ve ardından 27. satırdaki "mode" değişkenini "dev" olarak güncellemelisiniz. Ardıdan tanıtım botunuzu aşağıdaki komutla başlatabilirsiniz:
> python3 replica.py

!Bir bot aynı anda iki farklı betik üzerinden çalıştırılamaz. Çalıştırılması halinde çatışma(Conflict) hatası alınacaktır ve her iki betikte çalışma zamanında zarar
görecektir.

## HEROKU İLE ÇALIŞMAK

&emsp;Heroku üzerinde bir uygulama oluşturmak ve Github hesabını bağlamak için aşağıdaki makaleyi inceleyiniz;
> https://trailhead.salesforce.com/en/content/learn/projects/develop-heroku-applications/create-a-heroku-app

Heroku ücretsiz planda varsayılan olarak çalışan her bir işlemi günde bir kere SIGTERM göndererek öldürür ve daha sonra yeniden ayağa kaldırır. Bu  sizin
veri kaybetmenize neden olur. Programınızı bu bağlamda yazmanız gerekmektedir. Herokunun Dynoları ile ilgili daha detaylı bilgi için; 
> https://devcenter.heroku.com/articles/dynos

Heroku üzerindeki çalışan işlemlerinizi kontrollü olarak yeniden yapılandırmaya zamanlamak için öncelikle bir eklenti kurmak gerekiyor;
> Scheduler: https://elements.heroku.com/addons/scheduler

Eklentiyi kurduktan sonra iki adet yapılandırma değişkeni eklememiz gerekiyor. Uygulamanızın ayarlar bölümüne gelin ve Ayar Değişkenleri bölümünde
Yapılandırma Değişkenlerini Göster butonuna tıklayın. Ardından aşağıdaki anahtar ve değerleri ekleyin.
> KEY: HEROKU_APP_NAME | VALUE=[SİZİN_UYGULAMA_ADINIZ]
> KEY: HEROKU_AUTH_TOKEN | VALUE=[SİZİN_UYGULAMA_ADINIZ]

Eklentiyi kurduktan sonra uygulama ana sayfanızda kurulu eklentiler "Yüklü Eklentiler" kısmından Scheduler'ı seçin. Uygulama ana sayfanıza gitmek için aşağıdaki bağlantıda
kendi uygulama adınızı yazarak gidebilirsiniz;
> https://dashboard.heroku.com/apps/[HEROKU_APP_NAME]


