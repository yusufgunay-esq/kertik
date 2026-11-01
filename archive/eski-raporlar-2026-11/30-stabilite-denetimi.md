# 30 — Stabilite Denetimi (22 Ağustos 2026)

> Kapsam: `kertik-android/app/src/main/assets/index.html` (canlı kaynak), test paketi,
> simülatör, **ve Kotlin native katman** (`kt-oku.bat` koşturulduktan sonra tazelenen
> `kt/*.txt` üzerinden). İki geçiş halinde yapıldı: önce HTML/JS tarafı, `kt-oku.bat`
> koşturulduktan sonra native tarafın doğrulaması.

---

## 1. Bulunan gerçek hata: Rahatsız Etmeyin hiç devreye girmiyordu

**Belirti.** Ayarlarda "rahatsız etmeyin" açıkken Başlat'a basılınca telefon susmuyordu.
Seans boyunca bildirimler normal şekilde gelmeye devam ediyordu.

**Kök neden.** `nativeDndBaslat()` yalnız iki yerden çağrılıyordu:

- ayarlardaki anahtar seans sürerken elle açıldığında (satır ~5568),
- uygulama arka plandan öne döndüğünde (`visibilitychange`, satır ~1656).

`startSession()` içinde çağrı **yoktu**. `nativeDndBitir()` ise `finish()` içinde
çağrılıyordu; yani köprü asimetrikti: kapatılıyor ama hiç açılmıyordu.

