# Görev: Deneme Çapası (kaldırma, veri temizleme ve saat oynatmaya dayanıklı deneme)

**Veren:** Claude (analiz)
**Yapan:** Antigravity (uygulama)
**Onay:** Yusuf
**Durum:** yazılmadı

Bu dosya bir görev emridir, tartışma değil. Karar verilmiştir. Aşağıdaki
davranış aynen istenmektedir; mimari tercihlerde serbestsin, sözleşmede ve
kabul kriterlerinde değilsin. Bir madde sana yanlış geliyorsa uygulamadan önce
Yusuf'a sor, kendi kararınla değiştirme.

Bağlam için önce oku: `CLAUDE.md`, `Fiyat.md`, `16-para-kazanma.md`,
`37-kertik-tam-kod.md`.

---

## 1. Problem

Deneme başlangıcı `index.html` içinde `localStorage`'ta `kertik.kurulum`
anahtarında tutuluyor. Bu yüzden deneme dört ayrı yoldan sıfırlanabiliyor:

1. Uygulamayı kaldırıp yeniden kurmak. (Otomatik yedeği açık kullanıcıda
   `yedekleme_kurallari.xml` `app_webview` içerdiği için çoğunlukla çalışmaz.)
2. Ayarlar üzerinden "Verileri temizle". Geri yükleme yalnız kurulum anında
   çalıştığı için yedek devreye girmez. Kaldırmaktan kolay ve tamamen açık.
3. **Yedekle, temizle, geri yükle.** `kertik.kurulum` bilerek `S`'in dışında
   tutulduğu için bulut yedeği geçmişi geri getirir, denemeyi getirmez.
   Kullanıcı hem kaydını korur hem denemeyi sıfırlar. En ciddi delik budur.
4. Cihaz saatini geri almak. `now()` cihaz saatidir; zamanın kaynağı cihazda
   olduğu sürece çapa nereye konursa konsun duvar geçersizdir.

Uygulama henüz yayınlanmadı. Bu iş yayından **önce** kapanmalıdır.

## 2. Mevcut kod (doğrula, satır numaraları kayabilir)

| Yer | İçerik |
| --- | --- |
| `assets/index.html` ~2395 | Blok yorumu. **Eski freemium modelini anlatıyor, kod ile çelişiyor.** Düzeltilecek |
| `assets/index.html` ~2401 | `DENEME_GUN = 14`, `K_KURULUM = "kertik.kurulum"`, `K_PROVA` |
| `assets/index.html` ~2421 | `kurulumAni()`: anahtar yoksa `now()` yazar |
| `assets/index.html` ~2427 | `denemeKalanGun()` |
| `assets/index.html` ~2433 | `tamMi()`: prova, sahiplik, köprü yokluğu, deneme |
| `assets/index.html` 1272 | `startSession()` girişindeki sert duvar |
| `assets/index.html` ~2586 | `kasaDenemeKontrol()` |
| `kt/Kasa.kt` | Play Billing, sahiplik gölgesi `SharedPreferences`'ta, WebView köprüsü |
| `res/xml/yedekleme_kurallari.xml` | `app_webview` ve `sharedpref` dahil |

`MainActivity.kt:103` WebView hata ayıklamayı yalnız `BuildConfig.DEBUG`'da
açıyor. Bu doğru, böyle kalsın.

## 3. Karar

Üç katman. Birincisi asıl çözüm, diğer ikisi bedava taban.

### Katman 1: SSAID artı imzalı uzak çapa (asıl çözüm)

Kullanıcıya hiçbir şey sorulmaz. Giriş yok, izin yok, yeni ekran yok.

- Kimlik: `Settings.Secure.ANDROID_ID` (SSAID). İmza anahtarı başına sabittir,
  uygulama kaldırılınca sıfırlanmaz, yalnız fabrika ayarında değişir.
- Ham SSAID hiçbir yere gönderilmez. Gönderilen: `SHA256(SSAID + gömülü tuz)`.
- Sunucu bu özet için ilk görülme anını tutar ve **imzalı** döner.
- Kalan gün, sunucunun verdiği `simdi` ile `baslangic` farkından hesaplanır.
  Cihaz saati hesaba hiç girmez.

### Katman 2: Drive gizli klasöründe ikinci çapa

