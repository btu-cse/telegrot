# KURULUM
&emsp;&emsp;Bu depodaki kodlar Python3 aracığıyla yazılmıştır. Python3'ün en son versiyonunu bilgisayarınıza kurmak için;
> Python3: https://www.python.org/downloads/

Programın çalışması için gerekli paketleri pip3 aracılığıyla paketleri kurmak için deponun indirildiği dizine gelin ve çalıştırın;

    pip3 install requirements.txt

### API BİLGİSİ
&emsp;&emsp;Bu depoda iki ayrı bot bulunmaktadır. Her telegram botunun kendine özel API-TOKEN bilgisi vardır. Buradaki depo Heroku tarafıyla otomatik etkileşimli olduğu için 
TOKEN bilgisi güvenlik nedeniyle Heroku üzerinde saklanmaktadır. 

## NASIL ÇALIŞTIRILIR ?
### Tanıtım Botu
&emsp;&emsp;Gerekli kurulumları yaptıktan sonra tanıtım botunun bir kopyasını çalıştırmak için öncelikle "tanitim.py" içerisinde 9. satırdaki "TOKEN" değişkenini kendi botunuzun TOKEN bilgisi ile değiştirmelisiniz ve ardından 17. satırdaki "mode" değişkenini "dev" olarak güncellemelisiniz. Ardıdan tanıtım botunuzu aşağıdaki komutla başlatabilirsiniz:
    
    python3 tanitim.py

!Bir bot aynı anda iki farklı betik üzerinden çalıştırılamaz. Çalıştırılması halinde çatışma(Conflict) hatası alınacaktır ve her iki betikte çalışma zamanında zarar görecektir.

### Duyuru Replica Bot

&emsp;&emsp;Gerekli kurulumları yaptıktan sonra tanıtım botunun bir kopyasını çalıştırmak için öncelikle "tanitim.py" içerisinde 18. satırdaki "TOKEN" değişkenini kendi
botunuzun TOKEN bilgisi ile değiştirmelisiniz ve ardından 27. satırdaki "mode" değişkenini "dev" olarak güncellemelisiniz. Ardıdan tanıtım botunuzu aşağıdaki komutla başlatabilirsiniz:
    
    python3 replica.py

!Bir bot aynı anda iki farklı betik üzerinden çalıştırılamaz. Çalıştırılması halinde çatışma(Conflict) hatası alınacaktır ve her iki betikte çalışma zamanında zarargörecektir.

## HEROKU İLE ÇALIŞMAK

&emsp;&emsp;Heroku üzerinde bir uygulama oluşturmak ve Github hesabını bağlamak için aşağıdaki makaleyi inceleyiniz;
> https://trailhead.salesforce.com/en/content/learn/projects/develop-heroku-applications/create-a-heroku-app

&emsp;&emsp;Heroku üzerinde Python betiği çalıştırmak için iki adet ek dosyaya ihtiyaç duyuyor. Bunlar Requirements.txt ve Procfile. Requirements.txt içerisinde versiyonları ile birlikte paket isimlerimiz bulunuyor. Procfile içerisinde ise heroku dilinde Dyno olarak adlandırdığımız komutlarımız bulunuyor. Herokuda bir depoyu dağıttığımızda Dynolarımızı yenilememiz gerekir. Aşağıdaki linkten istediğiniz işlemi seçerek önce pasif daha sonra tekrar aktif hale getirerek çözebilirsiniz.
> Dynolarınız: https://dashboard.heroku.com/apps/[SİZİN_HEROKU_UYGULAMA_ADINIZ]/resources

Komut satırından Dyno'lar üzerinde işlem yapmak için ise;

- Yeni bir işlem atamak;

      heroku ps:scale worker.1 --app=[SİZİN_UYGULAMA_ADINIZ]
      
- Var olan işlemi yeniden başlatmak;

      heroku ps:restart worker.1 --app=[SİZİN_UYGULAMA_ADINIZ]
      
- Çalışan bir işlemi durdurmak;

      heroku ps:stop worker.1 --app=[SİZİN_UYGULAMA_ADINIZ]

&emsp;&emsp;Heroku ücretsiz planda varsayılan olarak çalışan her bir işlemi günde bir kere SIGTERM göndererek öldürür ve daha sonra yeniden ayağa kaldırır. Bu  sizin
veri kaybetmenize neden olur. Programınızı bu bağlamda yazmanız gerekmektedir. Herokunun Dynoları ile ilgili daha detaylı bilgi için; 
> https://devcenter.heroku.com/articles/dynos

&emsp;&emsp;Heroku üzerindeki çalışan işlemlerinizi kontrollü olarak yeniden yapılandırmaya zamanlamak için öncelikle bir eklenti kurmak gerekiyor;
> Scheduler: https://elements.heroku.com/addons/scheduler

&emsp;&emsp;Eklentiyi kurduktan sonra iki adet yapılandırma değişkeni eklememiz gerekiyor. Uygulamanızın ayarlar bölümüne gelin ve Ayar Değişkenleri bölümünde
Yapılandırma Değişkenlerini Göster butonuna tıklayın. Ardından aşağıdaki anahtar ve değerleri ekleyin.
> KEY: HEROKU_APP_NAME      VALUE=[SİZİN_UYGULAMA_ADINIZ]  
> KEY: HEROKU_AUTH_TOKEN    VALUE=[SİZİN_AUTH_TOKEN_DEĞERİNİZ]

AUTH TOKEN DEĞERİNİZİ aşağıdaki linkte verilen yolları izleyerek elde edebilirsiniz. Auth token değeriniz machine api.heroku.com altındaki "password" değeridir.

&emsp;&emsp;Daha sonra uygulama ana sayfanızda kurulu eklentiler "Yüklü Eklentiler" kısmından Scheduler'ı seçin. Uygulama ana sayfanıza gitmek için aşağıdaki bağlantıda kendi uygulama adınızı yazarak gidebilirsiniz;
> https://dashboard.heroku.com/apps/[SİZİN_UYGULAMA_ADINIZ]

Eklenti sayfasında "İş Ekle" butonuna tıklayarak yeni bir bash komutu zamanlayacağız. İş ekle dedikten sonra açılan pencerede zamanlayıcıyı isteğinize göre ayarlayın ve çalıştırılacak komut alanına aşağıda verilecek bash komutunu ekleyin.

    curl -n -X DELETE https://api.heroku.com/apps/${HEROKU_APP_NAME}/dynos \ -H "Content-Type: application/json" \ -H "Accept: application/vnd.heroku+json; version=3" \n -H "Authorization: Bearer ${HEROKU_AUTH_TOKEN}"
    
İşlem tamam. Zamanlayıcı kuruldu!



