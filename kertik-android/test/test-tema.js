// أَعُوذُ بِاللَّهِ مِنَ الشَّيْطَانِ الرَّجِيمِ
// بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ
// رَبِّ يَسِّرْ وَلَا تُعَسِّرْ رَبِّ تَمِّمْ بِالْخَيْرِ

/**
 * Otomatik / Sistem Teması (System/Light/Dark) Birim ve Entegrasyon Testleri
 */

const fs = require('fs');
const path = require('path');
const vm = require('vm');

let pass = 0, fail = 0;
function ok(ad, kosul) {
  if (kosul) { console.log('  ✓ ' + ad); pass++; }
  else { console.error('  ✗ ' + ad); fail++; }
}

function ortamKur(baslangicDark = false, storageGirdi = null) {
  let mediaMatches = baslangicDark;
  const mediaListeners = [];

  const classList = new Set();
  const metaAttrs = { 'name': 'theme-color', 'content': '#F5F2EA' };

  const storage = {};
  if (storageGirdi) {
    storage['kertik.v1'] = JSON.stringify(storageGirdi);
  }

  const mockDoc = {
    /* sakinHudSifirla() açılışta document.body'ye dokunuyor */
    body: {
      style: {},
      classList: { add: () => {}, remove: () => {}, toggle: () => {}, contains: () => false }
    },
    documentElement: {
      classList: {
        add: (c) => classList.add(c),
        remove: (c) => classList.delete(c),
        toggle: (c, force) => {
          if (force === undefined) {
            if (classList.has(c)) { classList.delete(c); return false; }
            else { classList.add(c); return true; }
          }
          if (force) classList.add(c); else classList.delete(c);
          return !!force;
        },
        contains: (c) => classList.has(c)
      }
    },
    querySelector: (sel) => {
      if (sel === 'meta[name="theme-color"]') {
        return {
          setAttribute: (name, val) => { metaAttrs[name] = val; },
          getAttribute: (name) => metaAttrs[name]
        };
      }
      return {
        offsetLeft: 0, offsetWidth: 100, style: {},
        setAttribute: () => {}, getAttribute: () => null,
        /* akisBosluk() kadranın yerini ölçer; sahte elemanda ölçü yok → genişlik 0 */
        getBoundingClientRect: () => ({ left: 0, top: 0, width: 0, height: 0 }),
        classList: { add: () => {}, remove: () => {}, toggle: () => {}, contains: () => false },
        querySelectorAll: () => []
      };
    },
    querySelectorAll: () => [],
    getElementById: (id) => {
      return {
        id,
        innerHTML: '',
        textContent: '',
        offsetLeft: 0, offsetWidth: 100,
        classList: { add: () => {}, remove: () => {}, toggle: () => {}, contains: () => false },
        style: {},
        onclick: null,
        appendChild: () => {},
        removeChild: () => {},
        addEventListener: () => {},
        querySelectorAll: () => [],
        querySelector: (s) => ({
          offsetLeft: 0, offsetWidth: 100, style: {},
          setAttribute: () => {}, getAttribute: () => null,
          appendChild: () => {}, removeChild: () => {},
          classList: { add: () => {}, remove: () => {}, toggle: () => {}, contains: () => false }
        })
      };
    },
    createElement: () => ({ setAttribute: () => {}, appendChild: () => {}, style: {}, classList: { add: () => {}, remove: () => {}, toggle: () => {}, contains: () => false } }),
    createElementNS: () => ({ setAttribute: () => {}, appendChild: () => {}, style: {}, classList: { add: () => {}, remove: () => {}, toggle: () => {}, contains: () => false } }),
    addEventListener: () => {}
  };

  const mockWindow = {
    matchMedia: (query) => {
      return {
        media: query,
        get matches() { return mediaMatches; },
        addEventListener: (event, handler) => {
          if (event === 'change') mediaListeners.push(handler);
        },
        addListener: (handler) => {
          mediaListeners.push(handler);
        }
      };
    },
    addEventListener: () => {},
    localStorage: {
      getItem: (k) => storage[k] || null,
      setItem: (k, v) => { storage[k] = String(v); },
      removeItem: (k) => { delete storage[k]; }
    },
    navigator: { vibrate: () => {} },
    getComputedStyle: () => ({ getPropertyValue: () => '#000' }),
    setTimeout: (fn) => fn,
    setInterval: () => 1,
    clearTimeout: () => {},
    clearInterval: () => {}
  };

  const context = vm.createContext({
    window: mockWindow,
    document: mockDoc,
    localStorage: mockWindow.localStorage,
    navigator: mockWindow.navigator,
    getComputedStyle: mockWindow.getComputedStyle,
    setTimeout: mockWindow.setTimeout,
    setInterval: mockWindow.setInterval,
    clearTimeout: mockWindow.clearTimeout,
    clearInterval: mockWindow.clearInterval,
    structuredClone: (obj) => JSON.parse(JSON.stringify(obj)),
    console: console,
    SENKRON_ACIK: false
  });

  return {
    context,
    doc: mockDoc,
    metaAttrs,
    classList,
    setSystemDark: (isDark) => {
      mediaMatches = isDark;
      for (const fn of mediaListeners) fn({ matches: isDark });
    }
  };
}

