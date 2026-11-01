# Kertik — "içine siniyor mu" denetimi ve düzeltme planı

## Özet ve kapsam

Amaç: uygulamanın geneliyle yeni eklenen algoritmaların (Ebru akış, Zen taşları,
Kum Bahçesi, arka plan tohumu) ve deneme çapasının koda gerçekten "sinip sinmediğini"
kanıtlamak; bulunan boşlukları düşük riskli, küçük adımlarla kapatmak.

Denetim kaynakta, Kotlin köprüsünde ve tam test koşusunda yapıldı. Sonuç: **algoritma
katmanı sağlam ve kilitli estetik dile uygun.** İki gerçek sorun var, ikisi de
uygulamanın çalışan yüzeyinde değil:

1. Test tezgâhındaki sahte canvas, kum taşı çiziminin kullandığı `quadraticCurveTo`'yu
   bilmiyor; bu yüzden `--hizli` koşusu hata basıyor (test arayüzü boşluğu, cihazdaki
   gerçek canvas'ta yok).
2. Deneme çapasının kurcalamaya dayanıklı hâli (SSAID + imzalı uzak çapa) henüz
   yazılmamış; kod hâlâ `localStorage` + cihaz saatine dayanıyor.

Kapsam: Faz 1 (bu planda uygulanacak) + Faz 2 (yayın öncesi, ayrıca onaylanacak).

---

## Denetim sonuçları (kanıt)

### Sağlam, dokunulmayacak

- **Tohum determinizmi doğru kurulmuş.** `hash32` (FNV-1a) + `rng32` (mulberry32)
  sabit ve deterministik (`index.html:2907-2912`). `vnoise`/`fbm` değer gürültüsü
  üzerine kurulu (`:3575-3581`), `Math.random` yok.
- **Arka plan tohumu üç yüzeye de gerçekten işlenmiş:**
  - Ebru: `seansTohumu()` → `se.tohum` (`:1296`), `akisBaslat` (`:3721`), `seansResmi` (`:5733`).
  - Zen taşları: `seansTohumu()` duvar taşı çiziminde (`:3458`).
  - Kum Bahçesi: `hash32(KOK_TOHUM + "|kum|" + gun)` (`:4185`) ve `KUM.tohum` (`:5285`).
  - Kök metin `KOK_TOHUM` tek noktada tanımlı (`:2920`), her yer oradan besleniyor.
- **Eski seans geriye dönük uyumu korunuyor.** `se.tohum` saklanıyor, `akisV` damgası
  (`:1294`) eski seansları eski sürüme bağlıyor; algoritma değişse bile eski resim bozulmaz.
- **Performans bütçesi var.** `akisBaslat` 1400 ms eşiğini aşınca desenden vazgeçiyor
  (`:3726`), kademeli sıklaşma `KD.butce` ile kesiliyor (`:3849`). Kum bahçesi alanı
  `Float32Array` ile tek geçişte kuruluyor (`kumAlanKur`).
- **Çalışan yüzey bozulmuyor.** 94 çizim + 30 ses + haptik + birleştirme testinin
  tüm önermeleri yeşil; hatalar yalnız sahte canvas'tan geliyor.

### Bulunan sorunlar

1. **Test tezgâhı boşluğu (asıl düzeltme).** `test-cizim.js:21` `sahteCtx()` gerçek
   `CanvasRenderingContext2D`'nin yalnız bir kısmını taklit ediyor. `kumTasYolu`
   (`index.html:3665`) `g.quadraticCurveTo` çağırıyor; sahte nesnede yok, bu yüzden
   kum/pomodoro çizim yollarında `TypeError: g.quadraticCurveTo is not a function`
   basılıyor. Cihazdaki WebView canvas bu metodu destekliyor, yani bu **çalışma
   zamanı hatası değil, test arayüzü boşluğu** (kalıtsal, bu oturumda üretilmedi).
2. **Deneme çapası yazılmamış.** `antigravity/deneme-capasi/00-GOREV-deneme-capasi.md`
   durumu "yazılmadı". Mevcut kod (`index.html:2401-2439`) denemeyi `kertik.kurulum`
   + `now()` ile sayıyor; kaldır/veri temizle/saat oynatma yolları açık. Yayından önce
   kapanması gereken, kendi sözleşmesi olan ayrı bir iş (Faz 2).

### İkincil (düşük öncelik, isteğe bağlı)

- `startSession` içinde tam dua metni `console.log` ile basılıyor (`:1299-1301`).
  Kullanıcıya görünmüyor ve WebView hata ayıklama yalnızca DEBUG'da açık
  (`MainActivity.kt:103`); yine de sürüm derlemesinde gereksiz. DEBUG'a bağlamak temiz olur.

---

## Karar verilen işler

- **Faz 1 (şimdi):** test tezgâhını düzelt, algoritma stres testini ekle, DEBUG log
  kapısını koy. Algoritmaların kendisine dokunma.
- **Faz 2 (yayın öncesi, onayla):** deneme çapası. Ayrı bir sözleşmesi var
  (`antigravity/deneme-capasi/00-GOREV-deneme-capasi.md`); bu planda yalnız kapsam ve
  kabul kriterleri özetleniyor, uygulaması ayrıca onay bekler.

---

## Tasarım yönü

- En küçük değişiklik ilkesi: çalışan algoritma koduna dokunulmaz, yalnız test
  taklitleri ve yeni test dosyası eklenir.
- Faz 1'de `index.html`'e yalnız bir satırlık DEBUG kapısı dokunur; başka hiçbir
  üretim davranışı değişmez.
- Faz 2 mevcut `antigravity/deneme-capasi` görev emrine uygun gider; kendi
  dosyalarını (`worker/`, `Deneme.kt`) açar, `Kasa.kt`'ye dokunmaz.

---

## Dosya bazında adımlar

### Faz 1 — test tezgâhı + stres testi

1. `kertik-android/test/test-cizim.js`
   - `sahteCtx()` içindeki sahte bağlamı, `kumTasYolu`'nun kullandığı
     `quadraticCurveTo` (ve gerekiyorsa `bezierCurveTo`, `arc`, `arcTo`) metotlarını
     `no-op`/kayıt eden yapıyla genişlet.
   - Kabul: `--hizli` koşusunda `quadraticCurveTo` kaynaklı hiçbir `TypeError` kalmaz.

2. `kertik-android/test/hepsi.js`
   - Koşunun gerçek çıkış kodunu doğrula; sahte canvas hatasından ötürü sürecin
     sıfırdan farklı dönüp dönmediğini tespit et. Dönüyorsa, sahte bağlam düzeltmesiyle
     yeşile döndüğünü kanıtla.
   - Kabul: `node test/hepsi.js --hizli` exit code 0 (CLAUDE.md'deki kalıcı kırmızılar hariç).

3. `kertik-android/test/test-algoritma-stres.js` (yeni)
   - `test-cizim.js`'deki kurulum kalıbını yeniden kullan (JSDOM + sahte context).
   - Ekleyecek önermeler:
     - **Determinizm:** aynı `dayKey` + aynı seans listesi aynı kum bahçesi imzasını
       (`KUM.imza`) ve aynı `akisAlan` çıktısını üretir; tekrar çizimde kayma yok.
     - **Uzun kronometre seansı (6 saat):** kademe ilerlemesi çalışır, hiçbir şerit
       koordinatında `NaN`/`Infinity` yok, `akisV` damgası korunur.
     - **Kalabalık gün (30 pomodoro):** `kumTasUret` tüm taşları üretir, taş merkezleri
       tuval sınırı içinde kalır, komşu güne taşma yok.
     - **Boş gün / tek taş gün:** bahçe kurulur, çizgi planı bozulmaz.
     - **Bütçe:** `akisBaslat`'ın 1400 ms eşiği ve kademe `KD.butce` yolunun çağrıldığı,
       sahte `performance` ile zorlanarak doğrulanır (aşırı yavaşlıkta desenden vazgeçer).
   - Kabul: yeni dosya `hepsi.js`'e bağlanır, `--hizli` içinde 0 hata.

4. `kertik-android/app/src/main/assets/index.html`
   - `:1299-1301` bloğunu yalnızca hata ayıklama bayrağına bağla (mevcut DEBUG kapısı
     varsa onu kullan; yoksa `BuildConfig` karşılığı sayfa bayrağından oku).
   - Kabul: sürüm derlemesinde dua metni loga düşmez, davranış başka hiçbir yerde değişmez.

5. Simülatör ve kanıt
   - `index.html` değiştiği için `node simulasyon/olustur-simulator.js` koş.
   - Koşu çıktısını ve (mümkünse) simülatör ekran görüntüsünü kanıt olarak kaydet.

### Faz 2 — deneme çapası (ayrı onay)

Sözleşme ve tam kabul kriterleri `antigravity/deneme-capasi/00-GOREV-deneme-capasi.md`'de.
Bu plan yalnız sırayı sabitler:

1. `worker/` — Cloudflare Workers + KV, `POST /deneme`, ECDSA P-256 imza, `worker/README.md`.
2. `app/src/main/java/com/yusufgunay/kertik/Deneme.kt` (yeni) — SSAID okuma, tuzlu özet,
   imza doğrulama, `elapsedRealtime` ile süre; `Kasa.kt`'ye dokunulmaz.
3. `index.html` — `kurulumAni()` köprüden beslenir, katman 3 (kayıt tanıklığı) eklenir,
   `K_PROVA` sürümde devre dışı.
4. Drive çapası (katman 2) ve kabul kriterlerinin 15 maddesinin koşulması + `kanit/`.

Faz 2 bu planda **uygulanmaz**; yalnız kayıt altına alınır ve ayrıca onaylanır.

---

## Doğrulama

- `node kertik-android/test/hepsi.js --hizli` → exit code 0, `quadraticCurveTo` hatası yok
  (kalıcı kırmızılar hariç).
- `node simulasyon/olustur-simulator.js` → simülatör yenilenir, hata yok.
- Yeni `test-algoritma-stres.js` önermelerinin tümü yeşil.
- Faz 1'de üretim algoritma kodunda (`akisAlan`, `akisSira`, `kumKur`, `tasSvg`, `hash32`,
  `rng32`, `fbm`) **sıfır değişiklik** olduğu diff ile doğrulanır.

---

## Varsayımlar

- Gerçek Android WebView `CanvasRenderingContext2D`'de `quadraticCurveTo`'yu destekler;
  bu nedenle hata yalnız test tezgâhına aittir (kanıt: yığın izi sahte context üzerinden
  `kumTasYolu`'na iner; cihaz yüzeyinde aynı yol yayındaki görselle çalışıyor).
- Deneme çapası yayınlanmadan önce kapatılması gereken ayrı bir iştir ve Faz 2 onayı
  bu planın parçası değildir.

---

## Riskler

- Sahte context genişletmesi eksik kalırsa başka bir canvas metodu benzer `TypeError`
  üretebilir; çözüm, gerçek context'in kullanılan metot kümesini tek tek taklit etmektir
  (adım 1'de kapsanır).
- Faz 1'de `index.html`'e eklenen DEBUG kapısı, mevcut bayrağın adı/erişimi yanlış
  okunursa sürümde logu yanlışlıkla açabilir; kabul kriteri bunu açıkça yasaklar.
- Faz 2 ertelenirse sil/kur + veri temizle + saat oynatma ile deneme sıfırlanabilir;
  yayın öncesi açık risk olarak durur.

---

## Kapsam dışı

- Ebru / Zen / Kum algoritmalarının görsel veya performans yeniden yazımı.
- Compose'a geçiş, mimari yenileme, `Kasa.kt` satın alma akışının değiştirilmesi.
- Rozet, seri, bildirim, analitik, abonelik (CLAUDE.md §7'de zaten yasaklı).
- Faz 2'nin bu turda uygulanması.
