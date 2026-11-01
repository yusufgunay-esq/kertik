# 36 — Tam native (Compose) geçişi: iddiaların incelenmesi ve karar kuralı

28 Ağustos 2026. `23-masaustu-ve-native-karar.md` Bölüm A'da "arayüz web kalıyor,
bu şimdilik değil mimari karar" yazıyordu. O karar iki yeni iddiayla yeniden açıldı.
Bu dosya iddiaları tek tek inceliyor, native'in gerçek kazançlarını olduğu gibi
yazıyor, maliyeti tahminle değil ölçümle veriyor ve sonunda tahmine değil ölçüme
dayanan bir karar kuralı öneriyor.

Kısa sonuç: **iddialardan biri yanlış, ama içinde ölçülebilir ve ciddi bir doğru
çekirdek var.** Kararı o çekirdeği ölçtükten sonra vermeliyiz — ki ölçmek yayına
çıkmayı gerektiriyor, geciktirmeyi değil.

---

## İddia 1 — "Native yapmazsak Play neredeyse yasaklıyor, öne çıkarmıyor"

Bu, yürürlükteki hâliyle **yanlış.** Google'ın konuyla ilgili politikalarının hiçbirinde
"WebView" kelimesi geçmiyor.

### Politika gerçekte ne diyor

İlgili politika "Spam ve Asgari İşlevsellik" başlığı altında ve iki maddesi var:

| Madde | Yasaklanan | Google'ın verdiği örnekler |
|---|---|---|
| **Bozuk işlevsellik** | "Çöken, kapanmaya zorlanan, donan veya anormal çalışan uygulamalar" | Kurulmayan, kurulup açılmayan, açılıp tepki vermeyen |
| **Sınırlı işlevsellik ve içerik** | "Yalnızca sınırlı işlevselliğe ve içeriğe sahip uygulamalar" | Yalnız metin veya yalnız PDF gösteren uygulamalar, tek duvar kâğıdı uygulamaları, hiçbir iş yapmayan uygulamalar |

Ağustos 2024'te yürürlüğe giren ve basına "Play düşük kaliteli uygulamaları siliyor"
diye yansıyan güncelleme de bu maddenin genişletilmesiydi. Hedef Google'ın kendi
ifadesiyle *"kararsız, tepkisiz veya gerçek bir değer sunmayan"* uygulamalar.

**Reddedilen WebView uygulamalarının ortak özelliği render motoru değil, boşluk:**
bir URL açıp bırakan, başkasının sitesini izinsiz saran, dinamik hiçbir özelliği
olmayan, mobil tarayıcıda o siteyi açmaktan fazlasını sunmayan uygulamalar.

### Kertik bunların hangisi?

Hiçbiri — ve bu tesadüf değil, `18-native-gecis.md`'de verilen kararların sonucu:

- **Açtığı bir URL yok.** Sayfa `https://appassets.androidplatform.net/` üzerinden
  **paketin içinden** servis ediliyor. İnternet olmadan tam çalışıyor.
- **Sardığı bir site yok.** Kertik'in bir web sitesi yok; "sarmalanan içerik" diye
  bir şey mevcut değil. HTML burada bir kaynak değil, bir çizim ortamı.
- **Native işlevleri var:** bildirim çubuğunda canlı sayaç (kilit ekranından görünür,
  Mola/Bitir tuşlarıyla), ana ekran widget'ı, sistem karanlık moduna uyum, dış
  bağlantıların sistem tarayıcısında açılması.
- **Kendi içeriğini üretiyor:** kadran, ebru akışı, kum bahçesi, iki duvar, kayıt
  detayı, 15 dilli arayüz, Drive senkronu. Bunların hiçbiri "bir siteyi göstermek" değil.

Yani politika açısından Kertik bir WebView uygulaması olarak değil, **çizimini
kendi yapan çevrimdışı bir uygulama** olarak duruyor. Reddedilme gerekçesi
oluşturacak bir madde yok.

### Sıralama / öne çıkarma cezası var mı?

Play'in bir uygulamanın içinde WebView olduğunu tespit edip sıralamada aşağı çektiğine
dair **belgelenmiş bir mekanizma yok.** Play'in ölçtüğü şey ekranın nasıl çizildiği
değil. Ölçtüğü şeyler: teknik sağlık (Android vitals), kurulum/kaldırma oranı, puanlar,
kullanım sürekliliği.

**Ama işte iddianın doğru çekirdeği burada.**

---

## İddianın doğru çekirdeği — Android vitals (bu kısım ciddi)

Play'in gerçekten uyguladığı ve sayıları açıkça yazılı bir cezalandırma sistemi var:

