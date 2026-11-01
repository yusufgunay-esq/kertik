/* Native köprünün SAYFA tarafını test eder.
   Kotlin tarafı burada derlenemiyor; onun yerine KertikNative arayüzünü birebir
   taklit eden bir sahte nesne enjekte edip sayfanın doğru çağrıları yaptığını
   doğruluyoruz. Kotlin tarafı bu sözleşmeye uymak zorunda:

     goster(baslik: String, alt: String, temelMs: String, geriSayim: Boolean, molada: Boolean)
     gizle()
     bildirimIzniVar(): Boolean
     bildirimIzniIste()
     ekraniAcikTut(acik: Boolean)
     surum(): String
     resimKaydet(b64: String, ad: String): "galeri" | "paylas" | "hata"
   ve sayfa şunları sağlar:
     window.kertikNativeEylem("break" | "resume" | "end")
     window.nativeBildir(zorla?)
*/
const { chromium } = require('playwright');
const path = require('path');
const URL = 'file://' + path.join(__dirname, '../app/src/main/assets/index.html');

let pass = 0, fail = 0;
const ok = (n, c, x) => { c ? (pass++, console.log("  ✓ " + n)) : (fail++, console.log("  ✗ " + n, x ?? "")); };

const SAHTE = () => {
  window.__cagrilar = [];
  window.KertikNative = {
    goster: (a, b, c, d, e) => window.__cagrilar.push({ m: "goster", baslik: a, alt: b, temel: c, geri: d, molada: e }),
    gizle: () => window.__cagrilar.push({ m: "gizle" }),
    bildirimIzniVar: () => { window.__cagrilar.push({ m: "izinVar" }); return true; },
    bildirimIzniIste: () => window.__cagrilar.push({ m: "izinIste" }),
    dndIzniVar: () => { window.__cagrilar.push({ m: "dndIzniVar" }); return true; },
    dndIzniIste: () => window.__cagrilar.push({ m: "dndIzniIste" }),
    dndBaslat: () => { window.__cagrilar.push({ m: "dndBaslat" }); return true; },
    dndBitir: () => { window.__cagrilar.push({ m: "dndBitir" }); return true; },
    ekraniAcikTut: (v) => window.__cagrilar.push({ m: "ekran", v }),
    titret: () => {},
    surum: () => "1.0",
    resimKaydet: (b64, ad) => { window.__cagrilar.push({ m: "resim", b64, ad }); return window.__resimSonuc || "galeri"; }
  };
};

