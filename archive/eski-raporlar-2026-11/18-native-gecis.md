# 18 — Gradle'a geçiş (S4'ün birinci yarısı)

`15-yol-haritasi-v2.md`'de S4 "native sürüm (Kotlin)" diye tek madde yazıyordu.
Uygulanırken ikiye bölündü, ve bölünme yeri önemli:

| | Ne | Durum |
| --- | --- | --- |
| **S4a** | Gerçek bir Gradle projesi + bildirim çubuğunda canlı sayaç | **bu dosya, yapıldı** |
| S4b | Arayüzün Compose'a taşınması, DND, widget | sonra, ve belki hiç |

Ayrım şu soruya dayanıyor: *Play'e çıkmak için arayüzü yeniden yazmak şart mı?*
Değil. Şart olan şey **gerçek bir Gradle derlemesi**. Bunlar iki ayrı eksen ve
karıştırılırsa iki aylık iş bir haftalık işin önüne konmuş olur.

---

## Neden şart oldu

1. **31 Ağustos 2026.** Play, o tarihten sonra yeni uygulamalarda API 36 hedefi
   istiyor. Eski derleme zinciri — hazır bir APK şablonuna `index.html` enjekte edip
   elle imzalamak — `targetSdk 34` üretiyordu ve yükseltilemiyordu, çünkü manifesti
   değiştirmek için Android SDK gerekiyor.
2. **AAB.** Play yeni uygulamalardan AAB istiyor; eski zincir yalnız APK üretebiliyordu.
3. **Bildirim çubuğunda canlı sayaç.** Bunun için native kod şart.

Üçü de "arayüzü Compose'a çevir" demiyor. Üçü de "gerçek bir derleme kur" diyor.

## Ne yapıldı

`kertik-android/` diye gerçek bir Gradle projesi. Uygulamanın tamamı hâlâ tek bir
`app/src/main/assets/index.html`; onu saran şey değişti.

- `compileSdk / targetSdk 36`, `minSdk 24`, `versionCode 30`, `versionName 3.0`
- `applicationId` ve imza anahtarı v2.2 ile **aynı** → bu sürüm 2.2'nin üstüne kurulur,
  kayıtlar durur. (2.0 → 2.2 geçişindeki gibi bir silme gerekmiyor.)
- Sayfa `https://appassets.androidplatform.net/` kaynağından servis ediliyor,
  yani Drive senkronunun dayandığı gerçek https kaynağı korundu.
- Dış bağlantılar (ör. `google.com/device`) artık **sistem tarayıcısında** açılıyor.
  Eskiden hiçbir yerde açılmıyordu; senkrona bağlanmak bu kadar kolaylaştı.
- İki izin: `INTERNET` ve `POST_NOTIFICATIONS`. Başka yok.
- Karanlık modda açılışta beyaz parlama olmasın diye `values-night` teması eklendi.

### Bildirim çubuğundaki canlı sayaç

Çalışan bir seans varken bildirim çubuğunda kronometre duruyor; kilit ekranından
da görünüyor. Üstünde iki tuş: **Mola / Devam et** ve **Bitir**.

Pomodoro modunda geri sayıyor; hedef dolunca kesmiyor, yukarı saymaya dönüyor ve
başlık "hedef doldu, sayaç sürüyor" oluyor. Dürüst kayıt ilkesi bildirimde de aynı.

**Foreground service bilerek kullanılmadı.** Android'in kronometreli bildirimi saati
kendisi işletiyor; saniyede bir uyanıp bildirimi yenilemiyoruz. Faydası üç tane:

- pil tüketimi yok denecek kadar az,
- Android 14'ün "foreground service türü" beyanı ve onun Play gerekçesi gerekmiyor
  (bu uygulama için uygun tek tür `specialUse` olurdu ve o, inceleme sırasında
  açıklama yazmayı gerektiriyor),
- uygulama öldürülse bile bildirim kalıyor ve doğru saymaya devam ediyor — çünkü
  gösterdiği şey bir sayaç değil, bir zaman damgası.

Bedeli dürüstçe: bildirimdeki tuşlar uygulamayı bir an öne getirir, işini yapar ve
kendini geri çeker (`moveTaskToBack`). Tam yerinde çalışması için foreground service
şart olur. O karar birkaç haftalık gerçek kullanımdan sonra verilecek — bu, `13-bulgular.md`
dosyasına yazılacak ilk somut soru.

### Bildirim veri tutmuyor

Bu, projenin en kolay bozulacak yeri olduğu için ayrıca yazılıyor: bildirim bir
**gösterge**. Kotlin tarafında hiçbir süre tutulmuyor, sayılmıyor, saklanmıyor.
Tuşlara basıldığında olan tek şey, sayfadaki `takeBreak()` / `resume()` / `finish()`
fonksiyonlarının çağrılması — yani uygulamanın normal akışı. İkinci bir doğruluk
kaynağı yok, olursa da uygulamanın var olma sebebi gider.

## Sırlar depodan çıkarıldı

