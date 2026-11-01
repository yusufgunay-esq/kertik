# 17 — Google Drive senkronu (S1)

`15-yol-haritasi-v2.md`'deki S1 maddesinin uygulanmış hâli. Bu dosya kararları,
gerekçeleri ve senin yapman gereken kurulumu tutar.

Durum: **kod yazıldı ve test edildi, gerçek Google'a karşı henüz denenmedi.**

**Güncelleme (17 Ağustos 2026):** Aşağıdaki "Karar 1" ve S5 madde 3, artık geçmiş
zaman. Cihaz akışı (device flow) tamamen bırakıldı; kod şu anda doğrudan **Google
Play Services Identity API'sinin `AuthorizationClient`'ı** ile çalışıyor
(`MainActivity.kt` → `googleYetkiIste()`, `Identity.getAuthorizationClient(...).authorize(...)`,
kapsam `drive.appdata`). Kullanıcı hiçbir kod yazmıyor — tek dokunuşla Google'ın
kendi hesap seçicisi açılıyor. Bunu yapabilmemizin sebebi, projenin `uygulama/`'dan
gerçek bir Gradle projesine (`kertik-android/`) geçmiş olması: artık kendi
`AndroidManifest`'imiz var, yani gömülü WebView'in OAuth engeli hiç devreye
girmiyor — akış tamamen native tarafta. `gizli.properties`'te de artık client
secret yok; kimlik paket adı + imza sertifikasının SHA-1'i üzerinden Google Cloud
Console'da eşleşiyor. Aşağıdaki tarihsel bölüm, bu karara nasıl varıldığını
gösterdiği için duruyor, ama "şu an ne oluyor" sorusunun cevabı bu paragraf.

---

## Bir cümlede

Kayıtlar kullanıcının kendi Google Drive'ında, `appDataFolder` denen ve kullanıcıya
bile görünmeyen özel alanda, tek bir `kertik.json` dosyasında durur. Bizim tarafta
sunucu yok, hesap yok, maliyet yok. "Sunucu yok" sözü bozulmadı.

---

## Karar 1 (tarihsel) — Neden cihaz akışı (device flow), neden normal giriş değil

> Bu bölüm artık geçerli değil, yukarıdaki "Güncelleme" notuna bakın. Tarihçe
> olarak duruyor: "neden önce cihaz akışı seçildi, sonra neden bırakıldı" sorusunun
> cevabı burada.

Kertik'in ilk APK'sı (v2.2 ve öncesi) WebView tabanlıydı, SDK'sız bir enjeksiyon
zinciriyle üretiliyordu ve kendi `AndroidManifest`'imiz yoktu. Google, 2016'dan beri
OAuth yetkilendirme ekranını **gömülü webview içinde açmayı engelliyor**; böyle bir
denemede kullanıcı `403: disallowed_useragent` görür. Bu bir hata değil, kasıtlı bir
güvenlik kararı: gömülü webview'de kullanıcı adres çubuğunu göremediği için kimlik
avına açık.

O zamanki kaçış yolları ve neden elendikleri:

| Yol | Neden olmaz |
| --- | --- |
| Yetkilendirmeyi WebView'de aç | Google engelliyor |
| Harici tarayıcıya çık, özel şemayla geri dön | `AndroidManifest`'e intent-filter gerek; o zamanki APK zinciri manifesti değiştiremiyor |
| Eski "kodu elle kopyala" akışı (`oob`) | Google 2022'de kapattı |
| **Cihaz akışı** | **O zaman tek çalışan yol buydu.** Tarayıcı yönlendirmesi hiç yok; uygulama bir kod gösterir, kullanıcı o kodu herhangi bir tarayıcıda girer |

Gradle projesine (`kertik-android/`) geçilince kendi manifestimiz oldu ve gerçek
native OAuth (Play Services `AuthorizationClient`) mümkün hâle geldi — cihaz akışı
o an bırakıldı. Senkron motoru (`mergeStates`, Drive katmanı, dosya biçimi) bu
geçişten hiç etkilenmedi: değişen tek şey "erişim anahtarını nereden alıyoruz"
kısmıydı.

