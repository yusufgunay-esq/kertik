# 26 — Ana Ekran Widget'ları uygulamaya girdi (16 Ağustos 2026)

`21-tam-ekran-widget-fiyat.md`'nin en önemli bulgusu şuydu:

> *"Ben bu uygulamayı açtıktan sonra tekrar bu uygulamaya dönmüyorum genel olarak."*
> → **Uygulamanın kendi dışında bir yüzü yok. Görünmeyen alet unutulur.**

Bu dosya o yüzün nasıl yapıldığını anlatıyor. Tasarım gerekçeleri
`25-widget-cubuk-ve-arkaplan.md`'de; burada **uygulama** var.

---

## Ne eklendi

| Dosya | İş |
|---|---|
| `WidgetDurum.kt` | Web tarafının bıraktığı durum aynası (SharedPreferences + JSON) |
| `WidgetCizer.kt` | Çubuğun ve duvarın `Canvas` ile `Bitmap`'e çizimi |
| `KontrolWidget.kt` | Kontrol widget'ı — ana ekranın küçültülmüş hâli |
| `DuvarWidget.kt` | Duvar widget'ı — son 30 gün, patina ile |
| `res/layout/widget_kontrol.xml`, `widget_duvar.xml` | Düzenler |
| `res/xml/widget_*_bilgi.xml` | Widget tanımları |
| `res/values/widget_renkler.xml` | Palet (uygulamanın `:root`'uyla aynı) |
| `res/drawable/widget_arka*.xml`, `widget_hap.xml`, `ic_centik_im.xml` | Zemin, hap düğme, çentik imi |
| `assets/index.html` → `widgetBildir()` | Durum aynasını dolduran taraf |
| `MainActivity.Kopru.widgetDurum()` | Köprü |
| `test/test-widget.js` | 36 test |

---

## Çözülmesi gereken asıl sorun: widget veriyi nereden okuyacak

Uygulamanın bütün verisi WebView'in `localStorage`'ında. Widget **ayrı bir
süreçte** çizilir ve oraya erişemez.

**Çözüm — tek yönlü ayna.** Web tarafı durumu her değiştiğinde küçük bir JSON
bırakıyor (`~900 bayt`), widget yalnız onu okuyor.

Aynanın üç kuralı var:

1. **Türevdir, hakikat değildir.** Süre hâlâ olay damgalarından hesaplanıyor.
   Aynada hiçbir şey sayılmıyor, hiçbir şey türetilmiyor.
2. **Bozulursa veri etkilenmez.** JSON ayrıştırılamazsa eskisi olduğu gibi
   kalır; en fazla widget bir süre eski görünür.
3. **Gereksiz trafik yok.** İmza karşılaştırması var: saniyede bir çağrılsa
   bile köprüden yalnız gerçekten değişince geçiyor. (Testte 40 çağrı → 0 geçiş.)

---

## Saniyeler nasıl akıyor — widget'ta sayaç sorunu

Sistem bir widget'ı en sık **30 dakikada bir** yeniler. Saniyelik sayaç bu
yolla imkânsız.

**Çözüm:** `Chronometer`. Saati **sistem** işletiyor; biz yalnız dayanak anını
veriyoruz. Pil tüketimi yok denecek kadar az. Aynı çözüm bildirim çubuğunda
zaten kullanılıyordu (`Bildirim.kt`), yani yeni bir yol açılmadı.

Pomodoro'da `setChronometerCountDown(true)` ile geri sayıyor; hedef dolunca
dayanak geçmiş bir ana düştüğü için kendiliğinden yukarı saymaya başlıyor.

`updatePeriodMillis = 0` — iki widget'ın da **kendi yenileme döngüsü yok.**

---

## Düğmeler — uygulama kapalıyken de çalışıyor

Bildirimdeki tuşlarla **birebir aynı yol**: `PendingIntent` → `MainActivity`
→ `kertikNativeEylem(...)` → uygulamanın normal akışı → `moveTaskToBack`.
Ayrı bir kod yolu açılmadı.

Yeni olan tek şey **`start`** eylemi: eskiden `kertikNativeEylem` seans yoksa
hemen dönüyordu (bildirimde seans yokken tuş olmaz). Widget'ta "Başlat" olduğu
için bu durum artık ele alınıyor.

---

## Aynı seans, aynı çubuk — sessiz bir tuzak

Çubuk seansın **kimliğinden** türeyen tohumlu rastgelelikle çiziliyor. Widget
Kotlin'de çizdiği için `hash32` ve `rng32`'nin JS'teki hâliyle **birebir**
olması gerekiyordu; olmasaydı aynı kaydın iki farklı resmi olurdu ve bu,
projenin "dürüst kayıt" iddiasını sessizce bozardı.

JS `Math.imul` + `|0` + `>>>` üçlüsü Kotlin'de `Int` taşması + `ushr` ile
karşılanıyor, ama **operatör önceliği** kolayca kaçıyor
(`t + imul(...) ^ t` → `(t + imul(...)) ^ t`). İlk yazımda kaçtı, yakalandı.

Doğrulama: iki uygulamanın da 500 adımı, birkaç farklı tohumda, birebir
karşılaştırıldı — fark yok.

> **Bu iki fonksiyon değişirse ikisi birden değişmeli.** Her iki dosyada da
> not düşüldü.

---

## Bellek — `RemoteViews` bir Binder işlemi

Bitmap'ler Binder üzerinden taşınıyor ve boyut sınırlı. `WidgetCizer` bitmap
alanını **150.000 piksel** ile kapıyor: büyük widget'ta çözünürlük düşer, ama
hiçbir zaman `TransactionTooLargeException` atmaz.

---

## Testler

`test/test-widget.js` — 36 test, `hepsi.js`'e kaydedildi.

- boş durumda ayna doğru mu, duvar 30 gün taşıyor mu
- widget'tan başlat gerçekten seans açıyor mu
- mola / devam / bitir durumları
- **köprü trafiği**: imza değişmeyince geçmiyor, zorlanınca geçiyor
- **JSON sözleşmesi**: Kotlin'in okuduğu 12 alanın hepsi var mı, tipleri doğru mu,
  paket makul boyutta mı
- `KertikNative` yokken (tarayıcıda) sessizce geçiyor mu

Mevcut 58 çizim testi ve birleştirme testleri kırılmadı.

---

## Elde doğrulanacaklar (jsdom'un göremediği)

1. Widget ana ekrana eklenince görünüyor mu, gece/gündüz doğru mu.
2. `Chronometer` gerçekten akıyor mu; pomodoro'da geri sayıyor mu.
3. **Uygulama kapalıyken** "Başlat" — açılış gecikmesi ne kadar göze batıyor.
4. Yeniden boyutlandırmada çubuk/duvar bitmap'i bozulmuyor mu.
5. Çok uzun seansta (6 saat) çubuk sütunları widget'a sığıyor mu — bkz. aşağıda.

---

## Açık kalan tasarım soruları (kullanıcı geri bildirimi, 16 Ağustos)

Bunlar **çözülmedi**, kaybolmasınlar diye buradalar.

### 1. Ekran sınırı — uzun seans

> *"Bir telefon aşağı yukarı iki buçuk saat kadar sürebiliyor. Ben altı saat
> çalışıyorum. Bu durumda bir yerden sonra ekranıma güncelleme gelmeyecek."*

**Gerçek bir sorun ve hiçbir tasarımda ele alınmadı.** Çubuk saat başı yeni
sütun açıyor; 6 saat = 6 sütun. Dar bir widget'ta ve tam ekran seansta bir
yerden sonra sığmıyor. Aynı sorun kum bahçesinde de var (tırmık cephesi
ekranın altına ulaşınca duruyor).

Düşünülecek yönler: sütun genişliğinin süreyle küçülmesi; belli bir saatten
sonra ölçeğin sıkışması; ya da "bir ekran = bir tur" kabul edip üstüne binmesi.
**Karar verilmedi.**

### 2. Pomodoro ile kronometre aynı çizmemeli

Pomodoro'da bir **tamamlanma** var; kronometrede yok. Görselin bunu
yansıtması gerekiyor. Kum bahçesi taslağında yaklaşım denendi ama karar yok.

### 3. Kum bahçesi fazla öngörülebilir

> *"Bu kum havuzunda daha başlamadan ne göreceğimi aşağı yukarı biliyorum."*

Doğru: taş sayısı ve tırmık aralığı sabit olduğu için çeşitlilik dar.
Mevcut akışın (`AKMOD.ebru`) bu konuda üstünlüğü var — rastgelelik payı yüksek,
seans sonunda gerçekten sürpriz çıkıyor. Kum bahçesi "ne kadar güzel olmuş"
aldı ama "wow" almadı.

### 4. Taş düşmesi — saklanan fikir

Seans başlarken havadan bir taş düşmesi (ve saat başlarında yenisi), düşerken
kısa bir titreşim/ses. Kullanıcının fikri, beğenildi. Riski: ekranı dağıtabilir.
`24-sanat-dili.md`'nin seijaku maddesiyle uyumlu — **biten** bir doğuş
animasyonu, döngü değil.

---

## Durum güncellemesi (17 Ağustos 2026)

Widget şu anlık bozuk; Claude kullanım limiti nedeniyle düzeltme bekletiliyor,
tekrar ele alınacak. (Kaynak: `13-bulgular.md`.)

## Durum güncellemesi (18 Ağustos 2026) — widget kaldırılmış

Bu dosyada "uygulandı" yazan `DuvarWidget.kt` ve `KontrolWidget.kt` artık
kaynak ağacında **yok** — bir sonraki oturumda (kayıt bulunamadı, muhtemelen
bir önceki güncellemedeki "bozuk" durumun üzerine) kaldırılmışlar.
`kertik-android/app/src/main/java/com/yusufgunay/kertik/` içinde yalnız
`.kt.txt` uzantılı eski kopyaları duruyor (`DuvarWidget.kt.txt`,
`KontrolWidget.kt.txt`); `WidgetCizer.kt` küçülmüş ama `cubuk()`/`duvar()`
hâlâ duruyor, `WidgetDurum.yenile()` artık boş gövde: *"Widget'ları yenile.
Artık widget kalmadığı için boş bırakıldı."* `AndroidManifest.xml`'de de
widget `<receiver>` kaydı yok.

Buna karşılık, duvar kavramı **uygulamanın kendisine** taşınmış:
`kertik-android/app/src/main/assets/index.html` içinde `duvarCiz()` / `renderLog()`
artık gerçek, çalışan bir "kayıt" sekmesi — ana ekran widget'ı değil, ama
kullanıcı açıp gördüğü bir arşiv. Pomodoro/taş kararı ([27](27-sanat-ayrisimi.md))
oraya uygulandı.

Bu satırlar, widget'ın ne zaman ve neden kaldırıldığına dair hiçbir karar
dosyasında not bulunmadığı için yazıldı — eğer widget kasıtlı olarak
bırakıldıysa bu dosyanın "uygulandı" başlığı yanıltıcı; eğer unutulduysa
`kt/` klasöründeki `.txt` kopyalar hâlâ referans olarak duruyor.

## Durum güncellemesi (3 Eylül 2026) — Widget'lar Yeniden Devreye Alındı

Kullanıcı istişaresi ve `21-tam-ekran-widget-fiyat.md`'deki *"Görünmeyen alet unutulur"* ilkesi
doğrultusunda, Kertik'in ana ekrandaki yüzü olan `KontrolWidget` ve `DuvarWidget`
yeniden aktifleştirildi:

1. `AndroidManifest.xml` içerisine `KontrolWidget` ve `DuvarWidget` için `<receiver>` kayıtları,
   `android.appwidget.action.APPWIDGET_UPDATE` eylemleri ve `@xml/widget_*_info` meta-data
   bağlantıları eklendi.
2. `test-ambient.js` regresyon sözleşmesi güncellendi; widget'ların manifestte varlığı
   ve receiver yapılandırması test bataryasına entegre edildi.
3. `test-widget.js` (36 test) ve `test-ambient.js` (28 test) sıfır hata ile doğrulandı.
