# 34 — Görev Ölçüsü ve Hedef: "seans hangi işe yazıldı"

> Soru (27 Ağustos 2026): *"Görevler kısmı var ama başlık olarak ekliyoruz;
> seans bittiğinde hangi görevi ve nasıl yaptığımızı seçemiyoruz. Görev olarak
> 'şu konudan şu kadar soru çözme' ya da 'şunu şuraya kadar okumak' desek?
> Seans sonunda görevin bitip bitmediğini seçeriz — sadece bitmeli değil, devam
> da edebilir. Hedefim o gün 300 soru, seans sonunda 200 çözmüşüm, onu girerim."*
>
> Zemin: `31-seans-ciktisi.md` (ölçü/künye kararı ve §9'daki geçici köprü),
> `04-cozum-gorevler.md` (durum modeli, gün sonu ritüeli, kasten yapılmayanlar),
> `08-veri-modeli.md` (olay listesi, sayılar türetilir),
> `24-sanat-dili.md` (wabi-sabi anayasası), `05-ozellik-listesi.md`,
> `CLAUDE.md` (uğraştıran ya da bitmemiş görünen özellik eklenmez).

Tarih: 27 Ağustos 2026 · Durum: **uygulandı** (bkz. §7)

---

## 1. Bu yeni bir yön değil, yazılı bir borcun ödenmesi

`31-seans-ciktisi.md` §1 ölçünün **işin** özelliği olması gerektiğini söylüyordu.
§9 ise uygulamada bunun kurulamadığını itiraf ediyordu: `tasks` günlük nesneler,
kalıcı bir `subject` yok, o yüzden ölçü geçici olarak **doğrudan seansa** takıldı.

Kullanıcının "hangi görevi yaptığımızı seçemiyoruz" dediği şey tam olarak o
eksik ayaktır. Bu dosya o ayağı kuruyor — ama `subject` tablosunu (Ç7)
kurmadan, mevcut günlük `task` nesnesinin üzerinden.

Kullanıcının eklediği yeni şey ise ölçü değil **hedef**tir.

---

## 2. Karar

> **Ölçü seansın değil GÖREVİN özelliğidir. Hedef ölçünün isteğe bağlı ekidir.
> Seans yalnız o ölçüye bir katkı yazar. Görevin durumu artık seçilmez, girilen
> sayıdan türer.**

Görev nesnesine iki alan eklendi, ikisi de geriye dönük uyumlu:

| Alan | Tip | Not |
|---|---|---|
| `olcu` | enum | `yok` (varsayılan) \| `sayfa` \| `soru` |
| `hedef` | int? | opsiyonel; ölçüsü olup hedefi olmayan iş meşrudur |

Seans nesnesine tek alan: `taskId` (null olabilir).

### Neden bu, "bitti/olmadı" menüsünü büyütmüyor — küçültüyor

Asıl gerekçe bu. Bugünkü akış: görev satırına dokun → altı seçenekli sayfa →
bitti/olmadı/taşındı seç → "olmadı" ise ayrıca sebep sorulur.

Yeni akış: seans sonunda zaten girdiğin `▲200` sayısı görevin durumunu **kendisi
söyler**. 200 < 300 ise `yapiliyor`, 300'e varılmışsa `bitti`. Kullanıcı bir
karar daha vermiyor, bir karar **eksik** veriyor. `CLAUDE.md`'nin tek cümlesini
("uğraştırıcı bir şey çıkarıyorsa eklemem") geçen tek sürüm budur.

Menü yerinde duruyor: türetme bir zorlama değil, bir kolaylık. Kullanıcı üzerine
yazabilir.

---

## 3. Kritik hamle: iki ölçünün doğası farklı, taşınmaları da farklı

Kullanıcının sorusunda iki ayrı şey iç içe geçmişti ve mekanizmaları zıt:

- **Günlük kota** — "bugün 300 soru". Bitmezse yarına *taşınmaz*; yarının kendi
  300'ü vardır. Kalanı taşımak hedefi çift sayar.
- **Kapsam hedefi** — "kitabı 120. sayfaya kadar". Biter, taşınır, birikir.

Bunu kullanıcıya soran bir ekran **eklenmedi**. Gerek yok: ayrım zaten ölçünün
türünde saklı.

| Ölçü | Doğası | Taşınınca |
|---|---|---|
| `soru` | **adet** — günlük kota | hedef aynı kalır, sayaç sıfırdan başlar |
| `sayfa` | **imleç** — kapsam | imleç zincir boyunca korunur, hedef sabit sayfa |

Sayfanın zincir boyunca korunması, `31 §5`'in *"s.52'de kaldın"* yer imini
kalıcı bir `subject` olmadan da yürürlüğe sokuyor: taşınan görevin künyesinde
ve başlat ekranındaki bağ satırında görünüyor. Kullanıcı hiçbir yerde çıkarma
yapmıyor.

> Zincir yeni bir alan gerektirmedi: `movedFromId` zaten vardı, geriye doğru
> yürünüyor.

---

## 4. İlerleme saklanmıyor, türetiliyor

`08-veri-modeli.md`'nin altın kuralı korundu. Görevde ilerleme alanı **yok**.

- `soru` → `taskId`'si o görev olan seansların `(correct+wrong+blank)` toplamı.
  Üç alandan hiçbiri girilmemişse o seans hiç sayılmaz (boş bırakılan seans
  eksik değildir, sadece ölçüsüzdür).
- `sayfa` → zincirdeki seansların **en son** `page` imleci.

Seans silinirse ilerleme kendiliğinden düzelir; ikinci bir defter tutulmuyor.

---

## 5. Akış (tam metin)

**Görev eklerken:** hiçbir şey değişmedi. Tek satır, tek dokunuş, ölçüsüz görev.
Özellik kendini göstermiyor.

**Ölçü ve hedef koymak:** görev satırına dokun → menüde `ölçü ve hedef` →
*hayır · sayfa · soru* → sayı. Sayı adımı her zaman `boş geç` ile atlanabilir.

**Başlat ekranı:** not alanının altında **tek satır**:
`bugünkü işler` → dokununca bugünün açık işleri sayfa olarak açılır → seçilince
satır `Matematik denemesi ×` olur. Sayfa ölçülü işte `· s.52'de kaldın` eklenir.
Bugün açık iş yoksa bu satır **hiç çizilmez**.

**Seans biterken** — üç yol, hiçbiri iki soru sormaz:

1. Seans bir işe bağlı ve o işin ölçüsü var → **tür sorusu atlanır**, doğrudan
   sayı istenir. (Kazanılan asıl dokunuş burası.)
2. Seans işe bağlı değil ama bugünün açık işleri var → tek dokunuşluk
   *"hangi işe?"*, `atla` ile geçilir.
3. Hiçbiri yoksa → bugünkü davranış birebir aynı.

**Görevler sekmesi:** görev satırının dibinde künye —
`▲ 200 → 300` · `s.52 → 120` · henüz sayı girilmemişse niyet satırı
(`300 soru` / `s.120'ye kadar`). Kutu yok, çubuk yok, renk yok.

---

## 6. Kırmızı çizgiler

`31 §3`'ün listesi aynen geçerli, üstüne bu dosyanın kendi kararları:

- ❌ **Yüzde.** "%66" tek başına bir puandır.
- ❌ **İlerleme çubuğu / doluluk halkası.** `24`'ün KPI panosu yasağı.
- ❌ **Kesir gibi okunan gösterim.** "200 / 300" bir skor gibi okunuyordu;
  yerine `▲200 → 300` seçildi — hedef bir paydanın değil, bir varış yerinin
  adı. Sayfa ölçüsündeki `→` ile aynı harf.
- ❌ **Gün başlığında toplam.** "bugün 640 soru" tam olarak `24`'ün
  "şirket çeyrek raporu" dediği şey. Görevin kendi satırında görünmesi başka.
- ❌ **Tekrar eden günlük hedef ayarı.** "Her gün 300 soru" hem `04 G7`'nin MVP
  dışı bıraktığı tekrarlayan görevdir hem de doğrudan seri (streak) üretir.
  Hedef her gün elle yazılır.
- ❌ **Zorunluluk.** Ölçüsü olan işin seansı sayı girilmeden bitirilebilir.
- ❌ **Widget'a girmez** (`26-widget-uygulandi.md`: widget yalnız zamanı gösterir).
- ❌ **Çip şeridi.** Başlat ekranına bugünün işleri yatay çip olarak konuldu ve
  **geri alındı**: üç işte ekranın dikey ritmi bozuluyor, beşte sayaç ekranı çip
  bulutuna dönüyordu. Ferahlık `CLAUDE.md`'nin stabilizasyon kuralının kendisi.
  Yerine kaç iş olursa olsun yüksekliği değişmeyen tek satır kondu.
  **Bu dalı tekrar önerme.**

---

## 7. Uygulandı (27 Ağustos 2026)

`kertik-android/app/src/main/assets/index.html`:

- `gorevZinciri` / `gorevIlerleme` / `gorevKunyeHtml` / `gorevDurumTazele`
- `askGorevOlcu` / `askGorevHedef` — görev menüsündeki `ölçü ve hedef`
- `renderGorevSec` + `seciliGorev` — başlat ekranındaki tek satırlık bağ
- `askOlcu` yönlendiriciye dönüştü; eski gövde `askOlcuTur` oldu;
  `askSeansGorev` eklendi
- `setOlcu` görevin ölçüsünü öğreniyor ve durumunu tazeliyor
- `startSession` → `taskId`; not boşsa işin adı nota düşüyor
- CSS: `.task .kunye`, `.gorevsec`
- Dil: `tr` ve `en` dolduruldu (`gorev_sec`, `gorev_hedef`, `hedef_baslik`,
  `hedef_kac_soru`, `hedef_hangi_sayfa`, `hedef_soru_ozet`, `hedef_sayfa_ozet`,
  `seans_hangi_is`, `gorev_kaldin`); diğer 13 dil `soz()`'ün geri düşüş
  zincirinden İngilizce görüyor — `31 §9`'daki aynı bilinçli borç.

### Doğrulandı (headless, Playwright + `/opt/pw-browsers/chromium`)

Dokuz yol, sıfır konsol hatası:

1. Başlat ekranı bağ satırı, iş seçimi, `taskId`'nin seansa yazılması
2. Ölçülü işte seans sonu → tür sorusu atlanıyor, doğrudan `kaç soru?`
3. Görev satırında künye + durumun `yapiliyor`a dönmesi
4. Hedefe varılınca durumun `bitti`ye dönmesi
5. Sayfa görevi taşınınca imlecin (52) ve hedefin (120) korunması
6. Soru görevi taşınınca hedefin (300) kalıp sayacın sıfırlanması
7. Ölçüsüz işte seans sonu → eski tür sorusu geliyor
8. Hiç görev yokken bağ satırının hiç çizilmemesi (anne yolu)
9. Bağlanmamış seans + açık görev → `hangi işe?` → seçim → ölçü

Ayrıca `node --check` ile script bloğu temiz; görevler ve başlat ekranı
ışık/karanlık modda ekran görüntüsüyle incelendi.

### Doğrulanmadı

- Gerçek cihazda dokunma hissi ve tipografi
- 13 dilin geri kalanında satır uzunlukları

---

## 8. Ç7 kurulduğunda ne değişir

`subject` tablosu geldiğinde `task.olcu` / `task.hedef` oraya taşınır ve hedef
günlük görevden derse geçer. `gorevIlerleme`'nin zincir yürüyüşü o zaman
gereksizleşir — ilerleme doğrudan dersin seanslarından türer. Künyenin görseli
(`.kunye`, `gorevKunyeHtml`) değişmeden kalabilir.


---

## 9. Ek: kayıt sekmesi ve "hedefe varınca" kuralı (aynı gün, sonradan)

İki küçük düzeltme aynı gün eklendi:

**Geçmiş gün satırına ölçü işlendi** (`gorevOlcuDuz`, `.logtask .lk`). Kayıt
sekmesinde artık `04-cozum-gorevler.md` G6'nın tek ekran görünümü birebir
çıkıyor:

```
dün                                  2s 30dk · 4 işten 2 oldu
–  Matematik denemesi · ▲200 → 300 · zaman yetmedi
✓  Fizik kitabı · s.120
✓  Kimya tekrarı
→  İngilizce kelime · 150 soru
```

Ne kadar, ne, oldu mu — üçü tek satırda. Salt okunur. Girilen sayının
ertesi gün gidecek bir yeri olmasaydı ölçü yarım kalırdı.

**Hedefe varılınca hedef bir daha yazılmıyor** (`varildi`). `▲300 → 300` ve
`s.120 → 120` gereksiz bir yankıydı; ✓ işareti zaten söylüyor. Sıra da
değişti: `başlık · ölçü · sebep` — sebep uzun ve yumuşak, satır sonunda o
kırılsın.

---

## 10. "Başka ölçü türleri ekleyelim mi?" — hayır, ve gerekçesi

> Soru (27 Ağustos 2026): *"Şu an soru çözme var, kitap okuma var. Başka bir
> şey de olabilir. Eklemeler yapmalı mıyız?"*

### 10.1 Adayların hepsi mevcut ikisinin kopyası

| Aday | Kim ister | Şekli | Karşılığı |
|---|---|---|---|
| tekrar / set | spor, ezber, kelime kartı | birikim | `soru` |
| kelime sayısı | tez, yazı | imleç | `sayfa` |
| video / ders / bölüm | kurs izleme | imleç | `sayfa` |
| madde / iş adedi | liste temizleme | birikim | `soru` |
| süre | herkes | (ayrı sınıf, bkz. 10.3) | — |

Sistemde tür değil **iki şekil** var:

- **birikim** — sıfırdan başlar, toplanır, hedef = *kaç tane* → `soru`
- **imleç** — mutlak konum, toplanmaz, hedef = *nereye kadar* → `sayfa`

Geri kalan her aday bu iki şekilden birinin başka bir adıdır. `sayfa`'yı
"kelime sayısı"ndan ayıran tek şey künyedeki `s.` ekidir.

### 10.2 Gerçek boşluk tek: tek sayılık birikim

Yine de bir şekil eksik: **tek sayı, birikir.** `soru` üçlü (▲▼○), `sayfa`
imleç. "50 kelime ezberledim" bugün ancak ▲ alanına yazılarak ifade ediliyor —
çalışıyor ama semantik olarak eğri.

Bir gün bir şey eklenecekse **`adet`** eklenmeli: tek sayı, birikir, künyede
işaretsiz. Kelime, tekrar, set, video, madde — hepsini tek başına karşılar.
Ve **son eklenen tür o olmalı.**

### 10.3 Süre hedefi: eklenebilir görünen ama eklenmemesi gereken tek aday

"Bu işe bugün 2 saat" cazip: seans zaten işe bağlı, süre zaten ölçülüyor,
kullanıcıdan **tek dokunuş bile istemiyor**, künye kendiliğinden doluyor.

Buna rağmen **hayır.** Gerekçe `02-urun-vizyonu.md`'nin birinci ilkesi:

> Sayfa ya da soru hedefi sayacı açık bırakarak şişirilemez. **Süre hedefi
> şişirilebilir** — ve şişirmeye teşvik eder. Kullanıcıyı kendi kaydına yalan
> söylemeye iten bir hedef, "dürüst kayıt" sözünü doğrudan hedef alır. Bu
> ürünün tek satılık noktası güven.

Forest'ın çözdüğünü sandığı, aslında ürettiği problem tam olarak budur.

### 10.4 Şimdilik karar: hiçbir şey ekleme

`05-ozellik-listesi.md`'nin kuralı bağlayıcı: *her özellik bir şikâyete
karşılık gelmeli.* Ortada şikâyet değil merak var — üstelik ölçünün kendisi
bugün eklendi ve **henüz telefonda hiç kullanılmadı.**

Ayrıca her yeni tür `bir şey sayıyor musun?` sayfasını genişletiyor: üç seçenek
bir bakış, beş seçenek bir menü, altı seçenek bir form. `CLAUDE.md`'nin tek
cümlesinin ısırdığı yer tam orası.

**Sıradaki adım tür eklemek değil, mevcut ikisini telefonda kullanmak.** Bir
hafta sonra "şuna sayı giremiyorum" diye somut bir cümle çıkarsa, §10.2'deki
`adet` hazır bekliyor.
