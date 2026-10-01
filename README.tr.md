<p align="center">
  <img src="assets/icon.png" alt="Birim Dönüştürücü ikonu" width="96">
</p>

<h1 align="center">Birim Dönüştürücü</h1>

<p align="center">
  <a href="README.md">English</a> | <b>Türkçe</b>
</p>

<p align="center">
  Python ve Tkinter ile yazılmış bir masaüstü birim dönüştürücü: dokuz kategori, günlük kurlarla 166 para birimi,<br>
  Türk mutfak ölçüleri ve GB ile GiB farkı. Hesaplar <code>Decimal</code> ile kesin yapılır.
</p>

<p align="center">
  <a href="https://github.com/MrcDprm/unit-converter/releases/latest"><b>⬇️ Windows için indir</b></a>
</p>

<p align="center">
  <img src="docs/demo.gif" alt="Birim dönüştürücünün kullanımını gösteren animasyon" width="720">
</p>

## Özellikler

**Dönüşüm**
- **Dokuz kategori, 58 birim:** uzunluk, ağırlık, sıcaklık, hacim, alan, hız, zaman, veri boyutu ve döviz
- **Canlı ve iki yönlü:** Hangi kutuya yazarsan diğeri güncellenir; ⇅ düğmesi birimlerin yerini değiştirir
- **Tüm birimler tek bakışta:** Değerin kategorideki bütün birimlerdeki karşılığı bir tabloda; satıra tıklayınca kopyalanır
- **Türk mutfak ölçüleri:** su bardağı, çay bardağı, yemek kaşığı, tatlı kaşığı ve çay kaşığı; yanında ABD ölçüleri (cup, fl oz)
- **GB ve GiB:** 10'luk ve 2'lik veri birimleri yan yana; 1 TB diskin Windows'ta neden 931 GB göründüğünü gösterir
- **Kesin sonuç:** `Decimal` ile hesap (`0.30000000000000004` yok), 12 anlamlı basamağa yuvarlama, çok büyük ve çok küçük sayılar için bilimsel gösterim
- **Girdi kontrolü:** Mutlak sıfırın altındaki sıcaklık, geçersiz sayı ve sınır dışı değerler için yanlış sonuç yerine anlaşılır bir mesaj

