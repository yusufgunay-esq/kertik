# 38 — DND: telefonun küresel anahtarı yerine Kertik'in kendi modu

6 Eylül 2026. Soru şuydu: seans sırasında bildirimleri susturmak için telefonun
var olan Rahatsız Etmeyin anahtarını mı çevirelim, yoksa Kertik'in kendi ayrı
modunu mu oluşturalım. Karar: **kendi mod, sistemin içinde.**

## Neden küresel anahtar değil

Önceki uygulama `setInterruptionFilter` ile telefonun tek küresel anahtarını
çeviriyor, eski değeri `KEY_DND_ORIJINAL` altında saklayıp seans bitince geri
koyuyordu. Üç yerden kanıyordu:

- Kullanıcının kendi "öncelikli" tanımını (kimler geçebilir, alarm çalar mı)
  devralıyorduk; o tanım gece uykusu için yapılmış, Kertik için değil.
- Uygulama beklenmedik şekilde öldürülürse telefon sessizde kalabiliyordu;
  `onCreate` içindeki yetim durum kurtarma kodu bunun pansumanıydı.
- Kullanıcı zaten başka bir mod açıkken seans başlatırsa iki taraf aynı
  anahtarı çekiştiriyordu.

## Neden tamamen kendi modumuz da değil

Bir uygulama, izin olmadan başka uygulamaların bildirimini susturamaz. Android'in
kendi Modlar sistemine girmeden "kendi modumuz" dediğimiz şey, Kertik'in kendi
sesini kısmaktan öteye geçmez; kullanıcıyı rahatsız eden zaten WhatsApp'tır,
Kertik değil. İzin gereksinimi ne olursa olsun aynı kalıyor.

## Karar: `AutomaticZenRule`

Android 7'den (API 24, bizim `minSdk`'miz) beri var. Uygulama sisteme "Kertik"
adında kendi kuralını kaydediyor, kendi politikasıyla. Kullanıcının kendi
Rahatsız Etmeyin tanımına hiç dokunulmuyor; Kertik, telefonun Modlar ekranında
kendi adıyla ayrı bir satır olarak duruyor (ekran görüntüsünde Ayşe'nin oğlu
Yusuf'un telefonunda gördüğümüz "Uyku Vakti", "Sürüş", "Ders" gibi).

Uygulanan mantık (`MainActivity.kt`):

- `zenKuralIdGetir`: kayıtlı bir kural kimliği varsa ve sistemde hâlâ duruyorsa
  onu kullanır; yoksa `AutomaticZenRule("Kertik", …)` ile yeni bir kural açar
  ve kimliğini `KEY_ZEN_KURAL_ID` altında kalıcı saklar. Kullanıcı kuralı
  Modlar ekranından elle silerse bir sonraki seansta sessizce yeniden açılır.
- `dndBaslat` / `dndBitir`: kuralı silmiyor, sadece `setAutomaticZenRuleState`
  ile `STATE_TRUE` / `STATE_FALSE` arasında geçiriyor.
- Politika (API 28 ve üstü): yalnızca alarmlar geçebiliyor
  (`PRIORITY_CATEGORY_ALARMS`), geri kalan her şey susuyor. API 24-27'de
  `Policy` ataması atlanıyor, kural yine de `INTERRUPTION_FILTER_PRIORITY` ile
  çalışıyor, sadece o dar aralıkta cihazın kendi öncelik ayarına bağlı kalıyor.
- Kural bir nedenle oluşturulamazsa (bazı OEM kabuklarında olabiliyor) eski
  küresel anahtar yöntemine sessizce yedek düşülüyor; kullanıcı farkı
  hissetmiyor.
- Yetim kalma kurtarması (`onCreate`) hem yeni yolu (`KEY_ZEN_AKTIF` işaretliyse
  kuralı kapat) hem eski yedek yolu kapsıyor.

## Test durumu

`test/test-dnd.js` yeni mekanizma için sekiz yeni kontrol aldı (kural
oluşturma, kimlik saklama, `setAutomaticZenRuleState`, silinmişse yeniden
oluşturma, sürüm korumalı politika, yalnız alarm geçişi, yedek yol, genişletilmiş
yetim kurtarma). Ayrıca 15 dilde `s_dnd`/`s_dnd_alt` kontrolündeki 300 karakterlik
pencere gerçek dil bloklarını (~8,5 KB) kapsamıyordu; blok sınırına göre
düzeltildi. Bu ortamda `node test/test-dnd.js` yeşil (45/45); gerçek Kotlin
derlemesi burada koşulamıyor (Android SDK yok), bir sonraki yerel derlemede
doğrulanmalı.

## Açık nokta

İzin ekranı hâlâ çıplak: kullanıcı anahtarı açtığında hiçbir açıklama olmadan
doğrudan sistem izin listesine düşüyor. Bu ayrı bir konu (izin öncesi açıklama
yaprağı, dönüşte doğrulama); bu dosyanın kapsamı yalnız hangi mekanizmanın
kullanılacağıydı.