## Karar 2 — Neden `drive.appdata`, neden Drive'ın tamamı değil

- `drive.appdata`, Google'ın sınıflandırmasında **hassas olmayan (non-sensitive)**
  kapsam. Yayın için ağır doğrulama sürecine (güvenlik değerlendirmesi, üçüncü taraf
  denetim) girmiyor, temel doğrulama yetiyor.
- Uygulama kullanıcının Drive'ındaki hiçbir dosyayı göremez. Sadece kendi yazdığı
  dosyayı görür. Kullanıcı da o klasörü Drive arayüzünde göremez.
- Kullanıcı yetkiyi Google hesap ayarlarından tek tıkla geri alabilir; uygulama
  bunu `invalid_grant`/yetki hatası olarak görür ve sessizce yerel moda düşer.

Yan etki, dürüstçe: kullanıcı yedeğini kendi gözüyle göremez, Drive'da bir dosya
olarak açamaz. Karşılığında hiçbir şeyi kirletmiyoruz. Elle yedek (dışa aktar)
duruyor; onu göremeyeceğin bir yere koymuyoruz.

## Karar 3 — Çakışma: "yalan söylemektense birleştir"

Senkron, dürüst kayıt iddiasını delebilecek ikinci yer (birincisi sayaç). Kural
basit tutuldu, çünkü karmaşık birleştirme sessizce veri uydurur.

Her seans ve görev artık `editedAt` damgası taşıyor. Her değişiklikte güncelleniyor.

| Durum | Kural |
| --- | --- |
| Kayıt yalnız bir tarafta | Alınır |
| Aynı `id` iki tarafta farklı | **Daha yeni `editedAt` kazanır** — kayıt bir bütün olarak, alan alan değil |
| Bir tarafta silinmiş | Silme bir `tombstone` (mezar taşı) bırakır; mezar taşı kaydın son düzenlemesinden yeniyse silme kazanır |
| Silindikten **sonra** öbür cihazda düzeltilmiş | **Kayıt geri gelir.** Düzeltme, silmeden yeni bir niyettir |
| Ayarlar | Bir bütün olarak son değiştiren cihazınki |
| Açık seans iki cihazda birden | **Elindeki cihaz kazanır.** Diğerinin seansı yine de kaydedilir, kaybolmaz |
| Öbür cihazda açık kalmış seans, yerelde hiç seans yok | 12 saatten yeniyse devralınır (telefon değişikliği senaryosu), daha eskiyse devralınmaz |

Mezar taşları 6 ay saklanıp temizleniyor: üçüncü bir cihaz aylar sonra bağlanırsa
silinmiş kayıtları geri diriltmesin diye.

**Alan alan birleştirme bilerek yapılmadı.** İki cihazda aynı seansın farklı
alanlarını birleştirmek, hiçbir cihazda hiç var olmamış bir kayıt üretir. Bu tam
olarak uygulamanın karşı olduğu şey.

---

## Kodda ne var (2026-08-17 itibarıyla, `kertik-android/app/src/main/assets/index.html`)

- `DEFAULTS`'a `tombstones`, `settingsEditedAt`, `sync` alanları eklendi.
- `touch(x)` ve `tomb(kind, id)` yardımcıları; bütün mutasyon noktalarına damga kondu
  (seans başlat/mola/devam/bitir/düzelt/sil, görev ekle/durum/sebep/taşı/sil).
- `mergeStates(A, B)` — saf fonksiyon, girdiyi değiştirmez, iki kez çalıştırılınca
  aynı sonucu verir. `/* MERGE:BEGIN */ … /* MERGE:END */` işaretleri arasında;
  testler bu bloğu dosyadan kesip koşuyor, yani test edilen kod ile çalışan kod
  aynı kod.
- Drive katmanı: `gAccessToken`, `driveFind`, `driveRead`, `driveWrite` (çok parçalı
  yükleme ile oluşturma, `media` ile güncelleme). Bunlar yalnız Drive REST uçlarını
  bilir; OAuth'u hiç bilmez — jetonu `nativeYetkiIste()` üzerinden Kotlin tarafından
  ister.
