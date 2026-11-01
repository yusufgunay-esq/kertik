# 06 — Estetik Konseptler

Üç yön ayrı ayrı, sonra öneri. Karar bu dosyadan çıkacak.

---

## Konsept A — "Tamamlanan Görsel"

Instagram'da gördüğün fikrin bizim versiyonu: çalıştıkça bir şey oluşuyor.

### Nasıl görünür
Ekranın ortasında ince çizgili bir illüstrasyon. Zaman geçtikçe çizgiler **çiziliyor** —
kalem gerçekten kâğıtta ilerliyormuş gibi. Renk yok, sadece tek renk çizgi; seans bitince
resim tamamlanınca hafif bir renk dolgusu gelir.

Çizim konuları rastgele bir kütüphaneden: bir ağaç, bir kedi, bir pencere, bir sokak lambası,
bir gemi, bir el. Aynı çizim üst üste iki kez gelmez.

### Kronometre modunun yarattığı zorluk
Geri sayımda "bitiş" belli — resmi ona göre bölersin. **Kronometrede bitiş yok.**
Üç çözüm:

1. **Dönüm noktalı çizim:** her 25 dakikada bir katman tamamlanır. 25dk = ana hatlar,
   50dk = detay, 75dk = gölge, 100dk = renk. Ne kadar çalışırsan resim o kadar "biter".
   Çalışmayı bırakınca resim yarım kalır — ve yarım resim de güzeldir, ceza gibi durmaz.
2. **Sonsuz büyüyen desen:** mandala / şehir silüeti / mercan gibi, teorik sonu olmayan bir form.
   Ne kadar sürerse o kadar büyür.
3. **Kendi hedefini koy:** başlangıçta "bugün bu resmi bitirmek istiyorum" dersin, o resmin
   tahmini süresi (ör. 90dk) hedefin olur. Kronometre serbest ama görsel bir hedefin olur.

> En iyisi 1 + 3 karışımı: varsayılan katmanlı, isteyen hedef koyar.

### Ödül katmanı
- Her tamamlanan seans bir **kart** olur: çizim + tarih + süre + ne çalışıldığı.
- Galeri: ayın kartları bir duvar gibi dizilir. Sadece bakmak bile motive edici.
- Kart tek dokunuşla resim olarak paylaşılabilir (isteyen için).

### Artıları
- Duygusal bağ kurar, "bırakırsam yarım kalır" hissi Forest'ın ağaç fikrinin aynısı ve işe yarıyor.
- Ekran görüntüsü paylaşılabilir → organik yayılma.
- Kronometre modunun "hedefsizlik" zaafını görsel olarak kapatır.

### Eksileri
- **Çok iş.** Onlarca illüstrasyon lazım, hepsi katmanlı SVG olarak hazırlanmalı.
- Animasyon performansı ve pil tüketimi dikkat ister.
- Anne profili için gereksiz olabilir — hatta dikkat dağıtıcı.
- Yapay zekâ ile üretilen çizimler "AI görseli" gibi durursa ucuzlar; el çizimi hissi şart.

---

## Konsept B — "Sakin"

Minimal ama soğuk değil. Kâğıt, mürekkep, nefes.

### Nasıl görünür
- Arka plan: kirli beyaz / gece için koyu lacivert-gri. Saf beyaz ve saf siyah **yok**.
- Sayaç: çok büyük, ince, tek renk. Ekranın %40'ını kaplar. `1:47:22`
- Tek vurgu rengi (mürekkep mavisi ya da terracotta), sadece aktif tuşta kullanılır.
- Tipografi tek ailede, 3 boy. Yuvarlak köşeler az, gölge yok.
- Geçişler yavaş ve yumuşak (300–400ms), hiçbir şey zıplamaz.
- Çalışırken ekranda **üç şey** var: süre, ne çalıştığın, tek tuş.

