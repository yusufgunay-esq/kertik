# 04 — Görevler Tarafı: "Yapamadım" Çözümü

Problem: [01-problem-tanimi.md](01-problem-tanimi.md) bölüm B.

---

## G1. Görev durum modeli

Google Tasks'ta 2 durum var. Bizde **6**:

| Durum | Anlamı | Renk / his |
|---|---|---|
| `bekliyor` | Planlandı, henüz başlanmadı | Nötr |
| `yapiliyor` | Üstünde çalışılıyor (bir seansa bağlı) | Vurgu rengi |
| `bitti` | Tamamlandı | Yumuşak yeşil |
| `olmadi` | O gün denendi/planlandı, tamamlanmadı | **Gri** — kırmızı değil |
| `tasindi` | Bilinçli olarak başka güne aktarıldı | Soluk mavi |
| `iptal` | Artık gerekmiyor, yapılmayacak | Üstü çizili, soluk |

### Neden kırmızı değil?
Kırmızı = hata = suç. Ama yapamamak bir hata değil, bir olgu.
Gri renk "bu oldu, geçti" der. Kullanıcı listeye bakınca kendini kötü hissetmemeli.
Bu ürün-felsefesi kararı, [02-urun-vizyonu.md](02-urun-vizyonu.md)'deki *nazik muhasebe* ilkesinden geliyor.

### `olmadi` vs `tasindi` farkı
İkisi de "yapılmadı" ama anlamları zıt:
- `tasindi` = **karar**. "Bugün değil, yarın." Yeni bir güne yeni kopya çıkar.
- `olmadi` = **sonuç**. "Niyetim vardı, olmadı." Görev arşive gider, tekrar planlanmaz.

Bir görev ikisini birden yapabilir: önce `olmadi` işaretlenir, sonra istersen yeni bir gün için
yeniden planlarsın. Ama eski kayıt **silinmez** — o gün o görev vardı ve olmadı, bu tarih.

---

## G2. Sebep etiketleri (isteğe bağlı ama önerilen)

`olmadi` işaretlendiğinde tek satırlık, atlanabilir bir soru:

> Ne oldu? *(istersen boş geç)*
> `Zaman yetmedi` · `Enerjim yoktu` · `Başka şey çıktı` · `Unuttum` · `Takıldım/zorlandı` · `Fikrim değişti`

Kural: **asla zorunlu değil.** Boş geçmek tek dokunuş olmalı, yoksa insan `olmadi` demekten kaçınır
ve tekrar Google Tasks durumuna düşeriz.

### Bu veriden ne çıkar
30 gün sonra otomatik bir cümle:

> Son 30 günde tamamlanmayan 22 işin 13'ünde sebep **"zaman yetmedi"**.
> Günde ortalama 6 iş planlıyorsun, ortalama 3,8 tanesi bitiyor.

Bu, uygulamanın kullanıcıya verebileceği en değerli tek bilgi:
**planlama kapasiten gerçekte ne kadar.** Hiçbir görev uygulaması bunu söylemiyor.

---

## G3. Gün sonu ritüeli (kapanış ekranı)

Günün sonunda (ya da ertesi sabah uygulamayı açınca) tek bir ekran:

> **Dün 4 iş kalmış.**
> Her biri için tek dokunuş:
> `Bitti` · `Yarına taşı` · `Olmadı` · `İptal`
> [Hepsini yarına taşı]  [Hepsini olmadı işaretle]

Bu ekran ürünün kalbi. Çünkü:
- Yapılmayan görevlerin listede sonsuza kadar birikmesini **yapısal olarak engeller.**
- Kullanıcıyı günde 20 saniyelik bir muhasebeye alıştırır.
- Tüm `olmadi` verisi buradan gelir.

Zorlayıcı olmamalı: kapatılabilir, ertelenebilir, "bugün sorma" denebilir.

---

## G4. Erteleme sayacı

Bir görev 3. kez taşındığında yanında küçük bir işaret: `↻3`
Ve tek seferlik nazik bir soru:

