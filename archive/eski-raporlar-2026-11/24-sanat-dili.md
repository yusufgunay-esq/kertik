# 24 — Sanat Dili: Wabi-Sabi Anayasası

> Bu dosya **kalıcıdır ve bağlayıcıdır.** Kertik'te üretilen her görsel —
> çubuk, akış, kadran, widget, mağaza görseli, ikon — buradan geçer.
> `06-estetik-konseptler.md` MVP dönemine ait bir *keşif* dosyasıdır ve
> geçerliliğini korur; bu dosya onun üstüne gelen **karar** katmanıdır.
>
> İlgili: `20-sanat-geri-bildirim.md` (gözlemler), `19-akis-ve-cubuk.md` (uygulama),
> `25-widget-ve-cubuk-estetigi.md` (bu ilkelerin ilk uygulaması)

Tarih: 16 Ağustos 2026

---

## 0. Cevap: evet, ama henüz değil

Soru şuydu: *"Wabi-sabi olarak bilinen bir sanat tarzına sahibiz herhalde şu an,
öyle değil mi?"*

**Niyet olarak evet. Uygulamada henüz hayır.** Ve bu ikisinin arasındaki boşluk,
kız kardeşinin "şirket grafiklerine benzedi" demesinin tam sebebi.

Şu an elimizde olan şey wabi-sabi değil, **minimalizm.** İkisi aynı şey sanılıyor
ama akrabası bile değiller — hatta zıt yönlerden gelirler:

| | Minimalizm (Batı) | Wabi-Sabi (Japon) |
|---|---|---|
| Kökeni | Endüstriyel tasarım, Bauhaus, Braun | Zen budizm, çay seremonisi, XVI. yy |
| Amacı | **Kusuru gidermek** | **Kusuru ağırlamak** |
| İdeali | Mükemmel, tekrarlanabilir, steril | Eskimiş, tek, geçici |
| Malzeme | Gizlenir (pürüzsüz yüzey) | **Açık edilir** (çatlak, damar, patina) |
| Zaman | Zamansız olmaya çalışır | **Zamanı üstünde taşır** |
| Sonucu | Braun saat, iPhone... **ve KPI panosu** | Raku çanağı, kintsugi, sumi-e |

Son satır kritik. **Minimalizm tek başına bırakıldığında kaçınılmaz olarak
kurumsal panoya yakınsar.** Çünkü ikisi de aynı şeyi yapıyor: gürültüyü at,
düz vektör bırak, eşit aralık koy, tek vurgu rengi kullan.

Bir şirketin çeyrek raporundaki bar grafiği de tam olarak budur: **temiz,
sade, düz, eşit, tek renkli.** Bizim çubuğumuz da öyle. Ad "çentik" olduğu
için farklı sandık; göz adı okumuyor, **malzemeyi** okuyor.

> **Kertik'in sanat dili wabi-sabi'dir.** Bu bir üslup tercihi değil, ürünün
> tek büyük fikrinin — *dürüst kayıt* — görsel karşılığıdır. Dürüstlük
> mükemmellikle çelişir. Kusursuz çizilmiş bir kayıt, kusursuz olmayan bir
> günü anlatamaz.

---

## 1. "İlk bakış illüzyonu" neden oldu — tekrar etmemesi için

`20-sanat-geri-bildirim.md` bunu doğru teşhis etmişti, buraya kalıcı olarak alıyorum:

İlk gördüğünde "wow" dedin, çünkü zihnin **fikri** gördü (kronometre yerine çentik)
ve aradaki boşlukları kendi kültürel çağrışımlarınla doldurdu — kaligrafi, tapınak,
parşömen. Göz alışınca çağrışım buharlaştı, geriye **ekrandaki gerçek piksel** kaldı.
Kız kardeşin ise o çağrışıma hiç sahip olmadığı için ilk saniyede gerçek pikseli gördü.

**Kural:** Bir görselin gerçek değeri, onu ilk kez gören ve fikrin arkasındaki
hikâyeyi bilmeyen birinin tepkisidir. Kendi tepkin taraflıdır, ilk gün geçersizdir.

