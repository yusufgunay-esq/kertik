# Uygulama içi deneme penceresi — taşınabilir tasarım

Bu belge tek bir uygulamaya ait değil. Ücretli, reklamsız mobil uygulamalarda
kullanıcıyı açılışta ödeme ekranıyla karşılaştırmadan, uygulamanın kendi saydığı bir
deneme penceresi kurmanın tasarımı. Yeni bir projeye taşırken sondaki kontrol listesi
yeterli; gerekçeleri okumak isteyen için aradaki bölümler var.

---

## 1. Neden

Ücretli uygulamada ödeme ekranını ilk açılışta göstermek, kullanıcıdan bedelini
ödeyeceği şeyi görmeden karar vermesini istemektir. Kullanıcı o an ürünün ne yaptığını
bilmiyor; gördüğü tek şey bir fiyat. Bu yüzden çoğu insan (ben dahil) o ekranı bir
saldırı gibi karşılıyor ve uygulamayı siliyor.

Alternatif, mağazanın deneme teklifini kullanmak. Ama mağaza denemesi de kart bilgisi
ve abonelik onayı istiyor, yani yine bir ödeme akışı. "Ücretsiz" yazsa da kullanıcı
tarafında hissi aynı.

Üçüncü yol: uygulama kendi deneme süresini kendisi sayar. Kullanıcı hiçbir şey
onaylamadan, hiçbir ekran görmeden kullanmaya başlar. Ürünü kullanır, alışır, ne işe
yaradığını görür. Pencere kapandığında karşısına çıkan öneri artık bir bilinmeze değil,
kullandığı ve beğendiği bir şeye ödeme yapma önerisidir. Dönüşüm oranı da bu yüzden
daha yüksek olur, ama asıl mesele o değil: kullanıcıya karşı dürüst olan yol bu.

Bedeli var. Deneme kullanıcısının her isteği para harcıyor ve bu para geri gelmeyebilir.
Bu tasarımın tamamı, o bedeli öngörülebilir bir tavana oturtmakla ilgili.

---

## 2. Tek ilke: pencereyi sunucu sayar

**İstemci pencereyi hesaplamaz. Sadece sunucunun söylediğini gösterir.**

Bu tek cümle, bu tasarımdaki hataların çoğunu önlüyor. İhlal edildiğinde olan şu:
istemci "pencere açık" der ve ödeme duvarını bastırır, sunucu pencereden habersizdir ve
isteği reddeder. Kullanıcı ne duvarı görür ne cevabı alır. Sessizce hiçbir şey çalışmaz,
ve bu hata kullanıcı şikâyet edene kadar fark edilmez, çünkü hiçbir yerde hata görünmez.

İstemcideki yerel hesap tamamen kaldırılmaz, ama görevi değişir: yalnızca sunucuya
**hiç** ulaşılamadığında, ödeme duvarının boş yere açılmasını engeller. Hak vermez.
Hakkı yalnızca sunucu verir.

---

## 3. Pencere neye yazılır

Pencerenin sayacı bir kimliğe yazılır. Hangi kimliğe yazıldığı, bu tasarımın
suistimale açık olup olmadığını belirleyen tek şeydir.

Kötüden iyiye:

| Nereye yazılır | Uygulama silinince | Telefon değişince |
|---|---|---|
| Yerel state / localStorage | sıfırlanır | sıfırlanır |
| SharedPreferences / UserDefaults | sıfırlanır | sıfırlanır |
| Cihaz kimliği (Android `ANDROID_ID`, iOS DeviceCheck) | **kalır** | sıfırlanır |
| Hesap (Google / Apple `sub`) | **kalır** | **kalır** |

Doğru yapı iki katmanlı:

1. **Hesap çıpası (asıl).** Kullanıcı Google veya Apple ile giriş yaptıysa, kimlik
   `g_<sub>` olur. Bu kimlik hesaba bağlıdır; telefon değişse, uygulama silinse de aynıdır.
2. **Cihaz kimliği (yedek).** Hiç giriş yapmamış kullanıcı için. Bölüm 9'daki cihaz
   kimlikleri kullanılmıyorsa bu katman zayıftır ve pencere sıfırlanabilir.

**Zamanı da sunucu yazar.** Pencerenin başlangıcı, istemcinin "ilk kurulum tarihi"
alanı değil, sunucunun o kimliği **ilk gördüğü an** olmalı. İstemcideki tarih yerel
state'te durur ve uygulama silinince gider; sunucudaki kayıt gitmez.

