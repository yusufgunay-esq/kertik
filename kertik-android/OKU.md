# Kertik — Android projesi

Gerçek bir Gradle projesi. Buradan itibaren **uygulamanın kaynağı burası**:
`app/src/main/assets/index.html`. Eski `uygulama/` klasörü 2.2'de donduruldu,
yalnız tarihçe olarak duruyor.

| Neresi | Ne |
| --- | --- |
| `app/src/main/assets/index.html` | Uygulamanın tamamı — arayüz, sayaç mantığı, görevler, Drive senkronu |
| `app/src/main/java/.../MainActivity.kt` | WebView kabuğu, native köprü, bildirim tuşlarının yönlendirilmesi |
| `app/src/main/java/.../Bildirim.kt` | Bildirim çubuğundaki canlı sayaç |
| `test/` | Sayfa tarafının testleri — Kotlin'e dokunmadan koşar |
| `.github/workflows/derle.yml` | Testleri koşar, APK + AAB üretir, imzalar |

## Neden Gradle'a geçildi

Üç sebep, üçü de teknik:

1. **Play Store 31 Ağustos 2026'dan itibaren yeni uygulamalarda API 36 istiyor.**
   Eski derleme zinciri (hazır APK şablonuna varlık enjeksiyonu) 34 üretiyordu ve
   yükseltilemiyordu.
2. **AAB** üretmek gerekiyor; eski zincir yalnız APK üretebiliyordu.
3. **Bildirim çubuğundaki canlı sayaç** native kod istiyor.

Arayüz bilerek Compose'a çevrilmedi. Çalışan, test edilmiş bir arayüzü atıp baştan
yazmak, kazanılmış her şeyi yeniden riske atmak olurdu. Compose'a geçiş, geçilecekse,
ekran ekran ve sonra.

## Derleme

Derlemenin GitHub'la bir ilgisi yok; **asıl yol Android Studio.**
Aşağıdaki GitHub Actions bölümü isteğe bağlı, istemezsen hiç dokunma.

### Android Studio (asıl yol)
`kertik-android` klasörünü aç, Gradle senkronunu bekle, Run.

İmzalı sürüm ve Google senkronu için `gizli.properties.ornek` dosyasını
**`gizli.properties`** adıyla kopyalayıp doldur. O dosya `.gitignore`'da; depoya girmez.
Derleme başlarken tek satır söyler: `Kertik: imza=var, google=var`.

### Komut satırı
```
./gradlew assembleRelease        # APK
./gradlew bundleRelease          # AAB (Play için)
```

### GitHub Actions (isteğe bağlı)
Gerekmiyor. İşe yaradığı iki durum var: kodun bilgisayarın dışında da yedeklenmesi,
ve derlemenin senin makinene kurulum yapmadan yapılabilmesi. **Private depo, kod
kimseye açılmaz** — GitHub yayınlamak değil, sürüm tutmak demek.

Kullanmak istersen: depoyu private aç ve it. Her `main` itişinde testler koşar,
imzalı APK + AAB üretilir. Önce dört sır tanımlanmalı — **Settings → Secrets and variables → Actions**:

| Sır | Değer |
| --- | --- |
| `KERTIK_KEYSTORE_B64` | `kertik-imza.p12` dosyasının base64'ü |
| `KERTIK_STORE_PASSWORD` | `kertik2026` |
| `KERTIK_GOOGLE_CLIENT_ID` | Google Cloud'daki client ID |
| `KERTIK_GOOGLE_CLIENT_SECRET` | Google Cloud'daki client secret |

Base64'ü üretmek için:

```
# Windows PowerShell
[Convert]::ToBase64String([IO.File]::ReadAllBytes("kertik-imza.p12")) > imza.b64
# macOS / Linux
base64 -w0 kertik-imza.p12 > imza.b64
```

Sırlar tanımlı değilse iş yine çalışır: imzasız çıktı üretir, Google senkronu kapalı
çıkar ve uyarır. Uygulamanın geri kalanı ikisi olmadan da tam çalışır.

