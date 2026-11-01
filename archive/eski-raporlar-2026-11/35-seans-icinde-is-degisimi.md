# 35 — Seans İçinde İş Değişimi: "üç saat, iki iş, biri bitti biri yarım"

> Soru (27 Ağustos 2026): *"Seansa ders çalışmak için oturuyorum, o gün ne
> çalışacağım var. Bugün medeni hukuk ve idari yargılama hukuku çalışalım
> diyorum. En başta 'ne çalışıyorsun' kısmı var ya, orası bana bir şeye hitap
> etmiyor. Üç saat çalışmış oluyorum; iki saatinde medeni hukukta istediğim
> limite gelmiş oluyorum — 200 soru çözmem gerekiyordu, çözmüşüm. Sonra idari
> yargılamaya geçmişim, oradan devam etmişim. Seans sonunda bir değil iki görev
> yapmışım: birini bitirmişim, diğeri yarım kalmış. Üstelik ilki soru çözmeydi,
> ikincisi konu anlatımı — kitap okumak."*
>
> Zemin: `34-gorev-olcusu.md` (ölçü/hedef, iki şekil: birikim ve imleç),
> `31-seans-ciktisi.md` (künye, imleç, §6'nın "Karma" reddi),
> `04-cozum-gorevler.md` (G6 tek ekran görünümü, durum modeli),
> `08-veri-modeli.md` (olay listesi, sayılar türetilir),
> `02-urun-vizyonu.md` (dürüst kayıt, sessiz arayüz),
> `24-sanat-dili.md`, `32-haptik-dili.md`, `CLAUDE.md`.

Tarih: 27 Ağustos 2026 · Durum: **uygulandı** (bkz. §13)

---

## 1. Teşhis: üç varsayım kırıldı, üçü de aynı yerden

Kullanıcı tek bir şikâyet anlatmıyor; üç ayrı varsayımın aynı anda çöktüğü tek
bir gerçek kullanım anlatıyor. Üçünün de kökü aynı: **uygulama "bir seans = bir
iş" sanıyor, oysa bir seans bir işler dizisidir.**

| # | Varsayım | Nerede yazılı | Gerçekte |
|---|---|---|---|
| V1 | Bir seansın bir işi vardır (`se.taskId` tekil) | `34 §2` | Üç saatte iki iş, sayaç hiç durmadı |
| V2 | Bir seansın bir ölçüsü vardır | `31 §6` | Biri soru, öteki sayfa — aynı seansta |
| V3 | Seansa başlarken ne çalışacağını yazarsın | `noteInput` | Başlarken **günün tamamı** biliniyor, seansın tek konusu bilinmiyor |

`31 §6` şöyle demişti: *"Aynı seansta hem sayfa hem soru girmek isteyen kullanıcı
Kertik'in hedef kitlesinin dışındadır."* Bu cümle **yanlışlandı** — hem de
ürünün birincil kullanıcısı tarafından, ilk gerçek kullanım anlatısında.
Ama nasıl yanlışlandığı önemli: kullanıcı *tek bir işe* iki ölçü istemiyor.
**İki ayrı işi** peş peşe yapıyor ve her birinin kendi ölçüsü var. §6'nın
reddettiği "Karma" modu (tek kayda hem D/Y/B hem sayfa) **hâlâ reddediliyor.**
Kırılan şey ölçünün tekilliği değil, **seansın tekilliği.**

Bu ayrımı kaybetmek bu dosyanın yapabileceği en büyük hata olurdu: çözüm seans
sonu kartını dört alanlı bir forma çevirmek değil, seansı ikiye bölmektir.

---

## 2. Karar

> **Seans bölünmez ama içi bölünür. Sayaç tek parça akar; içinde işten işe
> geçilir. Her geçiş bir "dönüş"tür: bırakılan işin sayısı tam o an sorulur,
> yeni iş oradan başlar. Süre kendiliğinden ikiye ayrılır, kullanıcı hiçbir
> çıkarma yapmaz.**

Üç karar, üçü de birbirinden bağımsız uygulanabilir:

| K | Karar | Kırdığı varsayım |
|---|---|---|
| **K1** | Seans içinde iş değiştirilebilir; süre dilimlere ayrılır | V1 |
| **K2** | Ölçü sorusu seans sonuna değil **geçiş anına** taşınır | V2 |
| **K3** | Başlat ekranındaki serbest yazı alanı kalkar; adlandırma sona iner | V3 |

### Neden bu, ekranı büyütmüyor

`CLAUDE.md`'nin tek cümlesi ("uğraştırıcı bir şey çıkarıyorsa eklemem") bu
tasarımın tek sınavı. Sayım:

- Başlat ekranından **bir alan eksiliyor** (yazı kutusu + klavye).
- Seans ekranına **hiçbir şey eklenmiyor**: bugün seans sürerken *gizlenen*
  tek satırlık iş bağı (`renderGorevSec`) artık gizlenmiyor, görünür kalıyor.
  Yeni piksel yok, var olan satırın ömrü uzuyor.
- Seans sonunda **soru sayısı azalmıyor ama yığılmıyor**: iki iş yapıldıysa
  iki sayı sorulur — biri geçişte, biri sonda. İkisi de kendi doğal anında.
- İş kullanmayan kullanıcı (anne yolu) için **hiçbir şey değişmiyor**; hatta
  başlat ekranı sadeleşiyor.

Net: bir alan eksik, bir jest fazla.

---

## 3. K1 — Dönüş: seansın içindeki iş değişimi

### 3.1 Jest

Seans sürerken, sayacın altındaki tek satır **kalır** ve o anki işi gösterir:

```
      02:14:31

   Medeni hukuk
```

Satıra dokunmak bugünün açık işlerini açar (bugün olduğu gibi, aynı sayfa).
Başka bir iş seçmek **dönüş**tür:

1. Bırakılan işin ölçüsü varsa tek sayı sorulur (`kaç soru?` / `nerede
   kaldın?`) — `boş geç` her zaman ilk satırda.
2. O ana kadar geçen **çalışma süresi** (mola hariç) o işe yazılır.
3. Yeni dilim başlar.

Aynı işe geri dönmek serbesttir; aynı iş bir seansta iki kez görünebilir.
Gösterimde birleştirilir, kayıtta ayrı durur.

### 3.2 Sormadan çözülen üç kenar durum

Bunların hiçbiri kullanıcıya soru olarak çıkmaz — soru sormak çözüm değil,
çözümsüzlüğün itirafıdır:

| Durum | Kural | Gerekçe |
|---|---|---|
| Seans işsiz başladı, ortada iş seçildi | Bağ **seansın başından** geçerlidir | Öncesinde başka iş yok; bölünecek bir şey yok |
| Geçişte sayı girilmedi (`boş geç`) | Dilim süreyle kaydedilir, künyesiz | `31 §3`: boş bırakılan seans eksik değildir |
| Süresi 60 sn'nin altında kalan dilim | Yazılmaz, yanlış dokunuş sayılır | Şüphede kaldığında az say (`02` ilke 1) |

### 3.3 Mola dönüşün neresinde

Mola verilip dönüldüğünde iş değişmez. Mola süresi hiçbir dilime yazılmaz —
`spans()` zaten mola aralıklarını ayırıyor, dilim süresi o aralıkların
**work** parçalarından türer. Molada verilen dönüş kararı (mola bitip başka
işe geçmek) dönüşü mola bitiminde başlatır, mola içinde değil.

---

## 4. K2 — Sayı, geçiş anında

`34 §5` bu soruyu seans sonuna koymuştu. İki işli seansta bu, sonda üst üste
binen bir sayfa üretir. Karar: **soru bırakma anına iner.**

Üç gerekçe, sırayla önem taşıyor:

1. **Cevap tam o an biliniyor.** Medeni hukuku bıraktığın an 200 sayısı
   önündedir; bir saat sonra hatırlamaya çalışırsın. `02`'nin birinci ilkesi
   ("emin olmadığını kaydetme") doğrudan bunu ister.
2. **Hedefe varış anı disiplinin ödendiği andır.** 200'ü tamamlayıp defteri
   kapattığın an, uygulamanın söyleyeceği tek cümlenin hak edildiği andır.
   Bir saat sonra söylenirse söz değil rapor olur.
3. **Seans sonu tek satır kalır.** Sonda yalnız son dilim sorulur — yani
   bugünkü davranışın birebir aynısı.

Bedeli dürüstçe yazılsın: **geçişe sürtünme eklenir.** Bu bilinçli. Geçiş
zaten bir duraklamadır (defter kapanır, kitap açılır); tek sayı o duraklamaya
sığar. Sürtünme kaçırılırsa `boş geç` ilk satırdadır ve hiçbir şey kaybolmaz.

### Hedefe varış — tek kertik

Girilen sayı hedefe ulaştıysa (`34`'ün `gorevDurumTazele` kuralı), geçiş
anında:

- Görev `bitti`ye döner (bugün de böyle, yeni değil).
- Kalasa **tek bir kertik** kazınır: `32`'nin `bitir` dokusunun tek vuruşluk
  hâli + `sesCalMaddi` ailesinden tek, kısa bir kesik. Uygulamanın adı zaten
  budur.
- Sayacın altındaki satır bir olgu cümlesine döner: `300'e vardın`. Sonraki
  dönüşe kadar durur, sonra yerini yeni işe bırakır.

Kırmızı çizgi: **bu bir kutlama değildir.** Konfeti (`20-sanat-geri-bildirim`
reddi), rozet, renk, büyüyen yazı, tekrar eden animasyon yok. `02`'nin kuralı:
*uygulama duygu üretmez, olguyu söyler.*

---

## 5. K3 — "ne çalışıyorsun?" kalkıyor

Bu alan üç şeyi aynı anda yapıyor ve üçünü de kötü yapıyor:

- Başlamadan önce **klavye açıyor.** Bir odak uygulamasının başlat tuşundan
  önceki son engel bir metin kutusu olamaz.
- **Söz aldırıyor.** Başlangıçta sorulan her şey bir taahhüttür; sonunda
  sorulan her şey bir kayıttır. Bu ürün kayıt tutar.
- İşe bağlanan seansta **kendini kopyalıyor** — `startSession` boş nota zaten
  işin adını yazıyor.

### Yerine ne geliyor: hiçbir şey (ve bu bir özellik)

Başlat ekranı: kadran, tek satırlık iş bağı (bugün açık iş varsa), Başlat.
Anne yolunda: kadran ve Başlat. Ekranda üçten fazla şey yok — `02` ilke 3.

**Ad kaybolmuyor, yeri değişiyor.** Seans özeti kâğıdında ve kayıt
sekmesindeki kartta seansın başlık satırı (bugün ya not, ya saat aralığı)
**dokunulabilir hale gelir**: dokun, yaz, biter. Yeni alan yok, etiket yok,
yer tutucu yok — var olan bir satır kalem kabul ediyor. `02`'nin *"geçmiş taş
değil, kurşun kalem"* cümlesinin görsel karşılığı.

> Bu, ekrana bir şey eklemeden bir yetenek kazanmanın tek dürüst yoludur:
> yeni bir kutu çizmek yerine mevcut bir satırı yumuşatmak.

---

## 6. Sanat dili: dönüş desende görünür

Kronometre modunun sanatı ebru (`kronometre-durum`: **değişmiyor**). Dönüşün
görsel karşılığı için yeni bir öge çizilmiyor — var olan bir parametre
kaydırılıyor:

> **Dönüş anında akışın açı alanı yeni bir tohum alır.** Fırça aynı sayfada
> devam eder, ama yönü döner. Hiçbir şey silinmez, hiçbir çizgi kesilmez.

Sonucu şu: **seansın resmine bakınca dönüşü görürsün.** İki saat bir yöne,
bir saat başka yöne akmış tek bir ebru. Ne etiket, ne ayraç, ne renk kodu.
`24`'ün üç saniye testi (*"istatistik mi?"*) burada kendiliğinden geçilir,
çünkü ortada okunacak bir şey yok — bakılacak bir şey var.

Kalastaki çubuk (`cizCubuk`) dönüm noktasında **saç teli inceliğinde bir
kertik** taşır. Yalnız seans kartında ve özet kâğıdında; **duvarda değil**
(orada çubuk 34 px, kertik gürültü olur).

**Pomodoro modunda hiçbir şey değişmez.** Kum bahçesinde taş seans başına
düşer, dönüş taşı bölmez. Gerekçe `05`'in kuralı: ortada pomodoro şikâyeti
yok, kullanıcının anlattığı üç saatlik akış kronometre modudur. `kronometre-durum`
notu bağlayıcı: **iki modu tek ölçekte birleştirmeye çalışma.**

---

## 7. Seans sonu: künye değil, defter

İki işli seansın özet kâğıdı, kalasın dibine kazınmış iki satır:

```
                2s 58dk

   Medeni hukuk        1s 54dk   ▲200 → 300  ✓
   İdari yargılama        58dk   s.52 → 120
```

- Süreler `--kopru` tonunda, kutu yok, çubuk yok, renk yok (`31 §3`).
- Hedefe varılan satırda hedef tekrar yazılmaz (`34 §9`'un `varildi` kuralı);
  ✓ zaten söylüyor.
- **Yüzde yok.** "Seansın %66'sı medeni hukuka gitti" tam olarak `24`'ün
  yasakladığı KPI panosudur.
- Tek işli seansta bu blok **tek satırdır** — yani bugünkü künyenin aynısı.
  Özellik kendini ancak iki iş yapıldığında gösterir.

Kayıt sekmesinde de aynı: açılmış seans kartı bir yerine iki künye satırı
taşır. Gün başlığı ve gün özeti (`{n} işten {d} oldu`) **değişmez** — orası
`04 G6`'nın görünümü, zaten iş bazlı.

---

## 8. Veri modeli

`08-veri-modeli.md`'nin altın kuralı korunuyor: **süre türetilir, saklanmaz.**
Saklanan tek yeni şey kullanıcının *girdiği* şeydir.

Seansa tek alan eklenir:

```js
se.isler = [
  { taskId, at, olcu, olcuVeri },   // at = dilimin başladığı an
  ...
]
```

| Kural | |
|---|---|
| `isler[0].at` | daima `se.startedAt` |
| Dilim sonu | bir sonrakinin `at`'i; sonuncunun sonu `se.endedAt` |
| Dilim süresi | o aralığın `spans()` **work** parçalarının toplamı — türetilir |
| `se.taskId` / `se.olcu` / `se.olcuVeri` | `isler[0]`'ın **aynası**, geriye dönük uyum için yazılır |

**Göç yok, okuma anında uyarlama var.** `seansIsleri(se)` erişimcisi `se.isler`
varsa onu, yoksa eski üç alandan tek elemanlı bir dizi üretir. Diskteki eski
seanslara dokunulmaz — `31 §4`'ün ilkesi: *geçmiş taş değil, ama geçmişin ne
olduğu da değişmez.*

`34`'ün türetmeleri dilim üzerinden yürür ve davranışları aynen korunur:

- `soru` (birikim) → aynı göreve yazılmış **tüm dilimlerin** `▲▼○` toplamı.
  Bir seansta aynı işe iki kez dönüldüyse ikisi de toplanır — doğru davranış.
- `sayfa` (imleç) → zincirdeki **en son** dilimin `page` değeri. İki kez
  dönüldüyse sonuncusu kazanır — doğru davranış.

İkisinin de değişmemesi, `34 §3`'teki "iki şekil" ayrımının sağlam kurulduğunu
gösteriyor: seans bölününce şekiller kendiliğinden doğru davrandı.

---

## 9. Kırmızı çizgiler

`31 §3` ve `34 §6`'nın listeleri aynen geçerli. Üstüne bu dosyanınkiler:

- ❌ **Geçmişte iş değiştirme.** Kayıt sekmesi salt okunur kalır (`04 G5`).
  Dünkü seansı ikiye bölmek, gün sonu muhasebesinin anlamını siler.
- ❌ **İş bazlı istatistik.** "Bu hafta medeni hukuka 6 saat" bir eğridir,
  eğri `31 §3`'te yasaklı.
- ❌ **Seans içi süre hedefi.** `34 §10.3` bağlayıcı: süre hedefi şişirilebilir.
  Dilim süresi hedefi bu yasağın küçültülmüş kopyasıdır.
- ❌ **Otomatik dönüş.** "25 dakikadır aynı işte, değiştirmek ister misin?"
  — uygulama seansın içine konuşmaz (`32 §1`: *seans sürerken uygulama
  kendiliğinden titremez*, aynı doktrinin sözlü hâli).
- ❌ **İkiden fazla işi tek ekranda listeleme baskısı.** Dönüş sayfası
  bugünün açık işlerinin **aynı sayfasıdır**; yeni bir seçici yapılmaz.
  Çip şeridi reddi (`34 §6`) burada da geçerli.
- ❌ **Tek işe iki ölçü.** `31 §6` yürürlükte. Bir dilimin bir ölçüsü vardır.

---

## 10. Eklenmeyenler ve gerekçeleri

**"Bugün ne çalışacağım" ekranı.** Kullanıcı günün gündemini biliyor ("bugün
medeni hukuk ve idari yargılama") — ama bu bilgi zaten görevler sekmesinde
duruyor. Başlat ekranına bir gündem paneli koymak, var olan bir listeyi ikinci
kez çizmektir. Tek satırlık bağ yeterli.

**Dilime not.** "Medeni hukuk — türev sorularında takıldım" cazip. Ama seans
içi karalama kutusu (`sessionNoteInput`) zaten var ve zaten seansın tamamına
ait. İkinci bir metin alanı yeni bir yetenek değil, yeni bir yüktür
(`31 §6`'nın terim kutusu için verdiği aynı karar).

**`adet` ölçüsü.** `34 §10.2`'de hazır bekliyor. Bu dosya onu çağırmıyor:
kullanıcının anlattığı iki iş de mevcut iki ölçüyle karşılanıyor (soru →
`soru`, konu anlatımı/kitap → `sayfa`). Şikâyet çıkarsa sıradaki odur.

---

## 11. Doğrulama ölçütleri

- [ ] Tek işli seans, bu dosya yokmuş gibi biter — fazladan tek piksel, tek
      soru, tek gecikme yok.
- [ ] İşsiz seans (anne yolu) başlat ekranında kadran + Başlat'tan ibaret;
      dönüş arayüzü hiç var olmaz.
- [ ] Üç saatlik seansta iki dönüş yapılır; sürelerin toplamı seansın onaylanmış
      süresine **birebir** eşittir (mola hariç, kayıp dakika yok).
- [ ] Molada yapılan dönüş, mola süresini hiçbir dilime yazmaz.
- [ ] Hedefe geçiş anında varıldığında görev `bitti` olur ve kertik **bir kez**
      kazınır (dönüş geri alınıp tekrarlanırsa iki kez değil).
- [ ] Aynı işe geri dönülen seansta `soru` toplanır, `sayfa` sonuncuyu alır.
- [ ] `boş geç` ile geçilen dilim, kayıtta eksik/uyarılı görünmez.
- [ ] 60 sn altındaki dilim hiç yazılmaz.
- [ ] Eski (isler'siz) seanslar kayıt sekmesinde birebir eskisi gibi çizilir.
- [ ] Üç saniye testi (`24 §1`): özet kâğıdındaki iki satırlık defter
      "istatistik" cevabı almıyor.
- [ ] Seans resmi dönüşte yön değiştiriyor; kesik/ayraç görünmüyor.
- [ ] Işık ve karanlık modda iki künye satırı kalastan ayrışıyor ama ondan
      yüksek sesli değil.

---

## 12. Uygulama sırası (bağımsız parçalar)

Üçü ayrı ayrı gönderilebilir; ikisi tek başına da değer üretir.

1. **K3** (yazı alanının kalkması + başlık satırının kalem kabul etmesi) —
   en küçük, en görünür, hiçbir şeye bağlı değil.
2. **K1** (`se.isler`, `seansIsleri`, dönüş sayfası, dilim süreleri, iki
   satırlık defter) — asıl iş.
3. **K2** (geçiş anında sayı + hedefe varış kertiği) — K1'in üstüne oturur.
4. Sanat: ebrunun tohum kayması, çubuktaki saç teli kertik.

`13-bulgular.md`'ye yazılacak asıl bulgu ise şu: **`31 §6`'daki "bu kullanıcı
hedef kitlemizin dışındadır" cümlesi, ürünün birincil kullanıcısını dışarıda
bırakıyormuş.** Kapsamı korumak için yazılan cümleler en çok bu şekilde
yanılır; bir sonraki "bu bizim işimiz değil" cümlesi yazılırken hatırlanmalı.

---

## 13. Uygulandı (27 Ağustos 2026)

`kertik-android/app/src/main/assets/index.html`:

- `se.isler` dizisi + `seansIsleri(se)` / `dilimler(se, ref)` / `dilimSuresi(se, a, b, ref)`.
  `se.taskId`/`olcu`/`olcuVeri` her zaman `isler[0]`'ın aynası. Eski (isler'siz)
  seanslar `seansIsleri()` içinde okuma anında uyarlanıyor — **disk göçü yok.**
- `renderGorevSecAktif` + `donusSec` + `donusYap` — seans sürerken sayacın
  altındaki satır kalıcı, dokununca dönüş. İki durum sormadan çözülüyor:
  seans işsiz başlayıp ilk kez iş seçilmesi (bölünmüyor, etiketleniyor) ve
  60 sn altı dilim (yanlış dokunuş, geri alınıyor).
  `askOlcuDetay`/`askDonusOlcu` artık ortak bir gövdeyi (`askOlcuDetayIcin`)
  paylaşıyor; `setOlcu` ve dönüşün `devamEt`i ortak `uygulaOlcu`'yu çağırıyor —
  hedefe varış tekliği (`buzz("kertik")` + `sesCalKertikCentik()` + `flash`)
  tek yerde, tek kez tetikleniyor.
- `defterHtml(se)` — tek işli seansta `kunyeHtml`'in birebir aynısı; iki+ işli
  seansta iş adı · dilim süresi · dilim künyesi satırları. Hem `showSummary`
  hem `renderLog` kartı bunu kullanıyor.
- `askSessionNote` — seans başlığı (özet ve kayıt kartında) artık dokununca
  yazılabiliyor. `noteInput` kaldırıldı; `startSession` artık notu iş adından
  **otomatik doldurmuyor** (bkz. aşağıdaki düzeltme).
- DOKU sözlüğüne `kertik` eklendi (`bitir`in tek vuruşluk hâli).
  Dil: `tr`/`en`'e `sn_baslik`, `sn_ekle`, `flash_hedefe_vardin` eklendi.

### Uygulama sırasında düzelttiğim iki nokta (tasarımdan sapma, bilerek)

1. **Künye stili tasarım taslağındaki gibi DEĞİL.** §7'nin mockup'ı
   "▲200 → 300 ✓" yazmıştı — bu, görev sekmesindeki KÜMÜLATİF künyenin
   (`gorevKunyeHtml`) biçimiydi, seans/dilim künyesinin (`kunyeHtml`) değil.
   Uygulamada zaten iki ayrı künye stili var: görev künyesi kümülatif +
   ok + varildığında sessiz; seans künyesi HAM giriş (`s.52`, `▲12 ▼3 ○1`),
   ok yok, hedef yok. Defter satırları seans künyesi ailesine ait olduğu
   için ham stili aldı — tutarlılık, taslaktaki örnek metinden önce geldi.
2. **`noteShow` çift satır sorunu.** İlk sürümde `startSession` notu hâlâ
   seçili işin adından dolduruyordu; ekran görüntüsünde iş adı hem `noteShow`
   hem yeni dönüş satırında (`gorevSec`) İKİ KEZ göründü — tam da `02`'nin
   "annem kaybolur mu" testinin yakalaması gereken yankı. Düzeltme: not artık
   session başlarken boş, yalnız `askSessionNote` ile sonradan yazılıyor.
3. **Hedefe varış "olgu cümlesi" kalıcı değil, geçici (`flash`).** §4 taslağı
   sayacın altındaki satırın dönüşe kadar "300'e vardın" olarak kalmasını
   öneriyordu; bu, ayrı bir kalıcı durum alanı gerektirirdi. Bunun yerine var
   olan `flash()` mekanizması (dönüm noktası bildirimleri zaten bunu kullanıyor)
   yeniden kullanıldı — yeni bir UI yüzeyi açmadan aynı hissi veriyor.

### Doğrulandı (headless, Playwright + `/opt/pw-browsers/chromium`)

Yirmi bir yol, sıfır konsol hatası: anne yolu (görevsiz), işsiz başlayıp ilk
iş seçimi (bölünmüyor), 60 sn altı dönüş (geri alınıyor), gerçek dönüş (ölçü
soruluyor, süre doğru dilime yazılıyor, hedefe varan iş `bitti` oluyor, tek
kertik), ikinci dilimde bitiş + sayfa ölçüsü, iki satırlık defter (özet +
kayıt kartı), seans başlığının sonradan adlandırılması, tek işli seansın
eskisiyle birebir davranması, eski (isler'siz) seansın hatasız uyarlanması,
dönüşte "boş geç" (künye sessiz kalıyor, undefined/NaN sızmıyor). Görevler
sekmesi ekran görüntüsüyle (kümülatif künye hâlâ doğru) ve seans özeti/duvar
ışık+karanlık modda ekran görüntüsüyle incelendi. `node --check` temiz.

### Doğrulanmadı

- Gerçek cihazda dokunma hissi, `kertik` dokusunun/`sesCalKertikCentik`'in
  gerçek titreşim motorunda hissi.
- Gerçek zamanlı (time-travel'sız) çok saatlik bir seansta toplam sürenin
  dilim sürelerinin toplamına birebir eşitliği yalnız ARALIK TOPLANABİLİRLİĞİ
  ile (matematiksel olarak) doğrulandı, dakikalarca gerçek bekleme ile değil.
- 13 dilin geri kalanında yeni üç anahtarın satır uzunlukları.


---

## 14. K4 — "+ yeni iş": görev listesi olmadan da adlandırma (2 Eylül 2026)

> Şikâyet: *"Borçlar hukukunda üçüncü kişilere ifayı bitirdim, soru çözdüm;
> şimdi zamanaşımına geçeceğim. Ama bunu yapamıyorum — illa görevlerde ekli
> ise seçebiliyorum, ben bugünün görevlerini eklemedim. İlk konuda çözdüğüm
> sorular farklı, ikinci konuda çözdüğüm sorular farklı."*

### Kırılan varsayım (V4)

`35` seansın tekilliğini kırdı ama bir varsayımı olduğu gibi bıraktı:
**dönülecek iş, dönmeden ÖNCE eklenmiş olmalı.** Üç seçim yüzeyi de
(`renderGorevSec`, `askSeansGorev`, `donusSec`) yalnız `bugunAcikGorevler()`
listesini çiziyordu; liste boşsa seans sürerken satır hiç görünmüyordu.
Sonuç: görevleri önceden eklemeyen kullanıcı — yani asıl kullanıcı — dönüş
özelliğine hiç erişemiyordu. `K3` klavyeyi başlat ekranından kaldırmıştı;
ama adlandırmayı sona indirirken **araya** inmesini unutmuştuk.

### Karar

> **Her iş seçim sayfasının son satırı `+ yeni iş`tir. Yazdığın ad o an
> bugünün işi olur, bir kez ölçüsü sorulur, akış kaldığı yerden devam eder.**

- Ad **gerçek bir görev** olur (`bekliyor`, bugüne planlı). Böylece kendi
  künyesini taşır: birinci konunun `▲12 ▼3 ○1`'i ile ikincininki karışmaz —
  şikâyetin özü buydu. Görevler sekmesinde görünür, `bitti` işaretlenebilir,
  hedef alabilir, `gorevDurumTazele` üzerinden kendiliğinden `yapiliyor`a döner.
- Ölçü sorusu **yalnız bir kez**, ad yazıldıktan hemen sonra sorulur
  (`askGorevOlcu`, hedef her zaman atlanabilir). Sonraki dönüşlerde artık
  tür bilindiği için yalnız sayı sorulur — `K2` aynen işler.
- **Görev ekleme anı öne değil, çalışılan ana kaydı.** Gündemi sabah yazma
  zorunluluğu kalktı; `04`'ün görev modeli aynı, yalnız giriş kapısı arttı.

### Başlat ekranı korunuyor

`+ yeni iş` satırı **başlat ekranında görünmez**. Ancak (a) zaten açılmış bir
seçim sayfasında — yani bugün en az bir iş varsa — ya da (b) seans
sürerken görünür. Anne yolu (`§11`) bozulmadı: iş kullanmayan kullanıcı
başlat ekranında hâlâ kadran + Başlat görüyor, klavye seans başlamadan açılmıyor.

**Tek sapma:** seans sürerken sayacın altındaki satır artık bugün hiç iş
olmasa da görünüyor (`renderGorevSecAktif`'in gizleme dalı kaldırıldı).
Bu bilinçli: satırın kendisi olmadan `+ yeni iş`e ulaşacak kapı yok.
`§11`'in "işsiz seansta dönüş arayüzü hiç var olmaz" ölçütü bu maddeyle
**yerini** şuna bırakır: *işsiz seansta başlat ekranı hiç değişmez.*

### Uygulandı

`kertik-android/app/src/main/assets/index.html`:
- `gorevOlustur(baslik)` — `addTask`'ın kutudan bağımsız hâli.
- `yeniIsSor(cb)` — ad sayfası → görev → `askGorevOlcu(t, onDone)` → `cb(t)`.
- `askGorevOlcu` / `askGorevHedef` opsiyonel `onDone` aldı (atlama yolu dahil).
- Üç seçim yüzeyine `+ yeni iş` satırı: başlat ekranı sayfası (→ `seciliGorev`),
  `donusSec` (→ `donusYap`), `askSeansGorev` (→ ilk dilime bağla → `askOlcu`).
- `askOlcu`, bugün hiç açık iş olmasa da `askSeansGorev`'i çağırıyor
  (sayfa yalnız `+ yeni iş` ve `atla` ile açılır) — seans sonunda adlandırma.
- Sözlük: `tr`/`en`'e tek anahtar `yeni_is`. Diğer 13 dil eksik (bilinen borç).

### Doğrulandı (headless, Playwright + `/opt/pw-browsers/chromium`)

Görevsiz başlatılan seansta satır görünüyor; `+ yeni iş` → "Borçlar — üçüncü
kişilere ifa" → soru/40 hedefi; 10 dakika sonra ikinci `+ yeni iş`
("Zamanaşımı") gerçek bir dönüş üretiyor: bırakılan iş için `kaç soru?`
soruluyor, `▲12 ▼3 ○1` birinci dilime yazılıyor, defter iki satır çıkıyor
(`Borçlar… 10m ▲12 ▼3 ○1` / `Zamanaşımı 0m`), ilk görev `yapiliyor`a dönüyor,
sayaç altı satır `Zamanaşımı` oluyor. 60 sn altı dönüş hâlâ geri alınıyor
(dilim bölünmüyor, yalnız etiketleniyor). Sıfır konsol hatası.

### Bu turda AÇILMAYAN: aynı işe hem sayfa hem soru

`Notlarım`'ın ikinci maddesi ("aynı anda hem sayfa hem soru"). `31 §6` ve
`§9` bunu açıkça reddediyor; açmak seans künyesi, görev künyesi ve hedef
türetmesinin tamamını yeniden yazmayı gerektirir. Kendi dosyasında tartışılsın.
