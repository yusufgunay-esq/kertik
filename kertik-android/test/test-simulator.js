/* SİMÜLATÖR TESTİ

   tasarim/simulator.html'i gerçekten açar ve içindeki uygulamayı sanal saatle
   sürer. Doğrulanan şey: simülatör uygulamayı bozmadan çalıştırıyor mu,
   hızlandırma gerçekten seansı ilerletiyor mu, senaryolar gerçek düğmelere
   basıyor mu, palet uygulanıyor mu.

   Bu test aynı zamanda simülatörün GÜNCEL olduğunu da tutuyor: gömülü uygulama
   metni kaynak dosyayla birebir değilse kırılır.

   Koşturmak için:  npm install jsdom && node test-simulator.js
*/
const fs = require("fs"), path = require("path");
const { JSDOM } = require("jsdom");

const KOK = path.join(__dirname, "../..");
const SIM = path.join(KOK, "simulasyon/simulator.html");
const UYG = path.join(KOK, "kertik-android/app/src/main/assets/index.html");

let pass = 0, fail = 0;
const ok = (n, c, x) => { c ? (pass++, console.log("  ✓ " + n))
                            : (fail++, console.log("  ✗ " + n, x === undefined ? "" : x)); };
const bekle = ms => new Promise(r => setTimeout(r, ms));

function sahteCtx() {
  const c = { canvas: null, globalAlpha: 1, globalCompositeOperation: "source-over",
              strokeStyle: "", fillStyle: "", lineWidth: 1, lineCap: "", lineJoin: "" };
  for (const k of ["beginPath","moveTo","lineTo","stroke","fill","fillRect","clearRect",
                   "setTransform","drawImage","putImageData","closePath","arc","save","restore"])
    c[k] = () => {};
  c.createImageData = (w, h) => ({ width: w, height: h, data: new Uint8ClampedArray(w * h * 4) });
  const g = { addColorStop() {} };
  c.createRadialGradient = () => g; c.createLinearGradient = () => g;
  return c;
}

