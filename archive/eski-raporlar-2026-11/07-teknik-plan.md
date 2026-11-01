# 07 — Teknik Plan (Android öncelikli)

Karar: **öncelik Android telefon.** Asıl kullanım orada, ve bildirim susturma /
arka plan sayacı gibi kritik özellikler ancak orada mümkün.

---

## Teknoloji seçimi

### Öneri: Kotlin + Jetpack Compose
| Neden | Açıklama |
|---|---|
| Arka plan işleri | Foreground Service, WorkManager, AlarmManager birinci sınıf |
| Rahatsız Etmeyin | `NotificationManager` API'sine doğrudan erişim, köprü yazmak yok |
| Bildirim | Canlı sayaç bildirimi, aksiyon tuşları, kanal kontrolü tam |
| Widget | Glance ile ana ekran widget'ı görece kolay |
| Yapay zekâ desteği | Compose için model bilgisi çok geniş, üretim kalitesi yüksek |
| Tek platform | iOS hedefi yok → çoklu platform bedelini ödemeye gerek yok |

### Alternatif: Flutter
- ✅ İleride iOS'a geçmek istersen tek kod tabanı, ve UI animasyonları çok rahat
  (Konsept A için avantaj).
- ❌ DND, foreground service, widget, boot receiver → hepsi için **platform kanalı** (Kotlin kodu)
  yazman gerekir. Yani zaten Kotlin öğreneceksin, üstüne bir katman daha.
- ❌ Sayacın doğruluğu gibi kritik iş, tam da platform kanalının arkasında kalıyor.

### Alternatif: PWA / web
- Yalnızca hızlı prototip için. Arka planda sayaç güvenilir değil, DND imkânsız.
- **Ama:** ekran akışını kâğıt yerine web'de denemek için harika. 1 günlük yatırım, sonra atılır.

> **Karar önerisi:** Kotlin + Compose. Flutter'ı ancak "6 ay sonra iPhone'a da lazım"
> diye kesin biliyorsan seç.

### Yığın
- UI: Jetpack Compose + Material 3 (renk şemasını kendimiz ezeceğiz)
- Mimari: tek modül, MVVM, ViewModel + StateFlow
- Veritabanı: **Room** (SQLite). Tamamen yerel, hesap yok.
- Arka plan: Foreground Service (sayaç) + AlarmManager (teyit ve dönüm noktası bildirimleri)
- Zamanlama: `System.currentTimeMillis()` (kayıt için) + `SystemClock.elapsedRealtime()` (ölçüm için)
- Tarih/saat: `java.time` (LocalDate, Instant)

---

## En kritik teknik kural: sayacı SAYMA, HESAPLA

Bu projenin çökebileceği tek yer burası.

```kotlin
// YANLIŞ — her saniye artan bir sayaç
var elapsed = 0L
tick() { elapsed += 1 }   // uygulama öldürülürse durur, telefon uykuya girerse kayar
```

```kotlin
// DOĞRU — başlangıç damgası sakla, geçen süreyi türet
val startedAt: Long = SystemClock.elapsedRealtime()
val elapsed get() = SystemClock.elapsedRealtime() - startedAt - toplamMolaSuresi
```

Kurallar:
1. Bir seansın gerçeği, veritabanındaki **olay damgalarıdır** (başladı, mola başladı,
   mola bitti, bitti). Ekrandaki sayı bu damgalardan **türetilir**.
2. Ekranın 1 saniyede bir yenilenmesi sadece **görsel**tir; veriyle ilgisi yoktur.
3. Uygulama öldürülse, telefon kapanıp açılsa, saat dilimi değişse bile süre doğru kalmalı.
4. `elapsedRealtime` cihaz yeniden başlatılınca sıfırlanır → **hem duvar saati hem monotonik
   saat** kaydet, yeniden başlatma tespit edilirse duvar saatinden hesapla.

### Mutlaka test edilecek senaryolar
- [ ] Seans açıkken uygulamayı görev listesinden kapat → süre doğru mu
- [ ] Seans açıkken telefonu yeniden başlat → seans kurtarılıyor mu
- [ ] Seans açıkken pil optimizasyonu uygulamayı öldürürse ne oluyor
- [ ] Uçak modu / saat dilimi değişimi
- [ ] Gece yarısını geçen seans hangi güne yazılıyor (karar: **başlangıç günü**)
- [ ] 6 saatlik tek seans (bozuk kalmış kayıt) — otomatik kırp ve sor

---

## Bildirimler ve arka plan

