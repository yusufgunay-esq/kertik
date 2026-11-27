/* Kertik Haptik Dili ve Titreşim Doğrulama Testi
   24-sanat-dili.md §6.5 ve 32-haptik-dili.md gereksinimlerini doğrular:
   - 14 Doku sözlüğü bütünlüğü ve genlik zarfları
   - 4 Kütle profili donanım eşleşmesi
   - Android Native Köprü sözleşmesi (titretDoku & kompozisyon)
   - Çift titreşim engelleme ve ayar disiplini
   - UI etkileşim noktalarının haptik geri bildirimleri
*/
const fs = require('fs');
const path = require('path');
const { JSDOM } = require('jsdom');

console.log('=== Kertik Haptik Dili & Titreşim Testleri ===\n');

let pass = 0, fail = 0;
const ok = (n, c, x) => { c ? (pass++, console.log('  ✓ ' + n)) : (fail++, console.log('  ✗ ' + n, x ?? '')); };

// 1. KOTLIN NATIVE KÖPRÜ DENETİMİ
console.log('1) Android Native Katmanı (MainActivity.kt & kt/MainActivity.txt)');
const ktFile = path.join(__dirname, '../app/src/main/java/com/yusufgunay/kertik/MainActivity.kt');
const ktTxtFile = path.join(__dirname, '../../kt/MainActivity.txt');

[ktFile, ktTxtFile].forEach(dosya => {
  const ad = path.basename(dosya);
  const ktCode = fs.readFileSync(dosya, 'utf8');
  ok(ad + ' icinde titretDoku tanimli', ktCode.includes('fun titretDoku(sureler: String, genlikler: String, komp: String)'));
  ok(ad + ' icinde kompozisyon yardimcisi tanimli', ktCode.includes('fun kompozisyon(v: android.os.Vibrator, ad: String)'));
  ok(ad + ' icinde tas_oturma donanim kompozisyonu tanimli',
    ktCode.includes('PRIMITIVE_THUD') && ktCode.includes('PRIMITIVE_LOW_TICK') && ktCode.includes('tas_oturma'));
  ok(ad + ' icinde hasAmplitudeControl ile createWaveform(t, a, -1) cagriliyor',
    ktCode.includes('hasAmplitudeControl()') && ktCode.includes('createWaveform(t, a, -1)'));
  ok(ad + ' icinde genliksiz cihazlar icin timings[0] = 0 yapisi mevcut',
    ktCode.includes('timings[0] = 0'));
});

// 2. WEB ARAYÜZÜ VE HAPTİK SÖZLÜĞÜ DOĞRULAMASI
const htmlPath = path.join(__dirname, '../app/src/main/assets/index.html');
const html = fs.readFileSync(htmlPath, 'utf8');

let haptikCagrilar = [];
let tarayiciVibrations = [];

const dom = new JSDOM(html, {
  runScripts: 'dangerously',
  pretendToBeVisual: true,
  url: 'http://localhost/',
  beforeParse(w) {
    if (!w.structuredClone) w.structuredClone = o => JSON.parse(JSON.stringify(o));
    w.requestAnimationFrame = (fn) => setTimeout(fn, 16);
    w.cancelAnimationFrame = (id) => clearTimeout(id);
    w.HTMLCanvasElement.prototype.getContext = () => ({
      canvas: {}, globalAlpha: 1, globalCompositeOperation: 'source-over',
      beginPath() {}, moveTo() {}, lineTo() {}, quadraticCurveTo() {}, bezierCurveTo() {},
      stroke() {}, fill() {}, fillRect() {}, strokeRect() {}, clearRect() {}, rect() {}, clip() {},
      setTransform() {}, drawImage() {}, putImageData() {}, closePath() {}, arc() {}, ellipse() {},
      save() {}, restore() {}, translate() {}, rotate() {}, scale() {}, setLineDash() {},
      measureText: () => ({ width: 10 }), strokeText() {}, fillText() {},
      createImageData: (w, h) => ({ width: w, height: h, data: new Uint8ClampedArray(w * h * 4) }),
      createRadialGradient: () => ({ addColorStop() {} }),
      createLinearGradient: () => ({ addColorStop() {} })
    });

    w.KertikNative = {
      goster: () => {},
      gizle: () => {},
      bildirimIzniVar: () => true,
      bildirimIzniIste: () => {},
      dndIzniVar: () => true,
      dndIzniIste: () => {},
      dndBaslat: () => true,
      dndBitir: () => true,
      ekraniAcikTut: () => {},
      surum: () => '1.0',
      resimKaydet: () => 'galeri',
      yedekKaydet: () => 'indirildi',
      titretDoku: (t, a, komp) => {
        haptikCagrilar.push({ tip: 'titretDoku', t: t.split(',').map(Number), a: a ? a.split(',').map(Number) : [], komp });
      },
      titretPattern: p => {
        haptikCagrilar.push({ tip: 'titretPattern', p });
      },
      titretHassas: (ms, amp) => {
        haptikCagrilar.push({ tip: 'titretHassas', ms, amp });
      },
      titret: ms => {
        haptikCagrilar.push({ tip: 'titret', ms });
      }
    };

    w.navigator.vibrate = function(pattern) {
      tarayiciVibrations.push(pattern);
      return true;
    };
  }
});

