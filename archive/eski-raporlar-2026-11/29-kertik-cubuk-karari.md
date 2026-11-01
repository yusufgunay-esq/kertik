# 29 — Çubuk: Kertik (C) modeline geçildi

> Kaynak: `tasarim/cubuk-laboratuvari.html` (beş yorum: A Mevcut, B Malzeme, C Kertik,
> D Sumi-e, E Kırık omurga). Kullanıcı kararı: **C · Kertik**, 18 Ağustos 2026.
> Zemin: `20-sanat-geri-bildirim.md` madde 3 ve 7 (genişletilmiş palet, "şirket
> istatistiği" eleştirisi), `19-akis-ve-cubuk.md` (çubuğun uygulamaya ilk girişi).

## 1. Karar

`cizCubuk` (`kertik-android/app/src/main/assets/index.html`) düz vektör çizgi
("A · Mevcut" — laboratuvardaki kontrol grubu, `20-sanat-geri-bildirim.md`'nin
"çizgi film gibi / KPI panosu" dediği hâl) yerine artık gerçek bir **kertik**
çiziyor: sütun bir çizgi değil GENİŞLİĞİ olan bir kalas, dakikalar da o kalasa
açılmış V kesitler — üstte ışık yüzü, altta gölge yüzü. Uygulamanın adıyla
görseli artık birebir aynı şeyi söylüyor.

Bu, `20-sanat-geri-bildirim.md` madde 3'ün istediği genişletilmiş paleti de
hayata geçiriyor: iki çiğ renk (accent/cool) yerine üç iş tonu + iki mola tonu
+ bir köprü tonu, şerit içi karışım yok — ton çentiğin **ağırlığından** geliyor
(saat başı en koyu, beşlikler orta, tek dakikalar en açık). Süre dağılımı artık
ölçmeden okunuyor: molanın uzunluğu kalasın arkasında görünür bir gölge bırakıyor.

## 2. Değişenler

| Dosya | Değişiklik |
|---|---|
| `kertik-android/app/src/main/assets/index.html` `:root` / `:root.dark` | Genişletilmiş palet eklendi: `--is1/--is2/--is3` (iş tonu, ağırlığa göre), `--kopru` (kalas ahşap tonu), `--mola1/--mola2` (mola gölgesi + kenar izi). Değerler laboratuvardaki `cubuk-laboratuvari.html` ile birebir aynı. |
| aynı dosya, `hash32`/`rng32`'nin hemen altı | `firca()` (dolgulu fırça şeridi — ışık yüzü ve dip gölgesi için) ve `tonu(mm)` (dakikanın ağırlığına göre renk) eklendi. |
| aynı dosya, `cizCubuk()` | Tamamen laboratuvardaki `cizC` mantığına göre yeniden yazıldı: kalas gövdesi (düzensiz kenar + damar + ışık/gölge kenarları), mola artık kalasın arkasında soluk bir gölge bandı + kenar izi (kesik atılmıyor — bu zaten değişmedi), çentikler V kesit (iki yüz: `tonu(mm)` dolgu + `firca()` ile ışık yüzü + dip gölgesi). Sayılmayan süre rayı aynı mantıkla duruyor, yalnız kalas kalınlığına (`KAL = sw*.62`) göre konumu güncellendi. |
| aynı dosya, çentik/kalas/mola grupları | Test edilebilirlik için `data-centik`, `data-kalas`, `data-mola` işaretleri eklendi (görsel etkisi yok). |
| `kertik-android/test/test-cizim.js` | Çubuk geometrisine bağlı 7 test, yeni V-kesit/kalas yapısına göre güncellendi (bkz. §3). Akış/duvar/tema testleri dokunulmadı. |

Kazınma animasyonu (`reveal`, seans özetinde kullanılıyor) korundu ama teknik
değişti: eski `stroke-dashoffset` çizgi-çizme hilesi dolgulu V-kesitlere
uygulanamıyordu (dolgu şekli, çizgi değil), bunun yerine kalas/mola/çentik
grupları aynı kademeli gecikmeyle (`n * adim`) opacity ile beliriyor. Sonuç
seans özetinde hâlâ "kazınıyor" hissi veriyor, üstelik artık **gerçekten**
bir kertik kazınıyor.

## 3. Testler

`test/test-cizim.js`'deki eski sayım yöntemi (`line[pathLength]` sayarak
çentik saymak) yeni yapıda anlamsız kaldı çünkü çentikler artık dolgulu
`<path>` grupları. Değişen ölçütler:

