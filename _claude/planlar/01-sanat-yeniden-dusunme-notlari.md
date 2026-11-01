# Kertik: sanatı yeniden düşünme notları (fikir bulacak ajanlar için)

Tarih: 1 Kasım 2026. Bu dosya bir fikir avı brifidir. Okuyan ajan: aşağıdaki bağlamı oku,
sonra en alttaki görevi yap. Hazır cevap arama; sıfırdan düşün.

## 1. Uygulama nedir

Kertik, Android için bir odak uygulaması. İki mod var:
- **Kronometre:** ucu açık. Başlatırsın, istediğin kadar çalışırsın, bitirirsin.
- **Pomodoro:** sınırlı döngüler. Hedef süre (ör. 25 dk) + mola, tekrar.

Tek büyük fikir: **dürüst kayıt.** Uygulama azarlamaz, rozet vermez, seri saymaz.
Çalışıldıkça ekranda bir sanat birikir; seans bitince o sanat kayıt olarak saklanır
(geçmiş ekranı, günlük "duvar", ana ekran widget'ı bu görselleri kullanır).

## 2. Sorun

Şu anki sanat (kronometrede akış alanı çizgileri / "ebru", pomodoroda kum bahçesi + taşlar)
sahibine **basit** geliyor. Referans aldığı his: LingDong'un {Shan, Shui}* projesi (2018),
yapay zekâ olmadan, yalnız matematikle canlı bir mürekkep manzarası üretiyor.
Kertik bu seviyede "vay" dedirtmiyor.

## 3. Reddedilen fikirler ve NEDEN reddedildikleri (bunları tekrar önerme)

Ortak hata: **kostüm giydirilmiş ilerleme çubuğu.** Süre arttıkça bir şey büyüyor/çoğalıyor/ilerliyor.
- Ağaç büyür (Forest'ın yaptığı)
- Havuzda balık sayısı artar
- Yelkenli ilerler
- Mürekkep resmi vuruş vuruş büyür, tomar uzar
- Gece göğünde her dakika bir yıldız yanar
- Akış alanı / flow field çizgileri: üretken sanatın en çok görülen görüntüsü, "bunu gördüm" hissi

## 4. Asıl test (her fikir bundan geçmeli)

1. **Ne kadar değil, NASIL çalıştığını göstermeli.** Kesintisiz çalışma, duraklatmalar,
   uzayan mola, iş değiştirme, günün saati görsele farklı biçimde yansımalı.
   Aynı süre, farklı çalışma biçimi = farklı resim.
2. **Saklanacak bir eser bırakmalı.** Seans sonu görseli tek, tekrarlanamaz, ekran görüntüsü
   alınıp paylaşılacak kadar güzel.
3. **Canlı ama sakin hareket.** Ekrana bakınca yaşadığını hissettirmeli; göz yormamalı,
   dikkat dağıtmamalı (kullanıcı çalışıyor).
4. **Üç saniye testi:** projeyi bilmeyen biri ekranı 3 saniye görünce "grafik / istatistik /
   uygulama arayüzü" dememeli. "Bu ne, çok güzel" demeli.
5. **Daha önce görülmemiş olmalı.** Odak uygulamalarında (Forest, Flora, Session, Focus Plant vb.)
   olan bir metafor ise ya çok daha derin bir yorumu olmalı ya da elenmeli.
6. İki mod **aynı dünyanın parçası** gibi hissettirmeli ama her biri kendi doğasına uymalı
   (kronometre ucu açık, pomodoro döngüsel).

## 5. Elimizdeki sinyaller (sanat bunları kullanabilir)

Seans başlangıcı, her dakika, duraklatma ve devam anları, toplam kesintisiz süre,
pomodoro hedef süresi ve kaçıncı pomodoro olduğu, mola başlangıcı ve molanın hedefi aşması,
seans içinde iş (görev) değişimi, günün saati, o günün önceki seansları, geçmiş günler.
Kullanıcının dokunmasıyla etkileşim mümkün ama şart değil.

## 6. Şu anki önde giden aday (eleştir, daha iyisini bul)

**Gece sahnesi: üstte gökyüzü, altta durgun havuz.**
- Kronometre = uzun pozlama: yıldızlar iz bırakıyor; Dünya saatte 15° döndüğü için yayın boyu
  gerçek süre. Duraklatma = deklanşör kapalı, izde boşluk.
- Pomodoro = durgun su: kesintisiz çalıştıkça su duruluyor, balıklar sakinleşiyor, en sonunda
  ay yansıması beliriyor (Zen: ay yalnızca durgun suda görünür). Duraklatma = yaprak düşer,
  halkalar yansımayı dağıtır. Mola = rüzgâr yüzeyi kırıştırır.
- Havuz gökyüzünü yansıtır; iki mod tek dünya.

Bilinen zayıflıkları: uygulamanın açık (kâğıt renkli) teması var, gece sahnesi ona nasıl uyacak?
Yıldız izi fotoğrafçılıkta çok görülmüş bir görüntü. Koi havuzu klişeye kayabilir.

## 7. Teknik çerçeve (fikri öldürmesin ama gerçekçi olsun)

- Uygulama Android'de WebView içinde çalışan tek bir HTML sayfası + Kotlin kabuk.
  Sanat WebGL2 shader'ları veya Canvas ile çizilecek. (Unity de mümkün ama ağır; gerekirse gerekçelendir.)
- Telefon pili: sürekli animasyon düşük kare hızında (ör. 24-30 fps) ya da GPU shader ile ucuz olmalı;
  ekran kapalıyken çizim durur.
- Aynı seans verisinden **her seferinde aynı resim** çıkmalı (tohumlu/deterministik),
  çünkü kayıt ve widget seans bittikten sonra resmi yeniden çizer.
- Widget için tek kare durağan hâli de güzel olmalı.

## 8. Esin için başka alanların araçları

Geleneksel yol "doğa metaforu + süre = büyüme". Bunun dışına çık. Başka bir alanın
matematiği veya fiziği daha iyi oturabilir. Bakılabilecek yönler (hepsi örnek, sınır değil):
astronomi ve gök mekaniği, akışkanlar ve dalga fiziği, kristal büyümesi, reaksiyon-difüzyon,
el sanatları (seramik sırrı, dokuma, cam, lake, kintsugi), ışık ve gölge, hava ve iklim,
kartografya, müzik ve akustik (Chladni desenleri), biyoloji (sürü davranışı, mantar ağları),
fotoğraf teknikleri (uzun pozlama, siyanotip), mimari (gün ışığının bir odada dolaşması).

## 9. Görev

1. Birbirinden **gerçekten farklı eksenlerde** en az 10 radikal fikir üret. Önce cesur ol, sonra ele.
2. En iyi 3 fikri seç. Her biri için yaz:
   - Tek cümlelik özü
   - Kronometre modunda ne oluyor, pomodoro modunda ne oluyor
   - Hangi sinyal görselde neye karşılık geliyor (özellikle duraklatma, mola aşımı, kesintisiz süre)
   - Hareket: ekranda canlı olarak ne kıpırdıyor
   - Seans sonunda kalan eser neye benziyor
   - Neden daha önce görülmemiş / neden klişe değil
   - Teknik olarak nasıl yapılır (shader mı, parçacık mı, simülasyon mu) ve pil maliyeti
   - En büyük riski
3. 6. bölümdeki gece sahnesini dürüstçe eleştir: seçtiğin 3 fikir ondan iyi mi, neden?
4. Kısa yaz. Süsleme yok, gerekçe var.
