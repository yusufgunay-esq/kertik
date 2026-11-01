# 25 — Widget, Çubuk Rengi ve Arka Plan Sanatı (16 Ağustos 2026)

Kaynak: `20-sanat-geri-bildirim.md`'deki gözlemler + canlı kullanım geri bildirimi.
İlkeler: `24-sanat-dili.md` (wabi-sabi anayasası).

Prototipler:
`tasarim/widget.html` · `tasarim/cubuk-laboratuvari.html` ·
`tasarim/durgun-murekkep.html` · `tasarim/durgun-murekkep-felsefe.md`

---

## 1. ÇUBUK — sorun geometri değil, RENK

### Bulgu

`cubuk-laboratuvari.html`'de çubuğun beş ayrı yorumu üretildi: mevcut vektör,
fırça basıncı, kalasa kazınmış V kesit, sumi-e mürekkep ağırlığı, kırık omurga.

**Hepsi birbirine benzedi.** Bu bir başarısızlık değil, bir **ölçüm**: çubuğun
algısını belirleyen şey çizginin geometrisi değilmiş.

Sonra tek değişkenli bir test yapıldı — **geometri birebir sabit, yalnız palet
değişti** (altı palet). Fark çarpıcı çıktı:

| Palet | Algı |
|---|---|
| terracotta (mevcut) | sıcak, agresif, "cehennemvari" |
| **is mürekkebi** (siyah/antrasit) | kaligrafi, çetele, sakin, zamansız |
| **çini** (indigo) | serin, zarif, mavi-beyaz porselen |
| **arduvaz** (petrol) | dingin, mineral, `20`'nin istediği ton |
| bister (sepya) | eski defter, deri, ılık |
| gece (ters) | taşa kazınmış, gece kaydı |

### Karar

> **`cizCubuk` yeniden yazılmayacak.** Geometri olduğu gibi kalıyor.
> Değişecek olan `:root` bloğundaki `--accent`.

Gerekçe:
- Geometri değişikliği 50 çizim testini kırar, riskli ve karşılığı düşük.
- Palet değişikliği **tek satır**, ve algıyı bütünüyle değiştiriyor.
- Renk uygulamanın her yerinden besleniyor (kadran, akış, çubuk, widget) —
  tek değişiklik hepsini birden düzeltiyor.

**Sıralama (öneri):** arduvaz · petrol → is mürekkebi → çini.
Terracotta tamamen atılmayabilir: **vurgu** olarak (canlı kadran çentiği,
"başlat" düğmesi) az miktarda kalması sıcaklık verir. Ana çizim rengi olmaktan
çıkarılıyor, o kadar.

### Yine de saklanan iki fikir

Laboratuvardaki yorumlar çöpe gitmiyor, ama **şimdi değil**:
- **C · Kertik (kalas + V kesit):** uygulamanın adıyla birebir örtüşen tek yorum.
  Seans sonu kartı gibi tek bir yerde, büyük ölçekte denenebilir.
- **B · Malzeme (fırça basıncı):** genlikleri artırılmış titreşim + künt uçlar.
  Palet değişikliğinden sonra hâlâ eksik hissedilirse ikinci adım budur.

---

## 2. WIDGET

### 2.1 Kontrol widget'ı = ana ekranın küçültülmüş hâli

**Önceki taslak yanlıştı.** Widget için ayrı bir düzen (solda çubuk, sağda süre
ve düğmeler) tasarlanmıştı. Doğru olan: **yeni bir arayüz icat etmemek.**

Widget artık ana ekranın birebir küçültülmüş hâli:

```
      ÇALIŞIYOR              ← eyebrow, harf aralıklı, vurgu renginde
        ｜—•                  ← çentik imi
       01:47                 ← ince, büyük, tabular
   2. saat, 47. çentik       ← alt satır
   [ Mola ]   Bitir          ← koyu hap + düz metin
```

Değişen tek şey **ölçek** ve düğme boyu. Sıra, hizalama, tipografi, renk —
hepsi aynı. Sağ üst köşede seansın çubuğu duruyor: widget'ın işi yalnız
"aç" demek değil, bir şey **göstermek** de.