**Test:** Ekranı, projeyi hiç bilmeyen birine 3 saniye göster ve sor:
*"Bu ne?"* — "Bir grafik" / "İstatistik" / "Uygulama arayüzü" cevabı **başarısızlıktır.**
"Bilmiyorum ama güzel" / "El yapımı bir şey" / "Bir kayıt gibi" cevabı başarıdır.

---

## 2. Yedi ilke ve Kertik'teki karşılıkları

Zen estetiğinin klasik yedi ilkesi (Hisamatsu Shin'ichi). Her birinin yanında
**Kertik'te şu an ne durumda olduğu** yazıyor — bu tablo yol haritasıdır.

### 2.1 Kanso 簡素 — Sadelik
Gereksiz olanı çıkarmak. Ama *çıkarmak*, "hiç koymamak" değildir.

**Durum: ✅ Tam.** Ürünün en güçlü tarafı. Rozet yok, seri yok, konfeti yok,
kilit ikonu yok. Buna dokunma.

**Tuzak:** Kanso'da fazla iyi olduğumuz için diğer altısını yapmadığımızı
fark etmedik. Sadelik tek başına yeterli sanıldı. Değil.

---

### 2.2 Fukinsei 不均整 — Asimetri, düzensizlik
Simetri makine işidir. El, asla iki şeyi birebir aynı yapamaz — ve güzellik
oradadır. Japon çömlekçi çanağı bilerek yamultmaz; **yamuk olmasına izin verir.**

**Durum: ⚠️ Yarım.** `cizCubuk` içinde tohumlu titreşim havuzu var
(`r1, r2, r3` → boy ±%4.5, y kayması ±0.35px, açı ±0.75px, kalınlık ±0.175px).
Matematik doğru, **genlik çok küçük.** Telefon ekranında 0.35 pikselik bir sapma
antialiasing içinde kayboluyor — kodda var, gözde yok.

**Yapılacak:** Sapma genlikleri gözle görülür seviyeye çıkarılmalı. Kural:
*bir insan, iki çentiğin farklı olduğunu ölçmeden görebilmeli.*

---

### 2.3 Shizen 自然 — Doğallık, yapmacıksızlık
Doğal olan, "doğa temalı" demek değil. **Niyetsiz görünmek** demek. Zorlanmış
bir el yapımı taklidi (sahte kahve lekesi, yapay yıpratma dokusu) shizen'in
tam zıddıdır — o *kitsch*'tir.

**Durum: ⚠️ Riskli.** Kâğıt dokusu denendi ve doğru kararla kaldırıldı
(`19-akis-ve-cubuk.md`) — çünkü **eklenen doku** yapmacıktı. Ekranı yaşlandırdı,
renkleri öldürdü. Doğru refleks.

**Ders:** Doku *üstüne serpilen bir katman* değil, **çizginin kendi
davranışından* çıkmalıdır. Kâğıt dokusu değil, fırça basıncı. Zemine değil,
çizgiye dokun.

---

### 2.4 Yugen 幽玄 — Örtük derinlik, ima
Her şeyi söylememek. Sisin arkasındaki dağ, dağın kendisinden güçlüdür.
Gösterilen değil, **sezdirilen.**

**Durum: ✅ Kavramsal olarak güçlü, ❌ görsel olarak yok.**
Ürün kavramsal olarak yugen dolu: sayılmayan sürenin konumu iddia edilmiyor,
sadece miktarı duruyor. Bu mükemmel bir yugen hamlesi — bilgiyi eksik bırakmak
dürüstlük oluyor.

Ama görselde hiç yok. Her çentik aynı netlikte, aynı opaklıkta, aynı kesinlikte.
Hiçbir yerde belirsizlik, solma, yarım bırakılmış bir uç yok.

**Yapılacak:** Çentiğin ucu her zaman aynı kesinlikte bitmemeli. Bazıları
soluklaşarak, bazıları keskin bitmeli — mürekkebin bittiği yer gibi.

---

### 2.5 Datsuzoku 脱俗 — Kalıptan kaçış
Formülün dışına çıkmak. Beklenen şablonu kırmak.

**Durum: ❌ Zayıf — asıl kırılma noktası burası.**
Çubuk şu an tam olarak beklenen şablonda: **dikey eksen + eşit aralıklı yatay
işaretler + soldan sağa büyüyen değer.** Bu, bar grafiğinin tanımıdır.
Yönü değiştirmek (yatay yerine dikey) şablonu kırmıyor, sadece döndürüyor.

**Yapılacak:** Bkz. `tasarim/cubuk-laboratuvari.html` — sütun mantığından
çıkan yorumlar (E: kesintili kolon, D: mürekkep yoğunluğu).

---

### 2.6 Seijaku 静寂 — Dinginlik, hareketsizlik
Sessizlik. Hareket etmeyen şeyin gücü.

**Durum: ✅ Tam ve korunmalı.** Sürekli animasyon yasağı (`ebru-muhur` kararı:
rAF yok, parçacık yok, nefes alan halka yok) bunun doğrudan uygulaması.
Pil için alınmış bir teknik karar sanılıyor ama **estetik olarak da doğru.**

**Tek istisna:** *Doğuş* animasyonları. Bir şeyin var olma anı (400–600 ms
kazınma/soluş) seijaku'yu bozmaz — çünkü biter ve durur. Yasak olan **döngüdür.**

---

### 2.7 Koko 考古 — Yıpranmışlık, çıplaklık, öz
Fazlalığın aşınıp gitmiş olması. Kemik kalması. Yaşlı bir tahta, eski bir taş.

**Durum: ❌ Hiç yok — "çizgi film" hissinin ana kaynağı.**
Ekrandaki çizgi **yeni.** Sıfır kilometre, plastik, taze basılmış vektör.
Hiçbir şey aşınmamış, hiçbir şey yaşamamış.

Kız kardeşinin anime referansı tam buraya oturuyor: iyi anime arka planları
(Ghibli, Shinkai, *Mushishi*) **malzeme dolu** — guaj dokusu, fırça kenarı,
kâğıt emişi. Kötü/ucuz animasyon ise düz vektördür. Gözü eğitilmiş biri
farkı anında görür ve bizimkini ikinci kategoriye koyar.

**Yapılacak:** Çizgiye yaş vermek. Ama shizen kuralı gereği *eklenen doku* ile
değil, **çizginin kendi geometrisi** ile — değişken kalınlık, düzensiz uç,
tek taraflı gölge.

---

## 3. Üç ek kavram

### Ma 間 — Aralık, boşluk
Boşluk "hiçlik" değil, **kompozisyonun malzemesidir.** Japon resminde boş alan,
dolu alandan daha çok karar gerektirir.

**Kertik'te:** Mola şu an bir *yokluk* (çentik atılmıyor) + kenarda serin bir iz.
Bu doğru ve güzel bir *ma* uygulaması. **Koru.** Molayı "doldurma" dürtüsüne
direnilmeli — mola boşluk olarak kalmalı.

### Sabi 寂 — Zamanın bıraktığı güzellik
Patina. Eskiyerek güzelleşen.

**Kertik'te potansiyeli devasa ve hiç kullanılmıyor:**
Bir aylık duvar, geçen zamanla **soluyabilir.** Bugünün çubuğu en koyu; 20 gün
öncesi biraz solmuş; 40 gün öncesi neredeyse hayalet. Bu hem *sabi*, hem
teknik olarak bedava, hem de "arşiv" hissini birden gerçek yapar.

> **Ödül değil.** Solma bir ceza ya da baskı değil; sadece kâğıdın davranışı.
> Eski defter sayfası soluktur. Bu bir yorum değil, bir olgudur.

### Shibumi 渋み — Gösterişsiz zarafet
Kendini beğendirmeye çalışmayan güzellik. **Bağırmayan kalite.**

**Kertik'te:** `21-tam-ekran-widget-fiyat.md`'deki "iyi bir defter — kimse
görmez, sen bilirsin" cümlesi shibumi'nin tam tanımıdır. Peşin ödeme,
kilitsiz arayüz, paylaşım katmanının yokluğu — hepsi shibumi. **Bu ürünün
karakteri budur.**

---

## 4. YASAK listesi

Aşağıdakiler estetik tercih değil, **kural ihlalidir.** Gerekçesi yanında.

| Yasak | Neden |
|---|---|
| Sürekli çalışan animasyon (rAF, parçacık, nefes alan halka, dalgalanma) | Seijaku'yu bozar + pil. Tek istisna: biten doğuş animasyonları |
| Zemine serpilmiş sahte doku (kâğıt lifi, leke, gren) | Shizen ihlali — yapmacık. Doku çizginin kendisinden çıkmalı |
| Gradyan dolgu, gölge kutusu (`box-shadow`), parlama | Malzeme taklidi değil, dijital efekt. Wabi-sabi malzemeyi taklit etmez, **kullanır** |
| Mükemmel eşit aralık, mükemmel simetri | Fukinsei ihlali. Makine parmak izi |
| İki çiğ renk zıtlığı | Palet genişletilmeli (bkz. `20`, madde 3) |
| Rozet, madalya, seri, konfeti, kutlama | Ürün felsefesi. `05-ozellik-listesi.md` "asla yapmayacaklarımız" |
| Yarım kalmış / tamamlanmamış görünen çizim | Forest'ın kuruyan ağacı. Suçlar. Her kayıt kendi başına tam görünmeli |
| AI üretimi raster illüstrasyon | Çentik–çizgi–kâğıt diline yabancı + APK şişirir |
| Yuvarlak köşeli kart + ince gölge + eşit grid | 2020 SaaS panosunun görsel imzası. Tam olarak kaçtığımız şey |

---

## 5. Filtre — her yeni görsel bundan geçer

Yeni bir görsel öğe (widget, ekran, kart, ikon) tasarlanınca, teslimden önce
altı soru. **İkiden fazla "hayır" varsa görsel geri döner.**

1. **Malzeme testi.** Bu çizgi neyden yapılmış? "Vektör" cevabıysa → hayır.
   (Mürekkep? Kazıma? Basınç? Bir şeyden yapılmış olmalı.)
2. **Asimetri testi.** İki komşu öğeyi yan yana koy. Farkları **ölçmeden**
   görülüyor mu?
3. **Yabancı testi.** Projeyi bilmeyen birine 3 saniye göster: "grafik/istatistik"
   dedi mi?
4. **Zaman testi.** Bu görselde hiç zaman geçmiş mi? Her şey aynı tazelikte mi?
5. **Ma testi.** Boşluk bilinçli mi, yoksa "doldurulmamış alan" mı?
6. **Bağırma testi.** Bu öğe kendini beğendirmeye çalışıyor mu? (Shibumi)

---

## 6. Malzeme sözlüğü — kelime yerine karar

Bundan sonra "premium", "estetik", "güzel", "wow" gibi kelimeler yerine bunlar
kullanılacak. Her biri **ölçülebilir bir kod değişikliğine** karşılık gelir.

| Terim | Görsel karşılığı | Kodda karşılığı |
|---|---|---|
| **Fırça basıncı** | Çizgi boyunca kalınlığın değişmesi; başta kalın, sonda incelen | Tek `line` yerine `path` + değişken `stroke-width`, ya da 2–3 parçalı çizgi |
| **Kazıma derinliği** | Çentiğin altında tek yönlü, ofsetli koyu iz | Var (`opacity .10`, `+0.6/+1.1px`) — genlik artırılmalı |
| **Mürekkep bitişi** | Ucun soluklaşarak bitmesi | `stroke-opacity` gradyanı veya uçta ikinci ince segment |
| **Emiş / kanama** | Mürekkebin kâğıda yayılması, ucun hafif genişlemesi | Uçta 1.2× kalınlıkta çok kısa, düşük opaklıkta ikinci vuruş |
| **Patina** | Eski kaydın solması | Duvar çiziminde yaşa göre `opacity` çarpanı |
| **Duraklama** | Elin durduğu yerde biriken mürekkep | Saat başı çentiklerinde kalınlık + hafif nokta |

---

## 6.5 Dokunulan malzeme — titreşim ve ses

Bu bölüm ayrı bir alan değil. Bu dosyanın tek cümlelik özeti *"eksik olan
malzeme"* idi; titreşim **elle hissedilen malzemedir.** Görsel malzemeyle
aynı kurallara tabidir.

### İlke: haptik bir bildirim değil, bir YÜZEYDİR

Ucuz uygulamalarda titreşim *dikkat çeker* — "bir şey oldu!" der. Pahalı
nesnelerde titreşim *maddeyi taklit eder*: Leica'nın deklanşörü, iyi bir
anahtarın tıkırtısı, ağır bir kapının kapanışı. Fark şudur:

- **Bildirim haptiği:** uzun, tek genlikte, geç. `VIBRATE 200ms`. Telefon uyarısı.
- **Malzeme haptiği:** kısa, keskin, **anında.** 8–20 ms. Parmağın altında
  bir şeyin *yerine oturması.*

Kural: **her titreşim bir maddi olaya karşılık gelmeli.** Karşılığı olmayan
titreşim, sahte dokuya eşdeğerdir — shizen ihlali.

### Haptik sözlüğü

| Olay | His | Android karşılığı |
|---|---|---|
| Başlat | Tek, net, biraz derin — bıçağın tahtaya ilk girişi | `HapticFeedbackConstants.CONFIRM` ya da tek `VibrationEffect.createOneShot(14, 90)` |
| Mola | Yumuşak, sönümlenen — bıçağın kalkması | `createOneShot(10, 45)` |
| Devam | Başlat'ın hafifi | `createOneShot(11, 70)` |
| Bitir | İki vuruş, ikincisi hafif — kapağın kapanması | `createWaveform([0,12,40,9], [0,110,0,60], -1)` |
| Saat başı (arka planda) | **Yok.** Çalışmayı bölmek yasak | — |
| Dönüm noktası bildirimi | En hafif, tek | `EFFECT_TICK` |
| Değer seçme / sekme | `EFFECT_TICK` | tek |

Kural: **seans sürerken uygulama kendiliğinden titremez.** Titreşim yalnız
kullanıcının dokunuşuna cevaptır. Seijaku haptikte de geçerli.

### Ses

**Varsayılan: sessiz.** Odaklanma uygulamasının ses çıkarması, sessiz kalma
sözünü bozar. Ama açılabilir bir katman olarak, tek bir kural:

> Ses **melodik olmamalı.** Nota yok, akor yok, çan yok, "başarı" tınısı yok.
> Yalnız **maddi ses:** tahtaya bir çentik, taşın kuma konması, kâğıda
> kalem teması.

Üç ses yeter: *başlat*, *mola*, *bitir*. Her biri 120–250 ms, düşük seviyeli,
kuyruğu kısa. Kaynak: gerçek kayıt (bir bıçak, bir taş), sentez değil —
sentetik ses her zaman "arayüz sesi" gibi duyulur.

**Yasak:** kutlama sesi, seri sesi, bildirim jingle'ı, doğa ambiyansı döngüsü
(bkz. `05-ozellik-listesi.md`, "asla yapmayacaklarımız").

### Neden bu ucuz ama etkili

Haptik, premium hissin **en yüksek getirili** kalemidir: birkaç saatlik iş,
APK'ya sıfır yük, pil etkisi ihmal edilebilir, ve elde bıraktığı izlenim
görsel bir değişiklikten daha kalıcı. `21`'deki "iyi bir defter" hedefi
için görsel kadar önemlidir — iyi defterin kâğıdı da ele öyle gelir.

---

## 7. Bu dosyanın statüsü

- **Değiştirilebilir.** Ama değişiklik gerekçesiyle birlikte yazılır, silinmez.
- **Bağlayıcı.** "Bu sefer istisna" diye geçilen her madde, bir sonraki
  "şirket grafiği gibi olmuş" anının tohumudur.
- **Tek cümlelik özeti:**

> *Sadelik bizde zaten var. Eksik olan malzeme.*
