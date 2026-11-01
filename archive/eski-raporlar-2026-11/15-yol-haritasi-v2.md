# 15 — Yol Haritası v2 (15 Ağustos 2026)

`10-yol-haritasi.md` MVP öncesi yazılmıştı. Bu dosya, çalışan v2.0'dan sonrasını tutar.
Fiyatlandırma ve para kazanma ayrı dosyada: [16-para-kazanma.md](16-para-kazanma.md).

---

## v2.0'da ne değişti

Tasarım yönü seçildi ve uygulandı: **Kâğıt** (açık mod imza, kirli beyaz zemin, saç teli çizgiler,
tek toprak kırmızısı vurgu). Gölge yok, kutu yok, bütün butonlar yuvarlak.

Asıl kavramsal düzeltme, dolan halkanın kaldırılması oldu.

> Dolan bir ilerleme halkası "bir varış noktası var" der. Kronometrede varış noktası yoktur.
> O halka ya hiç dolmaz ya da uydurma bir hedefe göre dolar; ikisi de dürüst kayıt iddiasını deler.

Yerine **kertik kadranı** kondu, uygulamanın adıyla aynı fikir:

| Olgu | Kadranda karşılığı |
| --- | --- |
| Geçen her dakika | Bir çentik |
| Dolan her saat | Bir dıştaki halka açılır, kadran ölçeklenip ekrana sığar |
| 5. ve 15. dakikalar | Daha uzun çentik, cetvel gibi okunur |
| Mola | Çentik atılmaz, soğuk renkli boş bir yay kalır |
| Molaya girmek | Bütün ekran birkaç ton soğur |
| Seansın bitmesi | Kadranın son hâli, o seansın kartı olur |

Böylece `06-estetik-konseptler.md`'deki Konsept A'nın ödül katmanı, tek bir illüstrasyon
çizmeden geldi. İki seans asla aynı şekli vermiyor.

**İkinci mod eklendi.** Pomodoro aynı alfabeyi sınırlı hâlde kullanır: hedef kaç dakikaysa
kadranda o kadar çentik vardır, teker teker kazınır. Dolan kalın halka burada da kullanılmadı,
çünkü çentik saymak yaydan göz kararı tahmin etmekten daha doğru. Hedef dolunca uygulama
kesmez, sayaç `+` ile fazla mesaiyi göstermeye devam eder; bu da dürüst kayıt ilkesinin gereği.

**"Buradayım" butonu kaldırıldı.** Gerekçe: dalmışken uygulamayı kontrol etmek, dalmayı bozar.
O buton kendi çözmeye çalıştığı sorunu üretiyordu. Yerine seans sonunda tek soru geldi (Ç2'nin
yeni hâli, aşağıda).

---

## Ç2 yeniden tanımı: teyit seans sırasında değil, sonunda

Eski davranış: her 20 dakikada titreşim, cevaplamazsan o süre onaylanmamış.
Yeni davranış: **seans sırasında hiçbir şey sorulmaz, hiç titreşim gelmez.**

Seans bitince ve yalnız uzunsa (varsayılan 1,5 saat üstü) tek soru çıkar:

> 1s 52dk çalışma yazıyorum.
> Arada masadan kalkıp molaya basmayı unuttuğun bir bölüm oldu mu?
> **[Hayır, hepsi çalışmaydı]** [15dk] [30dk] [1 saat] [başka]

Varsayılan cevap tek dokunuş ve her zaman "daha az çalışma" yönünde. Verilen süre
`session.awayMs` alanına yazılır, `stats()` bunu nettten düşer. Eşik ayarlardan değişir,
kapatılabilir.

Neden bu daha iyi: odaklanma bölünmüyor ama "telefonu bırakıp gittim" deliği kapalı kalıyor.
Uygulama yine emin olmadığı süreyi çalışmaya yazmıyor, sadece emin olma anını sonraya alıyor.

---

## S1 — Google Drive senkronu *(yapıldı → [17-google-senkron.md](17-google-senkron.md))*

Amaç: telefon değişince, uygulama silinince, ikinci cihazda kayıt kaybolmasın.

**Sunucu kurulmayacak.** Drive'ın `appDataFolder` alanı kullanılacak: veri kullanıcının kendi
Drive'ında, kendi kotasında, kullanıcıya görünmeyen özel bir klasörde durur. Bizim tarafta
hiçbir sunucu, hiçbir maliyet, hiçbir kişisel veri olmaz. "Sunucu yok" sözü bozulmaz.

