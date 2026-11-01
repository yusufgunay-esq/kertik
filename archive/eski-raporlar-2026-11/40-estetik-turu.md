# 40. Estetik turu (27 Eylül 2026)

Telefon boyutunda (412 × 915, Roboto ile) her ekran açık ve koyu temada çekilip
tek tek incelendi. Değişiklikler yalnız `index.html` içinde; çizim, akış, kum
havuzu ve metinler olduğu gibi duruyor.

## Yapılanlar

**1. Başlık yazısı.**
Sayfa başlıkları, sayfa içi başlıklar (`.sheetbox h3`), gün başlıkları ve boş
ekran cümlesi artık Newsreader ile yazılıyor (`--serif`). Gövde, rakamlar ve
saat eski yazıda kaldı. Yazı dosyanın içine gömülü: yalnız 360–560 ağırlık,
yalnız Latin alfabeleri, yaklaşık 80 KB. Kiril, Arapça ve Doğu Asya dillerinde
başlık kendiliğinden gövde yazısına düşer. Lisans SIL OFL.

**2. Mod anahtarı.**
Topuz siyahtan kâğıt beyazına döndü; ayarlardaki üçlü seçiciyle aynı malzeme.
Sayaç ekranında tek siyah kütle `başlat` kaldı.

**3. Sayfa içi seçenekler.**
Her seçenek ayrı kutuydu; dil listesinde on altı kutu alt alta diziliyordu.
Artık `.opt` satırları tek bir grup oluyor: ortak zemin, soldan içeride başlayan
ince ayraç, yalnız grubun ilk ve son köşesi yuvarlak. `.optgap` yeni grup açar.
Künye kartı ve ayar grupları zaten bu dili konuşuyordu. Sınıf adları değişmedi,
şablonlara dokunulmadı.

**4. Kayıt duvarı.**
Yuvarlak köşeli yarı saydam kart kaldırıldı (`24`, yasak listesinin son satırı).
Duvar doğrudan kâğıdın üstünde; iki duvar varsa aralarında tek ince çizgi.
Büyük harfli kalın etiket, ayarlardaki bölüm başlıklarıyla aynı küçük harfe indi.

**5. Koyu temada anahtar.**
Açık anahtarın topuzu fildişi zemin üstünde fildişiydi, görünmüyordu.
Topuz artık `--onFill`.

**6. Yanıp sönen nokta.**
Kadrandaki uç noktası sonsuz döngüyle yanıp sönüyordu; seijaku kuralı döngüyü
yasaklıyor. Nokta duruyor.

**7. İki düğmeli ayar satırı.**
"elle" satırında etiket iki satıra sıkışıyordu. İki düğmeli satırda düğmeler
artık etiketin altına iniyor.

**8. Kayıt satırlarındaki açma işareti** yarı saydamlığa çekildi; her satırda
tekrar eden işaret gürültü yapıyordu.

## İkinci tur: sayaç ekranının iki modu

Her iki mod seansın farklı anlarında (5, 25, 75, 140 dk; pomodoroda 3, 35, 49,
fazladan 8 dk) ve sekiz ayrı günün kum bahçesiyle çekilip incelendi.

**9. Kadranın içi boş kâğıt.**
Ebru ve tırmık çizgileri saatin rakamlarının üstünden geçiyordu. `#akis`
tuvaline yumuşak bir dairesel maske kondu (`akisBosluk()`): mürekkep kadrana
yaklaştıkça incelip çekiliyor, halkanın dışında tam. Yalnız ekranda; seansın
resmine işlenmiyor.

**10. Yazılara harita etiketi gibi hale.**
"başladın" satırı, "bitir", iş seçici, durum yazısı ve not satırı yoğun ebrunun
içinde okunmuyordu. `--hale`: yazının çevresinde çizgiler kâğıda çekiliyor.
Durum yazısının arkasındaki köşeli kâğıt kutusu ve not satırının kutusu kalktı,
aynı hale geldi.

**11. Taşlar arayüzün üstüne oturmuyor.**
Sekiz günün altısında bir taş ya "hazır" yazısının, ya tam ekran düğmesinin,
ya da "bugün … seans" satırının üstüne düşüyordu. `kumArayuz()` canlı bahçede
kadranı, mod anahtarını, durum yazısını, tam ekran düğmesini ve kadranın
altındaki yazı sütununu ölçüp taşı bunların dışına yerleştiriyor. Taşın yeri
artık üst bant ya da kontrollerin altındaki kum. Ölçüm günün ilk ölçümü olarak
saklanır; gün içinde yeni taş gelince eskiler kıpırdamaz. Yatay ekranda yazı
sütunu kadranın yanında sayılıyor. Resim ve duvar çizimi eski yerleşimi kullanır.
Taşın iriliği ekranın kısa kenarından: yatay ekranda taşlar kaya kadar büyüyordu.

