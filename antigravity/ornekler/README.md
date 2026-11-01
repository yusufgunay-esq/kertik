# Kertik - Antigravity Prototip ve Örnekler

Bu klasör, ana uygulamayı (`uygulama/www/index.html`) etkilemeden yeni özellikleri, animasyonları ve UX geliştirmelerini izole olarak test etmek için oluşturulmuştur.

## 1. Akışkan Geçiş (Morphing) Demosu
- **Dosya:** [`akiskangecis_demo.html`](akiskangecis_demo.html)
- **Özellik:** Kronometre ve Pomodoro modları arasındaki sert kesilmeyi kaldırıp yerine Apple tarzı kendi içine eriyen akışkan morfoloji geçişi getirir.
- **İçerik:**
  - SVG kadran çentiklerinin yumuşakça sönüp merkezden doğması (*in-place dissolve & spring scale*).
  - Pomodoro süre haplarının (`25dk`, `50dk`, `90dk`) kadranın altından yaylanarak açılıp kapanması (*accordion spring*).
  - Sayaç ve alt yazıların nefes alarak değişmesi (*subtle micro-fade*).
  - Üst tarafta bulunan **"Karşılaştır"** butonuyla hem eski sert geçişi hem de yeni akışkan geçişi anında kıyaslayabilme.

## 2. Arka Plan Canlanma & Boş Durum (Idle Teaser) Demosu
- **Dosya:** [`arkaplan_canlanma_demo.html`](arkaplan_canlanma_demo.html)
- **Özellik:** Kullanıcı uygulamayı ilk açtığında arkada çalışan üretken çizim (generative stream) sanatını hissettiren 'Görsel Sezdirme' (Visual Affordance) laboratuvarı.
- **İçerik:**
  - **4 Farklı Boş Durum Modeli:**
    1. *🌱 Model A (Uyuyan Tohum):* Uykuda bekleyen düşük opaklıklı mikroskobik Perlin akış çizgileri.
    2. *✨ Model B (Nefes Alan Hale):* 4.8s solunum ritminde ipeksi radyal kromatik aura.
    3. *🌊 Model C (Kılcal Rezonans):* Kadran çentiklerinden yayılan harmonik su halkaları.
    4. *⚪ Model D (Statik/Klasik):* Mevcut boş Kertik başlangıcı (kıyaslama için).
  - **Kesintisiz Seans Geçişi:** 'Başlat' butonuna basıldığında idle durumdaki tohumun gerçek seans çizimine erimesi (*seamless morph*).
  - **Akıllı Pil Tasarrufu (Eco-Sleep):** 10 saniye hareketsizlik sonrası animasyonu dondurarak pil tüketimini %0'a indirme simülasyonu.
  - **Canlı Telemetri:** 60 FPS kare hızı ve render maliyeti (<0.5 ms) monitörü.

## 3. Generatif Sanat ve Çizim Laboratuvarı (Pomodoro vs. Kronometre)
- **Dosya:** [sanat_laboratuvari.html](sanat_laboratuvari.html)
- **Özellik:** Pomodoro (hedefe kilitli/teleolojik) ve Kronometre (ucu açık/morfogenetik) çizim ontolojilerini canlı kıyaslayan, yüksek çözünürlüklü Retina tuval motoruna ve 4 doğal mineral pigment paletine sahip interaktif sanat laboratuvarı.
- **İçerik:**
  - **🍅 Pomodoro Motoru (Teleolojik / Hedefe Orantılı):**
    - Çizim ilerlemesi seçilen hedefe ($T \in \{25, 50, 90\}$ dk) göre normalize edilir.
    - %0-25 İskelet, %25-70 Gövde/Akış, %70-99 Kılcal/Gölge, %100 Mühürlü Tamamlanma.
    - Süre aşıldığında (+fazla çalışma) tuvalin dışına taşan altın/terracotta radyal **Aura** ışıltısı.
  - **⏱️ Kronometre Motoru (Morfogenetik / Organik Büyüme):**
    - Sabit tavanı yoktur; her dakikada tek başına dengeli bir form korur.
    - 0-20 dk Çekirdek Form, 20-50 dk 1. Yaş Halkası, 50-90 dk 2. Halka & Fraktal Çatallanma, 90+ dk Derin Orman / Kozmos.
  - **☕ Mola Entegrasyonu:** Mola dakikaları çizimi kesintiye uğratmaz; adaçayı/arduvaz tonunda dingin bir mürekkep yıkaması izi bırakır.
  - **🎨 4 Harmonik Palet:** Kâğıt & Pişmiş Toprak, Yanık Hardal & Orman, Bakır & Gece Mavisi, Koyu Gül & Arduvaz.
  - **🎛️ Canlı Kumanda:** 0-180 dk Scrubber, 1x-300x simülasyon hızları, mola tetikleyici ve tohum randomizer.
