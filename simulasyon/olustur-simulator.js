/* SİMÜLATÖR ÜRETİCİSİ

   Gerçek uygulamayı (kertik-android/app/src/main/assets/index.html) okur ve
   tek dosyalık bir tezgâha gömer: simulasyon/simulator.html

   Neden üretiliyor da elle yazılmıyor: simülatörün içindeki uygulama bir KOPYA
   değil, birebir kendisi. Uygulamada bir şey değişince bu betik yeniden
   koşturulur ve simülatör de değişir. Kopya tutulsaydı sessizce ayrışırdı.

   Koşturmak için:
     node simulasyon/olustur-simulator.js

   Bağımlılık yok.
*/
const fs = require("fs");
const path = require("path");

const KOK = path.join(__dirname, "..");
const KAYNAK = path.join(KOK, "kertik-android/app/src/main/assets/index.html");
const HEDEF = path.join(__dirname, "simulator.html");

const uygulama = fs.readFileSync(KAYNAK, "utf8");

/* Uygulama HTML'i <textarea> içine gömülüyor: orası RCDATA, içindeki <script>
   etiketleri metin sayılıyor. Tek dikkat edilecek şey & işareti — o yüzden
   kaçırılıyor, textarea.value okunurken tarayıcı geri çözüyor. */
const gomulu = uygulama.replace(/&/g, "&amp;").replace(/<\/textarea/gi, "&lt;/textarea");

/* ---------------------------------------------------------------- kabuk */
/* Sanal saat + mesaj köprüsü. Uygulamanın betiğinden ÖNCE koşar.
   Uygulamanın kendi kodu bir satır bile değişmiyor. */
