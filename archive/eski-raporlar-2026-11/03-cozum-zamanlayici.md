# 03 — Zamanlayıcı Tarafı: Çözüm Önerileri

Problem: [01-problem-tanimi.md](01-problem-tanimi.md) bölüm A.
Aşağıdaki 8 fikir bağımsız değil, **katmanlar**. 1–3 zorunlu çekirdek, 4–8 üstüne binen akıl.

---

## Ç1. Molanın üst sınırı yok *(zorunlu)*

Mola tuşuna basınca:
- Çalışma sayacı **durur**, yerinde donar.
- Mola sayacı **kendi başına** ilerlemeye başlar, sınırsız.
- Mola kendiliğinden bitmez. Sadece sen bitirirsin.

Böylece "geç kaldım, sayaç çalışmış" durumu **yapısal olarak imkânsız** hale gelir.
Bu tek başına şikâyetin %80'ini çözer.

Ekranda mola sırasında: `Mola — 12:41` ve tek tuş: **Devam et**.
Uyarı değil, bilgi. "Molan uzadı" demez.

---

## Ç2. Onaylanmamış süre (unconfirmed time) *(zorunlu — projenin fikri)*

Uygulama, çalışma modundayken **düzenli olarak "hâlâ orada mısın?" diye teyit alır.**
Ama can sıkmadan:

- Her N dakikada (varsayılan 20) **tek bir kısa titreşim**, ses yok, ekran açılmaz.
- Ekranda küçük bir nokta yanar. Telefona bakınca tek dokunuşla onaylarsın.
- Onaylamazsan seans durmaz — ama o andan itibaren geçen süre **"onaylanmamış"** işaretlenir.

Sonra:
- Seans bitince: `1s 47dk çalışma · 20dk onaylanmamış` diye ayrı gösterilir.
- İstatistiklerde onaylanmamış süre **varsayılan olarak sayılmaz**.
- Tek dokunuşla "hayır, o sürede de çalışıyordum" diyebilirsin ve sayılır.

> Neden bu güzel: uygulama artık tahmin etmiyor. *Bilmediğini söylüyor.*
> Hiçbir rakip bunu yapmıyor ve bu, ürünün imzası olabilir.

Ayar seçenekleri: teyit kapalı / 20dk / 30dk / 45dk.
Anne profili için varsayılan **kapalı** olmalı — o telefonu yanında tutuyordur.

---

## Ç3. Geçmişi düzeltebilme *(zorunlu)*

Her seans, bittikten sonra düzenlenebilir bir kayıt:
- Başlangıç saatini değiştir
- Bitiş saatini değiştir
- Molayı uzat/kısalt, mola ekle, mola sil
- Seansı ikiye böl, iki seansı birleştir
- Seansı tamamen sil

Arayüz: seans kartına dokun → zaman çizelgesi görünümü → parçaları sürükleyerek düzelt.
Hızlı düzeltmeler için hazır tuşlar: `−5dk` `−15dk` `Şimdi bitir`.

Bu, Toggl'ın en iyi özelliği ve odak uygulamalarının hiçbirinde yok.

---

## Ç4. Dönüşte akıllı soru

Mola 25 dakikayı geçtiyse, "Devam et"e bastığında tek bir soru çıkar:

> Molan 41 dakika sürdü.
> **[Doğru]**  [Aslında ~15dk sonra döndüm, telefonu almadım]  [Seansı orada bitir]

İkinci seçenek, en sık yaşanan gerçeği tek dokunuşla düzeltir:
telefonu bırakıp gittin, geri döndün, molayı bitirmeyi unuttun, sonra hatırladın.

Kritik detay: bu soru **çalışma süresini şişirmeye değil, doğrultmaya** yarar.
Ve varsayılan cevap her zaman "daha az çalışma" yönünde.

---

## Ç5. Ekran/hareket sinyalleriyle yumuşak tahmin

Kesin karar vermeden ipucu toplama:
- Telefon ekranı açıldı → muhtemelen yanındasın
- Uzun süre tamamen hareketsiz (sensör) → muhtemelen masada bırakılmış

Bu sinyaller **asla otomatik karar vermez**, sadece Ç4'teki sorunun tahminini iyileştirir:
"Molan 41 dakika sürdü, ama telefonu 14:52'de aldın. Molayı orada bitireyim mi?"

> Not: bu özellik pil ve izin maliyeti getirir. MVP'ye **girmeyecek**, v2 fikri.
> Ç2 + Ç4 zaten yeterince iyi çalışıyor.

---

## Ç6. Kronometre ama yumuşak sınırlı ("açık uçlu pomodoro")

Kronometre modunun bilinen zayıflığı: yapı yok, sınır yok
(bkz. [09-elestiri-ve-riskler.md](09-elestiri-ve-riskler.md)).
Ama Pomodoro'nun katılığı da sinir bozucu — tam akışa girmişken zil çalıyor.

Orta yol: **kronometre serbest akar, ama nazik dönüm noktaları var.**
- 50. dakikada tek titreşim + ekranda küçük bir işaret: *"50 dakika oldu."*
- Hiçbir şey durmaz, hiçbir şey zorunlu değil.
- İstersen o an mola verirsin, istersen 90 dakika devam edersin.

Böylece Pomodoro'nun faydası (sınırın farkında olma) alınır, zararı (kesinti) alınmaz.
Ayarlanabilir: kapalı / 25 / 50 / 90 dakika.

---

## Ç7. Seans bir göreve bağlanır

Başlat ekranında isteğe bağlı tek alan: **ne çalışıyorsun?**
- Bugünün görev listesinden seç, ya da
- Konu/etiket seç (Matematik, Kitap, İş), ya da
- Boş bırak (anne profili: hiç sorma, tek tuş başlat)

Kazanç:
- "Bu hafta matematiğe 6s 20dk" gibi gerçek veri.
- Gün sonunda: *"Matematik'e 1s 40dk verdin ama görevi tamamlandı işaretlemedin."*
- Zamanla **tahmin vs gerçek** öğrenmesi: "bu işe 30dk derdin, ortalama 55dk sürüyor."

---

## Ç8. Rahatsız etme modu entegrasyonu

Seans başlarken opsiyonel: **telefonu sessize al.**
- Android'de Rahatsız Etmeyin (DND) izniyle yapılır, tek onayla.
- Seans/mola bitince otomatik geri açılır — asıl değer bu, çünkü insan geri açmayı unutuyor.
- Molada DND kalksın mı? Ayar. (Varsayılan: kalksın, çünkü mola = telefon zamanı.)

Teknik detaylar: [07-teknik-plan.md](07-teknik-plan.md).

---

## Karar özeti

| Fikir | MVP'de mi? | Zorluk |
|---|---|---|
| Ç1 Sınırsız mola | ✅ Evet | Düşük |
| Ç2 Onaylanmamış süre | ✅ Evet | Orta |
| Ç3 Geçmişi düzeltme | ✅ Evet | Orta |
| Ç4 Dönüşte akıllı soru | ✅ Evet | Düşük |
| Ç5 Sensör tahmini | ❌ v2 | Yüksek |
| Ç6 Yumuşak dönüm noktası | ✅ Evet | Düşük |
| Ç7 Göreve bağlama | 🟡 v1 | Orta |
| Ç8 DND | 🟡 v1 | Orta (izin akışı) |
