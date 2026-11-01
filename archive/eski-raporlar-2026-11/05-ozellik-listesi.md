# 05 — Özellik Listesi (MVP / v1 / Sonrası)

Kapsam disiplini bu projenin en büyük riski.
Kural: **MVP'de olan her özelliğin bir şikâyete karşılık gelmesi gerekiyor.**

---

## MVP — "kendim kullanabilir miyim" sürümü

**Hedef**: 2–3 hafta. Yayınlanmaz, sadece telefona kurulur.

### Zamanlayıcı
- [ ] Kronometre modu: başlat / mola / devam / bitir
- [ ] **Sınırsız mola** (Ç1)
- [ ] Mola ve çalışma sürelerinin ayrı tutulması
- [ ] Uygulama kapansa/telefon yeniden başlasa bile doğru süre
      (zaman damgası tabanlı, tick sayarak değil — bkz. [07](07-teknik-plan.md))
- [ ] Bildirim çubuğunda canlı sayaç, oradan mola/devam
- [ ] **Onaylanmamış süre** teyit sistemi (Ç2) — varsayılan 20dk, kapatılabilir
- [ ] Uzun moladan dönüşte düzeltme sorusu (Ç4)
- [ ] Yumuşak dönüm noktası bildirimi (Ç6) — varsayılan 50dk, kapatılabilir

### Kayıt
- [ ] Seans listesi (bugün / bu hafta)
- [ ] **Seansı sonradan düzenleme**: başlangıç, bitiş, mola, sil (Ç3)
- [ ] Günlük toplam: çalışma + mola + onaylanmamış ayrı ayrı

### Görevler
- [ ] Basit günlük liste: ekle, sil, sırala
- [ ] **6 durumlu** işaretleme (G1)
- [ ] Gün sonu kapanış ekranı (G3)

### Genel
- [ ] Tek ekranlık ana görünüm, tek büyük başlat tuşu
- [ ] Karanlık mod
- [ ] Tamamen çevrimdışı, hesap yok

**MVP'de OLMAYACAKLAR:** istatistik grafikleri, sebep etiketleri, görsel/animasyon ödülü,
DND, widget, yedekleme, ayarların çoğu.

---

## v1 — "anneme kurabilir miyim" sürümü

Hedef: MVP'yi 3–4 hafta kullandıktan sonra.

- [ ] Görsel kimlik tam uygulanmış hali ([06-estetik-konseptler.md](06-estetik-konseptler.md))
- [ ] Seçilen estetik konseptin ödül katmanı (büyüyen görsel / seans kartı)
- [ ] **Rahatsız Etmeyin** entegrasyonu (Ç8) + seans sonu otomatik kapatma
- [ ] Seansı göreve/konuya bağlama (Ç7)
- [ ] Sebep etiketleri (G2)
- [ ] Erteleme sayacı ve nazik soru (G4)
- [ ] Takvim / geçmiş gün görünümü (G5)
- [ ] Haftalık özet: konu bazında süre, tamamlanma oranı
- [ ] Ana ekran widget'ı (tek dokunuşla başlat)
- [ ] Basit onboarding: 3 ekran, atlanabilir
- [ ] JSON dışa/içe aktarma (yedek)

---

## v2 — "başkaları da kullanabilir" sürümü

- [ ] Geri sayım (pomodoro) modu — kronometrenin yanında
- [ ] Tekrarlayan görevler
- [ ] Sensör/ekran sinyalleriyle akıllı mola tahmini (Ç5)
- [ ] Çapraz içgörüler (G6): "planladığının %63'ünü bitiriyorsun"
- [ ] Tahmin vs gerçek süre öğrenmesi
- [ ] Uygulama engelleme (belirli uygulamaları seans boyunca kilitleme)
- [ ] Ortam sesleri (yağmur, kafe) — *belki, sessiz arayüz ilkesiyle çelişebilir*
- [ ] Bulut yedek / çoklu cihaz
- [ ] Play Store yayını

---

## Asla yapmayacaklarımız

Bunları liste dışı tutmak bir karar, unutkanlık değil:

- ❌ Seri (streak) ve seri kaybetme korkusu
- ❌ Arkadaş listesi, sıralama tablosu, sosyal baskı
- ❌ Reklam
- ❌ Zorunlu hesap açma
- ❌ Motivasyon bildirimleri ("Seni özledik!")
- ❌ Yapay puan/coin ekonomisi
- ❌ Yapay zekâ sohbet asistanı (çünkü herkes ekliyor diye eklemek en kötü sebep)

Gerekçe: bunların hepsi kısa vadede kullanım artırır, uzun vadede **uygulamanın sessiz kalma
sözünü bozar.** Bu ürünün tek satılık noktası güven.
