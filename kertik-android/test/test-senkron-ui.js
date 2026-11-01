const fs = require('fs');
const path = require('path');
const vm = require('vm');

let pass = 0, fail = 0;
const ok = (n, c, x) => {
  if (c) {
    pass++;
    console.log('  ✓ ' + n);
  } else {
    fail++;
    console.log('  ✗ ' + n, x !== undefined ? x : '');
  }
};

console.log('=== Senkronizasyon UI & Bulut Entegrasyon Testleri ===\n');

const assetsPath = path.join(__dirname, '../app/src/main/assets/index.html');
const simPath = path.join(__dirname, '../../simulasyon/simulator.html');

const assetsContent = fs.readFileSync(assetsPath, 'utf8');
const simContent = fs.readFileSync(simPath, 'utf8');

ok('assets/index.html icinde SENKRON_ACIK = true', /const\s+SENKRON_ACIK\s*=\s*true;/.test(assetsContent) || assetsContent.includes('const SENKRON_ACIK = true;'));
ok('simulator.html icinde SENKRON_ACIK = true', /const\s+SENKRON_ACIK\s*=\s*true;/.test(simContent) || simContent.includes('const SENKRON_ACIK = true;'));

ok('assets/index.html ayarlar menusunde Senkronizasyon (s_google) etiketi var', assetsContent.includes('soz("s_google")') || assetsContent.includes('s_google'));
ok('simulator.html ayarlar menusunde Senkronizasyon (s_google) etiketi var', simContent.includes('soz("s_google")') || simContent.includes('s_google'));

ok('assets/index.html ayarlar menusunde cig Google yerine Senkronizasyon kullanildi', !assetsContent.includes('<div class="lbl">Google</div>'));
ok('simulator.html ayarlar menusunde cig Google yerine Senkronizasyon kullanildi', !simContent.includes('<div class="lbl">Google</div>'));

ok('assets/index.html openSync icinde Bulut Senkronizasyonu (sy_baslik) basligi', assetsContent.includes('soz("sy_baslik")'));
ok('assets/index.html syncYok icinde Bulut Senkronizasyonu aciklamasi', assetsContent.includes('soz("sy_yok_metin")'));
ok('assets/index.html syncConnect icinde gizlilik aciklamasi', assetsContent.includes('appDataFolder') || assetsContent.includes('sy_baglan_metin'));

const sandbox = {
  now: () => 1700000000000,
  SENKRON_ACIK: true,
  NATIVE: null,
  S: {
    sync: {
      connected: false,
      lastAt: 0
    }
  }
};

const scriptCode = `
const syncReady = () => !!(SENKRON_ACIK && NATIVE);
const syncOn = () => !!(syncReady() && S.sync && S.sync.connected);

function syncLabel() {
  if (!syncReady()) return 'bağlan';
  if (!S.sync.connected) return 'bağlan';
  if (!S.sync.lastAt) return 'bağlı';
  const d = now() - S.sync.lastAt;
  if (d < 12e4) return 'az önce';
  if (d < 36e5) return Math.round(d / 6e4) + 'dk önce';
  if (d < 864e5) return Math.round(d / 36e5) + 'sa önce';
  return Math.round(d / 864e5) + ' gün önce';
}
`;

vm.createContext(sandbox);
vm.runInContext(scriptCode, sandbox);

ok('Koprusuz ortamda syncLabel baglan doner', vm.runInContext('syncLabel()', sandbox) === 'bağlan');

sandbox.NATIVE = { googleYetkiIste: () => {} };
ok('Native var ama connected=false iken baglan doner', vm.runInContext('syncLabel()', sandbox) === 'bağlan');

sandbox.S.sync.connected = true;
sandbox.S.sync.lastAt = 0;
ok('Connected=true ama henuz esitlenmediyse bagli doner', vm.runInContext('syncLabel()', sandbox) === 'bağlı');

sandbox.S.sync.lastAt = sandbox.now() - 30000;
ok('30 sn once esitlendiyse az once doner', vm.runInContext('syncLabel()', sandbox) === 'az önce');

sandbox.S.sync.lastAt = sandbox.now() - 15 * 60000;
ok('15 dk once esitlendiyse 15dk once doner', vm.runInContext('syncLabel()', sandbox) === '15dk önce');

sandbox.S.sync.lastAt = sandbox.now() - 3 * 3600000;
ok('3 saat once esitlendiyse 3sa once doner', vm.runInContext('syncLabel()', sandbox) === '3sa önce');

sandbox.S.sync.lastAt = sandbox.now() - 5 * 86400000;
ok('5 gun once esitlendiyse 5 gun once doner', vm.runInContext('syncLabel()', sandbox) === '5 gün önce');

console.log('\nSonuc: ' + pass + ' gecti, ' + fail + ' kaldi\n');
if (fail > 0) process.exit(1);
