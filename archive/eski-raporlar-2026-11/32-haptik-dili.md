# 32 — Haptik Dili (uygulandı)

Tarih: 24 Ağustos 2026
İlgili: [24-sanat-dili.md](24-sanat-dili.md) §6.5 (doktrin), [05-ozellik-listesi.md](05-ozellik-listesi.md)

> §6.5 haptik sözlüğünü **yazmıştı** ama kod onu uygulamıyordu. Bu dosya
> aradaki farkı ve kapatılış biçimini kaydeder.

---

## 1. Denetimden önceki durum

Uygulamada 13 titreşim çağrısı vardı, üç ayrı yoldan giden:

| Yol | Nereye gidiyordu | Sorun |
|---|---|---|
| `buzz("click")` | `VibrationEffect.EFFECT_CLICK` | **Jenerik.** Android'in stok haptiği; her uygulamadaki her düğmeyle aynı his. Bizim değil. |
| `buzz([18,35,12])` | `createWaveform(timings, -1)` | **Genlik yok.** Yalnız süreler gidiyordu; her vuruş tam güçte. Zarf, yani "sönümlenme" hiç yoktu. |
| `buzz(10)`, `buzz(11)`, `buzz(12)`, `buzz(8)` | `createOneShot(ms, 190)` | Süreler 8–12 ms, genlik hepsinde sabit 190. Mola, devam, not kaydı ve gezinti **birebir aynı** hissediliyordu. |

Yani §6.5'teki `createWaveform([0,12,40,9], [0,110,0,60], -1)` satırının genlik
dizisi köprüde düşüyordu. Ses tarafında kütleye bağlı `decay`/`gain`
profilleri özenle kurulmuşken (`KUTLE_PROFILLERI`), haptik tarafında hiç
dinamik yoktu.

Ayrıca iki hata:

1. **Çift titreşim.** `buzz()` önce native köprüyü çağırıyor, sonra `return`
   etmeden `navigator.vibrate()` de çağırıyordu. WebView'de ikisi de
   çalıştığı için her dokunuş iki kez titriyordu.
2. **Dönüm noktası doktrine aykırıydı.** §6.5: *"seans sürerken uygulama
   kendiliğinden titremez."* Dönüm noktası `[25,90,25]` ile üç kez
   titriyordu. En hafif tek vuruşa (`donum`) indirildi. Kapatılabilir
   olduğu için tamamen kaldırılmadı.

---

## 2. Karar: doku sözlüğü

Titreşim artık `index.html` içinde tek bir `DOKU` sözlüğünden okunuyor.
Her dokunun **kendi genlik zarfı** var: `t[]` süreler, `a[]` genlikler.
Çift indisler vuruş, tek indisler sessizliktir.

### Elle hissedilenler (parmak ekranda, 9–14 ms)

| Doku | Süre/genlik | His |
|---|---|---|
| `baslat` | `[14] / [120]` | Bıçağın tahtaya ilk girişi — tek, net, biraz derin |
| `mola` | `[10,20,8] / [75,0,30]` | Bıçağın kalkması — yumuşak, sönümlenen |
| `devam` | `[11] / [95]` | Başlat'ın hafifi |
| `bitir` | `[12,40,9] / [110,0,60]` | Kapağın kapanması — iki vuruş, ikincisi hafif |
| `sec` | `[9] / [60]` | Değer seçme, sekme |
| `not` | `[11] / [80]` | Seans notu kaydedildi |
| `donum` | `[9] / [55]` | Dönüm noktası — en hafif tek |

### Maddi olaylar (sanatın kendi dili)

| Doku | Süre/genlik | His |
|---|---|---|
| `pomodoro` | `[22,26,12,34,9] / [190,0,95,0,45]` | **Taşın kuma oturması** — bkz. §3 |
| `kirik` | `[17,12,7,9,5] / [205,0,90,0,45]` | Taşın çatlaması — sert, kısa, düzensiz |
| `kintsugi` | `[8,20,14] / [50,0,125]` | Onarım — **artan** zarf; tek yükselen doku |
| `ruzgar1..3` | kademeli | Mola rüzgârı; kademe arttıkça uzayan alçak dalgalanma |

Kütle profilleri (`KUTLE_PROFILLERI`) de zarf kazandı: Çakıl `[9]/[75]`,
Standart `[14]/[120]`, İri Kaya `[16,20,10]/[150,0,70]`, Ağır Granit
`[20,24,14,18,6]/[178,0,110,0,55]`. Ağır taş gerçekten ağır düşüyor —
ama artık genlikle değil, süre ve vuruş sayısıyla.

---

## 2.1 — 2 Eylül 2026 denetimi ve üç düzeltme

**a) Titreşimi açmak hiçbir şey hissettirmiyordu.** Ayar anahtarında
`buzz("sec")` ayar **değişmeden önce** çağrılıyordu; `buzz()` de
`S.settings.vibrate`'i okuduğu için, titreşimi *açan* kullanıcı hiçbir
onay hissetmiyor, "çalışmıyor" sanıyordu. Sıra düzeltildi: önce ayar,
sonra titreşim. Şimdi açmak onay veriyor, kapatmak sessizleşiyor.
`test-haptik.js` bu sırayı iki yönde de doğruluyor.

