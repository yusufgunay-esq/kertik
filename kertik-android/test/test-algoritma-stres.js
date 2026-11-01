/* ALGORİTMA STRES TESTİ — tohum, kum bahçesi, tırmık, bütçe.

   Burada sınanan şey piksel değil, algoritmanın DEĞİŞMEZLERİ:
     · aynı seans ve aynı gün her açılışta aynı deseni veriyor mu (determinizm),
     · desen eski seansın damgasına bağlı kalıyor mu (geriye dönük uyum),
     · en kalabalık günde ve en uzun seansta sayı bozuluyor mu (NaN, taşma),
     · yavaş cihazda desenden vazgeçme yolu çalışıyor mu (bütçe).

   Kök tohumun (KOK_TOHUM) üç yüzeye de işlediği hem kaynakta hem çalışma
   zamanında doğrulanır — "eklendi" demek yetmez, kanıt istenir.

   Koşturmak için:  npm install jsdom && node test-algoritma-stres.js
*/
const fs = require("fs"), path = require("path");
const { JSDOM, VirtualConsole } = require("jsdom");

const HTML = path.join(__dirname, "../app/src/main/assets/index.html");
let pass = 0, fail = 0;
function ok(name, cond, extra) {
  if (cond) { pass++; console.log("  ✓ " + name); }
  else { fail++; console.log("  ✗ " + name, extra === undefined ? "" : extra); }
}
const bekle = ms => new Promise(r => setTimeout(r, ms));

/* ---------- sahte tuval ----------
   test-cizim.js ile aynı sözleşme: uygulamanın çağırdığı metot kümesinin
   tamamı taklit edilir, yoksa cihazda olmayan sahte bir arıza doğar. */
function sahteCtx() {
  const c = {
    canvas: null, globalAlpha: 1, globalCompositeOperation: "source-over",
    strokeStyle: "", fillStyle: "", lineWidth: 1, lineCap: "", lineJoin: ""
  };
  const yut = ["beginPath", "moveTo", "lineTo", "stroke", "fill", "fillRect", "clearRect",
               "setTransform", "drawImage", "putImageData", "closePath", "arc", "ellipse", "save", "restore", "translate", "rotate", "scale", "setLineDash",
               "quadraticCurveTo", "bezierCurveTo", "arcTo", "clip", "rect", "roundRect",
               "fillText", "strokeText", "strokeRect", "resetTransform", "getLineDash"];
  for (const k of yut) c[k] = () => {};
  c.measureText = t => ({ width: String(t).length * 6 });
  c.createImageData = (w, h) => ({ width: w, height: h, data: new Uint8ClampedArray(w * h * 4) });
  const grad = { addColorStop() {} };
  c.createRadialGradient = () => grad;
  c.createLinearGradient = () => grad;
  return c;
}

/* Sayfada kendi kendine düşen her hata kaydedilir: sessiz stderr yerine
   görünür kırmızı. (Eksik sahte tuval metodu bir kez böyle gizlenmişti.) */
function kur(kayit) {
  const hatalar = [];
  const vc = new VirtualConsole();
  vc.on("jsdomError", e => {
    const m = String((e && e.message) || e);
    /* "Not implemented" jsdom'un yetenek eksiği, uygulamanın hatası değil */
    if (/^Not implemented/.test(m)) return;
    hatalar.push(m);
  });
  const dom = new JSDOM(fs.readFileSync(HTML, "utf8"), {
    runScripts: "dangerously", pretendToBeVisual: true, virtualConsole: vc, url: "http://localhost/",
    beforeParse(w) {
      if (!w.structuredClone) w.structuredClone = o => JSON.parse(JSON.stringify(o));
      w.HTMLCanvasElement.prototype.getContext = function () {
        const c = sahteCtx(); c.canvas = this; return c;
      };
      w.HTMLCanvasElement.prototype.toDataURL = () => "data:image/png;base64,";
      if (kayit) w.localStorage.setItem("kertik.v1", JSON.stringify(kayit));
    }
  });
  return new Promise(res => setTimeout(() => { dom.window._hatalar = hatalar; res(dom.window); }, 60));
}

/* ---------- örnek veri ---------- */
const T = Date.now(), DK = 60000;
/* Gün sınırına yakalanmamak için sabit bir öğle saati kullanılır:
   gece yarısına 40 dk kala koşulsa bile seanslar aynı güne düşer. */