**12. Çentik el ile kesiliyor.**
Kadranın çentikleri tek tip vektördü. Artık her dakikanın boyu, açısı,
kalınlığı ve mürekkebi biraz farklı (`elCentik`, seansın kimliğinden tohumlu,
her çizimde aynı). Pomodoroda yalnız kazınan çentik elden geçer; bekleyenler
düzende durur.

**13. Kronometrede saat halkaları solar.**
İki saati geçince halkalar üst üste binip kalabalıklaşıyordu. Geçmiş saatlerin
çentiği kısalıyor ve soluyor (sabi); en koyu olan şu anki saat.
İçinde bulunulan saatin halkası seans boyunca hafifçe duruyor; başlatınca
kadranın biçimi kaybolmuyor.

**14. Pomodoro dolunca `bitir` öne çıkar.**
Süre içinde sessiz yazı olarak kalıyor; hedef dolunca siyah birincil düğme oluyor.

## Üçüncü tur: kum bahçesi

Konu yerinde bırakıldı: pomodoro başına bir taş, taşın iriliği hedef süreden,
tırmık bir seans boyunca bahçeyi bir kez tarar, uzayan mola rüzgârla aşındırır,
kırık taş altınla onarılır. Kayıt, widget ve seans resmi bu dile bağlı; sorun
fikirde değil, malzemedeydi ve iki hatadaydı.

**15. Yeni pomodoro başlayınca çizgilerin silinmesi (hata).**
`kumCizgiler` yalnız şu anki geçişi çiziyordu; seans başında çizgi sayısı sıfır
olduğu için `adet <= 0` satırı hayalet dokuyu da atlıyor, bahçe bomboş
kalıyordu. Kodun üstündeki "ikinci pomodoro bahçeyi sıfırlamaz" notuyla kod
da birbirini tutmuyordu.
Yeni kural: **yeniden tırmıklama.** Bahçe her pomodoroda baştan taranır, ama
önceki geçiş yeni tırmık üstünden geçene kadar yerinde durur (`eski: true`,
biraz daha soluk). Uzun moladan sonra rüzgârın aşındırdığı eski iz görünür
kalır ve yeni seans onu temizleyerek ilerler. Eski birikim fikri (her geçişte
sıklaşma) bırakıldı; günün kaçıncı pomodorosu olduğunu taşlar zaten söylüyor,
beşinci geçişten sonra çizgiler kalabalıklaşıyordu.
`test-cizim.js` bu sözleşmeye göre güncellendi ve hatanın kendisi için bir
kontrol eklendi.

**16. Tırmık dişleri.**
Her iz tek bir çizgiydi; bahçe kum gibi değil, cetvelli kâğıt ya da eş yükselti
haritası gibi okunuyordu. Artık her iz dört koşut oluk (`KUMMOD.dis`, `disAra`).
Alan uzaklık gibi davrandığı için c ± δ eğrileri kendiliğinden koşut; taşın
çevresindeki halkalar da dişli çıkıyor. Bantlar arası geniş boşluk (ma) aynen
duruyor. İlk çizim bir kez 5 kat pahalı, sonrası önbellekten.

**17. Taş yerleşimi.** Canlı bahçede aday sayısı 44'ten 160'a çıktı (boş kum
daha dar), kenar payı taşın çizilen genişliğine göre büyüdü; taşlar ekran
kenarında kesilmiyor. Not satırının altı da taşa kapalı.

Taşların biçimi ve rengi değişmedi: yakından bakınca en özenli parça onlar.

## Doğrulama

`node test/hepsi.js` değişiklikten önce ve sonra koşuldu; aynı 9 kırmızı dosya,
aynı tek tek kontroller. Kırmızıların beşi Kotlin dosyalarına erişim olmadığı
için koşmadı, kalanı `CLAUDE.md`'deki kalıcı kırmızılar ve `native köprü`
testindeki saat damgası kontrolü (bu turdan önce de kırmızıydı).
Simülatör yenilendi.

## Açık kalan

- Kum havuzunda taş, pomodoronun ilk dakikalarında sol üst köşeye, durum
  yazısının hizasına düşebiliyor. Çizim algoritmasına ait; bu turda dokunulmadı.
- `native köprü` testinde "dosya adı seansın tarihini taşıyor" kontrolü bu
  turdan önce de kırmızıydı; ayrıca bakılmalı.
