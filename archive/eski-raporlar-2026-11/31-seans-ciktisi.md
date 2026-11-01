# 31 — Seans Çıktısı: "Ölçü" (sayfa / soru / yok)

> Soru (24 Ağustos 2026): *"HMGS Takip'teki gibi 'şuraya kadar okudum', 'şu kadar
> doğru şu kadar yanlış' sistemini Kertik'e getirsek mi? Kullanıcı bazen sadece
> araştırma yapıyor olabilir, bazen test çözüyor, bazen kitap okuyor. Bunu sanat
> dilimizin içinde güzel yapabiliyorsak yapalım."*
>
> Zemin: `02-urun-vizyonu.md` (sessiz arayüz, "annem kaybolur mu"),
> `05-ozellik-listesi.md` (kapsam disiplini, "asla yapmayacaklarımız"),
> `08-veri-modeli.md` (olay listesi, sayılar türetilir),
> `24-sanat-dili.md` (wabi-sabi anayasası — özellikle *ma*, *kanso*, KPI panosu yasağı),
> `CLAUDE.md` (uğraştıran ya da bitmemiş görünen özellik eklenmez).
>
> Referans sistem: `HMGS_Takip_App/KARMA_CALISMA_MODULU.md` — oradaki
> "Karma (Konu+Soru)" kaydı.

Tarih: 24 Ağustos 2026

---

## 1. Karar

**Evet, ama HMGS'deki gibi değil.**

HMGS Takip bir *sınav hazırlık muhasebesidir*: D/Y/B, net projeksiyonu, sayfa
bütçesi, zayıflık indeksi. Orada doğru olan şey Kertik'te yanlıştır — çünkü o
uygulamanın tek kullanıcısı var ve o kullanıcı bir sınava hazırlanıyor. Kertik'in
ikinci kullanıcısı öğrenci bile değil.

Kertik'e giren şey şudur:

> **Ölçü** — bir *işe* (ders/konu) bir kez takılan, seans bitiminde tek satır
> soran, boş bırakılabilen, hiçbir yerde puana çevrilmeyen bir iz.

Üç değeri var, dördüncüsü yok:

| Ölçü | Ne zaman | Seans sonunda sorulan | Varsayılan |
|---|---|---|---|
| `yok` | Araştırma, yazı, hazırlık, "iş" | **hiçbir şey** | ✅ bu |
| `sayfa` | Kitap, doküman okuma | tek sayı: *nerede kaldın* | |
| `soru` | Test, soru bankası | üç küçük sayı: ▲ ▼ ○ | |

Ölçü **seansın değil, işin özelliğidir.** "Kimya" işine bir kez `sayfa` dersin,
o işin her seansı sonunda o tek satır çıkar. Her seans başında "bugün ne
yapacaksın?" diye soran bir mod seçici **yok** — o, `02`'deki sessiz arayüz
ilkesini ve `CLAUDE.md`'deki "uğraştırıcı olmasın" kuralını aynı anda çiğnerdi.

**Ölçüsü olmayan bir seans, bugünkü seansla birebir aynı davranır.** Anne
profili için hiçbir şey değişmez: iş bile seçmeyen bir kullanıcı bu özelliğin
var olduğunu asla öğrenmez. Özellik kendini göstermez, çağrıldığında gelir.

---

## 2. Kritik tasarım hamlesi: sayfa **aralığı** değil, **imleç**

HMGS'de kullanıcı `s.45-52` yazar. Kertik'te yazmaz. **Tek sayı yazar: 52.**

