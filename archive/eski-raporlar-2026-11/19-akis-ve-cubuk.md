# 19 — Akış ve Çubuk uygulamaya geçti

`tasarim/akis.html` ve `tasarim/cubuk.html` iki ayrı denemeydi. İkisi de uygulamaya
girdi. Bu dosya, demodan uygulamaya geçerken nelerin **değiştiğini** ve neden
değiştiğini anlatıyor — demoların kendisi olduğu gibi duruyor, karşılaştırmak
isteyince açılabilir.

Kaynak: `kertik-android/app/src/main/assets/index.html`.

---

## Akış — seans sürerken arkada oluşan alan

Seansın kimliğinden türeyen bir akış alanı. Aynı seans her açılışta aynı deseni
verir; başka seans başka desen. Dakikada bir grup çizgi ekleniyor, ekranda hiçbir
şey oynamıyor — sadece sessizce kalabalıklaşıyor. Mola dakikaları serin renkte ve
seyrek.

**Ne zaman görünür:** yalnızca seans sürerken, yalnızca Sayaç sekmesinde. Boş
ekran eskisi gibi sade. Seans bitince 1.1 saniyede soluyor. Ayar yok — açıp
kapatılacak bir şey değil, seansın kendisi.

### Demodan farklar

| Demo | Uygulama | Neden |
|---|---|---|
| Her dakika alanın tamamı baştan çiziliyor | Çevrimdışı bir tuvale **artımlı** çiziliyor, ekrana `drawImage` ile basılıyor | Dakikada bir 400 şeridi baştan çizmek telefonda pahalı. Artımlı çizimde dakikada sadece ~3 yeni şerit çizilir |
| Saydamlık her çizgi parçası için ayrı ayrı hesaplanıp `stroke` ediliyor | Şerit tek yolda çiziliyor, kadranın çevresi ve alt şerit sonradan **gradyanla siliniyor** (`destination-out`) | Aynı görüntü, binlerce `stroke` yerine bir `fillRect`. Görsel sonuç birebir: demodaki `a *= (d-ic)/(dis-ic)` formülünün tam karşılığı radyal gradyan |
| `dakika = i/toplam*120` ile mola aralığı sabit veriden okunuyor | Aynı eşleme, ama mola bilgisi **gerçek seans olaylarından** (`segments()`) geliyor | Şeritler dakika sırasına göre çizildiği için, bir şerit çizilirken o dakikanın mola olup olmadığı zaten kesin |
| `DSEP=3.4`, tuval 330×715 | `DSEP=3.2`, tuval 300×(ekran oranı) | Komşuluk taraması 3×3 olduğu için gerçek şerit aralığı ~3×DSEP'e oturuyor. 300 birimlik tuvalde demodaki yoğunluğu vermek için 3.2 gerekiyor |
| Yoğunluk ayarı var | Yok | Demoda "nereye kadar gidilebilir" diye duruyordu, zaten uygulamaya girmeyecekti |

### Maliyet

Alan seans başına bir kez hesaplanıyor, `setTimeout(...,60)` ile — yani önce
arayüz boyanıyor, sonra hesap yapılıyor, kullanıcı takılma görmüyor.

Ölçüm (Node, 300 birim genişlik): 500 birim yükseklikte 11 ms, 640'ta 30 ms,
760'ta 32 ms. Telefonda 5–10 kat yavaş varsayılsa bile 300 ms civarı.

Yine de bir güvenlik kapısı var: hesap **1400 ms'yi geçerse** o cihazda akış
tamamen kapanıyor (`AK.kapali`) ve bir daha denenmiyor. Uygulamanın geri kalanı
akış olmadan da aynen çalışır.

Dakikalık iş: ~3 şerit çiz + bir `drawImage` + iki gradyan. Yok denecek kadar az.

Tema değişince renkler alana işlenmiş olduğu için alan baştan çiziliyor
(`akisYeniden`). Katlanabilir telefon açılıp kapanınca en boy değiştiği için alan
yeniden hesaplanıyor.

---

## Çubuk — seansın kaydı, çentikten

Dakikada bir kesik, her saat yeni bir sütun. Mola kesik bırakmaz, sütunun solunda
serin bir iz bırakır. Kesikler seansın kendi verisinden çıkıyor: aynı seans her
zaman aynı çubuğu verir.

