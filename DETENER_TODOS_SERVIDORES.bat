@echo off
chcp 65001 >nul
title DVDcoin - Deteniendo Todos los Servidores
color 0C

echo.
echo ═══════════════════════════════════════════════════════════════
echo   🛑 DVDcoin - Deteniendo Todos los Servidores
echo ═══════════════════════════════════════════════════════════════
echo.

echo Buscando procesos Python en puertos 8000-8003...
echo.

REM Encontrar y matar procesos en cada puerto
for %%p in (8000 8001 8002 8003) do (
    echo Verificando puerto %%p...
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":%%p" ^| findstr "LISTENING"') do (
        echo   Deteniendo proceso %%a en puerto %%p
        taskkill /F /PID %%a >nul 2>&1
    )
)

echo.
echo ═══════════════════════════════════════════════════════════════
echo   ✅ Todos los servidores detenidos
echo ═══════════════════════════════════════════════════════════════
echo.

REM Verificar que los puertos están libres
echo Verificando que los puertos están libres...
netstat -ano | findstr ":8000 :8001 :8002 :8003" | findstr "LISTENING"
if errorlevel 1 (
    echo ✅ Todos los puertos están libres
) else (
    echo ⚠️  Algunos puertos aún están en uso
)

echo.
pause