### Mikro-detaylar (bu konsepti "güzel" yapan şeyler)
- Sayaç rakamları değişirken sadece değişen hane hafifçe kayar.
- Mola başlayınca tüm ekran yarım saniyede birkaç ton soğur — kelimeye gerek kalmaz.
- Onaylanmamış süre başlayınca sayacın altındaki ince çizgi kesikliye döner. Uyarı yok, çizgi konuşur.
- Seans bitişinde ekran bir an sessizleşir, sonra özet gelir. Konfeti yok.

### Artıları
- Anne de kullanır, sen de kullanırsın. Yaş/rol sinyali sıfır.
- Yapması **hızlı** — MVP'yi bu görünümle bitirebilirsin.
- Yaşlanmaz. 3 yıl sonra da modası geçmez.
- Odaklanma uygulamasının kendisinin dikkat çekmemesi, felsefeyle tutarlı.

### Eksileri
- Ekran görüntüsü paylaşılası değil, organik yayılma sıfır.
- "Neden Forest yerine bunu kullanayım" sorusuna görsel bir cevap vermez.
- Motivasyon katmanı yok — sadece dürüstlük satıyor.

---

## Konsept C — "Ayna" (veri odaklı)

İlk aklına gelen profesyonel yön, ama daha iyi bir çerçeveyle.

### Nasıl görünür
- Ana ekran değil, **ikinci sekme**: haftalık ısı haritası, konu bazında süre çubukları,
  tamamlanma oranı, en verimli saat aralığın.
- Renk paleti kısıtlı ve erişilebilir; grafikler sade, 3B yok, gradyan yok.
- Her grafiğin altında **tek cümlelik insan yorumu**:
  *"Bu hafta geçen haftaya göre 40 dakika az, ama tamamlanma oranın daha yüksek."*

### Artıları
- Ürünün "dürüst kayıt" iddiasının **kanıtı** burada görünür. Doğru veri tutuyorsan,
  onu güzel göstermek en büyük değer.
- `olmadi` verisinin ve sebep etiketlerinin karşılığını burası verir.
- Geri dönüp bakma sebebi yaratır.

### Eksileri
- Tek başına ana konsept olamaz — ilk gün boş grafiklerden ibaret olur.
- Aşırıya kaçarsa insanı "sayı avcısına" çevirir; ürün felsefesiyle çelişebilir
  (bkz. [09-elestiri-ve-riskler.md](09-elestiri-ve-riskler.md), Goodhart yasası).
- Anne profili buraya hiç girmeyebilir. Girmese de sorun olmamalı.

---

## Karşılaştırma

| | A · Tamamlanan Görsel | B · Sakin | C · Ayna |
|---|---|---|---|
| Yapım maliyeti | Yüksek | Düşük | Orta |
| MVP'ye uygun | ❌ | ✅ | ❌ |
| Anne kullanır mı | Belki | ✅ | ❌ |
| Paylaşılabilirlik | ✅ Yüksek | Düşük | Orta |
| Uzun vadede yaşar mı | Orta (bıkılır) | ✅ | ✅ |
| Felsefeyle uyum | Orta | ✅ Tam | Orta |

---

## Öneri: üçü rakip değil, **katman**

```
Taban        →  B (Sakin)      : tüm arayüzün dili. Çalışma ekranı buradan.
Ödül katmanı →  A (Görsel)     : seans BİTİNCE gelir, seans SIRASINDA değil.
İkinci sekme →  C (Ayna)       : isteyen bakar, istemeyen hiç görmez.
```

Kritik karar: **A konsepti çalışma ekranında değil, seans kartında yaşar.**
Yani çalışırken ekranda sadece sakin bir sayaç var (dikkat dağıtmıyor);
seansı bitirdiğinde çizim tamamlanmış olarak sana sunuluyor — sürpriz ve ödül.

Bu, A'nın maliyetini de düşürür: canlı animasyon yerine seans sonunda tek render.

### MVP için görsel karar
Sadece **B**. Çizimsiz, grafiksiz, sade. Önce dürüst çalışan bir sayaç,
sonra güzellik. Tersi yaparsan güzel ama yalan söyleyen bir uygulaman olur —
zaten şikâyetin buydu.
