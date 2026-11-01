# 22 — Çoklu Dil (i18n) — Ertelendi (16 Ağustos 2026)

> Silinen `20-kullanim-feedback.md`'nin dil bölümünün korunmuş ve **budanmış** hâli.
> Orijinal metin sekiz dilli bir pazar stratejisiydi; aşağıda neden ertelendiği ve
> şimdi yapılacak asgari işin ne olduğu var.

---

## Karar: v1'de **Türkçe + İngilizce**. Başka dil yok.

### Neden orijinal plan ertelendi

**1. Rakamlar dayanaksızdı.**
Silinen dosya "yerelleştirilmiş uygulamalar %128 daha fazla organik indirme ve %26 daha
yüksek dönüşüm elde eder" diyordu. Kaynağı yoktu. Karar bu sayılara dayandırılamaz.

**2. "~50 kelime" yanlış ölçü.**
Ayarlar açıklamaları, 6 görev durumu, dürüstlük sorusu, bildirim metinleri, tarih
formatları hesaba katılınca sayı büyüyor. Ama asıl mesele sayı değil:

> Bu uygulamanın metin **tonu** ürünün yarısı. "Hayır, sayılmasın" cümlesinin taşıdığı
> şey — suçlamayan, sakin, dürüst — çeviride kaybolur. Orijinal dosyadaki
> `Ehrlichkeits-Check` klinik bir muayene gibi duruyor.

**3. Kontrol edilemez.** Japonca/Korece çeviriyi ne sen ne ben doğrulayabiliriz.

**4. Ücretli uygulama, üstelik peşin ödemeli.** (bkz. `21`) Para verip açan kullanıcı
garip çeviri görürse yıldız düşer. Bedava uygulamada affedilen şey, ödenmiş uygulamada
affedilmez. Ve peşin ödemeli modelde **her yorum ağırlığının katı** — az sayıda yorum
olacağı için biri bile satışı etkiler.

---

## Şimdi yapılacak asgari iş

Altyapı ucuz ve doğru; **şimdi kurulsun**, diller sonra eklensin.

- `data-i18n` etiketleri ve ~60 satırlık sözlük yapısı (harici kütüphane yok).
- Dil tespiti: `localStorage` → `navigator.language` → `en`.
- Ayarlarda dil seçici — ama listede sadece **Türkçe ve English**.
- Bildirim metinleri de sözlükten gelsin (`kertik-android` native köprüsü üzerinden
  dil parametresi).
- Tarih formatı dile bağlansın (`DD.MM.YYYY` / `MM/DD/YYYY`).

### İngilizce nasıl yazılmalı

**Çeviri değil, ikinci kez yazılmış metin.** Türkçesine bakıp kelime karşılığı arama;
aynı duyguyu İngilizce'de baştan kur. Örnek:

| Türkçe | Kötü (birebir) | İyi |
|---|---|---|
| Hayır, sayılmasın | No, don't count it | Don't count this |
| Dürüstlük sorusu | Honesty Question | Honest check |
| Olmadı | Failed / Not done | Didn't happen |
| Yarım kaldı | Half remained | Left unfinished |

> "Olmadı" için **Failed** kesinlikle kullanılmaz — ürünün tonu suçlamamak üzerine kurulu.

---

## Sonraki diller — ne zaman

Şu üç şart birlikte sağlanınca:

1. Uygulama Play'de yayında ve **ilk 100 gerçek alıcı** geçilmiş.
2. Play Console'daki ülke dağılımı hangi dilin gerçekten talep gördüğünü gösteriyor.
3. O dili konuşan bir insan metni okuyup onaylayabiliyor.

Sıra (satın alma gücü ve kategori yakınlığına göre): **Almanca → Japonca → Korece**.
Almanca DACH bölgesinde ARPU lideri; Japonca sade/kâğıt estetiğine kültürel yatkınlık;
Korece yoğun çalışma kültürü. Ama üçü de yukarıdaki üç şarttan sonra.

---

## Diğer UX maddeleri (silinen dosyadan kurtarılan)

1. **Dürüstlük sorusu akışı** sürtünmesiz olmalı, tek dokunuşla geçilebilmeli.
2. **Modlar arası akışkan geçiş (morphing):** kronometre ↔ pomodoro geçişi sert
   kesilmek yerine yumuşak, organik bir animasyonla erisin.
   Çalışan prototip: `antigravity/ornekler/akiskangecis_demo.html`
3. **Google Tasks köprüsü:** 6 durumlu Kertik modelinin yabancı dil karşılıkları
   oturmalı — ama bu, dil eklendiğinde. Şimdilik açık madde değil.




## Yapıldı

(kontrol edilmesi lazım ama, işlem yarım kalmış olabilir)

