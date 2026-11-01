# 33 — Denetim: "içine sinmeyen ne var?" (24 Ağustos 2026)

> Soru: *"Uygulamaya bak, içine sinmeyen bir şey var mı; stabil ve premium
> hissettiriyor mu?"*
>
> Yöntem: `kertik-android/app/src/main/assets/index.html` headless Chromium'da
> (Playwright, 412×915 @2x, mobil dokunma) baştan sona kullanıldı — kronometre
> ve pomodoro, açık ve koyu, tr / de / ar (RTL), 360×640 küçük ekran; seans
> başlat → mola → devam → bitir → ölçü → özet → kayıt → görevler → ayarlar.
> Zaman `Date.now` üzerinden ileri sarıldı. Konsol ve `pageerror` dinlendi.

**Kısa cevap: stabil, evet. Premium, henüz tam değil.** Tek bir gerçek hata
buldum; geri kalanı "aynı özenin her ekrana ulaşmamış olması".

---

## A. Gerçek hatalar

### A1. Açılışta sekme değiştirilirse ebru diğer sayfaların altında kalıyor

**En somut hata bu.** Uygulama açıldıktan **~0,9 – 4 saniye** sonrasına kadar
`akisTanitim()` çalışıyor. Bu pencerede kullanıcı alta dokunup *kayıt* /
*görevler* / *ayarlar*'a geçerse ebru tuvali `opacity:1` ile açık kalıyor ve
sayfa metni koyu ebru girdaplarının üstünde okunmaz hale geliyor. Kendi kendine
~4 sn'de düzeliyor, ama açılışın ilk saniyeleri tam da sabırsız kullanıcının
sekmeye bastığı an.

Kök neden: `akisTazele()` başında `if (AK.tanit) return;` var (satır ~5144) —
tanıtım sürerken tuvalden `on` sınıfı **hiç kaldırılmıyor**. `akisTanitim()`
yalnız *başlarken* `tab !== "timer"` kontrolü yapıyor, başladıktan sonra sekme
değişimini umursamıyor.

Ölçüm (sekmeye geçiş anı → 2,5 sn sonraki tuval durumu):

```
 860 ms → on:true  opacity:1     3000 ms → on:false opacity:0
 900 ms → on:true  opacity:1     4000 ms → on:false opacity:0
1200 ms → on:true  opacity:1     5000 ms → on:false opacity:0
1500 ms → on:true  opacity:1
2000 ms → on:false opacity:0.96  (geçiş)
```

Öneri: sekme değişiminde (`tab` değişince) `tanitKapat()` çağır, ya da
`akisTazele()`'deki erken dönüşü `if (AK.tanit && tab === "timer") return;`
yap.

### A2. Ölçü sorusu her seans sonunda soruluyor

`showSummary()` içinde koşul `if (se.olcu === undefined) askOlcu(se);` —
ölçü **seansa** takılı olduğu için her yeni seansın `olcu`'su `undefined`.
Yani "hayır" demek o seansı kapatıyor, bir sonraki seansta soru yine geliyor.
Doğruladım: art arda iki seansta da sordu.

`31-seans-ciktisi.md` §9 ise açıkça şöyle diyor:

> **Hayır** (varsayılan, tek dokunuş, **bir daha sorulmaz**)

Karar ile kod ayrışmış. Bunun ağırlığı şu: hiçbir şey saymayan bir kullanıcı —
yani `02-urun-vizyonu.md`'deki "anne profili" — her seans sonunda ömür boyu
fazladan bir dokunuş yapıyor. `CLAUDE.md`'deki "uğraştırmayacaksın" ilkesinin
tam karşısı.

Ayrıca **ayarlarda kapatma yok.** Uygulamadaki diğer iki kesinti (*uzun mola
sorusu*, *seans sonu sorusu*) ayarlardan kapatılabiliyor; bu üçüncüsü
kapatılamıyor ve tek zorunlu olan o.