**b) `sec`/`not`/`donum` hissedilme eşiğinin altındaydı.** Süreleri 6–8 ms
idi; LRA motorlu cihazların çoğunda tek vuruşun eşiği ~9–10 ms. Yani
**en sık kullanılan doku** (`sec`, 26 `buzz()` çağrısının 12'si) büyük
ihtimalle hiç hissedilmiyordu. Taban 9 ms'e çekildi, hiyerarşi korundu:
`donum < sec < not < devam < kertik/bitir < baslat`. Çok vuruşlu
dokuların sonundaki 5–8 ms'lik yankılar zarfın parçası — ayrı kural,
değişmediler. Test artık **tek vuruşlu** her dokunun ≥ 9 ms olmasını
şart koşuyor.

**c) Başlangıç, bitişten sert vuruyordu.** Ağır Granit `235` genlikle
pomodoro **bitişinden** (`190`) daha güçlüydü — oysa doktrin: *bitiş bir
haberdir, başlangıç bir yüzeydir.* Yüzey haberden güçlü vuramaz. Elle
hissedilen bandın tavanı `178`'e indirildi ve test bu kuralı kalıcı
hâle getirdi: parmak ekrandayken hiçbir doku 190'ı geçemez.

**Hâlâ açık:** `sec` silme, sekme değişimi ve görev ekleme için aynı.
Geri alınamaz bir eylemin gezintiyle aynı hissetmesi sözlüğün tek anlam
boşluğu. Ayrı bir `sil` dokusu (geri çekilen zarf) düşünülebilir —
karar verilmedi.

---

## 3. Pomodoro bitişi — tek istisna

Diğer bütün dokular §6.5'in kuralına uyar: *haptik bir bildirim değil, bir
yüzeydir; yalnız kullanıcının dokunuşuna cevaptır.* Pomodoro bitişi bunun
tek istisnası, çünkü **o an parmak ekranda değil** — telefon cepte ya da
masada, kullanıcı çalışıyor. Burada haptik bir yüzey değil, bir haberdir.

Yine de alarm değil. Doku: net bir darbe (22 ms / 190), sonra iki
zayıflayan yankı (12 ms / 95, ardından 9 ms / 45). Toplam 103 ms.
Kum bahçesindeki taşın kuma oturmasının elle hissedilen karşılığı.

Android 12+ ve destekleyen cihazlarda bu doku donanım primitifleriyle
çalışıyor: `PRIMITIVE_THUD` (1.0) → 45 ms → `PRIMITIVE_LOW_TICK` (0.6) →
50 ms → `PRIMITIVE_LOW_TICK` (0.3). Desteklemeyen cihaz zarflı waveform'a,
genlik denetimi olmayan cihaz düz desene düşer. Üç kademede de titreşim
olur, yalnız dokusu kabalaşır — kullanıcının yapması gereken hiçbir şey yok.

**Reddedilen seçenek:** fark edilmezse 25 saniye sonra tekrar titretmek.
Disiplin için etkili olurdu ama "uygulama beni dürtüyor" hissi verirdi;
`05`'teki "asla yapmayacaklarımız" listesinin ruhuna aykırı. Fark edilmeyen
biti(ş) zaten Ç2'deki onaylanmamış süre teyidiyle kapanıyor.

---

## 4. Kod tarafı

- `index.html` → `DOKU` sözlüğü + yeniden yazılmış `buzz()`.
  `buzz()` artık doku adı (string), `{t,a}` nesnesi, eski dizi ya da eski
  sayı kabul ediyor; hepsini tek yola indiriyor ve **native varken
  `navigator.vibrate`'e asla düşmüyor.**
- `MainActivity.kt` → yeni `titretDoku(sureler, genlikler, komp)` köprüsü
  ve `kompozisyon()` yardımcısı. Eski `titret` / `titretHassas` /
  `titretOnTanimli` / `titretPattern` **duruyor** — eski APK'yla yeni
  index.html ya da tersi bir arada kalırsa titreşim yine çalışsın diye.

## 5. Açık kalan

- ~~**Zil moduna uyum.**~~ **Kapatıldı (2 Eylül 2026): hiçbir şey yapma.**
  Sessiz moda alan kullanıcı zaten titreşim bekler; mevcut davranış
  (sessizde ses yok, titreşim var) doğru. Ayarlarda ikinci kez sormak
  `CLAUDE.md`'deki "kullanıcıya hiçbir şey yaptırmamak" ilkesine aykırı
  olurdu.
- **Gerçek cihazda his denetimi.** Zarflar hesapla kuruldu; Ağır Granit ile
  Çakıl arasındaki farkın gerçekten hissedilip hissedilmediği telefonda
  denenmeli. Emülatörde anlamsız.
