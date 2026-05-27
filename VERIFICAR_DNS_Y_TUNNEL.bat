@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul
cd /d "%~dp0"

echo ═══════════════════════════════════════════════════════════════════════════
echo  🔍 VERIFICACIÓN COMPLETA: DNS Y TÚNEL CLOUDFLARE
echo ═══════════════════════════════════════════════════════════════════════════
echo.

set ERROR_COUNT=0
set WARNING_COUNT=0

REM ═══════════════════════════════════════════════════════════════════════════
echo [1/8] Verificando cloudflared.exe...
REM ═══════════════════════════════════════════════════════════════════════════

if exist "cloudflared.exe" (
    echo     ✅ cloudflared.exe encontrado
    cloudflared.exe --version 2>nul | findstr /C:"cloudflared version" >nul
    if !errorlevel! equ 0 (
        for /f "tokens=*" %%v in ('cloudflared.exe --version 2^>nul ^| findstr /C:"cloudflared version"') do (
            echo     ℹ️  %%v
        )
    )
) else (
    echo     ❌ cloudflared.exe NO encontrado
    echo     📥 Descarga desde: https://github.com/cloudflare/cloudflared/releases
    set /a ERROR_COUNT+=1
)
echo.

REM ═══════════════════════════════════════════════════════════════════════════
echo [2/8] Verificando autenticación con Cloudflare...
REM ═══════════════════════════════════════════════════════════════════════════

if exist "%USERPROFILE%\.cloudflared\cert.pem" (
    echo     ✅ Certificado encontrado: %USERPROFILE%\.cloudflared\cert.pem
) else (
    echo     ❌ NO autenticado con Cloudflare
    echo     🔧 Ejecuta: cloudflared.exe tunnel login
    set /a ERROR_COUNT+=1
)
echo.

REM ═══════════════════════════════════════════════════════════════════════════
echo [3/8] Verificando túneles existentes...
REM ═══════════════════════════════════════════════════════════════════════════

if exist "cloudflared.exe" (
    cloudflared.exe tunnel list >temp_tunnels.txt 2>&1
    
    findstr /C:"dvta-tunnel" temp_tunnels.txt >nul
    if !errorlevel! equ 0 (
        echo     ✅ Túnel 'dvta-tunnel' encontrado
        for /f "tokens=1,2,3" %%a in ('findstr /C:"dvta-tunnel" temp_tunnels.txt') do (
            echo     ℹ️  Tunnel ID: %%a
            echo     ℹ️  Nombre: %%b
            echo     ℹ️  Creado: %%c
            set TUNNEL_ID=%%a
        )
    ) else (
        findstr /C:"Cannot determine default origin certificate" temp_tunnels.txt >nul
        if !errorlevel! equ 0 (
            echo     ❌ No autenticado - ejecuta: cloudflared.exe tunnel login
            set /a ERROR_COUNT+=1
        ) else (
            echo     ⚠️  Túnel 'dvta-tunnel' NO encontrado
            echo     🔧 Ejecuta: cloudflared.exe tunnel create dvta-tunnel
            set /a WARNING_COUNT+=1
        )
    )
    
    del temp_tunnels.txt >nul 2>&1
) else (
    echo     ⚠️  No se puede verificar (cloudflared.exe no encontrado)
    set /a WARNING_COUNT+=1
)
echo.

REM ═══════════════════════════════════════════════════════════════════════════
echo [4/8] Verificando archivo de configuración...
REM ═══════════════════════════════════════════════════════════════════════════

if exist "cloudflare-dvta-config.yml" (
    echo     ✅ Archivo encontrado: cloudflare-dvta-config.yml
    
    findstr /C:"tunnel: TUNNEL_ID_AQUI" "cloudflare-dvta-config.yml" >nul
    if !errorlevel! equ 0 (
        echo     ⚠️  Configuración NO completada (contiene placeholders)
        echo     🔧 Ejecuta: CONFIGURAR_TUNNEL_DVTA_CH.bat
        set /a WARNING_COUNT+=1
    ) else (
        echo     ✅ Configuración completada
    )
) else (
    echo     ⚠️  Archivo de configuración NO encontrado
    set /a WARNING_COUNT+=1
)
echo.

REM ═══════════════════════════════════════════════════════════════════════════
echo [5/8] Verificando resolución DNS...
REM ═══════════════════════════════════════════════════════════════════════════

nslookup dvta.ch >temp_dns.txt 2>&1

findstr /C:"104.21" temp_dns.txt >nul
if !errorlevel! equ 0 (
    echo     ✅ dvta.ch resuelve a Cloudflare
    for /f "tokens=2" %%i in ('findstr /C:"Address:" temp_dns.txt ^| findstr /V "#53"') do (
        echo     ℹ️  IP: %%i
    )
) else (
    findstr /C:"172.67" temp_dns.txt >nul
    if !errorlevel! equ 0 (
        echo     ✅ dvta.ch resuelve a Cloudflare
        for /f "tokens=2" %%i in ('findstr /C:"Address:" temp_dns.txt ^| findstr /V "#53"') do (
            echo     ℹ️  IP: %%i
        )
    ) else (
        findstr /C:"can't find" temp_dns.txt >nul
        if !errorlevel! equ 0 (
            echo     ❌ dvta.ch NO resuelve (dominio no encontrado)
            echo     🔧 Configura rutas DNS: cloudflared.exe tunnel route dns dvta-tunnel dvta.ch
            set /a ERROR_COUNT+=1
        ) else (
            findstr /C:"timed out" temp_dns.txt >nul
            if !errorlevel! equ 0 (
                echo     ⚠️  Timeout DNS (puede ser temporal)
                set /a WARNING_COUNT+=1
            ) else (
                echo     ⚠️  Estado DNS desconocido
                set /a WARNING_COUNT+=1
            )
        )
    )
)

