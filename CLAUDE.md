# Kertik: Çalışma Sözleşmesi

Bu dosya, Kertik üzerinde çalışan her Claude oturumunun ilk okuduğu metindir.
Eski proje notları (`00-README.md` ve numaralı dosyalar) `archive/eski-raporlar-2026-11/`
altında tarihçe olarak duruyor; güncel karar sayılmaz. Çelişirse burası ve kod geçerlidir.

---

## 1. Uygulama ne yapar

> Ders veya iş çalışırken dürüst süre tutan, gün sonunda "yapamadım" demeye izin veren,
> sakin görünümlü bir Android uygulaması.

Tek büyük fikir: **dürüst kayıt.** Rakipler iyimser senaryoyu kaydeder; Kertik olanı kaydeder.
Molaya geç dönülen dakika sayılmaz, yapılmamış görev "tamamlandı" olmaz,
Google Tasks'a olmamış bir tamamlanma asla yazılmaz.

İkinci fikir: **disiplin, uyarıyla değil estetikle kurulur.** Uygulama kullanıcıyı azarlamaz,
rozet vermez, seri saymaz. Çalışıldıkça bir sanat birikir, mola uzadıkça o birikim aşınır.
Baskı buradan gelir, bildirimden değil.

---

## 2. Değişmez ilkeler

**İ1. Bitmiş görünmek, güçlü olmaktan önce gelir.**
Bir özellik uygulamayı teknik olarak iyileştiriyor ama son kullanıcıya uğraştırıcı geliyorsa
ya da yarım hissettiriyorsa, o özellik eklenmez. Ertelenir veya bırakılır.

**İ2. Son kullanıcı hiçbir şey bilmiyor varsayılır.**
Ekranda teknik jargon yok. Başka servis adı yok: yedekleme Drive'ın gizli klasöründe dursa bile
arayüzde "Google" yazmaz, sadece "Yedekle" yazar. Hata, boş durum ve uç durumlar sessizce halledilir.

**İ3. Bug ölçüsü kullanıcının gördüğüdür.**
"Teknik olarak doğru çalışıyor" veya "kullanıcı isterse ayardan düzeltir" savunma değildir.
Soru şu: bitmiş görünüyor mu.

**İ4. Estetik dil kilitli.**
Kâğıt zemin, mürekkep çizgi, kısıtlı palet, tek bilinçli aksan. Işık efekti yok:
glow, neon, RGB parıltı kullanılmaz. Arayüzde emoji kullanılmaz. Ferah yerleşim,
sıkışık ve ağır kontrastlı düzen değil. Geçişler fiziksel hissettirir, sert kesme yok.

**İ5. Yeni yüzey eskisini bozmaz.**
Arayüz web kalıyor; Compose'a geçilmeyecek. Çalışan ve test edilmiş bir yüzey,
daha temiz bir mimari uğruna baştan yazılmaz.

---

## 3. Bir özellik ne zaman girer

Sırayla üç soru. Biri "hayır" ise özellik girmez, `28-acik-fikirler-ve-hatalar.md` dosyasına düşer.

1. Kullanıcı bunu **öğrenmek zorunda mı?** Öğrenmesi gerekiyorsa yanlış tasarlanmıştır.
2. Yarım kaldığında **görünür mü?** Görünüyorsa ya tam yapılır ya hiç yapılmaz.
3. Dürüst kayıt ilkesini **zedeliyor mu?** Zedeliyorsa tartışılmaz, girmez.

İş seçtiren her yüzeye `+ yeni iş` konur: kullanıcı görevlerini önceden eklemiyor,
seansın içinde adlandırıyor.

---

## 4. Kaynak nerede

| Yol | Durum |
| --- | --- |
| `kertik-android/app/src/main/assets/index.html` | **Tek canlı kaynak.** Uygulamanın tamamı burada |
| `kertik-android/app/src/main/java/com/yusufgunay/kertik/*.kt` | Native kabuk, bildirim, DND |
| `kertik-android/test/` | Güncel testler |
| `simulasyon/simulator.html` | Hızlandırılmış tezgâh, üretilen dosya |
| `uygulama/www/`, `uygulama/imza/`, `uygulama/*.apk` | **Ölü.** 2.2'de donduruldu, tarihçe |
| `kt/*.txt` | **Güvenilir ayna değil.** Kaynaktan farklı ve daha yeni tarihli dosyalar var |

