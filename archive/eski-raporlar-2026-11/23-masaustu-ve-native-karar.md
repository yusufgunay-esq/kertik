# 23 — "Native'e niye geçiyoruz?" ve Masaüstü (Microsoft Store)

16 Ağustos 2026. İki soru, iki bölüm. Birincisi bir itiraz, ikincisi yeni bir yön.

---

## Bölüm A — Native'e niye geçtik?

Soru yerinde ve cevabı önce bir ayrım yapmayı gerektiriyor. `18-native-gecis.md`
"native geçiş" diye tek şeymiş gibi yazıyor ama ortada **iki ayrı iş** var:

| | Ne | Zorunlu mu? | Durum |
|---|---|---|---|
| **S4a** | Gradle projesi + gerçek Android kabuğu | **Evet, mecbur** | Yapıldı |
| **S4b** | Arayüzün Compose'a yeniden yazılması | **Hayır** | Yapılmayacak |
| **S4c** | Tek tek native parçalar (widget, haptik, saat) | Özelliğe göre | Sırada |

**Isrardan söz edilecek bir yer yok, çünkü ısrar edilen şey yapılmadı bile.**
Yapılan şey S4a'ydı ve o bir tercih değildi.

### S4a niye mecburdu

Eski derleme zinciri hazır bir APK şablonuna `index.html` enjekte edip elle
imzalıyordu. Üç yerde duvara çarptı:

1. **31 Ağustos 2026 — iki hafta sonra.** Play, o tarihten sonra yeni uygulamalardan
   ve güncellemelerden API 36 hedefi istiyor. Eski zincir `targetSdk 34` üretiyordu ve
   yükseltilemiyordu: manifesti değiştirmek Android SDK istiyor. Yani eski zincirle
   Play'e **hiç giremezdik.** (Gerekirse 1 Kasım 2026'ya kadar uzatma istenebiliyor,
   ama bu bir erteleme, çözüm değil.)
2. **AAB.** Play yeni uygulamalardan AAB istiyor, eski zincir sadece APK üretiyordu.
3. **Bildirim çubuğundaki canlı sayaç.** Bunun native karşılığı yok.

Kazanılanlar bunun yanında bedavaya geldi: dış bağlantılar artık sistem tarayıcısında
açılıyor (Drive senkronuna bağlanmak bu yüzden kolaylaştı), karanlık modda açılış
parlaması gitti, sırlar depodan çıktı, CI derliyor.

**Bedeli ne kadardı:** uygulamanın tamamı hâlâ tek bir `index.html`. Değişen şey onu
saran kabuk. Bu bir yeniden yazım değildi, ambalaj değişimiydi.

### S4b — Compose'a geçiş: hayır

Arayüzü Kotlin/Compose'a taşımak **hiçbir sorunu çözmüyor.** Kadran, akış alanı,
çubuk kaydı, ay duvarı — hepsi canvas/DOM ile zaten çalışıyor ve simülatörde
hızlandırılmış test edilebiliyor. Compose'a taşımak:

- iki aylık iş,
- `tasarim/simulator.html` tezgâhını çöpe atar (palet denemek bir daha bu kadar ucuz olmaz),
- masaüstü sürümünü **imkânsız** kılar (aşağıdaki B bölümünün tamamı buna dayanıyor),
- karşılığında kullanıcının fark edeceği tek şey birkaç milisaniyelik akıcılık.

Karar: **arayüz web kalıyor.** Bu, "şimdilik böyle" değil, mimari karar.

### S4c — hangi özellikler native kod istiyor

Bunlar arayüzü değiştirmiyor, yanına küçük parçalar ekliyor:

