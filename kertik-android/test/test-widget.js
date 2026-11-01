/* Widget köprüsü — web tarafı doğru JSON'u üretiyor mu, widget tuşları
   uygulamanın normal akışına giriyor mu. Kotlin tarafı burada yok;
   sınanan şey köprünün SÖZLEŞMESİ. */
const fs = require("fs"), path = require("path");
const { JSDOM, VirtualConsole } = require("jsdom");

const KAYNAK = path.join(__dirname, "..", "app", "src", "main", "assets", "index.html");
let gecti = 0, kaldi = 0;
const ok = (a, m) => { if (a) { gecti++; console.log("  ✓ " + m) } else { kaldi++; console.log("  ✗ " + m) } };
const bolum = t => console.log("\n" + t);

/* sahte tuval — test-cizim.js ile aynı yaklaşım: doğrulanan şey piksel değil */
function sahteCtx() {
  const c = {
    canvas: null, globalAlpha: 1, globalCompositeOperation: "source-over",
    strokeStyle: "", fillStyle: "", lineWidth: 1, lineCap: "", lineJoin: ""
  };
  for (const k of ["beginPath","moveTo","lineTo","stroke","fill","fillRect","clearRect",
                   "setTransform","drawImage","putImageData","closePath","arc","save","restore"])
    c[k] = () => {};
  c.createImageData = (w, h) => ({ width: w, height: h, data: new Uint8ClampedArray(w * h * 4) });
  const grad = { addColorStop() {} };
  c.createRadialGradient = () => grad;
  c.createLinearGradient = () => grad;
  return c;
}

function kur(kayit) {
  const gelen = [];
  const native = {
    goster(){}, gizle(){}, bildirimIzniVar: () => true, bildirimIzniIste(){},
    ekraniAcikTut(){}, titret(){}, surum: () => "test",
    widgetDurum(json) { gelen.push(json) }
  };
  const hata = [];
  const vc = new VirtualConsole();
  vc.on("jsdomError", e => hata.push(e.message));
  const dom = new JSDOM(fs.readFileSync(KAYNAK, "utf8"), {
    runScripts: "dangerously", pretendToBeVisual: true, virtualConsole: vc,
    url: "http://localhost/",
    beforeParse(w) {
      if (!w.structuredClone) w.structuredClone = o => JSON.parse(JSON.stringify(o));
      w.HTMLCanvasElement.prototype.getContext = function () {
        const c = sahteCtx(); c.canvas = this; return c;
      };
      w.HTMLCanvasElement.prototype.toDataURL = () => "data:image/png;base64,";
      w.KertikNative = native;
      if (kayit) w.localStorage.setItem("kertik.v1", JSON.stringify(kayit));
    }
  });
  if (hata.length) console.log("   (jsdom hatası: " + hata[0] + ")");
  return { dom, w: dom.window, gelen, hata };
}
const son = g => JSON.parse(g[g.length - 1]);

/* ---------------------------------------------------------- */
bolum("1) Boş durumda ayna");
{
  const { w, gelen } = kur();
  ok(gelen.length > 0, "açılışta widget durumu gönderildi");
  const d = son(gelen);
  ok(d.durum === "bos", 'seans yokken durum "bos"');
  ok(Array.isArray(d.duvar) && d.duvar.length === 30, "duvar 30 gün taşıyor");
  ok(d.cubuk === null, "seans yokken çubuk yok");
  ok(typeof d.bugunNet === "number", "bugünün toplamı sayı");
  w.close();
}

bolum("2) Widget'tan başlat — seans yokken");
{
  const { w, gelen } = kur();
  const oncekiSeans = w.eval("S.sessions.length");
  w.kertikNativeEylem("start");
  ok(w.eval("S.sessions.length") === oncekiSeans + 1, "yeni seans açıldı");
  ok(w.eval("!!S.active"), "seans etkin");
  const d = son(gelen);
  ok(d.durum === "calisiyor", 'durum "calisiyor"');
  ok(d.temel > 0, "kronometre dayanağı verildi");
  ok(d.cubuk && d.cubuk.id, "çubuk verisi var");
  w.close();
}

bolum("3) Mola ve devam");
{
  const { w, gelen } = kur();
  w.kertikNativeEylem("start");
  w.kertikNativeEylem("break");
  let d = son(gelen);
  ok(d.durum === "molada", 'mola sonrası durum "molada"');
  ok(d.temel > 0, "mola dayanağı verildi");
  w.kertikNativeEylem("resume");
  d = son(gelen);
  ok(d.durum === "calisiyor", "devam sonrası çalışıyor");
  w.close();
}

bolum("4) Bitir");
{
  const { w, gelen } = kur();
  w.kertikNativeEylem("start");
  w.kertikNativeEylem("end");
  const d = son(gelen);
  ok(d.durum === "bos", "bitince durum boş");
  ok(d.cubuk === null, "bitince canlı çubuk yok");
  ok(d.duvar[0].dk >= 0, "bugünün duvar girdisi güncellendi");
  w.close();
}

bolum("5) Gereksiz köprü trafiği yok");
{
  const { w, gelen } = kur();
  w.kertikNativeEylem("start");
  const once = gelen.length;
  for (let i = 0; i < 40; i++) w.widgetBildir();     // imza değişmedi
  ok(gelen.length === once, "imza değişmeyince köprüden geçmiyor (" + once + " çağrı)");
  w.widgetBildir(true);
  ok(gelen.length === once + 1, "zorlanınca geçiyor");
  w.close();
}

bolum("6) JSON sözleşmesi — Kotlin tarafının okuduğu alanlar");
{
  const { w, gelen } = kur();
  w.kertikNativeEylem("start");
  const d = son(gelen);
  for (const alan of ["durum","temel","geri","net","not","bugunNet","bas","mod","hedef","cubuk","duvar","t"])
    ok(alan in d, "alan var: " + alan);
  ok(typeof d.geri === "boolean", "geri mantıksal");
  ok(Array.isArray(d.cubuk.m), "cubuk.m dizi");
  ok(d.duvar.every(g => typeof g.g === "number" && typeof g.dk === "number" && Array.isArray(g.m)),
     "duvar girdileri {g,dk,m} biçiminde");
  ok(JSON.stringify(d).length < 60000, "paket makul boyutta (" + JSON.stringify(d).length + " bayt)");
  w.close();
}

bolum("7) Native yokken (tarayıcı) patlamıyor");
{
  const vc = new VirtualConsole();
  const dom = new JSDOM(fs.readFileSync(KAYNAK, "utf8"), {
    runScripts: "dangerously", pretendToBeVisual: true, virtualConsole: vc,
    url: "http://localhost/",
    beforeParse(w) {
      if (!w.structuredClone) w.structuredClone = o => JSON.parse(JSON.stringify(o));
      w.HTMLCanvasElement.prototype.getContext = function () {
        const c = sahteCtx(); c.canvas = this; return c;
      };
      w.HTMLCanvasElement.prototype.toDataURL = () => "data:image/png;base64,";
    }
  });
  ok(typeof dom.window.widgetBildir === "function", "widgetBildir tanımlı");
  let patladi = false;
  try { dom.window.widgetBildir(true) } catch (e) { patladi = true }
  ok(!patladi, "KertikNative yokken sessizce geçiyor");
  dom.window.close();
}

console.log("\n" + gecti + " geçti, " + kaldi + " kaldı");
process.exit(kaldi ? 1 : 0);
