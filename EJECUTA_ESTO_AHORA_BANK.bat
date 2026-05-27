@echo off
chcp 65001 >nul
title DVDBank - Solución Rápida
color 0A

echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo   🚀 SOLUCION RAPIDA - dvta.ch/bank
echo ═══════════════════════════════════════════════════════════════════════════
echo.
echo   Este script solucionará el problema de "Cloudflare Tunnel error"
echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo.

cd /d "%~dp0"

echo Presiona cualquier tecla para continuar...
pause >nul
echo.

echo ═══════════════════════════════════════════════════════════════════════════
echo   PASO 1/3: DETENIENDO TODO
echo ═══════════════════════════════════════════════════════════════════════════
echo.

call DETENER_TODO.bat

echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo   PASO 2/3: INICIANDO TODO
echo ═══════════════════════════════════════════════════════════════════════════
echo.

call INICIAR_TODO_BANK.bat

echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo   PASO 3/3: VERIFICANDO ESTADO
echo ═══════════════════════════════════════════════════════════════════════════
echo.

call VERIFICAR_ESTADO_BANK.bat

echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo   ✅ PROCESO COMPLETADO
echo ═══════════════════════════════════════════════════════════════════════════
echo.
echo   Si todo está OK, accede a: https://dvta.ch/bank
echo.
echo   Si sigue sin funcionar, revisa:
echo   - logs\python_server.log
echo   - logs\cloudflare_tunnel.log
echo.
pause
