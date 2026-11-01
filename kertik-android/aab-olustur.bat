@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul

cd /d "%~dp0"

echo ========================================================
echo      KERTIK - PLAY STORE ICIN AAB DERLEME ARACI
echo ========================================================
echo.

set "JAVA_HOME=C:\Users\yusuf_eqta17n\.jdks\jbr-21.0.11"
set "PATH=%JAVA_HOME%\bin;%PATH%"
set "ANDROID_HOME=C:\Users\yusuf_eqta17n\AppData\Local\Android\Sdk"

echo [1/3] Surum ve surum notu ayarlaniyor...
call node surum-yonetimi.js
if errorlevel 1 (
    echo.
    echo [HATA] Surum ayarlanamadi.
    pause
    exit /b 1
)

echo.
echo [2/3] Android AAB paketi derleniyor (bundleRelease)...
echo.

call gradlew.bat bundleRelease

if errorlevel 1 (
    echo.
    echo ========================================================
    echo  [HATA] Derleme basarisiz oldu! Yukaridaki hatayi okuyun.
    echo ========================================================
    echo.
    pause
    exit /b 1
)

echo.
echo [3/3] Paket ve surum notu hazirlaniyor...
copy /y "app\build\outputs\bundle\release\app-release.aab" "Kertik-Store.aab" >nul

echo.
echo ========================================================
echo  [BASARILI] Kertik Play Store paketi hazir!
echo.
echo  1. Dosya:       Kertik-Store.aab (proje kokunde)
echo  2. Surum notu:  surum-notu.txt (ve PANOYA KOPYALANDI)
echo                  Play Console'da Ctrl+V ile yapistirin.
echo ========================================================
echo.

start "" explorer.exe /select,"Kertik-Store.aab"

pause
