# Kabul Sözleşmesi: Tohum ve Arka Plan Dua Entegrasyonu

| Madde | Gereksinim / Kriter | Ölçüm / Kanıt | Durum |
|---|---|---|---|
| C1 | **Dürüst Bilgilendirme**: Kod tabanında Besmele ve Rabbi Yessir'in henüz bulunmadığı gerçeğinin kullanıcıya şeffafça açıklanması | Yanıt metninde açıklandı | GEÇTİ |
| C2 | **Sessiz / Sıfır Sürtünmeli UX**: Arayüze hiçbir dini buton, rozet veya görsel kalabalık eklenmemesi; tamamen arka planda çalışması | UI DOM ve CSS sıfır regresyon; ekranda hiçbir fazlalık yok | GEÇTİ |
| C3 | **Tohum (Seed) Entegrasyonu**: Ebru ve Zen taşı algoritmalarının tohum hesabında Besmele + Rabbi Yessir + Hz. Musa duası metinlerinin kök tohum olarak kullanılması | `KOK_TOHUM` ve `seansTohumu()` entegre edildi | GEÇTİ |
| C4 | **Seans Yaşam Döngüsü**: `startSession()` çağrıldığında arka planda sessiz niyet/dua izinin seans verisine ve dahili işleyişe dahil edilmesi | `[seans:id] tohum: ...` logu ve `se.tohum` ataması doğrulandı | GEÇTİ |
| C5 | **Eski Seans Uyumluluğu (Geriye Dönük Uyum)**: Eski seansların çizim damgasının (`akisV`) ve determinizminin bozulmaması | `test-cizim.js` 5.7s yeşil | GEÇTİ |
| C6 | **Dua Önerileri**: Kullanıcının istediği odaklanma, ilim ve zorluğu aşma dualarının anlam ve kaynaklarıyla sunulması | Tâhâ 25-28, Tâhâ 114, İbn Hibbân hadis duası ve İnşirah sunuldu | GEÇTİ |
| C7 | **Test Bütünlüğü**: Değişiklik sonrası `node test/hepsi.js --hizli` paketinin 0 hata ile geçmesi | 12 test dosyası, 30.1s, 0 hata ile GEÇTİ | GEÇTİ |


---

# Kabul Sözleşmesi: Kertik Titreşim ve Dokunsal Geri Bildirim (Haptics) Onarımı

| Madde | Gereksinim / Kriter | Ölçüm / Kanıt | Durum |
|---|---|---|---|
| H1 | **İşletim Sistemi ve DND Kısıtının Aşılması (USAGE_HARDWARE_FEEDBACK)**: MainActivity.kt içinde fireEffect fonksiyonu eklenmeli; USAGE_HARDWARE_FEEDBACK ve USAGE_ASSISTANCE_SONIFICATION ile sistem genelinde dokunma titreşimi kapalı olsa veya DND devrede olsa dahi titreşim çalışmalıdır. | Kotlin kod denetimi | BEKLEMEDE |
| H2 | **Donanım Kompozisyon Primitifleri (LRA Haptics)**: MainActivity.kt kompozisyon yardımcısına sec, baslat, kertik, mola, bitir, not, donum primitifleri eklenmeli; Pixel ve destekleyen cihazlarda anında tık hissi verilmelidir. | Kotlin kompozisyon analizi | BEKLEMEDE |
| H3 | **WebView Haptic Feedback Etkinleştirilmesi**: MainActivity.kt onCreate içinde web.isHapticFeedbackEnabled = true açıkça çağrılmalıdır. | Kod denetimi | BEKLEMEDE |
| H4 | **Mevcut DOKU Sözlüğü ve Test Uyumu**: index.html içindeki DOKU yapısı, KUTLE_PROFILLERI ve taş ağırlık hiyerarşisi bozulmadan komp anahtarlarıyla zenginleştirilmeli; test-haptik.js içindeki 86 testin tamamı firesiz geçmelidir. | test-haptik.js çıktısı (86/86 PASS) | BEKLEMEDE |
| H5 | **kt/MainActivity.txt Senkronizasyonu**: test-haptik.js hem MainActivity.kt hem kt/MainActivity.txt dosyalarını denetlediği için iki dosya da güncellenmeli ve eşit kalmalıdır. | Dosya içerik kontrolü | BEKLEMEDE |
| H6 | **Hızlı Test Paketi Bütünlüğü**: node test/hepsi.js --hizli koşturulmalı ve tüm testler hatasız tamamlanmalıdır. | Test paketi logu (exit code: 0) | BEKLEMEDE |
| H7 | **Android Derleme (Smoke Test)**: gradlew.bat assembleDebug hatasız tamamlanmalıdır. | Gradle derleme logu (exit code: 0) | BEKLEMEDE |
