const fs = require("fs");
const h = fs.readFileSync(require("path").join(__dirname,"../app/src/main/assets/index.html"), "utf8");
const src = h.split("/* --- MERGE:BEGIN ---")[1].split("/* --- MERGE:END --- */")[0];
const mergeStates = new Function(src.replace(/^[\s\S]*?function mergeStates/, "return function mergeStates").replace(/\/\* --- MERGE:END[\s\S]*$/, "") + ";")();

let pass = 0, fail = 0;
const T = 1e12;                       // sabit "şimdi"
function ok(name, cond, extra) { if (cond) { pass++; console.log("  ✓ " + name); } else { fail++; console.log("  ✗ " + name, extra ?? ""); } }
const se = (id, ed, extra) => Object.assign({ id, startedAt: T - 36e5, endedAt: T - 18e5, editedAt: ed, events: [] }, extra || {});
const tk = (id, ed, extra) => Object.assign({ id, title: id, createdAt: T - 36e5, editedAt: ed, status: "bekliyor" }, extra || {});
const st = o => Object.assign({ sessions: [], tasks: [], tombstones: [], active: null, settings: {}, settingsEditedAt: 0 }, o);
const M = (a, b) => mergeStates(a, b, { now: T });

console.log("\n1) Birleşme temeli");
{
  const r = M(st({ sessions: [se("a", 100)] }), st({ sessions: [se("b", 100)] }));
  ok("iki cihazın ayrı seansları birleşir", r.sessions.length === 2);
}
{
  const r = M(st({ sessions: [se("a", 100, { note: "eski" })] }), st({ sessions: [se("a", 200, { note: "yeni" })] }));
  ok("aynı id → yeni editedAt kazanır", r.sessions.length === 1 && r.sessions[0].note === "yeni");
}
{
  const r = M(st({ sessions: [se("a", 300, { note: "yerel" })] }), st({ sessions: [se("a", 200, { note: "uzak" })] }));
  ok("yerel daha yeniyse yerel kazanır", r.sessions[0].note === "yerel");
}
{
  const r = M(st({ sessions: [se("a", 100)] }), st({}));
  ok("boş uzak taraf veriyi silmez", r.sessions.length === 1);
}
{
  const r = M(st({}), st({ sessions: [se("a", 100)] }));
  ok("boş yerel taraf uzaktan veriyi çeker", r.sessions.length === 1);
}

console.log("\n2) Silme ve mezar taşı");
{
  const r = M(st({ tombstones: [{ kind: "session", id: "a", at: T - 1000 }] }), st({ sessions: [se("a", T - 5000)] }));
  ok("bir cihazda silinen kayıt diğerinden geri dirilmez", r.sessions.length === 0);
  ok("mezar taşı korunur (üçüncü cihaz için)", r.tombstones.length === 1);
}
{
  const r = M(st({ sessions: [se("a", T - 500, { note: "düzelttim" })] }), st({ tombstones: [{ kind: "session", id: "a", at: T - 5000 }] }));
  ok("silmeden SONRA düzeltilen kayıt geri gelir", r.sessions.length === 1 && r.sessions[0].note === "düzelttim");
  ok("çözülen mezar taşı temizlenir", r.tombstones.length === 0);
}
{
  const r = M(st({ tombstones: [{ kind: "task", id: "t1", at: T - 200 * 864e5 }] }), st({}));
  ok("6 aydan eski mezar taşı çöpe atılır", r.tombstones.length === 0);
}
{
  const r = M(st({ tasks: [tk("t1", T - 9000)], tombstones: [{ kind: "task", id: "t1", at: T - 400 }] }), st({ tasks: [tk("t1", T - 9000)] }));
  ok("görev silme de çalışır", r.tasks.length === 0);
}

console.log("\n3) Aktif seans");
{
  const A = st({ sessions: [se("x", 100, { endedAt: null, startedAt: T - 6e5 })], active: "x" });
  const B = st({ sessions: [se("y", 100, { endedAt: null, startedAt: T - 6e5 })], active: "y" });
  const r = M(A, B);
  ok("iki cihazda da seans açıksa elindeki cihaz kazanır", r.active === "x");
  ok("diğerinin seansı yine de kaydedilir", r.sessions.length === 2);
}
{
  const B = st({ sessions: [se("y", 100, { endedAt: null, startedAt: T - 6e5 })], active: "y" });
  const r = M(st({}), B);
  ok("yerel boşsa uzaktaki açık seans devralınır", r.active === "y");
}
{
  const B = st({ sessions: [se("y", 100, { endedAt: null, startedAt: T - 40 * 36e5 })], active: "y" });
  const r = M(st({}), B);
  ok("40 saatlik unutulmuş seans devralınmaz", r.active === null);
}
{
  const r = M(st({ sessions: [se("a", 100)], active: "a" }), st({}));
  ok("bitmiş seans aktif sayılmaz", r.active === null);
}

console.log("\n4) Ayarlar");
{
  const r = M(st({ settings: { theme: "light" }, settingsEditedAt: 100 }), st({ settings: { theme: "dark" }, settingsEditedAt: 200 }));
  ok("son değiştirilen ayar kazanır", r.settings.theme === "dark");
  const r2 = M(st({ settings: { theme: "light" }, settingsEditedAt: 300 }), st({ settings: { theme: "dark" }, settingsEditedAt: 200 }));
  ok("tersi de doğru", r2.settings.theme === "light");
}

console.log("\n5) Saflık ve sıra");
{
  const A = st({ sessions: [se("a", 100)] });
  const snap = JSON.stringify(A);
  M(A, st({ sessions: [se("b", 100)] }));
  ok("girdiyi değiştirmez", JSON.stringify(A) === snap);
}
{
  const a1 = se("a", 100); a1.startedAt = T - 1e5;
  const b1 = se("b", 100); b1.startedAt = T - 9e5;
  const r = M(st({ sessions: [a1] }), st({ sessions: [b1] }));
  ok("seanslar başlangıç saatine göre sıralı", r.sessions[0].id === "b");
}
{
  const A = st({ sessions: [se("a", 100), se("b", 200)], tasks: [tk("t", 50)] });
  const B = st({ sessions: [se("b", 300, { note: "b2" })], tasks: [tk("t", 50)] });
  const once = M(A, B);
  const twice = M(once, JSON.parse(JSON.stringify(once)));
  ok("iki kez eşitlemek aynı sonucu verir (idempotent)",
     JSON.stringify(once.sessions) === JSON.stringify(twice.sessions) && once.tasks.length === twice.tasks.length);
}
{
  const r = M(st({ sessions: [{ id: "z", startedAt: T - 1e5, endedAt: T, events: [] }] }), st({}));
  ok("editedAt'i olmayan eski kayıt (v2.0 verisi) kaybolmaz", r.sessions.length === 1);
}

console.log("\n" + pass + " geçti, " + fail + " kaldı");
process.exit(fail ? 1 : 0);
