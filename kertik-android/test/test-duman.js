/* DUMAN TESTİ — "uygulama hâlâ ayakta mı?"

   Diğer testler tek tek kuralları doğrular. Bu dosya onların altındaki
   varsayımı doğrular: sayfa açılıyor, konsol temiz, ana akış baştan sona
   yürüyor, kayıt yeniden açılışta duruyor.

   Buradaki en önemli kural şu:
     KONSOLA DÜŞEN HER HATA BU TESTİ KIRAR.
   Diğer test dosyaları pageerror'ı sadece ekrana basıyor; orada bir istisna
   fırlasa bile testler yeşil kalabiliyor. Burada kalmaz.

   Koşturmak için:  npm install playwright && node test-duman.js
*/
const { chromium } = require('playwright');
const path = require('path');
const URL = 'file://' + path.join(__dirname, '../app/src/main/assets/index.html');

let pass = 0, fail = 0;
const ok = (n, c, x) => { c ? (pass++, console.log("  ✓ " + n)) : (fail++, console.log("  ✗ " + n, x ?? "")); };

/* Sayfanın attığı her hata buraya birikir.
   Uyarılar (warning) sadece ekrana basılır, testi kırmaz: tarayıcının
   file:// altında ürettiği gürültü yüzünden testin "kurt geldi" diye
   bağırıp sonra kapatılmasını istemiyoruz. Hata ise hatadır. */
const hatalar = [];
function dinle(pg, etiket) {
  pg.on('pageerror', e => hatalar.push(etiket + " pageerror: " + e.message));
  pg.on('console', m => {
    if (m.type() === 'error') hatalar.push(etiket + " console.error: " + m.text());
    else if (m.type() === 'warning') console.log("    (uyarı) " + m.text());
  });
}

(async () => {
  /* Kapalı ortamlarda chromium'un yeri KERTIK_KROM ile verilebilir. */
  const b = await chromium.launch(
    process.env.KERTIK_KROM ? { executablePath: process.env.KERTIK_KROM } : {});
  const ctx = await b.newContext();
  const pg = await ctx.newPage();
  dinle(pg, "ilk açılış");

  /* ---------- 1. açılıyor mu ---------- */
  await pg.goto(URL);
  await pg.waitForTimeout(500);

  ok("sayfa yüklendi", await pg.title() !== null);
  ok("uygulama gövdesi ekranda", await pg.isVisible('#app'));
  ok("sayaç sayfası açık", await pg.isVisible('#timerPage'));
  ok("kadran çizildi", (await pg.evaluate(() => el("dial").children.length)) > 0);
  ok("saat sıfırda", (await pg.textContent('#clock')).trim() === "00:00", await pg.textContent('#clock'));
  ok("Başlat tuşu var", await pg.isVisible('#bStart'));

  /* İskeletin taşıdığı global sözleşme. Biri kaybolursa native köprü de,
     senkron da, çizim de sessizce çöker. */
  /* Not: S, el, activeSession `let`/`const` ile tanımlı — yani window'un
     üstünde DEĞİL, global sözlüksel kapsamda. O yüzden window[k] diye
     bakılmaz, adı doğrudan yazılır. */
  const eksik = await pg.evaluate(() => Object.entries({
    S: typeof S, el: typeof el, render: typeof render, save: typeof save,
    startSession: typeof startSession, finish: typeof finish,
    activeSession: typeof activeSession, stats: typeof stats,
    setTab: typeof setTab, addTask: typeof addTask,
    closeSheet: typeof closeSheet, nativeBildir: typeof nativeBildir
  }).filter(([, t]) => t === "undefined").map(([k]) => k));
  ok("global sözleşme yerinde", eksik.length === 0, eksik.join(", "));

  /* ---------- 2. dört sekme de açılıyor mu ---------- */
  for (const [tab, sayfa] of [["tasks", "tasksPage"], ["log", "logPage"], ["settings", "settingsPage"], ["timer", "timerPage"]]) {
    await pg.click(`nav button[data-tab="${tab}"]`);
    await pg.waitForTimeout(250);
    ok(tab + " sekmesi açıldı", await pg.evaluate(s => el(s).classList.contains("on"), sayfa));
  }

  /* ---------- 3. ana akış: başlat → mola → devam → bitir ---------- */
  await pg.click('#bStart'); await pg.waitForTimeout(300);
  ok("seans başladı", await pg.evaluate(() => S.active !== null));
  ok("durum etiketi değişti",
     (await pg.textContent('#stateLabel')).trim() !== await pg.evaluate(() => soz("durum_hazir")),
     await pg.textContent('#stateLabel'));

  await pg.click('#bBrk'); await pg.waitForTimeout(250);
  ok("mola başladı", await pg.evaluate(() => stats(activeSession()).onBreak) === true);

  await pg.click('#bRes'); await pg.waitForTimeout(250);
  ok("moladan dönüldü", await pg.evaluate(() => stats(activeSession()).onBreak) === false);
  ok("mola süresi sayıldı", await pg.evaluate(() => stats(activeSession()).brk) > 0);

  await pg.click('#bEnd'); await pg.waitForTimeout(400);
  ok("seans kapandı", await pg.evaluate(() => S.active) === null);
  ok("seans sonu sorusu açıldı", await pg.evaluate(() => el("sheet").classList.contains("on")));
  ok("kayıt tutuldu", await pg.evaluate(() => S.sessions.filter(s => s.endedAt).length) === 1);

  await pg.evaluate(() => closeSheet()); await pg.waitForTimeout(200);

  /* ---------- 4. görev akışı ---------- */
  await pg.click('nav button[data-tab="tasks"]'); await pg.waitForTimeout(200);
  await pg.fill('#taskInput', 'duman testi görevi');
  await pg.click('#taskAdd'); await pg.waitForTimeout(250);
  ok("görev eklendi", await pg.evaluate(() => S.tasks.length) === 1);
  ok("görev listede göründü", (await pg.textContent('#taskList')).includes("duman testi görevi"));

  /* ---------- 5. kayıt sayfası dolu veriyle çiziliyor mu ---------- */
  await pg.click('nav button[data-tab="log"]'); await pg.waitForTimeout(350);
  ok("kayıt sayfasında duvar çizildi", await pg.evaluate(() => el("wallBox").innerHTML.length) > 0);
  ok("seans kayıt listesinde", (await pg.textContent('#logBody')).length > 0);

  /* ---------- 6. yeniden açılışta veri duruyor mu ---------- */
  const pg2 = await ctx.newPage();
  dinle(pg2, "ikinci açılış");
  await pg2.goto(URL);
  await pg2.waitForTimeout(500);
  ok("kayıtlı seans geri yüklendi", await pg2.evaluate(() => S.sessions.length) === 1);
  ok("kayıtlı görev geri yüklendi", await pg2.evaluate(() => S.tasks.length) === 1);
  ok("dolu veriyle de Başlat tuşu var", await pg2.isVisible('#bStart'));

  /* ---------- 7. konsol temiz mi ---------- */
  await pg.waitForTimeout(300);
  ok("konsola tek bir hata düşmedi", hatalar.length === 0, "\n      " + hatalar.join("\n      "));

  console.log("\n" + pass + " geçti, " + fail + " kaldı");
  await b.close();
  process.exit(fail ? 1 : 0);
})();