- Kapsam: `https://www.googleapis.com/auth/drive.appdata`.
  Google bu kapsamı **hassas olmayan (non-sensitive)** olarak sınıflandırıyor, yani ağır
  doğrulama sürecine girmiyor. Bu, Drive'ın tam kapsamı yerine bunu seçmemizin asıl sebebi.
- Dosya: tek bir `kertik.json`, mevcut dışa aktarma formatının aynısı.
- Çakışma kuralı: seanslar ve görevler `id` taşıdığı için birleştirme yapılabilir.
  Aynı `id` iki tarafta farklıysa **daha yeni `editedAt` kazanır**; silinenler `tombstone`
  listesiyle taşınır, yoksa silinen kayıt diğer cihazdan geri diriler.
- Giriş zorunlu değil. Hesapsız kullanan hiçbir şey kaybetmez, sadece yedeği olmaz.

**Bilinen risk:** Advanced Protection açık Google hesaplarında üçüncü taraf OAuth engelleniyor
(HMGS projesinde bu duvara zaten çarpıldı). Giriş başarısız olursa uygulama sessizce yerel
moda düşmeli, hata ekranı göstermemeli.

> **Uygulanırken çıkan ek karar:** WebView'de OAuth yönlendirmesi Google tarafından
> engellendiği için giriş **cihaz akışıyla** (device flow) yapıldı — uygulama bir kod
> gösterir, kullanıcı onu herhangi bir tarayıcıda girer. Ayrıntı ve gerekçe 17'de.

---

## S2 — Google Tasks köprüsü

Bu uygulama zaten iki şikâyetten doğdu: Forest'ın yalan söyleyen sayacı ve Google Tasks'ın
"yapamadım" diyememesi. O yüzden Google Tasks'a bağlanmanın **doğru ve yanlış bir yolu var.**

### Neden bağlanmalı

Kertik'in görev listesi bugün ada. HMGS koçu haftanın görevlerini zaten Google Tasks'a
yazıyor; Kertik onları okuyabilirse çalışma planı elle kopyalanmadan sayaca bağlanır ve
"bu göreve ne kadar verdim" sorusu kendiliğinden cevaplanır.

### Neden tehlikeli

Google Tasks API'de bir görevin durumu yalnız iki değer alabilir: `needsAction` ve `completed`.
Kertik'in altı durumu oraya sığmaz. Naif bir iki yönlü senkron, "olmadı" ve "iptal" kayıtlarını
ya tamamlanmış ya da hiç olmamış gösterir. Yani uygulamanın var olma sebebini silen bir senkron
olur.

### Kural: yalan yazma, not düş

| Kertik durumu | Google Tasks'a yazılan | Gerekçe |
| --- | --- | --- |
| bekliyor | `needsAction` | doğrudan karşılığı var |
| yapılıyor | `needsAction` | Tasks'ta ara durum yok, bozmadan bırak |
| **bitti** | `status: completed` | tek gerçek eşleşme, yazılır |
| **taşındı** | `due` tarihi bir gün ileri, durum `needsAction` kalır | temsil edilebilir |
| **olmadı** | durum **yazılmaz**, `notes` sonuna satır eklenir | Tasks'ta karşılığı yok |
| **iptal** | durum **yazılmaz**, `notes` sonuna satır eklenir | aynı |

> **Altın kural:** Google Tasks'a olmamış bir `completed` asla yazılmaz.
> Temsil edilemeyen her durum, göreve serbest metin olarak düşülür:
> `15 Ağustos: olmadı (zaman yetmedi) · Kertik`

Böylece Google Tasks tarafında da gerçek görünür, üstelik Google'ın veremediği bilgiyi
Kertik oraya taşımış olur.

### Tek yazar kuralı (HMGS'deki ilkenin aynısı)

| Alan | Sahibi |
| --- | --- |
| Görevin var olması, başlık | Google Tasks (dışarıdan gelen görevler için) |
| `due` tarihi | Kertik yalnız "taşındı"da yazar |
| `status: completed` | Kertik yazar, yalnız "bitti"de |
| `notes` | Kertik yalnız **sona ekler**, mevcut metni asla silmez |
| Altı durumlu gerçek durum | Yalnız Kertik, hiçbir zaman dışarı yazılmaz |

Kertik bir görevin başlığını asla değiştirmez, asla görev silmez.

### Uygulama sırası

