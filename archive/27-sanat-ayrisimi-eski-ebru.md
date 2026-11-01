# 27 — Sanat Ayrışımı: Ebru → Kronometre · Kum Havuzu → Pomodoro

> Kaynak: `13-bulgular.md` 17.08 girdisi.
> İlgili prototipler: `tasarim/akis.html` (ebru), `tasarim/simulasyon-arkaplan.html` (kum havuzu).
> Bağlam: `24-sanat-dili.md` (wabi-sabi anayasası), `20-sanat-geri-bildirim.md`.

Tarih: 17 Ağustos 2026

---

## 1. Karar

Her mod kendi sanat dilini kullanacak:

| Mod | Sanat dili | Malzeme | Zaman ifadesi |
|---|---|---|---|
| **Kronometre** | Ebru (akış çizgileri) | Sıvı — mürekkep suda | Kalabalıklaşan çizgi alanı, katmanlar üst üste birikir |
| **Pomodoro** | Kum Bahçesi | Katı — taş kumda | Her pomodoro bir taş, çevresinde tırmık halkaları |

Bu ayrışım zorlanmamış: sıvı malzeme açık uçlu zamana, katı malzeme sayılabilir
birimlere doğal olarak karşılık geliyor.

---

## 2. Kum bahçesi — pomodoro detayları

### Taş düşüşü

Her pomodoro başlangıcında havadan bir taş düşer. Bu açılış hareketi:
- Taş büyüklüğü pomodoro süresine göre değişir (25 dk ≠ 60 dk).
- Ölçekleme kök oranıyla: `boyut ∝ √süre`. Lineer ölçekleme ekranı dolduruyor.
- Düşüş animasyonunun **muazzam** olması şart — şu anki prototip çok ham.
  Yerine oturma, hafif sekme, kum savrulması gibi detaylar lazım.

### Tırmık çizgileri

Seans sürerken tırmık çizgileri taşın çevresinde halkalar çiziyor.
Pomodoro'da kompozisyon sınırı hedefin kendisi — halkalar kâğıdın kenarına
ulaştığında bahçe "tam."

### Rüzgar — mola mekaniği

Mola sınırı aşılınca (varsayılan 10 dk) rüzgar eser, çizgiler dağılır:

1. Mola sınırı aşılır.
2. ~400 ms tek seferlik animasyon: çizgiler yeni pozisyonlarına kayar.
3. **Durur.** Ekran hareketsiz kalır. Sürekli rüzgar = seijaku ihlali.
4. Mola daha da uzarsa → ikinci bir dağılma, sonra yine durur.
5. Kullanıcı devam edince yeni tırmık çizgileri eski dağılmışların arasından geçer.
6. Taş her zaman yerinde kalır.

### Çoklu pomodoro

Gün boyunca birden fazla pomodoro yapılınca taşlar birikir. Duvar kısmında
o gün ve o ay kaç taş biriktirildiği gözükebilir. **Ama tonlama kayıt olacak,
ödül değil.** "Bugün 5 taş" — rozet yok, seri yok, kutlama yok.

### Duvar — taş kompozisyonu kararı ve uygulanması (18 Ağustos 2026)

