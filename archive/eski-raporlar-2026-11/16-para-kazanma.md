# 16 — Para Kazanma ve Yayın (15 Ağustos 2026)

Soru şuydu: uygulamayı Play'e koyup aylık 10-15 TL almak mantıklı mı?
Kısa cevap: **yayın evet, aylık abonelik hayır.** Gerekçeler aşağıda, veriyle.

---

## 1. Neden aylık abonelik değil

**Abonelik sürekli bir değer satar. Kertik'te henüz sürekli olan bir şey yok.**
Uygulama tamamen telefonda çalışıyor, sunucu maliyeti sıfır, tazelenen içerik yok.
Kullanıcının her ay yeniden ödediği şeyin karşılığı gösterilemiyor.

**Kategori lideri abonelik almıyor.** Doğrudan rakip Forest, Android'de 1,99 dolar
**tek seferlik**, iOS'ta 3,99 dolar tek seferlik alıyor. Milyonlarca kullanıcısı olan
uygulamanın fiyatı buysa, yeni bir uygulamanın aylık ücret istemesi savunulamaz.

**Aylık küçük tutar verimsiz.** Google hizmet ücreti geliştiricilerin %99'u için %15 veya altı.
15 TL'lik bir abonelikte her ay komisyon, her ay yenileme sürtünmesi, her ay iptal riski var.
Kazanılan para, harcanan güvene değmiyor.

**Ödeme eşiği 100 dolar.** O eşiğe aylık küçük tutarlarla ulaşmak uzun sürer; para
hesapta bekler.

---

## 2. Model kararı: ücretsiz çekirdek + tek seferlik açılış

| Katman | İçerik | Fiyat |
| --- | --- | --- |
| **Çekirdek, sonsuza kadar ücretsiz** | Kronometre, pomodoro, sınırsız mola, seans düzenleme, altı durumlu görevler, kayıt, kadran, yerel yedek | 0 |
| **Kertik Tam, tek seferlik** | Ayna sekmesi (istatistik), ana ekran widget'ı, Rahatsız Etmeyin entegrasyonu, bildirim çubuğunda canlı sayaç, seans kartı paylaşımı | tek ödeme |

Reklam yok, hiçbir katmanda.

### Deneme: 14 gün tam erişim, sonra düşüş

Kurulumdan sonraki 14 gün Kertik Tam açıktır. Süre bitince uygulama **kilitlenmez, düşer**:
çekirdek olduğu gibi kalır, yalnız Kertik Tam yüzeyleri kilitlenir. Böylece kullanıcının
kendi kaydı hiçbir zaman rehin alınmaz ve "önce bedavaydı, sonra kilitledi" şikayeti
doğmaz; buna karşılık satın alma baskısı gerçek olur, çünkü kullanıcı iki hafta boyunca
sahip olduğu widget'ı, sessizleşen telefonu ve Ayna'yı kaybeder.

Çekirdeğe ek olarak Drive senkronu, tema ve diller de her zaman ücretsizdir.

### Ücretli olması meşru olanlar

Yukarıdaki beş madde ortak bir özelliği paylaşıyor: **hepsi ek emek ve ek native iş**
gerektiriyor, hiçbiri kullanıcının kendi verisine erişimini kısıtlamıyor.

### Ücretli yapılmayacaklar, bunlar tartışmaya kapalı

- **Geçmiş kayıtların sınırlanması.** "Son 30 gün ücretsiz" gibi bir şey uygulamanın tek
  iddiasını, dürüst kaydı, rehin alır. Kullanıcının verisi kullanıcınındır.
- **Dışa aktarma.** Yedek alabilmek ücretli olamaz, aksi hâlde kullanıcı kilitlenmiş olur.
- **Karanlık tema, temel ayarlar.** Ucuz numara olarak okunur.
- **Bulut senkronu.** Drive `appDataFolder` kullanıldığı için bize maliyeti sıfır;
  maliyeti olmayan şeye ücret koymak, sonradan abonelik dayatmanın kılıfı gibi durur.
  Senkron ücretsiz kalsın, güven getirisi paradan yüksek.

---

## 3. Fiyat

**Güncellendi (4 Eylül 2026).** Aşağıdaki rakamlar karara bağlandı, gerekçe ve pazar
verisi için `Fiyat.md`.

- **Küresel açılış: 5,99 dolar tek seferlik.** Rakip tek seferlik bandı 1,99 ile 11,99
  arasında (Forest Android 1,99, Forest iOS 3,99, Focus To-Do ömür boyu 11,99,
  Be Focused Pro 1,99). 5,99 bu bandın ortasının üstü, "atılabilir zamanlayıcı"
  algısının dışı.