const KABUK = `
<script>
(function(){
  "use strict";
  var GERCEK_DATE = Date;
  var T = 0;                 /* sanal şimdi (ms) */
  var HIZ = 0;               /* gerçek 1 sn'de kaç sanal sn */
  var sanalIsler = [];
  var senaryo = null;

  /* ---------- hafızada localStorage: gerçek tarayıcı deposuna dokunmuyoruz ---------- */
  var kutu = {};
  try {
    Object.defineProperty(window, "localStorage", { configurable:true, value:{
      getItem: function(k){ return Object.prototype.hasOwnProperty.call(kutu,k) ? kutu[k] : null },
      setItem: function(k,v){ kutu[k] = String(v) },
      removeItem: function(k){ delete kutu[k] },
      clear: function(){ kutu = {} },
      key: function(i){ return Object.keys(kutu)[i] || null },
      get length(){ return Object.keys(kutu).length }
    }});
  } catch(e){}

  /* ---------- sanal saat ---------- */
  function SimDate(){
    if (arguments.length === 0) return new GERCEK_DATE(T);
    if (arguments.length === 1) return new GERCEK_DATE(arguments[0]);
    return new GERCEK_DATE(arguments[0],arguments[1],arguments[2]||1,
      arguments[3]||0,arguments[4]||0,arguments[5]||0,arguments[6]||0);
  }
  SimDate.prototype = GERCEK_DATE.prototype;
  SimDate.now   = function(){ return T };
  SimDate.parse = GERCEK_DATE.parse;
  SimDate.UTC   = GERCEK_DATE.UTC;
  window.Date = SimDate;

  /* Uygulamanın saniyelik işi gerçek zamana değil sanal zamana bağlanıyor.
     setTimeout'a dokunulmuyor: onlar animasyon/gecikme işleri, gerçek kalmalı. */
  var gercekSetInterval = window.setInterval.bind(window);
  window.setInterval = function(fn, ms){
    if (ms >= 900 && ms <= 1100) { sanalIsler.push({ fn:fn, ms:ms, son:T }); return -1; }
    return gercekSetInterval.apply(null, arguments);
  };

  /* ---------- sahte kayıt geçmişi ---------- */
  function rng(a){ a=a>>>0; return function(){ a=a+0x6D2B79F5|0;
    var t=Math.imul(a^a>>>15,1|a); t=t+Math.imul(t^t>>>7,61|t)^t;
    return ((t^t>>>14)>>>0)/4294967296 }; }
  function iki(n){ return n<10 ? "0"+n : ""+n }
  function gunAnahtar(ts){ var d=new GERCEK_DATE(ts);
    return d.getFullYear()+"-"+iki(d.getMonth()+1)+"-"+iki(d.getDate()) }

  var NOTLAR = ["tez — kaynak taraması","matematik","İngilizce","rapor","okuma",
                "sunum hazırlığı","alıştırma","not çıkarma",""];

  function gecmisUret(tohum, gunSayisi){
    var R = rng(tohum), seanslar = [], no = 0;
    for (var g = gunSayisi; g >= 1; g--) {
      if (R() < .22) continue;                              /* boş gün */
      var kac = R() < .45 ? 1 : (R() < .82 ? 2 : 3);
      var saat = 9 + Math.floor(R()*3);
      for (var s = 0; s < kac; s++) {
        var d = new GERCEK_DATE(T);
        d.setDate(d.getDate() - g);
        d.setHours(saat, Math.floor(R()*50), 0, 0);
        var bas = d.getTime();
        var dk = Math.round(20 + R()*R()*190);
        var olay = [{ type:"start", at:bas }], molalar = [];
        var m = Math.round(28 + R()*38);
        while (m < dk - 8) {
          var u = Math.round(5 + R()*17);
          olay.push({ type:"break_start", at: bas + m*60000 });
          olay.push({ type:"break_end",   at: bas + Math.min(dk, m+u)*60000 });
          molalar.push(u);
          m += u + Math.round(34 + R()*46);
        }
        var bit = bas + dk*60000;
        olay.push({ type:"end", at:bit });
        var molaTop = molalar.reduce(function(a,b){return a+b},0);
        var away = (R() < .2 && dk - molaTop > 70) ? Math.round(10 + R()*25) : 0;
        seanslar.push({
          id: "sim" + (no++), startedAt: bas, endedAt: bit, dayKey: gunAnahtar(bas),
          note: NOTLAR[Math.floor(R()*NOTLAR.length)], mode: R()<.25 ? "pomodoro":"stopwatch",
          target: 0, events: olay, awayMs: away*60000, unconfirmedOk:false,
          edited:false, editedAt: bit
        });
        saat += Math.floor(dk/60) + 2 + Math.floor(R()*3);
        if (saat > 20) break;
      }
    }
    var isler = [];
    var BUGUN = ["kaynakları tara","bölüm 3'ü bitir","e-postalara dön","30 dk okuma"];
    for (var i=0;i<BUGUN.length;i++) isler.push({
      id:"t"+i, title:BUGUN[i], plannedFor:gunAnahtar(T), status:"bekliyor",
      order:i, createdAt:T, editedAt:T
    });
    return { sessions: seanslar, tasks: isler, tombstones: [], active: null,
             settings: { mode:"stopwatch", pomoTarget:50, milestone:50, longBreakAsk:25,
                         longSessionAsk:90, keepAwake:true, theme:"system", vibrate:false },
             settingsEditedAt: T, sync: { connected:false, fileId:null, lastAt:0, lastErr:null, auto:false } };
  }

  /* ---------- palet ---------- */
  function paletUygula(v){
    var kok = document.documentElement;
    /* önce eskisini temizle */
    var eski = kok.getAttribute("data-palet-anahtar");
    if (eski) eski.split(",").forEach(function(k){ kok.style.removeProperty(k) });
    if (!v) { kok.removeAttribute("data-palet-anahtar"); }
    else {
      var anahtarlar = [];
      for (var k in v) { kok.style.setProperty(k, v[k]); anahtarlar.push(k); }
      kok.setAttribute("data-palet-anahtar", anahtarlar.join(","));
    }
    try { akisYeniden(); render(); } catch(e){}
  }

  /* ---------- senaryo: gerçek düğmelere basar ---------- */
  var ADIM_DUGME = { basla:"bStart", mola:"bBrk", devam:"bRes", bitir:"bEnd" };
  function senaryoIsle(){
    if (!senaryo) return;
    while (senaryo.i < senaryo.adim.length) {
      var a = senaryo.adim[senaryo.i];
      if (T < senaryo.t0 + a[1]*60000) return;
      var d = document.getElementById(ADIM_DUGME[a[0]]);
      if (d) d.click();
      senaryo.i++;
      if (senaryo.i >= senaryo.adim.length) { senaryo = null; HIZ = 0; bildir(); return; }
    }
  }

  /* ---------- ana döngü ---------- */
  var sonKare = 0;
  function kare(ts){
    requestAnimationFrame(kare);
    if (!sonKare) { sonKare = ts; return; }
    var dt = ts - sonKare; sonKare = ts;
    if (HIZ > 0) {
      if (dt > 250) dt = 250;
      /* Kare başına en çok bir sanal dakika. Yoksa çok yüksek hızda tek karede
         on dakika atlanıyor ve mola/bitiş anları o kabalıkta kayıyor. */
      T += Math.min(dt * HIZ, 60000);
      calistir();
    }
    bildir();
  }
  function calistir(){
    for (var i=0;i<sanalIsler.length;i++){
      var j = sanalIsler[i], n = 0;
      while (T - j.son >= j.ms && n < 400) { j.son += j.ms; try{ j.fn() }catch(e){} n++; }
      if (n >= 400) j.son = T;                 /* çok geride kaldıysa atla */
    }
    senaryoIsle();
  }

  function bildir(){
    var d = { tip:"durum", t:T, hiz:HIZ, senaryo: !!senaryo };
    try {
      var se = activeSession();
      d.aktif = !!se;
      d.sekme = tab;
      if (se) { var st = stats(se);
        d.gecen = st.gross; d.net = st.net; d.mola = st.brk;
        d.molada = st.onBreak; d.mod = se.mode; }
      d.seansSayisi = S.sessions.filter(function(x){return x.endedAt}).length;
      d.akis = { hazir: AK.hazir, serit: AK.serit.length, ciz: AK.ciz, yon: AKSEC };
    } catch(e){}
    parent.postMessage(d, "*");
  }

  addEventListener("message", function(e){
    var m = e.data || {};
    try {
      if (m.tip === "hiz")     { HIZ = m.v; if (m.v) sonKare = 0; }
      else if (m.tip === "atla") { T += m.v; calistir(); try{ render() }catch(_){} }
      else if (m.tip === "palet") paletUygula(m.v);
      else if (m.tip === "akisyon") akisYon(m.v);
      else if (m.tip === "tema") { S.settings.theme = m.v; applyTheme(); render(); }
      else if (m.tip === "sekme") { var b=document.querySelector('nav button[data-tab="'+m.v+'"]'); if(b) b.click(); }
      else if (m.tip === "senaryo") {
        var b2 = document.getElementById("bEnd"); if (b2) b2.click();
        if (m.v.mod) { var ms=document.querySelector('#modeSeg button[data-m="'+m.v.mod+'"]'); if(ms) ms.click(); }
        if (m.v.sure) { var ds=document.querySelector('.durs button[data-d="'+m.v.sure+'"]'); if(ds) ds.click(); }
        senaryo = { adim: m.v.adim, i: 0, t0: T };
        HIZ = m.hiz || 300;
        senaryoIsle();
      }
      else if (m.tip === "dur") { senaryo = null; HIZ = 0; }
    } catch(err){ parent.postMessage({ tip:"hata", mesaj: String(err) }, "*"); }
  });

  window.onerror = function(msg, kaynak, sat){
    parent.postMessage({ tip:"hata", mesaj: msg + " (satır " + sat + ")" }, "*");
  };

  /* ---------- açılış ---------- */
  var d0 = new GERCEK_DATE();
  d0.setHours(9, 12, 0, 0);
  T = d0.getTime();
  kutu["kertik.v1"] = JSON.stringify(gecmisUret(Number(SIM_TOHUM) || 7, 30));
  requestAnimationFrame(kare);
})();
<\/script>
`;