const win = dom.window;
const sonHaptik = () => haptikCagrilar[haptikCagrilar.length - 1];
const temizle = () => { haptikCagrilar = []; tarayiciVibrations = []; };

console.log('\n2) Doku Sözlüğü ve Genlik Zarfı Bütünlüğü');
const dokular = win.eval('DOKU');
const beklenenDokular = ['baslat', 'mola', 'devam', 'bitir', 'sec', 'not', 'donum', 'kertik', 'pomodoro', 'kirik', 'kintsugi', 'ruzgar1', 'ruzgar2', 'ruzgar3'];

beklenenDokular.forEach(k => {
  const d = dokular[k];
  ok('DOKU.' + k + ' tanimli', !!d);
  ok('DOKU.' + k + ' sure ve genlik uzunluklari esit', d && Array.isArray(d.t) && Array.isArray(d.a) && d.t.length === d.a.length);
  if (d && d.t && d.a) {
    const gecerliSure = d.t.every(t => typeof t === 'number' && t > 0);
    const gecerliGenlik = d.a.every(a => typeof a === 'number' && a >= 0 && a <= 255);
    ok('DOKU.' + k + ' sureleri pozitif ve genlikleri 0-255 araliginda', gecerliSure && gecerliGenlik);
  }
});

// Pomodoro taş oturma donanım primitifi ve sönümlenme
ok('DOKU.pomodoro tas_oturma kompozisyon adi tasiyor', dokular.pomodoro && dokular.pomodoro.komp === 'tas_oturma');
ok('DOKU.pomodoro sonumlenen 3 vuruslu zarfa sahip (190 -> 95 -> 45)',
  dokular.pomodoro && dokular.pomodoro.a[0] === 190 && dokular.pomodoro.a[2] === 95 && dokular.pomodoro.a[4] === 45);

// Kintsugi yükselen onarım zarfı
ok('DOKU.kintsugi yukselen zarfa sahip (50 -> 125)',
  dokular.kintsugi && dokular.kintsugi.a[0] < dokular.kintsugi.a[2] && dokular.kintsugi.a[2] === 125);

// Kırık taş çatlama zarfı
ok('DOKU.kirik sert baslangicli (205) ve duzensiz sonumlenmeli',
  dokular.kirik && dokular.kirik.a[0] === 205 && dokular.kirik.t.length === 5);

// 3. KÜTLE PROFİLLERİ DOĞRULAMASI
console.log('\n3) Taş Kütle Profilleri (KUTLE_PROFILLERI)');
const kutleler = win.eval('KUTLE_PROFILLERI');
const dakikalar = [15, 25, 50, 90];
dakikalar.forEach(dk => {
  const kp = kutleler[dk];
  ok('KUTLE_PROFILLERI[' + dk + '] haptik profili tanimli', kp && kp.haptik && Array.isArray(kp.haptik.t) && Array.isArray(kp.haptik.a));
  ok('KUTLE_PROFILLERI[' + dk + '] (' + (kp ? kp.ad : '') + ') genlik dizisi gecerli',
    kp && kp.haptik.a.every(a => a >= 0 && a <= 255));
});
ok('Agir granit (90 dk) kutle siralamasinin en sert vurusu',
  kutleler[90].haptik.a[0] > kutleler[50].haptik.a[0] &&
  kutleler[50].haptik.a[0] > kutleler[25].haptik.a[0] &&
  kutleler[25].haptik.a[0] > kutleler[15].haptik.a[0]);

/* Doktrin: bitis bir HABERDIR, baslangic bir YUZEYDIR. Parmak ekrandayken
   hicbir doku pomodoro bitisinden (190) sert vuramaz. */
const elBandi = [
  ...['baslat', 'mola', 'devam', 'bitir', 'sec', 'not', 'donum', 'kertik'].flatMap(k => dokular[k].a),
  ...dakikalar.flatMap(dk => kutleler[dk].haptik.a)
];
ok('Elle hissedilen hicbir doku pomodoro bitisinden (190) sert degil',
  Math.max(...elBandi) < dokular.pomodoro.a[0]);