- `MainActivity.kt` → `googleYetkiIste(interaktif)`: `Identity.getAuthorizationClient`
  ile `drive.appdata` kapsamını ister, sonucu `window.kertikYetkiSonuc(token, hata)`
  ile sayfaya iletir. Jeton hiçbir yerde diskte tutulmaz; Play Services kendi
  yetkilendirmesini yönetir.
- `syncNow()` — indir, birleştir, yerele uygula, geri yükle. Tek adımda.
- `autoSync()` — uygulama açılınca, öne gelince, arkaya gidince, seans bitince ve
  internet geri gelince. 2 dakikadan sık denemez. **Hata olursa ekranda hiçbir şey olmaz.**
- Ayarlar → **Google yedeği** satırı; bağlanma, elle eşitleme, bağlantıyı kesme.
- Ayarlar → **Elle yedek** (eski dışa/içe aktarma, aynen duruyor).

Drive'a giden pakete (`snapshot()`) **jeton/yenileme anahtarı konmuyor** — zaten
sayfa tarafında hiç tutulmuyor, Play Services'in kendi güvenli deposunda duruyor.

Ayarlar ekranındaki eski cümle ("Kertik hiçbir veriyi hiçbir yere göndermez")
artık koşullu: *"Google yedeğini açmadıkça hiçbir veri hiçbir yere gitmez."*
Doğru olmayan bir söz ekranda durmasın.

## Doğrulama

Birleştirme mantığı — 22 birim testi, hepsi geçti:
ayrı seansların birleşmesi, aynı id'de yeni olanın kazanması, boş tarafın veri
silmemesi, silinen kaydın geri dirilmemesi, silmeden sonra düzeltilen kaydın geri
gelmesi, eski mezar taşlarının temizlenmesi, iki cihazda açık seans, 40 saatlik
unutulmuş seansın devralınmaması, ayar çakışması, saflık, sıralama, idempotanlık,
`editedAt`'i olmayan v2.0 verisinin kaybolmaması.

Uçtan uca — sahte bir Google sunucusu kurulup tam akış koşuldu, 14 test geçti:
yetki isteği → onay → jetonun alınması → ilk yükleme → **ikinci boş cihazın aynı
hesapla bağlanıp bütün kayıtları indirmesi** → ikinci cihazda silme → birinci
cihazda geri dirilmemesi → yeni seansın karşı tarafa geçmesi → yetki iptalinde
sessizce yerel moda düşme ve verinin durması.

**Gerçek Google sunucusuna karşı test hâlâ yapılamadı** — bu geliştirme ortamından
(bulut kabı) Google API'lerine ağ erişimi kapalı. Yani `driveFind`/`driveRead`/
`driveWrite`'ın gerçek Drive REST uçlarına karşı ilk denemesi, Android Studio'da,
senin bilgisayarında olacak.

---

## Google Cloud kurulumu

**Durum (16-17 Ağustos 2026):** `kertik` projesi açık, **Android türünde istemci**
oluşturuldu (paket adı `com.yusufgunay.kertik` + imza SHA-1). Kullanıcının
uygulamaya hiçbir şey yapıştırması gerekmiyor: Ayarlar → Google yedeği →
**bağlan**, o kadar — Google'ın kendi hesap seçicisi açılır, tek dokunuş.

`gizli.properties`'te artık Google için client id/secret **yok** (bkz.
`gizli.properties.ornek`). Android istemcilerin zaten client secret'ı olmuyor;
kimlik doğrudan Cloud Console'daki paket adı + SHA-1 eşleşmesinden geliyor. Yani
"depoya sır sızması" riski bu adımda kendiliğinden ortadan kalktı.

Aşağıdaki adımlar kaydı tutmak ve gerekirse yeniden kurmak için. Konsolun adı
2025'te değişti, artık **Google Auth Platform**; menü adları biraz oynamış olabilir.