> Kaynak: bu sohbet. Deneme dosyası: `tasarim/duvar-tas-secenekleri.html`
> (üç seçenek yan yana + stres testi — 20×25 dk ve 7×60 dk'lık uç günler).

Üç kompozisyon denendi: **hesap taşları** (raf boyunca dizilen taşlar,
Latince *calculus* = "küçük taş" referansı), **taş istifi** (cairn) ve
**taş patikası** (kıvrılan yol). Aşırı gün senaryosuyla test edilince
istif kırıldı: 20 taş, ölçek küçülse bile dikey bir çizgiye sıkışınca taş
hissini kaybedip ince bir iğne/barkod gibi görünüyor, ve tek başına
komşularının iki katı yükseklikte bir sivri uçla duvarın dikkatini kendine
çekiyor — tam olarak "kule = rekabet hissi" riski. Hesap taşları ve patika
zarif bozuluyor: sıkışan gün ince bir çakıl/pirinç tanesi dizisine dönüşüyor,
komşu güne taşmıyor.

**Karar: hesap taşları.** Uygulandı — `kertik-android/app/src/main/assets/index.html`
içinde `gunTas()` / `cizTas()` / `tasSvg()` / `paketleTas()`. `duvarCiz()`
artık gün bazında ayrışıyor: gün en az bir pomodoro seansı içeriyorsa taşla,
yoksa çubukla çiziliyor (aynı günde ikisi karışmıyor). Taş boyu zaten
kararlaştırılan `√süre` oranıyla; bir güne çok taş sığmayınca hepsi aynı
oranda küçülüyor, bir tabandan sonra sıkışma bilerek görünür bırakılıyor
(gizlenmiyor). `test-cizim.js`'e "5b/5c/5d" testleri eklendi: pomodoro
günü taş çiziyor mu, aynı seans hep aynı taşı veriyor mu, 14 pomodorluk
uç durum komşu güne taşmadan sıkışıyor mu.

**Yapılmadı, açık kaldı:** taş düşüşü animasyonu (bu bölümün başındaki
"Taş düşüşü" hâlâ prototip aşamasında), kayıt kartındaki tekil seans
görünümü (`.cubukwrap` / `cizCubuk`) hâlâ pomodoro seansları için de
çubuk çiziyor — duvardaki ayrışım oraya taşınmadı, ayrı bir karar gerekir.

---

## 3. Ebru — kronometre detayları

### Damla doğuşu (**KARAR DEĞİŞTİ — 18 Ağustos akşamı: damla sistemin atomu oldu, bkz. bölüm 3.5**)

Seans başlangıcında ebru da bir açılış hareketi alacak: havadan bir damla
düşer, suya temas eder, sonra mürekkep yayılmaya başlar. Kum bahçesindeki
taş düşüşünün sıvı karşılığı.

Bu animasyonun da **muazzam** olması lazım. Kötü yapılırsa çok kötü durur.
Detaylar:
- Damlanın kendisi: düşerken hafif kuyruk, yüzeye çarparken küçük sıçramalar.
- Temas anı: organik halkalar (fbm gürültüsüyle yamulmuş, eşit değil).
- Yayılma: mürekkebin gerçekten suda yayılıyor hissi.

### Popping sorunu

Şu an arka plan çizimi bir anda "küt diye" beliriyor (`20-sanat-geri-bildirim.md`,
madde 1). Damla doğuşu bunu çözecek — çizimle damla tek bir hareket gibi
hissedecek. Akis.html'de `damlaOynat()` altyapısı var ama sadece "baştan oynat"
butonuna bağlı; seans başlangıcına bağlanmalı.

- Ya da böyle de kalabilir sen karar ver.

### Çoklu seans birikimi

Kronometre modunda gün boyunca birden fazla seans yapılınca ebru katmanlanır:
her yeni seans önceki seansların izinin üstüne eklenir. Önceki izler hafif
soluklaşır (sabi/patina). Günün sonunda zengin, katmanlı bir ebru oluşur. Belki her kronometreyi başlattığında farklı renkler gelebilir ama çıkan sonucun güzel olması lazım bunu yapmak kolay değil bilmiyorum şu anda.

### Sınırsız süre — katman sistemi (ekranın statikleşme sorunu)

> Kaynak: kullanıcı bulgusu, 18 Ağustos 2026 — "Ebru modu bir yerden sonra
> statikleşiyor... kronometre modu çok daha uzun süreler durabilir, 67 saat
> bile durabilir." Çözüm: aynı gün, prototipte doğrulandı (`tasarim/akis.html`).

**Doğrulanan hata:** `tasarim/akis.html`'de alanın ne kadarının göründüğü
`oran = Math.min(1, dk/120)` ile hesaplanıyordu. 120. dakikadan (2 saat) sonra
`oran` hep 1'de kalıyor — yani ekran **tam olarak 2 saatte "bitiyor"** ve
kronometre saatlerce (67 saate kadar) sürse bile geri kalan hiçbir dakika
pikselde görünmüyor. Test: `dk=150` ve `dk=165` aynı tuvali (`toDataURL()`
hash'i) üretiyordu — ekran gerçekten donmuş. Bu, ürünün tek büyük iddiası olan
**dürüst kayıt**'ı bozan bir hataydı: 65 saatlik ek çalışma hiçbir görsel
karşılık bulmuyordu.

**Kök neden mimari:** Sabit boyutlu bir tuval (W×H, DSEP aralıklı ızgara)
fiziksel olarak yalnızca sınırlı sayıda çizgi barındırabilir — bu `120`
sabitini büyütmek sorunu ertelerdi, çözmezdi.

**Karar — katmanlı büyüme:** `DONEM` (120 dk, mevcut ritim korunuyor) dolunca
o katman tamamlanmış sayılır; aynı alanda **yeni bir tohumla yeni bir katman**
büyümeye başlar. Tamamlanmış katmanlar arkada kalır ve soluklaşır
(`yaş katsayısı = .55^yaş` — sabi/patina, yukarıdaki "Çoklu seans birikimi"
ile aynı aile, burada tek seans içinde). Ekran hiçbir zaman "bitmiş" olmuyor;
67 saatlik bir seansta 33'ün üzerinde katman üst üste biriken, zengin bir
desen oluşuyor — kavramsal olarak gerçek ebrunun fiziğine de daha sadık
(aynı teknenin üstüne art arda mürekkep damlatmak).

**Bu çözüm estetik olarak başarısız oldu — bkz. bölüm 3.5.** Donma teknik olarak
çözülmüştü ama 4020. dakikada 33 bağımsız akış alanı üst üste binince ortaya ebru değil
*moiré gürültüsü* çıktı (kullanıcının ifadesi: "hiç estetik değil, daha çok mide bulantısı
gibi"). Aşağıdaki uygulama notu tarihsel kayıt olarak duruyor.

**Uygulandı (eski):** `tasarim/akis.html` — `ciz()` ve `alanHesapla()` yeniden
yazıldı, `katmanCiz`/`katmanSeritleriAl`/`eskiyeSurukleTumunu` eklendi.
Bellek/performans için: son 6 katman (~12 saat) vektör olarak taze tutuluyor,
ondan eskisi tek bir raster'e mühürleniyor (zaten ~%3 opaklıkta, fark
edilmiyor). "67 saat (stres testi)" ön ayarı eklendi — kaydırıcıyı sona
sürükleyince ekranın donmadığı doğrudan görülebiliyor. Playwright ile
otomatik doğrulandı: eski dosyada dk=150/165 aynı, yeni dosyada dk=2000/4020
farklı tuval üretiyor.

**Not — dairesel kadran için ayrı, küçük bir risk:** `kadran()` fonksiyonu
saat başına bir halka ekleyip ölçeği küçülterek (`sc=140/(R0+(tur-1)*GAP)`)
zaten sınırsız süreyi destekliyor, donmuyor — ama 67 turda halkalar o kadar
küçülüyor ki saat çentikleri pratikte görünmez oluyor. Bu görsel donma değil,
okunabilirlik sorunu; ayrı ele alınmalı (örn. belli bir tur sayısından sonra
en eski turları da soluklaştırıp/gizleyip yalnız son birkaç turu göstermek).

---

### 3.5. KARAR — birikim değil **yer değiştirme** (18 Ağustos 2026, akşam)

> Kaynak: kullanıcı geri bildirimi — "4020 görseline bakıyorum da hiç estetik bir şey
> gözükmüyor, daha çok mide bulantısı gibi. Yani sanat değil." + "bunun bir damla ile
> başlaması fikrini de düşünebilirsin" + "gerçekten ebru olmasına gerek yok, bununla
> sınırlı kalma".
> Prototip: `tasarim/damla.html` + `tasarim/damla-cekirdek.js`.

**Teşhis — sorun katman sayısı değil, mimarinin kendisiydi.**
Akış çizgisi yaklaşımı *biriktirme* mantığındaydı: her dakika ekrana yeni işaret ekle.
Biriktirme mantığı sonlu bir tuvalde matematiksel olarak doymak zorundadır. `120` sabitini
büyütmek de, katman eklemek de doymayı erteler, kaldırmaz. Katman çözümü donmayı
kaldırdı ama yerine daha kötü bir şey koydu: birbirinden bağımsız 33 gürültü alanının
üst üste binmesi. Göz bunu kompozisyon olarak okuyamaz, **titreşim (moiré)** olarak okur —
fizyolojik olarak rahatsız edici olmasının sebebi tam olarak bu.

**Çözüm — tek atom: damla. Ekranda biriken değil, yer değiştiren bir kompozisyon.**

Teknede tek bir kompozisyon var. Yeni bir damla düştüğünde ekrana bir şey *eklenmez*;
teknedeki **her şey** dışa doğru itilir. Alan koruyan, kapalı formda, tersinir dönüşüm
(Jaffer, *Marbling Deformation Mathematics*):

```
damla:  P′ = C + (P−C)·√(1 + r²/|P−C|²)
tarak:  P′ = P + u·M·λ^(d/z)
```

Bunun dört sonucu var, dördü de tam olarak ürünün ihtiyacı:

1. **Statikleşme yapısal olarak imkânsız.** Doyacak bir "boş yer" kavramı yok. 4020.
   dakikada da her yeni damla bütün resmi yeniden düzenliyor. Ayrıca aktif damla
   iki damla arasında *sürekli büyüdüğü* için ekran dakikalar arasında da hareketsiz
   değil — ama saniyede bir kare değil, **tek bir sessiz akış**; seijaku bozulmuyor.
2. **Dürüst kayıt malzemenin içinde.** 20. dakikanın damlası 40. saatte hâlâ orada —
   incelmiş, kıvrılmış, kenara sıkışmış bir kılcal damar hâlinde. Sabi/patina ayrıca
   *eklenmiyor*, eskime dönüşümün kendi sonucu. `24-sanat-dili.md` §2.3 shizen kuralı
   ("doku çizginin kendi davranışından çıkmalı") ilk kez gerçekten sağlanıyor.
3. **Mola dağılımı resimden okunuyor** (`20-sanat-geri-bildirim.md` madde 3.1, öncelikli
   madde). Molada düşen damlalar serin tondan; iç içe halka sırasında nerede durdukları
   seansın hangi bölümünde mola verildiğini gösteriyor.
4. **"Gri çamur" sorunu ortadan kalktı** (`ebru-muhur.md` teknik kısıtı). Şekiller opak
   çiziliyor, kompozisyon düzleştirildikten *sonra* tek seferde saydamlaştırılıyor.
   Yarı saydam üst üste binme hiç olmuyor, dolayısıyla renkler griye düşmüyor.

**Damla ile başlamak: evet — ama süs olarak değil, atom olarak.**
Soru "açılışa bir damla animasyonu ekleyelim mi" idi; cevap daha güçlü çıktı: damla
zaten sistemin tek yapı taşı. İlk kare *zaten* bir damla olduğu için `20-sanat-geri-bildirim.md`
madde 1'deki **popping sorunu kendiliğinden yok oluyor** — çizim "küt diye belirmiyor",
çünkü belirecek bir çizim yok; damla düşüyor ve yayılıyor. Ayrı bir açılış animasyonu
yazmaya gerek kalmadı.

**"Ebru" bir zorunluluk değil — mekanizma malzemeden bağımsız.**
Aynı motor üç ayrı giydirmeyle çalışıyor (`damla.html` → *görünüm* seçicisi):

| Görünüm | Çizim | Karakter |
|---|---|---|
| **damar** (varsayılan) | sadece kontur, ince çizgi | Akik kesiti / eş yükselti eğrisi. Hafif, arka plan olarak en okunur, "kertik/damar" adıyla en tutarlı. `tasarim/akik-kesiti.html` ve `damar.html` denemeleriyle aynı aile. |
| **sıvı** | dolu opak şekil + ince kontur | Klasik ebru. En zengin, ama arka plan olarak en baskın. |
| **sis** | düşük opaklıkta dolgu + kontur | Mineral yıkama. İkisinin arası. |

**KARAR: `damar`** (kullanıcı onayı, 18 Ağustos 2026). Sebep: ürün "dürüst kayıt" iddiasında ve arka plan bir *arka plan*
olmalı; dolu renk kütlesi saatle yarışıyor. Damar görünümü ayrıca `12-isim-fikirleri.md`
ve "kertik" adıyla malzeme olarak akraba. `sıvı` ve `sis` prototipte duruyor —
ileride tema seçeneği olarak açılabilir, varsayılan değil.

**Zamanlama.** Damlalar `t(k) = A·k^1.28` anında düşüyor (A≈2.4 dk): başta sık — ekran
ilk dakikalarda canlanır; sonra seyrekleşir — 67 saatte tekne doymaz. Ağaç halkası
mantığı; 4× uzun seans ≈ 2× geniş kompozisyon. Tarak (şal dokusunu veren yapısal olay)
varsayılan 45 dakikada bir, tek seferlik.

**Performans notu.** Prototip her karede kompozisyonu sıfırdan kuruyor (4020 dk ≈ 1 sn).
Canlı uygulamada artımlı olmalı: durum saklanır, yalnız yeni olay mevcut şekillere
uygulanır → dakika başına O(nokta), ihmal edilebilir. Kadraj dışına çıkan şekiller
eleniyor (`pay`), şekiller uzayan kenarlara nokta ekleyerek kendini yeniden örnekliyor.

**Yan fayda — kadran okunabilirliği çözüldü.** Yukarıdaki "ayrı, küçük risk" (67 turda
çentiklerin görünmez olması) `damla.html`'de kapatıldı: ölçek küçültme kaldırıldı,
yalnız **son 3 tur** çiziliyor (en eskisi soluk), gizlenen turlar kadranın içinde sessiz
bir `+64 SAAT` satırı olarak duruyor. Çentik her saatte aynı büyüklükte kalıyor.

**Açık kalanlar.**
- 25 dakikalık seans ekranı çok boş bırakıyor. Dürüst ama fazla sessiz olabilir;
  `A`/`US` ile ayarlanabilir — kullanıcı kararı.
- Mola difüzyonu (bölüm 3'teki 3 kademe) bu motora henüz bağlanmadı. Karşılığı doğal:
  molada damla düşmez, aktif damlanın büyümesi yavaşlar/durur ve kompozisyon hafifçe
  bulanır.
- Canlı uygulamaya (`uygulama/www/index.html`) taşınmadı; orada hâlâ yalnız
  `drawStopwatchDial` var.

---

### Mola sırasında bozulma (kum bahçesindeki rüzgarın ebru karşılığı)

> Kaynak: `Notlarım.md`, 18 Ağustos 2026. Çözüm: 18 Ağustos 2026 sohbeti.

Şu anki uygulamada çalışma ve mola için iki ayrı renk kullanılıyor; bu zaten
`20-sanat-geri-bildirim.md` madde 3'te çiğ bulunmuştu. Renk değiştirmek yerine,
mola 10 dakikayı geçince ebrunun kendisi bozulmaya başlar. Bu, "dolan halka
yerine kertik" ilkesiyle aynı yönde: mola ayrı bir palet değil, aynı kaydın
bozulan hâlidir.

**Ama mekanizma kum bahçesindeki rüzgarın birebir kopyası değil.** Rüzgar
dışarıdan gelen bir kuvvet — kum için doğru, sıvı için değil. Ebru zaten
bırakıldığında kendiliğinden bir şey yapar: mürekkep pasif difüzyonla yayılmaya,
kenarları yumuşamaya devam eder. Dışarıdan güç gerekmez, malzemenin kendi fiziği
yeterli. Üç kademe:

1. **10–20 dk mola:** pasif difüzyon başlar — çizgilerin keskin kenarları
   yumuşar, mürekkep hafifçe genişler. Aktif bir "olay" değil, sessiz ve yavaş.
2. **20–40 dk mola:** difüzyona hafif solma (sabi/patina) eklenir — ince
   detaylar birbirine karışır, kompozisyon bulanıklaşır ama tanınmaz olmaz.
3. **40+ dk mola:** desatürasyon artar, çizim bir "hatıra" gibi kalır — net
   değil ama silinmiş de değil.

Kullanıcı devam edince yeni damla eskinin üstüne düşer, taze çizgiler bulanık
zeminin üstünde keskin başlar — kum bahçesindeki "yeni tırmık eski dağılmışın
arasından geçer" mantığıyla aynı aile.

**Ses/titreşim: bilerek asimetrik, eklenmiyor.** Rüzgar aktif ve algılanabilir
bir kuvvet olduğu için hışırtı + titreşim mantıklı (bkz. bölüm 4–5). Difüzyon
ise sessiz, kendiliğinden bir şey — ona ses veya titreşim eklemek malzemeyi
yalanlar. Kullanıcı ekrana döndüğünde bulanıklaşmayı görür ama bir "bildirim"
gibi duymaz; sanki hep böyleymiş gibi sessizce olmuş olur. Bu asimetri (kum
duyulur, ebru duyulmaz) iki modun "aynı dil ama başka bir şey" hissini
pekiştiriyor — simetri zorlanmıyor.

---

## 4. Titreşim (haptic)

`24-sanat-dili.md` bölüm 6.5'teki haptik sözlüğü geçerli. Ek olarak:

| Olay | His | Not |
|---|---|---|
| **Taş düşüşü** (kum) | Ağır, tek, derin — bir şeyin zemine çarpması | Diğerlerinden ayrışmalı, daha ağır |
| **Damla düşüşü** (ebru) | Hafif, tok — sıvıya temas | Taştan daha hafif, farklı karakter |

Genel kural değişmedi: **malzeme haptiği**, bildirim haptiği değil. 8–20 ms,
keskin, anında. Seans sürerken uygulama kendiliğinden titremez.

Ekran sallanması (`sars()` fonksiyonu) şu anki haliyle sanat anlayışına
uymuyor. Ya kaldırılacak ya da çok daha kısa/sert bir "yerleşme" hareketine
dönüştürülecek — sallama değil, tek bir bırakma.

**Ebru mola bozulması için haptic yok** (bkz. bölüm 3, "Mola sırasında
bozulma") — difüzyon sessiz ve kendiliğinden, bildirim gibi hissettirilmemeli.

---

## 5. Ses efektleri

`24-sanat-dili.md` bölüm 6.5'teki kurallar geçerli:
- Varsayılan **sessiz.** Açılabilir katman.
- **Melodik olmamalı.** Nota yok, akor yok. Yalnız maddi ses.
- Kaynak: gerçek kayıt, sentez değil.

Yapılacak sesler:

| Olay | Ses karakteri |
|---|---|
| Başlat | Kısa, net — kâğıda kalem teması |
| Mola | Yumuşak, sönümlenen |
| Bitir | İki vuruş, ikincisi hafif |
| Taş düşüşü (kum) | Taşın kuma konması — tok, kısa, kuyruksuz |
| Damla düşüşü (ebru) | Damlanın suya düşmesi — ince, kısa |
| Rüzgar (mola aşımı) | Hafif hışırtı — çok kısa |

Her biri 120–250 ms, düşük seviyeli, kuyruğu kısa. **Ebru mola bozulması
(difüzyon) sessiz** — kum bahçesindeki rüzgarın aksine ses eşlik etmiyor,
bilinçli asimetri (bkz. bölüm 3).

---

## 6. Gün batımı sıfırlaması

Gün sonunda ekranın sıfırlanması fikri var ama **MVP sonrasına** bırakılıyor.
İlk aşamada: yeni güne boş ekranla başla. Sıfırlama animasyonu (kumda rüzgarın
her şeyi silmesi? Ebrunun solup kaybolması?) sonraki versiyonda.

---

## 7. Mola süresi — nörobilim referansı

| Kaynak | Çalışma / Mola | Not |
|---|---|---|
| Pomodoro Technique (Cirillo) | 25/5, her 4'te 15-30 | Popüler ama bilimsel temeli zayıf |
| DeskTime araştırması (2014) | 52/17 | En üretken %10'un kalıbı |
| Ultradian döngü (Peretz Lavie) | ~90/20 | Biyolojik ritme dayalı |
| Genel konsensüs | 5–10 dk optimal | 10+ dk'da bağlamsal bellek çözülüyor |

Varsayılan rüzgar sınırı **10 dakika** doğru.

---

## Yapılacaklar (bu dosyadan çıkan)

- [ ] Kum bahçesini pomodoro moduna bağla (her pomodoro = taş)
- [ ] Taş boyutunu süreye göre kök oranıyla ölçekle
- [ ] Rüzgar mekaniğini implemente et (tek seferlik, sonlu animasyon)
- [x] Ebru damla doğuşu animasyonu → damla artık sistemin atomu (`tasarim/damla.html`, bölüm 3.5)
- [ ] Kum bahçesi taş düşüş animasyonunu iyileştir (premium kalitede)
- [x] Popping sorununu damla doğuşuyla çöz → yapısal olarak çözüldü (bölüm 3.5)
- [ ] Taş düşüşü ve damla düşüşü için haptic ekle
- [ ] Ekran sarsıntısını gözden geçir / kaldır
- [ ] Ses efektlerini üret ve entegre et
- [x] Duvar kısmında taş sayısı görünümü (düz kayıt, ödül değil) — 18 Ağustos
      2026'da "hesap taşları" kompozisyonuyla uygulandı, yukarıdaki alt bölüme
      bakın. Kalan iş: tekil seans kartındaki çubuk hâlâ pomodoro için de
      çubuk çiziyor, orası ayrışmadı.
- [ ] Çoklu seans birikimi — yeni motorda karşılığı: gün içindeki ikinci seans aynı teknenin üstüne devam eder
- [x] Görünüm seçildi: **damar** (18 Ağustos 2026)
- [ ] Damla motorunu canlı uygulamaya taşı (artımlı hesapla)
- [ ] Gün batımı sıfırlama animasyonu (MVP sonrası)
- [ ] Ebru için mola bozulma mekaniğini implemente et (pasif difüzyon,
      3 kademe: 10–20 / 20–40 / 40+ dk — bkz. bölüm 3, ses/haptic yok)
