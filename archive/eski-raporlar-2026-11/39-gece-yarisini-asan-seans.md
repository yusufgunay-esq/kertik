# 39 — Gece Yarısını Aşan Seans ve Bitirmesi Unutulan Kayıt

Tarih: 8 Eylül 2026
Durum: uygulandı, testli.

---

## Bulgu

Telefonda bir seans akşam 20.26'da başlatılıp bitirilmesi unutulmuş, ertesi gün
17.46'da kapatılmış. Kayıt sekmesinde satır "20.26 – 17.46 · 21s 20dk" olarak
göründü. Kayıt teknik olarak doğruydu, ama üç yerde bitmemiş görünüyordu:

1. **Satır yazım hatası gibi okunuyordu.** Bitiş saati başlangıçtan küçük
   görünüyor, gün değiştiği hiçbir yerde yazmıyordu.
2. **Düzeltme çalışmıyordu.** Kart açılınca çıkan başlangıç ve bitiş saat
   kutuları `timeToTs` ile girilen saati o alanın kendi gününe oturtuyordu.
   Bitiş bir sonraki güne ait olduğu için ne yazılırsa yazılsın seans gece
   yarısını aşmaya devam ediyor, hatta 21.06 yazınca süre 24 saate çıkıyordu.
   Kullanıcının elinde tek çare kaydı silmekti; dürüst kayıt ilkesine göre
   yaşanmış 40 dakika da siliniyordu.
3. **"Ne kadar uzaktaydın" kutusunun tavanı 600 dakikaydı.** On saatten uzun
   unutulmuş bir seans bu yolla da işaretlenemiyordu.

## Karar

**Girilen saat, seansın kendi penceresine göre okunur.**

- Bitiş: başlangıçtan **sonraki ilk** o saat.
- Başlangıç: bitişten **önceki son** o saat.

Kural, kullanıcının kafasındaki cümlenin aynısı: "dün gece 21.06'da bitirmiştim".
Ekrana gün seçtiren bir alan eklenmiyor; öğrenilecek yeni bir şey yok (İ2).
Aynı gün içinde kalan seanslarda davranış birebir eskisi gibi.

Yanlış yazılan saat seansı sessizce şişirmesin diye iki sınır kondu:

- Elle kurulan seans, ne şu ankinden ne de on iki saatten uzun olabilir.
- Mola damgaları yeni uçların dışında kalamaz.

Kabul edilmeyen değer kutuda kalmaz; ekran kaydın kendi saatine döner.

Gün aşımı artık satırda küçük bir `+1` ile görünüyor. Rakam olduğu için on üç
dilin hiçbirine yeni metin eklemedi.

## Kod

`kertik-android/app/src/main/assets/index.html`

- `saatiGunaOturt(v, dayanak, sonra)`: girilen saati doğru güne oturtur. Gün
  eklemek yerine tarihi ilerletir, böylece yaz saati uygulanan ülkelerde bir
  saatlik kayma olmaz.
- `seansSaatiDuzenle(s, alan, deger)`: düzenlemenin tek kuralı; arayüzden ayrı
  durduğu için sınanabiliyor. `KAYIT-DUZENLEME:BEGIN/END` işaretleri arasında.
- `aralik(a, b)`: gün farkı varsa `+n` basar (`.gunartisi`).
- `askAway` içindeki dakika kutusunun tavanı seansın kendi uzunluğuna göre
  hesaplanıyor, sabit 600 değil.

## Test

`kertik-android/test/test-kayit-duzenleme.js`, `hepsi.js` listesine eklendi.
Tarayıcı gerektirmez. 17 kontrol: saatin güne oturması, gece yarısını aşan
seansın düzeltilmesi, şişirme ve mola sınırları, süren seansın düzenlenmemesi,
`+1` işaretinin basılması.

Doğrulama: `node hepsi.js --hizli` ile birlikte duman, dil ve native köprü
testleri koşuldu. Kırmızılar değişmedi (bilinen kalıcı kırmızılar ile Kotlin
dosyası okuyan testler). Playwright ile uçtan uca da denendi: 21s 20dk'lık
kayıt, bitişe 21.06 yazılınca 40 dakikaya indi, gün başlığı doğru güne taşındı,
konsol temiz kaldı.

## Açık kalan

Seansın bitirilmesi unutulduğunda uygulamanın kendiliğinden uyarması
(bildirim ya da açılışta sorma) bu dosyanın dışında bırakıldı: bildirimle
disiplin kurmama ilkesiyle ve izin isteyen akış istememekle çakışıyor.
Düzeltme yolu açık olduğu için şimdilik gerek görülmedi.