En küçük yama: kullanıcı bir kez "hayır" dediyse `S.settings.olcuSorma = true`
yaz, bir daha sorma (isteyen ayarlardan geri açsın). Ç7 (kalıcı `subject`)
kurulunca zaten ölçü işe taşınacak.

### A3. On dilde ölçü ekranı yarı İngilizce çıkıyor

`SOZLUK` 12 dil taşıyor. `tr` ve `en` 217 anahtar, **diğer 10 dilin hepsinde
aynı 10 anahtar eksik**: `olcu_baslik`, `olcu_hayir`, `olcu_sayfa`,
`olcu_soru`, `olcu_sayfa_soru`, `olcu_soru_baslik`, `olcu_soru_dogru`,
`olcu_soru_yanlis`, `olcu_soru_bos`, `btn_olcu_atla`.

`soz()`'ün geri düşüşü tek tek anahtar bazında çalıştığı için sonuç *tamamen
İngilizce* değil, **karışık** bir ekran oluyor. Almanca'da gerçekte gördüğüm:

> **how many questions?**  ·  correct / wrong / blank  ·  **speichern**  ·  skip

Tamamı İngilizce olsa "çeviri eksik" derdi kullanıcı; karışık olunca "bozuk"
diyor. Almanca ekranın ekran görüntüsü ekte.

### A4. Duvarda bir günün çubuğu komşu güne taşıyor

`cizCubuk`'ta `kolon = ceil(dk/60)` ve `satir = kolon > 1 ? 60 : dk`. Sonuç:
**60 dakikayı geçen her gün aynı yükseklikte.** 62 dk da, 200 dk da 137,8 px
(ölçtüm). Fark yalnız sütun sayısında — ki bu kavramsal olarak doğru (her
sütun bir saatlik çentik kalası). Ama sütunlar `.day`'in 54 px'ini taşıyor:
4 sütun ≈ 88 px. Kalaslar komşu günün üstüne biniyor, hangi çubuğun hangi güne
ait olduğu okunmuyor — özellikle "bugün" çizgisinin sağına düşen kalas kafa
karıştırıyor.

Ayrıca duvar 30 gün ve yatay kayıyor, ama **kaydırılabildiğine dair hiçbir
işaret yok** (kenar solması, tutamak, hiçbir şey). Kullanıcı 30 günün var
olduğunu öğrenemiyor.

### A5. Gösterge üç renk vaat ediyor, çubuk bir renk gösteriyor

`lgnd_calisma / lgnd_mola / lgnd_sayilmayan` her zaman basılıyor. Ama 9 dk
molası olan 1 saatlik seansta mola işareti neredeyse görünmez soluk bir gri
oldu; "çalışmaya sayılmayan" ise hiç oluşmadığı için göstergedeki kırmızı
kesikli çizginin karşılığı ekranda yok. Boş gösterge satırı, `24-sanat-dili.md`
"KPI panosu yasağı"na da ters düşen bir veri-grafiği tonu getiriyor.

Öneri: göstergeyi statik basma; o duvarda gerçekten çizilmiş türleri say,
yalnız onları göster (mola yoksa mola satırı çıkmasın).

### A6. "günlük ortalama" 7'ye değil, çalışılan gün sayısına bölünüyor

`renderLog()` içinde `wdays` bir `Set` — ortalama **çalışılan güne** bölünüyor.
Etiket ise "son 7 gün {a} · günlük ortalama {b}". Gerçek çıktı:
*"son 7 gün 5s 30dk · günlük ortalama 1s 50dk"* — kullanıcı 5s30/7 = 47dk
bekliyor. Ya etiket "çalışılan günde ortalama" olmalı, ya bölen 7.

Uç durum daha da tuhaf: tek gün çalışılmışsa *"son 7 gün 1 saat · günlük
ortalama 1 saat"* çıkıyor; aynı sayının iki kez yazılması hatalı görünüyor.

### A7. Almanca'da alt gezinti kenara yapışıyor

`einstellungen` ekranın sağ kenarına değiyor, sağ boşluk kalmıyor. Dört uzun
etiketli dillerde gezinti taşıyor.