(async () => {
  console.log("\n1) Simülatör güncel mi");
  {
    if (!fs.existsSync(SIM)) {
      console.log("  ✗ simulasyon/simulator.html yok — önce: node simulasyon/olustur-simulator.js");
      process.exit(1);
    }
    const s = fs.readFileSync(SIM, "utf8");
    const m = s.match(/<textarea id="app-src" hidden>([\s\S]*?)<\/textarea>/);
    ok("gömülü uygulama bulundu", !!m);
    const cozulmus = m[1].replace(/&lt;/g, "<").replace(/&gt;/g, ">").replace(/&amp;/g, "&");
    ok("gömülü uygulama kaynakla birebir (simülatör güncel)",
      cozulmus === fs.readFileSync(UYG, "utf8"),
      "→ node simulasyon/olustur-simulator.js koştur");
  }

  console.log("\n2) Açılış — hata yok, uygulama ayakta");
  const hatalar = [];
  const dom = new JSDOM(fs.readFileSync(SIM, "utf8"), {
    runScripts: "dangerously", pretendToBeVisual: true, resources: undefined,
    url: "http://localhost/sim.html",
    beforeParse(w) {
      donat(w);
      w.addEventListener("error", e => hatalar.push(String(e.message || e)));
      /* Simülatör çerçeveyi replaceChild ile tazeliyor; tam o anda, içine
         uygulama yazılmadan önce çerçevenin penceresini de donatıyoruz.
         (Gerçek tarayıcıda bunların hepsi zaten var — bu yalnız jsdom içindir.) */
      const asil = w.Node.prototype.replaceChild;
      w.Node.prototype.replaceChild = function (yeni, eski) {
        const r = asil.call(this, yeni, eski);
        try { if (yeni.tagName === "IFRAME" && yeni.contentWindow) donat(yeni.contentWindow); } catch (e) {}
        return r;
      };
    }
  });
  function donat(w) {
    if (!w.structuredClone) w.structuredClone = o => JSON.parse(JSON.stringify(o));
    if (w.HTMLCanvasElement) {
      w.HTMLCanvasElement.prototype.getContext = function () { const c = sahteCtx(); c.canvas = this; return c; };
      w.HTMLCanvasElement.prototype.toDataURL = () => "data:,";
    }
  }
  const W = dom.window;
  await bekle(400);

  /* çerçeve "baştan başlat"ta yenileniyor, o yüzden her seferinde tazesi alınır */
  const cerceve = () => W.document.getElementById("fr");
  const fr = cerceve();
  ok("çerçeve kuruldu", !!fr);
  const iw = fr.contentWindow;
  ok("uygulama çerçeveye yazıldı", iw.document.documentElement.outerHTML.length > 50000,
    iw.document.documentElement.outerHTML.length);
  await bekle(300);

  const idoc = iw.document;
  ok("uygulama çerçevede açıldı", !!idoc.getElementById("timerPage"));
  ok("uygulamanın betiği koştu", typeof iw.cizCubuk === "function");
  /* sanal saat bugünün 09:12'sine kurulur — gerçek saatle aynı olamaz */
  {
    const sanal = new Date(iw.eval("Date.now()"));
    ok("sanal saat kuruldu (bugün 09:12)",
      sanal.getHours() === 9 && sanal.getMinutes() === 12,
      sanal.toString());
    ok("sanal saat gerçek saatten bağımsız",
      Math.abs(iw.eval("Date.now()") - Date.now()) > 1000);
  }
  ok("kayıt geçmişi üretildi", iw.eval("S.sessions.length") > 10, iw.eval("S.sessions.length"));
  ok("konsola hata düşmedi", hatalar.length === 0, hatalar.join(" | "));

  console.log("\n3) Sanal saat gerçekten ilerliyor");
  {
    const t1 = iw.eval("Date.now()");
    cerceve().contentWindow.postMessage({ tip: "hiz", v: 300 }, "*");
    await bekle(500);
    const t2 = iw.eval("Date.now()");
    ok("300× hızda zaman ilerledi", t2 > t1, (t2 - t1) + " ms sanal");
    ok("gerçek saniyenin çok üstünde", (t2 - t1) > 5000, t2 - t1);
    cerceve().contentWindow.postMessage({ tip: "hiz", v: 0 }, "*");
    await bekle(120);
    const t3 = iw.eval("Date.now()");
    await bekle(200);
    ok("durdurunca zaman durdu", iw.eval("Date.now()") === t3);
  }

  console.log("\n4) Senaryo gerçek düğmelere basıyor");
  {
    cerceve().contentWindow.postMessage({ tip: "sekme", v: "timer" }, "*");
    await bekle(80);
    const once = iw.eval("S.sessions.filter(x=>x.endedAt).length");
    cerceve().contentWindow.postMessage(
      { tip: "senaryo", hiz: 3000,
        v: { adim: [["basla", 0], ["mola", 30], ["devam", 40], ["bitir", 60]] } }, "*");
    await bekle(200);
    ok("seans başladı", !!iw.eval("S.active"));
    /* 60 sanal dakika = 3600 sanal sn; 3000× hızda ~1.2 gerçek saniye */
    for (let i = 0; i < 40 && iw.eval("S.active"); i++) await bekle(100);
    ok("seans senaryo bitince kapandı", !iw.eval("S.active"));
    ok("kayda bir seans eklendi",
      iw.eval("S.sessions.filter(x=>x.endedAt).length") === once + 1);
    const se = iw.eval("S.sessions.filter(x=>x.endedAt).sort((a,b)=>b.startedAt-a.startedAt)[0]");
    const dk = Math.round((se.endedAt - se.startedAt) / 60000);
    ok("seans uzunluğu senaryoya uyuyor (~60 dk)", Math.abs(dk - 60) <= 2, dk + " dk");
    const molaSayisi = se.events.filter(e => e.type === "break_start").length;
    ok("mola gerçekten verildi", molaSayisi === 1, molaSayisi);
  }

  console.log("\n5) Kayıt sayfası — çubuk ve duvar çizildi");
  {
    cerceve().contentWindow.postMessage({ tip: "sekme", v: "log" }, "*");
    await bekle(200);
    const grids = idoc.querySelectorAll(".wallgrid");
    ok("duvar ızgarası açıldı", grids.length >= 1, grids.length);
    const herDuvar30 = [...grids].every(g => g.querySelectorAll(".day").length === 30);
    ok("duvar 30 gün çizdi", herDuvar30, [...grids].map(g => g.querySelectorAll(".day").length).join(", "));
    ok("duvarda dolu gün var",
      idoc.querySelectorAll(".wallgrid .day:not(.void) svg").length > 5,
      idoc.querySelectorAll(".wallgrid .day:not(.void) svg").length);
    const kart = idoc.querySelector("#logBody .card");
    kart.querySelector(".row").dispatchEvent(new iw.MouseEvent("click", { bubbles: true }));
    await bekle(60);
    const svg = kart.querySelector("[data-cubuk]");
    const cizildi = svg && (svg.querySelectorAll("[data-centik]").length > 10 || svg.querySelectorAll("[data-kalas]").length > 0 || svg.children.length > 0);
    ok("kart açılınca görsel/çubuk çizildi", !!cizildi);
  }

  console.log("\n6) Palet canlı uygulanıyor");
  {
    cerceve().contentWindow.postMessage({ tip: "palet", v: { "--accent": "#F04E23", "--cool": "#00A3A3" } }, "*");
    await bekle(150);
    ok("accent değişkeni uygulamaya işledi",
      idoc.documentElement.style.getPropertyValue("--accent").trim() === "#F04E23",
      idoc.documentElement.style.getPropertyValue("--accent"));
    cerceve().contentWindow.postMessage({ tip: "palet", v: null }, "*");
    await bekle(150);
    ok("palet geri alınabiliyor",
      idoc.documentElement.style.getPropertyValue("--accent").trim() === "");
  }

  console.log("\n7) Tema ve ileri sarma");
  {
    cerceve().contentWindow.postMessage({ tip: "tema", v: "dark" }, "*");
    await bekle(150);
    ok("karanlık tema uygulandı", idoc.documentElement.classList.contains("dark"));
    const t = iw.eval("Date.now()");
    cerceve().contentWindow.postMessage({ tip: "atla", v: 864e5 }, "*");
    await bekle(150);
    ok("bir gün ileri sarıldı", iw.eval("Date.now()") - t >= 864e5);
    ok("ileri sarınca hata çıkmadı", hatalar.length === 0, hatalar.join(" | "));
  }

  console.log("\n8) Gerçek depoya dokunulmadı");
  {
    ok("simülatör kendi hafızasını kullanıyor (localStorage sızmadı)",
      W.localStorage.getItem("kertik.v1") === null);
  }

  console.log("\n" + pass + " geçti, " + fail + " kaldı");
  process.exit(fail ? 1 : 0);
})().catch(e => { console.error(e); process.exit(1); });
