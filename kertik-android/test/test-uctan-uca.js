const { chromium } = require('playwright');
const O = "http://127.0.0.1:8899";
let pass=0, fail=0;
const ok=(n,c,x)=>{ c?(pass++,console.log("  ✓ "+n)):(fail++,console.log("  ✗ "+n, x??"")); };

/* Derlenmiş uygulamayı taklit eder: anahtar native köprüden gelir, kaynak dosyada yoktur. */
const NATIVE = (a) => {
  window.KertikNative = {
    goster: () => {}, gizle: () => {},
    bildirimIzniVar: () => true, bildirimIzniIste: () => {},
    ekraniAcikTut: () => {}, titret: () => {}, surum: () => "1.0",
    googleAnahtar: () => JSON.stringify(a)
  };
};
const ANAHTAR = { id: "x.apps.googleusercontent.com", secret: "GOCSPX-x" };

(async () => {
  /* Kapalı ortamlarda chromium'un yeri KERTIK_KROM ile verilebilir. */
  const b = await chromium.launch(
    process.env.KERTIK_KROM ? { executablePath: process.env.KERTIK_KROM } : {});
  const ctx = await b.newContext();
  await ctx.addInitScript(NATIVE, ANAHTAR);
  const pg = await ctx.newPage();
  pg.on('pageerror', e => console.log('PAGEERROR:', e.message));

  const wire = async p => p.evaluate(o => {
    GOOGLE.DEVICE = o + "/device/code";
    GOOGLE.TOKEN  = o + "/token";
    GOOGLE.FILES  = o + "/drive/v3/files";
    GOOGLE.UPLOAD = o + "/upload/drive/v3/files";
  }, O);

  /* ---- 1. cihaz ---- */
  await pg.goto(O + "/");
  await pg.waitForTimeout(300);
  await wire(pg);
  await pg.click('#bStart'); await pg.waitForTimeout(300);
  await pg.click('#bEnd');   await pg.waitForTimeout(400);
  await pg.click('#cls').catch(()=>{});
  await pg.click('[data-tab="tasks"]'); await pg.waitForTimeout(200);
  await pg.fill('#taskInput','telefon 1 işi'); await pg.click('#taskAdd'); await pg.waitForTimeout(200);

  await pg.click('[data-tab="settings"]'); await pg.waitForTimeout(250);
  await pg.click('#gsy'); await pg.waitForTimeout(250);
  // anahtar gömülü olduğu için doğrudan "bağlan" ekranı açılmalı
  ok("gömülü anahtarla kurulum ekranı atlanıyor", await pg.locator('#ci').count() === 0);
  await pg.click('#go'); await pg.waitForTimeout(500);          // "bağlan"
  const code = await pg.textContent('.mono[style*="30px"]').catch(()=>null);
  ok("cihaz kodu ekranda gösterildi", (code||"").trim() === "WXYZ-1234", code);
  await pg.waitForTimeout(13000);                                 // bekleyen → onaylı
  const d1 = await pg.evaluate(()=>JSON.parse(localStorage.getItem('kertik.v1')));
  ok("yenileme anahtarı saklandı", d1.sync.refresh === "RT-1");
  ok("ilk eşitleme yapıldı", !!d1.sync.lastAt && !d1.sync.lastErr, d1.sync.lastErr);
  ok("dosya kimliği tutuldu", !!d1.sync.fileId);

  /* ---- 2. cihaz: boş bir telefon, aynı hesap ---- */
  const ctx2 = await b.newContext();
  await ctx2.addInitScript(NATIVE, ANAHTAR);
  const p2 = await ctx2.newPage();
  p2.on('pageerror', e => console.log('P2 PAGEERROR:', e.message));
  await p2.goto(O + "/"); await p2.waitForTimeout(300); await wire(p2);
  await p2.evaluate(() => { S.sync.refresh = "RT-1"; save(); });
  const r2 = await p2.evaluate(() => syncNow());
  ok("ikinci cihaz eşitledi", r2.ok, r2.err);
  const d2 = await p2.evaluate(()=>({s:S.sessions.length, t:S.tasks.length, title:(S.tasks[0]||{}).title}));
  ok("seans ikinci telefona indi", d2.s === 1, JSON.stringify(d2));
  ok("görev ikinci telefona indi", d2.t === 1 && d2.title === "telefon 1 işi", JSON.stringify(d2));

  /* ---- 2. cihazda sil, 1. cihazda geri dirilmemeli ---- */
  await p2.evaluate(() => { const id = S.tasks[0].id; tomb("task", id); S.tasks = []; save(); });
  const r2b = await p2.evaluate(() => syncNow());
  ok("silme uzağa yazıldı", r2b.ok, r2b.err);
  const r1b = await pg.evaluate(() => syncNow());
  ok("birinci cihaz tekrar eşitledi", r1b.ok, r1b.err);
  const d1b = await pg.evaluate(()=>({t:S.tasks.length, tomb:S.tombstones.length}));
  ok("silinen görev geri dirilmedi", d1b.t === 0, JSON.stringify(d1b));

  /* ---- 1. cihazda yeni seans, 2. cihaza gitmeli ---- */
  await pg.evaluate(() => closeSheet()); await pg.waitForTimeout(200);
  await pg.click('[data-tab="timer"]'); await pg.waitForTimeout(200);
  await pg.click('#bStart'); await pg.waitForTimeout(300);
  await pg.click('#bEnd'); await pg.waitForTimeout(400);
  await pg.click('#cls').catch(()=>{});
  await pg.evaluate(() => syncNow());
  const r2c = await p2.evaluate(() => syncNow());
  const d2c = await p2.evaluate(()=>S.sessions.length);
  ok("yeni seans karşı telefona geçti", d2c === 2, d2c);

  /* ---- yetki iptal edilirse sessizce yerel moda düşmeli ---- */
  await p2.evaluate(() => { S.sync.refresh = "BOZUK"; gToken = null; gTokenExp = 0; save(); });
  const bad = await p2.evaluate(() => syncNow());
  const dbad = await p2.evaluate(()=>({r:S.sync.refresh, s:S.sessions.length}));
  ok("geçersiz yetkide hata yutuldu", bad.ok === false);
  ok("yetki temizlendi, veri duruyor", dbad.r === null && dbad.s === 2, JSON.stringify(dbad));

  console.log("\n" + pass + " geçti, " + fail + " kaldı");
  await b.close();
  process.exit(fail ? 1 : 0);
})();
