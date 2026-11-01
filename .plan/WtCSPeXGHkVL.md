# Kertik deneme çapası: ağsız, üç kaynak, en eski kazanır

## Karar (özet)

**Sunucu yok. Kotlin'e dokunulmaz. Deneme çapası yalnız web tarafında üç yerel
kaynaktan türetilir ve bunların en eskisi kazanır.**

Gizli anahtar, KV, ECDSA imzası, IP tavanı, günlük kota, yeni izin, gizlilik
beyanı değişikliği: hiçbiri yok. Toplam değişiklik tek dosyada (`index.html`).

---

## Neden bu kadar basit olabilir

Leucine'deki Worker + KV + ECDSA yığınının tek işi vardı: kurulum başına
harcamayı öngörülebilir bir tavana oturtmak (`GRACE_TOTAL × birim maliyet`).
İmza, IP hız sınırı, günlük tavan, `grace_limit` kodu, 24 saatlik çevrimdışı
penceresi, hepsi o tavanın çevresinde kurulmuştu. **Kertik'te istek başına para
yok, dolayısıyla korunacak tavan da yok.**

İkinci sebep: o mimari her açılışta Google girişi istiyordu. Kertik'te bunun
karşılığı yok. Ürünün vaadi "hiçbir şey sormayan, hiçbir veri toplamayan"
uygulama; giriş ekranı bu vaadi bozar.

### SSAID neden düşürüldü