Başlangıcı uygulama bilir — o işin bir önceki seansının bıraktığı yer. Aradaki
fark (7 sayfa) türetilir, saklanmaz (`08-veri-modeli.md`'nin altın kuralı).

Bunun üç sonucu var ve üçü de ürünün mevcut sözleriyle aynı hizada:

1. **Tek alan, tek dokunuş.** Anne testi geçer. İki alanlı bir "başlangıç–bitiş"
   formu geçmezdi.
2. **Kalıcı bir fayda üretir:** başlat ekranında, iş adının altında tek gri satır —
   *"Kimya · s.52'de kaldın"*. Bu bir istatistik değil, bir **yer imi**. Uygulamayı
   ertesi gün açmanın somut bir sebebi olur, üstelik motivasyon bildirimi
   kullanmadan (`05`, "asla yapmayacaklarımız").
3. **Dürüst kayıt ilkesine uyar.** Atlama olur (kitap değişir, geriye dönülür):
   fark negatifse ya da absürt büyükse uygulama **hesaplamaz, sadece yeni imleci
   yazar.** Uydurmaz. Şüphede kaldığında az sayar, çok değil.

Soru ölçüsünde simetrik hamle: **boş alanı kullanıcı doldurmaz.** Toplam soru
sayısı istenmez; ▲ doğru, ▼ yanlış, ○ boş — üçü de doğrudan girilir, `toplam`
türetilir. Üç sayıdan biri sıfırsa hiç yazılmaz.

---

## 3. Sanat dili karşılığı

`24-sanat-dili.md` bağlayıcı. Bu özelliğin görselinin geçmesi gereken sınav
oradaki testtir: *projeyi bilmeyen birine 3 saniye göster, "istatistik" derse
başarısız.*

### Ne olacak

- Çıktı, seans kartında **çubuğun altına** değil, kalasın **dibine kazınmış bir
  künye** olarak durur — `--kopru` ahşap tonunda, kalastan bir ton açık, kutu
  yok, çerçeve yok, ikon yok. Zaman kalasın üstünde, ölçü kalasın dibinde:
  ikisi aynı malzemeye kazınmış iki farklı derinlik.
- Soru ölçüsünde rakamların yanında sayı değil **işaret** durur: ▲ (dolu),
  ▼ (boş üçgen), ○ (halka). Renk **kullanılmaz** — doğru yeşil, yanlış kırmızı
  olmaz. `02`'nin kuralı: *"Kırmızı değil gri."* Yanlış bir suç değil, bir veri.
- Sayfa ölçüsünde tek bir satır: `s.52` ve altında, ancak bir önceki seans varsa,
  ince bir *"+7"*. Yüzde yok, hedef yok, çubuk yok.
- Doğuş animasyonu serbest (`24 §2.6` istisnası): künye 400 ms'de kazınır ve
  durur. Döngü yok.

### Ne olmayacak — kırmızı çizgiler

Bunlar liste dışı bırakılmış kararlardır, unutkanlık değil:

- ❌ **Başarı yüzdesi.** "%78 doğruluk" tek başına bir puandır; puan seri (streak)
  doğurur, seri de `05`'in yasakladığı her şeyi doğurur.
- ❌ **Haftalık/aylık toplam soru veya sayfa sayısı bir başlık olarak.** Bu tam
  olarak `24`'ün "şirket çeyrek raporu" dediği şeydir. (Geçmiş ekranında, seansın
  kendi kartında görünmesi başka; günün/haftanın tepesine yazılması başka.)
- ❌ **Grafik.** Doğru/yanlış eğrisi, sayfa hızı trendi, konu bazlı kırılım.
  Bunlar HMGS'nin işi ve HMGS'de kalır.
- ❌ **Zorunluluk.** Ölçüsü olan bir işin seansı bitirilirken alan boş
  bırakılabilir; "bitir" tuşu asla beklemez. Boş bırakılan seans eksik değildir,
  sadece ölçüsüzdür.
- ❌ **Hatırlatma.** "Dün kaç soru çözdüğünü girmedin" bildirimi yok.

---

## 4. Veri modeli eki

`08-veri-modeli.md`'ye eklenecek. İki değişiklik, ikisi de geriye dönük uyumlu.

### `subject` tablosuna tek alan

| Alan | Tip | Not |
|---|---|---|
| `measure` | enum | `yok` (varsayılan) \| `sayfa` \| `soru` |

### Yeni tablo: `session_outcome`

Seansın kendisine sütun eklenmiyor; ayrı satır. Sebep: ölçü **sonradan** girilen,
sonradan düzeltilebilen, silinebilen bir şey — seansın saflığını bozmamalı ve
`created_by` / `edited_at` şeffaflığını miras almalı.

| Alan | Tip | Not |
|---|---|---|
| `session_id` | UUID (PK) | |
| `measure` | enum | seans anındaki ölçü (iş sonradan değişse bile kayıt bozulmaz) |
| `page_at` | int? | `sayfa`: kalınan yer — **aralık değil, imleç** |
| `correct` / `wrong` / `blank` | int? | `soru`: üçü de opsiyonel |
| `entered_at` | epoch ms | |
| `edited_at` | epoch ms? | elle düzeltildiyse dolu |