**Neden bu doğru:** widget uygulamanın tanıtımı değil, kendisidir. Ayrı bir
düzen kurmak, kullanıcıya öğrenilecek ikinci bir arayüz vermek demektir.

**Zemin:** seans sürerken widget zemini de mürekkep alanını taşıyor (bölüm 3).
Böylece widget zamanla estetik kazanıyor — ana ekranda olduğu gibi.

Boylar: **4×2 ana**, 4×1 satır, 2×2 kare. Üçü de aynı dili konuşuyor.

### 2.2 Duvar widget'ı — onaylandı

Çalışma geçmişi widget'ı doğru çıkmış, geliştirilecek. İçindeki asıl fikir:

> **Patina.** Bugünün çubuğu en koyu, 20 gün öncesi solmuş, 40 gün öncesi
> neredeyse hayalet. Ödül ya da ceza değil — kâğıdın davranışı.
> Eski defter sayfası soluktur.

4×4 boyda ek olarak "gün ritmi": saat başına yoğunluk. Sayı yok, oran var.

**Geliştirme adayları:** dokunulan güne o günün özeti, ay geçişinde ince ayraç,
uzun basınca haftalık toplam.

### 2.3 Teknik gerçek (değişmedi)

| Ne | Nasıl |
|---|---|
| Metin, düğme, düzen | Doğrudan `RemoteViews` |
| Çubuk ve mürekkep zemini | Kotlin `Canvas` → `Bitmap` → `ImageView` |
| Düğmeler | `PendingIntent` → arka plan servisi, **uygulama açılmaz** |
| Saniyelik sayaç | Widget'ta **yapılamaz** (en sık 30 dk). `Chronometer` kullanılacak — sistem sayar |
| Dakikalık çentik | Widget için ideal, saniye gerekmiyor |

---

## 3. ARKA PLAN SANATI — "Durgun Mürekkep"

### 3.1 Neden mevcut akış "vav" vermiyor

Dürüst teşhis, beş madde:

1. **Doku, kompozisyon değil.** Akış alanı her yeri her yerine benzeyen bir
   yüzey üretiyor. **Bakılacak bir yer yok.** Duvar kâğıdı bu yüzden duvar
   kâğıdıdır.
2. **Süreyi anlatmıyor.** 25 dakika ile 3 saat, aynı dokunun iki yoğunluğu.
   Göz farkı okuyamıyor.
3. **Hiçbir şey kaydetmiyor.** `20`'nin en değerli maddesi —
   *"süre dağılımı desenden okunabilmeli"* — karşılanmıyor.
4. **Klişe.** Akış alanı (flow field), üretken sanatın en çok yapılan ilk
   projesidir. Gören herkes tanır. Datsuzoku'nun tam tersi.
5. **Zaten hiç bütün görülmüyor.** Soluk, arayüzün altında, kadranın çevresinde
   siliniyor.

Ayrıca denenip **elenen** bir yön: *tek sürüş* (seans boyunca uzayan tek bir
fırça çizgisi). Kavramsal olarak sağlamdı, görsel olarak solucan çıktı.
`tasarim/akis-tek-surus.html`'de duruyor — tekrar denenmemesi için.

### 3.1b Denenen ve ELENEN iki yön

Bu bölümün altındaki 3.2 (Durgun Mürekkep) **artık ana yön değil.** İki deneme
elendi, ikisi de sebebiyle birlikte burada duruyor ki tekrar denenmesin.

**Elenen 1 — Tek Sürüş** (`tasarim/akis-tek-surus.html`).
Seans boyunca uzayan tek bir fırça çizgisi. Kavramsal olarak sağlamdı
(süre = çizginin boyu, mola = boşluk), görsel olarak **solucan** çıktı.
Tek bir kalın kıvrımlı şerit, ne kadar ayarlanırsa ayarlansın organik bir
jest değil bir kurdele okunuyor.

**Elenen 2 — Durgun Mürekkep** (`tasarim/durgun-murekkep.html`).
Alan bükümüyle ebru. Görsel olarak referansa en yakın sonuç buydu, ama
kullanıcının teşhisi kesindi:

> *"Var olan bir fotoğrafı yavaş bağlantıda indirmek gibi.
> Statik bir görselin üstüne efekt atılmış."*

