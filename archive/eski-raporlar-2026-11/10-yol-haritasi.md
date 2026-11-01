# 10 — Yol Haritası

Tarihler değil, **sıra** önemli. Her aşamanın çıkış koşulu var; koşul sağlanmadan sonrakine geçilmez.

---

## Aşama 0 — Kâğıt (1–2 gün)

Kod yok.
- [ ] Ekran akışını kâğıda çiz: ana ekran → çalışıyor → molada → seans özeti → görev listesi → gün sonu
- [ ] Estetik yönü seç ([06-estetik-konseptler.md](06-estetik-konseptler.md)) — öneri: MVP'de sadece Konsept B
- [ ] Teknolojiyi seç ([07-teknik-plan.md](07-teknik-plan.md)) — öneri: Kotlin + Compose
- [ ] İsmi seç ([12-isim-fikirleri.md](12-isim-fikirleri.md)) — sonra değişebilir, şimdilik bir şey yeter

**Çıkış koşulu:** çalışma ekranını kâğıtta görüyorsun ve içinde 3'ten fazla şey yok.

---

## Aşama 1 — Sayaç çekirdeği (1 hafta)

**UI yok, ekran yok.** Sadece mantık ve testler.
- [ ] Veri modeli + Room şeması ([08-veri-modeli.md](08-veri-modeli.md))
- [ ] `SessionEngine`: start / break / resume / end / presence, hepsi olay tabanlı
- [ ] Türetilmiş hesaplar: brüt, mola, net, onaylanmamış, doğrulanmış
- [ ] **Birim testleri**: en az şu vakalar
  - 3 mola, biri 41 dk → doğru net süre
  - hiç onay gelmemiş 40 dk → onaylanmamış olarak işaretlenmiş
  - seans ortasında yeniden başlatma → süre korunuyor
  - gece yarısını geçen seans → başlangıç gününe yazılıyor
  - elle düzeltme sonrası tüm türetilmiş sayılar tutarlı

**Çıkış koşulu:** testler yeşil. Bu aşamayı atlamak, projenin şikâyet ettiği hatayı
kendi elle yeniden üretmek olur.

---

## Aşama 2 — Çalışan uygulama (1 hafta)

- [ ] Ana ekran: tek büyük başlat tuşu, sayaç, tek satır "ne çalışıyorsun"
- [ ] Mola / devam / bitir akışı
- [ ] Foreground service + canlı bildirim + bildirim aksiyonları
- [ ] Uzun moladan dönüşte düzeltme sorusu (Ç4)
- [ ] Yumuşak dönüm noktası bildirimi (Ç6)
- [ ] Seans listesi + **seans düzenleme ekranı** (Ç3)
- [ ] Karanlık mod
- [ ] Telefona kur

**Çıkış koşulu:** 3 gün üst üste kendi telefonunda sorunsuz kullanıldı, süre hiç yanlış saymadı.

---

## Aşama 3 — Paralel kullanım denemesi (3 hafta) ⭐

Bu aşama kod yazmak kadar önemli, ve genelde atlanır.

- [ ] Forest'ı **silme.** İkisini yan yana kullan.
- [ ] Her gün hangisini açtığını not et. Neden?
- [ ] Onaylanmamış süre dürtmesini 1. hafta açık, 2. hafta kapalı kullan. Hangisi daha iyi?
- [ ] Rahatsız eden, eksik gelen, hiç kullanılmayan her şeyi bu klasördeki bir
      `bulgular.md` dosyasına yaz.

**Çıkış koşulu:** kendi uygulamana Forest'tan daha çok basıyorsun.
Basmıyorsan — dur ve sebebini anla. Özellik eklemek çözüm değil.

---

## Aşama 4 — Görev tarafı (1–2 hafta)

Aşama 3'ten "evet, görev tarafı gerçekten lazım" cevabı çıktıysa.
- [ ] Günlük liste, ekle/sil/sırala
- [ ] 6 durumlu işaretleme (G1)
- [ ] Gün sonu kapanış ekranı (G3)
- [ ] Sebep etiketleri (G2)
- [ ] Seansı göreve bağlama (Ç7)
- [ ] Takvim / geçmiş gün görünümü (G5)

**Çıkış koşulu:** iki hafta boyunca Google Tasks'ı açmadın.

---

## Aşama 5 — Güzelleştirme ve "anne sürümü" (1–2 hafta)

- [ ] Estetik konseptin tam uygulanışı
- [ ] Seans sonu kartı / tamamlanan görsel (Konsept A ödül katmanı)
- [ ] Rahatsız Etmeyin entegrasyonu (Ç8) + iki katmanlı geri alma
- [ ] Widget
- [ ] 3 ekranlık atlanabilir onboarding
- [ ] JSON yedek
- [ ] Anneye kur, **hiçbir şey açıklamadan** ilk seansı yapmasını izle

**Çıkış koşulu:** annen tek soru sormadan bir seans tamamladı.
Sorduğu her soru bir tasarım hatasıdır — not al, düzelt.

---

## Aşama 6 — İstatistik ve içgörü

- [ ] Haftalık özet, ısı haritası, konu dağılımı (Konsept C)
- [ ] Sebep dağılımı ve kapasite içgörüsü ("günde 6 planlıyorsun, 3,8 bitiyor")
- [ ] Tahmin vs gerçek süre

---

## Aşama 7 — Yayın (isteğe bağlı)

Sadece Aşama 3–5'ten geçmiş, gerçekten kullandığın bir uygulama varsa.
- [ ] Gizlilik politikası ("hiçbir veri toplanmıyor")
- [ ] Play Console, foreground service tipi gerekçesi
- [ ] Ekran görüntüleri, açıklama metni
- [ ] Kapalı test: 5–10 kişi

---

## Nerede duracağını bilmek

Bu projeyi bitirmenin **üç meşru yolu** var:
1. Yayınlanmış bir uygulama.
2. Sadece kendinin kullandığı, Play Store'a hiç çıkmamış bir uygulama. ← en olası ve tamamen yeterli
3. Aşama 3'te "aslında Forest'ta esnek mola ayarını bulup halloldu" demek. ← bu da başarıdır, kayıp değil

Üçüncüsü olursa: 4 haftalık Android + Compose deneyimi kazanmış olursun.
Zaten fena bir sonuç değil.
