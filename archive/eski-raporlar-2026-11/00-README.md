# Kronometre + Pomodoro + Görevler — Proje Notları

Bu klasör, adı **Kertik** olan bir odaklanma & görev uygulamasının düşünce defteri.
Önce ne yapacağımızı netleştirdik, sonra yazdık. Uygulama artık çalışıyor.

## Tek cümlelik özet

> Ders/iş çalışırken **dürüst süre tutan** ve gün sonunda **"yapamadım" demeye izin veren**,
> sakin görünümlü bir Android uygulaması.

## Neden var?

İki gündelik sinir bozukluğundan doğdu:

1. **Forest (kronometre modu):** Mola sadece 5 dakika. Geç dönünce sayaç çalışmaya devam
   ediyor ve olduğundan fazla çalışmış görünüyorsun. Kayıt yalan söylüyor.
2. **Google Tasks:** Bir görevi yapamadıysan seçeneğin yok. Ya "yaptım" diyeceksin ya
   sileceksin. "O gün bu vardı ve olmadı" diye bir gerçek kaydedilemiyor.

İkisinin ortak kökü aynı: **uygulamalar iyimser senaryoyu kaydediyor, gerçeği değil.**
Bu projenin tek büyük fikri bu — *dürüst kayıt*.

## Dosya rehberi

| Dosya | İçerik |
|---|---|
| [01-problem-tanimi.md](01-problem-tanimi.md) | Şikâyetlerin ayrıştırılmış hali, kök neden analizi |
| [02-urun-vizyonu.md](02-urun-vizyonu.md) | Ürünün duruşu, ilkeler, kullanıcı profilleri |
| [03-cozum-zamanlayici.md](03-cozum-zamanlayici.md) | Mola/kronometre sorununa 8 somut çözüm önerisi |
| [04-cozum-gorevler.md](04-cozum-gorevler.md) | "Yapamadım" durumu ve görev durum modeli |
| [05-ozellik-listesi.md](05-ozellik-listesi.md) | MVP / v1 / sonrası özellik ayrımı |
| [06-estetik-konseptler.md](06-estetik-konseptler.md) | Üç görsel yön, karşılaştırma ve öneri |
| [07-teknik-plan.md](07-teknik-plan.md) | Android tarafı: teknoloji seçimi, tuzaklar |
| [08-veri-modeli.md](08-veri-modeli.md) | Tablolar, alanlar, neden öyle |
| [09-elestiri-ve-riskler.md](09-elestiri-ve-riskler.md) | Fikrin zayıf noktaları — dürüst versiyon |
| [10-yol-haritasi.md](10-yol-haritasi.md) | İlk yol haritası (MVP öncesi, artık tarihçe) |
| [11-rakip-analizi.md](11-rakip-analizi.md) | Forest, Toggl, TickTick vb. ve boşluk nerede |
| [12-isim-fikirleri.md](12-isim-fikirleri.md) | İsim adayları |
| [14-uygulama-v1.md](14-uygulama-v1.md) | İlk çalışan APK, teknik plandan sapmalar |
| [15-yol-haritasi-v2.md](15-yol-haritasi-v2.md) | v2.0'da ne değişti, sıradaki işler, Drive senkronu ve Tasks köprüsü |
| [16-para-kazanma.md](16-para-kazanma.md) | Fiyat modeli, Play Store şartları, zamanlama |
| [17-google-senkron.md](17-google-senkron.md) | Drive senkronu: kararlar, çakışma kuralları, Google Cloud kurulumu |
| [18-native-gecis.md](18-native-gecis.md) | Gradle projesine geçiş, bildirim çubuğunda canlı sayaç, CI |
| [19-akis-ve-cubuk.md](19-akis-ve-cubuk.md) | İki tasarım denemesinin uygulamaya geçişi, demodan farklar, sayılmayan sürenin çizilmesi |
| [20-sanat-geri-bildirim.md](20-sanat-geri-bildirim.md) | Çizim/görsel geri bildirimler |
| [21-tam-ekran-widget-fiyat.md](21-tam-ekran-widget-fiyat.md) | Tam ekran seans, widget kararı, **ödeme modeli: peşin 9,99 $** |
| [22-coklu-dil.md](22-coklu-dil.md) | i18n altyapısı ve İngilizce |
| [23-masaustu-ve-native-karar.md](23-masaustu-ve-native-karar.md) | Native geçişin gerekçesi (S4a/S4b/S4c ayrımı), **Compose'a geçilmeyecek**, masaüstü sürüm ve Microsoft Store |

## Şu anki durum

