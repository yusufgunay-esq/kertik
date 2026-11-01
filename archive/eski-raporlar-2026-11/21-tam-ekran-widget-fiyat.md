# 21 — Tam Ekran Seans, Widget ve Ödeme Modeli Kararı (16 Ağustos 2026)

Kaynak: birkaç saatlik gerçek kullanım. Bu dosya `20-kullanim-feedback.md`'nin
eksik bıraktığı **davranış** bulgularını ve bunların ürün/fiyat sonuçlarını içerir.
Rakip/fiyat verisi: `tasarim/kertik-rakip-karti.html`

---

## 1. Seans başlayınca tam ekran

**Gözlem:** Sayaç başladıktan sonra diğer sekmeler hâlâ tıklanabiliyor. Bu yanlış geliyor.

**Karar:** Seans başlayınca ekran sadeleşir — alt gezinme çubuğu solar, kadran ve arka
plan çizimi tüm ekranı alır.

**Ama kilit değil.** Ayrım önemli:

- **Forest'ın yaptığı:** çıkarsan cezalandırır. Baskı mekaniği.
- **Kertik'in yapacağı:** çıkmanı zorlaştırmaz, sadece **kendisi çekilir.**

Uygulama fikri "dürüst kayıt", "irade dayatma" değil. Kullanıcıyı kilitlemek, ürünün
reddettiği ton. Doğru davranış: gezinme gizlenir, geri getirmek için bilinçli bir hareket
gerekir (alttan yukarı kaydırma veya kadrana tek dokunuş). Sürtünme var, duvar yok.

**Yan kazanç:** Bu değişiklik `20-sanat-geri-bildirim.md`'deki çizim şikâyetlerini de
doğrudan çözüyor — çizim artık gerçekten tüm ekranda yaşıyor.

**Uygulama notları:**
- Android geri tuşu seansı bitirmemeli; önce gezinmeyi geri getirmeli.
- Geçiş sert olmamalı — 400–600 ms soluş. ("Küt diye" belirme şikâyeti aynı sebepten.)
- Ekran açık kalma (`keep screen on`) ayarı bu modda anlam kazanıyor, ayarlarda seçenek olsun.

---

## 2. Uygulamaya geri dönülmüyor — en önemli bulgu

**Gözlem (kelimesi kelimesine):** *"Ben bu uygulamayı açtıktan sonra tekrar bu uygulamaya
dönmüyorum genel olarak."*

Bu, `13-bulgular.md`'nin aradığı türden ilk gerçek bulgu. Ve tek bir şeyi söylüyor:
**uygulamanın kendi dışında bir yüzü yok.** Görünmeyen alet unutulur.

İki çözüm, ikisi de yapılacak:

- **Ana ekran widget'ı** — telefonun ana ekranında duran, açmadan görülen yüz.
- **Bildirim çubuğunda canlı sayaç** — zaten var ama ham hâlde; seans sürerken
  güvenilir biçimde görünmeli.

**İkisi de ücretsiz/ücretli tartışmasının dışında** — bkz. bölüm 3, artık katman yok.

---

## 3. ÖDEME MODELİ KARARI: peşin, tek seferlik, katmansız

`16-para-kazanma.md` "ücretsiz çekirdek + tek seferlik açılış" (freemium) diyordu.
**Bu model iptal.**

**Gerekçe (Baki, 16 Ağustos):** *"Uygulamayı para vermeyenler de kullansın kısmı bana
göre gelmiyor, ucuz hissettiriyor."*

Bu estetik bir itiraz değil, **stratejik olarak da doğru.** Freemium'un bedeli:
arayüzde kilit ikonları, yükseltme ekranları, "bu özellik Kertik Tam'da" mesajları.
Bir arayüzü ucuz gösteren şey tam olarak budur.

### Değerlendirilen üç model

| Model | Karar | Sebep |
|---|---|---|
| Freemium (ücretsiz çekirdek + ücretli ekstralar) | **Hayır** | Kilitli arayüz ucuz gösteriyor. Ayrıca ücretsiz katmanı zayıflatma baskısı doğuruyor. |
| Ücretsiz indirme + abonelik duvarı (Apple Music mantığı) | **Hayır** | Aşağıda. |
| **Peşin ödemeli, tek seferlik, her şey dahil** | **EVET** | Aşağıda. |

