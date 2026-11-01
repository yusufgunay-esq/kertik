/* Odak modu testleri — seans sürerken alt gezintinin çekilmesi.

   Doğrulanan ilke: bu bir KİLİT DEĞİL. Gezinti gizlenir ama kullanıcı
   çentiğe dokunarak ya da yukarı kaydırarak her an geri çağırabilir.

   Koşturmak için:  node test-odak.js
*/
const path = require("path");
const { chromium } = require("playwright");

const URL = "file://" + path.join(__dirname, "../app/src/main/assets/index.html");
let pass = 0, fail = 0;
const ok = (n, c, x) => { c ? (pass++, console.log("  ✓ " + n)) : (fail++, console.log("  ✗ " + n, x ?? "")); };

(async () => {
  const tarayici = await chromium.launch();
  const sayfa = await tarayici.newPage({ viewport: { width: 412, height: 915 }, hasTouch: true });

  const hatalar = [];
  sayfa.on("pageerror", e => hatalar.push(e.message));

  await sayfa.goto(URL);
  await sayfa.waitForTimeout(400);
  /* tanıtım akışını geç */
  await sayfa.mouse.click(206, 300);
  await sayfa.waitForTimeout(300);

  const gezintiYuksek = async () => {
    const k = await sayfa.locator("nav").boundingBox();
    return k ? k.height : 0;
  };
  const odakVar = () => sayfa.evaluate(() => document.documentElement.classList.contains("odak"));

  console.log("\n1) Seans yokken");
  ok("gezinti görünür", (await gezintiYuksek()) > 10);
  ok("odak sınıfı yok", !(await odakVar()));
  ok("çentik gizli", !(await sayfa.locator("#centik").isVisible()));

  console.log("\n2) Seans başlayınca");
  await sayfa.click("#bStart");
  await sayfa.waitForTimeout(900);
  ok("odak sınıfı kuruldu", await odakVar());
  ok("gezinti çekildi", (await gezintiYuksek()) < 10);
  ok("çentik göründü", await sayfa.locator("#centik").isVisible());
  ok("seans gerçekten sürüyor", await sayfa.evaluate(() => !!JSON.parse(localStorage.getItem("kertik.v1")).active));

  console.log("\n3) Çentik — kilit olmadığının kanıtı");
  await sayfa.click("#centik");
  await sayfa.waitForTimeout(800);
  ok("gezinti geri geldi", (await gezintiYuksek()) > 10);
  ok("odak sınıfı kalktı", !(await odakVar()));
  ok("seans bozulmadı", await sayfa.evaluate(() => !!JSON.parse(localStorage.getItem("kertik.v1")).active));

  console.log("\n4) Başka sekmeye geçiş");
  await sayfa.click('nav button[data-tab="tasks"]');
  await sayfa.waitForTimeout(400);
  ok("gezinti duruyor", (await gezintiYuksek()) > 10);
  ok("odak yok (sayaç sayfasında değiliz)", !(await odakVar()));

  console.log("\n5) Sayaca dönüş — odak kendini yeniden kurar");
  await sayfa.click('nav button[data-tab="timer"]');
  await sayfa.waitForTimeout(900);
  ok("odak tekrar kuruldu", await odakVar());
  ok("gezinti tekrar çekildi", (await gezintiYuksek()) < 10);

  console.log("\n6) Yukarı kaydırma");
  const k = await sayfa.locator("#centik").boundingBox();
  await sayfa.touchscreen.tap(k.x + k.width / 2, k.y + k.height / 2);
  await sayfa.waitForTimeout(700);
  ok("dokunmayla da açılıyor", (await gezintiYuksek()) > 10);

  console.log("\n7) Seans bitince");
  await sayfa.click('nav button[data-tab="timer"]');
  await sayfa.waitForTimeout(400);
  if (await sayfa.locator("#centik").isVisible()) {
    await sayfa.click("#centik");
    await sayfa.waitForTimeout(700);
  }
  const bitir = sayfa.locator("#bEnd");
  if (await bitir.count()) { await bitir.click(); await sayfa.waitForTimeout(1000); }
  ok("odak kapandı", !(await odakVar()));
  ok("gezinti kalıcı olarak görünür", (await gezintiYuksek()) > 10);

  console.log("\n9) Konsol");
  ok("sayfa hatası düşmedi", hatalar.length === 0, hatalar.join(" | "));
  await sayfa.close();

  /* ---- 8) Tanıtım günde bir kez ----
     Eskiden ömür boyu tek seferdi; bu yüzden uygulamanın en güzel görsel
     yanı ilk günden sonra bir daha görünmüyordu. Artık günlük. */
  console.log("\n8) Tanıtım günde bir kez");
  const temiz = await tarayici.newPage({ viewport: { width: 412, height: 915 } });
  await temiz.goto(URL);
  await temiz.waitForTimeout(1600);

  const anahtar = await temiz.evaluate(() => localStorage.getItem("kertik.akisTanit"));
  ok("tanıtım çalıştı ve tarih yazdı", !!anahtar && !isNaN(Date.parse(anahtar)), anahtar);
  ok("bugünün tarihi", anahtar === new Date().toDateString(), anahtar);

  /* aynı gün tekrar açılış: tanıtım tekrar oynamamalı */
  await temiz.reload();
  await temiz.waitForTimeout(1600);
  ok("aynı gün tekrarlamıyor", await temiz.evaluate(() => !AK.tanit));

  /* dün açılmış gibi yap: tanıtım yeniden oynamalı */
  await temiz.evaluate(() => {
    const d = new Date(Date.now() - 864e5);
    localStorage.setItem("kertik.akisTanit", d.toDateString());
  });
  await temiz.reload();
  await temiz.waitForTimeout(900);
  ok("yeni günde tekrar oynuyor",
    await temiz.evaluate(() => localStorage.getItem("kertik.akisTanit") === new Date().toDateString()));

  console.log("\n" + pass + " geçti, " + fail + " kaldı");
  await tarayici.close();
  process.exit(fail ? 1 : 0);
})();
