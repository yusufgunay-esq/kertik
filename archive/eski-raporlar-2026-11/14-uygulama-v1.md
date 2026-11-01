# 14 — Kertik v1.0 (çalışan sürüm)

İlk gerçek APK. `06`'daki karara sadık: sadece **Konsept B (Sakin)**, çizim yok, grafik yok.
`07`'deki altın kural uygulandı: **sayaç saymıyor, olay damgalarından hesaplanıyor.**

## Ne var

| Karar | Durum |
|---|---|
| Ç1 Sınırsız mola | ✅ Mola kendiliğinden bitmiyor, sadece sen bitiriyorsun |
| Ç2 Onaylanmamış süre | ✅ Varsayılan 20dk teyit, cevapsız kalan süre ayrı gösteriliyor ve toplamdan düşülüyor |
| Ç3 Geçmişi düzeltme | ✅ Başlangıç/bitiş saati düzenleme, seans silme, "onaylanmamışı say" |
| Ç4 Dönüşte akıllı soru | ✅ 25dk üstü molalarda üç seçenek (doğru / erken döndüm / seansı orada bitir) |
| Ç6 Yumuşak dönüm noktası | ✅ Varsayılan 50dk, hiçbir şeyi durdurmuyor |
| Kayıt | ✅ Gün gün liste + **saat saat zaman çizelgesi** (başladı / molaya girdi / devam etti / bitirdi) |
| G1 6 durumlu görev | ✅ bekliyor · yapılıyor · bitti · olmadı · taşındı · iptal |
| G2 Sebep etiketleri | ✅ "olmadı"da atlanabilir tek soru |
| G3 Gün sonu ritüeli | ✅ Geçmiş günlerden kalanlar + toplu taşı / toplu olmadı |
| G4 Erteleme sayacı | ✅ `↻n` işareti |

**Yok:** DND, widget, bildirim çubuğunda canlı sayaç, istatistik grafikleri, seansı göreve bağlama.
DND ve kalıcı bildirim native kod istiyor; bu sürüm WebView tabanlı.

## Teknik gerçeklik (07'den sapma)

`07-teknik-plan.md` Kotlin + Compose diyor ve uzun vadede doğru olan bu.
Ama bu APK **WebView tabanlı**: tek bir `index.html` + 9,6 KB'lık Java köprüsü.
Sebep: derleme ortamında Android SDK'ya erişim yoktu; Gradle'sız, SDK'sız üretildi
(hazır APK şablonuna varlık enjeksiyonu + aapt2 ile kaynak derleme + v1/v2/v3 imza).

Bunun bedeli:
- Arka planda foreground service yok → **bildirim çubuğunda canlı sayaç yok**.
- Uygulama kapalıyken teyit titreşimi gelmez.
- **Ama süre bozulmaz.** Olay damgaları `Date.now()` ile tutuluyor; uygulamayı kapatsan,
  telefon yeniden başlasa da açılışta seans olduğu yerden doğru şekilde devam eder.

Kotlin sürümüne geçildiğinde veri modeli aynen taşınabilir: `session` + `session_event`
akışı `08-veri-modeli.md` ile birebir aynı.

## Veri

Her şey telefonda, `localStorage` içinde. Hesap yok, sunucu yok, internet izni sadece
WebView şablonundan geliyor, hiçbir istek atılmıyor.
**Yedek: Ayarlar → dışa aktar.** Uygulamayı silersen kayıt da gider, ara ara al.

## Doğrulama

Sayaç mantığı için birim testler koşuldu (`09`'daki "test edilmemiş sayaç ironik olurdu" notu):
- 3 mola, biri 41dk → brüt 180dk, mola 58dk, net 122dk ✅
- 60. dk teyit, 95. dk onay → 35dk onaylanmamış, 85dk doğrulanmış ✅
- Cevapsız teyit → seans sonuna kadar onaylanmamış ✅
- Süren mola → net donuyor, mola akıyor ✅

Arayüz akışı da otomatik tarayıcı testinden geçirildi: 52dk çalışma → 41dk mola →
"erken döndüm" düzeltmesi → 1s 38dk doğru toplam.

## Sonraki adımlar

1. Birkaç hafta kullan, `05`'teki v1 listesini gerçek kullanımına göre buda.
2. Bildirim çubuğunda canlı sayaç + DND gerekiyorsa Kotlin sürümüne geç.
3. İsim kesinleşince paket adı `com.baki.kertik` güncellenir.
