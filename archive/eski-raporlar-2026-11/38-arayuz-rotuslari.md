# 38. Arayüz rötuşları (7 Eylül 2026)

Telefon boyutunda gerçek bir seans yaşanarak yapılan ikinci gözden geçirmenin çıktısı.
Bir önceki turda düzeltilenler (kontrast, `gorev_bos_alt`, çentik satırı bulanıklığı,
kayıt boş ekranı, 48 piksellik tam ekran düğmesi, mürekkep renkli anahtarlar,
"bulut · bağlan", seans sonunda "{s} yazıldı") burada tekrarlanmıyor.

## Yapılanlar

**1. Çalışırken düğme ağırlığı.**
Molanın doluluğu alınınca ekranın alt üçte biri sahipsiz kalmıştı; `--line` kenarlığın
kâğıtta da koyuda da kontrastı 1,3 olduğu için mola düğmesi görünmüyordu.
Yeni `.btn.soft` sınıfı: `--bg2` dolgu, 1,5 piksel `--muted` kenarlık, `--ink` yazı.
Mola artık düğme gibi okunuyor, bitir yazı olarak kalıyor. Sıralama var, çağrı yok.

**2. Seans sonu perdesi.**
`rgba(26,27,30,.22)` mavi siyah katman sıcak kâğıdı gri yeşile çeviriyordu.
`rgba(58,46,32,.20)` oldu, bulanıklık 6'dan 4'e indi. Washi tonu perdenin altında duruyor.

**3. Sayfa içi seçeneklerde birincil vurgu.**
Yeni `.opt.lead` sınıfı, "hangi işe?" sayfasında `+ yeni iş` düğmesine verildi.
"atla" ile aynı ağırlıkta durmuyor artık.

**4. Kayıt boş ekranı simgesi.**
Genel bir saat çiziliyordu. Yerine bir taban çizgisi üstünde dört çentik kondu;
alt metindeki "çentik veya taş olarak birikir" cümlesiyle aynı dili konuşuyor.

**5. Türkçede yedek düğmeleri.**
`btn_disa` ve `btn_ice` tek başına anlaşılmayan "dışa" ve "içe" idi, "dışa aktar" ve
"içe aktar" oldu. Satır dört satıra sarmasın diye `s_elle_alt` kısaldı: "yedek dosyası".
Yalnızca Türkçe değişti; diğer on dörtte düğme sözcükleri zaten kendi başına ayakta.

## Doğrulama

`node test/hepsi.js` değişiklikten önce ve sonra koşuldu, iki çıktı birebir aynı:
aynı 11 kırmızı dosya, aynı geçti-kaldı sayıları. Yani bu rötuşlar hiçbir şeyi bozmadı.
Kırmızıların bir kısmı ortam kaynaklı (Kotlin dosyaları ve simülatör klasörü o koşuda yoktu),
kalanı `CLAUDE.md`'de sayılan kalıcı kırmızılar.

`node simulasyon/olustur-simulator.js` çalıştırıldı, simülatör yenilendi.

## Açık kalan

- `test-dil.js` "ölü anahtar yok" kontrolü altı anahtar sayıyor:
  `ph_ne_calisiyorsun`, `btn_resmi_gor`, `btn_kopyala`, `btn_kopyalandi`, `btn_secildi`, `sy_yok`.
  Sözlükte tanımlı ama kodda çağrılmıyorlar. Bu rötuşlardan önce de vardılar.
- Seansın ilk dakikalarında saatin altı ile "bugünkü işler" arasında geniş bir boşluk kalıyor.
  Yay büyüdükçe kendiliğinden doluyor, o yüzden şimdilik dokunulmadı.
