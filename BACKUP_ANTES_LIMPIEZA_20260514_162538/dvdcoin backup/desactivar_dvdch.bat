@echo off
:: ============================================================
:: desactivar_dvdch.bat
:: Elimina la redirección dvd.ch → localhost:8000
:: Requiere ejecutar como Administrador
:: ============================================================

net session >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo  ERROR: Debes ejecutar como Administrador.
    echo.
    pause
    exit /b 1
)

echo.
echo  [1/4] Deteniendo proxy...
taskkill /f /fi "WINDOWTITLE eq DVDcoin-proxy" >nul 2>&1
taskkill /f /im python.exe /fi "WINDOWTITLE eq DVDcoin-proxy" >nul 2>&1
echo       Proxy detenido.

echo.
echo  [2/4] Eliminando entrada dvd.ch del archivo hosts...

set HOSTS=%SystemRoot%\System32\drivers\etc\hosts
set HOSTS_TMP=%TEMP%\hosts_backup.txt

:: Hacer copia de seguridad primero
copy "%HOSTS%" "%HOSTS_TMP%" >nul

:: Crear nuevo hosts sin la línea dvd.ch
type nul > "%HOSTS%.new"
for /f "delims=" %%L in (%HOSTS%) do (
    echo %%L | findstr /C:"dvd.ch" >nul 2>&1
    if errorlevel 1 echo %%L >> "%HOSTS%.new"
)

:: Reemplazar el hosts original
move /y "%HOSTS%.new" "%HOSTS%" >nul
echo       Entrada dvd.ch eliminada. Copia de seguridad en: %HOSTS_TMP%

echo.
echo  [3/4] Eliminando regla de firewall...
netsh advfirewall firewall delete rule name="DVDcoin proxy 80" >nul 2>&1
echo       Regla de firewall eliminada.

echo.
echo  [4/4] Vaciando caché DNS de Windows...
ipconfig /flushdns >nul
echo       Caché DNS vaciada.

echo.
echo  ============================================================
echo   OK  La redirección dvd.ch ha sido eliminada.
echo       dvd.ch volverá a apuntar a internet (o a nada).
echo  ============================================================
echo.
pause