SSAID **kimlik** verir, **depolama** vermez. Verileri temizlemek
SharedPreferences'ı ve `app_webview`'i birlikte siler
(`app/src/main/res/xml/yedekleme_kurallari.xml`: `sharedpref` + `file/app_webview`).
Uygulama deposunun dışında, temizlikten sağ çıkan bir yer yok. Sonuç iki kötü
seçenek: tanıdık cihaza tam süre vermek (hiçbir şey kazanılmaz) ya da reddetmek
(verisini temizleyen dürüst kullanıcıyı haksız yere kilitler, İ3'e aykırı).
Bu yüzden katman, sunucusuz hâliyle işe yaramıyor.

### Kertik'in kendi savunması

Denemeyi sıfırlamak için yok edilmesi gereken şey, uygulamaya gelinen şeyin ta
kendisi. Leucine'de kaydı silmek bedava; Kertik'te silinen kayıt ebru, kum
bahçesi ve duvar.

### Leucine parçalarının karşılığı

| Parça | Kertik'te | Neden |
| --- | --- | --- |
| Worker + KV | **Yok** | tek işi maliyet tavanıydı |
| ECDSA imza + açık anahtar | **Yok** | istemci yalanını engelliyordu, kazanç zaten sıfır |
| IP hız sınırı, `GRACE_TOTAL`, günlük tavan | **Yok** | sınırlanacak harcama yok |
| `grace` / `grace_limit` / `free_limit` | **Yok** | günlük tavan olmayınca "bugünlük hakkın doldu" durumu doğmuyor |
| 24 saatlik çevrimdışı penceresi | **Yok** | ağ hiç devrede değil |
| "Ödemiş kullanıcı ağdan engellenmez" | **Kendiliğinden** | ağ yok |
| SSAID | **Yok** | gerekçesi yukarıda |
| Kayıt tanıklığı | **Var** | en kolay aşılan yol, tek kuralla kapanıyor |
| Zaman kaynağı | **Yerel yüksek su işareti** | sunucu saatine eşdeğer işi yapar |

---

## Tasarım

### Durum alanı

```js
deneme: {
  baslangic: <ms|null>,   // en eski görülen çapa
  bakilan:   <ms>         // görülmüş en yüksek duvar saati
}
```

`S`'in içinde yaşar. Bunun bedava getirisi: `localStorage` (`kertik.v1`),
JSON dışa aktarma (`JSON.stringify(S)`, 7515), JSON içe aktarma (7618) ve Drive
yedeği aynı nesneyi taşıdığı için çapa kaydın kendisiyle birlikte yolculuk eder.

### Üç kaynak, en eski kazanır

1. `S.deneme.baslangic` (kaydın içinde; yedekle ve Drive ile taşınır)
2. Eski anahtar `kertik.kurulum` (göç: bir kez okunur, sonra silinir)
3. Kayıt tanıklığı: kayıttaki en eski seansın `startedAt` değeri

```
etkinBaslangic = min(bulunan kaynaklar)
```

Hiçbir kaynak eskisini ezemez. Hiçbir kaynak yoksa duvar saati yazılır (temiz
kurulum tam süre görür, kimse haksız kilitlenmez).

Üçünün ayrı ayrı işi var: 1 numara kalıcılığı taşır, 2 numara güncellemeyle
gelen eski kullanıcıyı korur, 3 numara "yedeği geri yükle" ile denemeyi
sıfırlama yolunu kapatır.

### Saat katmanı

```
duvarSaati() = max(now(), S.deneme.bakilan)
```

`bakilan` her diske yazımda ilerletilir (`yazDiske`, 1105). Cihaz saati geri
alınırsa kalan gün artmaz. İleri alınırsa azalır; bu kullanıcı aleyhine değil,
çapa zaten ileriyi ödüllendirmez. Teknik olarak yeni bir şey icat edilmiyor:
`KontrolWidget.kt:67` aynı düşünceyi (duvar saatini monoton bir çerçeveye
çevirme) zaten kullanıyor.

---

## Dosya bazında adımlar

Hepsi `kertik-android/app/src/main/assets/index.html` içinde. Kotlin tarafında
değişiklik yok.

1. **`DEFAULTS`'a `deneme` alanı ekle.** `load()` (1097) ve içe aktarma (7618)
   `Object.assign(structuredClone(DEFAULTS), d, ...)` kullandığı için alan hem
   varsayılanı alır hem eski kayıtlarda kaybolmaz hem de yedekten geri gelir.

2. **`kurulumAni()` (2432) yeniden yaz.** Üç kaynağı topla, en eskisini
   `S.deneme.baslangic`e yaz ve döndür. Eski `kertik.kurulum` anahtarını bir kez
   okuyup göç ettir, sonra sil (tek doğruluk kaynağı kalsın). Mevcut imza
   korunur; çağıranlar değişmez.

3. **`denemeKalanGun()` (2437) `duvarSaati()` kullansın.** `now()` yerine
   `duvarSaati()`. `Math.max(0, Math.min(DENEME_GUN, ...))` kırpması aynen kalır.
   `DENEME_GUN = 14` değişmiyor.

4. **`duvarSaati()` ve `bakilanIlerlet()` ekle**, `yazDiske()` (1105) içinden
   ilerlet.

5. **`mergeStates` (7692) çıktısına `deneme` ekle.** Dönen nesne bugün alan alan
   kuruluyor (`sessions, tasks, settings, active, tombstones, settingsEditedAt`),
   yani bu kural yazılmazsa **her Drive senkronunda çapa düşer.** Kural: en eski
   `baslangic`, en büyük `bakilan` kazanır.

6. **Çağrı noktaları değişmiyor.** `tamMi()` (2443), `kasaDenemeKontrol()` (2599)
   ve ayarlar satırı (7350) zaten `kurulumAni()` / `denemeKalanGun()` üzerinden
   gidiyor.

7. **Yeni test dosyası:** `kertik-android/test/test-deneme.js`, `hepsi.js`
   listesine kayıt (mevcut kalıp).

8. **Simülatörü yenile:** `node simulasyon/olustur-simulator.js`.

---

## Kabul kriterleri

Her biri `test-deneme.js` içinde önerme olarak yazılır.

1. Temiz kurulum: kalan gün 14.
2. Üç gün ileri sarılmış saat: kalan gün 11.
3. Bir ay geri alınmış saat: kalan gün değişmez.
4. Kayıtta 20 günlük seans var, çapa yok: deneme bitmiş sayılır (katman 3).
5. Kayıtta 2 günlük seans var, çapa yok: deneme başlangıcı o seansın tarihi olur.
6. Yedek al, durumu sil, yedeği geri yükle: seanslar döner, kalan gün **aynı yerden** devam eder.
7. Çapa varken eski seanslar silinirse kalan gün artmaz.
8. Dışa aktarılan JSON çapayı taşır.
9. İçe aktarılan eski biçim yedek (çapasız) uygulamayı bozmaz, çapa yoksa tanıklık devreye girer.
10. `mergeStates` iki farklı çapa arasından en eskisini seçer ve `deneme` alanını kaybetmez.
11. `tamMi()` false iken `startSession()` duvar açar; kayıt, geçmiş, dışa aktarma erişilebilir kalır.
12. Eski biçim seans (`tohum` ve `akisV` alanları yok) bozulmadan çalışır.

---

## Doğrulama

- `node kertik-android/test/hepsi.js --hizli`: yeni dosya dahil, 0 hata
  (CLAUDE.md'deki kalıcı kırmızılar hariç).
- `node simulasyon/olustur-simulator.js`: simülatör yenilenir, hata yok.
- `index.html` diff'i: yalnız `DEFAULTS`, deneme bölgesi (2412-2450 civarı),
  `yazDiske` (1105) ve `mergeStates` (7692) satırlarında değişiklik; algoritma
  kodunda sıfır dokunuş.

---

## Açıkta kalan (bilerek)

- Verileri temizleyip hiçbir yedeği geri yüklemeyen ve Drive'a bağlanmamış
  kullanıcı 14 günü yeniden görür. Maliyeti sıfır lira; zaten ödemeyecek bir
  kullanıcının 14 günü. Cihaz dışı tanık olmadan bu delik kapanmaz.
- Saat ileri alınırsa kalan gün azalır (kullanıcı aleyhine değil).
- Ham SSAID hiçbir yere yazılmadığı için gizlilik beyanı büyümez.

---

## Kapsam dışı

- Worker, KV, ECDSA, `Deneme.kt`, SSAID, gizli dosya/MediaStore numaraları.
- `DENEME_GUN` değeri (14) ve fiyatlandırma.
- `K_BITTI` (`kertik.tamBitti`) taşınmıyor: kaybı yalnız ödeme duvarının bir kez
  daha görünmesi, hile vektörü değil.
- Kotlin tarafı ve `Kasa.kt` satın alma akışı.
