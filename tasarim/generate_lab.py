# -*- coding: utf-8 -*-
import os

html = """<!doctype html>
<html lang="tr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Kertik — Çizim ve Renk Laboratuvarı</title>
<style>
:root {
  --bg: #141518;
  --bg2: #1D1E23;
  --card: #24262D;
  --ink: #F0ECE1;
  --ink2: #C8C3B7;
  --muted: #8E8A80;
  --faint: #5E5B54;
  --line: #32353E;
  --track: #383B46;
  
  --acc: #D0785B;
  --acc-light: #E5A38D;
  --acc-deep: #8E3A24;
  --cool: #79B3AE;
  --cool-light: #A4D0CB;
  --cool-deep: #3B6B67;
}

:root.light {
  --bg: #F5F2EA;
  --bg2: #EFEBE1;
  --card: #E5E0D3;
  --ink: #16181B;
  --ink2: #3E4148;
  --muted: #726E65;
  --faint: #9C978C;
  --line: #DCD5C6;
  --track: #DCD6C7;
  
  --acc: #B05237;
  --acc-light: #D9836C;
  --acc-deep: #6E2916;
  --cool: #3E7C77;
  --cool-light: #72ACA7;
  --cool-deep: #1F4C48;
}

* { box-sizing: border-box; -webkit-tap-highlight-color: transparent; }
html, body { margin: 0; min-height: 100%; }
body {
  background: var(--bg);
  color: var(--ink);
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, system-ui, sans-serif;
  font-size: 15px;
  line-height: 1.5;
  -webkit-font-smoothing: antialiased;
  padding: 32px 20px 80px;
  transition: background .4s ease, color .4s ease;
}

.header-wrap {
  max-width: 1240px;
  margin: 0 auto 28px;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  flex-wrap: wrap;
  gap: 16px;
}
.title-area h1 {
  font-size: 28px;
  font-weight: 500;
  letter-spacing: -.03em;
  margin: 0 0 6px;
}
.title-area p {
  color: var(--muted);
  font-size: 14.5px;
  margin: 0;
  max-width: 74ch;
}
.header-actions {
  display: flex;
  gap: 10px;
}

.main-layout {
  max-width: 1240px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 28px;
}
@media (max-width: 960px) {
  .main-layout { grid-template-columns: 1fr; }
}

.phone-card {
  background: var(--bg2);
  border: 1px solid var(--line);
  border-radius: 28px;
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 18px;
  box-shadow: 0 12px 36px rgba(0,0,0,.22);
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.card-badge {
  font-size: 12px;
  letter-spacing: .1em;
  text-transform: uppercase;
  font-weight: 600;
  padding: 5px 12px;
  border-radius: 999px;
  background: var(--track);
  color: var(--acc);
}
.card-meta {
  font-size: 13.5px;
  color: var(--muted);
}

.phone-view {
  position: relative;
  width: 100%;
  aspect-ratio: 9 / 17.5;
  max-height: 560px;
  background: var(--bg);
  border-radius: 24px;
  overflow: hidden;
  border: 1px solid var(--line);
  display: flex;
  flex-direction: column;
  align-items: center;
  margin: 0 auto;
}
.phone-view canvas {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
}
.phone-ui {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 24px 18px 24px;
  pointer-events: none;
  z-index: 2;
}
.ui-state {
  font-size: 11px;
  letter-spacing: .2em;
  text-transform: uppercase;
  color: var(--acc);
  font-weight: 600;
  margin-bottom: 12px;
}
.ui-clock {
  font-size: 40px;
  font-weight: 250;
  letter-spacing: -.04em;
  font-variant-numeric: tabular-nums;
  line-height: 1;
  color: var(--ink);
  margin-bottom: 4px;
}
.ui-caption {
  font-size: 12px;
  color: var(--muted);
}
.ui-footer {
  margin-top: auto;
  font-size: 12px;
  color: var(--muted);
  background: rgba(0,0,0,0.45);
  padding: 5px 14px;
  border-radius: 999px;
  backdrop-filter: blur(8px);
}
:root.light .ui-footer {
  background: rgba(255,255,255,0.7);
}

.info-box {
  background: var(--card);
  border: 1px solid var(--line);
  border-radius: 16px;
  padding: 14px 16px;
  font-size: 13.5px;
  line-height: 1.6;
}
.info-box b { color: var(--ink); font-weight: 600; }
.info-box span.highlight { color: var(--acc); font-weight: 500; }

.controls-panel {
  max-width: 1240px;
  margin: 28px auto 0;
  background: var(--bg2);
  border: 1px solid var(--line);
  border-radius: 24px;
  padding: 24px;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 24px;
}
.ctrl-group h3 {
  font-size: 12px;
  letter-spacing: .12em;
  text-transform: uppercase;
  color: var(--muted);
  margin: 0 0 12px;
  font-weight: 600;
}
.ctrl-row {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  align-items: center;
}

button {
  border: 1px solid var(--line);
  background: var(--card);
  color: var(--ink2);
  border-radius: 999px;
  padding: 8px 16px;
  font-size: 13.5px;
  font-family: inherit;
  cursor: pointer;
  transition: all .2s ease;
}
button:hover {
  border-color: var(--muted);
  color: var(--ink);
}
button.active {
  background: var(--acc);
  border-color: var(--acc);
  color: #fff;
  font-weight: 600;
}
:root.light button.active {
  color: #fff;
}
button.ghost {
  background: transparent;
}

.scrubber-wrap {
  width: 100%;
}
input[type=range] {
  width: 100%;
  height: 6px;
  border-radius: 999px;
  background: var(--track);
  accent-color: var(--acc);
  outline: none;
  margin: 10px 0;
}
.slider-labels {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: var(--muted);
  font-variant-numeric: tabular-nums;
}

.palette-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 12px;
}
.pal-dots {
  display: flex;
  gap: 4px;
}
.pal-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
}

.tag-list {
  display: flex;
  gap: 6px;
  margin-top: 8px;
  flex-wrap: wrap;
}
.tag {
  font-size: 11px;
  padding: 3px 9px;
  border-radius: 6px;
  background: var(--track);
  color: var(--muted);
}
.tag.active {
  background: rgba(208, 120, 91, 0.2);
  color: var(--acc);
  border: 1px solid var(--acc);
  font-weight: 500;
}
</style>
</head>
<body>

<div class="header-wrap">
  <div class="title-area">
    <h1>Kertik — Çizim ve Renk Laboratuvarı</h1>
    <p>Pomodoro (hedefe kilitli tam kompozisyon) ve Kronometre (ucu açık fraktal büyüme) modellerini canlı kıyasla. Zamanı sürükle, hızlandır, mola ekle ve harmonik renk tonlarını test et.</p>
  </div>
  <div class="header-actions">
    <button id="themeToggle">🌓 Tema Değiştir</button>
    <button id="newSeedBtn">🎲 Yeni Tohum</button>
  </div>
</div>

<div class="main-layout">
  
  <!-- SOL KART: POMODORO -->
  <div class="phone-card">
    <div class="card-header">
      <span class="card-badge">🍅 Pomodoro Modu</span>
      <span class="card-meta" id="pomoMeta">Hedef: 25 dk</span>
    </div>

    <div class="phone-view">
      <canvas id="pomoCanvas"></canvas>
      <div class="phone-ui">
        <div class="ui-state" id="pomoState">ÇALIŞIYOR</div>
        <div class="ui-clock" id="pomoClock">00:00</div>
        <div class="ui-caption" id="pomoCapt">0 / 25 çentik</div>
        <div class="ui-footer" id="pomoFooter">İskelet Aşaması (%0)</div>
      </div>
    </div>

    <div class="info-box">
      <b>Çizim Prensibi:</b> <span class="highlight">Teleolojik (Hedefe Ölçekli)</span><br>
      Süre seçilen hedefe (25/50/90 dk) göre normalize edilir. Hedefe ulaşıldığında (%100) tablo eksiksiz kapanır. Süre aşılırsa (+fazla çalışma) dışa altın/serin aura ışıltısı işlenir.
      <div class="tag-list" id="pomoStages">
        <span class="tag" id="pstg1">1. İskelet (%0-25)</span>
        <span class="tag" id="pstg2">2. Gövde/Akış (%25-70)</span>
        <span class="tag" id="pstg3">3. Kılcal & Gölge (%70-99)</span>
        <span class="tag" id="pstg4">4. Mühür / Tamam (%100)</span>
      </div>
    </div>
  </div>

  <!-- SAĞ KART: KRONOMETRE -->
  <div class="phone-card">
    <div class="card-header">
      <span class="card-badge">⏱️ Kronometre Modu</span>
      <span class="card-meta" id="kronoMeta">Açık Uçlu Akış</span>
    </div>

    <div class="phone-view">
      <canvas id="kronoCanvas"></canvas>
      <div class="phone-ui">
        <div class="ui-state" id="kronoState">ÇALIŞIYOR</div>
        <div class="ui-clock" id="kronoClock">00:00</div>
        <div class="ui-caption" id="kronoCapt">1. saat, 0. çentik</div>
        <div class="ui-footer" id="kronoFooter">Çekirdek Form (0. Dk)</div>
      </div>
    </div>

    <div class="info-box">
      <b>Çizim Prensibi:</b> <span class="highlight">Morfogenetik (Organik Büyüme)</span><br>
      Sabit bitiş tavanı yoktur. 15. dakikada minik ama eksiksiz bir çekirdektir; 60. ve 120. dakikalarda merkezden dışa doğru yaş halkaları, yeni akış kolları ve derinleşen mürekkep damarlarıyla evrilir.
      <div class="tag-list" id="kronoStages">
        <span class="tag" id="kstg1">Çekirdek (0-20dk)</span>
        <span class="tag" id="kstg2">1. Halka (20-50dk)</span>
        <span class="tag" id="kstg3">2. Halka & Çatallanma (50-90dk)</span>
        <span class="tag" id="kstg4">Derin Orman / Kozmos (90dk+)</span>
      </div>
    </div>
  </div>

</div>

<!-- ALT KUMANDA PANELİ -->
<div class="controls-panel">
  
  <!-- Zaman Çubuğu -->
  <div class="ctrl-group" style="grid-column: 1 / -1;">
    <h3>Zaman İlerlemesi & Kıyaslama Çubuğu</h3>
    <div class="scrubber-wrap">
      <input type="range" id="timeSlider" min="0" max="180" value="25" step="0.5">
      <div class="slider-labels">
        <span>0 dk (Başlangıç)</span>
        <span>25 dk (Pomo 1)</span>
        <span>50 dk (Pomo 2)</span>
        <span>90 dk (Pomo 3)</span>
        <span>120 dk (2 Saat)</span>
        <span>180 dk (3 Saat)</span>
      </div>
    </div>
  </div>

  <!-- Pomodoro Hedefi Seçimi -->
  <div class="ctrl-group">
    <h3>Pomodoro Hedefi</h3>
    <div class="ctrl-row">
      <button class="active" data-target="25">25 dk</button>
      <button data-target="50">50 dk</button>
      <button data-target="90">90 dk</button>
    </div>
  </div>

  <!-- Hız & Simülasyon -->
  <div class="ctrl-group">
    <h3>Canlı Akış Hızı</h3>
    <div class="ctrl-row">
      <button class="active" data-speed="0">Durdur</button>
      <button data-speed="1">1×</button>
      <button data-speed="10">10×</button>
      <button data-speed="60">60×</button>
      <button data-speed="300">300×</button>
    </div>
  </div>

  <!-- Mola Simülatörü -->
  <div class="ctrl-group">
    <h3>Mola Simülasyonu</h3>
    <div class="ctrl-row">
      <button id="toggleBreakBtn">☕ Molaya Gir / Çık</button>
      <button id="addBreak5Btn" class="ghost">+5 dk Mola Ekle</button>
    </div>
  </div>

  <!-- Renk Paletleri -->
  <div class="ctrl-group" style="grid-column: 1 / -1;">
    <h3>Harmonik Renk Paletleri (Tohumlu & Katmanlı)</h3>
    <div class="ctrl-row">
      <button class="palette-btn active" data-pal="klasik">
        <div class="pal-dots">
          <div class="pal-dot" style="background:#B05237"></div>
          <div class="pal-dot" style="background:#D99B56"></div>
          <div class="pal-dot" style="background:#3E7C77"></div>
        </div>
        1. Kâğıt & Pişmiş Toprak (Klasik)
      </button>

      <button class="palette-btn" data-pal="orman">
        <div class="pal-dots">
          <div class="pal-dot" style="background:#C39A55"></div>
          <div class="pal-dot" style="background:#E0B86C"></div>
          <div class="pal-dot" style="background:#4E7855"></div>
        </div>
        2. Yanık Hardal & Orman (Dingin)
      </button>

      <button class="palette-btn" data-pal="maden">
        <div class="pal-dots">
          <div class="pal-dot" style="background:#D0785B"></div>
          <div class="pal-dot" style="background:#A8462F"></div>
          <div class="pal-dot" style="background:#3B5B82"></div>
        </div>
        3. Bakır & Gece Mavisi (Derin)
      </button>

      <button class="palette-btn" data-pal="sarap">
        <div class="pal-dots">
          <div class="pal-dot" style="background:#A64B58"></div>
          <div class="pal-dot" style="background:#C76D5B"></div>
          <div class="pal-dot" style="background:#6C8294"></div>
        </div>
        4. Koyu Gül & Arduvaz (Rafine)
      </button>
    </div>
  </div>

</div>

<script>
/* 1. MATEMATİK & RASTGELELİK */
function h2i(i, j, s) {
  let n = Math.imul(i | 0, 374761393) ^ Math.imul(j | 0, 668265263) ^ Math.imul(s | 0, 362437);
  n = Math.imul(n ^ (n >>> 13), 1274126177);
  return ((n ^ (n >>> 16)) >>> 0) / 4294967296;
}

function vnoise(x, y, s) {
  const i = Math.floor(x), j = Math.floor(y), fx = x - i, fy = y - j;
  const u = fx * fx * (3 - 2 * fx), v = fy * fy * (3 - 2 * fy);
  const a = h2i(i, j, s), b = h2i(i + 1, j, s), c = h2i(i, j + 1, s), d = h2i(i + 1, j + 1, s);
  return (a * (1 - u) + b * u) * (1 - v) + (c * (1 - u) + d * u) * v;
}

function fbm(x, y, s) {
  return vnoise(x, y, s) * 0.6 + vnoise(x * 2.1, y * 2.1, s + 7) * 0.27 + vnoise(x * 4.3, y * 4.3, s + 19) * 0.13;
}

function rng32(seed) {
  let s = seed >>> 0;
  return function() {
    s = (s + 0x6D2B79F5) | 0;
    let t = Math.imul(s ^ (s >>> 15), 1 | s);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

/* 2. HARMONİK PALETLER */
const PALETLER = {
  klasik: {
    ad: "Kâğıt & Pişmiş Toprak",
    calisma: {
      acik: "#D99B56",
      orta: "#B05237",
      koyu: "#6B2D1B",
      yikama: "rgba(176, 82, 55, 0.08)"
    },
    mola: {
      acik: "#8FAFA8",
      orta: "#3E7C77",
      koyu: "#1E3F3D",
      yikama: "rgba(62, 124, 119, 0.14)"
    }
  },
  orman: {
    ad: "Hardal & Orman",
    calisma: {
      acik: "#E0B86C",
      orta: "#C39A55",
      koyu: "#4E3524",
      yikama: "rgba(195, 154, 85, 0.08)"
    },
    mola: {
      acik: "#7FA886",
      orta: "#4E7855",
      koyu: "#2D4A33",
      yikama: "rgba(78, 120, 85, 0.14)"
    }
  },
  maden: {
    ad: "Bakır & Gece Mavisi",
    calisma: {
      acik: "#E59882",
      orta: "#D0785B",
      koyu: "#8A3622",
      yikama: "rgba(208, 120, 91, 0.08)"
    },
    mola: {
      acik: "#6E93BA",
      orta: "#3B5B82",
      koyu: "#1C2A3D",
      yikama: "rgba(59, 91, 130, 0.16)"
    }
  },
  sarap: {
    ad: "Koyu Gül & Arduvaz",
    calisma: {
      acik: "#C76D5B",
      orta: "#A64B58",
      koyu: "#5C242E",
      yikama: "rgba(166, 75, 88, 0.09)"
    },
    mola: {
      acik: "#9BB3C4",
      orta: "#6C8294",
      koyu: "#435360",
      yikama: "rgba(108, 130, 148, 0.14)"
    }
  }
};

let seciliPalet = "klasik";
let genelTohum = 42819;

let durum = {
  gecenDakika: 25.0,
  pomoHedef: 25,
  hiz: 0,
  molaVarMi: false,
  molaAraliklari: [[12, 15]],
  sonGuncelleme: performance.now()
};

/* 3. POMODORO ÇİZİM MOTORU */
function pomoAlanUret(seed, W, H) {
  const R = rng32(seed);
  const DSEP = 2.0, STEP = 2.2, MAXL = 600;
  const gw = Math.ceil(W / DSEP) + 2, gh = Math.ceil(H / DSEP) + 2;
  const dolu = new Uint8Array(gw * gh);
  
  const aci = (x, y) => (fbm(x / (W / 2.6), y / (W / 2.6), seed) * 2 - 1) * Math.PI * 1.8
                      + (fbm(x / (W / 6.0), y / (W / 6.0), seed + 3) - 0.5) * 1.1;

  const bosMu = (x, y) => {
    const gi = (x / DSEP | 0) + 1, gj = (y / DSEP | 0) + 1;
    if (gi < 0 || gj < 0 || gi >= gw || gj >= gh) return false;
    for (let a = -1; a <= 1; a++) for (let b = -1; b <= 1; b++) {
      const q = (gj + b) * gw + (gi + a);
      if (q >= 0 && q < dolu.length && dolu[q]) return false;
    }
    return true;
  };

  const isaretle = (x, y) => {
    const gi = (x / DSEP | 0) + 1, gj = (y / DSEP | 0) + 1;
    if (gi >= 0 && gj >= 0 && gi < gw && gj < gh) dolu[gj * gw + gi] = 1;
  };

  const denemeler = [];
  for (let i = 0; i < 18000; i++) {
    const x = R() * W, y = R() * H;
    denemeler.push({ x, y, o: fbm(x / (W / 4), y / (W / 4), seed + 41) * 0.75 + R() * 0.25 });
  }
  denemeler.sort((a, b) => a.o - b.o);

  const seritler = [];
  for (const d of denemeler) {
    if (!bosMu(d.x, d.y)) continue;
    let pts = [];
    for (const yon of [1, -1]) {
      let x = d.x, y = d.y; const par = [];
      for (let k = 0; k < MAXL / STEP; k++) {
        const a = aci(x, y);
        x += Math.cos(a) * STEP * yon; y += Math.sin(a) * STEP * yon;
        if (x < -20 || y < -20 || x > W + 20 || y > H + 20) break;
        if (k > 2 && !bosMu(x, y)) break;
        par.push(x, y);
      }
      if (yon === 1) pts.push(...par);
      else {
        const rev = [];
        for (let k = par.length - 2; k >= 0; k -= 2) rev.push(par[k], par[k + 1]);
        pts.unshift(...rev);
      }
    }
    if (pts.length < 14) continue;
    for (let k = 0; k < pts.length; k += 2) isaretle(pts[k], pts[k + 1]);
    seritler.push(Float32Array.from(pts));
  }
  return seritler;
}

function cizPomo(ctx, W, H, seritler, dakika, hedef, molaAraliklari, pal) {
  ctx.clearRect(0, 0, W, H);
  const oran = Math.min(1.0, dakika / hedef);
  const toplam = seritler.length;
  const cizilecek = Math.floor(toplam * oran);
  const koyuMod = !document.documentElement.classList.contains("light");

  ctx.lineCap = "round";
  ctx.lineJoin = "round";

  for (let i = 0; i < cizilecek; i++) {
    const dkKonum = (i / toplam) * hedef;
    let mola = false;
    for (const m of molaAraliklari) {
      if (dkKonum >= m[0] && dkKonum <= m[1]) { mola = true; break; }
    }

    const p = seritler[i];
    const siraOran = i / toplam;
    const renkAilesi = mola ? pal.mola : pal.calisma;

    let renk = renkAilesi.orta;
    let kalinlik = 1.1;
    let alfa = koyuMod ? 0.35 : 0.28;

    if (siraOran < 0.60) {
      renk = renkAilesi.acik;
      kalinlik = 0.85;
      alfa = koyuMod ? 0.22 : 0.16;
    } else if (siraOran < 0.88) {
      renk = renkAilesi.orta;
      kalinlik = 1.35;
      alfa = koyuMod ? 0.42 : 0.35;
    } else {
      renk = renkAilesi.koyu;
      kalinlik = 2.2;
      alfa = koyuMod ? 0.65 : 0.55;
    }

    if (mola) {
      ctx.beginPath();
      ctx.moveTo(p[0], p[1]);
      for (let k = 2; k < p.length; k += 2) ctx.lineTo(p[k], p[k + 1]);
      ctx.strokeStyle = pal.mola.yikama;
      ctx.lineWidth = kalinlik * 3.5;
      ctx.stroke();
    }

    ctx.beginPath();
    ctx.moveTo(p[0], p[1]);
    for (let k = 2; k < p.length; k += 2) ctx.lineTo(p[k], p[k + 1]);
    ctx.strokeStyle = renk;
    ctx.globalAlpha = alfa;
    ctx.lineWidth = kalinlik;
    ctx.stroke();
  }

  if (dakika > hedef) {
    const fazlaDk = dakika - hedef;
    const auraAlpha = Math.min(0.45, fazlaDk * 0.03);
    const radyal = ctx.createRadialGradient(W / 2, H / 2, 40, W / 2, H / 2, W * 0.7);
    radyal.addColorStop(0, "rgba(255, 215, 0, 0)");
    radyal.addColorStop(0.7, "rgba(255, 215, 0, " + (auraAlpha * 0.15) + ")");
    radyal.addColorStop(1, "rgba(208, 120, 91, " + (auraAlpha * 0.25) + ")");
    ctx.fillStyle = radyal;
    ctx.globalAlpha = 1;
    ctx.fillRect(0, 0, W, H);
  }

  ctx.globalCompositeOperation = "destination-out";
  const cx = W / 2, cy = H * 0.28, r = W * 0.30;
  const gr = ctx.createRadialGradient(cx, cy, r * 0.5, cx, cy, r);
  gr.addColorStop(0, "rgba(0,0,0,1)");
  gr.addColorStop(1, "rgba(0,0,0,0)");
  ctx.fillStyle = gr;
  ctx.fillRect(cx - r, cy - r, r * 2, r * 2);
  ctx.globalCompositeOperation = "source-over";
}

/* 4. KRONOMETRE ÇİZİM MOTORU */
function kronoAlanUret(seed, W, H) {
  const R = rng32(seed + 999);
  const seritler = [];
  
  for (let katman = 1; katman <= 4; katman++) {
    const dsep = katman === 1 ? 3.0 : (katman === 2 ? 2.2 : 1.7);
    const step = 2.0;
    const maxl = katman * 180 + 100;
    const gw = Math.ceil(W / dsep) + 2, gh = Math.ceil(H / dsep) + 2;
    const dolu = new Uint8Array(gw * gh);

    const f1 = 2.0 * katman, f2 = 4.5 * katman;
    const aci = (x, y) => (fbm(x / (W / f1), y / (W / f1), seed + katman * 10) * 2 - 1) * Math.PI * 1.8
                        + (fbm(x / (W / f2), y / (W / f2), seed + 50) - 0.5) * 1.0;

    const bosMu = (x, y) => {
      const gi = (x / dsep | 0) + 1, gj = (y / dsep | 0) + 1;
      if (gi < 0 || gj < 0 || gi >= gw || gj >= gh) return false;
      for (let a = -1; a <= 1; a++) for (let b = -1; b <= 1; b++) {
        const q = (gj + b) * gw + (gi + a);
        if (q >= 0 && q < dolu.length && dolu[q]) return false;
      }
      return true;
    };

    const isaretle = (x, y) => {
      const gi = (x / dsep | 0) + 1, gj = (y / dsep | 0) + 1;
      if (gi >= 0 && gj >= 0 && gi < gw && gj < gh) dolu[gj * gw + gi] = 1;
    };

    const denemeSayisi = katman * 4000;
    const denemeler = [];
    for (let i = 0; i < denemeSayisi; i++) {
      const x = R() * W, y = R() * H;
      const dx = x - W/2, dy = y - H/2;
      const dist = Math.sqrt(dx*dx + dy*dy) / (W*0.6);
      let agirlik = fbm(x / 50, y / 50, seed) * 0.6;
      if (katman === 1) agirlik += (1 - Math.min(1, dist)) * 0.4;
      else if (katman >= 3) agirlik += Math.min(1, dist) * 0.4;
      denemeler.push({ x, y, o: agirlik });
    }
    denemeler.sort((a, b) => a.o - b.o);

    const katmanSeritleri = [];
    for (const d of denemeler) {
      if (!bosMu(d.x, d.y)) continue;
      let pts = [];
      for (const yon of [1, -1]) {
        let x = d.x, y = d.y; const par = [];
        for (let k = 0; k < maxl / step; k++) {
          const a = aci(x, y);
          x += Math.cos(a) * step * yon; y += Math.sin(a) * step * yon;
          if (x < -20 || y < -20 || x > W + 20 || y > H + 20) break;
          if (k > 2 && !bosMu(x, y)) break;
          par.push(x, y);
        }
        if (yon === 1) pts.push(...par);
        else {
          const rev = [];
          for (let k = par.length - 2; k >= 0; k -= 2) rev.push(par[k], par[k + 1]);
          pts.unshift(...rev);
        }
      }
      if (pts.length < 14) continue;
      for (let k = 0; k < pts.length; k += 2) isaretle(pts[k], pts[k + 1]);
      katmanSeritleri.push(Float32Array.from(pts));
    }
    seritler.push({ katman: katman, seritler: katmanSeritleri });
  }
  return seritler;
}

function cizKrono(ctx, W, H, katmanliSeritler, dakika, molaAraliklari, pal) {
  ctx.clearRect(0, 0, W, H);
  const koyuMod = !document.documentElement.classList.contains("light");

  ctx.lineCap = "round";
  ctx.lineJoin = "round";

  const katmanSureleri = [
    { bas: 0, bit: 20 },
    { bas: 20, bit: 50 },
    { bas: 50, bit: 90 },
    { bas: 90, bit: 180 }
  ];

  katmanliSeritler.forEach((kObj, idx) => {
    const kAralik = katmanSureleri[idx];
    if (dakika < kAralik.bas) return;

    const kOran = Math.min(1.0, (dakika - kAralik.bas) / (kAralik.bit - kAralik.bas));
    const cizSayi = Math.floor(kObj.seritler.length * kOran);

    for (let i = 0; i < cizSayi; i++) {
      const p = kObj.seritler[i];
      const gercekDk = kAralik.bas + (i / kObj.seritler.length) * (kAralik.bit - kAralik.bas);
      
      let mola = false;
      for (const m of molaAraliklari) {
        if (gercekDk >= m[0] && gercekDk <= m[1]) { mola = true; break; }
      }

      const renkAilesi = mola ? pal.mola : pal.calisma;
      let renk = renkAilesi.orta;
      let kalinlik = 1.0;
      let alfa = koyuMod ? 0.30 : 0.22;

      if (idx === 0) {
        renk = renkAilesi.acik;
        kalinlik = 0.85;
        alfa = koyuMod ? 0.26 : 0.18;
      } else if (idx === 1) {
        renk = renkAilesi.orta;
        kalinlik = 1.2;
        alfa = koyuMod ? 0.38 : 0.30;
      } else if (idx === 2) {
        renk = renkAilesi.orta;
        kalinlik = 1.6;
        alfa = koyuMod ? 0.50 : 0.42;
      } else {
        renk = renkAilesi.koyu;
        kalinlik = 2.4;
        alfa = koyuMod ? 0.68 : 0.58;
      }

      if (mola) {
        ctx.beginPath();
        ctx.moveTo(p[0], p[1]);
        for (let k = 2; k < p.length; k += 2) ctx.lineTo(p[k], p[k + 1]);
        ctx.strokeStyle = pal.mola.yikama;
        ctx.lineWidth = kalinlik * 3.5;
        ctx.stroke();
      }

      ctx.beginPath();
      ctx.moveTo(p[0], p[1]);
      for (let k = 2; k < p.length; k += 2) ctx.lineTo(p[k], p[k + 1]);
      ctx.strokeStyle = renk;
      ctx.globalAlpha = alfa;
      ctx.lineWidth = kalinlik;
      ctx.stroke();
    }
  });

  ctx.globalCompositeOperation = "destination-out";
  const cx = W / 2, cy = H * 0.28, r = W * 0.30;
  const gr = ctx.createRadialGradient(cx, cy, r * 0.5, cx, cy, r);
  gr.addColorStop(0, "rgba(0,0,0,1)");
  gr.addColorStop(1, "rgba(0,0,0,0)");
  ctx.fillStyle = gr;
  ctx.fillRect(cx - r, cy - r, r * 2, r * 2);
  ctx.globalCompositeOperation = "source-over";
}

/* 5. LAB BAĞLANTISI VE KONTROLLER */
let pomoSeritler = null;
let kronoSeritler = null;

const pomoCv = document.getElementById("pomoCanvas");
const kronoCv = document.getElementById("kronoCanvas");
const pomoCtx = pomoCv.getContext("2d");
const kronoCtx = kronoCv.getContext("2d");

function tuvalleriKur() {
  const dpr = Math.min(2, window.devicePixelRatio || 1);
  const w = 300;
  const h = 600;
  
  pomoCv.width = w * dpr; pomoCv.height = h * dpr;
  kronoCv.width = w * dpr; kronoCv.height = h * dpr;
  
  pomoCtx.setTransform(dpr, 0, 0, dpr, 0, 0);
  kronoCtx.setTransform(dpr, 0, 0, dpr, 0, 0);

  pomoSeritler = pomoAlanUret(genelTohum, w, h);
  kronoSeritler = kronoAlanUret(genelTohum, w, h);
}

function clockStr(sn) {
  const m = Math.floor(sn / 60), s = Math.floor(sn % 60);
  return String(m).padStart(2, "0") + ":" + String(s).padStart(2, "0");
}

function guncelle() {
  const pal = PALETLER[seciliPalet];
  const W = 300, H = 600;
  const dk = durum.gecenDakika;

  cizPomo(pomoCtx, W, H, pomoSeritler, dk, durum.pomoHedef, durum.molaAraliklari, pal);
  
  const pomoSec = Math.floor(dk * 60);
  const pomoHedefSec = durum.pomoHedef * 60;
  const pomoOran = dk / durum.pomoHedef;
  
  document.getElementById("pomoMeta").textContent = "Hedef: " + durum.pomoHedef + " dk";
  
  if (dk <= durum.pomoHedef) {
    const kalanSec = Math.max(0, pomoHedefSec - pomoSec);
    document.getElementById("pomoClock").textContent = clockStr(kalanSec);
    document.getElementById("pomoCapt").textContent = Math.floor(dk) + " / " + durum.pomoHedef + " çentik (%" + Math.round(pomoOran * 100) + ")";
    document.getElementById("pomoState").textContent = pomoOran >= 1.0 ? "TAMAMLANDI 🎉" : "ÇALIŞIYOR";
  } else {
    const fazlaSec = pomoSec - pomoHedefSec;
    document.getElementById("pomoClock").textContent = "+" + clockStr(fazlaSec);
    document.getElementById("pomoCapt").textContent = "+" + Math.floor(dk - durum.pomoHedef) + " dk fazla çalışma (Aura)";
    document.getElementById("pomoState").textContent = "HEDEF AŞILDI 🌟";
  }

  document.getElementById("pstg1").classList.toggle("active", pomoOran < 0.25);
  document.getElementById("pstg2").classList.toggle("active", pomoOran >= 0.25 && pomoOran < 0.70);
  document.getElementById("pstg3").classList.toggle("active", pomoOran >= 0.70 && pomoOran < 1.0);
  document.getElementById("pstg4").classList.toggle("active", pomoOran >= 1.0);

  const pomoFooter = document.getElementById("pomoFooter");
  if (pomoOran < 0.25) pomoFooter.textContent = "İskelet & Temel Akış (%0-25)";
  else if (pomoOran < 0.70) pomoFooter.textContent = "Gövde & Akış Yoğunluğu (%25-70)";
  else if (pomoOran < 1.0) pomoFooter.textContent = "Kılcallar & Derinlik (%70-99)";
  else pomoFooter.textContent = "Tamamlanmış Tablo (%100 Bütünlük)";

  cizKrono(kronoCtx, W, H, kronoSeritler, dk, durum.molaAraliklari, pal);
  
  const kronoSec = Math.floor(dk * 60);
  document.getElementById("kronoClock").textContent = clockStr(kronoSec);
  const saat = Math.floor(dk / 60) + 1;
  const centik = Math.floor(dk % 60);
  document.getElementById("kronoCapt").textContent = saat + ". saat, " + centik + ". çentik";
  
  document.getElementById("kstg1").classList.toggle("active", dk < 20);
  document.getElementById("kstg2").classList.toggle("active", dk >= 20 && dk < 50);
  document.getElementById("kstg3").classList.toggle("active", dk >= 50 && dk < 90);
  document.getElementById("kstg4").classList.toggle("active", dk >= 90);

  const kronoFooter = document.getElementById("kronoFooter");
  if (dk < 20) kronoFooter.textContent = "Çekirdek Form (Eksiksiz Embriyo)";
  else if (dk < 50) kronoFooter.textContent = "1. Yaş Halkası (Radyal Genişleme)";
  else if (dk < 90) kronoFooter.textContent = "2. Halka (Fraktal Çatallanma)";
  else kronoFooter.textContent = "Derin Kozmos (Tok Mürekkep & Zengin Katmanlar)";
}

const timeSlider = document.getElementById("timeSlider");
timeSlider.addEventListener("input", e => {
  durum.gecenDakika = parseFloat(e.target.value);
  guncelle();
});

document.querySelectorAll("[data-target]").forEach(btn => {
  btn.addEventListener("click", () => {
    document.querySelectorAll("[data-target]").forEach(b => b.classList.remove("active"));
    btn.classList.add("active");
    durum.pomoHedef = parseInt(btn.dataset.target);
    guncelle();
  });
});

document.querySelectorAll("[data-speed]").forEach(btn => {
  btn.addEventListener("click", () => {
    document.querySelectorAll("[data-speed]").forEach(b => b.classList.remove("active"));
    btn.classList.add("active");
    durum.hiz = parseInt(btn.dataset.speed);
  });
});

document.querySelectorAll(".palette-btn").forEach(btn => {
  btn.addEventListener("click", () => {
    document.querySelectorAll(".palette-btn").forEach(b => b.classList.remove("active"));
    btn.classList.add("active");
    seciliPalet = btn.dataset.pal;
    guncelle();
  });
});

document.getElementById("themeToggle").addEventListener("click", () => {
  document.documentElement.classList.toggle("light");
  guncelle();
});

document.getElementById("newSeedBtn").addEventListener("click", () => {
  genelTohum = Math.floor(Math.random() * 900000) + 10000;
  tuvalleriKur();
  guncelle();
});

let molaBas = 0;
document.getElementById("toggleBreakBtn").addEventListener("click", () => {
  durum.molaVarMi = !durum.molaVarMi;
  const b = document.getElementById("toggleBreakBtn");
  b.classList.toggle("active", durum.molaVarMi);
  if (durum.molaVarMi) molaBas = durum.gecenDakika;
  else durum.molaAraliklari.push([molaBas, durum.gecenDakika]);
  guncelle();
});

document.getElementById("addBreak5Btn").addEventListener("click", () => {
  durum.molaAraliklari.push([durum.gecenDakika, durum.gecenDakika + 5]);
  durum.gecenDakika += 5;
  timeSlider.value = durum.gecenDakika;
  guncelle();
});

function animLoop(now) {
  const dt = (now - durum.sonGuncelleme) / 1000;
  durum.sonGuncelleme = now;

  if (durum.hiz > 0) {
    durum.gecenDakika += (dt * durum.hiz) / 60;
    if (durum.gecenDakika > 180) durum.gecenDakika = 0;
    timeSlider.value = durum.gecenDakika;
    guncelle();
  }
  requestAnimationFrame(animLoop);
}

tuvalleriKur();
guncelle();
requestAnimationFrame(animLoop);
</script>
</body>
</html>
"""

with open(os.path.join('tasarim', 'cizim-laboratuvari.html'), 'w', encoding='utf-8') as f:
    f.write(html)

print("tasarim/cizim-laboratuvari.html successfully generated!")