const TB = new Date(2026, 5, 15, 14, 0, 0).getTime();
const bosKayit = (mode) => ({
  sessions: [], tasks: [], tombstones: [], active: null,
  settings: { mode: mode || "stopwatch", theme: "light" }, sync: { connected: false }
});
const gunAnahtari = ts => {
  const d = new Date(ts);
  return d.getFullYear() + "-" + String(d.getMonth() + 1).padStart(2, "0") + "-" + String(d.getDate()).padStart(2, "0");
};
function seans(id, bitTs, dakika, molalar, mode, target) {
  const bas = bitTs - dakika * DK;
  const ev = [{ type: "start", at: bas }];
  for (const [a, b] of (molalar || [])) {
    ev.push({ type: "break_start", at: bas + a * DK });
    ev.push({ type: "break_end", at: bas + b * DK });
  }
  ev.push({ type: "end", at: bitTs });
  return {
    id, startedAt: bas, endedAt: bitTs, dayKey: gunAnahtari(bas), note: "",
    mode: mode || "stopwatch", target: target || 0, events: ev,
    awayMs: 0, unconfirmedOk: false, edited: false, editedAt: bitTs
  };
}
/* Bahçe formunun altı yüzü de denenmeli: gün anahtarı hangi biçimi verirse
   o günü seçeriz (kumCepheMesafe'nin bütün dalları). */
function formGunu(adet) {
  const bulunan = {};
  for (let i = 0; i < (adet || 150); i++) {
    const d = new Date(2026, 0, 1 + i);
    const gun = d.getFullYear() + "-" + String(d.getMonth() + 1).padStart(2, "0") + "-" + String(d.getDate()).padStart(2, "0");
    const tur = wT.eval(`kumBicim(hash32(KOK_TOHUM + "|kumbahce|" + ${JSON.stringify(gun)})).tur`);
    if (!bulunan[tur]) bulunan[tur] = gun;
  }
  return bulunan;
}

let wT = null, wU = null;