**Döviz**
- Ücretsiz [ExchangeRate-API](https://www.exchangerate-api.com)'den 166 para birimi (API anahtarı gerekmez)
- Kurlar arka planda indirilir; pencere hiç donmaz
- Kurlar tarihiyle kaydedilir; internet yoksa son kurlarla çalışmaya devam eder ve kurların ne kadar eski olduğunu söyler
- Yaygın para birimleri (TRY, USD, EUR, GBP…) listenin başında

**Arayüz**
- Son 50 dönüşümün geçmişi; tıklayınca geri gelir
- Koyu ve açık tema, Türkçe ve İngilizce arayüz
- Sayılar seçili dile göre yazılır ve okunur: Türkçede `1.234,5`, İngilizcede `1,234.5`
- Son kategori, birimler, tema ve dil hatırlanır

**Diğer**
- 38 birim testi
- Kurulum sihirbazı: Başlat menüsü kısayolu, kaldırma desteği

## Ekran Görüntüleri

| Veri boyutu (koyu, Türkçe) | Türk mutfak ölçüleriyle hacim |
|---|---|
| <img src="docs/data-dark.png" alt="Koyu temada veri boyutu kategorisi" width="420"> | <img src="docs/volume-dark.png" alt="Türk mutfak ölçüleriyle hacim kategorisi" width="420"> |

**Döviz (açık, İngilizce)**

<img src="docs/currency-light-en.png" alt="Açık tema ve İngilizce arayüzde döviz kategorisi" width="620">

## Kurulum

1. [Releases](https://github.com/MrcDprm/unit-converter/releases/latest) sayfasından `UnitConverter-x.y.z-Setup.exe` dosyasını indir.
2. Çalıştır ve kurulum adımlarını izle. Yönetici izni gerekmez.
3. Uygulamayı Başlat menüsünde **Birim Dönüştürücü** adıyla bul. Arayüz Türkçe açılır; sol alttaki dil düğmesi İngilizceye çevirir.

> **Windows "Bilgisayarınız korundu" uyarısı:** Uygulama dijital olarak imzalı olmadığı için Windows SmartScreen ilk açılışta uyarı gösterebilir. **Ek bilgi → Yine de çalıştır** ile devam edebilirsin. Kaynak kodun tamamı bu depoda açık.

**Kaldırma:** Ayarlar → Uygulamalar → Yüklü uygulamalar → Birim Dönüştürücü → Kaldır.
Geçmiş, ayarlar ve kaydedilen kurlar `%USERPROFILE%\.unit-converter` klasöründe tutulur ve kaldırırken silinmez.

## Klavye Kısayolları

| Tuş | İşlev |
|---|---|
| `Ctrl+1` … `Ctrl+9` | Kategori değiştir |
| `Ctrl+R` | Birimlerin yerini değiştir |
| `Ctrl+Shift+C` | Sonucu kopyala |
| `Enter` | Dönüşümü hemen geçmişe kaydet |
| `Esc` | Girdiyi temizle |
| `F5` | Döviz kurlarını yeniden yükle |

## Kullanılan Teknolojiler

- **Python 3.12**: sadece standart kütüphane, harici paket yok
- **Tkinter / ttk**: kullanıcı arayüzü
- **decimal**: kesin hesap
- **urllib, threading, queue**: kurları arka planda indirme
- **unittest**: birim testleri
- **PyInstaller**: Windows `.exe` derlemesi
- **Inno Setup**: kurulum sihirbazı

## Proje Yapısı

```
unit-converter/
├── main.py         # Giriş noktası
├── gui.py          # Tkinter arayüzü
├── units.py        # Kategoriler ve birim tabloları
├── converter.py    # Sayı okuma ve dönüşüm
├── formatter.py    # Sayıları dile göre biçimlendirme
├── currency.py     # Döviz kurlarını indirme, doğrulama ve kaydetme
├── history.py      # Dönüşüm geçmişi
├── settings.py     # Dil, tema ve seçili birimler
├── i18n.py         # Türkçe ve İngilizce metinler
├── storage.py      # JSON dosyalarını kullanıcı klasörüne kaydeder
├── app_info.py     # Uygulama adı, sürüm, kaynak yolları
├── assets/         # Uygulama ikonu
├── docs/           # README görselleri
├── installer/      # Inno Setup betiği
└── tests/          # Birim testleri
```

## Kaynak Koddan Çalıştırma

Python 3.12 veya daha yenisi gerekir.

```bash
python main.py           # uygulamayı çalıştır
python -m unittest -v    # testleri çalıştır
```

### Kurulum dosyasını derleme

[PyInstaller](https://pyinstaller.org) ve [Inno Setup 6](https://jrsoftware.org/isinfo.php) gerekir.

```bash
python -m pip install pyinstaller
python -m PyInstaller --noconfirm UnitConverter.spec
ISCC installer/unit-converter.iss
```

Kurulum dosyası `installer/Output/` klasöründe oluşur.

**Yeni sürüm yayınlarken:** Sürüm numarasını hem `app_info.py` (`VERSION`) hem `installer/unit-converter.iss` (`AppVersion`) içinde güncelle, testleri çalıştır, iki derleme komutunu çalıştır ve kurulum dosyasını yeni bir GitHub Release'e yükle.

## Öğrendiklerim

- **Birim dönüştürmede ondalıklı sayılar (float) yetmiyor.** `float` ile `0.1 + 0.2` tam olarak `0.3` etmiyor. `Decimal` kullandım ve birim katsayılarını metin olarak yazdım ki kesin kalsınlar; sadece sonucu gösterirken yuvarladım.
- **Veri yapıları kodu kısaltıyor.** 58 birimin hepsi tek bir sözlükte. Menü, açılır listeler ve "tüm birimler" tablosu bu sözlükten üretiliyor; yeni birim eklemek tek satır demek.
- **Doğrusal birimler ve sıcaklık farklı problemler.** Çoğu birim sadece bir katsayıyla çevriliyor, ama sıcaklıkta bir de kayma var; bu yüzden formülle Celsius üzerinden çeviriyorum. Mutlak sıfırın altındaki değerleri de reddetmem gerekti.
- **Sayılar her dilde farklı yazılıyor.** Türkçede `1.000` bin, `1,5` bir buçuk; İngilizcede tam tersi. İki dil için kendi sayı okuyucumu ve biçimlendiricimi yazdım, biçimlendirilen metnin geri okunabildiğini test ettim.
- **API ile güvenli çalışmak.** Kurları `urllib` ile indirdim, yanıtın boyutunu ve süresini sınırladım, her alanı kullanmadan önce kontrol ettim; ağdan gelen veriye körü körüne güvenilmemeli. Kurları tarihiyle kaydetmek uygulamanın internetsiz de çalışmasını sağladı.
- **Arayüzü donmadan tutmak.** Yavaş bir indirme Tkinter penceresini dondurur. İndirmeyi arka planda bir iş parçacığında (thread) yaptım ve sonucu bir `queue` ile geri aldım, çünkü widget'lara sadece ana iş parçacığından dokunulabiliyor.
- **Küçük detaylar uygulamayı bitmiş gösteriyor.** Sonsuz güncelleme döngüsüne girmeyen iki yönlü dönüşüm, geçmişi kullanıcı yazmayı bitirince kaydetmek (debounce), son birimleri hatırlamak ve iki mesaj yerine tek net mesaj göstermek işin büyük kısmıydı.
- **Yan etkisiz test.** Testler gerçek ayarlarıma değil geçici bir klasöre yazsın diye `unittest.mock` kullandım, ağ çağrısını da sahte bir fonksiyonla değiştirdim.
- **Masaüstü uygulaması dağıtmak.** Uygulamayı PyInstaller ile paketledim, Inno Setup ile kurulum sihirbazı hazırladım ve kullanıcı verisini program klasörü yerine kullanıcı klasöründe tuttum.

## Gelecek Planları

- Favori birim çiftleri
- Basınç, enerji ve yakıt tüketimi (L/100 km ↔ mpg)
- Geçmiş döviz kuru grafikleri
- macOS ve Linux paketleri

## Lisans

[MIT](LICENSE) © 2026 Miraç Deprem