### Nerede

1. **Seans sonu özeti** — kazınma animasyonuyla. Çubuğun asıl yeri burası:
   "seans bitince ortaya çıkan kayıt" tam olarak bu an. Eski kadran kaldırıldı.
2. **Kayıt sayfası, seans kartı** — kart açılınca kadran yerine çubuk çizilir.
3. **Kayıt sayfası, duvar** — sayfanın başında son 30 gün.

Sayaç ekranındaki canlı kadran **duruyor**. Çubuk bir kayıt biçimi, sayaç değil;
akan bir seansı okumak için kadran hâlâ daha iyi.

### Sayılmayan süre — tek gerçek tasarım kararı

Demoda "şüpheli süre" belli bir dakika aralığıydı (`supheli:[[95,118]]`) ve
çubuğun o bölümü kesikli çiziliyordu. Uygulamada bu **mümkün değil**, çünkü veri
öyle değil: kullanıcıya seans sonunda "molaya basmayı unuttuğun bir bölüm oldu
mu?" diye soruluyor ve cevap bir **miktar** oluyor — "yaklaşık 30 dakika". Nerede
olduğu sorulmuyor, bilinmiyor.

O yüzden çubuğun herhangi bir yerini kesikli çizmek uydurma olurdu. Bu projenin
tek büyük fikri dürüst kayıt; görselin de yalan söylememesi gerekiyor.

Çözüm: sayılmayan süre çubuğa hiç yazılmıyor. Son sütunun sağında, boyu o kadar
dakika olan **kesikli bir ray** duruyor. Miktarı söylüyor, konum iddia etmiyor.
Çubuğun kendisi zaman çizgisi olarak bozulmadan kalıyor.

### Gün çubuğu (duvar)

Bir günde birden fazla seans varsa hepsi tek çubukta, başlangıç saatine göre sırayla.
Seanslar arasına **bir dakikalık boşluk** konuyor: o dakikaya kesik atılmıyor,
mola izi de çizilmiyor. Seanslar arası geçen gerçek süre çizilmiyor — çünkü o
süre hiçbir seansa ait değil, onu çizmek de bir iddia olurdu.

Çalışılmayan gün boş bir çizgi. Ödül yok, seri yok — sadece durduğu yerde duran kayıt.

---

## Kâğıt dokusu — denendi, kaldırıldı

`cubuk.html`'deki alaca + lif + tarama katmanı bir süre tüm ekranlara girdi,
sonra çıkarıldı. Sebep teknik değil: ekranı yaşlandırıyor, renkleri
soluklaştırıyordu. Zeminler yeniden düz.

Kod tamamen silindi (`kagitDoku`, `#paper` katmanı, alt gezintinin saydam
zemini geri alındı). Denemesi `tasarim/cubuk.html`'de duruyor.

Buradan çıkan yön: **daha canlı, daha doygun renk.** Palet arayışı
`tasarim/simulator.html` üzerinden yürüyor — orada beş palet canlı denenebiliyor.
Karar verilince uygulamanın `:root` bloğuna işlenecek.

---

## Yol boyunca çıkan bir hata

Betiğin sonunda v2.2'den kalma, artık tanımlı olmayan bir yardımcıya çağrı vardı.
Her açılışta hata fırlatıyor ve **altındaki üç senkron kancasını** hiç
kaydettirmiyordu:

```
autoSync(true);                       ← hiç çalışmıyordu
visibilitychange → autoSync()         ← hiç bağlanmıyordu
online → autoSync()                   ← hiç bağlanmıyordu
```

Yani Drive senkronu ne uygulama açılırken, ne öne gelirken, ne de internet geri
gelince kendiliğinden çalışıyordu; yalnız elle "şimdi eşitle" ve seans bitişindeki
`setTimeout` çalışıyordu. Ölü göç kodu silindi, kancalar geri geldi.

Bu, akış/çubuk işiyle ilgisi olmayan, önceden var olan bir hataydı.

---

## Simülatör

`tasarim/simulator.html` — hızlandırılmış bir tezgâh. Çift tıklayıp açılıyor,
kurulum yok.