/* TEK vuruslu dokular LRA motorlu cihazlarda 9 ms altinda hissedilmez.
   Cok vuruslu dokularin sonundaki yankilar zarfin parcasi, ayri kural. */
const tekVuruslular = [
  ...Object.entries(dokular).filter(([, d]) => d.t.length === 1).map(([k, d]) => [k, d.t[0]]),
  ...dakikalar.filter(dk => kutleler[dk].haptik.t.length === 1).map(dk => ['kutle' + dk, kutleler[dk].haptik.t[0]])
];
ok('Tek vuruslu her doku >= 9 ms (LRA hissedilirlik esigi)',
  tekVuruslular.every(([, ms]) => ms >= 9), tekVuruslular.filter(([, ms]) => ms < 9));

// 4. ÇİFT TİTREŞİM ENGELLEME VE İZOLASYON TESTLERİ
console.log('\n4) Çift Titreşim Önleme & Ayar İzolasyonu');
temizle();
win.eval('buzz("baslat")');
const h1 = sonHaptik();
ok('Native kopru varken titretDoku cagrildi', h1 && h1.tip === 'titretDoku' && h1.t[0] === 14 && h1.a[0] === 120);
ok('Native kopru varken navigator.vibrate ASLA cagrilmadi (cift titresim engellendi)', tarayiciVibrations.length === 0);

// Titreşim ayarı kapalıyken mutlak sessizlik
win.eval('S.settings.vibrate = false; save();');
temizle();
win.eval('buzz("baslat"); buzz("pomodoro"); buzz("mola");');
ok('S.settings.vibrate = false iken hicbir titresim tetiklenmedi', haptikCagrilar.length === 0);
win.eval('S.settings.vibrate = true; save();');

// 5. KULLANICI ARAYÜZÜ (UI) VE ETKİLEŞİM NOKTALARI
console.log('\n5) UI Dokunma Noktaları Haptik Entegrasyonu');

// Sekme değişimi (setTab)
temizle();
win.eval('setTab("tasks")');
const hSekme = sonHaptik();
ok('Sekme degistirildiginde sec dokusu tetiklendi', hSekme && hSekme.t[0] === 9 && hSekme.a[0] === 60);

// Görev ekleme
temizle();
win.document.getElementById('taskInput').value = 'Haptik test gorevi';
win.eval('addTask()');
const hGorev = sonHaptik();
ok('Gorev eklendiginde sec dokusu tetiklendi', hGorev && hGorev.t[0] === 9 && hGorev.a[0] === 60);

// Görev tamamlama (kertik)
temizle();
win.eval('applyStatus(S.tasks[S.tasks.length - 1], "bitti")');
const hBitti = sonHaptik();
ok('Gorev tamamlandiginda tek vurusluk kertik dokusu tetiklendi', hBitti && hBitti.t[0] === 12 && hBitti.a[0] === 110);

// Sayaca dön
win.eval('setTab("timer")');

// Mod değiştirme (Pomodoro seçimi)
temizle();
win.eval('S.settings.mode = "stopwatch"; save(); render();');
const pomoBtn = win.document.querySelector('#modeSeg button[data-m="pomodoro"]');
if (pomoBtn) {
  pomoBtn.click();
  const hMod = sonHaptik();
  ok('Mod degistirildiginde (Pomodoro) sec dokusu tetiklendi', hMod && hMod.t[0] === 9 && hMod.a[0] === 60);
}

// Süre çipi seçme (25 -> 50 dk)
temizle();
win.eval('S.settings.pomoTarget = 25; render();');
const dur50Btn = win.document.querySelector('.durs button[data-d="50"]');
if (dur50Btn) {
  dur50Btn.click();
  const hSure = sonHaptik();
  ok('Pomodoro sure cipi (50dk) secildiginde sec dokusu tetiklendi', hSure && hSure.t[0] === 9 && hSure.a[0] === 60);
}

// 6. SEANS YAŞAM DÖNGÜSÜ DOKULARI
console.log('\n6) Seans Yaşam Döngüsü ve Maddi Olaylar');

// Kronometre başlat
win.eval('S.settings.mode = "stopwatch"; save(); render();');
temizle();
win.eval('startSession()');
const hKronBaslat = sonHaptik();
ok('Kronometre basladiginda baslat dokusu (14ms / 120amp) tetiklendi',
  hKronBaslat && hKronBaslat.t[0] === 14 && hKronBaslat.a[0] === 120);