console.log('\n1) Varsayilan Ayar & isDarkTheme Fonksiyonu');
{
  const { context, doc, setSystemDark } = ortamKur(false);
  const html = fs.readFileSync(path.join(__dirname, '../app/src/main/assets/index.html'), 'utf-8');
  const jsMatch = html.match(/<script>([\s\S]*?)<\/script>/);
  if (!jsMatch) throw new Error('index.html script bulunamadi');
  
  vm.runInContext(jsMatch[1], context);
  
  const DEFAULTS = vm.runInContext("DEFAULTS", context);
  const S = vm.runInContext("S", context);
  
  ok('DEFAULTS.settings.theme system olarak ayarli', DEFAULTS.settings.theme === 'system');
  ok('Yeni yuklemede S.settings.theme system', S.settings.theme === 'system');
  
  setSystemDark(false);
  ok('Sistem acikken isDarkTheme() false', vm.runInContext("isDarkTheme()", context) === false);
  
  setSystemDark(true);
  ok('Sistem karanlikken isDarkTheme() true', vm.runInContext("isDarkTheme()", context) === true);
  
  vm.runInContext('S.settings.theme = "light"', context);
  ok('Sabit light iken sistem karanlik olsa da isDarkTheme() false', vm.runInContext("isDarkTheme()", context) === false);
  
  setSystemDark(false);
  vm.runInContext('S.settings.theme = "dark"', context);
  ok('Sabit dark iken sistem acik olsa da isDarkTheme() true', vm.runInContext("isDarkTheme()", context) === true);
}

console.log('\n2) applyTheme() ve Meta Theme Color');
{
  const { context, doc, metaAttrs } = ortamKur(false);
  const html = fs.readFileSync(path.join(__dirname, '../app/src/main/assets/index.html'), 'utf-8');
  const jsMatch = html.match(/<script>([\s\S]*?)<\/script>/);
  vm.runInContext(jsMatch[1], context);
  
  vm.runInContext('S.settings.theme = "dark"; applyTheme();', context);
  ok('Koyu temada .dark sinifi eklendi', doc.documentElement.classList.contains('dark'));
  ok('Koyu temada theme-color #111317', metaAttrs['content'] === '#111317');
  
  vm.runInContext('S.settings.theme = "light"; applyTheme();', context);
  ok('Acik temada .dark sinifi kaldirildi', !doc.documentElement.classList.contains('dark'));
  ok('Acik temada theme-color #F4F2EE', metaAttrs['content'] === '#F4F2EE');
}

console.log('\n3) Dinamik OS Tema Degisikligi (Canli matchMedia Event)');
{
  const { context, doc, metaAttrs, setSystemDark } = ortamKur(false);
  const html = fs.readFileSync(path.join(__dirname, '../app/src/main/assets/index.html'), 'utf-8');
  const jsMatch = html.match(/<script>([\s\S]*?)<\/script>/);
  vm.runInContext(jsMatch[1], context);
  
  vm.runInContext('S.settings.theme = "system"; applyTheme();', context);
  
  ok('Baslangicta acik sistem -> .dark yok', !doc.documentElement.classList.contains('dark'));
  
  setSystemDark(true);
  ok('OS gece moduna gecince .dark otomatik eklendi', doc.documentElement.classList.contains('dark'));
  ok('OS gece moduna gecince meta renk #111317 oldu', metaAttrs['content'] === '#111317');
  
  setSystemDark(false);
  ok('OS sabah moduna donunce .dark otomatik kalkti', !doc.documentElement.classList.contains('dark'));
  ok('OS sabah moduna donunce meta renk #F4F2EE oldu', metaAttrs['content'] === '#F4F2EE');
  
  vm.runInContext('S.settings.theme = "dark"; applyTheme();', context);
  setSystemDark(false);
  ok('Manuel dark seciliyken OS acik olsa bile koyu kalir', doc.documentElement.classList.contains('dark'));
}

