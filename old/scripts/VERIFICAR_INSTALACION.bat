@echo off
REM ============================================================
REM DVDCOIN BANK - VERIFICAR INSTALACION
REM Verifica que todo esté correctamente configurado
REM ============================================================

chcp 65001 >nul
title DVDCoin Bank - Verificar Instalación
cd /d "%~dp0"

echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                                                              ║
echo ║         DVDCOIN BANK - VERIFICACION DE INSTALACION           ║
echo ║                                                              ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

set ERRORS=0
set WARNINGS=0

REM ============================================================
REM VERIFICAR PYTHON
REM ============================================================
echo [1/10] Verificando Python...

python --version >nul 2>&1
if errorlevel 1 (
    echo       ✗ Python NO instalado
    set /a ERRORS+=1
) else (
    for /f "tokens=*" %%i in ('python --version 2^>^&1') do (
        echo       ✓ %%i
    )
)

echo.

REM ============================================================
REM VERIFICAR UVICORN
REM ============================================================
echo [2/10] Verificando Uvicorn...

python -m uvicorn --version >nul 2>&1
if errorlevel 1 (
    echo       ✗ Uvicorn NO instalado
    echo       Instala con: pip install uvicorn
    set /a ERRORS+=1
) else (
    echo       ✓ Uvicorn instalado
)

echo.

REM ============================================================
REM VERIFICAR FASTAPI
REM ============================================================
echo [3/10] Verificando FastAPI...

python -c "import fastapi" >nul 2>&1
if errorlevel 1 (
    echo       ✗ FastAPI NO instalado
    echo       Instala con: pip install fastapi
    set /a ERRORS+=1
) else (
    echo       ✓ FastAPI instalado
)

echo.

REM ============================================================
REM VERIFICAR ARCHIVOS PRINCIPALES
REM ============================================================
echo [4/10] Verificando archivos principales...

if exist "main.py" (
    echo       ✓ main.py encontrado
) else (
    if exist "src\main.py" (
        echo       ✓ src\main.py encontrado
    ) else (
        echo       ✗ main.py NO encontrado
        set /a ERRORS+=1
    )
)

if exist "static" (
    echo       ✓ Carpeta static/ encontrada
) else (
    echo       ✗ Carpeta static/ NO encontrada
    set /a ERRORS+=1
)

if exist "data" (
    echo       ✓ Carpeta data/ encontrada
) else (
    echo       ⚠ Carpeta data/ NO encontrada (se creará automáticamente)
    set /a WARNINGS+=1
)

echo.

REM ============================================================
REM VERIFICAR BASES DE DATOS
REM ============================================================
echo [5/10] Verificando bases de datos...

set DB_COUNT=0

if exist "data\users.db" (
    echo       ✓ users.db
    set /a DB_COUNT+=1
)
if exist "data\transactions.db" (
    echo       ✓ transactions.db
    set /a DB_COUNT+=1
)
if exist "data\rights.db" (
    echo       ✓ rights.db
    set /a DB_COUNT+=1
)
if exist "data\stats.db" (
    echo       ✓ stats.db
    set /a DB_COUNT+=1
)
if exist "data\opo.db" (
    echo       ✓ opo.db
    set /a DB_COUNT+=1
)

if %DB_COUNT% EQU 0 (
    echo       ⚠ No se encontraron bases de datos (se crearán al iniciar)
    set /a WARNINGS+=1
) else (
    echo       ✓ %DB_COUNT% bases de datos encontradas
)

echo.

REM ============================================================
REM VERIFICAR PUERTO 8000
REM ============================================================
echo [6/10] Verificando puerto 8000...

netstat -ano | findstr ":8000" | findstr "LISTENING" >nul 2>&1
if errorlevel 1 (
    echo       ✓ Puerto 8000 disponible
) else (
    echo       ⚠ Puerto 8000 ocupado
    echo       Ejecuta DETENER_SERVIDOR.bat para liberarlo
    set /a WARNINGS+=1
)

echo.

REM ============================================================
REM VERIFICAR NGROK
REM ============================================================
echo [7/10] Verificando ngrok...

set NGROK_FOUND=0

if exist "ngrok.exe" (
    set NGROK_FOUND=1
    echo       ✓ ngrok.exe encontrado en carpeta actual
)

if exist "tools\ngrok.exe" (
    set NGROK_FOUND=1
    echo       ✓ ngrok.exe encontrado en tools/
)

ngrok version >nul 2>&1
if not errorlevel 1 (
    set NGROK_FOUND=1
    for /f "tokens=*" %%i in ('ngrok version 2^>^&1') do (
        echo       ✓ ngrok instalado: %%i
    )
)

if %NGROK_FOUND% EQU 0 (
    echo       ⚠ ngrok NO encontrado
    echo       Descarga desde: https://ngrok.com/download
    set /a WARNINGS+=1
)

