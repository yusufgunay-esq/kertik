/* SİMÜLATÖR CANLI İZLEYİCİ (WATCHER)
   kertik-android/app/src/main/assets/index.html dosyasındaki değişiklikleri izler,
   kaydedildiği anda simulasyon/simulator.html dosyasını anında yeniden derler.
*/
const fs = require("fs");
const path = require("path");
const { spawnSync } = require("child_process");

const KOK = path.join(__dirname, "..");
const KAYNAK = path.join(KOK, "kertik-android/app/src/main/assets/index.html");
const BUILDER = path.join(__dirname, "olustur-simulator.js");

function derle() {
  const t0 = Date.now();
  const r = spawnSync("node", [BUILDER], { stdio: "inherit", cwd: KOK });
  if (r.status === 0) {
    console.log("[" + new Date().toLocaleTimeString("tr-TR") + "] ✓ Simülatör güncellendi (" + (Date.now() - t0) + " ms)");
  } else {
    console.error("[" + new Date().toLocaleTimeString("tr-TR") + "] ✗ Simülatör güncellenirken hata oluştu");
  }
}

console.log("==================================================");
console.log(" Kertik Simülatör Canlı İzleyici Başlatıldı ");
console.log(" İzlenen: kertik-android/app/src/main/assets/index.html");
console.log(" Çıkış için: Ctrl+C");
console.log("==================================================");

derle();

let debounceTimer = null;
fs.watch(KAYNAK, (eventType) => {
  if (debounceTimer) clearTimeout(debounceTimer);
  debounceTimer = setTimeout(() => {
    console.log("\n[" + new Date().toLocaleTimeString("tr-TR") + "] index.html değişti, simülatör derleniyor...");
    derle();
  }, 100);
});