/* --------------------------------------------------------------- panel */
const PANEL = String.raw`<!doctype html>
<html lang="tr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Kertik — simülatör</title>
<style>
:root{
  --bg:#16171A; --bg2:#212227; --ink:#EDE9E0; --ink2:#BCB7AC;
  --muted:#948F84; --faint:#6A665E; --line:#2E2F34; --acc:#D0785B;
}
*{box-sizing:border-box}
html,body{margin:0;min-height:100%}
body{
  background:var(--bg2);color:var(--ink);
  font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,system-ui,sans-serif;
  font-size:16px;line-height:1.5;-webkit-font-smoothing:antialiased
}
.wrap{max-width:1120px;margin:0 auto;padding:40px 24px 80px}
h1{font-size:32px;font-weight:400;letter-spacing:-.03em;margin:0}
.sub{color:var(--muted);font-size:15px;margin-top:6px;max-width:64ch}
.lab{display:flex;gap:38px;flex-wrap:wrap;align-items:flex-start;margin-top:30px}

.phone{
  position:relative;width:340px;height:722px;border-radius:44px;overflow:hidden;
  background:#000;border:1px solid var(--line);flex-shrink:0;
  box-shadow:0 24px 70px rgba(0,0,0,.4)
}
.phone iframe{width:100%;height:100%;border:0;display:block}

.panel{flex:1;min-width:320px}
h3{font-size:13px;font-weight:500;letter-spacing:.11em;text-transform:uppercase;
   color:var(--muted);margin:0 0 10px}
.blok{margin-bottom:26px}
.chips{display:flex;gap:8px;flex-wrap:wrap}
button{
  border:1px solid var(--line);background:none;color:var(--muted);border-radius:999px;
  padding:10px 16px;font-size:14.5px;font-family:inherit;cursor:pointer;transition:.2s
}
button:hover{color:var(--ink2);border-color:var(--faint)}
button.on{border-color:var(--acc);color:var(--acc)}
button.ana{background:var(--acc);border-color:var(--acc);color:#16171A;font-weight:600}
button.ana:hover{color:#16171A;filter:brightness(1.08)}

.oku{
  background:var(--bg);border:1px solid var(--line);border-radius:16px;
  padding:16px 18px;font-size:14.5px;line-height:1.85
}
.oku .sat{display:flex;justify-content:space-between;gap:20px}
.oku .k{color:var(--muted)}
.oku .v{font-variant-numeric:tabular-nums;color:var(--ink)}
.oku .v.acc{color:var(--acc)}

.hata{
  display:none;background:#3A1F1B;border:1px solid #7A4034;color:#F0B4A6;
  border-radius:14px;padding:13px 16px;font-size:14px;margin-bottom:18px;
  white-space:pre-wrap;font-family:ui-monospace,Menlo,Consolas,monospace
}
.hata.on{display:block}
.not{font-size:13.5px;color:var(--faint);margin-top:10px;max-width:46ch;line-height:1.65}
.paletgrid{display:flex;gap:8px;flex-wrap:wrap}
.paletgrid button{padding-left:11px;display:flex;align-items:center;gap:8px}
.sw{width:13px;height:13px;border-radius:4px;flex-shrink:0;box-shadow:0 0 0 1px rgba(255,255,255,.14) inset}
</style>
</head>
<body>
<div class="wrap">

<h1>Kertik — simülatör</h1>
<div class="sub">İçerideki uygulama kopya değil, gerçeğin kendisi: derlenen dosyanın aynısı,
sanal bir saatle çalışıyor. Hızlandır, bir seansı baştan sona izle, kayda bak, paletleri dene.
Kayıtlar hafızada tutuluyor — sayfayı yenilediğinde hepsi baştan üretilir.</div>

<div class="hata" id="hata"></div>

<div class="lab">
  <div class="phone"><iframe id="fr" title="Kertik"></iframe></div>

  <div class="panel">

    <div class="blok">
      <h3>hız</h3>
      <div class="chips" id="hiz"></div>
      <div class="not">300× demek: gerçek 1 saniye = 5 dakika seans. Kadran ve akış alanı
      o hızda dolar; sayaç yine olay damgalarından hesaplanır, saymaz.</div>
    </div>

    <div class="blok">
      <h3>senaryo — gerçek düğmelere basar</h3>
      <div class="chips" id="senaryo"></div>
      <div class="not">Seans kendiliğinden başlar, molaya girer, biter. Bitişte uygulamanın
      dürüstlük sorusu çıkarsa hız durur, cevabı sen verirsin.</div>
    </div>

    <div class="blok">
      <h3>zamanı ileri sar</h3>
      <div class="chips" id="atla"></div>
    </div>

    <div class="blok">
      <h3>sekme</h3>
      <div class="chips" id="sekme"></div>
    </div>

    <div class="blok">
      <h3>akış yönü</h3>
      <div class="chips" id="akisyon"></div>
      <div class="not">Üç yön de aynı şeritleri kullanıyor — geometri değişmiyor, yalnız nasıl
      çizildikleri. O yüzden anında geçiş yapabilirsin, alan baştan hesaplanmıyor.
      <b>sade</b> uygulamanın ilk hâli. <b>belirgin</b> aynı alfabe, daha görünür.
      <b>ebru</b> katmanlı: kalın damarlar, kılcal tüyler, altta geniş bir yıkama ve ton kayması.
      Yönü seans sürerken değiştir; en iyi 300× hızda 40. dakikadan sonra okunuyor.</div>
    </div>

    <div class="blok">
      <h3>palet</h3>
      <div class="paletgrid" id="palet"></div>
      <div class="chips" style="margin-top:9px" id="tema"></div>
      <div class="not">Palet canlı uygulanıyor: kadran çentiği, akış alanı, çubuk — hepsi
      aynı iki renkten besleniyor (çalışma ve mola). Beğendiğini söyle, uygulamaya işleyeyim.</div>
    </div>

    <div class="blok">
      <h3>durum</h3>
      <div class="oku" id="oku"></div>
    </div>

    <div class="blok">
      <div class="chips">
        <button id="yenile">baştan başlat (yeni kayıt geçmişi)</button>
      </div>
    </div>

  </div>
</div>
</div>

<textarea id="app-src" hidden>__UYGULAMA__</textarea>
<script>
const KABUK = __KABUK__;

/* ---------------- paletler ---------------- */
/* Her palet iki mod: açık ve karanlık. Uygulamanın kendi değişken adları. */
const PALETLER = {
  "kâğıt": null,                                    /* uygulamanın mevcut hâli */
  "kor": {
    light:{ "--bg":"#FFF8F0","--bg2":"#FFEFDE","--ink":"#1B1512","--ink2":"#4A3A31",
      "--muted":"#7C6558","--faint":"#A89283","--line":"#F0DAC1","--track":"#F0DAC1",
      "--accent":"#F04E23","--cool":"#00A3A3","--ok":"#4A9E5C","--danger":"#D3402E",
      "--fill":"#1B1512","--onFill":"#FFF8F0","--segsel":"#FFFDF8","--knob":"#FFFFFF" },
    dark:{ "--bg":"#14100D","--bg2":"#1F1915","--ink":"#F5EBE0","--ink2":"#CDB9A8",
      "--muted":"#9C8878","--faint":"#6E5D50","--line":"#322922","--track":"#3A2F27",
      "--accent":"#FF7A4D","--cool":"#35C9C9","--ok":"#7FA886","--danger":"#E08878",
      "--fill":"#F5EBE0","--onFill":"#14100D","--segsel":"#4A3D33","--knob":"#FFF6EC" }
  },
  "deniz": {
    light:{ "--bg":"#F3F8FC","--bg2":"#E6F0F9","--ink":"#0F1720","--ink2":"#33475A",
      "--muted":"#5E7285","--faint":"#92A5B5","--line":"#CDDFEE","--track":"#CDDFEE",
      "--accent":"#0A6ED1","--cool":"#E8792B","--ok":"#2F8F63","--danger":"#CE3B3B",
      "--fill":"#0F1720","--onFill":"#F3F8FC","--segsel":"#FBFDFF","--knob":"#FFFFFF" },
    dark:{ "--bg":"#0C1219","--bg2":"#141D26","--ink":"#E4EDF5","--ink2":"#B0C2D2",
      "--muted":"#7E93A5","--faint":"#56697A","--line":"#22303C","--track":"#26333F",
      "--accent":"#4FA3F7","--cool":"#FFA05C","--ok":"#5FBC8D","--danger":"#E87C7C",
      "--fill":"#E4EDF5","--onFill":"#0C1219","--segsel":"#33465A","--knob":"#EFF6FC" }
  },
  "bahar": {
    light:{ "--bg":"#F8FBF4","--bg2":"#ECF5E2","--ink":"#14180F","--ink2":"#3A452E",
      "--muted":"#66735A","--faint":"#97A38B","--line":"#D6E6C5","--track":"#D6E6C5",
      "--accent":"#E0356B","--cool":"#2E9E5B","--ok":"#2E9E5B","--danger":"#C42F49",
      "--fill":"#14180F","--onFill":"#F8FBF4","--segsel":"#FCFEF9","--knob":"#FFFFFF" },
    dark:{ "--bg":"#0F1310","--bg2":"#171D16","--ink":"#E9F0E2","--ink2":"#B7C4AE",
      "--muted":"#85937C","--faint":"#5C6955","--line":"#26301F","--track":"#2B3624",
      "--accent":"#FF5C89","--cool":"#4FC77E","--ok":"#4FC77E","--danger":"#F07A8E",
      "--fill":"#E9F0E2","--onFill":"#0F1310","--segsel":"#3B4735","--knob":"#F2F8EC" }
  },
  "mor": {
    light:{ "--bg":"#FAF7FD","--bg2":"#F1EAFA","--ink":"#17131F","--ink2":"#3F3550",
      "--muted":"#6B5F80","--faint":"#9D93AE","--line":"#DFD3EF","--track":"#DFD3EF",
      "--accent":"#7B3FE4","--cool":"#D98A00","--ok":"#3E8F6B","--danger":"#C93B67",
      "--fill":"#17131F","--onFill":"#FAF7FD","--segsel":"#FDFBFF","--knob":"#FFFFFF" },
    dark:{ "--bg":"#110E17","--bg2":"#1A1523","--ink":"#EDE7F5","--ink2":"#C0B5D2",
      "--muted":"#8F82A5","--faint":"#635873","--line":"#2A2237","--track":"#2F2740",
      "--accent":"#A97BFF","--cool":"#F0B03C","--ok":"#63BE99","--danger":"#EC7B9F",
      "--fill":"#EDE7F5","--onFill":"#110E17","--segsel":"#453A5C","--knob":"#F6F1FE" }
  }
};

const SENARYOLAR = [
  { ad:"25 dk kesintisiz",   adim:[["basla",0],["bitir",25]] },
  { ad:"52 dk + 12 dk mola", adim:[["basla",0],["mola",52],["devam",64],["bitir",92]] },
  { ad:"3 saat, iki mola",   adim:[["basla",0],["mola",58],["devam",71],["mola",126],["devam",138],["bitir",185]] },
  { ad:"pomodoro 50",        mod:"pomodoro", sure:50, adim:[["basla",0],["bitir",56]] },
  { ad:"5 saat — akış dolar", adim:[["basla",0],["mola",70],["devam",85],["mola",170],["devam",182],["bitir",300]] }
];

/* Üst sınır kare hızına bağlı: kare başına en çok bir sanal dakika ilerliyor,
   yani 60 fps'de tavan pratikte ~3600×. */
const HIZLAR = [["dur",0],["1×",1],["10×",10],["60×",60],["300×",300],["1800×",1800]];
const ATLAMALAR = [["+1 dk",6e4],["+10 dk",6e5],["+1 saat",36e5],["+1 gün",864e5]];
const SEKMELER = [["sayaç","timer"],["görevler","tasks"],["kayıt","log"],["ayarlar","settings"]];

/* ---------------- kurulum ---------------- */
let fr = document.getElementById("fr");
let paletAd = "kâğıt", tema = "system", hiz = 0, tohum = 7, akisYonu = "ebru";

function aktifKoyuMu() {
  if (tema === "dark") return true;
  if (tema === "light") return false;
  return !!(window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches);
}

/* Her kurulumda çerçeve baştan yaratılıyor: eski pencerede dönen sanal saat
   döngüsü de onunla birlikte gidiyor. srcdoc yerine document.write, çünkü
   about:blank çerçevesi ana sayfanın kökenini miras alıyor — dosyadan
   çift tıklayıp açtığında da çalışıyor. */
function kur() {
  const uyg = document.getElementById("app-src").value;
  const kabuk = KABUK.replace("SIM_TOHUM", String(tohum));
  const yeni = document.createElement("iframe");
  yeni.id = "fr"; yeni.title = "Kertik";
  fr.parentNode.replaceChild(yeni, fr);
  fr = yeni;
  const doc = fr.contentDocument;
  doc.open();
  doc.write(uyg.replace(/<body>/i, "<body>\n" + kabuk));
  doc.close();
  setTimeout(() => {
    gonder({ tip: "tema", v: tema });
    const pv = aktifKoyuMu() ? "dark" : "light";
    gonder({ tip: "palet", v: PALETLER[paletAd] ? PALETLER[paletAd][pv] : null });
    gonder({ tip: "akisyon", v: akisYonu });
  }, 120);
}
function gonder(m) { try { fr.contentWindow.postMessage(m, "*"); } catch (e) {} }

function chipler(kutu, liste, secili, tik) {
  kutu.innerHTML = "";
  liste.forEach((x, i) => {
    const b = document.createElement("button");
    b.textContent = x[0];
    if (secili === i) b.classList.add("on");
    b.onclick = () => tik(x, i);
    kutu.appendChild(b);
  });
}

function hizCiz() {
  chipler(document.getElementById("hiz"), HIZLAR,
    HIZLAR.findIndex(h => h[1] === hiz),
    x => { hiz = x[1]; gonder({ tip:"hiz", v:hiz }); hizCiz(); });
}
hizCiz();

chipler(document.getElementById("atla"), ATLAMALAR, -1,
  x => gonder({ tip:"atla", v:x[1] }));

(function(){
  const kutu = document.getElementById("sekme");
  function ciz(sec){
    chipler(kutu, SEKMELER, sec, (x, i) => { gonder({ tip:"sekme", v:x[1] }); ciz(i); });
  }
  ciz(0);
})();

(function(){
  const kutu = document.getElementById("senaryo");
  kutu.innerHTML = "";
  SENARYOLAR.forEach(s => {
    const b = document.createElement("button");
    b.textContent = s.ad; b.className = "ana";
    b.onclick = () => {
      hiz = 300; hizCiz();
      gonder({ tip:"senaryo", v:s, hiz:300 });
    };
    kutu.appendChild(b);
  });
  const d = document.createElement("button");
  d.textContent = "durdur";
  d.onclick = () => { hiz = 0; hizCiz(); gonder({ tip:"dur" }); };
  kutu.appendChild(d);
})();

const AKIS_YONLERI = [["sade","sade"],["belirgin","belirgin"],["ebru","ebru"]];
(function(){
  const kutu = document.getElementById("akisyon");
  function ciz(){
    chipler(kutu, AKIS_YONLERI, AKIS_YONLERI.findIndex(x => x[1] === akisYonu),
      x => { akisYonu = x[1]; gonder({ tip:"akisyon", v:akisYonu }); ciz(); });
  }
  ciz();
})();

(function(){
  const kutu = document.getElementById("palet");
  function ciz(){
    kutu.innerHTML = "";
    const pv = aktifKoyuMu() ? "dark" : "light";
    Object.keys(PALETLER).forEach(ad => {
      const b = document.createElement("button");
      const p = PALETLER[ad];
      const renk = p ? p[pv]["--accent"] : (pv === "dark" ? "#D0785B" : "#B05237");
      const s = document.createElement("span");
      s.className = "sw"; s.style.background = renk;
      b.appendChild(s);
      b.appendChild(document.createTextNode(ad));
      if (ad === paletAd) b.classList.add("on");
      b.onclick = () => { paletAd = ad;
        gonder({ tip:"palet", v: PALETLER[ad] ? PALETLER[ad][pv] : null }); ciz(); };
      kutu.appendChild(b);
    });
  }
  ciz();

  const tk = document.getElementById("tema");
  const TEMA_LISTESI = [["sistem", "system"], ["açık", "light"], ["karanlık", "dark"]];
  function temaCiz(){
    const seciliIdx = Math.max(0, TEMA_LISTESI.findIndex(x => x[1] === tema));
    chipler(tk, TEMA_LISTESI,
      seciliIdx,
      x => {
        tema = x[1];
        gonder({ tip:"tema", v:tema });
        setTimeout(() => {
          const pv = aktifKoyuMu() ? "dark" : "light";
          gonder({ tip:"palet", v: PALETLER[paletAd] ? PALETLER[paletAd][pv] : null });
        }, 60);
        temaCiz(); ciz();
      });
  }
  temaCiz();

  if (window.matchMedia) {
    try {
      const mq = window.matchMedia("(prefers-color-scheme: dark)");
      const mqHandler = () => {
        if (tema === "system") {
          gonder({ tip:"tema", v:"system" });
          const pv = mq.matches ? "dark" : "light";
          gonder({ tip:"palet", v: PALETLER[paletAd] ? PALETLER[paletAd][pv] : null });
          ciz();
        }
      };
      if (mq.addEventListener) mq.addEventListener("change", mqHandler);
      else if (mq.addListener) mq.addListener(mqHandler);
    } catch (_) {}
  }
})();

document.getElementById("yenile").onclick = () => {
  tohum = Math.floor(Math.random() * 1e6);
  hiz = 0; hizCiz();
  document.getElementById("hata").classList.remove("on");
  kur();
};

/* ---------------- durum okuması ---------------- */
const oku = document.getElementById("oku");
const sure = ms => {
  if (ms == null) return "—";
  const t = Math.floor(ms / 1000), h = Math.floor(t / 3600),
        m = Math.floor(t % 3600 / 60), s = t % 60;
  const p = n => String(n).padStart(2, "0");
  return (h ? h + ":" : "") + p(m) + ":" + p(s);
};
let sonDurum = null;
addEventListener("message", e => {
  const d = e.data || {};
  if (d.tip === "hata") {
    const h = document.getElementById("hata");
    h.textContent = "Uygulamadan hata: " + d.mesaj;
    h.classList.add("on");
    return;
  }
  if (d.tip !== "durum") return;
  sonDurum = d;
});

setInterval(() => {
  const d = sonDurum; if (!d) return;
  const saat = new Date(d.t);
  const p = n => String(n).padStart(2, "0");
  const sat = (k, v, acc) =>
    '<div class="sat"><span class="k">' + k + '</span><span class="v' +
    (acc ? " acc" : "") + '">' + v + "</span></div>";
  let h = "";
  h += sat("sanal saat", saat.toLocaleDateString("tr-TR", { day:"numeric", month:"long" }) +
       " " + p(saat.getHours()) + ":" + p(saat.getMinutes()) + ":" + p(saat.getSeconds()));
  h += sat("hız", d.hiz ? d.hiz + "×" : "durdu", !!d.hiz);
  h += sat("seans", d.aktif ? (d.molada ? "molada" : "çalışıyor") + " · " + d.mod : "yok", d.aktif);
  if (d.aktif) {
    h += sat("geçen", sure(d.gecen));
    h += sat("çalışma", sure(d.net), true);
    h += sat("mola", sure(d.mola));
  }
  h += sat("biten seans", d.seansSayisi == null ? "—" : d.seansSayisi);
  if (d.akis) h += sat("akış", d.akis.hazir
    ? d.akis.ciz + " / " + d.akis.serit + " şerit · " + d.akis.yon
    : (d.aktif ? "hesaplanıyor…" : "kapalı"));
  oku.innerHTML = h;
}, 100);

kur();
</script>
</body>
</html>
`;

/* Kabuk bir JS dizesi olarak panelin <script> bloğuna gömülüyor. İçinde
   </script> geçiyor (kabuğun kendi kapanış etiketi); kaçırılmazsa HTML
   çözümleyici paneli orada kapatır. JSON.stringify eğik çizgiyi kaçırmaz. */
const kabukDize = JSON.stringify(KABUK).replace(/<\//g, "<\\/");

const cikti = PANEL
  .replace("__UYGULAMA__", () => gomulu)
  .replace("__KABUK__", () => kabukDize);

fs.writeFileSync(HEDEF, cikti, "utf8");
console.log("yazıldı: " + path.relative(KOK, HEDEF) +
  "  (" + (cikti.length / 1024).toFixed(0) + " KB)");
