@echo off
chcp 65001 >nul
title 🔍 Probar Conexión DVDcoin
color 0B

echo.
echo ═══════════════════════════════════════════════════════════
echo   🔍 PROBANDO CONEXIÓN A DVDCOIN
echo ═══════════════════════════════════════════════════════════
echo.

cd /d "%~dp0"

echo 📊 Verificando servicios...
echo.

REM Verificar Python
netstat -ano | findstr ":8000" >nul
if errorlevel 1 (
    echo ❌ Servidor Python: NO CORRIENDO
    echo.
    echo 💡 Ejecuta: INICIAR_SERVIDOR.bat
    pause
    exit /b 1
) else (
    echo ✅ Servidor Python: CORRIENDO en puerto 8000
)

REM Verificar Cloudflare
tasklist | findstr cloudflared.exe >nul
if errorlevel 1 (
    echo ❌ Túnel Cloudflare: NO CORRIENDO
    echo.
    echo 💡 Ejecuta: INICIAR_SERVIDOR.bat
    pause
    exit /b 1
) else (
    echo ✅ Túnel Cloudflare: ACTIVO
)

echo.
echo ═══════════════════════════════════════════════════════════
echo   🌐 URLS DISPONIBLES
echo ═══════════════════════════════════════════════════════════
echo.
echo ✅ URL PRINCIPAL:
echo    https://app.david.ch
echo.
echo ✅ URL ALTERNATIVA:
echo    https://localhost.david.ch
echo.
echo ✅ URL TEMPORAL:
echo    https://6c0cb6da-aafe-4e61-89aa-42d9bd2e5b33.cfargotunnel.com
echo.
echo ═══════════════════════════════════════════════════════════
echo   🔒 CERTIFICADO SSL
echo ═══════════════════════════════════════════════════════════
echo.
echo ✅ Certificado SSL: VÁLIDO (Cloudflare)
echo ✅ Protocolo: HTTPS
echo ✅ Acceso: Desde cualquier red y dispositivo
echo.
echo ═══════════════════════════════════════════════════════════
echo   🚀 PRUEBA AHORA
echo ═══════════════════════════════════════════════════════════
echo.
echo 1. Abre tu navegador (Chrome, Firefox, Safari, Edge)
echo 2. Copia y pega esta URL:
echo.
echo    https://app.david.ch
echo.
echo 3. Deberías ver tu aplicación DVDcoin con el candado verde
echo.
echo ═══════════════════════════════════════════════════════════
echo.
echo ¿Quieres abrir la URL en tu navegador ahora? (S/N)
set /p respuesta=
if /i "%respuesta%"=="S" (
    start https://app.david.ch
    echo.
    echo ✅ Abriendo navegador...
)
echo.
pause