1. **Önce tek yön: Tasks → Kertik.** Seçilen listeden bugünün görevlerini içeri al.
   Riski sıfır, faydası hemen görülür.
2. Sonra yalnız `bitti` ve `taşındı` geri yazılsın.
3. `notes` satırı en son, ve ayardan kapatılabilir olsun (herkes Tasks'ının kirlenmesini istemez).

### Açık soru, kod yazmadan önce cevaplanacak

~~Tasks kapsamının hassas sayılıp sayılmadığı doğrulanamadı.~~ **Cevaplandı, ve beklenenden
sert çıktı:** Google'ın cihaz akışı yalnız şu kapsamları destekliyor — `openid`, `email`,
`profile`, `drive.appdata`, `drive.file` ve YouTube. **`.../auth/tasks` bu listede yok.**

Yani S2, WebView sürümünde hiç yapılamaz; normal OAuth yönlendirmesi gerekiyor, o da
`AndroidManifest` erişimi, yani **native sürüm (S4) demek.** Bu, S4'ü S2'nin önüne
alan yeni ve bağımsız bir gerekçe.

---

## S3 — Ayna sekmesi (istatistik)

`06`'daki Konsept C. Ana ekran değil, ayrı sekme; isteyen bakar.

- Haftalık ısı haritası, konu bazında süre, tamamlanma oranı, en verimli saat aralığı.
- Her grafiğin altında tek cümlelik insan yorumu.
- Kadran dili burada da sürsün: çubuk grafik yerine çentik yoğunluğu denenebilir.
- `09-elestiri-ve-riskler.md`'deki Goodhart uyarısı geçerli: sayıyı hedefe çevirmeyecek
  bir dil kurulmalı. Rekor, seri, rozet yok.

## S4 — Native sürüm *(birinci yarısı yapıldı → [18-native-gecis.md](18-native-gecis.md))*

Madde uygulanırken ikiye bölündü:

**S4a — yapıldı.** Gerçek bir Gradle projesi (`kertik-android/`), API 36, AAB, CI,
ve **bildirim çubuğunda canlı sayaç** (mola/devam/bitir tuşlarıyla). Arayüz Compose'a
çevrilmedi: çalışan ve test edilmiş bir arayüzü atmak gereksiz risk olurdu, ve Play'in
istediği şey Compose değil gerçek bir Gradle derlemesiydi.

**S4b — duruyor:**

- Rahatsız Etmeyin entegrasyonu ve seans sonu otomatik geri açma (Ç8)
- Ana ekran widget'ı, tek dokunuşla başlat
- Uygulama kapalıyken titreşim
- Arayüzün Compose'a taşınması (gerekliliği tartışmalı)

Veri modeli aynen taşınır, `session` + `session_event` akışı `08-veri-modeli.md` ile birebir.

## S5 — Play Store

Ayrıntılar [16-para-kazanma.md](16-para-kazanma.md)'de. Teknik olarak kritik iki madde:

- **31 Ağustos 2026'dan itibaren yeni uygulamalar API 36 (Android 16) hedeflemek zorunda.**
  Mevcut nitron şablonu 34 üretiyor, yani bu zincirle mağazaya çıkılamaz.
- AAB üretmek `bundletool` ister; Cowork ortamından Google ve GitHub sunucularına erişim yok.
  Derleme Yusuf'un makinesinde (Android Studio) ya da GitHub Actions'ta yapılmalı.

## S6 — Küçük işler

- Seansı göreve bağlama (Ç7): başlatırken bugünün listesinden seç, kayıt o göreve yazılsın.
- Seansı ikiye bölme ve iki seansı birleştirme (Ç3'ün eksik kalan kısmı).
- Kadranın seans kartı olarak dışa aktarımı (PNG), paylaşmak isteyen için.
- Onboarding: üç ekran, atlanabilir, "annem" profili için.
- Uygulama içi yedek hatırlatması: son dışa aktarmanın üstünden 30 gün geçtiyse tek satır not.

---

## Değişmeyecek olanlar

`05-ozellik-listesi.md`'deki "asla yapmayacaklarımız" listesi aynen yürürlükte:
seri, sıralama tablosu, reklam, zorunlu hesap, motivasyon bildirimi, yapay puan ekonomisi,
sohbet asistanı. Buna v2 ile bir madde daha eklendi:

- **Seans sırasında kullanıcıya soru sorulmaz.** Uygulamanın işi odaklanmayı korumaktır;
  doğrulamayı bekletmek, odaklanmayı bölmekten ucuzdur.
