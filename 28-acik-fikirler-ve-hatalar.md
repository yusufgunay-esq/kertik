# 28 — Açık Fikirler ve Hatalar (henüz karar dosyası yok)

> Kaynak: `13-bulgular.md` (16–17 Ağustos) ve `Notlarım.md` (18 Ağustos) —
> [20](20-sanat-geri-bildirim.md), [24](24-sanat-dili.md), [26](26-widget-uygulandi.md),
> [27](27-sanat-ayrisimi.md) gibi bir karar dosyasına henüz işlenmemiş kalan maddeler.
> Her madde işlendiğinde buradan silinip ilgili karar dosyasına taşınmalı.

Tarih: 18 Ağustos 2026

---

## Hatalar

1. **Sağ bar kalıntısı.** Sağ barda bazen "tablo" ve "görev" yazan, etkileşimsiz,
   kötü bir fonda duran bir öğe görünüyor. Hiçbir işlevi yok — ne tabloyla ne
   görevle etkileşime girilebiliyor. Kaldırılmalı ya da düzgün tasarlanana kadar
   gizlenmeli.
2. **Ebru açık modda zayıf.** Ebru deseni koyu modda iyi duruyor ama aydınlık
   modda o kadar iyi görünmüyor — algoritma açık zemine göre ayrıca
   ayarlanmalı.

---

## Fikirler

3. **Akıllı saat companion app'i.** Mola/devam/bitir tuşlarına saatten
   basılabilsin.
4. **Sistem koyu/açık mod ayarına otomatik uyum.** Şu an manuel mi otomatik mi
   net değil, kontrol edilmeli.
5. **Pomodoro'da üstte küçük bir sayaç.** Kaçıncı pomodoro olduğunu gösteren
   bir rakam (1, 2, 3…), gün batımında sıfırlanır.
   ([27](27-sanat-ayrisimi.md)'deki "duvarda taş sayısı" ile aynı aile, ama o
   günün toplamı yerine seans sırasında anlık göstergeye dair.)
6. **Çalışma modunda telefon sessize alınsın** (medya sesleri hariç). Bu zaten
   yol haritasında Ç8 / S4b olarak planlı ([15-yol-haritasi-v2.md](15-yol-haritasi-v2.md));
   buraya not düşüldü çünkü kullanım sırasında tekrar hissedilmiş bir ihtiyaç.
7. **"Telefon kullanılırsa sanat bozulur" fikri.** Çalışma sırasında telefon
   kullanılırsa ebru/kum bahçesinin bozulması. Kullanıcı bunun kullanım
   tespiti gerektirdiğini ve "kullanıcıyı izlemek" gibi hissettiğini kendi
   belirtti; en kaba yol kilit ekranının açılıp açılmadığına bakmak olabilir.
   Karar verilmeden önce `09-elestiri-ve-riskler.md` ile birlikte
   değerlendirilmeli — "hiçbir veri toplanmıyor" sözüyle gerilebilir.
8. **Ana ekran "teaser" metni moda göre farklı olmalı.** Kronometre modunda
   çalıştıkça arkada ilerde ne olacağına dair bir teaser görüntü/metin
   çıkıyor; pomodoro modunda bu metin ve teaser şu an aynı gibi duruyor,
   ayrışmalı.
9. **Kum Bahçesi — Tırmığın Taşı Organik Sarması (Laminar Akış / Erken Halka Optimizasyonu):**
   Mevcut `smin` modelinde tırmık daha ekranın yukarısındayken aşağıdaki taşların etrafında
   bağımsız halkalar önceden beliriyor (kapalı eşmerkezli kontur). 20 Ağustos 2026'da
   tırmık cephesini taşı laminar olarak bükecek bir domain deflection modeli denendi
   ancak animasyon/görsel his şu anki eşmerkezli halka dinginliğini vermediği için
   geri alındı. İleride animasyonlar, geçişler veya alternatif bir tırmık deformasyonu
   daha rafine edilerek tekrar masaya yatırılabilir. Formül temeli: `domain warp + inverse push vector`.
