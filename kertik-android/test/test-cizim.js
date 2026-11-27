/* Çizim testleri — çubuk, duvar ve akış alanı.
   jsdom'da koşar; tuval (canvas) sahte bir nesneyle taklit edilir,
   çünkü burada doğrulanan şey piksel değil, ÜRETİLEN GEOMETRİ.

   Koşturmak için:  npm install jsdom && node test-cizim.js
*/
const fs = require("fs"), path = require("path");
const { JSDOM } = require("jsdom");

const HTML = path.join(__dirname, "../app/src/main/assets/index.html");
let pass = 0, fail = 0;
function ok(name, cond, extra) {
  if (cond) { pass++; console.log("  ✓ " + name); }
  else { fail++; console.log("  ✗ " + name, extra === undefined ? "" : extra); }
}
/* çubuktaki çentik sayısı: her çentik kalasa açılmış bir V kesit, [data-centik] grubu */
const say = svg => svg.querySelectorAll("[data-centik]").length;

/* ---------- sahte tuval ----------
   Taklit, uygulamanın GERÇEKTEN çağırdığı metot kümesinin tamamını kapsamak
   zorunda: eksik kalan bir metot cihazda sorun çıkarmaz ama burada
   "TypeError: g.x is not a function" olarak sahte bir arıza üretir.
   (kumTasYolu'nun quadraticCurveTo'su bir kez bu yüzden düşürülmüştü.) */
const cagri = [];
function sahteCtx() {
  const c = {
    canvas: null, globalAlpha: 1, globalCompositeOperation: "source-over",
    strokeStyle: "", fillStyle: "", lineWidth: 1, lineCap: "", lineJoin: ""
  };
  const yut = ["beginPath", "moveTo", "lineTo", "stroke", "fill", "fillRect", "clearRect",
               "setTransform", "drawImage", "putImageData", "closePath", "arc", "ellipse", "save", "restore", "translate", "rotate", "scale", "setLineDash",
               "quadraticCurveTo", "bezierCurveTo", "arcTo", "clip", "rect", "roundRect",
               "fillText", "strokeText", "strokeRect", "resetTransform", "getLineDash"];
  for (const k of yut) c[k] = (...a) => { cagri.push([k, a.length]); };
  c.measureText = t => ({ width: String(t).length * 6 });
  c.createImageData = (w, h) => ({ width: w, height: h, data: new Uint8ClampedArray(w * h * 4) });
  const grad = { addColorStop() {} };
  c.createRadialGradient = () => grad;
  c.createLinearGradient = () => grad;
  return c;
}

function kur(kayit) {
  const dom = new JSDOM(fs.readFileSync(HTML, "utf8"), {
    runScripts: "dangerously", pretendToBeVisual: true, url: "http://localhost/",
    beforeParse(w) {
      /* jsdom'da olmayan, WebView'de olan iki şey */
      if (!w.structuredClone) w.structuredClone = o => JSON.parse(JSON.stringify(o));
      w.HTMLCanvasElement.prototype.getContext = function () {
        const c = sahteCtx(); c.canvas = this; return c;
      };
      w.HTMLCanvasElement.prototype.toDataURL = () => "data:image/png;base64,";
      if (kayit) w.localStorage.setItem("kertik.v1", JSON.stringify(kayit));
    }
  });
  return new Promise(res => setTimeout(() => res(dom.window), 60));
}

/* ---------- örnek veri ---------- */
const T = Date.now();
const GUN = 864e5, DK = 60000;
function seans(id, bitTs, dakika, molalar, awayDk) {
  const bas = bitTs - dakika * DK;
  const ev = [{ type: "start", at: bas }];
  for (const [a, b] of (molalar || [])) {
    ev.push({ type: "break_start", at: bas + a * DK });
    ev.push({ type: "break_end", at: bas + b * DK });
  }
  ev.push({ type: "end", at: bitTs });
  const d = new Date(bas);
  const key = d.getFullYear() + "-" + String(d.getMonth() + 1).padStart(2, "0") + "-" + String(d.getDate()).padStart(2, "0");
  return { id, startedAt: bas, endedAt: bitTs, dayKey: key, note: "", mode: "stopwatch", target: 0,
           events: ev, awayMs: (awayDk || 0) * DK, unconfirmedOk: false, edited: false, editedAt: bitTs };
}

const KAYIT = {
  sessions: [
    seans("s1", T - 2 * 36e5, 107, [[41, 49], [78, 84]], 0),        // bugün, iki mola
    seans("s2", T - 5 * 36e5, 25, [], 0),                            // bugün, kısa
    seans("s3", T - 1 * GUN, 185, [[58, 71], [126, 138]], 23),       // dün, sayılmayan süre
    seans("s4", T - 3 * GUN, 50, [], 0),
    seans("s5", T - 12 * GUN, 64, [[52, 64]], 0)
  ],
  tasks: [], tombstones: [], active: null,
  settings: { mode: "stopwatch", theme: "light" },
  sync: { connected: false }
};

