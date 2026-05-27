@echo off
chcp 65001 >nul
title Diagnóstico Completo del Sistema
color 0B

echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo   🔍 DIAGNÓSTICO COMPLETO DEL SISTEMA DVDBANK
echo ═══════════════════════════════════════════════════════════════════════════
echo.
echo Generando informe completo...
echo.

cd /d "%~dp0"

REM Crear archivo de informe
set "INFORME=DIAGNOSTICO_%date:~-4%%date:~3,2%%date:~0,2%_%time:~0,2%%time:~3,2%%time:~6,2%.txt"
set "INFORME=%INFORME: =0%"

(
echo ═══════════════════════════════════════════════════════════════════════════
echo   DIAGNÓSTICO COMPLETO DEL SISTEMA DVDBANK
echo   Fecha: %date% %time%
echo ═══════════════════════════════════════════════════════════════════════════
echo.
echo.

echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo [1] INFORMACIÓN DEL SISTEMA
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.
systeminfo | findstr /C:"Nombre del sistema operativo" /C:"Versión del sistema" /C:"Tipo de sistema" /C:"Memoria física total"
echo.

echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo [2] PROCESOS ACTIVOS
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.
echo Python:
tasklist | findstr "python.exe"
if errorlevel 1 echo    No hay procesos Python activos
echo.
echo Cloudflare:
tasklist | findstr "cloudflared.exe"
if errorlevel 1 echo    No hay procesos Cloudflare activos
echo.

echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo [3] PUERTOS EN USO
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.
echo Puerto 8000 ^(Python^):
netstat -ano | findstr ":8000"
if errorlevel 1 echo    Puerto 8000 no está en uso
echo.

echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo [4] ARCHIVOS DE CONFIGURACIÓN
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.
if exist "main.py" (echo    ✅ main.py) else (echo    ❌ main.py NO ENCONTRADO)
if exist "cloudflared.exe" (echo    ✅ cloudflared.exe) else (echo    ⚠️  cloudflared.exe NO ENCONTRADO)
if exist "cloudflare-dvta-config.yml" (echo    ✅ cloudflare-dvta-config.yml) else (echo    ⚠️  cloudflare-dvta-config.yml NO ENCONTRADO)
if exist "INICIAR_SISTEMA_DVTA.bat" (echo    ✅ INICIAR_SISTEMA_DVTA.bat) else (echo    ❌ INICIAR_SISTEMA_DVTA.bat NO ENCONTRADO)
if exist "DETENER_SISTEMA.bat" (echo    ✅ DETENER_SISTEMA.bat) else (echo    ❌ DETENER_SISTEMA.bat NO ENCONTRADO)
if exist "VER_ESTADO_SISTEMA.bat" (echo    ✅ VER_ESTADO_SISTEMA.bat) else (echo    ❌ VER_ESTADO_SISTEMA.bat NO ENCONTRADO)
echo.

echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo [5] INICIO AUTOMÁTICO
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.
echo Tarea programada:
schtasks /Query /TN "DVDBank_AutoStart" 2>nul
if errorlevel 1 (echo    ⚠️  No configurada) else (echo    ✅ Configurada)
echo.
echo Registro de Windows:
reg query "HKCU\Software\Microsoft\Windows\CurrentVersion\Run" /v "DVDBank_dvta" 2>nul
if errorlevel 1 (echo    ⚠️  No configurada) else (echo    ✅ Configurada)
echo.
echo Carpeta de inicio:
if exist "%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\DVDBank_dvta.lnk" (echo    ✅ Configurada) else (echo    ⚠️  No configurada)
echo.

echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo [6] BASES DE DATOS
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.
if exist "data\users.db" (echo    ✅ users.db) else (echo    ⚠️  users.db NO ENCONTRADA)
if exist "data\rights.db" (echo    ✅ rights.db) else (echo    ⚠️  rights.db NO ENCONTRADA)
if exist "data\transactions.db" (echo    ✅ transactions.db) else (echo    ⚠️  transactions.db NO ENCONTRADA)
if exist "data\stats.db" (echo    ✅ stats.db) else (echo    ⚠️  stats.db NO ENCONTRADA)
if exist "data\opo.db" (echo    ✅ opo.db) else (echo    ⚠️  opo.db NO ENCONTRADA)
if exist "data\apuestas.db" (echo    ✅ apuestas.db) else (echo    ⚠️  apuestas.db NO ENCONTRADA)
echo.

echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo [7] LOGS RECIENTES
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.
if exist "logs\python_server.log" (
    echo Python Server ^(últimas 5 líneas^):
    powershell -Command "Get-Content logs\python_server.log -Tail 5 -ErrorAction SilentlyContinue | ForEach-Object { Write-Host '   ' $_ }"
) else (
    echo    ⚠️  logs\python_server.log NO ENCONTRADO
)
echo.
if exist "logs\cloudflare_tunnel.log" (
    echo Cloudflare Tunnel ^(últimas 5 líneas^):
    powershell -Command "Get-Content logs\cloudflare_tunnel.log -Tail 5 -ErrorAction SilentlyContinue | ForEach-Object { Write-Host '   ' $_ }"
) else if exist "logs\cloudflare_quick.log" (
    echo Cloudflare Quick Tunnel ^(últimas 5 líneas^):
    powershell -Command "Get-Content logs\cloudflare_quick.log -Tail 5 -ErrorAction SilentlyContinue | ForEach-Object { Write-Host '   ' $_ }"
) else (
    echo    ⚠️  No hay logs de Cloudflare
)
echo.

echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo [8] CONECTIVIDAD
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.
echo Servidor local ^(http://localhost:8000^):
curl -s -o nul -w "   HTTP %%{http_code}" http://127.0.0.1:8000 2>nul
if errorlevel 1 (echo    ❌ No responde) else (echo.)
echo.
echo Internet:
ping -n 1 8.8.8.8 >nul 2>&1
if errorlevel 1 (echo    ❌ Sin conexión) else (echo    ✅ Conectado)
echo.

echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo [9] ESPACIO EN DISCO
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.
wmic logicaldisk where "DeviceID='C:'" get DeviceID,Size,FreeSpace /format:table
echo.

echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo [10] VERSIONES DE SOFTWARE
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.
echo Python:
python --version 2>nul
if errorlevel 1 echo    ⚠️  Python no encontrado en PATH
echo.
echo Cloudflared:
if exist "cloudflared.exe" (
    cloudflared.exe --version 2>nul
) else (
    echo    ⚠️  cloudflared.exe no encontrado
)
echo.

echo ═══════════════════════════════════════════════════════════════════════════
echo   FIN DEL DIAGNÓSTICO
echo ═══════════════════════════════════════════════════════════════════════════
echo.
echo Informe guardado en: %INFORME%
echo.
) > "%INFORME%"

REM Mostrar el informe en pantalla
type "%INFORME%"

echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo.
echo Informe guardado en: %INFORME%
echo.
echo Para ver el estado en tiempo real:
echo    VER_ESTADO_SISTEMA.bat
echo.
pause