console.log('\n4) Ayarlar Ekrani (renderSettings) Segment Butonlari');
{
  const { context, doc } = ortamKur(false);
  const html = fs.readFileSync(path.join(__dirname, '../app/src/main/assets/index.html'), 'utf-8');
  const jsMatch = html.match(/<script>([\s\S]*?)<\/script>/);
  vm.runInContext(jsMatch[1], context);
  
  let setHtml = '';
  const setBox = {
    set innerHTML(val) { setHtml = val; },
    get innerHTML() { return setHtml; },
    querySelectorAll: () => [],
    querySelector: () => ({ onclick: null })
  };
  
  doc.getElementById = (id) => {
    if (id === 'setBody') return setBox;
    if (id === 'setSub') return { textContent: '' };
    return { classList: { add: () => {}, remove: () => {} }, onclick: null };
  };
  
  vm.runInContext('renderSettings()', context);
  
  ok('Ayarlar ekraninda tema segmenti render edildi', setHtml.includes('data-set="theme"'));
  ok('Uclu segmentte system butonu var', setHtml.includes('data-set="theme" data-v="system"'));
  ok('Uclu segmentte light butonu var', setHtml.includes('data-set="theme" data-v="light"'));
  ok('Uclu segmentte dark butonu var', setHtml.includes('data-set="theme" data-v="dark"'));
}

console.log('\n5) Geriye Donuk Uyumluluk (Legacy Storage Migration)');
{
  const { context: ctxDark } = ortamKur(false, { settings: { theme: 'dark' } });
  const html = fs.readFileSync(path.join(__dirname, '../app/src/main/assets/index.html'), 'utf-8');
  const jsMatch = html.match(/<script>([\s\S]*?)<\/script>/);
  vm.runInContext(jsMatch[1], ctxDark);
  ok('Eski dark kaydi aynen korundu', vm.runInContext('S.settings.theme', ctxDark) === 'dark');
  ok('Eski dark kaydi karanlik render edildi', vm.runInContext('isDarkTheme()', ctxDark) === true);

  const { context: ctxLight } = ortamKur(true, { settings: { theme: 'light' } });
  vm.runInContext(jsMatch[1], ctxLight);
  ok('Eski light kaydi aynen korundu', vm.runInContext('S.settings.theme', ctxLight) === 'light');
  ok('Eski light kaydi sistem karanlik olsa bile acik render edildi', vm.runInContext('isDarkTheme()', ctxLight) === false);

  const { context: ctxNone } = ortamKur(true, { settings: { mode: 'stopwatch' } });
  vm.runInContext(jsMatch[1], ctxNone);
  ok('Tema alani eksik olan eski veri varsayilan olarak sisteme baglandi', vm.runInContext('isDarkTheme()', ctxNone) === true);
}

console.log('\n6) Android Native Kopru & onConfigurationChanged Hook');
{
  const kt = fs.readFileSync(path.join(__dirname, '../app/src/main/java/com/yusufgunay/kertik/MainActivity.kt'), 'utf-8');
  ok('MainActivity.kt icinde onConfigurationChanged tanimli', kt.includes('override fun onConfigurationChanged'));
  ok('MainActivity.kt icinde sistemKoyuMu JavascriptInterface tanimli', kt.includes('fun sistemKoyuMu(): Boolean'));
  ok('MainActivity.kt icinde temaDegisti JavascriptInterface tanimli', kt.includes('fun temaDegisti(koyu: Boolean)'));
  ok('MainActivity.kt icinde statusBarColor ve navigationBarColor guncelleniyor', kt.includes('window.statusBarColor = renk'));

  let nativeDarkState = true;
  let nativeThemeReported = null;
  const mockNative = {
    sistemKoyuMu: () => nativeDarkState,
    temaDegisti: (k) => { nativeThemeReported = k; }
  };

  const { context, doc } = ortamKur(false);
  context.window.KertikNative = mockNative;
  const html = fs.readFileSync(path.join(__dirname, '../app/src/main/assets/index.html'), 'utf-8');
  const jsMatch = html.match(/<script>([\s\S]*?)<\/script>/);
  vm.runInContext(jsMatch[1], context);

  ok('KertikNative.sistemKoyuMu() true iken isDarkTheme() true', vm.runInContext('isDarkTheme()', context) === true);
  ok('applyTheme cagrildiginda KertikNative.temaDegisti true iletildi', nativeThemeReported === true);

  nativeDarkState = false;
  ok('KertikNative.sistemKoyuMu() false iken isDarkTheme() false', vm.runInContext('isDarkTheme()', context) === false);
  vm.runInContext('applyTheme()', context);
  ok('applyTheme cagrildiginda KertikNative.temaDegisti false iletildi', nativeThemeReported === false);

  ok('window.sistemTemaDegisti fonksiyonu tanimli', typeof vm.runInContext('window.sistemTemaDegisti', context) === 'function');
  nativeDarkState = true;
  vm.runInContext('window.sistemTemaDegisti(true)', context);
  ok('window.sistemTemaDegisti cagrisi sonrasi .dark sinifi eklendi', doc.documentElement.classList.contains('dark'));
}

console.log(`\nToplam: ${pass} geçti, ${fail} kaldı\n`);
if (fail > 0) process.exit(1);

