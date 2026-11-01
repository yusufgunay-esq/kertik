/* Kayıt satırındaki saat düzenlemesi: gece yarısını aşan seanslar da
   düzeltilebilmeli, yanlış yazılan saat seansı şişirmemeli.
   Tarayıcı gerektirmez; kural index.html'den sökülüp doğrudan koşulur. */
const fs = require("fs");
const path = require("path");
const h = fs.readFileSync(path.join(__dirname, "../app/src/main/assets/index.html"), "utf8");

const bas = h.indexOf("function saatiGunaOturt");
const son = h.indexOf("/* --- KAYIT-DUZENLEME:END --- */");
if (bas < 0 || son < 0) { console.error("Kural bloğu bulunamadı."); process.exit(1); }
const src = h.slice(bas, son);

const kur = new Function(`
  const pad = n => String(n).padStart(2, "0");
  function dayKey(ts) { const d = new Date(ts); return d.getFullYear() + "-" + pad(d.getMonth() + 1) + "-" + pad(d.getDate()); }
  ${src}
  return { saatiGunaOturt, seansSaatiDuzenle, dayKey };
`)();
const { saatiGunaOturt, seansSaatiDuzenle, dayKey } = kur;

let pass = 0, fail = 0;
function ok(ad, kosul, ek) { if (kosul) { pass++; console.log("  ✓ " + ad); } else { fail++; console.log("  ✗ " + ad, ek ?? ""); } }
const g = (y, ay, gun, s, d) => new Date(y, ay - 1, gun, s, d, 0, 0).getTime();
const dk = ms => Math.round(ms / 60000);
const seans = (b, bit, ev) => ({
  id: "x", startedAt: b, endedAt: bit, dayKey: dayKey(b),
  events: ev || [{ type: "start", at: b }, { type: "end", at: bit }]
});

/* Ekrandaki hata: 8 Eylül 20:26'da başlayıp bitirilmesi unutulan,
   9 Eylül 17:46'da kapatılan 21s 20dk'lık seans. */
const BAS = g(2026, 9, 8, 20, 26);
const BIT = g(2026, 9, 9, 17, 46);

console.log("\n1) Girilen saat doğru güne oturuyor mu");
ok("bitiş, başlangıçtan sonraki ilk o saat",
  saatiGunaOturt("21:06", BAS, true) === g(2026, 9, 8, 21, 6));
ok("aynı saat girilirse bir sonraki güne kayar (0 uzunluk olmaz)",
  saatiGunaOturt("20:26", BAS, true) === g(2026, 9, 9, 20, 26));
ok("başlangıç, bitişten önceki son o saat",
  saatiGunaOturt("16:00", BIT, false) === g(2026, 9, 9, 16, 0));
ok("bitişten sonraki saat girilirse bir önceki güne düşer",
  saatiGunaOturt("21:00", BIT, false) === g(2026, 9, 8, 21, 0));
ok("boş ya da bozuk değer null döner",
  saatiGunaOturt("", BAS, true) === null && saatiGunaOturt("abc", BAS, true) === null);

console.log("\n2) Gece yarısını aşan seans düzeltilebiliyor");
{
  const s = seans(BAS, BIT);
  const r = seansSaatiDuzenle(s, "end", "21:06");
  ok("unutulmuş seansın bitişi geceye çekilir", r && dk(s.endedAt - s.startedAt) === 40, dk(s.endedAt - s.startedAt) + "dk");
  ok("bitiş damgası da düzelir", s.events[s.events.length - 1].at === s.endedAt);
  ok("seans düzeltilmiş işaretlenir", s.edited === true);
}
{
  const s = seans(BAS, BIT);
  const r = seansSaatiDuzenle(s, "start", "16:00");
  ok("başlangıç bitişin gününe çekilebilir", r && dk(s.endedAt - s.startedAt) === 106);
  ok("gün başlığı da taşınır", s.dayKey === "2026-09-09");
}

console.log("\n3) Şişirme ve saçma değerler geri çevriliyor");
{
  const b = g(2026, 9, 8, 9, 0), bit = g(2026, 9, 8, 10, 0);
  const s = seans(b, bit);
  ok("bir saatlik seans, başlangıçtan önceki bitişle 23 saate çıkmaz",
    seansSaatiDuzenle(s, "end", "08:00") === false && s.endedAt === bit);
  ok("makul uzatma kabul edilir",
    seansSaatiDuzenle(s, "end", "11:30") === true && dk(s.endedAt - s.startedAt) === 150);
}
{
  const b = g(2026, 9, 8, 9, 0), bit = g(2026, 9, 8, 10, 0);
  const s = seans(b, bit, [
    { type: "start", at: b },
    { type: "break_start", at: g(2026, 9, 8, 9, 30) },
    { type: "break_end", at: g(2026, 9, 8, 9, 40) },
    { type: "end", at: bit }
  ]);
  ok("mola damgalarını dışarıda bırakan bitiş kabul edilmez",
    seansSaatiDuzenle(s, "end", "09:20") === false && s.endedAt === bit);
  ok("molaları kapsayan bitiş kabul edilir",
    seansSaatiDuzenle(s, "end", "09:50") === true);
}
{
  const s = { id: "y", startedAt: BAS, endedAt: null, events: [{ type: "start", at: BAS }] };
  ok("süren seans düzenlenmez", seansSaatiDuzenle(s, "end", "21:00") === false);
}

console.log("\n4) Gün aşımı ekranda görünüyor");
{
  const ar = h.slice(h.indexOf("function aralik(a, b)"), h.indexOf("function clockStr"));
  ok("aralık, gün farkı varsa +n işareti basıyor", /gunartisi/.test(ar) && /fark > 0/.test(ar));
  ok("+n için stil tanımlı", /\.gunartisi\{/.test(h));
}

console.log("\n" + (fail ? `${pass} geçti, ${fail} kaldı` : `${pass} geçti, 0 kaldı`));
process.exit(fail ? 1 : 0);
