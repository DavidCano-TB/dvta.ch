@echo off
chcp 65001 >nul
cls
echo.
echo ═══════════════════════════════════════════════════════════
echo   VERIFICACIÓN COMPLETA DEL SISTEMA DVDCOIN
echo ═══════════════════════════════════════════════════════════
echo.

set ERRORES=0

REM ============================================================
REM [1] VERIFICAR SERVIDOR PYTHON
REM ============================================================
echo [1/8] Verificando servidor Python...
tasklist /FI "IMAGENAME eq python.exe" 2>NUL | find /I /N "python.exe">NUL
if "%ERRORLEVEL%"=="0" (
    echo       ✅ Servidor Python está corriendo
) else (
    echo       ❌ Servidor Python NO está corriendo
    set /a ERRORES+=1
)

REM ============================================================
REM [2] VERIFICAR PUERTO 8000
REM ============================================================
echo.
echo [2/8] Verificando puerto 8000...
netstat -ano | findstr ":8000" | findstr "LISTENING" >nul 2>&1
if "%ERRORLEVEL%"=="0" (
    echo       ✅ Puerto 8000 está abierto y escuchando
) else (
    echo       ❌ Puerto 8000 NO está disponible
    set /a ERRORES+=1
)

REM ============================================================
REM [3] VERIFICAR CLOUDFLARE TUNNEL
REM ============================================================
echo.
echo [3/8] Verificando Cloudflare Tunnel...
tasklist /FI "IMAGENAME eq cloudflared.exe" 2>NUL | find /I /N "cloudflared.exe">NUL
if "%ERRORLEVEL%"=="0" (
    echo       ✅ Cloudflare Tunnel está activo
) else (
    echo       ⚠️  Cloudflare Tunnel NO está corriendo
    echo       Ejecuta: OBTENER_URL_PUBLICA.bat
)

REM ============================================================
REM [4] VERIFICAR JWT SECRET
REM ============================================================
echo.
echo [4/8] Verificando JWT Secret...
if exist "conf\jwt_secret.txt" (
    echo       ✅ JWT Secret configurado
) else (
    echo       ❌ JWT Secret NO encontrado
    set /a ERRORES+=1
)

REM ============================================================
REM [5] VERIFICAR BASES DE DATOS
REM ============================================================
echo.
echo [5/8] Verificando bases de datos...
set DB_COUNT=0
if exist "dvdcoin.db" set /a DB_COUNT+=1
if exist "users.db" set /a DB_COUNT+=1
if exist "transactions.db" set /a DB_COUNT+=1
if exist "apuestas.db" set /a DB_COUNT+=1
if exist "votaciones.db" set /a DB_COUNT+=1

if %DB_COUNT% GEQ 3 (
    echo       ✅ Bases de datos encontradas (%DB_COUNT%/5)
) else (
    echo       ⚠️  Solo %DB_COUNT% bases de datos encontradas
)

REM ============================================================
REM [6] VERIFICAR PREGUNTAS PASAPALABRA
REM ============================================================
echo.
echo [6/8] Verificando preguntas Pasapalabra...
if exist "static\pasapalabra\preguntas.json" (
    echo       ✅ Archivo de preguntas encontrado
) else (
    echo       ❌ Archivo de preguntas NO encontrado
    echo       Ejecuta: GENERAR_PREGUNTAS_PASAPALABRA.bat
    set /a ERRORES+=1
)

REM ============================================================
REM [7] VERIFICAR BACKUPS
REM ============================================================
echo.
echo [7/8] Verificando sistema de backups...
if exist "backup\" (
    echo       ✅ Directorio de backups existe
) else (
    echo       ⚠️  Directorio de backups NO existe
)

REM ============================================================
REM [8] TEST DE CONECTIVIDAD LOCAL
REM ============================================================
echo.
echo [8/8] Probando conectividad local...
curl -s -o nul -w "%%{http_code}" http://localhost:8000 >nul 2>&1
if "%ERRORLEVEL%"=="0" (
    echo       ✅ Servidor responde correctamente
) else (
    echo       ⚠️  No se pudo verificar (curl no disponible)
)

REM ============================================================
REM RESUMEN
REM ============================================================
echo.
echo ═══════════════════════════════════════════════════════════
if %ERRORES%==0 (
    echo   ✅ SISTEMA COMPLETAMENTE FUNCIONAL
) else (
    echo   ⚠️  SISTEMA CON %ERRORES% ERRORES
)
echo ═══════════════════════════════════════════════════════════
echo.

REM ============================================================
REM INFORMACIÓN ADICIONAL
REM ============================================================
echo INFORMACIÓN DEL SISTEMA:
echo.
echo Servidor Local:
echo   http://localhost:8000
echo.
echo Para obtener URL pública:
echo   OBTENER_URL_PUBLICA.bat
echo.
echo Para ver logs:
echo   type server.log
echo   type cloudflare_tunnel.log
echo.
echo Documentación completa:
echo   URL_Y_ACCESO.txt
echo   RESUMEN_SISTEMA_COMPLETO.md
echo.

if %ERRORES% GTR 0 (
    echo ⚠️  ACCIONES RECOMENDADAS:
    echo.
    echo 1. Si el servidor no está corriendo:
    echo    python main.py
    echo.
    echo 2. Si Cloudflare no está activo:
    echo    OBTENER_URL_PUBLICA.bat
    echo.
    echo 3. Si hay errores críticos:
    echo    DETENER_SERVIDOR.bat
    echo    ARRANCAR.bat
    echo.
)

pause