REM Verificar configuración de ngrok
if exist "conf\.ngrok_token" (
    echo       ✓ Configuración de ngrok encontrada
) else (
    echo       ⚠ conf\.ngrok_token NO encontrado
    set /a WARNINGS+=1
)

echo.

REM ============================================================
REM VERIFICAR CLOUDFLARED
REM ============================================================
echo [8/10] Verificando Cloudflare Tunnel...

cloudflared version >nul 2>&1
if errorlevel 1 (
    if exist "cloudflared.exe" (
        echo       ✓ cloudflared.exe encontrado en carpeta actual
    ) else (
        echo       ⚠ cloudflared NO instalado
        echo       Instala con: winget install --id Cloudflare.cloudflared
        echo       O descarga desde: https://github.com/cloudflare/cloudflared/releases
        set /a WARNINGS+=1
    )
) else (
    for /f "tokens=*" %%i in ('cloudflared version 2^>^&1') do (
        echo       ✓ cloudflared instalado: %%i
    )
)

REM Verificar configuración de Cloudflare
if exist "cloudflare-config.yml" (
    echo       ✓ cloudflare-config.yml encontrado
    
    REM Verificar si está configurado
    findstr "<TUNNEL-ID>" cloudflare-config.yml >nul 2>&1
    if not errorlevel 1 (
        echo       ⚠ cloudflare-config.yml NO configurado
        echo       Ejecuta: CONFIGURAR_CLOUDFLARE.bat
        set /a WARNINGS+=1
    ) else (
        echo       ✓ cloudflare-config.yml configurado
    )
) else (
    echo       ⚠ cloudflare-config.yml NO encontrado
    set /a WARNINGS+=1
)

REM Verificar autenticación
if exist "%USERPROFILE%\.cloudflared\cert.pem" (
    echo       ✓ Autenticado con Cloudflare
) else (
    echo       ⚠ NO autenticado con Cloudflare
    echo       Ejecuta: cloudflared tunnel login
    set /a WARNINGS+=1
)

echo.

REM ============================================================
REM VERIFICAR CURL
REM ============================================================
echo [9/10] Verificando curl...

curl --version >nul 2>&1
if errorlevel 1 (
    echo       ⚠ curl NO instalado (opcional)
    set /a WARNINGS+=1
) else (
    echo       ✓ curl instalado
)

echo.

REM ============================================================
REM VERIFICAR SCRIPTS DE INICIO
REM ============================================================
echo [10/10] Verificando scripts de inicio...

if exist "ARRANCAR.bat" (
    echo       ✓ ARRANCAR.bat (ngrok)
)
if exist "INICIAR_CON_CLOUDFLARE.bat" (
    echo       ✓ INICIAR_CON_CLOUDFLARE.bat (Cloudflare Tunnel)
)
if exist "DETENER_SERVIDOR.bat" (
    echo       ✓ DETENER_SERVIDOR.bat
)
if exist "CONFIGURAR_CLOUDFLARE.bat" (
    echo       ✓ CONFIGURAR_CLOUDFLARE.bat
)

echo.

REM ============================================================
REM RESUMEN
REM ============================================================
echo ══════════════════════════════════════════════════════════════
echo.

if %ERRORS% EQU 0 (
    if %WARNINGS% EQU 0 (
        echo ╔══════════════════════════════════════════════════════════════╗
        echo ║                                                              ║
        echo ║              ✓ TODO CORRECTO - LISTO PARA USAR               ║
        echo ║                                                              ║
        echo ╚══════════════════════════════════════════════════════════════╝
        echo.
        echo Para iniciar el servidor:
        echo   - Con Cloudflare Tunnel: INICIAR_CON_CLOUDFLARE.bat
        echo   - Con ngrok:             ARRANCAR.bat
    ) else (
        echo ╔══════════════════════════════════════════════════════════════╗
        echo ║                                                              ║
        echo ║         ✓ FUNCIONAL - HAY %WARNINGS% ADVERTENCIAS                      ║
        echo ║                                                              ║
        echo ╚══════════════════════════════════════════════════════════════╝
        echo.
        echo El sistema puede funcionar, pero hay algunas advertencias.
        echo Revisa los mensajes anteriores para más detalles.
    )
) else (
    echo ╔══════════════════════════════════════════════════════════════╗
    echo ║                                                              ║
    echo ║            ✗ HAY %ERRORS% ERRORES QUE CORREGIR                      ║
    echo ║                                                              ║
    echo ╚══════════════════════════════════════════════════════════════╝
    echo.
    echo Revisa los mensajes anteriores y corrige los errores.
)

echo.
echo Errores:       %ERRORS%
echo Advertencias:  %WARNINGS%
echo.
echo ══════════════════════════════════════════════════════════════
echo.
pause