**Ve bu teşhis doğru.** Yöntem şuydu: alanın tamamı en baştan hesaplanıyor,
sonra zamanla *açılıyor*. Yani görüntü **yapılmıyor, açığa çıkarılıyordu.**
İlerleyen bir maske, tanımı gereği "yüklenen resim" gibi görünür.

**Buradan çıkan kalıcı kural:**

> Arka plan sanatı **eklemeli** olmalıdır. Her dakika bir şey **var edilir**,
> hazır bir şeyin üstündeki örtü kaldırılmaz. Ortaya çıkış (reveal) yasaktır;
> birikme (accretion) esastır.

Ayrıca kullanıcının istediği ambiyans netleşti: **ferah, minimalist,
dinlendirici.** Yoğun, koyu, kenardan kenara dolu bir mermer levha bunun
tersiydi.

---

### 3.2 SEÇİLEN YÖN — "Kum Bahçesi" (karesansui)

`tasarim/kum-bahcesi.html`

Kuru taş bahçesi: kum, birkaç taş, tırmık izleri. Wabi-sabi'nin kanonik
görüntüsü, ve tam olarak istenen ambiyans — **ferah, sakin, çok boşluklu.**

**Zaman nasıl kaydediliyor:**

- **Her tırmık izi bir dakika kümesi** (varsayılan 3 dk). O dakika geldiğinde
  çizilir ve **bir daha değişmez.** Eklemeli — açılan bir şey yok.
- **Her tamamlanan saat bir taş koyar.** 25 dakikalık bahçede tek taş,
  üç saatlik bahçede dört. Taş sayısı süsleme değil kayıt.
- **Mola tırmıklanmaz.** Kum düz kalır. 24 dakikalık bir mola, bahçenin
  ortasında geniş ve boş bir bant olarak durur — ölçülmeden görülür.
- **Sayılmayan süre kesik tırmık.** İz var ama sürekli değil.
- **Kısa seans küçük bahçe.** Boş kalan kum eksiklik değil; kuru bahçenin
  yarısı zaten boşluktur. "Yarım kalmış resim" sorunu doğmuyor.

**Algoritma tek satırda:** tırmık cephesi ile taşlara olan uzaklıkların
**yumuşak enküçüğü** (`smin`). Açık kumda koşut çizgiler, taşların çevresinde
halkalar, ikisi arasında yumuşak geçiş — kuru bahçenin bütün görüntüsü
buradan çıkıyor. Eğriler yürüyen karelerle (marching squares) çıkarılıp
**vektör olarak** çiziliyor; piksel tamponu yok, dolayısıyla "fotoğrafa
efekt" hissi de yok.

**Maliyet:** alan bir kez ızgaraya hesaplanıyor, bütün seviyeler aynı
ızgaradan çıkıyor. Ölçüm (Node, 348×734): **330–510 ms**, seans başına bir kez.
Uygulamada her yeni iz tek başına eklenir — dakikalık iş yok denecek kadar az.
Animasyon döngüsü yok.

---

### 3.2-eski Durgun Mürekkep (arşiv)

**Alan bükümü (domain warping) ile ebru.** Ama süsleme değil:

> **Her halka bir dakika.**

- Bükülmüş bir gürültü alanı `m(x,y)` kuruluyor ve **seansın zaman ekseni**
  olarak yorumlanıyor. Her pikselin bir "dakikası" var.
- Her dakika sınırında bir **kılcal** beliriyor — çubuktaki "dakikada bir
  çentik" dili, alan diline çevrilmiş hâli. Saat başları daha güçlü.
- **Çalışılan dakika:** çalkantılı, kılcallı, doygun.
- **Mola:** alan düzleşiyor, doygunluk düşüyor, kılcallar susuyor.
  24 dakikalık bir mola, desenin ortasında **geniş ve durgun bir su** olarak
  duruyor. Kimse "bu bir moladır" demiyor; göz zaten biliyor.
- **Yayılma:** mürekkep `m ≤ ilerleme` olan yere ulaşmış. Seans ilerledikçe
  organik olarak yayılıyor — daire değil.
- **Ulaşmamış yer delik değil.** Desen orada zaten var, sadece %10 görünürlükte
  bir hayalet. (İlk denemede saydam bırakılmıştı; "kesilmiş" gibi okunuyordu.)