del temp_dns.txt >nul 2>&1
echo.

REM ═══════════════════════════════════════════════════════════════════════════
echo [6/8] Verificando servidor Python...
REM ═══════════════════════════════════════════════════════════════════════════

tasklist | findstr "python.exe" >nul
if !errorlevel! equ 0 (
    echo     ✅ Servidor Python está corriendo
    
    REM Verificar si responde en puerto 8000
    powershell -Command "try { $response = Invoke-WebRequest -Uri 'http://localhost:8000' -TimeoutSec 5 -UseBasicParsing; exit 0 } catch { exit 1 }" >nul 2>&1
    if !errorlevel! equ 0 (
        echo     ✅ Servidor responde en http://localhost:8000
    ) else (
        echo     ⚠️  Servidor no responde en puerto 8000
        set /a WARNING_COUNT+=1
    )
) else (
    echo     ❌ Servidor Python NO está corriendo
    echo     🔧 Ejecuta: INICIAR_DVDBANK_DVTA.bat
    set /a ERROR_COUNT+=1
)
echo.

REM ═══════════════════════════════════════════════════════════════════════════
echo [7/8] Verificando túnel Cloudflare activo...
REM ═══════════════════════════════════════════════════════════════════════════

tasklist | findstr "cloudflared.exe" >nul
if !errorlevel! equ 0 (
    echo     ✅ Túnel Cloudflare está corriendo
    
    if exist "logs\tunnel.log" (
        findstr /C:"registered" "logs\tunnel.log" >nul
        if !errorlevel! equ 0 (
            echo     ✅ Túnel registrado correctamente
        ) else (
            echo     ⚠️  Verificando estado del túnel...
            set /a WARNING_COUNT+=1
        )
    ) else if exist "logs\cloudflare_tunnel.log" (
        findstr /C:"registered" "logs\cloudflare_tunnel.log" >nul
        if !errorlevel! equ 0 (
            echo     ✅ Túnel registrado correctamente
        ) else (
            echo     ⚠️  Verificando estado del túnel...
            set /a WARNING_COUNT+=1
        )
    )
) else (
    echo     ❌ Túnel Cloudflare NO está corriendo
    echo     🔧 Ejecuta: INICIAR_DVDBANK_DVTA.bat
    set /a ERROR_COUNT+=1
)
echo.

REM ═══════════════════════════════════════════════════════════════════════════
echo [8/8] Verificando acceso web...
REM ═══════════════════════════════════════════════════════════════════════════

REM Solo verificar si DNS resuelve
nslookup dvta.ch >nul 2>&1
if !errorlevel! equ 0 (
    powershell -Command "try { $response = Invoke-WebRequest -Uri 'https://dvta.ch' -TimeoutSec 10 -UseBasicParsing; if ($response.StatusCode -eq 200) { exit 0 } else { exit 1 } } catch { exit 1 }" >nul 2>&1
    if !errorlevel! equ 0 (
        echo     ✅ https://dvta.ch accesible (HTTP 200)
    ) else (
        echo     ⚠️  https://dvta.ch no responde o da error
        echo     ℹ️  Puede tardar unos minutos en propagarse
        set /a WARNING_COUNT+=1
    )
) else (
    echo     ⚠️  No se puede verificar (DNS no resuelve)
    set /a WARNING_COUNT+=1
)
echo.

REM ═══════════════════════════════════════════════════════════════════════════
echo ═══════════════════════════════════════════════════════════════════════════
echo  📊 RESUMEN
echo ═══════════════════════════════════════════════════════════════════════════

if !ERROR_COUNT! equ 0 (
    if !WARNING_COUNT! equ 0 (
        echo.
        echo     ✅✅✅ TODO ESTÁ PERFECTO ✅✅✅
        echo.
        echo     Tu sistema está completamente configurado y funcionando.
        echo.
        echo     🌐 Accede a: https://dvta.ch
        echo.
    ) else (
        echo.
        echo     ⚠️  Sistema funcional con !WARNING_COUNT! advertencia(s)
        echo.
        echo     El sistema debería funcionar, pero hay algunas advertencias.
        echo     Revisa los detalles arriba.
        echo.
    )
) else (
    echo.
    echo     ❌ Se encontraron !ERROR_COUNT! error(es) y !WARNING_COUNT! advertencia(s)
    echo.
    echo     El sistema NO está completamente configurado.
    echo     Revisa los errores arriba y sigue las instrucciones.
    echo.
    echo     📖 Guía completa: GUIA_COMPLETA_DNS_DVTA_CH.txt
    echo.
)

echo ═══════════════════════════════════════════════════════════════════════════
echo.
pause