| Ölçüt | "Kötü davranış" eşiği |
|---|---|
| Kullanıcı algılı **çökme** oranı | Günlük kullanıcıların **≥ %1,09**'u (tek cihaz modelinde %8) |
| Kullanıcı algılı **ANR** (yanıt vermiyor) oranı | Günlük etkin kullanıcıların **≥ %0,47**'si (tek cihaz modelinde %8) |

Eşiği aşan uygulama için Google'ın kendi ifadesiyle sonuç:

> "Play'de daha az keşfedilebilir olması muhtemeldir" — ve bazı durumlarda "mağaza
> sayfasında kullanıcı beklentisini ayarlamak ve alternatif arama seçeneği sunmak
> için bir uyarı gösterilebilir."

Ayrıca belirli cihaz modellerinde sorun görülürse Play "o cihazlardaki kullanıcıları
bu uygulamalardan uzaklaştırıp daha uygun olanlara yönlendiriyor."

**Bu, iddiayı doğru biçimde yeniden ifade etmemizi sağlıyor.** Doğru cümle şu değil:

> ~~"WebView olduğu için Play bizi cezalandırır."~~

Doğru cümle şu:

> **"WebView, ucuz telefonlarda ANR eşiğini aştırırsa Play bizi cezalandırır."**

Fark hayati, çünkü ikinci cümle **ölçülebilir bir iddia.** Birincisi bir korku;
ikincisi Play Console'da iki sayıya bakarak cevaplanır. Ve bu risk Kertik için
tamamen hayali de değil: ebru ve kum bahçesi her karede canvas boyuyor, ucuz
cihazda ana iş parçacığını tıkarsa ANR olarak sayılır.

Bu yüzden aşağıdaki karar kuralının merkezinde bu iki sayı var.

---

## İddia 2 — "Uygulama zaten bitti, sadece masaüstü kaldı, ikisi de Drive'a yazar"

Bu iddianın senkron kısmı doğru, "bitti" kısmı erken, ve sonuç kısmı **tam native
seçilirse kendi kendini bozuyor.**

### Senkron: doğru

İki taraf da Drive `appDataFolder`'a yazarsa senkron kurulur. Bu mimariden bağımsız —
Compose da olsa web de olsa aynı. Bu argüman native lehine ya da aleyhine değil, nötr.

### "Bitti": henüz değil

Android tarafı yayına **hazır**, ama "bitti" başka bir şey. Açık duran işler:

- Widget'ın Kotlin tarafı (`WidgetCizer.kt`) hâlâ eski çizgi mantığında — **kum havuzu
  widget'a hiç yansımadı.** Yani ana ekranda gösterdiğimiz sanat, uygulamadaki sanat değil.
- Gradle derlemesi kullanıcının makinesinde henüz yeşile dönmedi (`widget-denetim.md`).
- Kum havuzu ve tanıtımı **telefonda gerçek kullanımda hiç denenmedi** — ses, titreşim,
  taşın düşme hissi bilinmiyor.
- `13-bulgular.md` bulgu günlüğü olması gerekirken fikir dosyasına döndü; Ç1, Ç2, Ç7 cevapsız.
- Aşama 3 (Forest ile paralel kullanım denemesi) yaşanmadı.

`CLAUDE.md`'nin kendi ölçütü — *"bitmiş şekilde görünmüyorsa o özelliği eklemem"* —
burada bir yeniden yazıma değil, **önce bu listenin kapanmasına** işaret ediyor.

### "Sadece masaüstü kaldı": tam native bunu ucuzdan pahalıya çeviriyor

Bu, iddianın en çok gözden kaçan yeri. Masaüstü işinin bugünkü fiyatı **bir hafta sonu**,
çünkü yapılacak şey mevcut `index.html`'i Tauri ile sarmak: ~5–10 MB paket, WebView2'yi
Windows'un kendisi sağlıyor, kaynak tek.

Compose'a geçilirse Tauri yolu **ölür**. Yerine gelen seçenek Compose Multiplatform
Desktop ve dürüst olmak gerekirse bunun gerçek bir avantajı var: sanat kodu bir kez
yazılır, telefonda ve masaüstünde aynı kod çalışır. Ama bedeli:

- Paket bir JVM çalışma zamanı taşır: ~5–10 MB yerine **~50–80 MB**.
- Microsoft Store'a JVM uygulaması dağıtmak Tauri'den belirgin daha zahmetli.
- Ve o iş bir hafta sonu değil.

Yani "geriye sadece masaüstü kaldı" cümlesi, tam native kararıyla birlikte doğruluğunu
yitiriyor: geriye kalan iş **bir hafta sonu değil, ikinci bir uygulama** olur.

---

## Native'in gerçek kazançları (bunları küçümsemiyorum)

Yukarıdaki iki itiraz, native'in faydasız olduğu anlamına gelmiyor. Dördü gerçek:

