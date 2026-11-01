/* StandBy Zen, Canlı Kapsül & Ana Ekran Widget'ları Entegrasyon Testi
   - Manifest receiver kayıtları (KertikEylemAlici, KontrolWidget, DuvarWidget)
   - KertikEylemAlici BroadcastReceiver ve Bildirim.kt getBroadcast mimarisi
   - StandBy Zen Masaüstü Odak Ekranı DOM, CSS ve Durum Yönetimi
*/
const fs = require("fs");
const path = require("path");
const { JSDOM, VirtualConsole } = require("jsdom");

const manifestPath = path.join(__dirname, "../app/src/main/AndroidManifest.xml");
const bildirimKtPath = path.join(__dirname, "../app/src/main/java/com/yusufgunay/kertik/Bildirim.kt");
const mainKtPath = path.join(__dirname, "../app/src/main/java/com/yusufgunay/kertik/MainActivity.kt");
const aliciKtPath = path.join(__dirname, "../app/src/main/java/com/yusufgunay/kertik/KertikEylemAlici.kt");
const assetHtmlPath = path.join(__dirname, "../app/src/main/assets/index.html");

const manifest = fs.readFileSync(manifestPath, "utf8");
const bildirimKt = fs.readFileSync(bildirimKtPath, "utf8");
const mainKt = fs.readFileSync(mainKtPath, "utf8");
const aliciKt = fs.existsSync(aliciKtPath) ? fs.readFileSync(aliciKtPath, "utf8") : "";
const html = fs.readFileSync(assetHtmlPath, "utf8");

let pass = 0, fail = 0;
function ok(name, cond, extra) {
  if (cond) { pass++; console.log("  ✓ " + name); }
  else { fail++; console.log("  ✗ " + name, extra ?? ""); }
}

console.log("\n=== StandBy Zen, Canlı Kapsül & Widget Doğrulama Testleri ===");

console.log("\n1) AndroidManifest.xml Receiver ve Widget Kayıtları");
ok("KontrolWidget receiver kaydı mevcut", manifest.includes('android:name=".KontrolWidget"'));
ok("DuvarWidget receiver kaydı mevcut", manifest.includes('android:name=".DuvarWidget"'));
ok("APPWIDGET_UPDATE intent-filter mevcut", manifest.includes("android.appwidget.action.APPWIDGET_UPDATE"));
ok("KertikEylemAlici receiver eklendi", manifest.includes('android:name=".KertikEylemAlici"'));
ok("com.yusufgunay.kertik.EYLEM intent-filter mevcut", manifest.includes("com.yusufgunay.kertik.EYLEM"));

console.log("\n2) Sessiz Canlı Bildirim & Broadcast Mimarisi");
ok("KertikEylemAlici.kt dosyası mevcut", aliciKt.length > 0);
ok("KertikEylemAlici aktiviteye eylem yönlendiriyor", aliciKt.includes("aktivite.eylemGonder(eylem)"));
ok("MainActivity eylemGonder içinde window.kertikNativeEylem çağrısı var", mainKt.includes("window.kertikNativeEylem"));
ok("Bildirim.kt buton aksiyonları için getBroadcast kullanıyor", bildirimKt.includes("PendingIntent.getBroadcast"));
ok("Bildirim.kt bildirim gövdesine dokunma için getActivity kullanıyor", bildirimKt.includes("PendingIntent.getActivity"));
ok("MainActivity companion object içinde aktifOrnek tutuluyor", mainKt.includes("var aktifOrnek: MainActivity? = null"));
ok("MainActivity EXTRA_SESSIZ durumunda moveTaskToBack çalıştırıyor", mainKt.includes("moveTaskToBack(true)"));

console.log("\n3) StandBy Zen DOM ve CSS Varlığı");
ok("#standbyZen katmanı HTML'de mevcut", html.includes('id="standbyZen"'));
ok("#btnStandby butonu HTML'de mevcut", html.includes('id="btnStandby"'));
ok("#sbClock tabular saat elemanı mevcut", html.includes('id="sbClock"'));
ok("#sbStatus durum etiketi mevcut", html.includes('id="sbStatus"'));
ok("#sbSub alt bilgi elemanı mevcut", html.includes('id="sbSub"'));
ok("#sbTask görev adı elemanı mevcut", html.includes('id="sbTask"'));
ok(".standby-layer CSS sınıfı tanımlı", html.includes(".standby-layer"));
ok("html.standby-active CSS kuralı tanımlı", html.includes("html.standby-active"));
ok("SOZLUK tr içinde sb_cikis tanımlı", html.includes('"sb_cikis":"çıkmak için dokun"'));
ok("SOZLUK en içinde sb_cikis tanımlı", html.includes('"sb_cikis":"tap anywhere to exit"'));

console.log("\n4) JSDOM Davranış & Yaşam Döngüsü Simülasyonu");
{
  const vc = new VirtualConsole();
  const dom = new JSDOM(html, {
    runScripts: "dangerously",
    pretendToBeVisual: true,
    virtualConsole: vc,
    url: "http://localhost/",
    beforeParse(w) {
      if (!w.structuredClone) w.structuredClone = o => JSON.parse(JSON.stringify(o));
      w.HTMLCanvasElement.prototype.getContext = () => ({
        canvas: {}, globalAlpha: 1, globalCompositeOperation: "source-over",
        beginPath(){}, moveTo(){}, lineTo(){}, stroke(){}, fill(){}, fillRect(){}, clearRect(){},
        setTransform(){}, drawImage(){}, putImageData(){}, closePath(){}, arc(){}, save(){}, restore(){},
        createImageData: (w, h) => ({ width: w, height: h, data: new Uint8ClampedArray(w * h * 4) }),
        createRadialGradient: () => ({ addColorStop(){} }),
        createLinearGradient: () => ({ addColorStop(){} })
      });
      w.HTMLCanvasElement.prototype.toDataURL = () => "data:image/png;base64,";
      w.KertikNative = {
        goster(){}, gizle(){}, bildirimIzniVar: () => true, bildirimIzniIste(){},
        ekraniAcikTut(){}, titret(){}, surum: () => "test", widgetDurum(){}
      };
    }
  });

  const w = dom.window;
  ok("toggleStandby fonksiyonu pencerede tanımlı", typeof w.toggleStandby === "function");
  ok("guncelleStandby fonksiyonu pencerede tanımlı", typeof w.guncelleStandby === "function");

  // StandBy aç
  w.toggleStandby(true);
  ok("toggleStandby(true) sonrası html üzerinde standby-active sınıfı var",
     w.document.documentElement.classList.contains("standby-active"));

  // StandBy açıkken saat güncellemesi
  w.guncelleStandby();
  const sbClock = w.document.getElementById("sbClock");
  ok("sbClock içeriği 00:00 olarak güncellendi", sbClock && sbClock.textContent === "00:00");

  // Seans başlatıldığında StandBy saati
  w.kertikNativeEylem("start");
  w.guncelleStandby();
  ok("Seans başladıktan sonra sbClock zaman gösteriyor", sbClock && sbClock.textContent.includes(":"));

  // StandBy kapat
  w.toggleStandby(false);
  ok("toggleStandby(false) sonrası standby-active sınıfı kalktı",
     !w.document.documentElement.classList.contains("standby-active"));

  w.close();
}

console.log(`\nSonuç: ${pass} geçti, ${fail} kaldı.`);
process.exit(fail === 0 ? 0 : 1);
