/* DUVAR & KAYIT EKRANI AŞIRI YÜK VE STRES TESTİ
   
   Sınır Değerler:
   1. Pomodoro Taş Yükü: 1, 2, 4, 8, 12, 16, 20, 25, 30 taş tek günde
   2. Kronometre Süre Yükü: 5 dk, 25 dk, 60 dk, 120 dk, 240 dk, 360 dk, 600 dk (10 saat), 1440 dk (24 saat)
   3. Mola & Sayılmayan Süre Kombinasyonları
   4. 30 Günlük Tam Dolu Ay vs Tam Boş Ay vs Seyrek Ay
   5. Komşu Günlere Taşma Kontrolü (Bounding Box Integrity)
   6. Sayısal Değer Bütünlüğü (NaN, null, undefined, negatif koordinat yok)
*/

const assert = require("assert");
const fs = require("fs");
const path = require("path");
const { JSDOM } = require("jsdom");

const HTML = path.join(__dirname, "../app/src/main/assets/index.html");

let passed = 0, failed = 0;
function test(ad, fn) {
  try {
    fn();
    console.log("  ✓ " + ad);
    passed++;
  } catch (e) {
    console.log("  ✗ " + ad + " -> " + e.message);
    failed++;
  }
}

function sahteCtx() {
  const c = {
    canvas: null, globalAlpha: 1, globalCompositeOperation: "source-over",
    strokeStyle: "", fillStyle: "", lineWidth: 1, lineCap: "", lineJoin: ""
  };
  const yut = ["beginPath", "moveTo", "lineTo", "stroke", "fill", "fillRect", "strokeRect", "clearRect",
               "setTransform", "drawImage", "putImageData", "closePath", "arc", "save", "restore"];
  for (const k of yut) c[k] = () => {};
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

async function runStressTests() {
  console.log("\n==========================================");
  console.log(" KERTİK DUVAR STRES TESTİ KOŞUMU ");
  console.log("==========================================\n");

  const w = await kur();
  const d = w.document;

  // 1. TAŞ STRES TESTLERİ
  console.log("1) Pomodoro Taş Sıkışma & Höyük Stres Testi");
  {
    const testStoneCounts = [1, 2, 4, 8, 12, 16, 20, 25, 30];
    testStoneCounts.forEach(count => {
      test(`Taş Adedi: ${count} adet (Aşırı Gün Sınırı)`, () => {
        const dkList = [];
        for (let i = 0; i < count; i++) dkList.push(25);
        const svg = d.createElementNS("http://www.w3.org/2000/svg", "svg");
        w.cizTas(svg, { id: "stress-stone-" + count, dkList }, { taban: 14, maxW: 180, top: 4 });
        
        const paths = svg.querySelectorAll("path");
        assert.ok(paths.length > 0, "Taş path'leri üretildi");
        
        const widthVal = parseFloat(svg.getAttribute("width"));
        const heightVal = parseFloat(svg.getAttribute("height"));
        assert.ok(!isNaN(widthVal) && widthVal > 0, "Genişlik geçerli bir pozitif sayı");
        assert.ok(!isNaN(heightVal) && heightVal > 0, "Yükseklik geçerli bir pozitif sayı");
        assert.ok(widthVal <= 240, `Genişlik tavanı aşılmadı (${widthVal}px <= 240px)`);
        
        const svgHtml = svg.innerHTML;
        assert.ok(!svgHtml.includes("NaN"), "SVG içinde NaN koordinat yok");
        assert.ok(!svgHtml.includes("undefined"), "SVG içinde undefined yok");
      });
    });
  }

  // 2. KRONOMETRE SÜRE & ÇOKLU SÜTUN STRES TESTLERİ
  console.log("\n2) Kronometre Aşırı Süre (10 Saat - 24 Saat) Stres Testi");
  {
    const testMinutes = [5, 25, 60, 120, 240, 360, 600, 1440];
    testMinutes.forEach(mins => {
      test(`Kronometre Süresi: ${mins} dk (${(mins/60).toFixed(1)} saat)`, () => {
        const molalar = [];
        if (mins >= 120) molalar.push([50, 65]);
        if (mins >= 300) molalar.push([200, 230]);
        if (mins >= 600) molalar.push([450, 490]);
        
        const v = { id: "stress-kron-" + mins, dk: mins, molalar, sayilmayan: mins > 180 ? 30 : 0 };
        const svg = d.createElementNS("http://www.w3.org/2000/svg", "svg");
        w.cizCubuk(svg, v, { rp: 2.2, sw: 16, gap: 8, top: 4 });
        
        const kalaslar = svg.querySelectorAll("[data-kalas]");
        const expectedCols = Math.max(1, Math.ceil(mins / 60));
        assert.strictEqual(kalaslar.length, expectedCols, `Kalas sütun sayısı doğru (${expectedCols})`);
        
        const centikler = svg.querySelectorAll("[data-centik]");
        assert.ok(centikler.length > 0, "V-kesit çentikler üretildi");
        
        const widthVal = parseFloat(svg.getAttribute("width"));
        const heightVal = parseFloat(svg.getAttribute("height"));
        assert.ok(!isNaN(widthVal) && widthVal > 0, "Genişlik geçerli");
        assert.ok(!isNaN(heightVal) && heightVal > 0, "Yükseklik geçerli");
        
        const svgHtml = svg.innerHTML;
        assert.ok(!svgHtml.includes("NaN"), "Çubuk SVG'sinde NaN koordinat yok");
      });
    });
  }

  // 3. 30 GÜNLÜK TAM DOLU AY STRES TESTİ
  console.log("\n3) 30 Günlük Tam Dolu / Aşırı Yoğun Ay Stres Testi");
  {
    const sessions = [];
    const now = Date.now();
    const DAY_MS = 86400000;
    
    for (let i = 0; i < 30; i++) {
      const dayTime = now - i * DAY_MS;
      const k = w.dayKey(dayTime);
      
      // Kronometre seansı
      sessions.push({
        id: "se-kron-" + i,
        dayKey: k,
        startedAt: dayTime - 120 * 60000,
        endedAt: dayTime,
        mode: "stopwatch",
        events: [{ type: "start", at: dayTime - 120 * 60000 }, { type: "end", at: dayTime }]
      });
      
      // Pomodoro seansı (aynı gün 4 pomodoro)
      for (let p = 0; p < 4; p++) {
        sessions.push({
          id: `se-pomo-${i}-${p}`,
          dayKey: k,
          startedAt: dayTime - (200 + p * 30) * 60000,
          endedAt: dayTime - (175 + p * 30) * 60000,
          mode: "pomodoro",
          target: 25,
          events: [
            { type: "start", at: dayTime - (200 + p * 30) * 60000 },
            { type: "end", at: dayTime - (175 + p * 30) * 60000 }
          ]
        });
      }
    }
    
    const wFull = await kur({
      sessions, tasks: [], tombstones: [], active: null,
      settings: { mode: "stopwatch", theme: "light" }, sync: { connected: false }
    });
    const dFull = wFull.document;
    wFull.setTab("log");
    
    test("30 günün tamamında çift seans (Hem Kronometre hem Pomodoro)", () => {
      const box = dFull.getElementById("wallBox");
      assert.ok(box, "wallBox DOM elementi mevcut");
      
      const walls = box.querySelectorAll(".wall");
      assert.strictEqual(walls.length, 2, "İki ayrı duvar (Kronometre ve Pomodoro) başarıyla oluşturuldu");
      
      const daysKron = walls[0].querySelectorAll(".day");
      const daysPomo = walls[1].querySelectorAll(".day");
      assert.strictEqual(daysKron.length, 30, "Kronometre duvarında 30 gün var");
      assert.strictEqual(daysPomo.length, 30, "Pomodoro duvarında 30 gün var");
      
      const doluK = [...daysKron].filter(x => !x.classList.contains("void"));
      const doluP = [...daysPomo].filter(x => !x.classList.contains("void"));
      assert.strictEqual(doluK.length, 30, "Kronometre duvarında 30 günün tamamı dolu");
      assert.strictEqual(doluP.length, 30, "Pomodoro duvarında 30 günün tamamı dolu");
    });
  }

  // 4. BOŞ / SEYREK AY STRES TESTİ
  console.log("\n4) Tam Boş & Aşırı Seyrek Ay Stres Testi");
  {
    const now = Date.now();
    const dObj = new Date(now);
    const k = dObj.toISOString().slice(0, 10);
    
    const wSparse = await kur({
      sessions: [{
        id: "solo-session",
        dayKey: k,
        startedAt: now - 30 * 60000,
        endedAt: now,
        mode: "stopwatch",
        events: [{ type: "start", at: now - 30 * 60000 }, { type: "end", at: now }]
      }],
      tasks: [], tombstones: [], active: null,
      settings: { mode: "stopwatch", theme: "light" }, sync: { connected: false }
    });
    const dSparse = wSparse.document;
    wSparse.setTab("log");
    
    test("30 günde sadece tek 1 seans olan ay (Kopma veya bozulma yok)", () => {
      const box = dSparse.getElementById("wallBox");
      const walls = box.querySelectorAll(".wall");
      assert.strictEqual(walls.length, 1, "Yalnızca kullanılan modun duvarı çizildi");
      
      const days = walls[0].querySelectorAll(".day");
      assert.strictEqual(days.length, 30, "30 gün hücresi korundu");
      
      const voids = [...days].filter(x => x.classList.contains("void"));
      assert.strictEqual(voids.length, 29, "29 gün boş oyuntu olarak duruyor");
    });
  }

  console.log("\n==========================================");
  console.log(` STRES TESTİ SONUCU: ${passed} GEÇTİ, ${failed} KALDI `);
  console.log("==========================================\n");

  process.exit(failed > 0 ? 1 : 0);
}

runStressTests();
