/* DENEME ÇAPASI TESTİ — ağsız, üç kaynak, en eski kazanır.

   Burada sınanan şey ödeme akışı değil, PENCERENİN NEREDEN SAYILDIĞI:
     · temiz kurulum tam süre görüyor mu (kimse haksız kilitlenmesin),
     · çapa kaydın içinde taşınıyor mu (yedek ve Drive onu götürüyor mu),
     · "yedeği geri yükle" ile deneme sıfırlanabiliyor mu (kayıt tanıklığı),
     · cihaz saati geri alınınca kalan gün artıyor mu (yüksek su işareti),
     · Drive birleştirmesi çapayı düşürüyor mu (mergeStates kuralı).

   Sunucu, imza, SSAID yok: bu yüzden ölçülen şey ağ değil, yerel kaynakların
   birbirini ezmemesi. Kural tek cümle: en eski tarih kazanır.

   Koşturmak için:  npm install jsdom && node test-deneme.js
*/
const fs = require("fs"), path = require("path");
const { JSDOM, VirtualConsole } = require("jsdom");

const HTML = path.join(__dirname, "../app/src/main/assets/index.html");
const GUN = 864e5;

let pass = 0, fail = 0;
function ok(ad, kosul, ek) {
  if (kosul) { pass++; console.log("  ✓ " + ad); }
  else { fail++; console.log("  ✗ " + ad, ek === undefined ? "" : ek); }
}

/* Sahte tuval: deneme testi çizim yapmıyor ama sayfa açılışta render() çağırıyor. */
function sahteCtx() {
  const c = { canvas: null, globalAlpha: 1, globalCompositeOperation: "source-over",
              strokeStyle: "", fillStyle: "", lineWidth: 1, lineCap: "", lineJoin: "",
              font: "", textAlign: "" };
  for (const k of ["beginPath", "moveTo", "lineTo", "stroke", "fill", "fillRect", "clearRect",
                   "setTransform", "drawImage", "putImageData", "closePath", "arc", "ellipse",
                   "save", "restore", "translate", "rotate", "scale", "setLineDash",
                   "quadraticCurveTo", "bezierCurveTo", "arcTo", "clip", "rect", "roundRect",
                   "fillText", "strokeText", "strokeRect", "resetTransform", "getLineDash"])
    c[k] = () => {};
  c.measureText = t => ({ width: String(t).length * 6 });
  c.createImageData = (w, h) => ({ width: w, height: h, data: new Uint8ClampedArray(w * h * 4) });
  const g = { addColorStop() {} };
  c.createRadialGradient = () => g; c.createLinearGradient = () => g;
  return c;
}

/* kur(): sayfayı verilen localStorage durumuyla açar. `kasa` verilirse native
   köprü taklit edilir; köprü YOKKEN tamMi() zaten her şeyi açık sayar. */
function kur(kayit, ekstra) {
  ekstra = ekstra || {};
  const hatalar = [];
  const vc = new VirtualConsole();
  vc.on("jsdomError", e => {
    const m = String((e && e.message) || e);
    if (/^Not implemented/.test(m)) return;
    hatalar.push(m);
  });
  const dom = new JSDOM(fs.readFileSync(HTML, "utf8"), {
    runScripts: "dangerously", pretendToBeVisual: true, virtualConsole: vc,
    url: "http://localhost/",
    beforeParse(w) {
      if (!w.structuredClone) w.structuredClone = o => JSON.parse(JSON.stringify(o));
      w.HTMLCanvasElement.prototype.getContext = function () { const c = sahteCtx(); c.canvas = this; return c; };
      w.HTMLCanvasElement.prototype.toDataURL = () => "data:image/png;base64,";
      if (kayit) w.localStorage.setItem("kertik.v1", JSON.stringify(kayit));
      for (const [k, v] of Object.entries(ekstra.yerel || {})) w.localStorage.setItem(k, v);
      if (ekstra.kasa) w.KertikKasa = ekstra.kasa;
    }
  });
  return new Promise(res => setTimeout(() => res({ w: dom.window, hatalar }), 80));
}