### Çıpa devri (atlanmaması gereken ayrıntı)

Kullanıcı önce anonim başlar, sonra hesabına bağlanır. Kimlik `d:<cihaz>`'dan
`g:<sub>`'a geçer. Yeni kimliğin kaydı yoksa **eski kimliğin kaydı devralınmalı**.

Devralınmazsa: "önce cihazda üç gün kullan, sonra hesabını bağla, üç gün daha" diye
pencere ikiye katlanabilir. Devralınırsa hem bu kapanır hem de dürüst kullanıcının
saati hesabını bağladı diye baştan başlamaz.

---

## 4. Üç sınır, üçü de gerekli

```
GRACE_DAYS   = 3    gün
GRACE_TOTAL  = 40   pencere boyunca toplam istek
GRACE_DAILY  = 15   pencere içinde günlük tavan
```

Üçünün ayrı ayrı işi var:

- **Gün** kullanıcıya verilen sözdür. Anlaşılır ve dürüst: "üç günün var".
- **Toplam** maliyet tavanıdır. Kullanıcıya verilmiş bir söz değil, senin bütçe sigortan.
  En kötü ihtimalle bir kurulumun sana maliyeti `GRACE_TOTAL × birim maliyet`. Leucine'de
  `40 × ~0,0020 USD ≈ 8 sent`. Bu sayıyı bilerek uyuyabilirsin, o yüzden var.
- **Günlük** tavan, pencerenin tamamının tek oturumda yakılmasını engeller. Normal
  kullanıcı bunu hiç görmez; gören kişi zaten normal kullanıcı değildir.

Bu sayıları belirlerken: günlük tavanı **normal kullanımın en az 3-4 katına** koy, yoksa
gerçek kullanıcı çarpar ve pencere vaat ettiği şeyi vermez. Toplamı, kaybetmeyi göze
alacağın kurulum başına maliyetten geriye doğru hesapla.

---

## 5. Sunucu sözleşmesi

### Kayıt

```
KV/DB anahtarı:  grace:<identity>
Değer:           { t: <ilk görülme, ms>, u: <pencerede harcanan istek> }
TTL:             GRACE_DAYS + birkaç gün pay
```

### Pencere hesabı

```
pencere_açık =  değil_abone
             && (şimdi - kayıt.t) < GRACE_DAYS gün
             && kayıt.u < GRACE_TOTAL
```

Kayıt yoksa **o an açılır**. Bu, durum ucunda da yapılmalı: kullanıcı uygulamayı açıp
hiçbir şey yapmasa bile saat işlemeli, yoksa "üç gün" sözü "ilk kullanımdan üç gün"e
kayar ve kullanıcı üç gün sonra açtığında hâlâ tam pencereye sahip olur.

### Günlük limit

```
limit = abone     ? PRO_DAILY
      : pencere_açık ? GRACE_DAILY
      : FREE_DAILY        (ücretsiz kademe yoksa 0)
```

### Hata kodları — burası önemli

Pencere açıkken günlük tavana çarpmak **duvar sebebi değildir**.

| Durum | Kod | İstemci ne yapar |
|---|---|---|
| Pencere açık, günlük tavan doldu | `grace_limit` | "Bugünlük hakkın doldu, yarın devam" der. Duvar açmaz. |
| Pencere kapandı | `free_limit` | Ödeme duvarını açar. |
| Abone, tavana çarptı | `pro_limit` | "Günlük tavan" der. |

İki kodu tek `free_limit` altında toplarsan, kullanıcıya verdiğin "üç gün boyunca hiçbir
uyarı çıkmayacak" sözünü ikinci günün akşamı kendi elinle bozarsın.

### Cevap gövdesi

Hem durum ucu hem de başarılı istekler pencereyi taşımalı:

```json
"grace": { "active": true, "used": 12, "total": 40,
           "dailyLimit": 15, "daysLeft": 2, "endsAt": 1788... }
```

İstemci bunu okur, kendi hesabını yapmaz.

---

## 6. İstemci kuralları

- `pencereDeMi()` yalnızca sunucunun `grace.active` alanını okur.
- Yerel yedek hesap sadece sunucuya hiç ulaşılamadığında devreye girer ve **hak vermez**;
  yalnızca duvarın boşuna açılmasını engeller. Ağ hatası bir kapı olmamalı.