- **Hedef: 9,99 dolar.** Üç şart birlikte sağlanınca yükseltilir: 200 üstü yorum ve 4,5
  üstü ortalama, ikinci bir yüzey (iOS ya da masaüstü), Ayna sekmesinin olgunlaşması.
  Uygulama içi ürünün fiyatı sonradan yükseltilebilir, önceden alanlar etkilenmez;
  açılış penceresi ise tekrarlanamaz. Bu yüzden düşük açılış, yüksek açılıştan güvenli.
- **Türkiye: 149,99 TL.** Play'in otomatik çevirisi bırakılırsa 5,99 dolar yaklaşık 290 TL
  eder ve satmaz. 149,99'un KDV sonrası karşılığı 124,99, Küçük İşletme Programı'nın
  %15 komisyonu sonrası eline geçen yaklaşık 106 TL.
- Diğer ülkeler için Play'in satın alma gücüne göre bölgesel fiyatlandırması açılır.
  Elle ayarlanacak tek ülke Türkiye.
- **İndirim yok.** İndirim, bekleyeni ödüllendirir ve tam fiyatı savunulamaz hale getirir.

### Abonelik yine de istenirse

Anlamlı hâle geldiği tek senaryo: gerçek bir sunucu maliyeti doğduğunda (çapraz cihaz
gerçek zamanlı senkron, web sürümü, ekip özellikleri). O gün geldiğinde bile:

- **Aylık değil yıllık.** Bir yardımcı uygulamada aylık ödeme, tutar ne olursa olsun
  psikolojik olarak pahalı hissettirir; yıllık tek karar daha ucuz hissettirir.
- Tek seferlik satın alanların hakkı korunur, sonradan abone olmaya zorlanmaz.

---

## 4. Play Store'a çıkmanın gerçek maliyeti

Para dışında ödenecek bedeller, sırayla:

| Şart | Ayrıntı |
| --- | --- |
| Geliştirici hesabı | 25 dolar, tek seferlik, iade yok |
| **Kapalı test** | 13 Kasım 2023'ten sonra açılan bireysel hesaplar için **12 benzersiz testçi, 14 gün kesintisiz**, sonra üretim erişimi başvurusu. Ücretsiz uygulamalar dahil. En zor madde bu: on iki gerçek Google hesabı bulmak gerekiyor. |
| **Hedef API** | 31 Ağustos 2026'dan itibaren yeni uygulamalar API 36 (Android 16). Mevcut WebView zinciri 34 üretiyor, yetmez. |
| Gizlilik politikası | Çalışan, herkese açık bir URL zorunlu |
| Data Safety formu | Kullanılan tüm SDK'lar dikkate alınarak doldurulmalı; uyumsuzluk yayından kaldırma sebebi |
| Ödeme eşiği | 100 dolar |
| Vergi | Şirket zorunlu değil; GVK mükerrer 20/B kapsamında limit altı uygulama geliri stopajla çözülebilir. **Mali müşavire teyit ettirilecek.** |

### Ayrıca dikkat

- **Düşük işlevsellik riski.** Play, ince WebView sarmalayıcılarını "minimum functionality"
  gerekçesiyle reddedebiliyor. Native sürüme geçmek yalnız özellik meselesi değil,
  yayın güvenliği meselesi de.
- **İnternet izni.** Mevcut şablon `permissions: []` yazılmasına rağmen manifeste
  `INTERNET` koyuyor. Veri güvenliği formuyla çelişmemesi için native sürümde temizlenmeli
  ya da Drive senkronu geldiğinde dürüstçe beyan edilmeli.

---

## 5. Zamanlama

HMGS sınavı **27 Eylül 2026**. Play süreci en iyi ihtimalle üç dört haftalık bir bürokrasi
ve 12 testçi maddesi tek başına iki hafta yiyor.

Önerilen sıra:

1. **Şimdi:** APK kendi telefonuna kurulsun, birkaç hafta gerçekten kullanılsın.
   Eksikler yaşanarak bulunsun, `05`'teki v1 listesi gerçek kullanıma göre budansın.
2. **Sınavdan sonra:** native sürüm ve Play projesi.
3. **En son:** ücretli katman. Önce insanların ücretsiz sürümü kullanıp kullanmadığı görülsün;
   kimsenin kullanmadığı bir uygulamaya fiyat koymak, cevabı olmayan bir soruya cevap yazmaktır.

---

## Kaynaklar

- Play Console, kişisel hesaplar için test şartı:
  https://support.google.com/googleplay/android-developer/answer/14151465
- Play hedef API seviyesi şartları:
  https://support.google.com/googleplay/android-developer/answer/11926878
- Play hizmet ücreti:
  https://support.google.com/googleplay/android-developer/answer/11131145
- Drive API kapsam sınıflandırması (`drive.appdata` hassas değil):
  https://developers.google.com/workspace/drive/api/guides/api-specific-auth
- Forest fiyatlandırması (2026): https://calmevo.com/forest-app-review/