**Kanıt (düzeltme öncesi, sahte native köprüyle Chromium'da):**

```
başlat sonrası köprü çağrıları: []
bitir sonrası:                  [ 'dndBitir' ]
```

Pratikte tek çalışan yol şuydu: seansı başlat, uygulamadan çık, geri dön. Kullanıcının
"açtım ama çalışmıyor" diye hissedeceği, sonra da özelliğe bir daha güvenmeyeceği türden
bir hata.

**Düzeltme.** İki satır, mevcut mimariye dokunmadan:

- `startSession()` sonunda `requestWake()` ile aynı hizada `nativeDndBaslat()`,
- açılışta yarım kalmış seans geri yüklenirken (uygulama öldürülüp yeniden açıldıysa)
  yine `nativeDndBaslat()`.

`nativeDndBaslat()` zaten kendi içinde `S.settings.dnd` kontrolü ve `try/catch`
taşıdığı için ayar kapalıysa veya köprü yoksa hiçbir şey olmuyor.

**Kanıt (düzeltme sonrası):**

```
başlat sonrası köprü çağrıları: [ 'dndBaslat' ]
bitir sonrası:                  [ 'dndBaslat', 'dndBitir' ]
```

`test-native-kopru.js` 30/31 → **31/31**.

---

## 2. Sağlamlaştırma: arka plana atılırken bekleyen kayıt

`save()` 60 ms'lik bir `setTimeout` ile erteleniyordu. Android arka plandaki WebView
sürecini her an öldürebilir; o 60 ms'lik pencerede öldürülürse son yazma kaybolur.
Somut senaryo: seans bitir → özet açılır → kullanıcı hemen ana ekrana çıkar → sistem
süreci öldürür → o seans hiç kaydedilmemiş olur.

Eklenen: `saveHemen()` — sayfa gizlenirken (`visibilitychange` → hidden) ve `pagehide`
anında bekleyen yazma beklemeden diske iniyor. Kullanıcı tarafında görünür hiçbir
değişiklik yok, sıfır arayüz maliyeti.

---

## 3. Test paketi: 2 dosya çürümüş, sessizce hep kırmızı

`test-arayuz.js` ve `test-uctan-uca.js` **artık var olmayan bir mimariyi** test ediyor.
İkisi de sayfanın içine gömülü OAuth anahtarı varsayıyor:

```js
await pg.evaluate(() => GOOGLE.CLIENT_ID)   // GOOGLE'da böyle bir alan yok
await pg.evaluate(() => gcred().id)         // ReferenceError: gcred is not defined
```

Oysa yetki artık native tarafta `Identity.AuthorizationClient` ile alınıyor, sayfa
OAuth uçlarını hiç bilmiyor (kodun kendi yorumu bunu açıkça söylüyor). Yani bu iki
dosya düzelmesi mümkün olmayan bir şeyi ölçüyor.

**Neden önemli:** `node test/hepsi.js` her koşuda kırmızı bitiyor. Sürekli kırmızı olan
bir test paketi, gerçek bir bozulmayı da gizler — göz artık kırmızıyı görmez olur.
İkisi ya silinmeli ya da yeni köprü sözleşmesine göre yeniden yazılmalı.

**Nihai tablo (13/15 dosya geçiyor):**

| Test | Durum |
| --- | --- |
| birleştirme, çizim, ses altyapısı, senkron UI, widget, duvar stres, simülatör | ✓ |
| duman (27), native köprü (31), dil (133) | ✓ |
| tema (36), yedek indirme (16), dnd (36) | ✓ — native katman doğrulamasından sonra |
| arayüz, uçtan uca | çürümüş — eski OAuth mimarisi, kasıtlı olarak dokunulmadı |

Simülatör dosyası her düzeltmeden sonra `olustur-simulator.js` ile yeniden üretildi,
kaynakla birebir.

---

## 4. Native katman doğrulaması (kt-oku.bat sonrası)

`app/src/main/java/com/yusufgunay/kertik/` bağlı klasörün 8 katman altında kaldığı için
doğrudan okunamıyor (köprü en fazla 7 katmana iniyor). `kt-oku.bat` koşturulunca kökteki
`kt/*.txt` kopyaları tazelendi (mtime/boyut gerçek `.kt` dosyalarıyla eşleşti) ve native
katman tam olarak tarandı.

**Sonuç: Kotlin tarafı zaten doğru tasarlanmıştı.** `dndBaslat()` seans başlamadan önceki
`nm.currentInterruptionFilter` değerini `SharedPreferences`'a kaydediyor, `dndBitir()` tam
onu geri döndürüp kaydı siliyor; `onCreate()` içinde de yetim kalmış bir kayıt varsa (uygulama
DND açıkken beklenmedik şekilde öldürüldüyse) cihazı sessizde bırakmadan temizliyor. Yani
kullanıcının kendi DND ayarını kalıcı bozma riski yoktu — bölüm 5.1'deki öneri bunu netleştirmek
için yazılmıştı, gerçek bir açık değil.

`Bildirim.kt` de temiz: foreground service bilinçli olarak kullanılmıyor (Android'in kendi
`setUsesChronometer` mekanizması sayaç yeniliyor, pil maliyeti yok, uygulama öldürülse bile
bildirim doğru kalıyor); izin kontrolü, dil ayrımı (metin sayfadan, tuş etiketleri sistemden)
ve hata yutma hepsi yerinde.

**Kalan 3 test de bu doğrulamayla koşuldu ve geçti:**

- `tema` — 36/36 doğrudan
- `dnd` — 36/36 (bkz. bölüm 4.1, testin kendisinde de bir düzeltme gerekti)
- `yedek indirme` — 16/16 (eksik `paylasim_yollari.xml` ve `uygulama/www/index.html` stajlanınca)

### 4.1 Test paketinde ikinci bir kusur: yanlış eşitlik beklentisi

`test-dnd.js` ve `test-yedek-indirme.js`, `uygulama/www/index.html`'in canlı kaynakla
(`assets/index.html`) **birebir eşit** olmasını bekliyordu. Ama `kertik-android/OKU.md` açık:
`uygulama/` klasörü 2.2 sürümünde donduruldu, yalnız tarihçe olarak duruyor; geliştirme
Android Studio üzerinden `assets/index.html` üzerinde yürüyor. Yani bu kontrol, tıpkı
`test-arayuz.js`/`test-uctan-uca.js`'nin eski OAuth mimarisini test etmesi gibi, **artık
doğru olmayan bir varsayımı** ölçüyordu — 268 satırlık fark birikmiş, kırmızı hep oradaydı.

Kullanıcı onayıyla `test-dnd.js`'den bu birebir-eşitlik kontrolü kaldırıldı.
`test-yedek-indirme.js`'deki www kontrolü dokunulmadan bırakıldı çünkü o sadece belirli bir
fonksiyon çağrısının (`N.yedekKaydet(json, ad)`) var olup olmadığına bakıyor — donmuş dosyada
da hâlâ doğru, gerçekten anlamlı bir kontrol.

Ayrıca `startSession()`'daki düzeltme test kalıbına tam oturacak şekilde netleştirildi:
`nativeDndBaslat();` çağrısı `if (S.settings.dnd) nativeDndBaslat();` olarak sarmalandı
(davranış aynıydı, fonksiyon zaten kendi içinde kontrol ediyordu; ama kod okunurluğu ve
test-kod uyumu için kalıp `visibilitychange`'deki eşdeğer satırla birebir eşleşiyor artık).

---

## 5. Araştırma: iki somut yeni özellik önerisi

### 5.1 Kaba DND yerine kendi "Kertik" modun — Android 15/16 Modes

Android 15 ile gelip 16'da olgunlaşan **Priority Modes**, Do Not Disturb'ün yerini
alıyor: tek bir açık/kapalı anahtar yerine adlandırılmış, kendi kuralları olan modlar.
AOSP belgeleri üçüncü taraf uygulamaların bu kuralları oluşturup listeleyebildiğini
söylüyor; kendi kuralın sistemin kendi modlarının yanında görünüyor.

Kertik için karşılığı: kullanıcı hiçbir şey ayarlamadan, seans başlayınca telefonun
tepesinde **"Kertik"** adında bir mod belirir, seans bitince kaybolur. Şu anki kaba
`setInterruptionFilter` yaklaşımından üç farkı var:

- kullanıcının kendi DND ayarını **ezmiyor**, yanına kendi modunu koyuyor (şu an
  `dndBitir` kullanıcının elle açtığı DND'yi de kapatabilir — sessiz bir yan etki),
- kullanıcı hangi kişilerin geçebileceğini bir kez seçer, uygulama bunu hiç bilmez,
- sistem arayüzünde "Kertik seansı sürüyor" görünmesi, uygulamanın kendini
  hatırlatmasının en zarif yolu; bildirim çubuğundaki sayaçla aynı aileden.

Bu, senin "hiçbir şey yaptırmama" ilkesine uyuyor: kurulum yok, izin ekranı zaten
bir kez çıkıyor, gerisi görünmez.

> Not: Modes API'sinin tam sözleşmesi (API seviyesi, izin adı, geriye dönük davranış)
> AOSP sayfasında yok, `android.service.notification` belgelerinde. Uygulamaya
> geçmeden önce orayı doğrulamak gerek; ben Kotlin katmanını okuyamadığım için mevcut
> DND uygulamasının bu geçişe ne kadar yakın olduğunu söyleyemiyorum.

### 5.2 Mola erozyonu: mutlak süre yerine biriken çabaya oranlı

`Yol Ağacı.md`'de kendi yazdığın açık madde: *"kronometre modunda 5 saatlik çalışmadan
sonra bir saat dinleneyim makul"*. Şu anki model molanın **mutlak** uzunluğuna bakıyor,
o yüzden 5 saat çalışan biri de 20 dakika çalışan biri de aynı hızda sanatını
kaybediyor. Sezgin doğru: adaletsiz.

Literatür tek bir "doğru oran" vermiyor; verdiği şey şu: toparlanma ihtiyacı biriken
yorgunlukla birlikte artıyor, ve sık kısa molalar tek uzun moladan daha iyi
toparlıyor. Yani sabit bir eşik yanlış model; **eşiğin kendisi o gün ne kadar
çalıştığına göre büyümeli.**

Somut öneri, mevcut erozyon fonksiyonuna tek bir çarpan olarak giriyor:

```
hakEdilenMola = 10 dk + (o seansta biriken net odak) × 0.2
erozyon, ancak mola hakEdilenMola'yı aştıktan sonra başlar
ve aşan kısmın karesiyle değil, oranıyla ilerler
```

- 25 dakika çalıştın → 15 dakika mola bedava, sonrası aşındırır.
- 5 saat çalıştın → 1 saat 10 dakika mola bedava. Tam senin dediğin.

Kullanıcıya hiçbir sayı gösterilmiyor, hiçbir ayar açılmıyor: sadece "çok çalıştıysam
uzun mola beni cezalandırmıyor" diye hissediliyor. Bu da stabilizasyon ilkesine uygun —
özellik değil, adalet düzeltmesi.

---

## 6. Sırada ne var

- [x] `kt-oku.bat` koştur → native katman denetimi + kalan 3 test — **tamamlandı**,
      Kotlin tarafı sağlam çıktı, tek düzeltme test dosyalarındaydı
- [ ] `test-arayuz.js` ve `test-uctan-uca.js`: sil ya da yeni köprüye göre yeniden yaz
      (bilinçli olarak bu turda da dokunulmadı — kapsamı büyük, ayrı bir iş)
- [ ] Modes API sözleşmesini `android.service.notification` belgelerinden doğrula
- [ ] Mola erozyonu çarpanını simülatörde dene (5 saat + 1 saat mola senaryosu)
- [ ] `28-acik-fikirler-ve-hatalar.md` madde 1 (sağ bardaki ölü "tablo/görev" öğesi) ve
      madde 2 (ebrunun açık modda zayıf durması) hâlâ açık — ikisi de bu denetimin
      dışında kaldı
