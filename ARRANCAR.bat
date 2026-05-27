@echo off
chcp 65001 >nul
title DVDBank - Arranque del Sistema
color 0A

echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo   🚀 DVDBANK - ARRANQUE DEL SISTEMA
echo ═══════════════════════════════════════════════════════════════════════════
echo.

cd /d "%~dp0"

REM Matar procesos Python anteriores
echo [1/3] Deteniendo procesos anteriores...
taskkill /F /IM python.exe >nul 2>&1
timeout /t 2 /nobreak >nul
echo      ✅ Procesos detenidos
echo.

REM Iniciar el servidor
echo [2/3] Iniciando servidor Python en puerto 8000...
start "DVDBank Server" python main.py
timeout /t 3 /nobreak >nul
echo      ✅ Servidor iniciado
echo.

REM Verificar que el servidor esté funcionando
echo [3/3] Verificando servidor...
timeout /t 2 /nobreak >nul
tasklist | findstr "python.exe" >nul 2>&1
if %errorlevel% equ 0 (
    echo      ✅ Servidor funcionando correctamente
) else (
    echo      ❌ Error: El servidor no se inició
)
echo.

echo ═══════════════════════════════════════════════════════════════════════════
echo   ✅ SERVIDOR INICIADO
echo ═══════════════════════════════════════════════════════════════════════════
echo.
echo El servidor DVDBank está ejecutándose en:
echo   • http://localhost:8000
echo.
echo Para acceder desde internet (dvta.ch):
echo   • Ejecuta: INICIAR_TUNNEL_DVTA.bat
echo.
echo Para detener el servidor:
echo   • Cierra la ventana "DVDBank Server"
echo   • O ejecuta: taskkill /F /IM python.exe
echo.
pause
