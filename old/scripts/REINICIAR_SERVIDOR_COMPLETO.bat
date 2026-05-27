@echo off
REM ============================================================
REM REINICIAR SERVIDOR COMPLETO
REM Redirige a INICIAR_COMO_ADMIN.bat
REM ============================================================
chcp 65001 >nul
cls
echo ================================================================================
echo REINICIAR SERVIDOR COMPLETO - DVDcoin Bank
echo ================================================================================
echo.
echo Este script detendra todos los procesos y reiniciara el sistema completo.
echo.
pause

cd /d "%~dp0"

echo.
echo [1/2] Deteniendo todos los servicios...
echo ================================================================================
call DETENER_TODO.bat

echo.
echo [2/2] Iniciando sistema completo...
echo ================================================================================
call INICIAR_COMO_ADMIN.bat
