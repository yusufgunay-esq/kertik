/* Google anahtarının nereden geldiğini ve ayarlar akışını test eder.
   Kural: anahtar KAYNAK DOSYADA YOK. Üç kaynak var, bu öncelikle:
     1. kullanıcının elle girdiği anahtar
     2. derlemede gömülen anahtar (native köprüden: KertikNative.googleAnahtar())
     3. hiçbiri — senkron kapalı, ayarlarda "kur" yazar
*/
const { chromium } = require('playwright');
const path = require('path');
const URL = 'file://' + path.join(__dirname, '../app/src/main/assets/index.html');

let pass = 0, fail = 0;
const ok = (n, c, x) => { c ? (pass++, console.log("  ✓ " + n)) : (fail++, console.log("  ✗ " + n, x ?? "")); };

const GOMULU_ID = "111-gomulu.apps.googleusercontent.com";
const GOMULU_SECRET = "GOCSPX-gomulu";

/* Derlenmiş uygulamayı taklit eder: köprü anahtarı veriyor. */
const NATIVE_ANAHTARLI = (a) => {
  window.KertikNative = {
    goster: () => {}, gizle: () => {},
    bildirimIzniVar: () => true, bildirimIzniIste: () => {},
    ekraniAcikTut: () => {}, titret: () => {},
    surum: () => "1.0",
    googleAnahtar: () => JSON.stringify({ id: a.id, secret: a.secret })
  };
};
/* Anahtarsız derleme (sır tanımlanmadan CI'da üretilmiş APK). */
const NATIVE_ANAHTARSIZ = () => {
  window.KertikNative = {
    goster: () => {}, gizle: () => {},
    bildirimIzniVar: () => true, bildirimIzniIste: () => {},
    ekraniAcikTut: () => {}, titret: () => {},
    surum: () => "1.0",
    googleAnahtar: () => null
  };
};

(async () => {
  /* Kapalı ortamlarda chromium'un yeri KERTIK_KROM ile verilebilir. */
  const b = await chromium.launch(
    process.env.KERTIK_KROM ? { executablePath: process.env.KERTIK_KROM } : {});

  /* ---- 1. Tarayıcı: köprü yok, anahtar yok ---- */
  {
    const pg = await b.newPage();
    pg.on('pageerror', e => console.log('PAGEERROR:', e.message));
    await pg.goto(URL); await pg.waitForTimeout(400);
    ok("kaynak dosyada anahtar gömülü değil", await pg.evaluate(() => GOOGLE.CLIENT_ID) === "");
    ok("köprüsüz senkron kapalı", await pg.evaluate(() => syncReady()) === false);
    await pg.click('[data-tab="settings"]'); await pg.waitForTimeout(300);
    ok("ayarlarda etiket 'kur'", (await pg.textContent('#gsy')).trim() === "kur");
    await pg.click('#gsy'); await pg.waitForTimeout(250);
    ok("kendi anahtarını girme ekranı açılıyor", await pg.locator('#ci').count() === 1);
    await pg.close();
  }

  /* ---- 2. Derlenmiş uygulama: anahtar köprüden geliyor ---- */
  {
    const ctx = await b.newContext();
    await ctx.addInitScript(NATIVE_ANAHTARLI, { id: GOMULU_ID, secret: GOMULU_SECRET });
    const pg = await ctx.newPage();
    pg.on('pageerror', e => console.log('PAGEERROR:', e.message));
    await pg.goto(URL); await pg.waitForTimeout(400);
    ok("köprüden gelen anahtar kullanılıyor", await pg.evaluate(() => gcred().id) === GOMULU_ID);
    ok("senkron hazır", await pg.evaluate(() => syncReady()) === true);
    await pg.click('[data-tab="settings"]'); await pg.waitForTimeout(300);
    ok("etiket 'bağlan'",
       (await pg.textContent('#gsy')).trim() === await pg.evaluate(() => soz("sy_baglan")));
    await pg.click('#gsy'); await pg.waitForTimeout(250);
    ok("kurulum ekranı atlanıyor", await pg.locator('#ci').count() === 0);
    ok("doğrudan bağlan ekranı", await pg.locator('#go').count() === 1);

    /* kendi anahtarı gömülüyü ezmeli */
    await pg.click('#kk'); await pg.waitForTimeout(250);
    await pg.fill('#ci', 'benim.apps.googleusercontent.com');
    await pg.fill('#cs', 'GOCSPX-benim');
    await pg.click('#sv'); await pg.waitForTimeout(300);
    ok("kullanıcının anahtarı önceliklidir", await pg.evaluate(() => gcred().id) === "benim.apps.googleusercontent.com");
    await pg.evaluate(() => { S.sync.clientId = ""; S.sync.clientSecret = ""; save(); });
    ok("boşaltınca gömülüye dönüyor", await pg.evaluate(() => gcred().id) === GOMULU_ID);
    await pg.close();
  }

  /* ---- 3. Sırsız derlenmiş APK: köprü var, anahtar yok ---- */
  {
    const ctx = await b.newContext();
    await ctx.addInitScript(NATIVE_ANAHTARSIZ);
    const pg = await ctx.newPage();
    let hata = null;
    pg.on('pageerror', e => hata = e.message);
    await pg.goto(URL); await pg.waitForTimeout(400);
    ok("anahtarsız derlemede patlamıyor", hata === null, hata);
    ok("senkron kapalı kalıyor", await pg.evaluate(() => syncReady()) === false);
    ok("uygulama yine de çalışıyor", await pg.evaluate(() => typeof startSession === "function"));
    await pg.close();
  }

  /* ---- 4. Eski sürümden kalan hatalı anahtar bir kez temizlenmeli ---- */
  {
    const ctx = await b.newContext();
    await ctx.addInitScript(NATIVE_ANAHTARLI, { id: GOMULU_ID, secret: GOMULU_SECRET });
    const pg = await ctx.newPage();
    pg.on('pageerror', e => console.log('PAGEERROR:', e.message));
    await pg.goto(URL); await pg.waitForTimeout(300);
    await pg.evaluate(() => {
      const d = JSON.parse(localStorage.getItem('kertik.v1'));
      d.sync.clientId = "111gomulu.apps.googleusercontent.com"; // tiresi düşmüş hâli
      d.sync.clientSecret = "GOCSPX-eski";
      d.sync.keysMigrated = false;
      d.sync.lastErr = "invalid_client";
      localStorage.setItem('kertik.v1', JSON.stringify(d));
    });
    await pg.reload(); await pg.waitForTimeout(500);
    ok("eski hatalı anahtar temizlendi", await pg.evaluate(() => S.sync.clientId) === "");
    ok("gömülü anahtara dönüldü", await pg.evaluate(() => gcred().id) === GOMULU_ID);
    ok("eski hata kaydı silindi", await pg.evaluate(() => S.sync.lastErr) === null);
    await pg.reload(); await pg.waitForTimeout(400);
    ok("göç bir kez çalışıyor", await pg.evaluate(() => S.sync.keysMigrated) === true);

    /* hata ekranı teşhis satırı */
    await pg.evaluate(() => syncFail("deneme", "invalid_client · HTTP 401"));
    await pg.waitForTimeout(200);
    const t = await pg.textContent('#sheetBox');
    ok("hata ekranı teşhis gösteriyor", t.includes("invalid_client") && t.includes("HTTP 401"));
    ok("hata ekranından anahtar değiştirilebiliyor", await pg.locator('#kk').count() === 1);
    await pg.close();
  }

  console.log("\n" + pass + " geçti, " + fail + " kaldı");
  await b.close();
  process.exit(fail ? 1 : 0);
})();
