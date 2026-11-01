@echo off
setlocal
set "H=%~dp0kt"
set "K=%~dp0kertik-android\app\src\main\java\com\yusufgunay\kertik"
if not exist "%H%" (echo kt klasoru yok. Once kt-oku.bat calistir. & pause & exit /b 1)
for %%f in ("%H%\*.txt") do copy /y "%%f" "%K%\%%~nf.kt" >nul
dir /b "%K%"
echo.
echo Tamam. kt klasorundeki dosyalar kaynak agacina geri yazildi.
pause
