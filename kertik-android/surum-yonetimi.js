const fs = require('fs');
const path = require('path');
const readline = require('readline');
const { execSync } = require('child_process');

const gradlePath = path.join(__dirname, 'app', 'build.gradle.kts');
const noteFilePath = path.join(__dirname, 'surum-notu.txt');

if (!fs.existsSync(gradlePath)) {
  console.error('[HATA] build.gradle.kts bulunamadi:', gradlePath);
  process.exit(1);
}

let content = fs.readFileSync(gradlePath, 'utf8');

const codeMatch = content.match(/versionCode\s*=\s*(\d+)/);
const nameMatch = content.match(/versionName\s*=\s*"([^"]+)"/);

const currentCode = codeMatch ? parseInt(codeMatch[1], 10) : 1;
const currentName = nameMatch ? nameMatch[1] : '1.0.0';

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
});

const ask = (query) => new Promise((resolve) => rl.question(query, resolve));

async function main() {
  console.log('========================================================');
  console.log('       KERTIK - SURUM VE SURUM NOTU YONETIMI');
  console.log('========================================================\n');
  console.log(` Mevcut surum: v${currentName} (kod: ${currentCode})`);
  console.log(' (Google Play her yeni yayinda daha buyuk bir surum kodu ister)\n');

  const suggestedCode = currentCode + 1;
  const inputCode = await ask(` Yeni surum kodu [Enter = ${suggestedCode}]: `);
  const newCode = inputCode.trim() ? parseInt(inputCode.trim(), 10) : suggestedCode;

  const inputName = await ask(` Yeni surum adi (ornek: 1.1.0) [Enter = ${currentName}]: `);
  const newName = inputName.trim() ? inputName.trim() : currentName;

  console.log('\n --- SURUM NOTU (Play Console icin) ---');
  console.log(' Bu guncellemede ne yapildigini yazin.');
  console.log(' (Enter basarsaniz varsayilan profesyonel not kullanilir)');
  const inputNote = await ask(' Surum notu: ');
  rl.close();

  const noteText = inputNote.trim() || 'Performance improvements and bug fixes.';
  
  // Play Console formatinda surum notu
  const formattedReleaseNote = `<en-US>\n${noteText}\n</en-US>\n<tr-TR>\n${noteText}\n</tr-TR>`;

  // build.gradle.kts guncelle
  content = content.replace(/(versionCode\s*=\s*)\d+/, `$1${newCode}`);
  content = content.replace(/(versionName\s*=\s*)"[^"]+"/, `$1"${newName}"`);
  fs.writeFileSync(gradlePath, content, 'utf8');

  // surum-notu.txt kaydet
  fs.writeFileSync(noteFilePath, formattedReleaseNote, 'utf8');

  // Panoya kopyala (Windows clip)
  try {
    execSync('clip', { input: formattedReleaseNote });
    console.log('\n [OK] Surum notu panoya kopyalandi! (Play Console\'da Ctrl+V yapabilirsiniz)');
  } catch (e) {
    // ignore
  }

  console.log(` [OK] Surum ayarlandi: v${newName} (kod: ${newCode})`);
  console.log(` [OK] Surum notu kaydedildi: surum-notu.txt\n`);
  console.log('--------------------------------------------------------');
  console.log(formattedReleaseNote);
  console.log('--------------------------------------------------------\n');
}

main().catch((err) => {
  console.error('[HATA]', err);
  process.exit(1);
});