// Mola başlat
temizle();
win.eval('takeBreak()');
const hMola = sonHaptik();
ok('Molaya girildiginde sonumlenen mola dokusu (75 -> 30) tetiklendi',
  hMola && hMola.t.length === 3 && hMola.a[0] === 75 && hMola.a[2] === 30);

// Devam et
temizle();
win.eval('resume()');
const hDevam = sonHaptik();
ok('Mola bittiginde hafif devam dokusu (11ms / 95amp) tetiklendi',
  hDevam && hDevam.t[0] === 11 && hDevam.a[0] === 95);

// Seans notu ekle
temizle();
const snInput = win.document.getElementById('sessionNoteInput');
if (snInput) {
  snInput.value = 'Haptik test notu';
  win.eval('addSessionNote()');
  const hNot = sonHaptik();
  ok('Seans notu eklendiginde not dokusu (11ms / 80amp) tetiklendi',
    hNot && hNot.t[0] === 11 && hNot.a[0] === 80);
}

// Kronometre bitir
temizle();
win.eval('finish()');
const hBitir = sonHaptik();
ok('Kronometre basariyla bitirildiginde bitir dokusu (110 -> 60) tetiklendi',
  hBitir && hBitir.t.length === 3 && hBitir.a[0] === 110 && hBitir.a[2] === 60);

// Pomodoro seansı (erken bitirme / kırık taş)
win.eval('S.settings.mode = "pomodoro"; S.settings.pomoTarget = 25; save(); render();');
win.eval('startSession()');
temizle();
win.eval('finish()');
const hKirik = sonHaptik();
ok('Hedefe ulasilmadan bitirilen Pomodoro kirik dokusu (205 -> 90 -> 45) tetikledi',
  hKirik && hKirik.t.length === 5 && hKirik.a[0] === 205 && hKirik.a[2] === 90 && hKirik.a[4] === 45);

// Pomodoro hedef dolumu (otomatik zamanlayıcı)
win.eval('S.settings.mode = "pomodoro"; S.settings.pomoTarget = 25; save(); render();');
win.eval('startSession()');
temizle();
win.eval('const se = activeSession(); se.startedAt -= 26 * 60000; se.events[0].at = se.startedAt; pomoDone = false; tickChecks();');
const hPomoHedef = sonHaptik();
ok('Pomodoro hedefi doldugunda pomodoro donanim haptigi (tas_oturma / 190 -> 95 -> 45) tetiklendi',
  hPomoHedef && hPomoHedef.komp === 'tas_oturma' && hPomoHedef.a[0] === 190 && hPomoHedef.a[2] === 95 && hPomoHedef.a[4] === 45);
win.eval('finish()');

// 7. AYARLAR MENÜSÜ HAPTİK TEPKİLERİ
console.log('\n7) Ayarlar Menüsü Haptik Tepkileri');
win.eval('setTab("settings"); renderSettings();');

temizle();
const segMilestoneBtn = win.document.querySelector('button[data-set="milestone"][data-v="25"]');
if (segMilestoneBtn) {
  segMilestoneBtn.click();
  const hSeg = sonHaptik();
  ok('Ayar segment secildiginde sec dokusu tetiklendi', hSeg && hSeg.t[0] === 9 && hSeg.a[0] === 60);
}

temizle();
const togKeepAwakeBtn = win.document.querySelector('button[data-tog="keepAwake"]');
if (togKeepAwakeBtn) {
  togKeepAwakeBtn.click();
  const hTog = sonHaptik();
  ok('Ayar toggle anahtari tiklandiginda sec dokusu tetiklendi', hTog && hTog.t[0] === 9 && hTog.a[0] === 60);
}

/* Regresyon: buzz() ayar DEGISTIKTEN sonra cagrilmali. Ters sirada
   "titresim"i acmak hicbir sey hissettirmiyordu — kullanici acar,
   calismadigini sanirdi. */
win.eval('S.settings.vibrate = false; renderSettings();');
temizle();
const togVibBtn = win.document.querySelector('button[data-tog="vibrate"]');
if (togVibBtn) {
  togVibBtn.click();
  ok('Titresim ayari ACILDIGINDA onay titresimi geldi (sira regresyonu)',
    win.eval('S.settings.vibrate') === true && haptikCagrilar.length === 1);

  win.eval('renderSettings();');
  temizle();
  const togVibBtn2 = win.document.querySelector('button[data-tog="vibrate"]');
  togVibBtn2.click();
  ok('Titresim ayari KAPATILDIGINDA sessiz kaldi',
    win.eval('S.settings.vibrate') === false && haptikCagrilar.length === 0);
  win.eval('S.settings.vibrate = true;');
}

console.log('\n' + pass + ' gecti, ' + fail + ' kaldi');
process.exit(fail ? 1 : 0);
