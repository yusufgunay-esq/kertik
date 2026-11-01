const { chromium } = require('playwright');
let pass = 0, fail = 0;
const ok = (n, c, x) => { c ? (pass++, console.log("  ✓ " + n)) : (fail++, console.log("  ✗ " + n, x ?? "")); };
const URL = 'file://' + require('path').join(__dirname, '../www/index.html');

(async () => {
  const b = await chromium.launch();

  /* --- temiz kurulum --- */
  const pg = await b.newPage();
  pg.on('pageerror', e => console.log('PAGEERROR:', e.message));
  await pg.goto(URL); await pg.waitForTimeout(400);
  const cid = await pg.evaluate(() => gcred().id);
  ok("gömülü anahtar kullanılıyor", cid.includes("-") && cid.endsWith(".apps.googleusercontent.com"), cid);
  ok("senkron hazır", await pg.evaluate(() => syncReady()) === true);
  await pg.click('[data-tab="settings"]'); await pg.waitForTimeout(300);
  ok("etiket 'bağlan'", (await pg.textContent('#gsy')).trim() === "bağlan");
  await pg.click('#gsy'); await pg.waitForTimeout(250);
  ok("kurulum ekranı atlandı", await pg.locator('#ci').count() === 0);

  /* --- kullanıcı kendi anahtarını girerse o kazanmalı --- */
  await pg.click('#kk'); await pg.waitForTimeout(250);
  await pg.fill('#ci', 'benim.apps.googleusercontent.com');
  await pg.fill('#cs', 'GOCSPX-benim');
  await pg.click('#sv'); await pg.waitForTimeout(300);
  ok("kendi anahtarı gömülüyü eziyor", await pg.evaluate(() => gcred().id) === "benim.apps.googleusercontent.com");
  await pg.evaluate(() => { S.sync.clientId = ""; S.sync.clientSecret = ""; save(); });
  ok("boşaltınca gömülüye dönüyor", (await pg.evaluate(() => gcred().id)) === cid);

  /* --- v2.1'den gelen hatalı anahtar bir kez temizlenmeli --- */
  const p2 = await b.newPage();
  p2.on('pageerror', e => console.log('P2 PAGEERROR:', e.message));
  await p2.goto(URL); await p2.waitForTimeout(300);
  await p2.evaluate(() => {
    const d = JSON.parse(localStorage.getItem('kertik.v1'));
    d.sync.clientId = "867461126439n9iol5g15f0m183vni93hioiq4vpfh8g.apps.googleusercontent.com"; // tiresi düşmüş hâli
    d.sync.clientSecret = "GOCSPX-eski";
    d.sync.keysMigrated = false;
    d.sync.lastErr = "invalid_client";
    localStorage.setItem('kertik.v1', JSON.stringify(d));
  });
  await p2.reload(); await p2.waitForTimeout(500);
  ok("eski hatalı anahtar temizlendi", await p2.evaluate(() => S.sync.clientId) === "");
  ok("gömülü anahtara dönüldü", await p2.evaluate(() => gcred().id) === cid);
  ok("eski hata kaydı silindi", await p2.evaluate(() => S.sync.lastErr) === null);
  await p2.reload(); await p2.waitForTimeout(400);
  ok("göç bir kez çalışıyor (tekrar etmiyor)", await p2.evaluate(() => S.sync.keysMigrated) === true);

  /* --- hata ekranı --- */
  await pg.evaluate(() => syncFail("deneme", "invalid_client · HTTP 401"));
  await pg.waitForTimeout(200);
  const t = await pg.textContent('#sheetBox');
  ok("hata ekranı teşhis gösteriyor", t.includes("invalid_client") && t.includes("HTTP 401"));

  console.log("\n" + pass + " geçti, " + fail + " kaldı");
  await b.close();
  process.exit(fail ? 1 : 0);
})();