- [x] Problem netleşti
- [x] Notlar yazıldı
- [x] Estetik yön seçildi: **Kâğıt**, açık mod imza, **kertik kadranı**
- [x] MVP kodu ve çalışan APK (v1.0)
- [x] v2.0: yeni tasarım dili, pomodoro modu, seans sonu dürüstlük sorusu
- [x] Google Drive senkronu — kod yazıldı ve test edildi ([17](17-google-senkron.md))
- [ ] Google Tasks köprüsü
- [ ] Ayna sekmesi (istatistik)
- [x] Gradle projesi + bildirim çubuğunda canlı sayaç ([18](18-native-gecis.md))
- [x] Akış alanı, çubuk kaydı, ay duvarı ([19](19-akis-ve-cubuk.md))
- [x] Hızlandırılmış simülatör — `simulasyon/simulator.html`
- [ ] Palet kararı: kâğıt yönü bırakıldı, daha canlı renk aranıyor (simülatörde beş aday)
- [ ] Tam ekran seans modu, ana ekran widget'ı, ince haptik, DND ([21](21-tam-ekran-widget-fiyat.md))
- [x] ~~Compose arayüz~~ — **yapılmayacak, arayüz web kalıyor** ([23](23-masaustu-ve-native-karar.md))
- [ ] Play Store
- [ ] Masaüstü sürüm (Tauri) + Microsoft Store — sınavdan sonra ([23](23-masaustu-ve-native-karar.md))

## Bir sonraki adım

`kertik-android/OKU.md` — depoyu GitHub'a it, iki sırrı tanımla, Actions'ın yeşil
olmasını bekle. Çıkan APK 2.2'nin üstüne kurulur, kayıtlar durur.

Sonra Drive senkronunu gerçek Google'a karşı ilk kez dene; artık `google.com/device`
bağlantısı sistem tarayıcısında açılıyor.

Ondan sonrası **S2, Tasks köprüsü**. Cihaz akışı `auth/tasks` kapsamını desteklemiyordu;
artık gerçek bir Gradle projesi olduğu için normal OAuth mümkün, yani engel kalktı.
Altın kural yine aynı:

> Google Tasks'a olmamış bir "tamamlandı" asla yazılmaz.

## Nerede ne var

> **UYARI (18 Ağustos 2026) — iki `index.html` var, biri ölü.** Aşağıdaki
> tablo bunu daha önce net yazmıyordu ve bir Claude oturumu bu yüzden yanlış
> dosyayla çalışmaya başladı. Tek doğru, canlı, düzenlenen dosya:
> **`kertik-android/app/src/main/assets/index.html`.** `uygulama/www/index.html`
> ve `uygulama/imza/` (`derle.py`, `apkbuild.py`, `sablon.apk`) native geçişten
> ([18](18-native-gecis.md)) kalma eski Cordova zincirinin parçaları — artık
> **kullanılmıyor** (kurulum Android Studio'dan yapılıyor, APK yaması yolu
> terk edildi). `apkbuild.py` ayrıca `assets/www/index.html` yoluna yama
> yapıyor; bu, güncel dosyanın Android paketindeki gerçek yoluyla
> (`assets/index.html`, `www/` alt klasörü yok) uyuşmuyor — o script artık
> hiçbir güncel dosyayla doğru çalışmaz. Silinmediler, ama bir sonraki
> oturum önce bu uyarıyı okumalı.

| Yol | İçerik |
|---|---|
| `kertik-android/` | **Asıl proje.** Gradle, API 36, AAB üretir, CI'lı |
| `kertik-android/app/src/main/assets/index.html` | **Canlı, tek doğru kaynak.** Uygulamanın tamamı — buradan düzenlenir, Android Studio'dan derlenir |
| `uygulama/Kertik-2.2.apk` | Eski zincirin son APK'sı (donduruldu, artık üretilmiyor) |
| `uygulama/imza/` | **Ölü — kullanılmıyor.** Eski Cordova zincirinin APK yama/imza betikleri, yukarıdaki uyarıya bakın |
| `uygulama/test/` | Birleştirme birim testleri + sahte Google ile uçtan uca test — hangi `index.html`'e karşı koştuğu kontrol edilmeli, bkz. `kertik-android/test/` (güncel testler orada) |
| `uygulama/www/index.html` | **Ölü — kullanılmıyor, güncellenmiyor.** Eski Cordova kopyası, yukarıdaki uyarıya bakın |
| `tasarim/kertik-tasarim-laboratuvari.html` | Üç estetik yönün karşılaştırması |
| `tasarim/kertik-kadran.html` | Kertik kadranının canlı, hızlandırılabilir demosu |
| `tasarim/akis.html` | Akış alanının demosu — uygulamaya geçti ([19](19-akis-ve-cubuk.md)) |
| `tasarim/cubuk.html` | Çubuk kaydının ve duvarın demosu — uygulamaya geçti ([19](19-akis-ve-cubuk.md)) |
| `tasarim/duvar-tas-secenekleri.html` | Pomodoro duvarı için taş kompozisyon denemeleri — karar "hesap taşları", uygulamaya geçti ([27](27-sanat-ayrisimi.md)) |
| `simulasyon/simulator.html` | **Hızlandırılmış tezgâh.** Gerçek uygulamayı sanal saatle koşturur; palet denemek için |
| `simulasyon/olustur-simulator.js` | Simülatörü üretir. Uygulama değişince `node simulasyon/olustur-simulator.js` |