Yedek için Drive'a zaten bağlanan kullanıcıda aynı çapa `appDataFolder`'a da
yazılır. Fabrika ayarını ve cihaz değişimini de kapatır. Yeni izin gerekmez,
mevcut yetkinin içindedir. Bağlanmayan kullanıcı için sessizce atlanır.

### Katman 3: Kayıt tanıklığı

Çapa yoksa ama kayıtta `DENEME_GUN` günden eski seans varsa deneme bitmiş
sayılır. Bu, yedekle aklama yolunu sunucu hiç devreye girmeden kapatır.
Geçmişi olmayan temiz kurulum her zaman tam süre görür, yani kimse haksız
kilitlenmez.

**Etkin başlangıç = bu üç kaynaktan gelen tarihlerin en eskisi.** Birleşmede
daima eski tarih kazanır. Hiçbir kaynak yeni bir tarihle eskisini ezemez.

## 4. Sunucu sözleşmesi

Cloudflare Workers artı KV, ücretsiz katman. Başka sağlayıcı kullanacaksan önce
sor.

**Uç nokta:** `POST /deneme`

İstek:
```json
{ "id": "<64 karakter hex>", "v": 1 }
```

Yanıt (200):
```json
{ "baslangic": 1788600000000, "simdi": 1788700000000, "imza": "<base64>" }
```

- `imza`: `id + ":" + baslangic + ":" + simdi` dizesinin **ECDSA P-256,
  SHA256withECDSA** imzası. Özel anahtar Worker gizli değişkeninde, uygulamada
  yalnız açık anahtar gömülü. Ed25519 kullanma; `minSdk` uyumu için P-256.
- KV şeması: anahtar `d:<id>`, değer başlangıç zaman damgası. Başka hiçbir şey
  yazılmaz. IP, kayıt, olay, sayaç tutulmaz.
- Geçersiz `id` biçimi: 400. Yöntem yanlışsa 405.
- Ücretsiz katman sınırı günde bin yazma; yazma yalnız ilk temasta olur.
  Cloudflare tarafında IP başına hız sınırı açılacak.
- Sunucu kodu bu klasöre `worker/` altına konacak, dağıtım adımları
  `worker/README.md` içinde yazılacak. Gizli anahtar depoya girmeyecek.

## 5. İstemci

Yeni Kotlin dosyası: `Deneme.kt`. `Kasa.kt` dokunulmadan kalır; sahiplik ile
deneme ayrı sorumluluklardır, birbirine karıştırılmayacak.

Sorumlulukları:

1. SSAID oku, özetle, uç noktaya sor.
2. Yanıtın imzasını açık anahtarla doğrula. **İmza geçersizse yanıt yok
   sayılır.** Doğrulama Kotlin tarafında yapılır, WebView'e yalnız sonuç iner.
3. Doğrulanmış `baslangic` değerini `SharedPreferences`'a yaz. Yazarken eski
   tarih kazanır kuralı uygulanır.
4. Açılış sonrası geçen süreyi `SystemClock.elapsedRealtime()` ile say; cihaz
   duvar saatine hiçbir yerde güvenme.
5. Sayfaya köprüden `{ baslangic, simdi, dogrulandi }` ver. `index.html`
   `kurulumAni()` yerine bu değeri kullanacak; köprü yoksa (tarayıcı,
   simülatör) bugünkü davranış aynen sürecek, orada kilit anlamsızdır.

`index.html` tarafında:

- `kurulumAni()` köprüden gelen değeri esas alır, yereli yalnız köprü yokken
  kullanır.
- Katman 3 kuralı eklenir: çapa yokken kayıttaki en eski seans tarihi
  `DENEME_GUN` günden eskiyse deneme bitmiş sayılır.
- ~2395'teki eski freemium yorumu, kodun gerçeğiyle değiştirilir: on dördüncü
  günden sonra `startSession()` açılmaz, çekirdek kayıt ve geçmiş yerinde kalır.
- `K_PROVA` yalnız hata ayıklama derlemesinde çalışacak. Sürüm derlemesinde
  köprüden gelen bir bayrakla tamamen devre dışı bırakılacak.

## 6. Çevrimdışı ve kesinti kuralları

Bu tablo pazarlık konusu değildir. Amaç iki yönlüdür: hile kapanacak, ama
senin kesintin dürüst kullanıcıyı asla kilitlemeyecek.

