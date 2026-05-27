@echo off
chcp 65001 >nul
cls
echo ═══════════════════════════════════════════════════════════
echo   🔍 VERIFICACIÓN DNS CLOUDFLARE
echo ═══════════════════════════════════════════════════════════
echo.
echo Este script verificará todos los registros DNS actuales
echo en Cloudflare para dvta.ch
echo.
echo ═══════════════════════════════════════════════════════════
echo.

REM Verificar si Python está instalado
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python no está instalado o no está en PATH
    echo.
    pause
    exit /b 1
)

REM Verificar si el script existe
if not exist "verificar_dns_cloudflare.py" (
    echo ❌ No se encuentra verificar_dns_cloudflare.py
    echo.
    pause
    exit /b 1
)

echo Verificando registros DNS...
echo.
python verificar_dns_cloudflare.py

echo.
pause
