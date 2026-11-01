# 09 — Eleştiri ve Riskler

Talep edilen dürüst versiyon. Amaç fikri öldürmek değil, zayıf yerlerini önceden bilmek.

---

## Önce genel yargı

**Problemler gerçek, çözümler mantıklı, ama fikir "büyük" değil.**

- Şikâyetlerin ikisi de doğru ve iyi teşhis edilmiş. Uydurma değil, gerçekten yaşanan şeyler.
- "Onaylanmamış süre" ve "olmadı durumu" gerçekten piyasada boş duran yerler.
- Ama bunlar **kimseyi uygulama değiştirmeye ikna edecek** büyüklükte problemler değil.
  Kimse "sayaç 10 dakika fazla saydı" diye Forest'ı silmez.

Dolayısıyla dürüst çerçeve şu: **bu, ticari bir ürün fikri değil, çok iyi bir kişisel araç fikri.**
Ve bu kötü bir şey değil — kendisi için yazılmış araçlar genelde en iyi araçlardır.
Ama beklentiyi baştan doğru kurmak lazım: hedef "Forest'ı yenmek" değil,
"kendi çalışma kaydımın doğru olması".

---

## R1. Kronometre modu gerçekten iyi bir yöntem mi?

Kendin de sormuşsun, haklı bir soru. Dürüst cevap: **ikisi de farklı işe yarıyor.**

**Kronometrenin zaafı:** sınır yok. Pomodoro'nun asıl faydası süreyi ölçmek değil,
**süreyi sınırlamak.** 25 dakikalık kutu iki şey yapar:
- Başlamayı kolaylaştırır ("sadece 25 dakika" diyerek erteleme kırılır)
- Parkinson yasasını tersine çeker: iş, verilen süreye göre büzülür

Kronometre bunların ikisini de vermez. Ölçer ama yönetmez.
Ayrıca ölçüm hedefe dönüşünce **saat şişirme** riski doğar: masada oturup 4 saat kaydetmek,
2 saat gerçekten çalışmaktan daha iyi görünür. (Goodhart yasası: bir ölçüt hedef olunca
ölçüt olmaktan çıkar.)

**Kronometrenin gücü:** akışı kesmez. Tam anlamışken zil çalmaz. Ve ne kadar sürdüğünü
önceden bilmediğin işlerde (soru çözümü, okuma) geri sayım anlamsız bir tahmin ister.

**Öneri:** ikisini karşıt görmeyi bırak. [03](03-cozum-zamanlayici.md)'teki **Ç6 (yumuşak
dönüm noktası)** tam olarak bunun için: kronometre serbest akar ama 50. dakikada nazikçe
"bak, 50 dakika oldu" der. Sınırın farkındalığı gelir, kesinti gelmez.
Ve v2'de geri sayım modu da eklenir; kullanıcı ne isterse.

> Yani: kronometre modu "yanlış" değil, **eksik**. Eksiği kapatılabilir.

---

## R2. Bu özellikler gerçekten hiçbir yerde yok mu?

Kısmen var. Farklılaşmayı tek özelliğe yıkmamak lazım.

| İddia | Gerçek |
|---|---|
| "Esnek mola hiçbir yerde yok" | ❌ Toggl Track, Clockify gibi zaman takip araçlarında serbest başlat/durdur var |
| "Kaydı düzeltmek yok" | ❌ Toggl'da tam var, hatta en iyi özelliği |
| "'Yapamadım' durumu yok" | 🟡 TickTick'te "Won't Do" var, Habitica'da kaçırılan günler var |
| "Onaylanmamış süre kavramı" | ✅ Bunu bilinçli yapan bir uygulama gerçekten görülmüyor |
| "Neden yapamadın + kapasite içgörüsü" | ✅ Bu birleşim nadir |

Yani gerçek farklılaşma tek tek özelliklerde değil, **birleşimde ve tonda**:
Toggl'ın esnekliği + odak uygulaması estetiği + suçlamayan görev dili.
Bu savunulabilir bir konum ama "kimse yapmamış" demek değil.

---

## R3. İki uygulamayı birleştirmek = kapsam patlaması

En büyük **pratik** risk bu. Bitmeyen kişisel proje mezarlığının 1 numaralı sebebi.

- Zamanlayıcı tek başına ~2 hafta.
- Görev yönetimi tek başına ~2 hafta.
- İkisi arası bağ, gün sonu ritüeli, istatistik: +2 hafta.
- Estetik konsept A (illüstrasyonlar): +haftalar, ve sonu belirsiz.

**Önlem:** [05-ozellik-listesi.md](05-ozellik-listesi.md)'deki MVP sınırına sadık kal.
Görev tarafını MVP'de *en ilkel haliyle* (ekle/sil + 6 durum) yap.
Zamanlayıcı tarafını mükemmelleştir. Güzellik sonra.

Alternatif ve daha güvenli yol: **sadece zamanlayıcıyı bitir, 3 hafta kullan, sonra karar ver.**
Görev tarafına gerçekten ihtiyaç duyuyor musun yoksa fikir hoş geldiği için mi istiyorsun —
bunu ancak kullanınca öğrenirsin.

---

## R4. "Onaylanmamış süre" can sıkabilir