- `say(svg)` → `svg.querySelectorAll("[data-centik]").length`
- "iki sırt çizgisi var" → "iki kalas var": `[data-kalas]` sayısı sütun sayısına eşit
- viewBox regex `-7 0` → `-8 0` (kalas kenar düzensizliği için sol pay büyüdü)
- Kayıt kartı testi artık `[data-cubuk] line` yerine `[data-cubuk] [data-centik]` sayıyor

Doğrulanan davranış aynı kaldı, değişen yalnız ölçüm yöntemi:
çalışma dakikası = çentik sayısı, mola/boşluk dakikasına kesik atılmaz, aynı
seans hep aynı çubuk, sayılmayan süre tek dikey ray olarak sağda durur.

**Not — eşzamanlı TAŞ (pomodoro) çalışmasıyla birleştirildi.** Bu değişiklik
sürerken `index.html`/`test-cizim.js` ayrıca `cizTas`/`gunTas` (pomodoro günü
taş, kronometre günü çubuk — `27-sanat-ayrisimi.md`'nin kararı) ile
güncellenmişti. İkisi çakışmadı, tek istisna: "5b" testi taş/çubuk gününü
`svg path` / `svg line` varlığına bakarak ayırıyordu; kertikli çubuk artık
kendi de `<path>` kullandığı için bu ölçüt `[data-kalas]` işaretine
çevrildi (davranış aynı, yalnız ayrım yöntemi değişti).

Koşum: `61 geçti, 3 kaldı` (kalan 3'ü çubukla ilgisiz, önceden de kırık olan
"akış tuvali" testleri — bkz. §5).

Ayrıca `full.html` üzerinden Playwright ile ışık/karanlık modda gerçek bir
seans çubuğu ekran görüntüsü alınarak görsel olarak da doğrulandı: kalas
dokusu, V kesitler ve mola gölgesi bekleneni veriyor.

## 4. Dokunulmayanlar (bilinçli olarak kapsam dışı)

- **`WidgetCizer.kt`** (Android widget'ın Kotlin çizim karşılığı) ve
  `res/values/widget_renkler.xml` — `26-widget-uygulandi.md`'ye göre widget şu
  anlık zaten bozuk ve ayrı ele alınacak. `hash32`/`rng32` iki dilde birebir
  olmak zorunda (bkz. o dosyanın "sessiz tuzak" bölümü); **widget düzeltilirken
  `cizCubuk`'un yeni V-kesit mantığı da Kotlin tarafına taşınmalı**, yoksa
  widget ile uygulama farklı çubuk çizer.
- `tasarim/cubuk-laboratuvari.html` ve `tasarim/cubuk-laboratuvari.html`'nin
  eski kopyası `tasarim/cubuk-laboratuvari.html` (laboratuvar) olduğu gibi
  bırakıldı — karşılaştırma için hâlâ açılabilir olması isteniyor.
- Kadran (dairesel sayaç görünümü, `drawStopwatchDial`/`drawPomodoroDial`)
  değişmedi. Bu karar yalnız **çubuğu** (kayıt biçimini) kapsıyor.

## Yapılacaklar (bu dosyadan çıkan)

- [ ] Widget düzeltilirken `WidgetCizer.kt`'a Kertik V-kesit mantığını taşı,
      `widget_renkler.xml`'e genişletilmiş paleti ekle.
- [ ] `tasarim/olustur-simulator.js` ile üretilen `simulator.html`'i yeniden
      koştur — gömülü uygulama artık eskisiyle ayrışmış olabilir (bkz.
      `19-akis-ve-cubuk.md`, "gömülü uygulama kaynakla birebir" testi).