| İstenen (kaynak) | Native şart mı? | Not |
|---|---|---|
| Ana ekran widget'ı — `21`, en önemli bulgu | **Evet** | Glance/RemoteViews. WebView'in erişimi yok. Ayrı, küçük, izole iş. |
| İnce haptik ("taptic klik") — `13` | **Evet** | Web'in `vibrate()` API'si sadece kaba titreşim verir. `HapticFeedbackConstants` köprüsü ~30 satır. |
| Akıllı saatten mola/devam — `13` | **Evet** | Wear OS ayrı modül. En pahalısı, en sona. |
| Bildirimde canlı sayaç | Evet | Zaten yapıldı. |
| DND açma/kapama | Evet | Küçük köprü. |
| Ekran açık kalma (`keep screen on`) | Evet | Tek satır. |
| Tam ekran seans modu — `21` | Hayır | CSS ve JS ile. |
| Sistem karanlık moduna uyma — `13` | Hayır | `prefers-color-scheme` WebView'de çalışıyor. |

Yani doğru cümle şu: *"native'e geçiyoruz"* değil, **"native kabuğun içinden birkaç
sistem özelliğine uzanıyoruz."** Kabuk zaten var, uzanmak ucuz.

---

## Bölüm B — Masaüstü sürüm ve Microsoft Store

Fikir doğru ve zannedilenden **çok daha ucuz**, çünkü B bölümünün tamamı A bölümünde
verilen karara dayanıyor: uygulama tek bir `index.html`. Compose'a geçilseydi bu
konuşma hiç açılamazdı.

### Niye mantıklı

- **Kullanım yeri doğru.** Ders/iş çalışılan yer masa başı. Kronometre telefonda
  duruyor ama çalışılan yerde durmuyor. `21`deki en önemli bulgu — *"uygulamayı
  açtıktan sonra dönmüyorum"* — masaüstünde kendiliğinden çözülüyor: ekranın köşesinde
  duran bir pencere, telefon widget'ının yapmaya çalıştığı şeyi zaten yapıyor.
- **Senkron altyapısı hazır.** Drive `appDataFolder` telefon–bilgisayar köprüsünü
  kurulmuş hâlde veriyor. Yeni sunucu, yeni hesap sistemi gerekmiyor.
- **Rakip boşluğu.** Forest'ın masaüstü tarafı zayıf, Session macOS ağırlıklı,
  TickTick'in odak sayacı ürünün küçük bir parçası. Windows'ta "dürüst kayıt" iddiasıyla
  masaüstü kronometre yok denecek kadar az.
- **Mağaza girişi bedava ve hızlı.** Microsoft bireysel geliştirici kaydındaki 19 $
  ücreti kaldırdı; şirket hesaplarındaki ücret de kalktı. Play'in 25 $ + 12 testçi ×
  14 gün kapalı test şartı gibi bir engel yok, inceleme genelde 24 saat.
- **Komisyon lehte.** Microsoft'un ödeme altyapısı kullanılırsa oyun dışı uygulamalarda
  %15; kendi ödeme altyapını kullanırsan gelirin %100'ü sende kalıyor (oyun dışı).
  Play %15/%30 alıyor. `21`deki 9,99 $ peşin fiyat burada daha çok kâr bırakıyor.

### İki yol var ve seçim önemli