---

## B. "Premium hissettiriyor mu?" — ayrışmalar

### B1. Pomodoro'ya geçince sanat tamamen kayboluyor

En keskin an bu. `akisTazele()` (satır 5147): seans yokken kum bahçesi
**yalnız o gün pomodoro seansı varsa** çiziliyor. Kronometrede ebru her zaman
var. Yani kullanıcı ilk açılışta üstteki anahtara dokunuyor ve dolu, dokulu,
etkileyici bir ekrandan **tamamen boş siyah/krem bir ekrana** düşüyor. Aynı
şey her sabah tekrarlanıyor (gün dönünce taşlar sıfırlanıyor).

Kararın mantığı anlaşılıyor (bahçe o günün taşlarıdır), ama bedeli ilk temas
anında ödeniyor. Boş bahçenin de bir hâli olmalı: taşsız, sadece tırmıklanmış
kum. `kumTanitim()` zaten var — boşta da (yalnız açılışta değil) kalıcı
tırmık deseni bırakabilir.

### B2. Sanat yalnız sayaç sekmesinde; diğer üç sekme başka bir uygulama

Görevler / kayıt / ayarlar düz krem zemin, gri dolgulu jenerik `input`,
siyah "ekle" hapı. Sayaç ekranındaki kâğıt-mürekkep dili oraya hiç geçmemiş.
Özellikle **görevler boş hâli**: tek bir cümle ("bugün için iş yok.") ve
altında ekranın %70'i boşluk. `ma` (boşluk) bilinçli olabilir ama burada
"bitmemiş" okunuyor — sayaçtaki `ph_ne_calisiyorsun` alt çizgili zarif
alanıyla, buradaki gri kutu aynı elden çıkmış gibi durmuyor.

### B3. Sheet perdesi sıcak kâğıdı ölü haki tona çeviriyor

Özet/soru sheet'i açılınca arkadaki krem zemin çamurlu bir haki-griye dönüyor
ve **ebru tamamen kayboluyor**. Üstelik `#modeSeg` (kronometre/pomodoro)
perdenin üstünde tam parlaklıkta kalıyor — özet ekranındaki en yüksek
kontrastlı öğe, kullanıcının bakması gereken sheet değil, mod anahtarı oluyor.