### Türetilenler (sorgu, tablo değil)

- **imleç:** bir iş için `page_at`'i dolu son seans → başlat ekranındaki "s.52'de kaldın"
- **fark:** `page_at − (aynı işin bir önceki page_at'i)`; negatifse veya bir eşiği
  aşıyorsa **gösterilmez** (uydurma yok)
- **toplam soru:** `correct + wrong + blank`

> `measure` alanının seansta kopyalanması bilinçli: kullanıcı "Kimya"yı sonradan
> `soru`ya çevirirse eski sayfa kayıtları anlamsızlaşmaz. Geçmiş taş değil, ama
> geçmişin ne olduğu da değişmez.

---

## 5. Akış (tam metin)

**İş oluştururken** — tek satır, atlanabilir:

> Bu işte bir şey sayıyor musun?
> **Hayır** · Sayfa · Soru

Varsayılan seçili: *Hayır*. Üç kelime, açıklama yok, örnek yok.

**Seans biterken** (yalnız ölçülü işlerde), özet kartının altında:

> `sayfa` → "Nerede kaldın?" · [ 52 ] · *atla*
> `soru`  → ▲ [ ] ▼ [ ] ○ [ ] · *atla*

*atla* tuşu her zaman görünür ve kartı kapatır. Klavye otomatik açılmaz —
sayı alanına dokununca açılır (bir tuş fazladan, ama zorlamayan bir arayüz için
ödenecek doğru bedel).

**Ertesi gün, başlat ekranında:**

> Kimya
> s.52'de kaldın

Tek satır. Gri. Dokunulabilir değil.

---

## 6. Neden HMGS'nin "Karma" modu buraya alınmıyor

HMGS'de doğru bir problem çözülmüştü: 40 dakikalık tek blokta hem soru çözülüyor
hem konu okunuyordu, kullanıcı bunu ikiye bölemiyordu — çözüm, tek kayda hem
D/Y/B hem sayfa hem terim koymaktı.

Kertik'te bu problem **başka türlü çözülüyor:** ölçü işe bağlı olduğu için bir
seans zaten tek bir ölçüye sahiptir; ikiye bölme baskısı hiç doğmaz. Aynı seansta
hem sayfa hem soru girmek isteyen kullanıcı, Kertik'in hedef kitlesinin
dışındadır ve o kullanıcının elinde zaten HMGS Takip var.

"Karma" modu buraya alınırsa seans sonu kartı dört alanlı bir forma dönüşür —
`CLAUDE.md`'nin tek cümlesi bu özelliği orada keser: *uğraştırıcı bir şey
çıkarıyorsa eklemem.*

Terimler/anahtar kelime kutusu da alınmıyor. Onun karşılığı Kertik'te zaten var:
`session.note` (tek satır, serbest). İkinci bir metin alanı açmak yeni bir yetenek
değil, yeni bir yük olur.

---

## 7. Yol haritasındaki yeri

**v1, Ç7'den (seansı işe/konuya bağlama) sonra.** Öncesinde teknik olarak
imkânsız: ölçü işe takılıyor, iş yoksa ölçü de yok.

MVP'ye alınmaz. `05`'in kuralı: *MVP'deki her özellik bir şikâyete karşılık
gelmeli.* Bu bir şikâyetin değil, bir merakın karşılığı — ve en iyi hâliyle bile
yer imi üretiyor, dürüst kayıt üretmiyor. Dürüst kayıt önce biter.

---

## 8. Doğrulama ölçütleri (bu iş yapıldığında geçmesi gerekenler)

- [ ] Ölçüsüz bir iş seçilerek yapılan seans, bu özellik yokmuş gibi biter —
      fazladan tek piksel, tek gecikme yok.
- [ ] İş seçmeden yapılan seansta ölçü arayüzü hiç var olmaz (anne yolu).
- [ ] Seans sonu kartında "atla" ile kapatılan seans, geçmişte eksik/uyarılı
      görünmez — sadece künyesi olmaz.
- [ ] Aynı işte ikinci seansta girilen sayfa, birincisinden küçükse fark
      **gösterilmez**, imleç yine de güncellenir.