### Abonelik neden hayır — asıl sebep

**Abonelik kiracılıktır. Lüks sahip olunandır.**

Statü nesnesi kiralanmaz. Rolex, Leica, iyi bir defter — hepsi **satın alınır.**
Aylık fatura gelen hiçbir şey "benim" hissi vermez; her ay hatırlatılan şey ürünün
değeri değil, **ev sahibinin varlığıdır.** "Minimalist lüks niş" hedefiyle abonelik
aynı cümlede duramaz.

Yardımcı sebepler:

- **Sürekli bir maliyet yok.** Uygulama telefonda çalışıyor, Drive `appDataFolder`
  bedava, tazelenen içerik yok. Aboneliğin karşılığı gösterilemiyor.
- **Kategori az önce bunu yaptı ve kullanıcı kızgın.** Forest **Aralık 2025'te**
  aboneliğe geçti (tüm platformlarda, iOS dahil; Pro tek seferlik yeni kullanıcılara
  kapatıldı). Session ~4,99 $/ay, TickTick 3,99 $/ay, Focus Keeper 3,99 $/ay.
  Tek seferlik taraf boşaldı — Nudge 6,99 $, Be Focused Pro 19,99 $ kaldı.
  Aboneliğe geçmek, **elimize yeni geçmiş tek farkı geri vermek** olur.
- **Solo geliştirici yükü.** Yenileme, iptal, iade, ödeme başarısızlığı, kesinti
  duyurusu — hepsi süregiden iş. 27 Eylül'de sınav var.
- **Apple Music karşılaştırması yürümüyor.** Apple'ın başka yerde bulunmayan bir
  kataloğu ve dünyaca bilinen markası var. Sıfır yorumlu bir uygulamanın açılışta
  sert duvar koyması, indirenlerin on saniyede silmesi ve tek yıldız bırakması demek.

### Peşin ödemenin sonuçları — dürüstçe

**Kazanç:**
- Arayüzde **tek bir kilit ikonu yok.** Her şey açık. Ucuzluk hissinin kaynağı ortadan kalkıyor.
- Uygulama içi satın alma yok, yükseltme ekranı yok, "premium" rozeti yok.
- Fiyat ilk temasta konumlandırma yapıyor: indiren herkes **alıcı.**
- `16-para-kazanma.md`'deki "neyi ücretli yapalım" tartışmasının tamamı düşüyor.
  Ayna, widget, DND, paylaşım kartı — hepsi dahil.

**Bedel — kabul ediliyor:**
- **İndirme sayısı çok düşük olacak.** Peşin ödemeli uygulamalar bedavayla yarışamaz.
- **Yorum azlığı.** Mağaza sayfası uzun süre ıssız görünecek; ilk yorumlar kritik.
- **Viral döngü yok.** Sosyal katman zaten yok, bedava kullanıcı da olmayınca ağızdan
  ağıza yayılma yavaş.
- Bu, bilinçli olarak seçilen bir takas: **az sayıda, doğru kullanıcı.**

### Deneme meselesi çözülü — Play iadesi