Ayrıca sheet'in üst kenarı arkadaki metni **ortadan kesiyor** ("bugün 1s 8dk ·
1 seans" yarısı görünüyor). Perde yerine hafif karartma + arkaplanın hafifçe
küçülmesi (ya da sheet'in metin çizgilerine oturması) bu anı toparlar.

### B4. Kertik çubuğu — ödül anı, ince bir şerit gibi duruyor

Seans özetinde çubuk ~35 px genişliğinde, sayfanın ortasında ince uzun bir
şerit. Uygulamanın duygusal ödülü bu; ekranda en zayıf duran şey de bu.
1s25dk'lık seansta iki eşit olmayan sütun çıkıyor ve sol sütunun dibine kopuk
gri bir dikdörtgen (mola işareti) düşüyor — kalasın dışında durduğu için hata
gibi görünüyor.

### B5. Kırık taş özette dağılıyor

Pomodoro yarıda bırakılınca özetteki taş sağa kaçık duruyor ve **soluna kopuk
bir elips** (gölge) düşüyor — taşla hizalı değil. Dahası: bahçedeki taş
3B gölgeli/dokulu, özetteki taş düz kesme-kâğıt. `kum-bahcesi-krater.md`
Kural 3 aynı derdi tırmık/krater için çözmüştü ("aynı kalem"); taşın kendisi
iki ayrı kalemle çiziliyor.

### B6. Koyu modda sheet mavimsi, uygulama nötr siyah

Sheet zemini lacivert-gri, sayfa zemini nötr siyah. Yan yana iki palet
görünüyor.

### B7. Pomodoro'da tek eylem, en zayıf görünürlükte

Pomodoro sürerken ekrandaki tek dokunulabilir şey "bitir" ve o da hayalet
metin — çerçevesiz, düşük kontrast, ortada asılı. Kronometrede dolu hap +
hayalet ikili var, denge oturuyor. Pomodoro'da tek eylemin en silik eleman
olması hem tuhaf hem tereddüt yaratıyor.

### B8. Küçük ayrıntılar

- **Açık modda ebru**, koyu modun yanında çamurlu: lacivert mürekkep krem
  üstünde kirli gri okuuyor. (`28-acik-fikirler-ve-hatalar.md` madde 2 —
  hâlâ geçerli, koyu modu gördükten sonra fark çok daha net.)
- **Ayarlarda seçili segment saf beyaz** (`#fff`). Palette hiçbir yerde saf
  beyaz yok; kâğıt tonunun yanında parlıyor.
- Ayarlarda üst üste üç kiremit kırmızısı anahtar, sakin paletin içinde
  "uyarı" tonu gibi okunuyor.
- Kayıt listesi alt gezintinin altına giriyor, alt boşluk yok — son satır
  ortadan kesiliyor.
- 360×640'ta seans notu alanı ekranın en altına sıkışıyor, alt güvenli alan
  payı kalmıyor.
- `28-acik-fikirler-ve-hatalar.md` madde 1 (**sağ bardaki ölü "tablo/görev"
  öğesi**) bu sürümde **yok** — kodda hiçbir karşılığı kalmamış. O madde
  kapatılabilir.

---

## C. İyi olan, dokunulmaması gereken

- **Sıfır konsol hatası, sıfır `pageerror`** — tüm akışlar boyunca.
- **Performans temiz.** Ölçtüm: `akisTazele()` ort. **0,01 ms**,
  `renderTimer()` ort. **0,62 ms**, kum bahçesi tazeleme **0,03 ms**.
  Saniyede bir dönen döngü hiçbir şeye mal olmuyor; damga kontrolü işini
  yapıyor. "Ekran açık kalsın" varsayılan açıkken bile pil derdi yok.
- **RTL kusursuz.** Arapça'da hap/hayalet ikilisi, tarih, saat, çubuk —
  hepsi doğru aynalanıyor. Çoğu uygulamanın beceremediği yer burası.
- **Molada renk çekilmesi.** Kırmızı çentiklerin molada griye düşmesi,
  uygulamanın en iyi tek hamlesi. Anlatmadan anlatıyor.
- **Koyu mod ebrusu** gerçekten güzel; uygulamanın en güçlü ekranı.
- **Ayarlar sayfası** oturmuş: gruplama, alt açıklamalar, segment seçiciler.
- Seans özeti dili ("mola: 8dk (1 kez)") ölçülü, övmüyor, yargılamıyor.

---

## D. Sıra önerisi

| # | İş | Neden önce |
|---|---|---|
| 1 | A2 — ölçü sorusunu bir kez sor | Her seansta her kullanıcıya değiyor |
| 2 | A3 — 10 dilde 10 anahtar | Karışık dil "bozuk" okunuyor; yarım saatlik iş |
| 3 | A1 — tanıtım sızması | Açılışın ilk saniyeleri, kolay yama |
| 4 | B1 — boş pomodoro ekranı | İlk temasta sanatın kaybolduğu tek an |
| 5 | A4 + A5 + A6 — duvar | Kayıt sekmesinin tamamı bundan ibaret |
| 6 | B3 + B4 — sheet perdesi ve çubuk ölçüsü | Ödül anının kendisi |
| 7 | B2 — diğer üç sekmeye sanat dili | Büyük iş, ayrı bir tur |

---

## E. Denetlenmeyenler

- Gerçek cihazda görsel/haptik his (emülatörde anlamsız).
- Native katman (`kt/*.txt` bu turda tazelenmedi; `30-stabilite-denetimi.md`
  §4'teki doğrulama son durum sayılıyor).
- Widget ve bildirim çıktıları.
- Google senkron akışı (native köprü gerekiyor).
- `test/` paketi koşturulmadı (bu turda stajlanmadı).