**1. Widget ile uygulama arasındaki çizim ikiliği biter.** Bu listedeki en sağlam
argüman, çünkü bir korku değil **şu anda yaşanan bir hata.** Sanat JS'te, widget
Kotlin'de olduğu için her sanat kararı iki kez yazılmak zorunda ve ikincisi hep
geride kalıyor. Kum havuzu bunun kanıtı.

**2. Açılış süresi ve parlama.** WebView başlatması 200–400 ms; Compose'da ~100 ms.
Karanlık moddaki açılış parlamasını `values-night` temasıyla yamamak zorunda kalmıştık —
native'de o sorun hiç doğmaz. "Sağlam ve stabil görünmek" hedefi için boş bir kazanç değil.

**3. Bellek ve ANR riski.** WebView tek başına 80–150 MB taşıyor. Ucuz telefonda arka
planda öldürülme ve yukarıdaki ANR eşiğini zorlama ihtimalini artıran şey bu.

**4. Köprü ortadan kalkar.** Haptik, DND, ekran açık kalma, akıllı saat — hepsi
doğrudan çağrı olur; `KertikNative` sözleşmesi ve onun 23 testi gereksizleşir.

---

## Gerçek maliyet (tahmin değil, ölçüm)

`kertik-android/app/src/main/assets/index.html` bugün:

| | |
|---|---|
| Toplam | **6.938 satır / 428 KB** |
| Script | 6.207 satır |
| CSS | 623 satır |
| Fonksiyon | **345** |
| 15 dilli sözlük | ~120 KB (bunun taşınması mekanik ve kolay) |

Geriye kalan ~300 KB'ın taşınması "çeviri" değil, **yeniden ayarlama**, çünkü içindeki
sayıların hiçbiri türetilebilir değil — hepsi deneyerek bulundu ve `kronometre-durum`
hafıza dosyasında "keyfi değil" diye özellikle işaretlendi:

- Kum aralığı sabit değil: `maxF/6.2`, 30–58 arasında kırpılıyor
- 4 kademe, her kademede aralık yarıya, bedel `kat:2.9` katına
- `dkl:5` dk/çizgi; taş düşüşü 440 ms + squash + settle
- Tanıtım zamanlaması 560 / 2320 / 560 ms (akış tanıtımıyla eşleşsin diye)
- Taş dışlama elipsi `W*.30`, kadrana yakın taş %62'ye çekiliyor
- **Taşlar maskeden sonra çiziliyor** — önce çizilince mat kütle parlak plastik yumurtaya dönüyor

Ve bir de reddedilenler mezarlığı var: moiré (katman sistemi), konfeti (damla),
ahşap damarı (dar aralık), plastik yumurta (çizim sırası), "üzücü işler"
(halka/damar/kırağı). Bunlar aylık iterasyonun bedeli. **Yeni bir çizim ortamında
bu tuzakların hiçbiri aynı yerde durmuyor** — hepsi yeniden keşfedilir.

Buna ek olarak kaybedilen iki şey:

- **`tasarim/simulator.html` ve `akis-afilli.html` tezgâhı.** Palet denemesi
  2 saniyeden bir Gradle derlemesine çıkar. Bu projedeki tüm sanat kararları o
  tezgâhın ucuzluğu sayesinde alındı.
- **Eşzamanlı oturum düzeni.** Bu proje üzerinde aynı anda başka oturumlar çalışıyor
  ve aynı `index.html`'e yazıyorlar. Kademeli bir geçiş sırasında iki ayrı kaynakta
  aynı özelliğin iki hâli olur — bu, koordinasyonu bugünkünden çok daha pahalı yapar.

---

## Belirleyici engel: tam geçişi doğrulayamam

Bu, listedeki diğer her şeyden önce gelir.

- **Bu ortamda Kotlin derlenmiyor.** Çıkış filtresi `dl.google.com` (Android SDK),
  `maven.google.com` (AndroidX) ve `repo1.maven.org` (Maven Central) adreslerini kapatıyor.
  `18-native-gecis.md` bunu zaten kayda geçirmişti; 294 satırlık Kotlin derlenmemiş
  teslim edilmişti.
- **Bugünkü doğrulama yolu web'e bağlı:** Playwright/Chromium ile sayfayı aç,
  `localStorage["kertik.v1"]`e sahte veri yaz, ekran görüntüsü al ve **bak**.
  "Parlak plastik yumurta" hatası bu şekilde yakalandı. Compose'da bu yolun karşılığı yok.
- **Senin makinende de test koşmuyor:** `kertik-android/test` → `MODULE_NOT_FOUND`.

Toplamı şu: tam geçiş, **benim hiç göremediğim ve senin de otomatik test altyapın
olmayan ~7.000 satır** demek. Ve buradaki ironi önemli — geçişin ana gerekçesi
ANR/çökme riskini düşürmekti; ama doğrulanamayan bir yeniden yazım, o riski
düşürmez, **kısa vadede kesin olarak artırır.** Yani gerekçe kendi çözümünü yiyor.

