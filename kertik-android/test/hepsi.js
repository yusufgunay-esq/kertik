/* TÜM TESTLER — tek komut.

     node hepsi.js            hepsini koş
     node hepsi.js duman      sadece adında "duman" geçenleri koş
     node hepsi.js --hizli    tarayıcı gerektirmeyenleri koş (birleştirme + çizim)

   Sahte Google sunucusunu kendi başlatır, iş bitince kapatır.
   Herhangi bir dosya kalırsa çıkış kodu 1'dir — CI bunu görür.

   Bir kereye mahsus kurulum:
     npm install playwright jsdom && npx playwright install chromium
*/
const fs = require("fs");
const { spawn, spawnSync } = require("child_process");
const path = require("path");
const net = require("net");

const KOK = __dirname;

function simulasyonGuncelle() {
  const simBuilder = path.join(KOK, "../../simulasyon/olustur-simulator.js");
  if (fs.existsSync(simBuilder)) {
    const r = spawnSync("node", [simBuilder], { stdio: "pipe" });
    if (r.status === 0) {
      console.log("· Simülasyon dosyası güncellendi: simulasyon/simulator.html");
    } else {
      console.error("· Simülasyon dosyası güncellenirken hata:", r.stderr.toString() || r.stdout.toString());
    }
  }
}

/* sira: ucuzdan pahalıya. Bir şey bozulduysa en hızlı test önce bağırsın. */
const TESTLER = [
  { ad: "birleştirme", dosya: "test-birlestirme.js", not: "senkron çakışma kuralları", tarayici: false },
  { ad: "çizim", dosya: "test-cizim.js", not: "çubuk, duvar, akış alanı", tarayici: false },
  { ad: "ses altyapısı", dosya: "test-ses-altyapisi.js", not: "çan akustiği", tarayici: false },
  { ad: "haptik dili", dosya: "test-haptik.js", not: "14 doku zarfı ve native köprü", tarayici: false },
  { ad: "tema", dosya: "test-tema.js", not: "açık, koyu, sistem teması", tarayici: false },
  { ad: "kayıt düzenleme", dosya: "test-kayit-duzenleme.js", not: "gece yarısını aşan seansın saat düzeltmesi", tarayici: false },
  { ad: "senkron UI", dosya: "test-senkron-ui.js", not: "senkronizasyon ve bulut arayüzü", tarayici: false },
  { ad: "yedek indirme", dosya: "test-yedek-indirme.js", not: "JSON dışa aktarma ve native köprü", tarayici: false },
  { ad: "dnd", dosya: "test-dnd.js", not: "odak modu ve native köprü", tarayici: false },
  { ad: "widget", dosya: "test-widget.js", not: "Android widget çizimleri", tarayici: false },
  { ad: "standby zen ve kapsül", dosya: "test-ambient.js", not: "masaüstü odak ve canlı bildirim", tarayici: false },
  { ad: "duvar stres", dosya: "test-duvar-stres.js", not: "sınır yükler ve aşırı yoğun ay", tarayici: false },
  { ad: "deneme çapası", dosya: "test-deneme.js", not: "pencere, göç, yedek, birleşme", tarayici: false },
  { ad: "algoritma stres", dosya: "test-algoritma-stres.js", not: "tohum, kum bahçesi, tırmık, bütçe", tarayici: false },
  { ad: "simülatör", dosya: "test-simulator.js", not: "sanal saat, senaryolar, palet", tarayici: false },
  { ad: "duman", dosya: "test-duman.js", not: "açılış, ana akış, konsol temizliği", tarayici: true },
  { ad: "native köprü", dosya: "test-native-kopru.js", not: "bildirim sözleşmesi", tarayici: true },
  { ad: "arayüz", dosya: "test-arayuz.js", not: "anahtar kaynağı, hata ekranı", tarayici: true },
  { ad: "dil", dosya: "test-dil.js", not: "15 dil, çoğul, tarih, sağdan-sola", tarayici: true },
  { ad: "uçtan uca", dosya: "test-uctan-uca.js", not: "iki cihaz arası senkron", tarayici: true, sahteGoogle: true }
];

const arg = process.argv.slice(2);
const hizli = arg.includes("--hizli");
const suzgec = arg.filter(a => !a.startsWith("--"));
const secili = TESTLER.filter(t =>
  (!hizli || !t.tarayici) &&
  (suzgec.length === 0 || suzgec.some(s => t.ad.includes(s) || t.dosya.includes(s))));

if (secili.length === 0) { console.error("Eşleşen test yok."); process.exit(1); }

/* --- bağımlılık kontrolü: eksikse baştan ve anlaşılır şekilde söyle --- */
function var_mi(paket) { try { require.resolve(paket, { paths: [KOK, process.cwd()] }); return true; } catch { return false; } }
const eksik = [];
if (secili.some(t => !t.tarayici) && !var_mi("jsdom")) eksik.push("jsdom");
if (secili.some(t => t.tarayici) && !var_mi("playwright")) eksik.push("playwright");
if (eksik.length) {
  console.error("\nEksik paket: " + eksik.join(", "));
  console.error("Kur:  npm install " + eksik.join(" ") +
    (eksik.includes("playwright") ? " && npx playwright install chromium" : "") + "\n");
  process.exit(1);
}

const portBos = p => new Promise(r => {
  const s = net.createConnection(p, "127.0.0.1");
  s.on("connect", () => { s.destroy(); r(false); });
  s.on("error", () => r(true));
});
const bekle = ms => new Promise(r => setTimeout(r, ms));

(async () => {
  /* Testler öncesi simülasyon dosyasını derle ve hazırla */
  simulasyonGuncelle();

  let google = null;
  if (secili.some(t => t.sahteGoogle)) {
    if (await portBos(8899) === false) {
      console.log("· sahte Google zaten 8899'de çalışıyor, yenisi açılmadı");
    } else {
      google = spawn("python3", [path.join(KOK, "sahte-google.py")], { stdio: "ignore" });
      for (let i = 0; i < 40 && await portBos(8899); i++) await bekle(250);
      console.log("· sahte Google açıldı (8899)");
    }
  }

  const sonuc = [];
  const t0 = Date.now();
  for (const t of secili) {
    console.log("\n\x1b[1m" + t.ad + "\x1b[0m — " + t.not);
    const b = Date.now();
    const r = spawnSync("node", [path.join(KOK, t.dosya)], { stdio: "inherit", cwd: KOK });
    sonuc.push({ ...t, kod: r.status, sn: ((Date.now() - b) / 1000).toFixed(1) });
  }

  if (google) google.kill();

  /* Testler sonrası simülasyon dosyasının güncelliğini kesinleştir */
  simulasyonGuncelle();

  const kalan = sonuc.filter(s => s.kod !== 0);
  console.log("\n" + "─".repeat(52));
  for (const s of sonuc) console.log((s.kod === 0 ? "  ✓ " : "  ✗ ") + s.ad.padEnd(16) + s.sn + "s");
  console.log("─".repeat(52));
  console.log(kalan.length === 0
    ? `\x1b[32mHepsi geçti\x1b[0m — ${sonuc.length} dosya, ${((Date.now() - t0) / 1000).toFixed(1)}s`
    : `\x1b[31m${kalan.length} dosya kaldı:\x1b[0m ` + kalan.map(k => k.ad).join(", "));

  process.exit(kalan.length ? 1 : 0);
})();