### 1. Proje aç
[console.cloud.google.com](https://console.cloud.google.com) → üstteki proje
seçicisi → **Yeni proje** → ad: `Kertik`. Faturalandırma gerekmiyor.

### 2. Drive API'yi aç
Sol menü → **API'ler ve Hizmetler → Kitaplık** → "Google Drive API" ara → **Etkinleştir**.

### 3. Kimlik doğrulama ekranını kur
Sol menü → **Google Auth Platform**.

- **Branding (Marka)**: uygulama adı `Kertik`, destek e-postası senin adresin.
  Buraya yazdığın ad, kullanıcının onay ekranında göreceği addır.
- **Audience (Hedef kitle)**: **External (Harici)**. Google Workspace hesabın
  olmadığı için tek seçenek zaten bu.
- **Data Access (Veri erişimi)** → **Kapsam ekle** → şunu ara ve ekle:
  ```
  https://www.googleapis.com/auth/drive.appdata
  ```
  Başka hiçbir kapsam ekleme. Bir tane fazla kapsam, doğrulama sürecini ağırlaştırır.

### 4. İstemci oluştur
**Clients (İstemciler)** → **İstemci oluştur** → uygulama türü: **Android**.

Sorulacaklar: paket adı (`com.yusufgunay.kertik`) ve imza sertifikasının SHA-1'i:

Yerel Yükleme İmzası (.p12):
SHA-1   : F4:29:B5:B5:9B:75:91:B3:15:C5:B3:D8:34:8C:9E:4B:13:C5:45:DB
SHA-256 : E3:B6:C1:4C:87:46:EE:0F:5F:6F:86:12:23:29:BA:9C:40:EF:7C:27:E3:97:3F:97:ED:03:4C:5A:99:F9:96:69

Google Play App Signing (Asıl Mağaza / Kapalı Test Dağıtımı):
SHA-1   : 19:8E:EC:81:51:F4:AC:34:BF:3A:96:0A:47:C5:F2:80:BD:95:31:A8

Google Play App Signing (Kuantum Uyumlu Yeni Anahtar):
SHA-1   : 48:44:DD:DE:B9:BD:AD:F1:E0:8A:8B:41:D2:C8:36:39:EF:E3:D1:A5

> Play App Signing devrede olduğu için mağazadan inen sürüm bu SHA-1 ile imzalanır.
> Google Cloud Console'da her üç SHA-1 de ayrı birer Android istemcisi olarak
> kayıtlı olmalıdır (biri yerel geliştirme için, biri asıl mağaza dağıtımı için, biri yeni anahtar için).

### 5. Yayın durumunu "Üretim"e al
**Audience** ekranında uygulama muhtemelen **Testing (Test)** durumundadır.
Bunu **Publish app / Üretime al** ile değiştir.

> **Bu adım atlanmazsa emin olunması gereken şey:** Android istemcilerde jeton
> ömrü, cihaz akışındaki gibi "7 günde bir kopan yenileme anahtarı" mantığına tabi
> değil — Play Services yetkilendirmeyi kendi yönetiyor. Yine de doğrulama
> aşamasını Test'te bırakmamak, kullanıcı sayısı arttığında Google'ın "doğrulanmamış
> uygulama" uyarısını göstermesini engeller. `drive.appdata` hassas olmayan bir
> kapsam olduğu için üretime almak ağır inceleme gerektirmez.

### 6. Uygulamaya gir
Kertik → Ayarlar → **Google yedeği** → **bağlan**. Google'ın hesap seçicisi açılır,
hesabı seç, onayla. Kod yazmak yok.

---

## Takılırsan: hata mesajlarının anlamı

Hata ekranında altta tek satırlık teşhis var. Anlamları:

| Ekranda gördüğün | Gerçek sebep | Ne yapmalı |
| --- | --- | --- |
| `ApiException` / "12500" veya "10" (DEVELOPER_ERROR) | Cloud Console'daki paket adı+SHA-1 eşleşmiyor, ya da istemci "Android" türünde değil | Paket adını ve **imzalayan** anahtarın SHA-1'ini kontrol et — yerel `.p12` ile derliyorsan onun SHA-1'i, Play App Signing ile derliyorsan Play'in verdiği SHA-1 |
| "12501" (SIGN_IN_CANCELLED) | Kullanıcı hesap seçiciyi kapattı | Yeniden dene |
| Yetki isteği sessizce başarısız (arka planda, `interaktif=false`) | Beklenen davranış — önceden izin yoksa arka planda hiç soru sormadan başarısız olur | Kullanıcı "bağlan"a basınca `interaktif=true` ile tekrar denenir |
| "Google'a ulaşılamadı" (Drive REST çağrısında) | Ağ yok, ya da Drive API projede etkin değil | İnterneti kontrol et, 2. adımı doğrula |

---

## Play Store'a çıkarken (S5) kalan maddeler

1. ~~Client secret derlenmiş APK'nın içinde olacak~~ — **artık geçersiz.** Android
   istemcilerde secret yok, bu risk kendiliğinden ortadan kalktı.
2. ~~Yayın durumu Üretim olmak zorunda, yoksa 7 günde bir kopar~~ — **artık geçersiz.**
   O risk cihaz akışına özgüydü. Yine de "Üretim"e almak doğrulanmamış uygulama
   uyarısını önler (yukarıdaki 5. adım).
3. ~~Cihaz akışı bırakılacak~~ — **yapıldı.**
4. **Play "Veri güvenliği" formu:** veri bizim sunucumuza gitmediği için
   "toplanmıyor" doğru; ama kullanıcının kendi Drive'ına yedeklendiğini ve
   şifrelenmiş bağlantı kullanıldığını yazmak gerekir. Formda yalan söylememek
   uygulamanın bütün karakterinin bir parçası.
5. **Gizlilik politikası** artık "hiçbir veri toplanmıyor" diyemez, şunu demeli:
   *"Kertik hiçbir veri toplamaz. Google yedeğini açarsan kayıtların doğrudan
   senin Google Drive'ına gider; biz göremeyiz, saklamayız."*
6. **Play App Signing SHA-1'i de Cloud Console'a Android istemcisi olarak
   eklenmeli** (bkz. yukarıda 4. adımın notu) — yoksa mağaza sürümünde senkron
   sessizce çalışmaz.

---

## Bilinen riskler ve açık uçlar

- **Gerçek Google'a karşı hiç denenmedi.** Aşağıdaki maddeler teorik; ilk gerçek
  denemede biri çıkabilir. Android Studio'da ilk "bağlan" denemesi bunu netleştirir.
- **Gelişmiş Koruma (Advanced Protection) açık hesaplar** üçüncü taraf OAuth'a izin
  vermeyebilir. Uygulama bu durumda hata ekranı göstermeden yerel moda düşüyor.
- **Aynı anda iki cihazda açık seans** teknik olarak destekleniyor ama insanî olarak
  anlamsız. Şu an sessizce elindeki cihazı kazandırıyoruz. İleride "başka cihazda
  açık bir seans var" satırı gösterilebilir.
- **12 saatten eski, bitmemiş, devralınmayan seans** hiçbir ekranda görünmez
  (kayıt listesi yalnız bitmiş seansları gösterir). Veri kaybolmuyor ama görünmüyor.
  S6'ya madde: "yarım kalmış seansları göster ve sor".
- **Kota.** Drive API'nin ücretsiz kotası bu kullanım için fazlasıyla yeterli;
  eşitleme 2 dakikada birden sık denenmiyor.

---

## Sıradaki

1. **Android Studio'da ilk gerçek deneme.** `kertik-android`'i aç, Run, Ayarlar →
   Google yedeği → bağlan. Burada çıkacak ilk hata (varsa) yukarıdaki tabloya göre
   teşhis edilir.
2. S2 — Google Tasks köprüsü. Kural `15-yol-haritasi-v2.md`'de yazılı ve değişmedi:
   **önce tek yön (Tasks → Kertik)**, `completed` yalnız gerçekten bittiğinde yazılır,
   temsil edilemeyen durumlar `notes`'a serbest metin olarak düşülür.

   Not: Tasks kapsamı (`.../auth/tasks`) artık native `AuthorizationClient` ile
   istenebilir — cihaz akışının kapsam kısıtı bu geçişle birlikte ortadan kalktı.
   S2'yi S4'ün önüne almış olan gerekçe artık geçersiz; S2 istenirse şimdi
   yapılabilir.
