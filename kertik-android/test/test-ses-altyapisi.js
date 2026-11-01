const fs = require("fs");
const path = require("path");
const { JSDOM } = require("jsdom");

console.log("=== SES VE AUDIOCONTEXT YASAM DONGUSU TESTI ===");

let pass = 0, fail = 0;
function ok(msg, cond) {
  if (cond) { console.log("  ✓ " + msg); pass++; }
  else { console.error("  ✗ " + msg); fail++; }
}

class MockAudioContext {
  constructor(options) {
    this.options = options;
    this.sampleRate = (options && options.sampleRate) || 48000;
    this.state = "running";
    this.currentTime = 0;
    this.destination = {};
  }
  createBuffer(channels, length, sampleRate) {
    const data = new Float32Array(length);
    return {
      numberOfChannels: channels,
      length,
      sampleRate,
      getChannelData: (c) => data
    };
  }
  createBufferSource() {
    return {
      buffer: null,
      connect: () => {},
      disconnect: () => {},
      start: () => {},
      stop: () => {},
      onended: null
    };
  }
  createBiquadFilter() {
    return {
      type: "bandpass",
      frequency: {
        setValueAtTime: () => {},
        exponentialRampToValueAtTime: () => {}
      },
      Q: { setValueAtTime: () => {} },
      connect: () => {},
      disconnect: () => {}
    };
  }
  async resume() {
    this.state = "running";
  }
  async suspend() {
    this.state = "suspended";
  }
}