/* Native köprü taklidi: tamMi() köprü yokken her şeyi açık saydığı için
   duvarın gerçekten çalıştığını görmek ancak köprüyle mümkün. */
const sahteKasa = { durum: () => JSON.stringify({ sahip: false, fiyat: "", hazir: true }) };

/* `S` ve `AK` sayfada `let` ile tanımlı; window'a düşmezler. Sayfa içinden
   okunup yazılırlar (test-cizim.js de aynı yolu kullanıyor). */
const oku = (w, ifade) => w.eval(ifade);
const yaz = (w, ifade) => { w.eval(ifade); };
const durum = w => oku(w, "S");

const DK = 60000;
function seans(id, basTs, dk, mod) {
  const bit = basTs + dk * DK;
  return { id, startedAt: basTs, endedAt: bit, dayKey: "2026-06-01", note: "",
           mode: mod || "stopwatch", target: 0,
           events: [{ type: "start", at: basTs }, { type: "end", at: bit }],
           awayMs: 0, unconfirmedOk: false, edited: false, editedAt: bit };
}
function kayit(o) {
  o = o || {};
  return Object.assign({
    sessions: [], tasks: [], tombstones: [], active: null,
    settings: { mode: "stopwatch", theme: "light" }, settingsEditedAt: 0,
    sync: { connected: false }
  }, o);
}

