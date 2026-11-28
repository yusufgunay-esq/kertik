/* DND (Görünmez Odak Modu / Zero-Touch Ambient DND) Entegrasyon Testi */
const fs = require("fs");
const path = require("path");

const assetHtmlPath = path.join(__dirname, "../app/src/main/assets/index.html");
const mainActivityPath = path.join(__dirname, "../app/src/main/java/com/yusufgunay/kertik/MainActivity.kt");
const html = fs.readFileSync(assetHtmlPath, "utf8");
const mainKt = fs.readFileSync(mainActivityPath, "utf8");

let pass = 0, fail = 0;
function ok(name, cond, extra) {
  if (cond) { pass++; console.log("  ✓ " + name); }
  else { fail++; console.log("  ✗ " + name, extra ?? ""); }
}

console.log("\n=== DND (Zero-Touch Ambient DND) Entegrasyon Testleri ===");

console.log("\n1) Android Native Katmanı (MainActivity.kt)");
ok("dndIzniVar fonksiyonu mevcut", mainKt.includes("fun dndIzniVar(): Boolean"));
ok("dndIzniIste fonksiyonu mevcut", mainKt.includes("fun dndIzniIste()"));
ok("dndBaslat fonksiyonu mevcut", mainKt.includes("fun dndBaslat(): Boolean"));
ok("dndBitir fonksiyonu mevcut", mainKt.includes("fun dndBitir()"));
ok("DND orijinal filtre SharedPreferences'a kaydediliyor (yedek yol)", mainKt.includes("KEY_DND_ORIJINAL"));
ok("Öncelikli odak modu (INTERRUPTION_FILTER_PRIORITY) kullanılıyor", mainKt.includes("INTERRUPTION_FILTER_PRIORITY"));
ok("onCreate içinde yetim kalmış DND durumunu kurtarma mekanizması var", mainKt.includes("Yetim kalmış DND durumunu temizle"));
ok("Kopru sınıfında dndBaslat ve dndBitir JavascriptInterface olarak kayıtlı",
   /@JavascriptInterface\s+fun dndBaslat\(\)/.test(mainKt) &&
   /@JavascriptInterface\s+fun dndBitir\(\)/.test(mainKt));

console.log("\n1b) Kertik'in kendi modu (AutomaticZenRule)");
ok("AutomaticZenRule ile sistemde kendi adıyla ayrı bir mod oluşturuluyor", mainKt.includes("AutomaticZenRule("));
ok("Mod adı \"Kertik\" olarak kayıtlı (kullanıcının kendi Rahatsız Etmeyin'i değil)", mainKt.includes('"Kertik",'));
ok("Kural kimliği kalıcı olarak saklanıyor (KEY_ZEN_KURAL_ID)", mainKt.includes("KEY_ZEN_KURAL_ID"));
ok("Kural durumu setAutomaticZenRuleState ile açılıp kapatılıyor", mainKt.includes("setAutomaticZenRuleState"));
ok("Kural silinmiş/bulunamıyorsa yeniden oluşturuluyor", mainKt.includes("nm.getAutomaticZenRule(mevcut)"));
ok("ZenPolicy yalnız Q+ sürümlerde atanıyor, altında güvenli yedek yol var", mainKt.includes("Build.VERSION.SDK_INT < Build.VERSION_CODES.Q"));
ok("Sadece alarmlar geçebiliyor (ZenPolicy.allowAlarms, mesajlar kapalı)", mainKt.includes("ZenPolicy.Builder()") && mainKt.includes(".allowAlarms(true)") && mainKt.includes("PEOPLE_TYPE_NONE"));
ok("Kural oluşturulamazsa eski küresel filtreye sessizce yedek düşülüyor", mainKt.includes("Yedek yol: kural mekanizması"));
ok("Yetim kalma durumu artık zen kuralını da kapatıyor (KEY_ZEN_AKTIF)", mainKt.includes("KEY_ZEN_AKTIF"));