> Bu iş 3 kez taşındı. Hâlâ yapılacak mı, yoksa listeden kaldıralım mı?
> [Duruyor]  [İptal et]  [Küçük parçalara böl]

"Küçük parçalara böl" özellikle işe yarar — 3 kez ertelenen iş, genelde **çok büyük tanımlanmış** iştir.

---

## G5. Geçmiş günlere bakabilme

> **Uygulandı — 23 Ağustos 2026. Takvim ızgarası olarak değil, kayıt sekmesinde.**
> Ay ızgarası bilinçli olarak yapılmadı: (1) ilk günlerde boş kutular uygulamayı
> bitmemiş gösteriyor — `CLAUDE.md`'deki stabilizasyon kuralına aykırı, (2) jenerik
> verimlilik mobilyası, ebru/kum diline yabancı, (3) görevler sekmesinin gücü tek
> güne odaklanması; üstüne gezinme aracı koymak onu tarayıcıya çevirir.
> Bunun yerine **kayıt sekmesindeki mevcut gün başlıklarının altına** o günün
> görevleri eklendi (`renderLog`). Yeni ekran, yeni sekme, yeni gezinme yok —
> G6'daki tek-ekran görünümü doğrudan çıktı.
> Gün kümesi artık seans günleri ∪ görev günleri: sayaç hiç çalışmamış ama görev
> planlanmış bir gün de kayıtta görünüyor.
> **Geçmiş salt okunur.** Dünkü `olmadı` oradan düzeltilemez; yoksa gün sonu
> muhasebesinin ve "o gün o görev vardı" kaydının anlamı kalmaz.
> Gün başlığı özeti kısa tutuldu (`{n} işten {d} oldu`); `olmadı` sayısı satırdaki
> `–` işaretinden zaten okunuyor. Yeni dil anahtarı gerekmedi.

Takvim görünümü. Herhangi bir güne dokunduğunda:
- O gün planlanmış işler ve son durumları
- O gün tutulan seanslar ve süreler
- Toplam: `3s 10dk · 4 işten 2'si`

Google Tasks'ta olmayan şey tam olarak bu: **geçmişin kaydı.**
"O gün o görev vardı ve yapamadım" cümlesinin karşılığı bu ekran.

---

## G6. Zaman ↔ görev birleşimi (iki uygulamanın kesiştiği yer)

Bu proje neden iki uygulamanın birleşimi olmalı, tek ekranda görünür:

```
Bugün · 12 Ağustos
──────────────────────────────
◍ Matematik — türev tekrarı        1s 40dk   [bitti]
◍ İngilizce kelime                    25dk   [olmadı · zaman yetmedi]
◍ Fizik soru çözümü                   —      [taşındı → yarın]
◍ Kitap 30 sayfa                      50dk   [bitti]
──────────────────────────────
Toplam 2s 55dk · onaylanmamış 15dk
```

Tek ekranda hem **ne kadar** hem **ne** hem **oldu mu** görünüyor.
Ne Forest bunu verebiliyor ne Google Tasks.

### Otomatik çapraz içgörüler
- "Fizik'e 0 dakika verdin ve 3 gündür taşınıyor."
- "İngilizce'ye 25dk verdin, tamamlanmadı — sence ne kadar daha gerekirdi?"
- "En verimli olduğun saat aralığı: 21:00–23:00."

---

## G7. Kasten yapmadığımız şeyler

Kapsamı korumak için açıkça **dışarıda** bırakılanlar:

- Alt görevler / iç içe klasörler (Todoist'in işi)
- Tekrarlayan görevler — *v2'de olabilir, MVP'de yok*
- Etiket sistemi (konu/ders yeterli)
- Paylaşım, işbirliği, atama
- Doğal dil ile tarih girişi ("yarın 5'te")
- Puan, rozet, seri, seviye — bilinçli olarak yok
  ([02-urun-vizyonu.md](02-urun-vizyonu.md) sessiz arayüz ilkesi)