Peşin ödemeli uygulamada "denemeden alamıyorum" itirazının cevabı var:
**Google Play satın almadan sonraki kısa pencerede otomatik iade veriyor.**
Bu, ayrı bir ücretsiz katman kurmadan denenebilirliği sağlıyor.
Mağaza açıklamasına açıkça yazılmalı — güven artırır, "gizli bir şey yok" der.
*(Yayın öncesi Play Console'daki güncel iade politikasından teyit edilecek.)*

---

## 4. Fiyat: 9,99 dolar peşin

Önceki not 6,99 diyordu; **ücretsiz katman kalktığı için rakam yükseldi.**
Gerekçe: 6,99 bir *yükseltme* fiyatıydı (zaten kullanan kişiye satılır). Şimdi
rakamın işi farklı — **ilk temasta konumlandırma yapıyor.** İndiren herkes alıcı
olduğu için fiyat, mağaza sayfasındaki en güçlü sinyal.

- Be Focused Pro **19,99 $** peşin — sade bir pomodoro sayacı, satıyor. Tavan orada.
- Nudge **6,99 $** — taban orada.
- Forest Plus bir yıl ~60 $. 9,99 $ bunun **altıda biri**, ve bir kere.
- Structured ömürlük **99,99 $** (2021'de 29,99 $) — olgunlaşınca fiyat artırılabiliyor.
- 9,99 $ "impuls alım" bandının üstünde, "düşünülmüş alış" bandında. İstenen his bu.

**Türkiye:** Play'in ülke bazlı fiyatlandırmasıyla belirgin düşük yerel rakam.
Structured da satın alma gücüne göre fiyatlıyor. Yayın anında Play Console'un o günkü
önerisine bakarak yuvarlak bir rakam seçilecek.

**Lansmanda indirim yok.** İndirimle açılan uygulama tam fiyata dönemiyor.
Fiyat sonradan **artırılabilir** (Structured yolu); ucuz başlayan marka algısı düzelmez.

---

## 5. `16-para-kazanma.md` iki yerden geçersiz

**a) Rakip verisi eskimiş.** O dosya "kategori lideri abonelik almıyor, Forest Android'de
1,99 $ tek seferlik" diyor. **Aralık 2025'te** Seekrtech Forest'ı ücretsiz indirme +
Forest Plus aboneliğine geçirdi; geçiş tüm platformlarda. Forest Pro tek seferlik yeni
kullanıcılara kapalı, eski sahipler hakkını koruyor.

> Not: calmevo gibi ikincil inceleme siteleri hâlâ eski "Android 1,99 $" bilgisini
> veriyor. Birincil kaynaklarla çelişiyor, güvenme.

**b) Model kararı değişti.** O dosyadaki "Çekirdek ücretsiz / Kertik Tam ücretli"
tablosu artık geçerli değil. **Katman yok, her şey dahil, peşin ödeme.**

`16-para-kazanma.md`'nin hâlâ geçerli kısımları: aylık aboneliğe karşı gerekçeler,
Play Console şartları (25 $ hesap, 12 testçi × 14 gün, API 36, gizlilik politikası,
Data Safety, 100 $ ödeme eşiği, vergi), zamanlama.

**Not:** Peşin ödemeli uygulamada da kapalı test şartı geçerli; testçiler test
kanalında ücret ödemeden erişir.

---

## 6. "Premium hissetsin" — doğru içgüdü, ama iki kelimeyi ayır

- **Premium = zanaat.** Reklam yok, seri baskısı yok, karanlık desen yok, tek vurgu
  rengi, gereksiz ekran yok, **kilit ikonu yok.** Ürün zaten bu; peşin ödeme bunu
  tamamlıyor.
- **Statü = gösteriş.** Statü *görülmeyi* gerektirir: paylaşım, rozet, sosyal katman.
  Kertik'te bunların hiçbiri yok ve bilinçli olarak olmayacak. Bu yolu kovalarsan
  ürünün reddettiği şeyi inşa etmeye başlarsın.

Doğru his: **iyi bir defter.** Kimse görmez, sen bilirsin.
İyi defter karmaşık değildir — bu yüzden "premium" hedefi ile **"annem bu ekranda
kaybolur mu?"** filtresi çelişmiyor, aynı yere bakıyor. Sadelik burada lüks göstergesi.

*(Davetiye/referans ile satış fikri: eğlenceli ama Play'in dağıtım modeliyle uyuşmuyor
ve 12 testçi şartını çözmüyor. Aynı hissi fiyat + kilitsiz arayüz zaten veriyor.)*

---

## Yapılacaklar sırası

1. **Tam ekran seans modu** — gezinme solar, çizim ekranı alır, geçiş yumuşak.
2. **Bildirimde canlı sayacın güvenilir hâle gelmesi.**
3. **Basit ana ekran widget'ı.**
4. Çizim düzeltmeleri — `20-sanat-geri-bildirim.md`.
5. `13-bulgular.md` doldurulmaya devam.
6. i18n altyapısı + İngilizce — `22-coklu-dil.md`.
7. Sınavdan sonra (27 Eylül 2026) native/Play süreci.
8. Fiyat ve mağaza sayfası — en son.
