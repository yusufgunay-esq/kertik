# İmza anahtarı ve derleme — bunu kaybetme

Bu klasör Kertik'in kalıcı imza anahtarını ve APK derleme zincirini tutar.

| Dosya | Ne işe yarar |
| --- | --- |
| `kertik-imza.p12` | Kalıcı imza anahtarı. Parola `kertik2026`, alias `kertik`, 2056'ya kadar geçerli |
| `parola.txt` | Derleme betiğinin okuduğu parola |
| `sablon.apk` | Değiştirilmeyen APK iskeleti (manifest, dex köprüsü, ikonlar) |
| `apkbuild.py` | Asıl iş: içerik değişimi + v1 imza + 4 bayt hizalama + APK İmza Şeması v2 |
| `derle.py` | Tek komutluk sarmalayıcı |

## Derleme

```
python3 derle.py
```

`../www/index.html` dosyasını `sablon.apk` içine koyar, imzalar, doğrular ve
`../Kertik.apk` olarak yazar. Başka bir çıktı adı istersen:

```
KERTIK_CIKTI=../Kertik-2.3.apk python3 derle.py
```

Doğrulama için tek bağımlılık: `pip install apksigtool`.
Android SDK, Gradle, Android Studio gerekmiyor — betik saf Python.

## Neden bu anahtar önemli

Android bir uygulamanın güncellenmesine ancak **aynı anahtarla imzalanmışsa** izin verir.
Bu dosya kaybolursa Kertik bir daha güncellenemez; herkesin uygulamayı silip baştan
kurması gerekir — yani bütün kayıtlar gider.

**Bu klasörü yedekle.** Bulut, harici disk, ne olursa.

## v2.0 → v2.2 geçişinde bir kerelik sorun

v2.0, Android'in geçici hata ayıklama anahtarıyla imzalanmıştı ve o anahtar kayıp.
v2.2 bu yeni anahtarla imzalandı; imzalar farklı olduğu için üstüne kurulum yapılamaz:

1. Kertik v2.0'ı aç → Ayarlar → Elle yedek → **dışa aktar** → metni bir yere kaydet
2. v2.0'ı **kaldır**
3. `Kertik-2.2.apk`'yı kur
4. Ayarlar → Elle yedek → **içe aktar** → metni yapıştır

Bu son kez. Bundan sonraki bütün sürümler bu anahtarla imzalanacağı için üstüne kurulur.

## Play Store'a çıkarken

Play App Signing kullanılacak; bu anahtar **yükleme anahtarı** olarak kaydedilecek.
Ama Play iki şey daha istiyor ve ikisi de bu zincirle üretilemiyor:

- **AAB** formatı (bu betik APK üretir)
- **API 36 hedefi** — şablon `targetSdk 34` üretiyor, yeni uygulamalar için
  31 Ağustos 2026'dan itibaren 36 zorunlu

İkisi de gerçek bir Gradle derlemesi gerektiriyor. Bkz. `15-yol-haritasi-v2.md`, S5.
