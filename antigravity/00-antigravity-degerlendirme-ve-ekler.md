# Antigravity Değerlendirmesi ve Ek Notlar

Bu klasör, Antigravity (Google DeepMind AI asistanı) tarafından kullanıcının ham istemi ve Claude'un oluşturduğu 14 proje notu incelendikten sonra eklenen bağımsız analiz, mimari ekler ve tasarım yorumlarını içerir.

---

## 1. Ham Prompttan Çıkan Derin İçgörüler ve Ekler

### A. Instagram İllüstrasyon Fikri (Konsept A) ve Kronometre Çelişkisi
- **Kullanıcının Gözlemi:** Instagram'da bir Pomodoro uygulamasında süre aktıkça bir resim çizildiğini gördü ve estetiğini çok tatlı buldu.
- **Teknik ve Estetik Risk:** Pomodoro'da süre (ör. 25dk) belli olduğu için çizim çizgileri sürece eşit bölünebilir. Fakat **kronometre modunda bitiş zamanı belli değildir.**
- **Antigravity Ek Notu:** Kronometre modunda canlı çizim yapmaya çalışmak ya çizimin erken bitip donmasına ya da çok yavaş ilerleyip görsel zevkin kaybolmasına yol açar. Claude'un `06-estetik-konseptler.md` belgesindeki önerisini derinleştiriyoruz:
  - **Dönüm Noktalı Katmanlar (25dk / 50dk / 75dk):** Çizim ekranda canlı çizilmez; seans sürdükçe her dönüm noktasında çizime yeni bir katman (arkaplan, detay, renklendirme) eklenir.
  - **Seans Sonu Ödül Kartı:** Asıl illüstrasyon tamamlama sürprizi **seans bittiğinde** bir kart olarak sunulur. Böylece hem çalışma anında dikkat dağıtmaz hem de kronometrenin belirsiz süresine tam uyum sağlar.

---

### B. Rahatsız Etmeyin (DND) Entegrasyonu: Özellik Değil, "Sürtünmesizlik"
- **Kullanıcının Gözlemi:** "Telefonu rahatsız etme modlarından birine almak da aynı şey ama bunu uygulama daha kolay yaparsa insanlar tercih eder."
- **Antigravity Ek Notu:** Kullanıcının bahsettiği şey bir özellik değil, **psikolojik sürtünmenin (friction) sıfırlanmasıdır**. 
  - İnsanlar DND modunu elle açmayı üşenir veya unutur.
  - En tehlikelisi: Seans bitince DND modunu elle kapatmayı unutup önemli aramaları kaçırırlar (bu durum uygulamayı sildiren ana nedendir).
  - **Mimari Zorunluluk:** DND modu başlatılınca açılmalı, seans bittiğinde, mola verildiğinde veya **uygulama çökse/kapatılsa dahi** otomatik olarak eski haline döndürülmelidir (bkz. `07-teknik-plan.md` iki katmanlı geri alma).

---

### C. Anne Profilinin (The Mom Test) Mühendislik Değeri
- **Kullanıcının Gözlemi:** "Annem de kullanır bence... Çok öğrencilere hitap etmesine gerek yok."
- **Antigravity Ek Notu:** "Annem de kullanabilsin" ifadesi yazılım mimarisinde bir **kısıtlama değil, en büyük tasarım hediyesidir**.
  - Uygulamaya "Pomodoro", "Streak", "Session", "XP" gibi teknik ve oyunlaştırılmış terimler koymamızı engeller.
  - Ana ekranda tek bir dev **"BAŞLAT"** butonu olmasını zorunlu kılar.
  - Ürünün yaşlanmasını önler ve sade tutar.

---

### D. Google Tasks "Yapamadım" İhtiyacı ve Kapasite İçgörüsü
- **Kullanıcının Gözlemi:** "Google Tasks'ta iptal oldu, yapamadım seçeneği yok, sadece yaptım var. Görevi silmek istemiyorum, o gün o görev vardı ve yapamadım kısmı olsun istiyorum."
- **Antigravity Ek Notu:** Kırmızı renk başarısızlık ve suçluluk hissettirir. `olmadi` durumunun **Nötr Gri** renkle sunulması kullanıcının dürüst kaygı tutmasını sağlar.
  - 30 gün sonunda üretilecek tek cümlelik içgörü: *"Günde ortalama 6 görev planlıyorsun ama ortalama 3.8 görev tamamlanıyor."* Bu veri, kullanıcının hayatında ilk kez kendi gerçek kapasitesini görmesini sağlayacaktır.

---

## 2. Antigravity Mimari Tavsiyesi ve Mühendislik Sözü

1. **Notlarda Kalma Riskine Karşı (Anti-Overthinking):** Claude 14 adet şahane not hazırlamış. Notlar yeterince olgun. Bundan sonra yeni doküman eklemek yerine koda geçmek şarttır.
2. **Kodlama Sırası (Aşama 1):**
   - Önce Room Veritabanı Entity ve Dao katmanı (`SessionEntity`, `BreakEntity`, `TaskEntity`).
   - Sonra Olay Tabanlı Süre Motoru (`SessionEngine`).
   - Son olarak JUnit5/Kotest ile %100 kapsama sağlayan Birim Testleri.

---
*Not: Bu dosya Antigravity tarafından oluşturulmuştur ve Claude'un notlarından bağımsız olarak `antigravity/` klasöründe saklanmaktadır.*