### Canlı sayaç bildirimi
- Foreground Service + kalıcı bildirim.
- Bildirim üzerinde iki aksiyon: **Mola / Devam** ve **Bitir**.
- Android 13+ için `POST_NOTIFICATIONS` izni istenir.
- Android 14+ foreground service tipi bildirilmek zorunda — bu iş için `shortService`
  uygun değil (süre sınırı var), muhtemelen `specialUse` gerekir ve Play Store'a
  gerekçe yazılır. *Yayın aşamasında güncel dokümandan doğrulanacak.*

### Teyit ve dönüm noktası bildirimleri (Ç2 / Ç6)
- `AlarmManager.setExactAndAllowWhileIdle` ile planlanır, Doze moduna dayanıklı.
- Ses yok, sadece kısa titreşim. Bildirim kanalı ayrı: "Sessiz hatırlatmalar",
  önem seviyesi düşük.

### Pil optimizasyonu
Bazı üreticiler (Xiaomi, Samsung, Huawei) uygulamaları agresif öldürür.
- Onboarding'de tek seferlik: "sayacın doğru çalışması için pil optimizasyonundan çıkar"
  yönlendirmesi (`REQUEST_IGNORE_BATTERY_OPTIMIZATIONS`).
- Ama **çıkarmasa bile bozulmamalı** — çünkü zaman damgası tabanlı hesap kullanıyoruz.
  Bildirim kesilir, süre kesilmez.

---

## Rahatsız Etmeyin (DND) entegrasyonu

- API: `NotificationManager.setInterruptionFilter(INTERRUPTION_FILTER_PRIORITY)`
- Gerekli izin: **Bildirim politikası erişimi** — normal izin değil, kullanıcıyı
  `ACTION_NOTIFICATION_POLICY_ACCESS_SETTINGS` ekranına götürüp elle açtırmak gerekir.
- Bu izin ilk seansta değil, kullanıcı bu özelliği açmak istediğinde istenmeli.
- Seans bitince / iptal edilince **mutlaka geri al**. Uygulama çökerse bile:
  service `onDestroy`'da ve bir yedek WorkManager işinde geri alma mantığı olsun.
  (Telefonu sessizde bırakan uygulama, silinen uygulamadır.)
- Android 15+ bildirim ve DND davranışında değişiklikler var; kodlamadan önce güncel
  `developer.android.com` davranış değişiklikleri sayfası okunacak.
- Not: sistem zaten "Odak modu" sunuyor. Bizim katma değerimiz **otomatik açıp
  otomatik kapatmak** — yani sürtünmeyi kaldırmak.

---

## Veri, yedek, gizlilik

- Her şey cihazda. Sunucu yok, hesap yok, analitik yok.
- Yedek: tek dokunuşla **JSON dışa aktarma** (v1). İçe aktarma da olsun.
- Android otomatik yedeklemesi açık kalsın ama tek başına güvenilmesin.
- Gizlilik politikası basit olacak: "hiçbir veri toplanmıyor." Play Store'a çıkarsa bu bir avantaj.

---

## Klasör yapısı (öneri)

```
app/
  data/
    db/          Room entity + dao + database
    repo/        SessionRepository, TaskRepository
  domain/
    model/       Session, Break, Task, TaskStatus
    usecase/     StartSession, TakeBreak, ResumeSession, ConfirmPresence, EditSession
  service/
    TimerService.kt        foreground service
    AlarmScheduler.kt      teyit + dönüm noktası
    DndController.kt       rahatsız etmeyin
  ui/
    timer/       çalışma ekranı
    tasks/       günlük liste + kapanış ekranı
    history/     seans listesi + düzenleme
    theme/       renk, tipografi
```

---

## Yapay zekâ ile geliştirme notu

Bu projeyi AI ile yazacaksın; işe yarayan yöntem:
1. **Önce veri modeli ve use-case'ler** yazılsın, UI en son. Sayaç mantığı doğru olmadan
   ekran yapmak zaman kaybı.
2. Sayaç mantığı için **birim testleri yaz(dır)**: "3 mola, biri 41 dakika, sonuç ne olmalı".
   Bu proje tam olarak "hesabı yanlış yapan uygulama" şikâyetinden doğduğu için,
   test edilmemiş sayaç mantığı ironik olurdu.
3. Her adımda tek bir dosya/ekran isteyin, "tüm uygulamayı yaz" demeyin.
4. Bu klasördeki markdown dosyalarını bağlam olarak verin — kararlar burada yazılı.