En sevdiğim fikir, ama en riskli fikir de bu.

- 20 dakikada bir titreşim = 3 saatlik seansta 9 kez rahatsız edilmek.
  Odaklanma uygulamasının kullanıcıyı 9 kez dürtmesi ironik.
- Dürtüyü onaylamak için telefona bakmak gerekiyorsa, **telefona bakma alışkanlığını
  besliyor** olabilirsin. Ki tam olarak kaçmak istediğin şey bu.
- Bazı insanlar için "onaylanmamış 20dk" yazısı huzursuzluk yaratır, faydası değmez.

**Önlemler:** varsayılan aralık uzun olsun (30dk+), kapatılabilir olsun, anne profilinde
kapalı gelsin. Ve şu alternatifi de değerlendir: dürtme hiç olmasın, sadece **mola
25 dakikayı geçtiğinde** dönüşte sorulsun (Ç4). Bu, şikâyetinin %90'ını dürtmeden çözer.

> İki hafta Ç4'lü, iki hafta Ç2'li kullan. Hangisi hayatta kalıyorsa o kalsın.

---

## R5. Estetik fikri (Konsept A) bıkkınlık üretebilir

Forest'ın ağacı da güzeldi — ilk 50 seans. Sonra görsel ödül **görünmez** hale gelir,
insan zaten sayaç için açar. Bu doğal ve kötü değil, ama:
- Onlarca illüstrasyon üretme maliyetini görsel ödülün ömrüyle karşılaştır.
- AI ile üretilen çizimler "AI çizimi" gibi durursa değeri **eksiye** düşer.
- Bu yüzden [06](06-estetik-konseptler.md)'da görsel katmanı seans sonuna aldık —
  ucuz, sürprizli, dikkat dağıtmayan.

---

## R6. DND entegrasyonu sistemin zaten yaptığı şey

Android'in kendi Odak modu / Rahatsız Etmeyin zamanlaması var, ve iyi çalışıyor.
Bizim katma değerimiz özellik değil **sürtünme**: tek tuş, ve en önemlisi
**seans bitince otomatik geri açma**. Bunu doğru yapamazsak özellik değersiz;
telefonu sessizde bırakan uygulama silinir.

Bu yüzden [07](07-teknik-plan.md)'de geri alma mantığı iki katmanlı yazıldı.

---

## R7. En büyük risk: sen bırakırsın

Kişisel projelerin gerçek ölüm sebebi teknik değil. Şu sırada olur:
uygulamayı yazarken heves → MVP biter → 1 hafta kullanılır → küçük bir bug çıkar →
Forest'a geri dönülür → proje unutulur.

**Önlemler:**
1. MVP'yi *kullanılabilir* değil, **güvenilir** yap. Sayaç bir kez yanlış sayarsa güven biter.
2. MVP'yi 3 hafta boyunca Forest'ı **silmeden** paralel kullan. Hangisine bastığını izle.
3. Güzelleştirmeyi ödül olarak sona sakla, motivasyon yakıtı olarak kullan.
4. Bu klasördeki notları güncel tut — 2 hafta ara verirsen geri dönüş maliyeti düşer.

---

## R8. Ölçmenin kendisi tuzak olabilir

Felsefi ama önemli: ders çalışma süresini ölçmek, **çalışmanın kalitesini** ölçmüyor.
Dürüst bir sayaç yapmak, dürüst bir öğrenme ölçütü yapmak demek değil.

Bunu ürünün içinde de dengelemek mümkün:
- İstatistik ekranında hiçbir yerde "hedef süre" olmasın. Süre bir **gözlem**, bir hedef değil.
- Görev tamamlanması, süreden daha görünür yerde dursun.
  *"3 saat çalıştın"* değil, *"4 işten 2'si oldu · 3 saat"*.
- Rekor, seri, "geçen haftayı geçtin" gibi ifadeler olmasın.

Bu, [02-urun-vizyonu.md](02-urun-vizyonu.md)'deki ton kurallarının sebebi.

---

## Özet: hangi risklere karşı ne yapıyoruz

| Risk | Önlem | Nerede |
|---|---|---|
| Kronometre yapı vermiyor | Yumuşak dönüm noktası (Ç6), v2'de geri sayım | [03](03-cozum-zamanlayici.md) |
| Özellikler eşsiz değil | Farkı birleşimde ve tonda ara | [02](02-urun-vizyonu.md) |
| Kapsam patlaması | Sert MVP sınırı; gerekirse sadece zamanlayıcı | [05](05-ozellik-listesi.md) |
| Dürtme can sıkar | Uzun varsayılan, kapatılabilir, A/B dene | [03](03-cozum-zamanlayici.md) |
| Görsel ödül bıkkınlık | Seans sonuna al, canlı animasyon yapma | [06](06-estetik-konseptler.md) |
| DND yarım kalır | İki katmanlı geri alma | [07](07-teknik-plan.md) |
| Projeyi bırakma | Güvenilirlik önce, 3 hafta paralel kullanım | [10](10-yol-haritasi.md) |
| Ölçüm tuzağı | Hedef yok, süre gözlem; görev önde | [02](02-urun-vizyonu.md) |