Proje GitHub'a çıkacağı için Google istemci anahtarı `index.html`'den alındı.
Depoya giren bir sır git geçmişinden bir daha çıkmaz; sonradan silmek işe yaramaz.

Yeni düzen:

| Sır | Yerel derleme | GitHub Actions |
| --- | --- | --- |
| İmza anahtarı yolu ve parolası | `gizli.properties` | `KERTIK_KEYSTORE_B64`, `KERTIK_STORE_PASSWORD` |
| Google client ID / secret | `gizli.properties` | `KERTIK_GOOGLE_CLIENT_ID`, `KERTIK_GOOGLE_CLIENT_SECRET` |

`gizli.properties` `.gitignore`'da. Değerler `BuildConfig`'e gömülüyor, oradan
`KertikNative.googleAnahtar()` köprüsüyle sayfaya geçiyor. Hiçbiri tanımlı değilse
uygulama tam çalışır — sadece imzasız çıkar ve senkron kapalı olur. Derleme başında
tek satır söylüyor: `Kertik: imza=var, google=YOK`.

Kaynak dosyalarda artık hiçbir sır yok; depo private açılsa bile bu böyle kalmalı.

## Doğrulama

Kotlin tarafı **bu ortamda derlenemiyor**: çıkış filtresi `dl.google.com` (Android SDK),
`maven.google.com` (AndroidX) ve `repo1.maven.org` (Maven Central) adreslerini kapatıyor.
Yani 294 satırlık Kotlin kodu derlenmemiş hâlde teslim ediliyor. Bunu telafi etmek için:

- **Kotlin kasten küçük ve sıradan tutuldu.** İki dosya, alışılmış kalıplar, iki bağımlılık.
- **Köprünün sözleşmesi test edildi.** `test/test-native-kopru.js`, Kotlin'in sunduğu
  arayüzü birebir taklit eden sahte bir nesne enjekte edip sayfanın doğru çağrıları
  yaptığını doğruluyor — 23 test. Kotlin tarafı bu imzalara uymak zorunda; değişirse
  test de değişmeli.
- **Derleme CI'da yapılıyor.** `.github/workflows/derle.yml` önce testleri koşuyor,
  sonra imzalı APK + AAB üretiyor. İlk çalıştırmada sürüm uyuşmazlığı çıkarsa
  düzeltilecek yer `build.gradle.kts`'in en üstü.

Toplam sayfa testi: **79** (22 birleştirme + 20 arayüz + 23 native köprü + 14 uçtan uca),
hepsi geçiyor. Arayüz testleri artık anahtarın üç kaynağını da kapsıyor: kullanıcının
girdiği, derlemede gömülen, ve hiç olmayan.

> Dürüst beklenti: ilk CI koşusunun bir sürüm numarasında takılma ihtimali gerçek.
> AGP 8.11.1 / Kotlin 2.1.21 / Gradle 8.14.3 seçildi. Takılırsa hata kaydını
> göndermek yeterli; düzeltmesi tek satır.

## Sıradaki adımlar

1. **Android Studio'yu kur, projeyi aç, Build.** `gizli.properties` hazır; imza ve
   Google anahtarı oradan geliyor. GitHub gerekmiyor — CI dosyası duruyor ama isteğe bağlı.
2. Çıkan APK'yı telefona kur — 2.2'nin üstüne kurulur, kayıtlar durur.
3. Drive senkronunu **gerçek Google'a karşı** ilk kez dene. Artık `google.com/device`
   bağlantısı tarayıcıda açılıyor, akış çok daha rahat.
4. Bildirimi birkaç hafta kullan; "tuşlar uygulamayı öne getiriyor" gerçekten rahatsız
   ediyor mu, `13-bulgular.md`'ye yaz.
5. **Cihaz akışını bırak, normal OAuth'a geç.** Artık `AndroidManifest` bizim olduğu
   için Android türünde bir OAuth istemcisi açılabilir; Android istemcilerin client
   secret'ı yoktur, kimlik paket adı + imza SHA-1'idir. Yani gömülecek sır hiç kalmaz
   ve kullanıcı kod yazmaz. Gereken değerler `17-google-senkron.md`'de hazır.
   Bunu CI yeşile döndükten **sonra** yap: derlenmemiş OAuth kodunu derlenmemiş WebView
   kodunun üstüne koymak iki bilinmeyen eder.
6. Play Console hesabı ve AAB yüklemesi — `16-para-kazanma.md`.

## Bundan sonra ne değişti (çalışma düzeni)

Uygulamanın kaynağı artık `kertik-android/app/src/main/assets/index.html`.
Eski `uygulama/` klasörü 2.2'de donduruldu; içindeki elle imzalama zinciri
(`imza/apkbuild.py`) çalışmaya devam ediyor ama artık yedek yol.

## Değişmeyenler

- Sayaç saymıyor, olay damgalarından hesaplıyor.
- Seans sırasında kullanıcıya soru sorulmuyor.
- Seri, rozet, sosyal, reklam, zorunlu hesap, motivasyon bildirimi yok.
- Bildirim kanalı sessiz: ses yok, titreşim yok, rozet yok.
