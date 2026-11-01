/* Dil testi — 15 dilin her birinde uygulamayı açar, ekranları gezer,
   metin taşması / eksik anahtar / yanlış yön arar. */
const { chromium } = require("playwright");
const path = require("path");
/* Yerel kurulumda tarayıcı yolu gerekmiyor; kapalı ortamlarda
   KERTIK_KROM ile chromium'un yeri verilebilir. */
const KROM = process.env.KERTIK_KROM || null;
const URLS = "file://" + path.join(__dirname, "../app/src/main/assets/index.html");

let gecti = 0, kaldi = 0;
function ok(ad, kosul, ek) {
  if (kosul) { gecti++; }
  else { kaldi++; console.log("  ✗ " + ad + (ek ? "  → " + ek : "")); }
}

(async () => {
  const br = await chromium.launch(KROM ? { executablePath: KROM } : {});

  /* --- 1) anahtar bütünlüğü --- */
  {
    const pg = await br.newPage();
    await pg.goto(URLS);
    const r = await pg.evaluate(() => {
      const diller = Object.keys(SOZLUK);
      const ref = Object.keys(SOZLUK.tr);
      const eksik = {}, fazla = {};
      for (const d of diller) {
        const k = Object.keys(SOZLUK[d]);
        const e = ref.filter(x => !(x in SOZLUK[d]));
        const f = k.filter(x => ref.indexOf(x) < 0);
        if (e.length) eksik[d] = e;
        if (f.length) fazla[d] = f;
      }
      return { diller, sayi: ref.length, eksik, fazla };
    });
    console.log("\n1) Sözlük bütünlüğü");
    ok("15 dil var", r.diller.length === 15, r.diller.length);
    ok("hiçbir dilde anahtar eksik değil", Object.keys(r.eksik).length === 0, JSON.stringify(r.eksik));
    ok("fazladan anahtar yok", Object.keys(r.fazla).length === 0, JSON.stringify(r.fazla));
    console.log("   (" + r.sayi + " anahtar × " + r.diller.length + " dil)");

    /* kodda soz() ile çağrılan her anahtar sözlükte var mı */
    /* kod bölgesi = sözlük bloğu çıkarılmış kaynak */
    const tam = await pg.evaluate(() => document.documentElement.outerHTML);
    const b0 = tam.indexOf("const SOZLUK = {"), b1 = tam.indexOf("\n};\n", b0) + 4;
    const kod = tam.slice(0, b0) + tam.slice(b1);
    const ref = await pg.evaluate(() => Object.keys(SOZLUK.tr));
    /* anahtar ya doğrudan soz("x") ile ya da yz/ph yardımcılarıyla geçiyor */
    const gecen = new Set([...kod.matchAll(/"([a-z][a-z0-9_]*_[a-z0-9_]+|s_google|s_elle|s_ekran)"/g)].map(m => m[1]));
    const yok = [...gecen].filter(k => ref.indexOf(k) < 0 && /^(nav|mod|durum|ph|btn|capt|alt|ek|dk|flash|um|aw|oz|kayit|lgnd|lbl|sil|ev|gorev|st|neden|kalan|ayar|s|yd|ia|sy|hata|resim|bld|sure|tanit)_/.test(k));
    ok("koddaki her anahtar sözlükte var", yok.length === 0, yok.join(", "));
    /* dinamik kurulanlar: neden_*, mod_*, nav_* ve sistem etiketi */
    const kullanilmayan = ref.filter(k => !gecen.has(k) && !/^neden_|^s_dil_sistem$/.test(k));
    ok("ölü anahtar yok", kullanilmayan.length === 0, kullanilmayan.join(", "));
    await pg.close();
  }

  /* --- 2) her dilde ekranlar --- */
  console.log("\n2) Ekranlar — 15 dil");
  const diller = ["tr","en","de","fr","es","it","pt-BR","nl","pl","ru","ja","ko","zh-Hans","zh-Hant","ar"];
  for (const dil of diller) {
    const ctx = await br.newContext({ viewport: { width: 360, height: 640 }, locale: dil });
    const pg = await ctx.newPage();
    const konsol = [];
    pg.on("console", m => { if (m.type() === "error") konsol.push(m.text()); });
    pg.on("pageerror", e => konsol.push(String(e)));
    await pg.goto(URLS);
    await pg.evaluate(() => { try { localStorage.clear(); } catch (e) {} });
    await pg.reload();
    await pg.waitForTimeout(160);

    const secilen = await pg.evaluate(() => DIL);
    ok(dil + ": doğru dil seçildi", secilen === dil, secilen);

    /* veri üret: bir seans + görevler */
    await pg.evaluate(() => {
      const t = Date.now() - 95 * 60000;
      S.sessions.push({
        id: "x1", startedAt: t, endedAt: t + 95 * 60000, dayKey: dayKey(t),
        note: "", mode: "stopwatch", target: 0, awayMs: 4 * 60000, unconfirmedOk: false,
        edited: false, editedAt: t, akisV: 2,
        events: [{ type: "start", at: t }, { type: "break_start", at: t + 30 * 60000 },
                 { type: "break_end", at: t + 42 * 60000 }, { type: "end", at: t + 95 * 60000 }]
      });
      S.tasks.push({ id: "t1", title: "Deneme", plannedFor: todayKey(), status: "bitti", reason: null, moveCount: 0, order: 0, createdAt: t, closedAt: t, editedAt: t });
      S.tasks.push({ id: "t2", title: "İkinci", plannedFor: todayKey(), status: "olmadi", reason: "zaman", moveCount: 1, order: 1, createdAt: t, closedAt: t, editedAt: t });
      S.tasks.push({ id: "t3", title: "Üçüncü", plannedFor: todayKey(), status: "bekliyor", reason: null, moveCount: 0, order: 2, createdAt: t, closedAt: null, editedAt: t });
      save(); render();
    });

    const rtlBekleniyor = dil === "ar";
    const yonu = await pg.evaluate(() => document.documentElement.dir);
    ok(dil + ": yazı yönü", yonu === (rtlBekleniyor ? "rtl" : "ltr"), yonu);

    /* dört sekmeyi de gez */
    const tasan = [];
    for (const sekme of ["timer", "tasks", "log", "settings"]) {
      await pg.click('[data-tab="' + sekme + '"]');
      await pg.waitForTimeout(120);
      const t = await pg.evaluate(() => {
        const kotu = [];
        document.querySelectorAll(".page.on button, .page.on .lbl, .page.on .pagetitle, nav button")
          .forEach(e => {
            if (!e.offsetParent) return;
            /* yatay taşma: içerik kutusundan 2px'ten fazla dışarı çıkıyorsa */
            if (e.scrollWidth > e.clientWidth + 2) kotu.push(e.className + " «" + e.textContent.trim().slice(0, 40) + "»");
          });
        return kotu;
      });
      tasan.push(...t.map(x => sekme + ": " + x));
    }
    ok(dil + ": metin taşması yok", tasan.length === 0, tasan.slice(0, 4).join(" | "));

    /* sheet'ler: görev menüsü ve neden ekranı */
    await pg.click('[data-tab="tasks"]');
    await pg.waitForTimeout(80);
    await pg.click('[data-t="t3"]');
    await pg.waitForTimeout(120);
    const sheetMetin = await pg.textContent("#sheetBox");
    ok(dil + ": görev menüsü doldu", sheetMetin.trim().length > 10);
    ok(dil + ": sheet'te anahtar sızmadı", !/\b[a-z]+_[a-z_]+\b/.test(sheetMetin), sheetMetin.slice(0, 80));

    /* ayarlar → dil seçimi ekranı */
    await pg.evaluate(() => closeSheet());
    await pg.click('[data-tab="settings"]');
    await pg.waitForTimeout(100);
    const dilBtn = await pg.textContent("#dilBtn");
    ok(dil + ": ayarlarda dil adı görünüyor", dilBtn.trim().length > 0, dilBtn);
    await pg.click("#dilBtn");
    await pg.waitForTimeout(120);
    const secenek = await pg.evaluate(() => document.querySelectorAll("#sheetBox [data-l]").length);
    ok(dil + ": 16 dil seçeneği (sistem + 15)", secenek === 16, secenek);

    ok(dil + ": konsol temiz", konsol.length === 0, konsol.slice(0, 2).join(" | "));
    await ctx.close();
  }

  /* --- 3) biçimlendirme doğruluğu --- */
  console.log("\n3) Biçimlendirme");
  {
    const ctx = await br.newContext({ locale: "en-US" });
    const pg = await ctx.newPage();
    await pg.goto(URLS);
    const r = await pg.evaluate(() => {
      const c = {};
      const dene = d => {
        S.settings.lang = d; dilKur();
        return {
          sure: human(95 * 60000),
          bir: human(60 * 60000),
          kisa: human(7 * 60000),
          seans1: soz("alt_bugun", { s: "1h", n: 1 }),
          seans5: soz("alt_bugun", { s: "5h", n: 5 }),
          gun: soz("sy_gun_once", { n: 2 }),
          tarih: fullDate("2026-08-16"),
          bugun: dayLabel(new Date().getFullYear() + "-" +
            String(new Date().getMonth() + 1).padStart(2, "0") + "-" +
            String(new Date().getDate()).padStart(2, "0")),
          saat: hhmm(new Date(2026, 7, 16, 14, 5).getTime()),
          ham: hhmmHam(new Date(2026, 7, 16, 14, 5).getTime())
        };
      };
      for (const d of ["tr","en","de","ru","ja","ar","pl"]) c[d] = dene(d);
      S.settings.lang = "auto"; dilKur();
      return c;
    });
    for (const d in r) console.log("   " + d.padEnd(3) + " " + JSON.stringify(r[d]));
    ok("Rusça çoğul 5 → 'сессий'", /сесси[йи]/.test(r.ru.seans5), r.ru.seans5);
    ok("Lehçe çoğul 5 ≠ 1", r.pl.seans1 !== r.pl.seans5);
    ok("İngilizce 1 seans tekil", /1 session\b/.test(r.en.seans1), r.en.seans1);
    ok("ham saat her dilde 24 saat", r.en.ham === "14:05" && r.ar.ham === "14:05", r.en.ham + "/" + r.ar.ham);
    ok("Türkçe tarih küçük harf", r.tr.tarih === r.tr.tarih.toLocaleLowerCase("tr"), r.tr.tarih);
    ok("Almanca tarih büyük harfli", /[A-ZÄÖÜ]/.test(r.de.tarih), r.de.tarih);
    ok("bugün etiketi dile göre", r.tr.bugun === "bugün" && r.en.bugun === "today", r.tr.bugun + "/" + r.en.bugun);
    ok("Arapça rakamlar latin", /\d/.test(r.ar.ham));
    await ctx.close();
  }

  await br.close();
  console.log("\n" + gecti + " geçti, " + kaldi + " kaldı");
  process.exit(kaldi ? 1 : 0);
})();