async function test() {
  const htmlPath = path.join(__dirname, "../app/src/main/assets/index.html");
  const html = fs.readFileSync(htmlPath, "utf8");

  const dom = new JSDOM(html, {
    runScripts: "dangerously",
    pretendToBeVisual: true,
    url: "http://localhost/",
    beforeParse(w) {
      if (!w.structuredClone) w.structuredClone = o => JSON.parse(JSON.stringify(o));
      w.AudioContext = MockAudioContext;
      w.webkitAudioContext = MockAudioContext;
      w.requestAnimationFrame = (fn) => setTimeout(fn, 16);
      w.cancelAnimationFrame = (id) => clearTimeout(id);
      w.HTMLCanvasElement.prototype.getContext = () => ({
        canvas: {}, globalAlpha: 1, globalCompositeOperation: "source-over",
        beginPath() {}, moveTo() {}, lineTo() {}, stroke() {}, fill() {}, fillRect() {}, clearRect() {},
        setTransform() {}, drawImage() {}, putImageData() {}, closePath() {}, arc() {}, ellipse() {},
        save() {}, restore() {}, translate() {}, rotate() {}, scale() {}, setLineDash() {},
        createImageData: (w, h) => ({ width: w, height: h, data: new Uint8ClampedArray(w * h * 4) }),
        createRadialGradient: () => ({ addColorStop() {} }),
        createLinearGradient: () => ({ addColorStop() {} })
      });
      w.HTMLCanvasElement.prototype.toDataURL = () => "data:image/png;base64,";
    }
  });

  await new Promise(res => setTimeout(res, 80));
  const w = dom.window;

  console.log("\n1) Donanim Hizi ve AudioContext Baslatma");
  const ctx = w.eval("getAudioContext()");
  ok("AudioContext basariyla olusturuldu", !!ctx);
  ok("AudioContext donanim hizinda calisiyor (48000 Hz)", ctx.sampleRate === 48000);
  ok("AudioContext'e zorla 44100 Hz secenegi verilmedi (AudioFlinger kacinmasi)", !ctx.options || !ctx.options.sampleRate);

  console.log("\n2) 4. Derece Filtreleme ve Sifir-Gecis Pencereleme (Zero Pop / DC-Offset)");
  const dummyData = new Float32Array(480);
  dummyData.fill(0.85);
  const lp = w.eval(`applyIIRLowpass(new Float32Array([${Array.from(dummyData).join(',')}]), 48000, 280)`);
  ok("4. derece IIR filtre hesaplandi", lp && lp.length === 480);
  ok("Filtre cikisi sonlu ve sayisal olarak kararli (NaN veya Inf yok)", !lp.some(x => isNaN(x) || !isFinite(x)));

  const winData = new Float32Array(480);
  winData.fill(1.0);
  w.eval(`(function() { const d = new Float32Array(480); d.fill(1.0); applyAudioWindow(d, 48000); return [d[0], d[479]]; })()`);
  const winEnds = w.eval(`(function() { const d = new Float32Array(480); d.fill(1.0); applyAudioWindow(d, 48000); return [d[0], d[479]]; })()`);
  ok("applyAudioWindow baslangici yumusak bastirdi (d[0] === 0.0)", Math.abs(winEnds[0]) < 1e-5);
  ok("applyAudioWindow bitisini kesin olarak sifirladi (d[end] === 0.0)", Math.abs(winEnds[1]) < 1e-5);

  console.log("\n3) Ses Fonksiyonlari ve Tampon Sentezi");
  const prof15 = w.eval("getKutleProfili(15)");
  const prof25 = w.eval("getKutleProfili(25)");
  const prof50 = w.eval("getKutleProfili(50)");
  const prof90 = w.eval("getKutleProfili(90)");
  
  ok("sesCalKutleDarbe(15dk) hatasiz calisti", !(() => { w.eval(`sesCalKutleDarbe(${JSON.stringify(prof15)})`); })());
  ok("sesCalKutleDarbe(25dk) hatasiz calisti", !(() => { w.eval(`sesCalKutleDarbe(${JSON.stringify(prof25)})`); })());
  ok("sesCalKutleDarbe(50dk) hatasiz calisti", !(() => { w.eval(`sesCalKutleDarbe(${JSON.stringify(prof50)})`); })());
  ok("sesCalKutleDarbe(90dk) hatasiz calisti", !(() => { w.eval(`sesCalKutleDarbe(${JSON.stringify(prof90)})`); })());
  ok("sesCalMaddi('baslat') hatasiz calisti", !(() => { w.eval("sesCalMaddi('baslat')"); })());
  ok("sesCalMaddi('mola') hatasiz calisti", !(() => { w.eval("sesCalMaddi('mola')"); })());
  ok("sesCalMaddi('devam') hatasiz calisti", !(() => { w.eval("sesCalMaddi('devam')"); })());
  ok("sesCalMaddi('pomodoro') hatasiz calisti", !(() => { w.eval("sesCalMaddi('pomodoro')"); })());
  ok("sesCalMaddi('bitir') hatasiz calisti", !(() => { w.eval("sesCalMaddi('bitir')"); })());
  ok("sesCalDamlaDarbe() geriye donuk uyumlu calisti", !(() => { w.eval("sesCalDamlaDarbe()"); })());
  ok("sesCalZenCani() geriye donuk uyumlu calisti", !(() => { w.eval("sesCalZenCani()"); })());
  ok("sesCalKertikCentik() geriye donuk uyumlu calisti", !(() => { w.eval("sesCalKertikCentik()"); })());
  ok("sesCalTasKirilma() hatasiz calisti", !(() => { w.eval("sesCalTasKirilma()"); })());
  ok("sesCalKintsugi() hatasiz calisti", !(() => { w.eval("sesCalKintsugi()"); })());
  ok("sesCalRuzgar(1) hatasiz calisti", !(() => { w.eval("sesCalRuzgar(1)"); })());
  ok("sesCalRuzgar(2) hatasiz calisti", !(() => { w.eval("sesCalRuzgar(2)"); })());

  console.log("\n4) Ses Bittiginde Kanal Acik Kalir (arkaplan muzigiyle tekrar tekrar acilip kapanma onlenir)");
  ok("Baslangicta ses kanali calisir durumda (running)", ctx.state === "running");
  w.eval("sesCalDamlaDarbe()");
  await new Promise(r => setTimeout(r, 150));
  ok("Ses bittikten sonra da kanal acik kaliyor (state === running), otomatik askiya alinmiyor", ctx.state === "running");

  console.log("\n5) Sayfa Gizlendiginde Askiya Alma (visibilitychange)");
  Object.defineProperty(w.document, "visibilityState", { value: "hidden", writable: true });
  w.document.dispatchEvent(new w.Event("visibilitychange"));
  ok("Sayfa gizlendiginde acik ses kanali derhal askiya alindi", ctx.state === "suspended");

  console.log("\n6) Sayfa Ondeyken Yeni Seste Yeniden Uyanma (Auto-Resume)");
  w.eval("sesCalDamlaDarbe()");
  ok("Yeni ses calarken ses kanali uyandi (state === running)", ctx.state === "running");

  console.log("\n7) Modern Haptik ve Titresim Sistemi");
  let nativeHapticCalls = [];
  w.KertikNative = {
    titretDoku: (t, a, komp) => nativeHapticCalls.push({ type: "doku", t, a, komp }),
    titretHassas: (ms, amp) => nativeHapticCalls.push({ type: "precise", ms, amp }),
    titretPattern: (p) => nativeHapticCalls.push({ type: "pattern", p }),
    titret: (ms) => nativeHapticCalls.push({ type: "legacy", ms })
  };

  w.eval("buzz('pomodoro')");
  ok("buzz('pomodoro') native titretDoku cagirdi", nativeHapticCalls.some(c => c.type === "doku" && c.komp === "tas_oturma"));

  w.eval("buzz(12)");
  ok("buzz(12) hassas genlikli titretDoku veya titretHassas cagirdi", nativeHapticCalls.some(c => (c.type === "doku" && c.t === "12") || (c.type === "precise" && c.ms === 12)));

  w.eval("buzz([8, 14, 12])");
  ok("buzz([8, 14, 12]) titretDoku veya titretPattern cagirdi", nativeHapticCalls.some(c => c.type === "doku" || c.type === "pattern"));

  console.log("\n==========================================");
  console.log(` TEST SONUCU: ${pass} GECTI, ${fail} KALDI `);
  console.log("==========================================");

  process.exit(fail ? 1 : 0);
}

test().catch(e => {
  console.error("Test hatasi:", e);
  process.exit(1);
});