Uyarılar:

- `uygulama/www/index.html` düzenlenmez. Bir oturum bu yüzden yanlış dosyayla çalıştı.
- `kt-yaz.bat`, `kt-oku.bat` ile tazelenmeden asla çalıştırılmaz; kaynağı bozar.
- Sırlar (`gizli.properties`, `local.properties`, imza dosyaları) hiçbir zaman
  kaynak dosyaya gömülmez ve depoya girmez.
- `gradlew.bat` sessizce hiç çıktı vermeden dönerse (exit 0, ekranda hiçbir şey yok,
  Java süreci de başlamamış) ilk şüpheli Avast'tır: `gradle-wrapper.jar` dosyasını
  `IDP.HELU.JarMat16` yanlış pozitifiyle engeller (2026-11-27, 21:34). Jar git'te
  izlenir ve temizdir. O an derleme doğrudan
  `"C:\Users\yusuf_eqta17n\.jdks\jbr-21.0.11\bin\java.exe" -jar gradle/wrapper/gradle-wrapper.jar assembleDebug`
  ile koşulur. Yusuf 2026-11-27'de `C:\Users\yusuf_eqta17n` klasörünü Avast
  istisnasına ekledi; `D:\Projelerim` kapsam dışı, orada aynı sessiz engel olursa
  orası da istisnaya eklenir. Avast'ın çekirdek havuzu ayrıca RAM şişirir
  (bir dalgada worker'ları beş kez öldürdü).

---

## 5. Çalışma düzeni

1. **Önce oku, sonra dokun.** Dosyanın tamamını bağlama yığma; ilgili satırları ara ve o aralığı oku.
2. **Hedefli düzenleme.** Büyük dosyalar sıfırdan yeniden üretilmez; `str_replace`, append, insert kullanılır.
3. **`index.html` değiştiyse test koş:** `node test/hepsi.js`, yazarken `--hizli`.
4. **`index.html` değiştiyse simülatörü yenile:** `node simulasyon/olustur-simulator.js`.
5. **Kanıtla.** Her değişiklik test çıktısı, diff veya ekran görüntüsüyle doğrulanır; iddia yeterli değil.
   Web tarafı testi Claude kendi ortamında Playwright ile koşar; Yusuf'un elle test etmesi son çaredir.
6. **Kararı yaz.** Yeni bir karar veya bulgu, ilgili numaralı dosyaya veya proje hafızasına düşer.
   Bir sonraki oturum onu koddan çıkaramaz.

### Kalıcı kırmızılar, regresyon sanma

- `test-arayuz.js` ve `test-uctan-uca.js`: eski gömülü anahtar mimarisini test ediyorlar.
  Yetki artık native tarafta `Identity.AuthorizationClient` ile alınıyor.
- `test-odak.js` "Tanıtım günde bir kez" dört kontrolü.
- `test-dil.js` iki kontrolü: on üç dilde bazı anahtarlar eksik, bir ölü anahtar var.
- `tema`, `yedek indirme`, `dnd` testleri `MainActivity.kt` okuyor; Kotlin erişimi olmadan koşmaz.

---

## 6. Yazı dili

Kullanıcının gördüğü her metin ve bu klasördeki notlar Türkçe yazılır, TDK yazımıyla.
Uzun çizgi (—) kullanılmaz; virgül ve noktalı virgül yeterlidir.
Klişe benzetmelerden ve yapay zekâ tınısı veren kalıplardan kaçınılır.
Belgeler Markdown'dır; gerektiğinde Mermaid şema kullanılır, PDF üretilmez.

---

## 7. Yapmayacaklarımız

- Compose arayüz.
- Rozet, seri, motivasyon bildirimi, sosyal karşılaştırma.
- Kullanıcıdan izin isteyen, ayar açtıran, açıklama gerektiren akışlar.
- Abonelik. Ödeme modeli peşin, tek seferlik.
- Reklam, izleme, üçüncü taraf analitik.
- Test yeşile dönmediği hâlde "tamam" demek.
