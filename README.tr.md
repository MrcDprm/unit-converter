# Birim Dönüştürücü (Unit Converter)

[English](README.md) | **Türkçe**

Python ve Tkinter ile yazılmış bir masaüstü birim dönüştürücü: güncel döviz kurları, Türk mutfak ölçüleri ve GB ile GiB farkı dahil dokuz kategori.

> 🚧 Geliştiriliyor. Bu README şimdilik proje planı; v1.0.0'da tamamlanacak.

## Plan

### MVP
- **Kategoriler:** uzunluk, ağırlık, sıcaklık, hacim, alan, hız, zaman, veri boyutu ve döviz.
- **Gerçek dünya dokunuşları:**
  - Hacimde Türk mutfak ölçüleri (su bardağı, çay bardağı, yemek kaşığı, tatlı kaşığı, çay kaşığı), yanında ABD ölçüleri (cup, fl oz).
  - Veri boyutunda 10'luk (GB) ve 2'lik (GiB) birimler yan yana; 1 TB diskin neden 931 GB göründüğünü gösterir.
- **Döviz:** Ücretsiz ve anahtarsız ExchangeRate-API'den 166 para birimi. Kurlar tarihiyle birlikte kaydedilir; internet yoksa son kurlarla çalışmaya devam eder ve kurların ne kadar eski olduğunu söyler.
- **İki yönlü, canlı dönüşüm:** Hangi kutuya yazarsan diğeri güncellenir; ⇄ düğmesi birimlerin yerini değiştirir.
- **Tüm birimler tek bakışta:** Değerin kategorideki bütün birimlerdeki karşılığını gösteren tablo; satıra tıklayınca kopyalanır.
- **Geçmiş:** Son 50 dönüşüm; tıklayınca yeniden açılır, tek düğmeyle temizlenir.
- **Doğruluk:** Hesaplar `Decimal` ile yapılır, mutlak sıfırın altındaki sıcaklık reddedilir, çok büyük ve küçük sayılar bilimsel gösterimle yazılır, Türkçe ondalık virgül (`3,5`) kabul edilir.
- **Kullanım:** Kopyala düğmesi ve Ctrl+C, hatırlanan kategori ve birimler, koyu ve açık tema, klavye kısayolları, Türkçe ve İngilizce.
- **Masaüstü uygulaması:** İkon, sürüm, Hakkında penceresi, kullanıcı klasörüne kaydedilen ayarlar, Windows kurulum dosyası (PyInstaller + Inno Setup).
- **Testler:** Bütün dönüşümler, gidiş-dönüş (A → B → A), sıcaklığın kenar durumları, kur önbelleği ve geçmiş.

### Gelecek Planları
- Favori birim çiftleri.
- Basınç, enerji ve yakıt tüketimi (L/100 km ↔ mpg).
- Geçmiş döviz kuru grafikleri.

## Kullanılan Teknolojiler
- Python 3, Tkinter
- Kesin hesap için `decimal`
- [ExchangeRate-API](https://www.exchangerate-api.com) açık erişim (ücretsiz, API anahtarı gerekmez)
- `unittest`
- PyInstaller, Inno Setup