**İçindeki uygulama kopya değil, derlenen dosyanın kendisi.** Simülatör elle
yazılmıyor, üretiliyor:

```
node tasarim/olustur-simulator.js
```

Uygulamada bir şey değişince bu komut yeniden koşturulur. Kopya tutulsaydı
sessizce ayrışır ve bir süre sonra yalan söylemeye başlardı; testlerden biri
gömülü metnin kaynakla birebir olduğunu kontrol ediyor, ayrışırsa kırılıyor.

### Nasıl çalışıyor

Uygulamanın kodunda **tek satır değişmiyor**. Uygulamanın betiğinden önce bir
kabuk koşuyor ve üç şeyi değiştiriyor:

| Ne | Neden |
|---|---|
| `Date` — sanal saat | Uygulama zamanı hep `Date.now()`'dan okuyor; saati biz sürünce seans da hızlanıyor |
| `setInterval(…, 1000)` | Uygulamanın saniyelik işi gerçek saniyeye değil **sanal** saniyeye bağlanıyor, yoksa 300× hızda saniyede bir kez güncellenirdi. `setTimeout`'a dokunulmuyor — onlar animasyon işleri, gerçek kalmalı |
| `localStorage` — hafızada | Gerçek tarayıcı deposuna hiç dokunulmuyor. Açılışta 30 günlük sahte kayıt geçmişi üretilip oraya konuyor |

Kare başına en çok bir sanal dakika ilerleniyor; yoksa çok yüksek hızda tek
karede on dakika atlanıp mola/bitiş anları o kabalıkta kayıyor.

Senaryolar uygulamayı dışarıdan sürmüyor — **gerçek düğmelerine basıyorlar**
(`#bStart`, `#bBrk`, `#bRes`, `#bEnd`). Yani seansı senin bastığın gibi
başlatıyor, molaya sokuyor, bitiriyor. Bitişte uygulamanın dürüstlük sorusu
çıkarsa hız duruyor, cevabı sen veriyorsun.

Panel ile çerçeve `postMessage` ile konuşuyor; dosyadan çift tıklayıp açtığında
da çalışsın diye çerçeve `about:blank` üstüne `document.write` ile kuruluyor.

Paletler yalnız simülatörde: uygulamanın CSS değişkenlerini canlı eziyor. Kadran
çentiği, akış alanı, çubuk — hepsi aynı iki renkten besleniyor (çalışma ve mola),
o yüzden iki rengi değiştirmek bütün uygulamayı değiştiriyor.

---

## Testler

İki dosya, ikisi de jsdom'da koşuyor — tarayıcı indirmeye gerek yok. Tuval sahte
bir nesneyle taklit ediliyor, çünkü doğrulanan şey piksel değil, üretilen geometri.

```
cd kertik-android/test
npm install jsdom
node hepsi.js --hizli        # tarayıcı gerektirmeyen hepsi
```

`test-cizim.js` — 50 test, çubuk/duvar/akış.
`test-simulator.js` — 27 test, simülatörü gerçekten açıp uygulamayı sanal saatle
sürüyor: hız ilerletiyor mu, senaryo gerçek düğmelere basıyor mu, çıkan seansın
uzunluğu senaryoyla uyuşuyor mu, palet uygulanıyor mu, gerçek depoya sızıyor mu.

Neyi tutuyor:

- çubuktaki çentik sayısı çalışma dakikasıyla birebir (mola dakikasına kesik atılmaz)
- aynı seans hep aynı çubuk, başka seans başka çubuk
- sayılmayan süre tek bir dikey kesikli ray, sütunun sağında, zaman çizgisini bozmuyor
- gün çubuğunda seanslar arası boşluk dakikası çentik almıyor
- duvar 30 gün çiziyor, boş günde çubuk yok, bugün işaretli
- kayıt kartında kadran değil çubuk var
- akış alanı aynı tohumda aynı, koordinatlarda NaN yok
- seans yokken akış tuvali kapalı, seans başlayınca açılıyor, bitince kapanıyor
- tema değişimi patlamıyor
- **betik sonuna kadar koşuyor** — yukarıdaki hatanın tekrarını yakalar
- simülatöre gömülü uygulama kaynakla birebir — ayrışırsa kırılır
