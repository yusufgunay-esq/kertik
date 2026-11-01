@echo off
setlocal
set "K=%~dp0kertik-android\app\src\main\java\com\yusufgunay\kertik"
set "H=%~dp0kt"
if not exist "%H%" mkdir "%H%"
for %%f in ("%K%\*.kt") do copy /y "%%f" "%H%\%%~nf.txt" >nul
dir /b "%H%"
echo.
echo Tamam. Proje kokunde kt klasoru olustu, Claude artik okuyabilir.
pause