| | **PWA → MSIX (PWABuilder)** | **Tauri (veya Electron)** |
|---|---|---|
| İş yükü | Bir hafta sonu | 1–2 hafta |
| Nasıl çalışır | Mağazadaki paket **barındırdığın bir URL'yi** açar | `index.html` **paketin içinde**, yerelden çalışır |
| Barındırma | **Zorunlu.** GitHub Pages bedava ama site düşerse uygulama açılmaz | Yok |
| Çevrimdışı | Service worker'a bağlı, kırılgan | Tam çevrimdışı |
| Boyut | ~1 MB | Tauri ~5–10 MB (WebView2'yi Windows sağlıyor), Electron ~100 MB |
| Dosya sistemi, tepsi ikonu, kısayol tuşu | Sınırlı | Tam |
| Risk | PWABuilder paketleme servisinde 2026 başında kesinti bildirimleri var | Kendi zincirin, kimseye bağlı değil |

**Öneri: Tauri.** Gerekçe, `18`de foreground service'i reddederkenki gerekçenin aynısı —
**dışarıya bağımlılık istemiyoruz.** PWA yolu ürünün "sunucu yok" sözünü fiilen bozuyor:
bir URL'ye bağlanmadan açılmayan uygulama, sunucusuz değildir. Ayrıca 9,99 $ ödeyen
birinin uygulaması internet kesildiğinde açılmıyorsa, o iade demektir.

Tauri'nin ikinci faydası: Windows paketi çıkarken macOS ve Linux paketi de aynı
kaynaktan çıkıyor. Bugün gerekmiyor, ama kapı açık kalıyor.

### Dürüst maliyetler

- **Ayrı satın alma.** Play ile Microsoft Store arasında lisans taşınmıyor. Telefonda
  9,99 $ ödeyen kişi bilgisayarda tekrar ödeyecek. Bunun iki cevabı var ve **karar
  verilmedi:** (a) masaüstünü belirgin ucuz tut (3,99 $) ve "eklenti" gibi konumlandır,
  (b) telefon uygulaması içinden verilen bir kodla masaüstünü aç — ama bu kendi lisans
  altyapını kurmak demek, ve `21`in reddettiği türden bir karmaşa.
- **İkinci bir mağaza sayfası, ikinci bir inceleme kuyruğu, ikinci bir destek kanalı.**
  Solo geliştirici için bu, koddan daha pahalı olan kısım.
- **Dokunmatik olmayan arayüz.** Kadran parmak için tasarlandı; fare ve klavye için
  ayrı düşünülmesi gereken şeyler var (kısayol tuşları, hover, pencere küçültülünce ne olur).
- **Windows'ta widget karşılığı yok.** Karşılığı sistem tepsisi ikonu ve küçük "her
  zaman üstte" penceresi. Bunlar Tauri'de var ama tasarlanmadı.

### Zamanlama — sıraya girmiyor

Bu iş **27 Eylül'deki sınavdan ve Play yayınından sonra.** Gerekçe: masaüstü sürüm
telefon sürümünün `index.html`'ini paylaşıyor, yani telefon tarafı oturmadan masaüstünü
paketlemek **iki cephede aynı anda değişen tek dosya** demek. Önce dosya dursun.

Sıralama:

1. Play yayını (telefon) — `21`deki liste.
2. Birkaç hafta gerçek kullanım, `13-bulgular.md` dolsun.
3. Tauri denemesi: `index.html`'i sarıp bir `.exe` çıkar, **kendi bilgisayarında** kullan.
   Mağaza yok, fiyat yok, kayıt yok. Bu adım bir hafta sonu.
4. Kendin bir ay kullandıktan sonra mağaza kararı.

3. adım bedava ve geri dönüşü var; asıl bilgi oradan gelecek.

---

## Bu dosyanın kararları

- Compose'a geçilmeyecek. Arayüz web kalıyor. **(kesin)**
- Native kod sadece sistem özelliklerine uzanmak için yazılacak: widget, haptik,
  DND, ekran açık kalma, sonra saat. **(kesin)**
- Masaüstü sürüm yapılacak, yolu **Tauri**, mağazası Microsoft Store. **(yön kesin,
  zamanı sınavdan sonra)**
- Masaüstü fiyatı ve telefon lisansıyla ilişkisi **açık soru.**

---

## Kaynaklar

- [Target API level requirements for Google Play apps — Play Console Help](https://support.google.com/googleplay/android-developer/answer/11926878?hl=en)
- [Publish a PWA to the Microsoft Store — Microsoft Learn](https://learn.microsoft.com/en-us/microsoft-edge/progressive-web-apps/how-to/microsoft-store)
- [Choose a distribution path for your Windows app — Microsoft Learn](https://learn.microsoft.com/en-us/windows/apps/package-and-deploy/choose-distribution-path)
- [Free developer registration for individual developers — Microsoft Learn](https://learn.microsoft.com/en-us/windows/apps/publish/whats-new-individual-developer)
- [Benefits of distributing your apps via Microsoft Store — Microsoft Learn](https://learn.microsoft.com/en-us/windows/apps/publish/publish-your-app/why-distribute-through-store)
- [PWABuilder paketleme servisi kesintisi (GitHub Issue #5303)](https://github.com/pwa-builder/PWABuilder/issues/5303)