- `grace_limit` kodunu yakalayan **her** çağrı noktası duvar yerine bilgi mesajı
  göstermeli. Uygulamada modele giden kaç yol varsa hepsi. Biri unutulursa duvar oradan
  sızar; bunu test etmenin yolu kodda `openPaywall` çağrılarını tek tek gözden geçirmek.
- Açılışta gösterilen proaktif tanıtım/davet ekranları da pencere açıkken çıkmamalı.
  Bunlar genelde kota kontrolünden geçmez, ayrı bir yolda durur ve gözden kaçar.
- Ekran "bir kez gösterilir" işaretini pencere açıkken **koyma**; yoksa ömür boyu tek
  olan o ekranı kullanıcı hiç görmeden harcamış olursun.

---

## 7. Arayüzde ne gösterilir, ne gösterilmez

**Göster:** kalan gün. "Başlangıç dönemi, 2 günün kaldı."

**Gösterme:** kalan istek sayısı.

Sayıyı göstermek pencereyi tayına çevirir. Kullanıcı her işlemde bir sayacın azaldığını
görürse ürünü serbestçe kullanmaz, ölçer. Alışkanlık kurmasını istediğin dönemde
yapmasını istediğin son şey bu. Toplam adet senin maliyet tavanın, ona verilmiş bir söz
değil; söz olan gün sayısıdır.

Ayrıca pencere açıkken "Abonelik yok" yazmak yanlıştır: kullanıcının o an erişimi vardır.

---

## 8. Suistimal: neyin kapalı, neyin açık

**Kapalı:**
- Telefon değiştirmek (hesaba bağlı kullanıcıda)
- Uygulama verilerini temizlemek
- Önce cihazda kullanıp sonra hesap bağlayarak pencereyi ikiye katlamak
- Her istekte yeni bir kullanıcı kimliği uydurmak (IP tavanı yakalar)

**Açık:** hesabına hiç bağlanmamış kullanıcının uygulamayı silip yeniden kurması.

Bunu kabul ediyorsan zarar sınırlıdır ve hesaplanabilir:

```
kurulum başına en kötü hâl = GRACE_TOTAL × birim maliyet
üstüne IP başına günlük tavan hız sınırı koyar
```

Bu, "birinin sömürebileceği açık" ile "birinin sömürmesinin sana kurulum başına 8 sente
mal olduğu açık" arasındaki fark. İkincisiyle yaşanır. Ama kapatmak istersen:

---

## 9. Açığı tamamen kapatmanın yolları

### a) Cihaz kimliği (önerilen, kullanıcıya sürtünme eklemez)

**Android — `Settings.Secure.ANDROID_ID` (SSAID).** Android 8.0'dan beri bu değer
(uygulama imza anahtarı + kullanıcı + cihaz) üçlüsüne özeldir ve **uygulama silinip
kurulunca değişmez**. Aynı imza anahtarıyla imzalandığın sürece aynı kalır. Yalnızca
fabrika ayarlarına dönüşte değişir. Deneme penceresini cihaza çıpalamak için doğrudan
bunun için biçilmiş kaftan.

```java
String ssaid = Settings.Secure.getString(getContentResolver(), Settings.Secure.ANDROID_ID);
```

Sunucuya ham hâlde değil, **bir tuzla hash'lenmiş hâlde** gönder; kayıtlarında ham cihaz
kimliği tutma. Gizlilik politikasında kötüye kullanım önleme amacıyla kullanıldığını yaz
ve reklam kimlikleriyle ilişkilendirme.

**iOS — DeviceCheck.** Apple bunu tam olarak bu iş için yapmış: cihaz başına iki bit,
uygulama silinse de kalıcı, Apple'ın sunucusunda durur. "Bu cihaz denemesini kullandı"
bilgisini tutmak için kullanılır.

Bu ikisi eklendiğinde silme/kurma döngüsü kapanır ve kullanıcıdan hiçbir şey istemen
gerekmez. Bu tasarımın tercih edilen hâli budur.

### b) Pencerenin devamını girişe bağlamak

Pencere anonim başlar (sürtünme yok), ama ikinci güne veya N'inci isteğe geçmek için
hesap girişi istenir. Sürtünmeyi kullanıcı ürünü zaten beğendikten sonra ekler, ödeme
ekranından çok daha az rahatsız eder. Cihaz kimliği kullanamadığın platformlarda makul.