| Durum | Davranış |
| --- | --- |
| Doğrulanmış çapa var, sunucuya erişilemiyor | Yerel çapayla devam, süresiz. Hiçbir şey değişmez |
| Çapa yok, sunucuya erişilemiyor | Yirmi dört saatlik geçici deneme ver, arka planda denemeye devam et. Bu süre içinde tek bir başarılı yanıt gelmezse duvar |
| Sunucu deneme bitti diyor | Bitti. Yerel ne derse desin |
| Sunucu hata veya bozuk yanıt | Erişilemiyor sayılır. Kullanıcı aleyhine düşülmez |
| Sahiplik var | Deneme hiç sorgulanmaz. Satın almış kullanıcı ağa hiç çıkmadan çalışır |

Son satır kritik: **ödemiş kullanıcı hiçbir koşulda ağ yüzünden engellenmez.**

## 7. Kabul kriterleri

Her biri kanıtlanacak. İddia yeterli değil; test çıktısı, log veya ekran
görüntüsü istenir.

1. Kur, üç gün ileri sar, kalan on bir gün görünür.
2. Uygulamayı kaldır, yeniden kur: kalan gün **aynı yerden** devam eder.
3. Verileri temizle: kalan gün aynı yerden devam eder.
4. Yedek al, verileri temizle, yedeği geri yükle: geçmiş geri gelir, deneme
   **sıfırlanmaz**.
5. Cihaz saatini bir ay geri al: kalan gün değişmez.
6. Cihaz saatini bir ay ileri al: kalan gün değişmez.
7. Uçak modunda temiz kurulum: uygulama açılır ve çalışır, yirmi dört saat
   sonra ağ hiç gelmediyse duvara çarpar.
8. Deneme ortasında sunucu kapalı: kullanıcı hiçbir fark hissetmez.
9. Sahiplik varken sunucu kapalı ve uçak modu: her şey açık.
10. On dördüncü gün: `startSession()` duvarı açılır, kayıt, geçmiş, yedek ve
    dışa aktarma erişilebilir kalır.
11. Satın alma sonrası duvar anında kalkar, seans başlar.
12. Bozuk veya taklit imzalı yanıt: yok sayılır, deneme uzamaz.
13. Sürüm derlemesinde `kertik.tamProva` hiçbir etki yapmaz.
14. `node test/hepsi.js` yeşil. `CLAUDE.md`'deki kalıcı kırmızılar hariç, yeni
    kırmızı üretilmeyecek.
15. `index.html` değiştiği için `node simulasyon/olustur-simulator.js` koşulacak.

## 8. Yapılmayacaklar

- Kullanıcıya giriş yaptırmak, hesap sormak, izin ekranı açmak.
- Reklam kimliği, `AD_ID` izni, üçüncü taraf analitik veya SDK.
- IP, konum, kullanım olayı, herhangi bir telemetri toplamak.
- Ham SSAID'yi göndermek veya saklamak.
- Ödemiş kullanıcıyı çevrimdışı diye engellemek.
- `Kasa.kt`'nin satın alma akışını yeniden yazmak.
- Compose, mimari yenileme, çalışan yüzeyleri baştan yazmak.
- Arayüzde "sunucu", "kimlik", "doğrulama" gibi kelimeler göstermek.
  Kullanıcı bu katmanı hiçbir zaman görmeyecek.

## 9. Yayın öncesi eklenecek beyanlar

Kod bittiğinde şunlar da bu görevin parçasıdır:

- `PRIVACY.md`: cihaza özel, kimliği taşımayan bir kod ve tek bir tarihin
  sahtekârlığı önleme amacıyla saklandığı, iki cümleyle ve sade dille.
- Play Data Safety formu için not: "cihaz kimlikleri, sahtekârlığı önleme".
  Bunu Yusuf dolduracak, sen metni hazırlayacaksın.

## 10. Sıra

1. Worker ve KV, tek başına `curl` ile doğrulanmış hâlde.
2. `Deneme.kt` ve imza doğrulaması, birim testleriyle.
3. Köprü ve `index.html` uyarlaması, katman 3 kuralı, eski yorumun düzeltilmesi.
4. Katman 2, Drive çapası.
5. On beş kabul kriterinin koşulması ve kanıtların bu klasöre `kanit/` altına
   konması.
6. Kararın `16-para-kazanma.md` dosyasına tek bölüm olarak düşülmesi.

Bittiğinde bu dosyanın başındaki **Durum** satırını güncelle ve yanına neyin
farklı yapıldığını, hangi kabul kriterinin nasıl kanıtlandığını yazan bir
`01-rapor.md` bırak.
