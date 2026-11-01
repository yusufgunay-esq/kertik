# 21 — Diller

Kertik 15 dilde: Türkçe, İngilizce, Almanca, Fransızca, İspanyolca, İtalyanca,
Portekizce (Brezilya), Hollandaca, Lehçe, Rusça, Japonca, Korece, Basit Çince,
Geleneksel Çince, Arapça.

Seçim sırası **Play'de para harcayan pazarlar**. Türkiye zaten vardı; geri kalanı
uygulama içi satın alma cirosunun büyük kısmını üreten ülkeler. Hintçe, Endonezce,
Tayca gibi büyük ama ucuz pazarlar bilerek dışarıda: bakım yükü getirir, ücretli
uygulamada karşılığı az.

## Nasıl çalışıyor

Ekranda görünen **hiçbir metin artık koda gömülü değil.** Hepsi `index.html`
içindeki `SOZLUK` nesnesinde, anahtar → metin olarak duruyor. Kod her yerde
`soz("anahtar")` çağırıyor.

```js
soz("btn_baslat")                        // "Başlat" / "Start" / "開始"
soz("um_baslik", { s: human(len) })      // yer tutucu
soz("alt_bugun", { s: "1s 20dk", n: 3 }) // çoğul: n'e göre biçim seçilir
```

Çoğul gereken metinler nesne olarak yazılıyor; hangi biçimin seçileceğine
`Intl.PluralRules` karar veriyor. Rusça'nın üç, Lehçe'nin üç, Arapça'nın altı
çoğul biçimi var — elle if yazılmıyor, tarayıcı kendi kurallarını uyguluyor.

Tarih, saat ve sayı biçimi de `Intl`den geliyor:

- **Saat** dilin kendi biçiminde (`hhmm`). İngilizce'de "2:05 PM", Almanca'da "14:05".
- `<input type="time">` ve dosya adları **her zaman** 24 saat (`hhmmHam`).
  İkisini karıştırma — biri ekran, öteki veri.
- **Tarih** `Intl.DateTimeFormat`. Türkçe'de tasarım dili gereği küçük harfe
  çevriliyor ("16 ağustos pazar"); diğer dillerde büyük harf korunuyor, çünkü
  Almanca'da ay adı, İngilizce'de gün adı büyük yazılır.
- **bugün / dün** `Intl.RelativeTimeFormat`'tan; sözlükte anahtarı yok.
- **Rakamlar her dilde latin** (`-u-nu-latn`). Arapça'da hint rakamına düşmesin
  diye: kadrandaki kronometre zaten ASCII, karışığı çirkin duruyor.

## Dil nasıl seçiliyor

`S.settings.lang` — varsayılan `"auto"`, yani cihazın dili (`navigator.language`).
Ayarlar → dil → istediğini seç. Seçim kayıtlara yazılıyor, senkronla diğer
cihaza da geçiyor.

Eşleme toleranslı: `de-AT` → Almanca, `pt-PT` → Portekizce (Brezilya),
`zh-HK`/`zh-TW`/`zh-Hant-*` → Geleneksel, kalan `zh-*` → Basit. Hiçbiri
tutmazsa İngilizce.

## Arapça — sağdan sola

`document.documentElement.dir` Arapça'da `rtl` oluyor, CSS mantıksal
özelliklerle (`margin-inline-start`, `inset-inline-start`, `text-align:start`)
kendiliğinden aynalanıyor.

**Aynalanmayan üç şey var, bilerek:** kadran, çubuk ve kronometre. Bunlar cümle
değil, ölçü aleti. `[dir="rtl"]` bloğunda `direction:ltr` ile sabitlendiler.

Saat damgaları ayrı bir sorun: "14:00 – 15:30" içindeki tire yönsüz bir karakter
olduğu için Arapça bir cümlede uçlar yer değiştiriyor ve saat ters okunuyor.
`saatY()` ve `aralik()` bunun için var — damgaları U+2066/U+2069 yalıtımına
alıyorlar. Soldan-sağa dillerde hiçbir işaret eklenmiyor.

`AndroidManifest.xml`'de `supportsRtl` **false'tan true'ya çevrildi.** Bu
olmadan bildirim ve sistem diyalogları aynalanmıyor.

## Android tarafı

Bildirimin başlığı ve alt satırı sayfadan geliyor, yani uygulama içi dille aynı.
Kanal adı ve tuş etiketleri (`Devam et` / `Mola` / `Bitir`) ise Android
kaynaklarından: `res/values-XX/strings.xml`. Bunlar **sistemin** dilini izliyor.
İkisi ayrı olsun diye böyle: kullanıcı uygulama içinden başka bir dil seçse bile
sistem tuşlarının telefonun dilinde kalması doğrusu.

`res/xml/diller.xml` Android 13+ için: Ayarlar → Uygulamalar → Kertik → Dil
listesini besliyor.

## Yeni dil eklemek

Beş yer, sırayla:

1. `index.html` → `SOZLUK`'a aynı anahtarlarla yeni bir blok. Eksik anahtar
   bırakılırsa uygulama patlamaz, İngilizce'ye düşer — ama test bağırır.
2. `index.html` → `DIL_ADI`'na bir satır, dilin **kendi** adıyla ("Svenska").
   Sağdan sola bir dilse `DIL_RTL`'e de kodunu ekle.
3. `res/values-XX/strings.xml` — beş bildirim metni.
4. `res/xml/diller.xml` — bir `<locale>` satırı.
5. `22-magaza-metinleri.md` — Play girişi için üç alan.

Sonra `node test/hepsi.js dil`. Test eksik anahtarı, ölü anahtarı, yer tutucu
uyuşmazlığını ve metin taşmasını yakalıyor.

## Testler

`test/test-dil.js` — 133 doğrulama:

- 15 dilin hepsinde aynı anahtar kümesi var mı, fazlası eksiği var mı
- Kodda çağrılan her anahtar sözlükte duruyor mu; sözlükte kullanılmayan
  ölü anahtar kaldı mı
- Her dilde dört sekme + sheet'ler açılıyor, konsol temiz mi
- **Metin taşması:** tuş ve etiketlerin içeriği kutusundan taşıyor mu (Almanca
  ve Rusça uzun; 360px genişlikte deneniyor)
- Yazı yönü doğru mu (yalnız Arapça rtl)
- Çoğul biçimleri: Rusça 5 → "сессий", Lehçe 1 ≠ 5, İngilizce 1 → tekil
- Ham saat her dilde 24 saat kalıyor mu
- Türkçe tarih küçük, Almanca tarih büyük harfli mi

Eski testlerdeki Türkçe metin karşılaştırmaları da `soz()`e çevrildi; artık
testler hangi dilde koşarsa koşsun geçiyor. Kapalı ortamlarda tarayıcı yolu
`KERTIK_KROM` ortam değişkeniyle verilebilir.

## Bilinen sınır

`index.html` 104 KB'dan 209 KB'a çıktı; artışın hepsi sözlük. Yerel bir dosya
olduğu için ağ maliyeti yok, açılışa etkisi ölçülemeyecek kadar az. 25 dile
çıkarsan da sorun olmaz; onun ötesinde dilleri ayrı dosyalara bölüp yalnız
seçileni yüklemek gerekir — ama o zaman "tek dosya" mimarisi biter, acele etme.
