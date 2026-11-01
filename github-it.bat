@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion
cd /d "%~dp0"

echo ==========================================
echo   Kertik - GitHub'a ilk itis
echo   Klasor: %CD%
echo ==========================================
echo.

where git >nul 2>&1
if errorlevel 1 (
  echo [HATA] git bulunamadi. Git for Windows kurulu ama PATH'te degil olabilir.
  echo Cozum: Git Bash icinden bu dosyayi calistir, ya da Git'i yeniden kurarken
  echo "Git from the command line" secenegini isaretle.
  pause & exit /b 1
)

if not exist ".gitignore" (
  echo [HATA] .gitignore yok. Once onu yerine koy.
  pause & exit /b 1
)

if exist ".git" (
  echo [i] Depo zaten baslatilmis, atlaniyor.
) else (
  git init -b main
  if errorlevel 1 ( echo [HATA] git init basarisiz. & pause & exit /b 1 )
)

echo.
echo --- Dosyalar hazirlaniyor ---
git add -A
if errorlevel 1 ( echo [HATA] git add basarisiz. & pause & exit /b 1 )

echo.
echo --- GUVENLIK KONTROLU: sirlar depoya giriyor mu ---
set SIZINTI=0
for %%S in (gizli.properties local.properties imza.properties) do (
  git diff --cached --name-only | findstr /I /C:"%%S" >nul && (
    echo [SIZINTI] %%S eklenmis!
    set SIZINTI=1
  )
)
git diff --cached --name-only | findstr /I /R "\.p12$ \.jks$ \.keystore$ \.b64$" >nul && (
  echo [SIZINTI] Imza anahtari eklenmis!
  set SIZINTI=1
)
if "!SIZINTI!"=="1" (
  echo.
  echo [DURDURULDU] Sir dosyalari staging'de. Hicbir sey itilmedi.
  echo .gitignore'u duzeltip tekrar calistir.
  git reset >nul
  pause & exit /b 1
)
echo [OK] Sir dosyasi bulunamadi.

echo.
echo --- Eklenecek dosya sayisi ---
git diff --cached --name-only | find /c /v "" 
echo.

git rev-parse HEAD >nul 2>&1
if errorlevel 1 (
  git commit -m "Kertik 2.2: ilk surum" -m "Kaynak, testler, tasarim notlari ve simulator."
  if errorlevel 1 ( echo [HATA] commit basarisiz. Git kullanici adi/e-posta ayarli mi? & echo   git config --global user.name "Yusuf Gunay" & echo   git config --global user.email "yusufgunay@gmail.com" & pause & exit /b 1 )
) else (
  git commit -m "Guncelleme" || echo [i] Yeni degisiklik yok.
)

echo.
git remote get-url origin >nul 2>&1
if errorlevel 1 goto :UZAK_YOK
echo [i] Uzak sunucu zaten tanimli:
git remote get-url origin
goto :IT

:UZAK_YOK
echo --- Uzak sunucu tanimli degil ---
where gh >nul 2>&1
if errorlevel 1 goto :ELLE

echo [i] GitHub CLI bulundu. Private depo olusturulacak.
gh auth status >nul 2>&1
if errorlevel 1 (
  echo Once GitHub'a giris yapilacak, tarayici acilacak.
  gh auth login
  if errorlevel 1 ( echo [HATA] Giris basarisiz. & pause & exit /b 1 )
)
gh repo create kertik --private --source=. --remote=origin
if errorlevel 1 ( echo [HATA] Depo olusturulamadi. Ayni isimde depo olabilir. & goto :ELLE )
goto :IT

:ELLE
echo.
echo GitHub CLI yok ya da otomatik olusturma calismadi.
echo 1) https://github.com/new adresinden PRIVATE bir depo ac (adi: kertik).
echo    README, .gitignore, lisans EKLEME - bos birak.
echo 2) Adresini asagiya yapistir (ornek: https://github.com/yusufgunay/kertik.git)
echo.
set /p REPO_URL="Depo adresi: "
if "!REPO_URL!"=="" ( echo [IPTAL] Adres girilmedi. & pause & exit /b 1 )
git remote add origin !REPO_URL!

:IT
echo.
echo --- Itiliyor ---
git push -u origin main
if errorlevel 1 (
  echo.
  echo [HATA] Itis basarisiz. Sik sebepler:
  echo  - Kimlik dogrulama: kullanici adi + PAROLA degil, Personal Access Token gerekir.
  echo  - Depoda zaten commit var: once "git pull --rebase origin main" dene.
  pause & exit /b 1
)

echo.
echo ==========================================
echo   BITTI. Depo GitHub'da.
echo ==========================================
git remote get-url origin
echo.
pause