- [ ] `3 saniye testi` (`24 §1`): seans kartı projeyi bilmeyen birine gösterildiğinde
      "istatistik / grafik / uygulama arayüzü" cevabı gelmiyor.
- [ ] Işık ve karanlık modda künye kalastan ayrışıyor ama ondan yüksek sesli değil.

## Yapılacaklar (bu dosyadan çıkan)

- [ ] `08-veri-modeli.md`'ye `subject.measure` ve `session_outcome` işlensin.
- [ ] `15-yol-haritasi-v2.md`'ye v1 maddesi olarak eklensin (Ç7 bağımlılığıyla).
- [x] Künye görseli için `tasarim/` altında küçük bir laboratuvar: kalas dibine
      kazınmış ölçü — üç varyant (sayfa / soru / boş), ışık+karanlık.
      → `tasarim/kunye-laboratuvari.html` (24 Ağustos 2026).
- [ ] Widget'a **girmez** — karar: widget yalnız zamanı gösterir (`26-widget-uygulandi.md`).

---

## 9. Uygulamaya giren ilk sürüm — "seansa direkt" (24 Ağustos 2026)

`§1`'deki karar (ölçü işe takılı olsun, kalıcı `subject` üzerinden) uygulamada
henüz kurulamıyor: `kertik-android/app/src/main/assets/index.html`'deki
`tasks` tamamen **günlük** nesneler (`plannedFor` bir tarih, durumu
`bekliyor/bitti/olmadı/taşındı`) — `08-veri-modeli.md`'nin öngördüğü kalıcı
`subject` tablosu (Ç7) henüz hiç kurulmadı. Bu yüzden bugün kodlanan sürüm
kasıtlı olarak **küçültülmüş**:

- Ölçü işe değil, **doğrudan seansa** takılı. Seans biterken bir kez sorulur
  (`askOlcu`): *"bir şey sayıyor musun?"* → **Hayır** (varsayılan, tek dokunuş,
  bir daha sorulmaz) · Sayfa · Soru.
- Sayfa seçilirse tek sayı istenir (`olSayfaAtla` ile atlanabilir). **Fark
  (`+7`) hesaplanmıyor** — çünkü kalıcı bir "iş" olmadığı için bir önceki
  değere güvenli biçimde bakılamıyor. Künye yalnız o seansın kendi sayısını
  gösteriyor: `s.52`.
- Soru seçilirse ▲/▼/○ üç ayrı sayı istenir, hepsi opsiyonel.
- Künye iki yerde görünüyor: seans özeti kağıdında (kalasın altında) ve
  geçmiş listesindeki seans kartının açılmış görünümünde (kalasın dibinde,
  `.kunye` CSS sınıfı — `--kopru` tonunda, kutu/ikon/renk kodu yok).
- **Başlat ekranındaki yer imi eklenmedi** (`§5`'teki "s.52'de kaldın" satırı)
  — kalıcı bir "iş" olmadan hangi işin hangi künyesine bakılacağı belirsiz.
- Çeviri: yalnız `tr` ve `en` dolduruldu; `soz()`'ün kendi geri düşüş
  zincirinden (`DIL → en → tr → anahtar`) diğer 13 dil İngilizce görüyor.

**Bu bölümdeki her şey `§1`–`§8`'in yerini almıyor, geçici bir köprü.** Ç7
kurulduğunda: `se.olcu`/`se.olcuVeri` seans yerine `subject.measure`'a taşınır,
fark hesaplanabilir hale gelir, yer imi eklenir — künye görselinin kendisi
(`.kunye`, `kunyeHtml()`) değişmeden kalabilir.

**Doğrulandı (headless, Playwright + `/opt/pw-browsers/chromium`):** sayfa/soru/hayır/atla
dört yol da hatasız çalışıyor, `node --check` ile script bloğu sözdizimi
temiz, künye HTML'i beklenen yerlerde (özet + geçmiş kartı) çıkıyor.
**Doğrulanmadı:** gerçek cihazda görsel inceleme, `test/test-cizim.js` koşumu
(bu oturumda staged değildi — çizim fonksiyonlarına dokunulmadı, risk düşük
ama koşulmadı), 13 dilin geri kalanında görünüm.
