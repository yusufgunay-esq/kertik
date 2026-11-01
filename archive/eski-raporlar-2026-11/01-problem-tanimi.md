# 01 — Problem Tanımı

## A. Kronometre & mola sorunu (Forest)

### Yaşanan
1. Kronometre modu açılıyor, çalışma başlıyor.
2. Ara verilecek: "mola" tuşuna basılıyor.
3. Forest molayı **5 dakikayla sınırlıyor**. 5 dakika dolunca sayaç kendiliğinden
   çalışma moduna dönüyor.
4. Kullanıcı 15 dakika sonra döndüğünde uygulama **10 dakika fazla çalışma** kaydetmiş oluyor.

### Kök neden
Uygulama, **"kullanıcı ne yapıyor" bilgisine sahip değilken varsayımda bulunuyor.**
Ve bu varsayım hep iyimser yönde: emin değilse "çalışıyordur" diyor.

Doğru davranış, emin olunmayan zamanı *çalışma sayması* değil, **emin olunmadığını
işaretlemesi** olurdu.

### Neden rahatsız ediyor (küçük bir şey gibi görünse de)
Ölçüm aracının değeri güvenilirliğinden gelir. 10 dakikalık hata "aman ne olacak"tır,
ama şişmiş olduğunu **bildiğin** bir sayıya bakmak, sayıya bakma isteğini öldürür.
Bozuk tartıya çıkmak gibi.

### Alt problemler
- **Mola üst sınırı:** neden 5 dakika? Tuvalet + çay + biriyle konuşma = 12 dakika, gayet normal.
- **Dönüş sinyali yok:** kullanıcı geri döndüğünü uygulamaya söylemedi, uygulama da sormadı.
- **Geriye dönük düzeltme yok:** "aslında 14:20'de bırakmıştım" denemiyor. Kayıt taşa yazılmış.
- **Telefon bırakılıp gidiliyor:** odaklanma uygulamasının doğası gereği telefon *uzakta*.
  Yani "dönünce butona bas" çözümü de tek başına yetmez, unutulur.

---

## B. Görev sorunu (Google Tasks)

### Yaşanan
1. Sabah plan yapılıyor: "bugün şu 6 şeyi yapacağım."
2. Gün sonunda 4 tanesi yapılmış, 2 tanesi olmamış.
3. Google Tasks'ta yapılmayan görev için tek seçenek: **sil** ya da **öylece bırak**.
   Tek "durum" var: tamamlandı / tamamlanmadı.
4. Silmek istemiyorsun — o gün o görev vardı, bu bir gerçek. Ama "tamamlandı" da diyemezsin.

### Kök neden
Görev modeli **iki durumlu** (yapıldı / yapılmadı). Gerçek hayat en az **altı durumlu**:
yapıldı, yarına taşıdım, artık gerekmiyor, denedim olmadı, unuttum, hiç başlamadım.

Bu ayrımların silinmesi iki şeyi birden bozar:
- **Duygusal:** bitmemiş görevler listede sürekli birikir, liste bir suçluluk anıtına dönüşür.
- **Bilgisel:** neden yapamadığın hiçbir yerde yazmadığı için, **planlama alışkanlığın hiç düzelmez.**
  Her gün kapasitenin %140'ını planlamaya devam edersin.

### Alt problemler
- "Yapamadım" için bir durum yok.
- Neden yapamadığın sorulmuyor.
- Bir görevin kaç kez ertelendiği görünmüyor.
- Geçmiş bir güne dönüp "o gün ne vardı, ne oldu" diye bakılamıyor.

---

## C. İkisinin birleştiği yer

Bu iki problem tesadüfen aynı kişide toplanmadı. Aynı şeyin iki yüzü:

| | Zamanlayıcı tarafı | Görev tarafı |
|---|---|---|
| Ne kaydediliyor | Ne kadar çalıştım | Ne yapacaktım |
| Yalan nerede | Süre şişiyor | Yapılmayan kayboluyor |
| Eksik olan | Belirsizliği işaretleme | "Olmadı" durumu |
| Sonuç | Veriye güven yok | Plana güven yok |

Ve pratikte zaten iç içeler: **çalıştığın süre bir göreve harcanır.** İki ayrı uygulamada
tutmak, "matematiğe bu hafta kaç saat verdim" sorusunu cevapsız bırakır.

> Birleştirme kararı bu yüzden mantıklı — ama kapsam riski var,
> bkz. [09-elestiri-ve-riskler.md](09-elestiri-ve-riskler.md).

---

## D. Problemin ölçeği hakkında dürüst not

Bunlar **küçük** problemler. Kimse "10 dakika fazla göründü" diye uygulama değiştirmez.
Ürünü büyük yapacak şey problemin büyüklüğü değil, **çözümün tutarlılığı** olacak:
"bu uygulama sana yalan söylemez" tek bir cümle olarak her ekranda hissedilirse,
küçük problemler bir *duruş*a dönüşür.