(async () => {
  /* Kapalı ortamlarda chromium'un yeri KERTIK_KROM ile verilebilir. */
  const b = await chromium.launch(
    process.env.KERTIK_KROM ? { executablePath: process.env.KERTIK_KROM } : {});
  const ctx = await b.newContext();
  await ctx.addInitScript(SAHTE);
  const pg = await ctx.newPage();
  pg.on('pageerror', e => console.log('PAGEERROR:', e.message));
  await pg.goto(URL);
  await pg.waitForTimeout(400);

  const cagri = () => pg.evaluate(() => window.__cagrilar);
  const son = async m => (await cagri()).filter(c => c.m === m).pop();
  const temizle = () => pg.evaluate(() => { window.__cagrilar = []; });

  ok("köprü görüldü", await pg.evaluate(() => NATIVE !== null));
  ok("seans yokken bildirim gizleniyor", !!(await son("gizle")));

  /* --- seans başlat --- */
  await temizle();
  await pg.click('#bStart'); await pg.waitForTimeout(300);
  ok("izin bir kez soruldu", !!(await son("izinVar")));
  const g1 = await son("goster");
  ok("çalışıyor bildirimi gönderildi",
     g1 && g1.baslik === await pg.evaluate(() => soz("durum_calisiyor")), JSON.stringify(g1));
  ok("kronometre temeli seansın başlangıcı", g1 && Math.abs(Number(g1.temel) - (await pg.evaluate(() => activeSession().startedAt))) < 5, g1 && g1.temel);
  ok("temel metin olarak gönderiliyor (precision)", typeof g1.temel === "string", typeof g1.temel);
  ok("geri sayım kapalı (kronometre modu)", g1.geri === false);
  ok("molada değil", g1.molada === false);
  ok("ekran açık tutuluyor", (await son("ekran")).v === true);

  /* --- aynı durumda tekrar tekrar bildirim atmamalı --- */
  await temizle();
  await pg.waitForTimeout(2500);
  ok("durum değişmedikçe bildirim yenilenmiyor", (await cagri()).filter(c => c.m === "goster").length === 0);

  /* --- bildirimdeki Mola tuşu --- */
  await pg.evaluate(() => window.kertikNativeEylem("break"));
  await pg.waitForTimeout(200);
  const g2 = await son("goster");
  ok("Mola tuşu molayı başlattı", await pg.evaluate(() => stats(activeSession()).onBreak) === true);
  ok("bildirim molaya döndü",
     g2.baslik === await pg.evaluate(() => soz("durum_mola")) && g2.molada === true, JSON.stringify(g2));

  /* --- Devam --- */
  await pg.evaluate(() => window.kertikNativeEylem("resume"));
  await pg.waitForTimeout(200);
  ok("Devam tuşu molayı bitirdi", await pg.evaluate(() => stats(activeSession()).onBreak) === false);
  ok("mola süresi kayda geçti", await pg.evaluate(() => stats(activeSession()).brk) > 0);

  /* --- Bitir --- */
  await temizle();
  await pg.evaluate(() => window.kertikNativeEylem("end"));
  await pg.waitForTimeout(300);
  ok("Bitir tuşu seansı kapattı", await pg.evaluate(() => S.active) === null);
  ok("bildirim kaldırıldı", !!(await son("gizle")));
  ok("seans kayda geçti", await pg.evaluate(() => S.sessions.filter(s => s.endedAt).length) >= 1);

  /* --- DND (Rahatsız Etmeyin) kontrolü --- */
  await pg.evaluate(() => { closeSheet(); S.settings.dnd = true; save(); });
  await temizle();
  await pg.evaluate(() => startSession());
  await pg.waitForTimeout(200);
  ok("DND açıkken seans başlayınca dndBaslat çağrıldı", !!(await son("dndBaslat")));
  await temizle();
  await pg.evaluate(() => { finish(); closeSheet(); });
  await pg.waitForTimeout(200);
  ok("seans bitince dndBitir çağrıldı", !!(await son("dndBitir")));
  await pg.evaluate(() => { S.settings.dnd = false; save(); });

  /* --- pomodoro: geri sayım --- */
  await pg.evaluate(() => { closeSheet(); S.settings.mode = "pomodoro"; S.settings.pomoTarget = 25; save(); ctlKey = ""; render(); });
  await temizle();
  await pg.evaluate(() => startSession());
  await pg.waitForTimeout(300);
  const g3 = await son("goster");
  ok("pomodoroda geri sayım açık", g3 && g3.geri === true, JSON.stringify(g3));
  ok("pomodoro alt metni çentik sayıyor",
     g3.alt === await pg.evaluate(() => soz("capt_centik", { a: 0, b: 25 })), g3.alt);
  const hedef = await pg.evaluate(() => activeSession().startedAt + 25 * 60000);
  ok("geri sayım hedefi doğru an", Math.abs(Number(g3.temel) - hedef) < 2000, g3.temel + " vs " + hedef);

  /* --- hedef dolunca yukarı saymaya dönmeli --- */
  await pg.evaluate(() => { const s = activeSession(); s.startedAt -= 26 * 60000; s.events[0].at = s.startedAt; save(); });
  await temizle();
  await pg.evaluate(() => nativeBildir(true));
  await pg.waitForTimeout(150);
  const g4 = await son("goster");
  ok("hedef dolunca geri sayım kapanıyor", g4.geri === false, JSON.stringify(g4));
  ok("başlık fazla mesaiyi söylüyor",
     g4.baslik === await pg.evaluate(() => soz("bld_hedef_doldu")), g4.baslik);

  /* --- seans resmi köprüye base64 PNG olarak gidiyor --- */
  await pg.evaluate(() => { const b=document.getElementById("bEnd"); if(b) b.click(); closeSheet(); });
  await pg.waitForTimeout(200);
  await temizle();
  const sid = await pg.evaluate(() => S.sessions.filter(s => s.endedAt).pop().id);
  await pg.evaluate(id => resmiKaydet(S.sessions.find(s => s.id === id)), sid);
  await pg.waitForTimeout(2500);
  const r = await son("resim");
  ok("köprüye resim gönderildi", !!r);
  ok("PNG base64 ve boş değil", r && r.b64.length > 2000 && !r.b64.startsWith("data:"), r && r.b64.length);
  ok("dosya adı seansın tarihini taşıyor", r && /^kertik-\d{4}-\d{2}-\d{2}-\d{4}\.png$/.test(r.ad), r && r.ad);
  ok("kullanıcıya sonuç söylendi",
    (await pg.evaluate(() => document.getElementById("resimDurum").textContent)) ===
      await pg.evaluate(() => soz("resim_galeri")),
    await pg.evaluate(() => document.getElementById("resimDurum").textContent));
  await pg.evaluate(() => { window.__resimSonuc = "hata"; });
  await pg.evaluate(id => resmiKaydet(S.sessions.find(s => s.id === id)), sid);
  await pg.waitForTimeout(2500);
  ok("kaydedilemezse sessiz kalmıyor",
    (await pg.evaluate(() => document.getElementById("resimDurum").textContent)) ===
      await pg.evaluate(() => soz("resim_olmadi")));

  /* --- aynı seans hep aynı resim: desen saklanmıyor, kimlikten üretiliyor --- */
  const iki = await pg.evaluate(id => {
    const se = S.sessions.find(s => s.id === id);
    const a = seansResmi(se, 120, 260, 1, false).toDataURL();
    const b = seansResmi(se, 120, 260, 1, false).toDataURL();
    const c = seansResmi(S.sessions.filter(x => x.endedAt && x.id !== id).pop() || se, 120, 260, 1, false).toDataURL();
    return { ayni: a === b, farkli: a !== c };
  }, sid);
  ok("aynı seans hep aynı resmi veriyor", iki.ayni);

  /* --- köprü yokken hiçbir şey patlamamalı --- */
  const ctx2 = await b.newContext();
  const p2 = await ctx2.newPage();
  let hata = null;
  p2.on('pageerror', e => hata = e.message);
  await p2.goto(URL); await p2.waitForTimeout(300);
  await p2.click('#bStart'); await p2.waitForTimeout(600);
  ok("köprüsüz (tarayıcı) çalışmaya devam ediyor", hata === null && await p2.evaluate(() => S.active) !== null, hata);

  console.log("\n" + pass + " geçti, " + fail + " kaldı");
  await b.close();
  process.exit(fail ? 1 : 0);
})();
