@echo off
REM ============================================================
REM REINICIAR SERVIDOR AHORA
REM Redirige a INICIAR_COMO_ADMIN.bat
REM ============================================================
echo ========================================
echo REINICIANDO SERVIDOR DVDCOIN
echo ========================================
echo.

cd /d "%~dp0"

echo [1/2] Deteniendo procesos...
taskkill /F /IM python.exe /T >nul 2>&1
taskkill /F /IM pythonw.exe /T >nul 2>&1
taskkill /F /IM ngrok.exe /T >nul 2>&1
timeout /t 2 /nobreak >nul

echo [2/2] Iniciando sistema completo...
call INICIAR_COMO_ADMIN.bat