---

## Karar kuralı — tahmin yerine ölçüm

Native tartışmasının tamamı tek bir bilinmeyene indirgenebilir: *WebView bu uygulamayı
gerçek cihazlarda eşiğin üstüne çıkarıyor mu?* Bunu bilmenin yolu tartışmak değil,
yayınlamak. Sıra:

**1. Şimdi: mimariye dokunmadan yayına çık.**
Kabuk hazır, API 36 karşılanıyor, AAB üretiliyor. Yayın için native'in *gerekli*
olduğu kısım (S4a) zaten yapıldı; gerekmediği kısım (S4b) yayını hiçbir şekilde
engellemiyor.

**2. Paralel, şimdi yapılabilir: widget kum havuzu portu.**
`WidgetCizer.kt`'yi Kotlin Canvas ile kum bahçesine geçir. Bu tek iş üç şeyi birden verir:
canlı hatayı kapatır, sanatın Kotlin'de nasıl durduğunu **gerçek ekranda** gösterir,
ve tam geçişin fiyatını tahminle değil ölçümle söyler. Kötü giderse kaybedilen
iki ay değil, bir hafta sonu.

**3. Yayından 2–4 hafta sonra: Play Console → Android vitals.**

| Ölçüm | Sonuç |
|---|---|
| Çökme < %1,09 **ve** ANR < %0,47 | Native'in performans gerekçesi **düşer.** Masaüstü Tauri ile bir hafta sonu. |
| Eşiklerden biri aşılıyor | Gerekçe **doğrulanır** — ve vitals hangi ekranda, hangi cihazda olduğunu da söyler. Önce o ekran hedefli düzeltilir; çözülmezse tam geçiş masaya gelir. |

**4. Masaüstü kararı 2. ve 3. adımdan sonra.**
Vitals temizse Tauri. Vitals kötüyse ve widget portu iyi gittiyse Compose Multiplatform
ciddi biçimde tartışılır — ama o noktada elimizde iki gerçek veri olur, bugün sıfır var.

Bu sıralamanın tek maliyeti **birkaç hafta beklemek.** Karşılığında iki aylık, doğrulanamayan
ve geri dönüşü olmayan bir işi tahmine dayanarak başlatmamış oluyoruz.

---

## Bu dosyanın kararları

- **"Play WebView'i cezalandırıyor" iddiası yanlış** — politika metninde WebView geçmiyor,
  yasaklanan şey bozuk ve boş uygulamalar. Kertik hiçbir maddeye girmiyor. **(kesin)**
- **Ama Android vitals cezası gerçek ve sayısı belli** (çökme %1,09 / ANR %0,47).
  Native tartışması bundan sonra bu iki sayı üzerinden yürütülecek. **(kesin)**
- **Yayın mimari değişikliği beklemeden yapılacak.** **(kesin)**
- **Widget kum havuzu portu sıradaki iş** ve aynı zamanda tam geçişin pilotu. **(kesin)**
- **Tam Compose geçişi ertelendi, reddedilmedi** — kararı vitals ölçümü ve widget
  portunun sonucu verecek. **(açık, kriteri belli)**
- Masaüstü yolu (Tauri ↔ Compose Multiplatform) yukarıdaki karara bağımlı hâle geldi.
  `23`teki "yol Tauri" kararı artık koşullu. **(açık)**

---

## Kaynaklar

- [Spam, Functionality, and User Experience — Play Console Help](https://support.google.com/googleplay/android-developer/topic/9876964)
- [Functionality, Content, and User Experience policy — Play Console Help](https://support.google.com/googleplay/android-developer/answer/9898783?hl=en)
- [Monitor your app's technical quality with Android vitals (kötü davranış eşikleri) — Play Console Help](https://support.google.com/googleplay/android-developer/answer/9844486?hl=en)
- [ANRs — Android Developers](https://developer.android.com/topic/performance/vitals/anr)
- [Raising the bar on technical quality on Google Play — Android Developers Blog](https://android-developers.googleblog.com/2022/10/raising-bar-on-technical-quality-on-google-play.html)
- [Google to start removing low-quality apps from the Play Store — PhoneArena](https://www.phonearena.com/news/google-to-start-removing-low-quality-apps-from-the-play-store-beginning-next-month_id160547)
- [Does Google Play accept webview apps? — Median.co](https://median.co/blog/will-google-play-approve-my-webview-app)
- [Are WebView Apps Google Play Store Compliant? — Nativine](https://nativine.com/blog/are-webview-apps-google-play-store-compliant-policy-guide)

İç atıflar: `18-native-gecis.md`, `23-masaustu-ve-native-karar.md`, `13-bulgular.md`,
`21-tam-ekran-widget-fiyat.md`, `CLAUDE.md`
