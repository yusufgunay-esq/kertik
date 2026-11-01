# Girdi Envanteri ve Gerçeklik Manifesti (Tohum / Arka Plan Dua Mimarisi)

## 1. Kullanıcı Talebi ve Doğrulama
- **Kullanıcı İfadesi:** "Uygulamamızda besmele ve Rabbi Yessir duası var ya hatta desenler de ona göre çiziliyor diye biliyorum ceed olarak bu arka planda yani kullanıcıya gösterilmeden her seans başlatıldığında da yazsa ya yap, ayrıca başka dua önerirsen onu da söyle bana"
- **Temel Varsayım Doğrulaması (Premise Attack):**
  - Kod tabanında (`kertik-android`, `simulasyon`, dokümantasyon) "besmele", "rabbi", "yessir", "dua", "bismillah" anahtar sözcükleri ripgrep ile tarandı.
  - **Sonuç:** Kod tabanında şu an hiçbir dua veya besmele metni bulunmamaktadır. Mevcut tohumlama saf zaman damgası ve rastgele string üzerinden (`hash32(id)` / `uid()`) yapılmaktadır.
  - **Karar:** Kullanıcıya mevcut durum açıkça ve dürüstçe bildirilecek; ardından talep ettiği gibi hem tohumlama formülüne hem de seans başlangıç yaşam döngüsüne sessizce (kullanıcıya görsel/arayüz kalabalığı çıkarmadan) dahil edilecek mimari sunulacaktır.

## 2. İncelenen Dosyalar ve Ölçümler
1. `CLAUDE.md` (120 satır, 5.622 bayt):
   - Tek canlı kaynağın `kertik-android/app/src/main/assets/index.html` olduğu teyit edildi.
   - Test komutunun `node test/hepsi.js --hizli` olduğu belirlendi.
2. `kertik-android/app/src/main/assets/index.html` (7.957 satır, 504.968 bayt):
   - Satır 1069: `uid()` üretimi.
   - Satır 1223–1260: `startSession()` seans başlatma fonksiyonu.
   - Satır 2852: `hash32(t)` FNV-1a 32-bit tohum hash fonksiyonu.
   - Satır 3643–3660: `akisBaslat(se)` fonksiyonunda `AK.tohum = hash32(id)` ile Ebru akış çizgilerinin üretilmesi.
   - Satır 3390: `tasSvg(..., hash32((v.id || "x") + "|" + globalIdx))` ile Zen taşlarının tohumlanması.
3. `kertik-android/test/test-cizim.js` (533 satır, 26.418 bayt):
   - Tohum determinizmi testleri incelendi.
4. `kertik-android/test/hepsi.js`:
   - 12 test dosyası icra edildi, 24.0 saniyede tüm testlerin (0 hata) geçtiği kanıtlandı.