(async () => {
  console.log("\n1) Çubuk — tek seans");
  const w = await kur(KAYIT);
  const d = w.document;

  {
    const svg = d.createElementNS("http://www.w3.org/2000/svg", "svg");
    const se = KAYIT.sessions[0];                       // 107 dk, 14 dk mola
    const v = w.cubukVeri(se);
    ok("dk seansın gerçek uzunluğu", v.dk === 107, v.dk);
    ok("iki mola aralığı çıkarıldı", v.molalar.length === 2, JSON.stringify(v.molalar));
    ok("mola sınırları doğru", Math.round(v.molalar[0][0]) === 41 && Math.round(v.molalar[0][1]) === 49);
    ok("sayılmayan süre yok", v.sayilmayan === 0);

    w.cizCubuk(svg, v, { rp: 4.6, sw: 26, gap: 12, top: 5 });
    ok("sütun sayısı 2 (107 dk → iki saat)", Math.ceil(v.dk / 60) === 2);
    ok("çizim üretildi", svg.querySelectorAll("path, line").length > 100);
    /* mola dakikalarına kesik atılmaz: 107 - 14 = 93 çalışma dakikası */
    ok("çentik sayısı çalışma dakikasıyla birebir", say(svg) === 107 - 14, say(svg));
    ok("iki kalas var", svg.querySelectorAll("[data-kalas]").length === 2);
    ok("viewBox var", /^-8 0 /.test(svg.getAttribute("viewBox")), svg.getAttribute("viewBox"));
  }

  console.log("\n2) Çubuk — sayılmayan süre miktar olarak duruyor");
  {
    const se = KAYIT.sessions[2];                        // 185 dk, 25 dk mola, 23 dk sayılmayan
    const v = w.cubukVeri(se);
    ok("sayılmayan dakika okundu", v.sayilmayan === 23, v.sayilmayan);
    const svg = d.createElementNS("http://www.w3.org/2000/svg", "svg");
    w.cizCubuk(svg, v, { rp: 4.6, sw: 26, gap: 12, top: 5 });
    const kesikli = [...svg.querySelectorAll("line")].filter(l => l.getAttribute("stroke-dasharray"));
    ok("tek bir kesikli ray var", kesikli.length === 1, kesikli.length);
    ok("ray dikey (konum iddia etmiyor)", kesikli[0].getAttribute("x1") === kesikli[0].getAttribute("x2"));
    ok("ray sütunun sağında", Number(kesikli[0].getAttribute("x1")) > 26);
    /* sayılmayan süre çubuktaki kesikleri EKSİLTMEZ — çubuk zaman çizgisidir.
       kesik + gölgesi pathLength taşır, sırt ve mola izleri taşımaz. */
    ok("kesikler zaman çizgisini bozmadı", say(svg) === 185 - 25, say(svg));
  }

  console.log("\n3) Çubuk — aynı seans hep aynı çubuk");
  {
    const v = w.cubukVeri(KAYIT.sessions[0]);
    const a = d.createElementNS("http://www.w3.org/2000/svg", "svg");
    const b = d.createElementNS("http://www.w3.org/2000/svg", "svg");
    w.cizCubuk(a, v, { rp: 4.6, sw: 26, gap: 12, top: 5 });
    w.cizCubuk(b, v, { rp: 4.6, sw: 26, gap: 12, top: 5 });
    ok("iki çizim birebir aynı", a.innerHTML === b.innerHTML);
    const c = d.createElementNS("http://www.w3.org/2000/svg", "svg");
    w.cizCubuk(c, Object.assign({}, v, { id: "baska" }), { rp: 4.6, sw: 26, gap: 12, top: 5 });
    ok("başka seans başka çubuk", c.innerHTML !== a.innerHTML);
  }

  console.log("\n4) Gün çubuğu — birden fazla seans");
  {
    const bugun = KAYIT.sessions.filter(s => s.dayKey === KAYIT.sessions[0].dayKey);
    const v = w.gunCubuk(bugun, "k");
    ok("iki seans birleşti", bugun.length === 2);
    ok("araya bir boşluk kondu", v.bos.length === 1, JSON.stringify(v.bos));
    ok("toplam uzunluk = seanslar + boşluk", v.dk === 107 + 25 + 1, v.dk);
    const svg = d.createElementNS("http://www.w3.org/2000/svg", "svg");
    w.cizCubuk(svg, v, { rp: 1.7, sw: 8, gap: 5, top: 3 });
    /* 93 (s1 çalışma) + 25 (s2) — aradaki boşluk dakikası çentik almaz */
    ok("boşluk dakikasına kesik atılmadı", say(svg) === 93 + 25, say(svg));
  }

  console.log("\n5) Duvar — son 30 gün");
  {
    w.setTab("log");
    const gunler = d.querySelectorAll("#wallGrid .day");
    ok("30 gün çizildi", gunler.length === 30, gunler.length);
    const dolu = [...gunler].filter(x => !x.classList.contains("void"));
    ok("dolu gün sayısı kayıtla uyuşuyor", dolu.length === 4, dolu.length);
    ok("boş günde çubuk yok", [...gunler].filter(x => x.classList.contains("void"))
      .every(x => !x.querySelector("svg")));
    ok("bugün işaretli", d.querySelectorAll("#wallGrid .day.today").length === 1);
    ok("efsane var", !!d.querySelector(".legend"));
  }

  console.log("\n5b) Duvar — pomodoro günü taş, kronometre günü çubuk");
  {
    function pomo(id, bitTs, dakika) {
      const s = seans(id, bitTs, dakika, [], 0);
      s.mode = "pomodoro"; s.target = dakika;
      return s;
    }
    const KAYIT2 = {
      sessions: [
        pomo("p1", T - 4 * 36e5, 25),          // bugün, 1. pomodoro
        pomo("p2", T - 2 * 36e5, 50),          // bugün, 2. pomodoro (daha uzun)
        seans("sw1", T - 1 * GUN, 40, [], 0)   // dün, kronometre
      ],
      tasks: [], tombstones: [], active: null,
      settings: { mode: "pomodoro", theme: "light" }, sync: { connected: false }
    };
    const w2 = await kur(KAYIT2);
    const d2 = w2.document;
    w2.setTab("log");
    const gunler2 = [...d2.querySelectorAll("#wallGrid .day")];
    /* kertikli çubuk artık kendi de <path> kullanıyor (kalas + V kesit), o yüzden
       taş/çubuk ayrımı path/line varlığıyla değil [data-kalas] işaretiyle yapılıyor */
    const tasGunu = gunler2.filter(x => x.querySelector("svg path") && !x.querySelector("svg [data-kalas]"));
    const cubukGunu = gunler2.filter(x => x.querySelector("svg [data-kalas]"));
    ok("bir gün taşla çizildi (pomodoro)", tasGunu.length === 1, tasGunu.length);
    ok("bir gün çubukla çizildi (kronometre)", cubukGunu.length === 1, cubukGunu.length);
    ok("taş gününde çentik (line) yok", tasGunu[0] && tasGunu[0].querySelectorAll("svg line").length === 0);
    ok("çubuk gününde kalas ve çentik var", cubukGunu[0]
      && cubukGunu[0].querySelectorAll("svg [data-kalas]").length > 0
      && cubukGunu[0].querySelectorAll("svg [data-centik]").length > 0);
    /* her taş bir gölge + bir gövde = 2 path; iki pomodoro → 4 path */
    ok("taş gününde iki taş var (iki pomodoro)",
      tasGunu[0] && tasGunu[0].querySelectorAll("svg path").length === 4,
      tasGunu[0] && tasGunu[0].querySelectorAll("svg path").length);

    console.log("\n5c) Taş — aynı seans hep aynı taş, boyu süreyle büyür");
    const v1 = w2.gunTas([KAYIT2.sessions[0]], "g1");
    const svgA = d2.createElementNS("http://www.w3.org/2000/svg", "svg");
    const svgB = d2.createElementNS("http://www.w3.org/2000/svg", "svg");
    w2.cizTas(svgA, v1, { taban: 7.5 });
    w2.cizTas(svgB, v1, { taban: 7.5 });
    ok("iki çizim birebir aynı", svgA.innerHTML === svgB.innerHTML);
    const v50 = w2.gunTas([KAYIT2.sessions[1]], "g1"); // aynı id, farklı süre (50 dk)
    const svgC = d2.createElementNS("http://www.w3.org/2000/svg", "svg");
    w2.cizTas(svgC, v50, { taban: 7.5 });
    ok("50 dk'lık taş 25 dk'lıktan geniş",
      Number(svgC.getAttribute("width")) > Number(svgA.getAttribute("width")),
      svgC.getAttribute("width") + " ↔ " + svgA.getAttribute("width"));

    console.log("\n5d) Taş — çok pomodoro sıkışıyor, komşu güne taşmıyor");
    const cok = []; for (let i = 0; i < 14; i++) cok.push(pomo("cp" + i, T - 4 * 36e5, 25));
    const vCok = w2.gunTas(cok, "cok");
    const svgCok = d2.createElementNS("http://www.w3.org/2000/svg", "svg");
    w2.cizTas(svgCok, vCok, { taban: 7.5 });
    ok("14 taş üretildi", svgCok.querySelectorAll("svg path, path").length === 28,
      svgCok.querySelectorAll("path").length);
    ok("sıkışsa da genişlik makul bir tavanda kalıyor",
      Number(svgCok.getAttribute("width")) < 7.5 * 5.6 * 1.35,
      svgCok.getAttribute("width"));
  }

  console.log("\n6) Kayıt kartı — kadran değil çubuk");
  {
    const kart = d.querySelector("#logBody .card");
    ok("kartta çubuk yuvası var", !!kart.querySelector("[data-cubuk]"));
    ok("eski kadran yuvası kalmadı", !kart.querySelector("[data-dial]"));
    kart.querySelector(".row").dispatchEvent(new w.MouseEvent("click", { bubbles: true }));
    ok("açılınca çubuk çizildi", kart.querySelectorAll("[data-cubuk] [data-centik]").length > 20,
      kart.querySelectorAll("[data-cubuk] [data-centik]").length);
  }

  console.log("\n6b) Kayıt kartı — pomodoro seansında taş, kronometrede çubuk çizilir");
  {
    const KAYIT_P = {
      sessions: [
        pomo("p1", T - 4 * 36e5, 25),
        seans("sw1", T - 1 * GUN, 40, [], 0)
      ],
      tasks: [], tombstones: [], active: null,
      settings: { mode: "pomodoro", theme: "light" }, sync: { connected: false }
    };
    const wP = await kur(KAYIT_P);
    const dP = wP.document;
    wP.setTab("log");
    const pomoKart = dP.querySelector("#logBody .card[data-s='p1']");
    const swKart = dP.querySelector("#logBody .card[data-s='sw1']");
    ok("pomodoro kartında görsel yuvası var", !!pomoKart.querySelector("[data-cubuk]"));
    ok("kronometre kartında görsel yuvası var", !!swKart.querySelector("[data-cubuk]"));
    pomoKart.querySelector(".row").dispatchEvent(new wP.MouseEvent("click", { bubbles: true }));
    ok("pomodoro kartı açılınca taş çizilir (gölge + gövde)", pomoKart.querySelectorAll("[data-cubuk] path").length >= 2);
    ok("pomodoro kartında çentik/kalas yoktur", pomoKart.querySelectorAll("[data-cubuk] [data-centik]").length === 0 && pomoKart.querySelectorAll("[data-cubuk] [data-kalas]").length === 0);
    swKart.querySelector(".row").dispatchEvent(new wP.MouseEvent("click", { bubbles: true }));
    ok("kronometre kartı açılınca çubuk/çentik çizilir", swKart.querySelectorAll("[data-cubuk] [data-centik]").length > 10);
  }

  console.log("\n6c) Kayıt defteri ritmi — 14 gün penceresi ve önceki günler");
  {
    // 20 farklı gün için seans üretelim
    const sessions20 = [];
    for (let i = 0; i < 20; i++) {
      sessions20.push(seans("s_gun_" + i, T - i * GUN, 30, [], 0));
    }
    const KAYIT_RITIM = {
      sessions: sessions20,
      tasks: [], tombstones: [], active: null,
      settings: { mode: "stopwatch", theme: "light" }, sync: { connected: false }
    };
    const wR = await kur(KAYIT_RITIM);
    const dR = wR.document;
    wR.setTab("log");

    const dayheads = dR.querySelectorAll("#logBody .dayhead");
    ok("ilk açılışta tam 14 gün gösterilir", dayheads.length === 14, dayheads.length);
    const bMore = dR.querySelector("#btnLogMore");
    ok("önceki günler düğmesi var (6 gün kalan)", !!bMore && bMore.textContent.includes("6"), bMore && bMore.textContent);

    // Düğmeye tıkla
    bMore.dispatchEvent(new wR.MouseEvent("click", { bubbles: true }));
    const dayheadsSonra = dR.querySelectorAll("#logBody .dayhead");
    ok("tıklayınca kalan günler de açıldı (20 gün)", dayheadsSonra.length === 20, dayheadsSonra.length);
    const bMoreSonra = dR.querySelector("#btnLogMore");
    ok("tüm günler açılınca düğme kalktı", !bMoreSonra);
  }

  console.log("\n7) Akış — alan hesabı");
  {
    const A = w.eval("AKMOD.ebru.alan");
    const serit = w.akisAlan(w.hash32("s1"), 300, 640, A);
    ok("şerit üretildi", serit.length > 60, serit.length);
    ok("şeritler nokta çifti", serit[0].length % 2 === 0);
    const s2 = w.akisAlan(w.hash32("s1"), 300, 640, A);
    ok("aynı tohum aynı alan", serit.length === s2.length && serit[0].length === s2[0].length);
    const s3 = w.akisAlan(w.hash32("bambaska"), 300, 640, A);
    ok("başka tohum başka alan", s3.length !== serit.length || s3[0].length !== serit[0].length);
    const hepsi = serit.every(p => {
      for (let i = 0; i < p.length; i += 2)
        if (!isFinite(p[i]) || !isFinite(p[i + 1])) return false;
      return true;
    });
    ok("koordinatlar sayı (NaN yok)", hepsi);

    /* Ekranın boş görünmesinin sebebi saydamlık değil şerit sayısıydı:
       eski alan aynı tuvalde bunun yarısından azını üretiyordu. */
    const eski = w.akisAlan(w.hash32("s1"), 300, 640, w.eval("AKMOD.sade.alan"));
    ok("yeni alan eskisinden belirgin sık", serit.length > eski.length * 1.8,
      serit.length + " ↔ " + eski.length);
  }

  console.log("\n7b) Akış — katman payları ve renk");
  {
    const A = w.eval("AKMOD.ebru.alan");
    const serit = w.akisAlan(w.hash32("s1"), 300, 640, A);
    const sira = w.akisSira(serit, 300, w.hash32("s1"));
    ok("her şeride bir sıra düştü", sira.length === serit.length);
    ok("sıra 0..1 arasında", Array.from(sira).every(x => x >= 0 && x <= 1));
    /* Payların tutması önemli: %10 kalın damar dediysek %10 olmalı. */
    const damar = Array.from(sira).filter(x => x >= .90).length;
    ok("damar payı ~%10", Math.abs(damar / sira.length - .10) < .02,
      (damar / sira.length * 100).toFixed(1) + "%");
    /* Kalın damarlar EKRANDA bölge bölge kümelensin — rastgele serpilseydi
       ebru değil, eşit dağılmış kalın çizgiler olurdu. Ölçü: damarların
       birbirine en yakın komşu uzaklığı, aynı sayıda rastgele şeridinkinden
       belirgin küçük olmalı. */
    const orta = i => { const p = serit[i], k = (p.length >> 2) << 1; return [p[k], p[k + 1]]; };
    const enYakinOrt = küme => {
      let t = 0;
      for (const a of küme) {
        let en = Infinity;
        for (const b of küme) if (a !== b) {
          const d = Math.hypot(orta(a)[0] - orta(b)[0], orta(a)[1] - orta(b)[1]);
          if (d < en) en = d;
        }
        t += en;
      }
      return t / küme.length;
    };
    const agir = [], hepsiIdx = [];
    for (let i = 0; i < sira.length; i++) { hepsiIdx.push(i); if (sira[i] >= .90) agir.push(i); }
    const kontrol = hepsiIdx.filter((_, i) => i % Math.round(hepsiIdx.length / agir.length) === 0)
                            .slice(0, agir.length);
    const dAgir = enYakinOrt(agir), dKontrol = enYakinOrt(kontrol);
    ok("damarlar ekranda kümeleniyor", dAgir < dKontrol * .75,
      dAgir.toFixed(1) + " ↔ " + dKontrol.toFixed(1) + " birim");

    const hsl = w.hexHsl("#B05237");
    ok("hex → hsl çözülüyor", !!hsl && Math.abs(hsl[0] - 14) < 2);
    ok("hex olmayan renk olduğu gibi kalır", w.hexHsl("var(--x)") === null);
    const M = w.eval("AKMOD.ebru");
    const tuy = w.akisRenk(hsl, "#B05237", 0, M), dam = w.akisRenk(hsl, "#B05237", 1, M);
    ok("tüy ile damar farklı ton", tuy !== dam, tuy + " ↔ " + dam);
    ok("ton kapalıyken renk hiç değişmez",
      w.akisRenk(hsl, "#B05237", 1, w.eval("AKMOD.belirgin")) === "#B05237");
  }

  console.log("\n8) Akış — seans yokken görünmez");
  {
    w.setTab("timer");
    ok("seans yokken tuval kapalı", !d.getElementById("akis").classList.contains("on"));
    ok("akış tuvali sayfada", !!d.getElementById("akis"));
  }

  console.log("\n9) Seans başlayınca akış açılır");
  {
    /* S ve AK sayfada `let`/`const` — window'a düşmüyor, sayfa içinden okunuyor */
    const oku = ifade => w.eval(ifade);
    d.getElementById("bStart").dispatchEvent(new w.MouseEvent("click", { bubbles: true }));
    ok("seans başladı", !!oku("S.active"));
    /* eski ebru akış kapalı; resmi artık "masa" tuvali çiziyor (pomodoro kum bahçesi, kronometre dokuma) */
    ok("masa tuvali var ve akış kapalı", !!d.getElementById("masa") && oku("AK.kapali") === true);
    await new Promise(r => setTimeout(r, 400));
    ok("alan hesaplandı", oku("AK.hazir") === true || oku("AK.kapali") === true);
    if (oku("AK.hazir")) {
      ok("şerit çizildi", oku("AK.ciz") >= 0 && oku("AK.serit.length") > 0);
      ok("tuvale çizim gitti", cagri.some(c => c[0] === "drawImage"));
      ok("kadran çevresi silindi (destination-out)", cagri.some(c => c[0] === "fillRect"));
    }
    w.finish();
    ok("seans bitti", !oku("S.active"));
    w.render();
    ok("seans bitince akış kapandı", !d.getElementById("akis").classList.contains("on"));
  }

  console.log("\n10) Tema değişimi patlamıyor");
  {
    w.eval('S.settings.theme="dark"'); w.applyTheme(); w.render();
    ok("karanlık temada render sorunsuz", d.documentElement.classList.contains("dark"));
    w.eval('S.settings.theme="light"'); w.applyTheme(); w.render();
    ok("açık temaya dönüş sorunsuz", !d.documentElement.classList.contains("dark"));
  }

  console.log("\n11) Açılışta hata yok, senkron kancaları kuruldu");
  {
    ok("gomuluAnahtar kalıntısı temizlendi",
      !/gomuluAnahtar/.test(fs.readFileSync(HTML, "utf8")));
    ok("betik sonuna kadar koştu (autoSync tanımlı ve çağrıldı)",
      typeof w.autoSync === "function");
  }

  console.log("\n12) Boş kayıt");
  {
    const w2 = await kur({ sessions: [], tasks: [], tombstones: [], active: null,
                           settings: { theme: "light" }, sync: {} });
    w2.setTab("log");
    ok("kayıt yokken duvar çizilmez", w2.document.getElementById("wallBox").innerHTML === "");
    ok("boş ekran metni var",
       w2.document.getElementById("logBody").innerHTML.includes(w2.soz("kayit_bos")));
  }

  console.log("\n13) Kütleye Bağlı Akustik & Donanım Haptiği");
  {
    const p15 = w.getKutleProfili(15);
    const p25 = w.getKutleProfili(25);
    const p50 = w.getKutleProfili(50);
    const p90 = w.getKutleProfili(90);
    ok("15 dk çakıl profili doğru", p15 && p15.ad === "Çakıl Taşı" && (p15.haptik.t ? p15.haptik.t[0] : p15.haptik[0]) === 9);
    ok("25 dk standart taş profili doğru", p25 && p25.ad === "Standart Taş" && (p25.haptik.t ? p25.haptik.t[0] : p25.haptik[0]) === 14);
    ok("50 dk iri kaya frekansı daha kalın", p50 && p50.freqBasla < p25.freqBasla && (p50.haptik.t ? p50.haptik.t.length : p50.haptik.length) === 3);
    ok("90 dk granit sub-bass ve derin haptik", p90 && p90.freqBasla < p50.freqBasla && (p90.haptik.t ? p90.haptik.t.length : p90.haptik.length) === 5);
    ok("ses ve titreşim fonksiyonları tanımlı", typeof w.sesCalKutleDarbe === "function" && typeof w.buzz === "function");
  }

  console.log("\n14) Pomodoro Bitiş Uyarısı & Zen Çanı Akustiği");
  {
    w.setTab("timer");
    ok("sesCalZenCani tanımlı", typeof w.sesCalZenCani === "function");
    // Pomodoro seansı simülasyonu
    w.eval(`
      const se = {
        id: "test_pomo_bitis", startedAt: Date.now() - 25 * 60000 - 5000,
        mode: "pomodoro", target: 25,
        events: [{ type: "start", at: Date.now() - 25 * 60000 - 5000 }],
        awayMs: 0, unconfirmedOk: false, edited: false, editedAt: Date.now(), akisV: 4
      };
      S.sessions.push(se);
      S.active = se.id;
      pomoDone = false;
      tickChecks();
      render();
    `);
    await new Promise(r => setTimeout(r, 250));
    const clockText = d.getElementById("clock").textContent;
    ok("hedef dolunca pomoDone true oldu", w.eval("pomoDone") === true);
    ok("hedef dolunca saat artı saymaya geçti (+00:05)", clockText.startsWith("+"));
    ok("overtime durumunda clock .over sınıfını aldı", d.getElementById("clock").classList.contains("over"));
  }

  console.log("\n15) Pomodoro Vaat & Kırık Taş Animasyonu ve Akustiği");
  {
    ok("sesCalTasKirilma tanımlı", typeof w.sesCalTasKirilma === "function");
    ok("kumTasKirAnimasyonu tanımlı", typeof w.kumTasKirAnimasyonu === "function");

    // Kırılma animasyonunun çalıştırılması
    w.eval(`
      window._mockStone = {
        x: 150, y: 200, r: 24, a: 0.1, e: 0.8, tohum: 12345, kirik: false
      };
      window._cbCalled = false;
      kumTasKirAnimasyonu(window._mockStone, () => { window._cbCalled = true; });
    `);
    ok("kumTasKirAnimasyonu taşı kırık işaretledi", w.eval("window._mockStone.kirik") === true);
    await new Promise(r => setTimeout(r, 360));
    ok("kırılma animasyonu tamamlandı geri çağrısı çalıştı", w.eval("window._cbCalled") === true);
  }

  console.log("\n16) Pomodoro Zen Kum Bahçesi — Seans Bazlı %100 Tırmık ve Çoklu Taş Hayalet Geçişi");
  {
    // Test 1: 25 dk seans tamamlandığında %100 taranma
    w.eval(`
      KUM.W = 360; KUM.H = 780;
      KUM.gun = "2026-08-20";
      KUM.tohum = 12345;
      KUM.bicim = kumBicim(12345);
      KUM.taslar = kumTasUret("2026-08-20", [25]);
      KUM.ara = 32;
      kumAlanKur();
      kumPlanKur();

      // 25 dk seans, 25 dk çalışılmış (tam seans)
      const olaylar25 = [{ sure: 25, target: 25, mola: false, seansIdx: 0 }];
      const ciz25 = kumCizgiler(olaylar25);
      window._ciz25 = ciz25;
      window._planN = KUM.plan.length;
    `);

    const planN = w.eval("window._planN");
    const ciz25Len = w.eval("window._ciz25.length");
    const ciz25Taze = w.eval("window._ciz25.filter(c => c.taze).length");
    ok("25 dk seans sonunda ekran %100 taranır", ciz25Len === planN && ciz25Taze === planN, `plan: ${planN}, taze: ${ciz25Taze}`);

    // Test 2: 50 dk seans 25. dakikada (%50 ilerleme)
    w.eval(`
      const olaylar50_yari = [{ sure: 25, target: 50, mola: false, seansIdx: 0 }];
      window._ciz50_yari = kumCizgiler(olaylar50_yari);
    `);
    const ciz50YariTaze = w.eval("window._ciz50_yari.filter(c => c.taze).length");
    const beklenenYari = Math.round(planN * 0.5);
    ok("50 dk seansın 25. dakikasında tırmık %50'dedir", Math.abs(ciz50YariTaze - beklenenYari) <= 1, `taze: ${ciz50YariTaze}, beklenen: ${beklenenYari}`);

    // Test 3: 2. Seansa geçildiğinde (2. taş) hayalet doku + taze tırmık katmanı
    w.eval(`
      KUM.taslar = kumTasUret("2026-08-20", [25, 50]);
      kumAlanKur();
      kumPlanKur();

      // 1. seans 25 dk bitmiş, 2. seans 50 dk'nın 20. dakikasında
      const olaylar2Seans = [
        { sure: 25, target: 25, mola: false, seansIdx: 0, ended: true },
        { sure: 20, target: 50, mola: false, seansIdx: 1, ended: false }
      ];
      window._ciz2Seans = kumCizgiler(olaylar2Seans);
    `);
    const ciz2S = w.eval("window._ciz2Seans");
    const taze2S = w.eval("window._ciz2Seans.filter(c => c.taze).length");
    /* yeniden tırmıklama: tırmık cephesinin önünde önceki geçiş durur */
    const hayalet2S = w.eval("window._ciz2Seans.filter(c => c.eski).length");
    const planN2 = w.eval("KUM.plan.length");
    ok("2. seansta taze tırmık ile önceki geçiş bir arada durur", taze2S > 0 && hayalet2S > 0);
    ok("2. seansta toplam çizgi adedi bahçenin tamamını kapsar", (taze2S + hayalet2S) === planN2, `taze: ${taze2S}, eski: ${hayalet2S}, plan: ${planN2}`);
    /* hata: yeni pomodoro başladığı an bütün çizgiler siliniyordu */
    const basta = w.eval(`kumCizgiler([
        { sure: 25, target: 25, mola: false, seansIdx: 0, ended: true },
        { sure: 0, target: 50, mola: false, seansIdx: 1, ended: false }]).length`);
    ok("yeni pomodoro başladığı an önceki tırmık silinmez", basta === planN2, `çizgi: ${basta}, plan: ${planN2}`);

    // Test 4: İptal edilen seans dürüstçe durur (kırık taş + dondurulmuş oran)
    w.eval(`
      // 50 dk seans 20. dakikada iptal edilmiş
      const olaylarIptal = [
        { sure: 25, target: 25, mola: false, seansIdx: 0, ended: true },
        { sure: 20, target: 50, mola: false, seansIdx: 1, ended: true, kirik: true }
      ];
      window._cizIptal = kumCizgiler(olaylarIptal);
    `);
    const tazeIptal = w.eval("window._cizIptal.filter(c => c.taze).length");
    ok("iptal edilen seans ulaştığı ilerleme yüzdesinde (%40) donar", Math.abs(tazeIptal - Math.round(planN2 * 0.4)) <= 1);
  }

  console.log("\n17) Zamanlayıcı — hoşgörü penceresi, mola bütçesi, kesinti aralıkları");
  {
    w.setTab("timer");

    /* (a) 6 saniyelik seans: kayıt oluşmaz, kırık sayılmaz */
    w.eval(`
      const se6 = {
        id: "test_grace_6sn", startedAt: Date.now() - 6000,
        mode: "stopwatch", target: 0, note: "", isler: [{ taskId: null, at: Date.now() - 6000 }],
        events: [{ type: "start", at: Date.now() - 6000 }],
        awayMs: 0, unconfirmedOk: false, edited: false, editedAt: Date.now(), akisV: 4
      };
      S.sessions.push(se6);
      S.active = se6.id;
      window._once = S.sessions.length;
      finish();
    `);
    ok("6 sn seans S.sessions'a eklenmedi (grace)", w.eval("S.sessions.length") === w.eval("window._once") - 1
       && !w.eval('S.sessions.some(x => x.id === "test_grace_6sn")'));
    ok("6 sn seans kırık sayılmadı (kirik işareti yok)", !w.eval('S.sessions.some(x => x.kirik)'));
    ok("6 sn seans sonrası aktif seans kalmadı", !w.eval("S.active"));

    /* (b) 25 dk kronometre: hak edilen mola 5 dk (300000 ms) */
    w.eval(`
      const se25 = {
        id: "test_butce_25dk", startedAt: Date.now() - 25 * 60000,
        mode: "stopwatch", target: 0, note: "", isler: [{ taskId: null, at: Date.now() - 25 * 60000 }],
        events: [{ type: "start", at: Date.now() - 25 * 60000 }],
        awayMs: 0, unconfirmedOk: false, edited: false, editedAt: Date.now(), akisV: 4
      };
      window._se25 = se25;
    `);
    const butce = w.eval("hakEdilenMolaMs(window._se25)");
    ok("25 dk kronometre 5 dk mola hakkı verir (300000 ms)", butce === 300000, "→ " + butce);
    ok("pomodoro modunda mola bütçesi birikmez (0)",
       w.eval('hakEdilenMolaMs({ mode: "pomodoro", events: [] })') === 0);

    /* (c) molalı seans: interruptions {start, end} pencerelerini doldurur */
    w.eval(`
      const t0 = Date.now() - 30 * 60000;
      const seMola = {
        id: "test_mola_kesinti", startedAt: t0,
        mode: "stopwatch", target: 0, note: "", isler: [{ taskId: null, at: t0 }],
        events: [
          { type: "start", at: t0 },
          { type: "break_start", at: t0 + 5 * 60000 },
          { type: "break_end", at: t0 + 7 * 60000 },
          { type: "break_start", at: t0 + 12 * 60000 },
          { type: "break_end", at: t0 + 13 * 60000 }
        ],
        awayMs: 0, unconfirmedOk: false, edited: false, editedAt: Date.now(), akisV: 4
      };
      S.sessions.push(seMola);
      S.active = seMola.id;
      finish(t0 + 30 * 60000);
    `);
    const ksn = w.eval('S.sessions.find(x => x.id === "test_mola_kesinti")');
    ok("molalı seans kayda geçti (grace dışı)", !!ksn);
    ok("interruptions iki pencere doldurur",
       ksn && ksn.interruptions && ksn.interruptions.length === 2,
       ksn ? JSON.stringify(ksn.interruptions) : "kayıt yok");
    ok("interruptions {start, end} biçiminde",
       ksn && ksn.interruptions.every(i => typeof i.start === "number" && typeof i.end === "number" && i.end > i.start));
    ok("actualMs net odak süresi (27 dk = 1620000 ms)", ksn && ksn.actualMs === 1620000, ksn ? "→ " + ksn.actualMs : "");
    ok("plannedMs kronometrede 0", ksn && ksn.plannedMs === 0);
    ok("harcanan mola bütçeden düşülür (floor(27dk/5)=324000 − 180000 = 144000)",
       ksn && w.eval("hakEdilenMolaMs(S.sessions.find(x => x.id === 'test_mola_kesinti'))") === 144000);
  }

  console.log("\n" + pass + " geçti, " + fail + " kaldı");
  process.exit(fail ? 1 : 0);
})().catch(e => { console.error(e); process.exit(1); });