### Sırlar neden kaynak dosyalarda değil

Google anahtarı bir süre `index.html` içinde gömülüydü, oradan alındı. Sebebi sadece
GitHub değil: anahtarın kaynak dosyada durması, dosyayı paylaştığın her yerde
(yedek, ekran görüntüsü, birine gönderme) anahtarı da paylaşman demek. Şimdi anahtar
tek bir yerel dosyada — `gizli.properties` — ve derlenmiş uygulamanın içinde.

## Testler

Kotlin tarafı bu ortamda derlenemiyor; sayfa tarafı ise tamamen test edilebiliyor.

**Kural: `index.html` her değiştiğinde, commit'ten önce `node test/hepsi.js` koşar.**
CI de aynı şeyi koşar ve testler geçmeden APK/AAB üretmez.

```
cd test
npm install playwright jsdom && npx playwright install chromium

node hepsi.js               # hepsi — sahte Google'ı kendi açıp kapatır
node hepsi.js --hizli       # tarayıcısız olanlar (~2 sn, yazarken bunu koş)
node hepsi.js duman         # tek dosya
```

| Dosya | Ne | Kaç |
|---|---|---|
| `test-duman.js` | **Duman testi.** Açılıyor mu, konsol temiz mi, başlat→mola→devam→bitir yürüyor mu, kayıt yeniden açılışta duruyor mu | 22 |
| `test-birlestirme.js` | Senkron çakışma kuralları | 22 |
| `test-cizim.js` | Çubuk, duvar, akış alanı geometrisi | 51 |
| `test-native-kopru.js` | Bildirim köprüsü sözleşmesi | 23 |
| `test-arayuz.js` | Anahtarın nereden geldiği, hata ekranı | 20 |
| `test-uctan-uca.js` | İki cihaz arası senkron (sahte Google'a karşı) | 14 |

Yeni test dosyası eklerken `hepsi.js` içindeki `TESTLER` listesine bir satır ekle;
CI'a dokunmak gerekmiyor, workflow zaten `hepsi.js` çağırıyor.

`test-duman.js` diğerlerinden farklı: kural doğrulamıyor, **sayfanın ayakta olduğunu**
doğruluyor. Tek özelliği var — konsola düşen her hata bu testi kırar. Diğer dosyalar
`pageerror`'ı sadece ekrana basar, orada bir istisna fırlasa bile yeşil kalabilirler.

`test-native-kopru.js` özellikle önemli: Kotlin tarafının uymak zorunda olduğu arayüzü
(`goster / gizle / bildirimIzniVar / bildirimIzniIste / ekraniAcikTut / googleAnahtar`)
sahte bir nesneyle taklit edip sayfanın doğru çağrıları yaptığını doğruluyor.
Kotlin imzalarını değiştirirsen o testi de değiştir.

## Bildirim neden foreground service değil

Android'in kronometreli bildirimi saati kendisi işletiyor, biz saniyede bir uyanıp
bildirimi yenilemiyoruz. Bunun üç faydası var: pil tüketimi yok denecek kadar az,
Android 14'ün "foreground service türü" beyanı ve onun Play gerekçesi gerekmiyor,
uygulama öldürülse bile bildirim doğru saymaya devam ediyor.

Bedeli: bildirimdeki Mola/Devam/Bitir tuşları uygulamayı bir an öne getirir, işini
yapar ve kendini geri çeker. Tam yerinde çalışması için foreground service şart olur;
o karar birkaç haftalık gerçek kullanımdan sonra verilecek.

## Veri

Hiçbir şey değişmedi. Kayıtlar hâlâ WebView'in `localStorage`'ında, sayaç hâlâ
saymıyor — olay damgalarından hesaplıyor. Bildirim yalnızca bir gösterge; orada
hiçbir süre tutulmuyor, saklanmıyor.

Paket adı (`com.yusufgunay.kertik`) ve imza anahtarı v2.2 ile aynı. Yani bu sürüm
**2.2'nin üstüne kurulur, kayıtlar durur.**