### c) Baştan zorunlu giriş

Açığı kapatır ama bu tasarımın varlık sebebini de kapatır: kullanıcı yine bir duvara
çarpar, sadece duvarın adı değişmiştir. Önerilmez.

---

## 10. Mağaza politikası notu

Uygulama içi bu pencere, mağazanın "ücretsiz deneme" teklifiyle **aynı şey değildir**.
O bir abonelik teklifidir ve mağaza üzerinden yürür. Bu ise sadece ücretsiz kullanımdır.

İkisini karıştırma:

- Mağaza listelemesinde ve uygulama içi metinlerde bu pencereyi "abonelik denemesi"
  gibi anlatma. "İlk günler ücretsiz" de, "7 gün ücretsiz deneme" deme.
- Uygulama içinde bir gün sayısı yazıyorsan ve o sayı mağazadaki intro offer süresine
  aitse, ikisi **birebir aynı** olmalı. Tutmaması mağaza ret sebebidir. En sağlamı, ekranda
  yazan süreyi mağazadan okunan teklifin gerçek süresinden almaktır, sabit yazmak değil.
- Cihaz kimliği kullanıyorsan gizlilik politikasında amacını belirt.

Bu maddeleri yayınlamadan önce güncel mağaza politikasından teyit et; ikisi de zaman
içinde değişiyor.

---

## 11. Yapma listesi

- Pencereyi istemcide sayma.
- Pencereyi istemcinin "ilk kurulum tarihi" alanına dayandırma.
- Pencereyi yalnızca rastgele üretilmiş yerel bir kimliğe yazma.
- Pencere içi günlük tavanı duvarla karşılama.
- Kalan istek sayısını kullanıcıya gösterme.
- Sunucuya ulaşılamadığında kapıyı açma.
- Uygulama güncellemesinde pencereyi sıfırlama (sunucuda tutulursa bu zaten olmaz).
- Kullanıcı hesabını bağladığında pencereyi baştan başlatma.

---

## 12. Referans uygulama: Leucine (9 Eylül 2026)

| Katman | Dosya | Ne var |
|---|---|---|
| Sunucu | `worker/src/index.js` | `GRACE_DAYS/TOTAL/DAILY`, `grc:<identity>` kaydı, `graceDurumu()`, `graceKullan()`, çıpa devri, `grace_limit` kodu, `/v1/status` içinde `grace` alanı |
| İstemci | `app.js` | `isInHabitGracePeriod()` sunucudan okur, `GRACE_LIMIT` geri çağrısı, plan panelinde kalan gün |
| Yapılandırma | `config.js` | `grace: { days, total, dailyLimit }` — yalnızca çevrimdışı yedek |
| Test | `worker/test.mjs` | süre dolunca kapanma, toplam dolunca kapanma, günlük tavanda `grace_limit`, sayacın kimliğe yazılı olması, hesap bağlanınca devir, aboneye açılmaması |

Leucine'de **henüz yapılmamış** olan: bölüm 9'daki cihaz kimliği katmanı. Yani silme/kurma
açığı orada hâlâ duruyor, kurulum başına ~8 sentle sınırlı.

---

## 13. Yeni uygulamaya taşırken kontrol listesi

1. Sunucuda üç sabiti tanımla; toplamı birim maliyetinden geriye doğru hesapla.
2. `grace:<identity>` kaydını kur; ilk görülme anını **sunucu** yazsın.
3. Kimliği hesaba çıpala; cihaz kimliğini yedek olarak kur (mümkünse bölüm 9a).
4. Çıpa devrini yaz (cihaz → hesap).
5. Limit hesabına pencereyi ekle.
6. `grace_limit` kodunu ayır.
7. Durum ucunun cevabına `grace` nesnesini koy.
8. İstemcide yerel sayımı sil, sunucudan oku.
9. Modele giden **her** yolda `grace_limit` işlensin; `openPaywall` çağrılarını tek tek gözden geçir.
10. Açılış tanıtım/davet ekranlarını pencereye bağla.
11. Arayüzde kalan **günü** göster, sayıyı gösterme.
12. Testleri yaz: süre, toplam, günlük, kimlik kalıcılığı, devir, abone.
13. Mağaza metinlerini bölüm 10'a göre gözden geçir.
