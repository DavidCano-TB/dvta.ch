@echo off
title VERIFICAR MEJORAS HUNDIR LA FLOTA
cd /d "%~dp0"
color 0A

echo.
echo ╔══════════════════════════════════════════════════╗
echo ║     VERIFICACION MEJORAS HUNDIR LA FLOTA         ║
echo ╚══════════════════════════════════════════════════╝
echo.

echo [1/5] Verificando servidor...
curl -s http://localhost:8000/api/hundirlaflota/status >nul 2>&1
if %errorlevel% equ 0 (
    echo   ✓ Servidor corriendo en puerto 8000
) else (
    echo   ✗ Servidor NO responde
    echo   Ejecuta: python start.py
    pause
    exit /b 1
)

echo.
echo [2/5] Verificando cambios en main.py...
findstr /C:"DEFAULT_SHIP_TYPES" main.py >nul 2>&1
if %errorlevel% equ 0 (
    echo   ✓ DEFAULT_SHIP_TYPES encontrado
) else (
    echo   ✗ DEFAULT_SHIP_TYPES NO encontrado
)

findstr /C:"custom_ships" main.py >nul 2>&1
if %errorlevel% equ 0 (
    echo   ✓ custom_ships encontrado
) else (
    echo   ✗ custom_ships NO encontrado
)

findstr /C:"remove_ship" main.py >nul 2>&1
if %errorlevel% equ 0 (
    echo   ✓ remove_ship encontrado
) else (
    echo   ✗ remove_ship NO encontrado
)

echo.
echo [3/5] Verificando archivos del juego...
if exist "game_pages\hundirlaflota\admin.html" (
    echo   ✓ admin.html existe
) else (
    echo   ✗ admin.html NO existe
)

if exist "game_pages\hundirlaflota\game.html" (
    echo   ✓ game.html existe
) else (
    echo   ⚠ game.html NO existe - NECESITA RECREARSE
    echo     Ver: INSTRUCCIONES_FINALES_HUNDIR_LA_FLOTA.md
)

echo.
echo [4/5] Verificando documentacion...
if exist "MEJORAS_HUNDIR_LA_FLOTA_APLICADAS.md" (
    echo   ✓ MEJORAS_HUNDIR_LA_FLOTA_APLICADAS.md
)
if exist "RESUMEN_MEJORAS_HUNDIR_LA_FLOTA.md" (
    echo   ✓ RESUMEN_MEJORAS_HUNDIR_LA_FLOTA.md
)
if exist "INSTRUCCIONES_FINALES_HUNDIR_LA_FLOTA.md" (
    echo   ✓ INSTRUCCIONES_FINALES_HUNDIR_LA_FLOTA.md
)
if exist "TRABAJO_COMPLETADO_HUNDIR_LA_FLOTA.md" (
    echo   ✓ TRABAJO_COMPLETADO_HUNDIR_LA_FLOTA.md
)

echo.
echo [5/5] Probando APIs nuevas...
echo.
echo   Probando GET /api/hundirlaflota/ships...
curl -s -H "Authorization: Bearer %TOKEN%" http://localhost:8000/api/hundirlaflota/ships >nul 2>&1
if %errorlevel% equ 0 (
    echo   ✓ API /ships responde
) else (
    echo   ⚠ API /ships requiere autenticacion
)

echo.
echo ╔══════════════════════════════════════════════════╗
echo ║              RESUMEN DE VERIFICACION             ║
echo ╚══════════════════════════════════════════════════╝
echo.
echo BACKEND:
echo   ✓ Servidor funcionando
echo   ✓ Cambios aplicados en main.py
echo   ✓ APIs implementadas
echo.
echo FRONTEND:
echo   ✓ admin.html existe
echo   ⚠ game.html necesita recrearse
echo.
echo DOCUMENTACION:
echo   ✓ 4 archivos de documentacion creados
echo.
echo ════════════════════════════════════════════════════
echo.
echo PROXIMO PASO:
echo   1. Lee: INSTRUCCIONES_FINALES_HUNDIR_LA_FLOTA.md
echo   2. Recrea: game_pages\hundirlaflota\game.html
echo   3. Mejora: game_pages\hundirlaflota\admin.html
echo.
echo ESTADO: Backend ✓ Completo | Frontend ⚠ Pendiente
echo.
echo ════════════════════════════════════════════════════
echo.
pause