(async () => {
  wT = await kur(bosKayit());
  wU = await kur(bosKayit());

  console.log("\n1) Kök tohum üç yüzeye işlemiş mi (kaynak kanıtı)");
  {
    const src = fs.readFileSync(HTML, "utf8");
    const tanim = (src.match(/const KOK_TOHUM/g) || []).length;
    ok("kök tohum tek noktada tanımlı", tanim === 1, tanim + " tanım");
    ok("seans tohumu kökten besleniyor", /function seansTohumu[\s\S]{0,220}KOK_TOHUM/.test(src));
    ok("kum TAŞI kökten besleniyor", src.includes('KOK_TOHUM + "|kum|"'));
    ok("kum BAHÇESİ kökten besleniyor", src.includes('KOK_TOHUM + "|kumbahce|"'));
    ok("seans kaydına tohum yazılıyor", /tohum:\s*seansTohumu\(/.test(src));
    ok("akış (ebru) kayıtlı tohumu okuyor", /AK\.tohum = se\.tohum \|\| seansTohumu\(/.test(src));
    ok("resim (seansResmi) kayıtlı tohumu okuyor", /const tohum = se\.tohum \|\| seansTohumu\(/.test(src));
    ok("zen taşı tohumu seansTohumu'ndan geçiyor", /tasSvg\([^)]*seansTohumu\(/.test(src));
  }

  console.log("\n2) Tohum fonksiyonları — determinizm ve ayrışma");
  {
    const r = wT.eval(`(() => {
      const deger = [], kume = new Set();
      for (let i = 0; i < 300; i++) { const t = seansTohumu("seans-" + i); deger.push(t); kume.add(t); }
      return {
        hepsiTamsayi: deger.every(v => Number.isInteger(v) && v >= 0 && v <= 4294967295),
        tekil: kume.size,
        kararli: seansTohumu("seans-7") === seansTohumu("seans-7"),
        nesneIleAyni: seansTohumu({ id: "seans-7" }) === seansTohumu("seans-7"),
        bosGirdi: seansTohumu(null) === hash32(KOK_TOHUM + "|"),
        kokKatkili: seansTohumu("x") !== hash32("x"),
        kokEsit: seansTohumu("x") === hash32(KOK_TOHUM + "|x")
      };
    })()`);
    ok("hash32 32-bit işaretsiz tamsayı üretiyor", r.hepsiTamsayi);
    ok("300 farklı seans → 300 farklı tohum (çakışma yok)", r.tekil === 300, r.tekil);
    ok("aynı seans her çağrıda aynı tohum", r.kararli);
    ok("nesne girdisi kimliğe indirgeniyor", r.nesneIleAyni);
    ok("boş girdi bozulmuyor", r.bosGirdi);
    ok("kök tohum tohumun İÇİNDE (süs değil)", r.kokKatkili && r.kokEsit);
  }

  console.log("\n3) Kademe aritmetiği — boşluksuz, katlanarak");
  {
    const k = wT.eval(`(() => {
      const M = AKMOD.ebru, KD = M.kademe, out = [];
      for (let n = 0; n < KD.say; n++) { const a = kademeAralik(M, n); out.push([a[0], a[1]]); }
      return { aralik: out, dolum: M.dolum, kat: KD.kat, say: KD.say,
               guncel: AKIS_GUNCEL, surumTanimi: !!AKIS_SURUM[AKIS_GUNCEL] };
    })()`);
    ok("ilk kademe 0'dan başlıyor", k.aralik[0][0] === 0, k.aralik[0][0]);
    ok("ilk kademe dolum süresinde bitiyor", k.aralik[0][1] === k.dolum, k.aralik[0][1]);
    const bitisik = k.aralik.every((a, i) => i === 0 || a[0] === k.aralik[i - 1][1]);
    ok("kademeler bitişik — boşluk ya da çakışma yok", bitisik, JSON.stringify(k.aralik));
    const katli = k.aralik.every((a, i) => i === 0 || Math.abs((a[1] / a[0]) - k.kat) < 1e-9);
    ok("her kademenin süresi bir öncekinin " + k.kat + " katı", katli);
    ok("son kademe 2160 dk'yı (36 saat) aşıyor", k.aralik[k.say - 1][1] >= 2160, k.aralik[k.say - 1][1]);
    ok("güncel akış sürümü tanımlı", k.guncel === 2 && k.surumTanimi);
  }

  console.log("\n4) Eski seans uyumu — damga bugünkü algoritmaya bağlanmıyor");
  {
    const r = wT.eval(`({
      yok: akisYonu({}), eski: akisYonu({ akisV: 1 }), yeni: akisYonu({ akisV: 2 }),
      bilinmeyen: akisYonu({ akisV: 99 }), sessizKayit: akisYonu(null)
    })`);
    ok("damgasız seans v1 (sade) ile çizilir", r.yok === "sade");
    ok("akisV=1 → sade, akisV=2 → ebru", r.eski === "sade" && r.yeni === "ebru");
    ok("bilinmeyen damga çökmek yerine güvenli tarafa düşer", r.bilinmeyen === "sade");
    ok("seans yokken de akış yönü sorulabilir", r.sessizKayit === "sade");
  }

  console.log("\n5) Kum taşı yerleşimi — kalabalık gün, NaN ve çakışma yok");
  {
    let oncekiR = Infinity;
    for (const adet of [1, 2, 4, 8, 12, 16, 20, 25, 30]) {
      const t = wT.eval(`(() => {
        KUM.W = 360; KUM.H = 780;
        const dk = []; for (let i = 0; i < ${adet}; i++) dk.push(25);
        const tas = kumTasUret("2026-08-20", dk);
        let kotu = 0, disari = 0, cakisma = 0, enR = 0, enYakin = Infinity;
        for (let i = 0; i < tas.length; i++) {
          const a = tas[i];
          if (![a.x, a.y, a.r, a.a, a.e, a.tohum].every(v => isFinite(v))) kotu++;
          if (a.x < KUM.W * .11 || a.x > KUM.W * .89 || a.y < KUM.H * .085 || a.y > KUM.H * .685) disari++;
          if (a.r > enR) enR = a.r;
          for (let j = i + 1; j < tas.length; j++) {
            const b = tas[j], d = Math.hypot(a.x - b.x, a.y - b.y);
            if (d < enYakin) enYakin = d;
            if (d < a.r + b.r) cakisma++;
          }
        }
        return { adet: tas.length, kotu, disari, cakisma, enR, enYakin };
      })()`);
      const etiket = adet + " taş";
      ok(etiket + ": hepsi üretildi", t.adet === adet, t.adet);
      ok(etiket + ": NaN/Infinity yok", t.kotu === 0, t.kotu);
      ok(etiket + ": bahçenin ayrılan bandında (kadrana taşmıyor)", t.disari === 0, t.disari);
      ok(etiket + ": taşlar birbirine girmiyor", t.cakisma === 0, t.cakisma);
      ok(etiket + ": irilik sıkıştıkça küçülüyor", t.enR <= oncekiR + 1e-9,
        t.enR.toFixed(2) + " ≤ " + oncekiR.toFixed(2));
      oncekiR = t.enR;
    }

    const d = wT.eval(`(() => {
      KUM.W = 360; KUM.H = 780;
      const a = kumTasUret("2026-08-20", [15, 25, 50]);
      const b = kumTasUret("2026-08-20", [15, 25, 50]);
      const c = kumTasUret("2026-08-20", [15, 25, 50, 25, 25]);
      const e = kumTasUret("2026-08-21", [15, 25, 50]);
      return {
        ayni: JSON.stringify(a) === JSON.stringify(b),
        onEkKorundu: JSON.stringify(c.slice(0, 3)) === JSON.stringify(a),
        gunFarkli: JSON.stringify(e) !== JSON.stringify(a),
        dkBuyudukceBuyuk: kumTasUret("2026-08-20", [15])[0].r < kumTasUret("2026-08-20", [90])[0].r
      };
    })()`);
    ok("aynı gün + aynı dakikalar → birebir aynı yerleşim", d.ayni);
    ok("yeni taş eklenince ESKİ taşlar yerinden oynamıyor", d.onEkKorundu);
    ok("başka gün başka bahçe (gün tohumu işliyor)", d.gunFarkli);
    ok("uzun seansın taşı daha iri", d.dkBuyudukceBuyuk);
  }

  console.log("\n6) Boş gün — bahçe kurulmuyor diye çökmüyor");
  {
    const r = wT.eval(`(() => {
      KUM.W = 360; KUM.H = 780;
      return { tas: kumTasUret("2026-08-20", []).length,
               olay: kumOlaylar("2026-08-20").length,
               seans: kumSeanslar("2026-08-20").length };
    })()`);
    ok("taş listesi boşken taş üretilmiyor", r.tas === 0);
    ok("seanssız günün olayı yok", r.olay === 0);
    ok("seanssız günün pomodorosu yok", r.seans === 0);
  }

  console.log("\n7) Bahçe formunun altı yüzü — plan ve alan makul kalıyor");
  {
    const gunler = formGunu();
    const turler = Object.keys(gunler);
    ok("altı bahçe biçiminin tamamı üretilebiliyor", turler.length === 6, turler.join(","));
    for (const tur of turler) {
      const gun = gunler[tur];
      const bitTs = new Date(gun + "T12:00:00").getTime();
      const se = seans("bicim", bitTs, 25, [], "pomodoro", 25);
      const r = wT.eval(`(() => {
        const se = ${JSON.stringify(se)};
        S.sessions = [se];
        KUM.W = 360; KUM.H = 780; KUM.hazir = false; KUM.imza = "";
        const yeni = kumKur(${JSON.stringify(gun)}, ${bitTs});
        let bozuk = 0;
        for (let i = 0; i < KUM.G.length; i += 41) if (!isFinite(KUM.G[i])) bozuk++;
        const ciz = kumCizgiler(kumOlaylar(${JSON.stringify(gun)}, ${bitTs}));
        return { tur: KUM.bicim.tur, yeni, maxF: KUM.maxF, plan: KUM.plan.length,
                 bozuk, tas: KUM.taslar.length, taze: ciz.filter(c => c.taze).length,
                 tekrar: kumKur(${JSON.stringify(gun)}, ${bitTs}) };
      })()`);
      const e = tur + " günü";
      ok(e + ": biçim gerçekten kuruldu", r.tur === tur && r.yeni === true, r.tur);
      ok(e + ": tek pomodoro = tek taş", r.tas === 1, r.tas);
      ok(e + ": alan derinliği sonlu ve makul", isFinite(r.maxF) && r.maxF > 0 && r.maxF < 1500, r.maxF);
      ok(e + ": tırmık planı makul", r.plan >= 2 && r.plan <= 400, r.plan);
      ok(e + ": alan ızgarasında bozuk sayı yok", r.bozuk === 0, r.bozuk);
      ok(e + ": tam geçiş bahçenin tamamını tarar", r.taze === r.plan, r.taze + "/" + r.plan);
      ok(e + ": aynı gün ikinci kurulum gereksiz (imza tutuyor)", r.tekrar === false);
    }
  }

  console.log("\n8) Tırmık ilerlemesi — ara verdikçe geri gitmiyor");
  {
    const r = wT.eval(`(() => {
      KUM.W = 360; KUM.H = 780;
      KUM.tohum = hash32(KOK_TOHUM + "|kumbahce|2026-08-20");
      KUM.bicim = kumBicim(KUM.tohum);
      KUM.taslar = kumTasUret("2026-08-20", [25]);
      KUM.ara = 46 * (KUM.H / 780);
      kumAlanKur();
      KUM.ara = Math.min(KUMMOD.araMax, Math.max(KUMMOD.araMin, KUM.maxF / KUMMOD.bant)) * KUM.bicim.araKat * (KUM.H / 780);
      kumAlanKur();
      kumPlanKur();
      const N = KUM.plan.length, seri = [];
      for (let adim = 0; adim <= 10; adim++) {
        const ciz = kumCizgiler([{ sure: (25 * adim) / 10, target: 25, mola: false, seansIdx: 0, ended: false }]);
        seri.push(ciz.filter(c => c.taze).length);
      }
      return { N, seri };
    })()`);
    const artan = r.seri.every((v, i) => i === 0 || v >= r.seri[i - 1]);
    ok("geçen süre arttıkça taranan çizgi azalmıyor", artan, r.seri.join(" "));
    ok("başlangıçta hiç çizgi yok", r.seri[0] === 0, r.seri[0]);
    ok("25 dk sonunda planın tamamı taranmış", r.seri[10] === r.N, r.seri[10] + "/" + r.N);
  }

  console.log("\n9) Rüzgar ve mola kademesi — eşikler sözleşmeye uyuyor");
  {
    /* Kademe 0 = rüzgar yok: kısa mola hiç olay üretmez, kum düz kalır. */
    for (const [dk, bek] of [[5, 0], [9, 0], [10, 1], [19, 1], [20, 2], [29, 2], [30, 3]]) {
      const se = seans("mola" + dk, T, 60, [[5, 5 + dk]], "pomodoro", 25);
      const k = wT.molaKademeleri(se);
      const uyuyor = bek === 0 ? k.length === 0 : (k.length === 1 && k[0].kademe === bek);
      ok(dk + " dk mola → " + (bek === 0 ? "rüzgar yok" : "kademe " + bek), uyuyor, JSON.stringify(k));
    }
    const r = wT.eval(`(() => {
      S.sessions = [];
      const uzun = ${JSON.stringify(seans("uzun", TB, 60, [[5, 35]], "pomodoro", 25))};
      const orta = ${JSON.stringify(seans("orta", TB, 60, [[5, 25]], "pomodoro", 25))};
      const korumaOncesi = { uzun: molaKirar(uzun), orta: molaKirar(orta) };
      const bit = ${TB};
      for (let i = 0; i < 3; i++) {
        S.sessions.push(${JSON.stringify(seans("tam0", TB, 25, [], "pomodoro", 25))});
      }
      const eksik = ${JSON.stringify(seans("eksik", TB, 60, [], "pomodoro", 25))};
      eksik.endedAt = eksik.startedAt + 20 * 60000;
      eksik.events = [{ type: "start", at: eksik.startedAt }, { type: "end", at: eksik.endedAt }];
      return {
        korumaOncesi,
        koruma: fudoshinKoruma(dayKey(${TB})),
        sonra: { uzun: molaKirar(uzun), orta: molaKirar(orta) },
        vaat: { eksik: tasKirikMi(eksik), tamam: tasKirikMi(S.sessions[0]) }
      };
    })()`);
    ok("30 dk mola taşı kırar", r.korumaOncesi.uzun === true);
    ok("20 dk mola taşı kırmaz (kum dağılır, taş durur)", r.korumaOncesi.orta === false);
    ok("üç tamamlanmış pomodoro fudōshin korumasını açar", r.koruma === true);
    ok("koruma açıkken uzun mola taşı kıramaz", r.sonra.uzun === false && r.sonra.orta === false);
    ok("vaadini tutmayan seans kırık taş", r.vaat.eksik === true);
    ok("vaadini tutan seans sağlam taş", r.vaat.tamam === false);
  }

  console.log("\n10) Altı saatlik seans — kademeler açılıyor, bütçe taşmıyor");
  {
    const kurulum = wU.eval(`(() => {
      akisTuval();
      window._sePin = { id: "pinli", startedAt: Date.now() - 60 * 60000, endedAt: null,
        dayKey: dayKey(Date.now()), mode: "stopwatch", target: 0,
        events: [{ type: "start", at: Date.now() - 60 * 60000 }], awayMs: 0,
        unconfirmedOk: false, edited: false, editedAt: Date.now(), akisV: 2, tohum: 123456789 };
      akisBaslat(window._sePin);
      return { W: AK.w, H: AK.h };
    })()`);
    ok("tuval ekranın en-boy oranıyla kuruldu", kurulum.W > 0 && kurulum.H > 0, JSON.stringify(kurulum));
    await bekle(250);
    ok("kayıtlı tohum varsa o kullanılıyor (kayıt pinli)", wU.eval("AK.tohum") === 123456789, wU.eval("AK.tohum"));

    wU.eval(`(() => {
      window._se6 = { id: "uzun6", startedAt: Date.now() - 360 * 60000, endedAt: null,
        dayKey: dayKey(Date.now()), mode: "stopwatch", target: 0,
        events: [{ type: "start", at: Date.now() - 360 * 60000 }], awayMs: 0,
        unconfirmedOk: false, edited: false, editedAt: Date.now(), akisV: 2 };
      S.sessions.push(window._se6); S.active = "uzun6";
      akisBaslat(window._se6);
    })()`);
    await bekle(300);
    const t0 = Date.now();
    wU.eval("akisIsle()");
    const sn = Date.now() - t0;

    const r = wU.eval(`(() => {
      const katmanlar = [AK.serit].concat(AK.ek.filter(Boolean).map(x => x.serit));
      let kotu = 0, nokta = 0;
      for (const s of katmanlar) for (const p of s) for (let i = 0; i < p.length; i += 2) {
        nokta++; if (!isFinite(p[i]) || !isFinite(p[i + 1])) kotu++;
      }
      return { hazir: AK.hazir, kapali: AK.kapali, ekKapali: AK.ekKapali,
               seviye: AK.ek.filter(Boolean).length, cizili: AK.ek.map(x => (x ? x.ciz : 0)),
               serit: AK.serit.length, nokta, kotu, tohum: AK.tohum, ciz: AK.ciz,
               beklenen: seansTohumu("uzun6"), butce: AKMOD.ebru.kademe.butce };
    })()`);
    /* eski ebru akış motoru bilerek kapalı (masa tuvali aldı); veri modeli ve kademeler yine de doğrulanır */
    ok("desen hazır (veri modeli çalışıyor)", r.hazir === true);
    ok("tohumu olmayan eski seans kimliğinden türetiliyor", r.tohum === r.beklenen);
    ok("6 saatlik seans iki ince kademe açtı", r.seviye === 2, r.seviye);
    ok("her kademe çizildi (biri boş kalmadı)", r.ciz > 0 && r.cizili.every(v => v > 0), JSON.stringify(r.cizili));
    ok("kademe bütçesi aşılmadı", r.ekKapali === false);
    ok("şerit koordinatlarının tamamı sonlu", r.kotu === 0, r.kotu + "/" + r.nokta + " nokta bozuk");
    ok("6 saatlik desen bütçe içinde hesaplandı", sn < 5000, sn + " ms (bütçe " + r.butce + " ms/kademe)");

    /* Negatif denetim: bütçe imkânsız kılınırsa desen durur, uygulama ayakta kalır. */
    wU.eval("AKMOD.ebru.kademe.butce = -1; AK.ek = []; AK.ekKapali = false; AK.ciz = 0;");
    wU.eval("akisIsle()");
    const b = wU.eval("({ ekKapali: AK.ekKapali, seviye: AK.ek.filter(Boolean).length, hazir: AK.hazir, ciz: AK.ciz })");
    ok("bütçe aşılırsa ince kademelerden vazgeçilir", b.ekKapali === true && b.seviye === 0, JSON.stringify(b));
    ok("vazgeçse bile temel desen ve uygulama ayakta", b.hazir === true && b.ciz > 0, JSON.stringify(b));
    wU.eval("AKMOD.ebru.kademe.butce = 900;");
  }

  console.log("\n11) Sayfa hiçbir çalışma zamanı hatası düşürmedi");
  ok("birinci sayfa hatasız", wT._hatalar.length === 0, wT._hatalar.join(" | "));
  ok("ikinci sayfa hatasız", wU._hatalar.length === 0, wU._hatalar.join(" | "));

  console.log("\n" + pass + " geçti, " + fail + " kaldı");
  process.exit(fail ? 1 : 0);
})().catch(e => { console.error(e); process.exit(1); });
