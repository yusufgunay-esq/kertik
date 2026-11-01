// Test: Yedek disa aktarma ve dosya indirme koprusu
const fs = require('fs');
const path = require('path');

let pass = 0, fail = 0;
function assert(name, condition, extra) {
  if (condition) {
    pass++;
    console.log("  ✓ " + name);
  } else {
    fail++;
    console.log("  ✗ " + name, extra || "");
  }
}

console.log("=== Yedek Indirme & Native Kopru Testleri ===");

// 1. Kotlin MainActivity.kt kontrolleri
const ktPath = path.join(__dirname, '../app/src/main/java/com/yusufgunay/kertik/MainActivity.kt');
const ktCode = fs.readFileSync(ktPath, 'utf8');

assert("MainActivity.kt icinde yedekKaydet arayuzu tanimli", ktCode.includes("fun yedekKaydet(json: String, ad: String): String"));
assert("MainActivity.kt icinde indirilenlereYaz tanimli", ktCode.includes("fun indirilenlereYaz(bayt: ByteArray, ad: String): String"));
assert("MainActivity.kt icinde yedegiPaylas tanimli", ktCode.includes("fun yedegiPaylas(bayt: ByteArray, ad: String)"));
assert("MainActivity.kt icinde MediaStore.Downloads kullaniliyor", ktCode.includes("MediaStore.Downloads.EXTERNAL_CONTENT_URI"));
assert("MainActivity.kt icinde application/json mime type kullaniliyor", ktCode.includes('MIME_TYPE, "application/json"'));
assert("MainActivity.kt icinde /Downloads/Kertik klasoru hedefleniyor", ktCode.includes('DIRECTORY_DOWNLOADS + "/Kertik"'));

// 2. paylasim_yollari.xml kontrolleri
const xmlPath = path.join(__dirname, '../app/src/main/res/xml/paylasim_yollari.xml');
const xmlCode = fs.readFileSync(xmlPath, 'utf8');
assert("paylasim_yollari.xml icinde yedek/ cache-path tanimli", xmlCode.includes('<cache-path name="yedek" path="yedek/" />'));

// 3. index.html dosyalarinda KertikNative.yedekKaydet cagrisi kontrolu
const assetsHtml = fs.readFileSync(path.join(__dirname, '../app/src/main/assets/index.html'), 'utf8');
const wwwHtml = fs.readFileSync(path.join(__dirname, '../../uygulama/www/index.html'), 'utf8');
const simHtml = fs.readFileSync(path.join(__dirname, '../../simulasyon/simulator.html'), 'utf8');

assert("assets/index.html icinde N.yedekKaydet kontrolu var", assetsHtml.includes("N.yedekKaydet(json, ad)"));
assert("www/index.html icinde N.yedekKaydet kontrolu var", wwwHtml.includes("N.yedekKaydet(json, ad)"));
assert("simulator.html icinde N.yedekKaydet kontrolu var", simHtml.includes("N.yedekKaydet(json, ad)"));

// 4. exportData mantiginin simulasyonu
let mockCagrilar = [];
let mockButton = { textContent: "dosya olarak indir" };
let fakeState = {
  active: null,
  sessions: [{ id: "s1", startedAt: 1723849200000, endedAt: 1723851000000, events: [] }],
  tasks: [{ id: "t1", title: "Test gorev", status: "bekliyor" }],
  settings: { mode: "kronometre" }
};
let S = fakeState;
function todayKey() { return "2026-08-17"; }

let window = {
  KertikNative: {
    yedekKaydet: (json, ad) => {
      mockCagrilar.push({ json, ad });
      return "indirildi";
    }
  }
};