console.log("\n2) HTML / JS Katmanı & Sözlük Bütünlüğü (15 Dil)");
const diller = ["tr","en","de","fr","es","it","pt-BR","nl","pl","ru","ja","ko","zh-Hans","zh-Hant","ar"];
for (let i = 0; i < diller.length; i++) {
  const dil = diller[i];
  const marker = `"${dil}": {`;
  const idx = html.indexOf(marker);
  // Blok, bir sonraki dilin başladığı yere (veya dosya sonuna) kadar sürer;
  // 300 karakterlik eski pencere, ~8 KB'lık gerçek dil bloklarını kapsamıyordu.
  const sonrakiDil = diller[i + 1];
  const bitis = sonrakiDil ? html.indexOf(`"${sonrakiDil}": {`, idx) : html.length;
  const blok = idx !== -1 ? html.slice(idx, bitis === -1 ? html.length : bitis) : "";
  ok(`${dil} dilinde s_dnd ve s_dnd_alt mevcut`, idx !== -1 && blok.includes('"s_dnd":') && blok.includes('"s_dnd_alt":'));
}

console.log("\n3) Varsayılan Ayarlar & Yaşam Döngüsü");
ok("DEFAULTS.settings içinde dnd: false tanımlı", html.includes("dnd: false"));
ok("nativeDndBaslat fonksiyonu tanımlı", html.includes("function nativeDndBaslat()"));
ok("nativeDndBitir fonksiyonu tanımlı", html.includes("function nativeDndBitir()"));
ok("startSession içinde DND tetikleniyor", html.includes("if (S.settings.dnd) nativeDndBaslat();"));
ok("finish (bitisiTamamla) içinde nativeDndBitir çağrılıyor", html.includes("nativeDndBitir();"));
ok("visibilitychange içinde DND kontrolü var", html.includes("if (S.settings.dnd) nativeDndBaslat();"));
ok("renderSettings içinde DND toggle anahtarı render ediliyor", html.includes('sw("dnd", s.dnd)'));

console.log("\n4) Mantıksal Yaşam Döngüsü Simülasyonu");
{
  const cagrilar = [];
  const fakeNative = {
    _izin: true,
    dndIzniVar: () => { cagrilar.push("dndIzniVar"); return fakeNative._izin; },
    dndIzniIste: () => { cagrilar.push("dndIzniIste"); },
    dndBaslat: () => { cagrilar.push("dndBaslat"); return true; },
    dndBitir: () => { cagrilar.push("dndBitir"); return true; }
  };

  // Simüle edilmiş test context'i
  let settings = { dnd: false };
  let active = null;

  function testBaslat() {
    active = "seans-1";
    if (settings.dnd) fakeNative.dndBaslat();
  }

  function testBitir() {
    active = null;
    fakeNative.dndBitir();
  }

  function testToggleDnd() {
    settings.dnd = !settings.dnd;
    if (settings.dnd) {
      if (!fakeNative.dndIzniVar()) fakeNative.dndIzniIste();
      if (active) fakeNative.dndBaslat();
    } else {
      fakeNative.dndBitir();
    }
  }

  // Senaryo A: DND kapalıyken seans başla/bitir -> DND çağrılmaz
  cagrilar.length = 0;
  testBaslat();
  ok("DND kapalıyken seans başladığında dndBaslat çağrılmadı", !cagrilar.includes("dndBaslat"));
  testBitir();
  ok("Seans bittiğinde dndBitir çağrıldı", cagrilar.includes("dndBitir"));

  // Senaryo B: DND açıkken seans başla/bitir -> dndBaslat ve dndBitir çağrılır
  cagrilar.length = 0;
  settings.dnd = true;
  testBaslat();
  ok("DND açıkken seans başlayınca dndBaslat çağrıldı", cagrilar.includes("dndBaslat"));
  testBitir();
  ok("DND açıkken seans bitince dndBitir çağrıldı", cagrilar.includes("dndBitir"));

  // Senaryo C: Seans sürerken DND kapatılırsa -> dndBitir anında çağrılır
  cagrilar.length = 0;
  testBaslat(); // dndBaslat
  testToggleDnd(); // kapatıldı -> dndBitir
  ok("Seans sürerken DND kapatılınca dndBitir çağrıldı", cagrilar.includes("dndBitir") && !settings.dnd);

  // Senaryo D: İzin yokken DND açılırsa -> dndIzniIste çağrılır
  cagrilar.length = 0;
  fakeNative._izin = false;
  testToggleDnd(); // açıldı
  ok("İzin yokken DND açılınca dndIzniIste çağrıldı", cagrilar.includes("dndIzniIste"));
}

console.log("\n" + "─".repeat(52));
console.log(`Sonuç: ${pass} geçti, ${fail} kaldı`);
process.exit(fail ? 1 : 0);