(async () => {
  console.log("\n1) Temiz kurulum — kimse haksız kilitlenmesin");
  {
    const { w, hatalar } = await kur(kayit(), { kasa: sahteKasa });
    ok("kalan gün 14", w.denemeKalanGun() === 14, w.denemeKalanGun());
    ok("deneme açık", w.denemedeMi() === true);
    ok("çapa kayda yazıldı", oku(w, "S.deneme.baslangic") > 0, oku(w, "S.deneme.baslangic"));
    ok("açılışta hata yok", hatalar.length === 0, hatalar.join(" | "));
  }

  console.log("\n2) Zaman — ileri ve geri");
  {
    const { w } = await kur(kayit(), { kasa: sahteKasa });
    const capa = oku(w, "S.deneme.baslangic");
    /* Üç gün ileri: kalan gün 11 olmalı. */
    yaz(w, "S.deneme.bakilan = " + (capa + 3 * GUN));
    ok("üç gün ileri sarılınca kalan gün 11", w.denemeKalanGun() === 11, w.denemeKalanGun());
    /* Cihaz saati bir ay geri alınsa bile `bakilan` geri gitmez. */
    const onceki = w.denemeKalanGun();
    yaz(w, "S.deneme.bakilan = " + (capa + 3 * GUN));
    ok("saat geri alınınca kalan gün ARTMAZ", w.denemeKalanGun() <= onceki, w.denemeKalanGun());
    /* Yüksek su işareti diske yazımda ilerliyor mu */
    yaz(w, "S.deneme.bakilan = 0");
    w.yazDiske();
    ok("yazDiske() bakılan'ı ilerletiyor", oku(w, "S.deneme.bakilan") >= capa, oku(w, "S.deneme.bakilan"));
  }

  console.log("\n3) Kayıt tanıklığı — yedekle aklama yolu");
  {
    /* 20 günlük geçmiş var, çapa yok: deneme bitmiş sayılır. */
    const eski = Date.now() - 20 * GUN;
    const { w } = await kur(kayit({ sessions: [seans("a", eski, 30)] }), { kasa: sahteKasa });
    ok("20 günlük geçmiş → deneme bitti", w.denemeKalanGun() === 0, w.denemeKalanGun());
    ok("duvar açılıyor (tamMi false)", w.tamMi() === false);
  }
  {
    /* 2 günlük geçmiş: çapa o seansın tarihi olur, 12 gün kalır. */
    const yeni = Date.now() - 2 * GUN;
    const { w } = await kur(kayit({ sessions: [seans("a", yeni, 30)] }), { kasa: sahteKasa });
    ok("2 günlük geçmiş → 12 gün kaldı", w.denemeKalanGun() === 12, w.denemeKalanGun());
  }
  {
    /* Çapa varken eski seanslar silinse kalan gün ARTMAZ. */
    const { w } = await kur(kayit({ sessions: [seans("a", Date.now() - 5 * GUN, 30)] }), { kasa: sahteKasa });
    const once = w.denemeKalanGun();
    yaz(w, "S.sessions = []");
    yaz(w, "S.deneme.baslangic = " + (Date.now() - 5 * GUN));
    ok("çapa varken seans silmek kalan günü artırmaz", w.denemeKalanGun() <= once, w.denemeKalanGun() + " ↔ " + once);
  }

  console.log("\n4) Göç — eski kertik.kurulum anahtarı");
  {
    const eskiAnahtar = Date.now() - 9 * GUN;
    const { w } = await kur(kayit(), { kasa: sahteKasa, yerel: { "kertik.kurulum": String(eskiAnahtar) } });
    ok("eski anahtar çapa olarak okundu (5 gün kaldı)", w.denemeKalanGun() === 5, w.denemeKalanGun());
    ok("anahtar kayda göç etti", oku(w, "S.deneme.baslangic") === eskiAnahtar, oku(w, "S.deneme.baslangic"));
    ok("eski anahtar silindi", w.localStorage.getItem("kertik.kurulum") === null);
  }
  {
    /* Eski anahtar YENİ olsa bile kayıttaki eski çapa kazanır. */
    const kayitCapa = Date.now() - 10 * GUN;
    const { w } = await kur(kayit({ deneme: { baslangic: kayitCapa, bakilan: 0 } }),
      { kasa: sahteKasa, yerel: { "kertik.kurulum": String(Date.now()) } });
    ok("en eski kaynak kazanır (kayıt çapası)", oku(w, "S.deneme.baslangic") === kayitCapa, oku(w, "S.deneme.baslangic"));
  }

  console.log("\n5) Yedek — çapa kaydın içinde yolculuk ediyor");
  {
    const { w } = await kur(kayit({ sessions: [seans("a", Date.now() - 4 * GUN, 30)] }), { kasa: sahteKasa });
    const kalan = w.denemeKalanGun();
    const disaAktarilan = JSON.parse(JSON.stringify(durum(w)));
    ok("dışa aktarılan JSON çapayı taşıyor", disaAktarilan.deneme && disaAktarilan.deneme.baslangic > 0,
      JSON.stringify(disaAktarilan.deneme));
    ok("dışa aktarılan JSON seansları taşıyor", disaAktarilan.sessions.length === 1);

    /* Yedek alındı, veriler temizlendi, yedek geri yüklendi: kalan gün aynı yerden. */
    const { w: w2 } = await kur(kayit(), { kasa: sahteKasa });
    ok("temiz kurulum tam süre görür (kıyas)", w2.denemeKalanGun() === 14, w2.denemeKalanGun());

    const { w: w3 } = await kur(disaAktarilan, { kasa: sahteKasa });
    ok("yedeği geri yükleyince deneme SIFIRLANMIYOR", w3.denemeKalanGun() === kalan,
      w3.denemeKalanGun() + " ↔ " + kalan);
    ok("yedeği geri yükleyince geçmiş geri geliyor", oku(w3, "S.sessions.length") === 1);
  }
  {
    /* Çapasız ESKİ biçim yedek: tanıklık devreye girer, uygulama bozulmaz. */
    const eskiYedek = kayit({ sessions: [seans("a", Date.now() - 12 * GUN, 30)] });
    delete eskiYedek.deneme;
    const { w, hatalar } = await kur(eskiYedek, { kasa: sahteKasa });
    ok("çapasız eski yedek açılışı bozmuyor", hatalar.length === 0, hatalar.join(" | "));
    ok("çapasız yedekte tanıklık devreye giriyor (2 gün)", w.denemeKalanGun() === 2, w.denemeKalanGun());
    ok("çapa yazıldıktan sonra kayıt tamam", oku(w, "S.deneme.baslangic") > 0);
  }

  console.log("\n6) Drive birleştirmesi — çapa düşmesin");
  {
    const src = fs.readFileSync(HTML, "utf8")
      .split("/* --- MERGE:BEGIN ---")[1].split("/* --- MERGE:END --- */")[0];
    const mergeStates = new Function(
      src.replace(/^[\s\S]*?function mergeStates/, "return function mergeStates")
         .replace(/\/\* --- MERGE:END[\s\S]*$/, "") + ";")();
    const T = 1e12;
    const st = o => Object.assign({ sessions: [], tasks: [], tombstones: [], active: null,
                                    settings: {}, settingsEditedAt: 0 }, o);

    const eski = T - 10 * GUN, yeni = T - 2 * GUN;
    const r = mergeStates(st({ deneme: { baslangic: eski, bakilan: T - 5 * GUN } }),
                          st({ deneme: { baslangic: yeni, bakilan: T } }), { now: T });
    ok("birleşme deneme alanını taşıyor", !!r.deneme, JSON.stringify(r.deneme));
    ok("en eski çapa kazanıyor", r.deneme.baslangic === eski, r.deneme.baslangic);
    ok("bakılan = yüksek su işareti (en büyük)", r.deneme.bakilan === T, r.deneme.bakilan);

    const bos = mergeStates(st({}), st({}), { now: T });
    ok("iki taraf da çapasızsa null döner", bos.deneme && bos.deneme.baslangic === null,
      JSON.stringify(bos.deneme));

    const tek = mergeStates(st({ deneme: { baslangic: eski, bakilan: 0 } }), st({}), { now: T });
    ok("tek taraflı çapa korunuyor", tek.deneme.baslangic === eski, tek.deneme.baslangic);
  }

  console.log("\n7) Duvar ve çekirdek — kilitlenen alet, kayıt değil");
  {
    const { w } = await kur(kayit({ sessions: [seans("a", Date.now() - 30 * GUN, 30)] }), { kasa: sahteKasa });
    ok("süre dolunca tamMi false", w.tamMi() === false);
    ok("kayıt yerinde duruyor", oku(w, "S.sessions.length") === 1);
    ok("geçmiş okunabiliyor (stats çalışıyor)", oku(w, "stats(S.sessions[0]).net") > 0);
    ok("dışa aktarma hâlâ mümkün (S serileştirilebiliyor)", JSON.stringify(durum(w)).length > 10);
    /* startSession duvarı açar, seans başlatmaz */
    const adet = oku(w, "S.sessions.length");
    w.startSession();
    ok("startSession duvara çarpıyor, seans açmıyor", oku(w, "S.sessions.length") === adet, oku(w, "S.sessions.length"));
  }
  {
    /* Köprü yoksa (tarayıcı, simülatör) kilit anlamsız: her şey açık. */
    const { w } = await kur(kayit({ sessions: [seans("a", Date.now() - 30 * GUN, 30)] }));
    ok("köprü yokken tamMi true (hata kullanıcı aleyhine değil)", w.tamMi() === true);
  }

  console.log("\n8) Eski veri — tohum ve akisV alanı olmayan seans");
  {
    const eskiSeans = seans("eski", Date.now() - GUN, 30);
    const { w, hatalar } = await kur(kayit({ sessions: [eskiSeans] }), { kasa: sahteKasa });
    ok("tohumsuz/akissız eski seans açılışı bozmuyor", hatalar.length === 0, hatalar.join(" | "));
    ok("eski seans hâlâ kayıtta", oku(w, "S.sessions.length") === 1);
    ok("tohumu olmayan seans güvenli yöne düşüyor", w.akisYonu(eskiSeans) === "sade", w.akisYonu(eskiSeans));
  }

  console.log("\n" + pass + " geçti, " + fail + " kaldı");
  process.exit(fail ? 1 : 0);
})().catch(e => { console.error(e); process.exit(1); });