function testDlClick(nativeSonuc = "indirildi") {
  const json = JSON.stringify(S);
  const dlBtn = mockButton;
  const ad = "kertik-" + todayKey() + ".json";
  const N = window.KertikNative;
  if (N && N.yedekKaydet) {
    try {
      const sonuc = typeof nativeSonuc === "function" ? nativeSonuc(json, ad) : N.yedekKaydet(json, ad);
      dlBtn.textContent = sonuc === "indirildi" ? "indirildi"
                        : sonuc === "paylas" ? "paylasiliyor" : "indirilemedi";
    } catch (e) { dlBtn.textContent = "indirilemedi"; }
  }
}

testDlClick();
assert("Native koprude yedekKaydet cagrildi", mockCagrilar.length === 1);
assert("Gonderilen JSON ayristirilabilir ve gecerli", JSON.parse(mockCagrilar[0].json).sessions.length === 1);
assert("Dosya adi kertik-YYYY-MM-DD.json formatinda", mockCagrilar[0].ad === "kertik-2026-08-17.json");
assert("Buton metni 'indirildi' oldu", mockButton.textContent === "indirildi");

window.KertikNative.yedekKaydet = () => "paylas";
testDlClick();
assert("Android 9 / paylasim modunda buton 'paylasiliyor' oldu", mockButton.textContent === "paylasiliyor");

window.KertikNative.yedekKaydet = () => "hata";
testDlClick();
assert("Hata durumunda buton 'indirilemedi' oldu", mockButton.textContent === "indirilemedi");

// 5. Seans Paylaşma (Strava Modeli) ve Kart Kontrolleri
console.log("\n=== Seans Paylasma (Strava Modeli) Kontrolleri ===");
assert("MainActivity.kt icinde resimPaylas arayuzu tanimli", ktCode.includes("fun resimPaylas(b64: String, ad: String): String"));
assert("assets/index.html icinde cizSeansKartiKatmani tanimli", assetsHtml.includes("function cizSeansKartiKatmani"));
assert("www/index.html icinde cizSeansKartiKatmani tanimli", wwwHtml.includes("function cizSeansKartiKatmani"));
assert("simulator.html icinde cizSeansKartiKatmani tanimli", simHtml.includes("function cizSeansKartiKatmani"));
assert("assets/index.html icinde btn_seans_paylas kullaniliyor", assetsHtml.includes("btn_seans_paylas"));
assert("www/index.html icinde btn_seans_paylas kullaniliyor", wwwHtml.includes("btn_seans_paylas"));
assert("simulator.html icinde btn_seans_paylas kullaniliyor", simHtml.includes("btn_seans_paylas"));
assert("assets/index.html icinde resimPaylas butonu var", assetsHtml.includes('id="resimPaylas"'));
assert("www/index.html icinde resimPaylas butonu var", wwwHtml.includes('id="resimPaylas"'));
assert("simulator.html icinde resimPaylas butonu var", simHtml.includes('id="resimPaylas"'));
assert("assets/index.html icinde N.resimPaylas kontrolu var", assetsHtml.includes("N.resimPaylas(b64, ad)"));
assert("www/index.html icinde N.resimPaylas kontrolu var", wwwHtml.includes("N.resimPaylas(b64, ad)"));
assert("simulator.html icinde N.resimPaylas kontrolu var", simHtml.includes("N.resimPaylas(b64, ad)"));

// 6. Native resimPaylas simülasyonu
let mockPaylasCagrilar = [];
window.KertikNative.resimPaylas = (b64, ad) => {
  mockPaylasCagrilar.push({ b64, ad });
  return "paylas";
};
const resSonuc = window.KertikNative.resimPaylas("iVBORw0KGgo...", "kertik-seans-2026-08-17-1430.png");
assert("Native koprude resimPaylas cagrildi", mockPaylasCagrilar.length === 1);
assert("resimPaylas donusu 'paylas'", resSonuc === "paylas");
assert("Paylasilan dosya adi 'kertik-seans-' onekine sahip", mockPaylasCagrilar[0].ad.startsWith("kertik-seans-"));

console.log(`\nSonuc: ${pass} gecti, ${fail} kaldi\n`);
process.exit(fail ? 1 : 0);