**Kavramsal tohum — hiçbir yerde yazmayacak:** ebru. Teknesi bir kere kaldırılır,
geri alınamaz. Uygulamanın tek iddiası da bu: *dürüst kayıt.*
Bilen hisseder, bilmeyen sadece güzel bir şey görür.

### 3.3 Bunun getirdiği karar: seans modu KARANLIK

Derinlik karanlık ister. Referans görselin etkileyici olmasının sebebi
konusu değil, **değer aralığı**: neredeyse siyahtan parlak vurguya.
Krem zeminde bu aralık yok.

> **Seans başlayınca ekran mürekkebe dönüyor** — tema ne olursa olsun.
> Seans bitince geri geliyor.

Yan kazançlar: OLED'de pil, gece kullanımı, ve `21`'deki tam ekran seans
kararının doğal tamamlayıcısı. Uygulamanın geri kalanı (kayıt, görevler,
ayarlar) krem kalıyor.

Kâğıt paletleri yine de üretildi — boş ekran ve kayıt sayfası için, aynı
algoritma ters değer aralığıyla.

### 3.4 Maliyet

Seans başına **tek hesap**, düşük çözünürlüklü tampona, sonra yumuşatılarak
büyütülür. Ölçüm (Node, 240×507): **250–290 ms.**
Kare döngüsü yok, parçacık yok, `requestAnimationFrame` yok — `24-sanat-dili.md`
seijaku maddesi korunuyor. Hesap bitince işlemci tamamen serbest.

Mevcut akışın 22.000 deneme + komşuluk taraması maliyeti tamamen düşüyor.

### 3.5 Açık sorular

- **Okunabilirlik.** Büyük ince rakam, çalkantılı zeminin üstünde okunacak mı?
  Muhtemelen bir karartma katmanı gerekecek — ama katman deseni de öldürür.
  Denenecek: sadece metnin arkasında yerel karartma, ya da desenin merkezde
  sakinleşmesi.
- **Palet sayısı.** Dört gece paleti çok mu? Tek bir palet + tohum çeşitliliği
  daha shibumi olabilir.
- **Tane (grain).** Şu an mineral parıltısı veriyor; bazı tohumlarda toz gibi
  okunabiliyor. Eşik aranacak.

---

## 4. Titreşim ve ses

`24-sanat-dili.md` bölüm 6.5'e eklendi. Özet: **haptik, elle hissedilen
malzemedir** — bu dosyanın "eksik olan malzeme" tezinin dokunma karşılığı.

- Bildirim haptiği değil **malzeme haptiği**: 8–20 ms, keskin, anında.
- Her titreşim bir maddi olaya karşılık gelir; karşılıksız titreşim
  sahte dokuya eşdeğerdir.
- **Seans sürerken uygulama kendiliğinden titremez.** Yalnız dokunuşa cevap.
- Ses varsayılan **kapalı**; açılırsa melodik değil maddi (çentik, taş, kalem).
- Gerekçe: en yüksek getirili premium kalemi — birkaç saat iş, sıfır APK yükü.

---

## Yapılacaklar sırası

1. **Palet kararı** — arduvaz/petrol mü, is mürekkebi mi. `:root` tek satır.
   *(En yüksek etki / en düşük maliyet. Önce bu.)*
2. **Kum Bahçesi**: gerçek telefonda okunabilirlik testi — büyük ince rakam
   tırmık izlerinin üstünde okunuyor mu. (Mürekkep denemesindeki asıl risk
   buydu; bahçe çok daha açık olduğu için muhtemelen sorun değil.)
3. Kontrol widget'ı: ana ekranın küçültülmüş hâli, `RemoteViews` + `Bitmap`.
4. Duvar widget'ı: patina ile.
5. Haptik sözlüğü — üç olay (başlat / mola / bitir), yarım gün iş.
6. Çubuk geometrisi — **yalnız 1. madde yetmezse.**

**Not:** `tasarim/durgun-murekkep.html` ve `tasarim/akis-tek-surus.html`
silinmedi. İkisi de neden elendiğiyle birlikte duruyor; aynı yola tekrar
girilmemesi için.
