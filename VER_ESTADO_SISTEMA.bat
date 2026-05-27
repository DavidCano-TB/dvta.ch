@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul
cd /d "%~dp0"

cls
echo ═══════════════════════════════════════════════════════════════════════════
echo  ESTADO DEL SISTEMA DVDBANK - dvta.ch
echo ═══════════════════════════════════════════════════════════════════════════
echo  Actualizado: %date% %time%
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.

REM ═══════════════════════════════════════════════════════════════════════════
REM [1] SERVIDOR PYTHON
REM ═══════════════════════════════════════════════════════════════════════════
echo [1] SERVIDOR PYTHON (Puerto 8000)
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

tasklist | findstr "python.exe" >nul 2>&1
if errorlevel 1 (
    echo     Estado: ❌ DETENIDO
    echo     Acción: Ejecuta INICIAR_DVDBANK.bat para iniciar
) else (
    echo     Estado: ✅ ACTIVO
    
    REM Contar procesos Python
    for /f %%i in ('tasklist ^| findstr "python.exe" ^| find /c /v ""') do set PYTHON_COUNT=%%i
    echo     Procesos: !PYTHON_COUNT!
    
    REM Verificar conectividad HTTP
    powershell -Command "$response = try { Invoke-WebRequest -Uri 'http://localhost:8000' -TimeoutSec 2 -UseBasicParsing; $_.StatusCode } catch { 'Error' }; if ($response -eq 200) { Write-Host '    HTTP: OK (200)' } else { Write-Host '    HTTP: Error' }" 2>nul
)
echo.

REM ═══════════════════════════════════════════════════════════════════════════
REM [2] TÚNEL CLOUDFLARE
REM ═══════════════════════════════════════════════════════════════════════════
echo [2] TÚNEL CLOUDFLARE
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

tasklist | findstr "cloudflared.exe" >nul 2>&1
if errorlevel 1 (
    echo     Estado: ❌ DETENIDO
    echo     Acción: Ejecuta INICIAR_DVDBANK.bat para iniciar
) else (
    echo     Estado: ✅ ACTIVO
    
    REM Mostrar URL del túnel
    if exist "logs\tunnel_url.txt" (
        set /p TUNNEL_URL=<logs\tunnel_url.txt
        if defined TUNNEL_URL (
            echo     URL: !TUNNEL_URL!
        ) else (
            echo     URL: Extrayendo...
        )
    ) else (
        echo     URL: No disponible aún
    )
)
echo.

REM ═══════════════════════════════════════════════════════════════════════════
REM [3] INICIO AUTOMÁTICO
REM ═══════════════════════════════════════════════════════════════════════════
echo [3] INICIO AUTOMÁTICO CON WINDOWS
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

schtasks /query /tn "DVDBank_AutoStart" >nul 2>&1
if errorlevel 1 (
    echo     Estado: ❌ NO CONFIGURADO
    echo     Acción: Ejecuta CONFIGURAR_INICIO_AUTOMATICO_COMPLETO.bat
) else (
    echo     Estado: ✅ CONFIGURADO
    echo     Tarea: DVDBank_AutoStart
)
echo.

REM ═══════════════════════════════════════════════════════════════════════════
REM [4] ACCESOS RÁPIDOS
REM ═══════════════════════════════════════════════════════════════════════════
echo [4] ACCESOS RÁPIDOS
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo     Local:  http://localhost:8000
if exist "logs\tunnel_url.txt" (
    set /p TUNNEL_URL=<logs\tunnel_url.txt
    if defined TUNNEL_URL (
        echo     Túnel:  !TUNNEL_URL!
    )
)
echo.

echo ═══════════════════════════════════════════════════════════════════════════
echo  COMANDOS DISPONIBLES
echo ═══════════════════════════════════════════════════════════════════════════
echo.
echo  INICIAR_DVDBANK.bat                    - Iniciar sistema
echo  CONFIGURAR_INICIO_AUTOMATICO_COMPLETO.bat - Configurar inicio automático
echo  DESACTIVAR_INICIO_AUTOMATICO.bat      - Desactivar inicio automático
echo.
echo ═══════════════════════════════════════════════════════════════════════════

pause
