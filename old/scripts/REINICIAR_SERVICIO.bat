@echo off
REM ============================================================
REM REINICIAR SERVICIO DVDCOIN
REM Redirige a INICIAR_COMO_ADMIN.bat
REM ============================================================

title DVDcoin - Reiniciar Servicio
cd /d "%~dp0"

net session >nul 2>&1
if %errorlevel% neq 0 (
    echo Solicitando permisos de administrador...
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b
)

echo [1/3] Deteniendo servicio DVDcoinBank...
nssm.exe stop DVDcoinBank force >nul 2>&1
sc stop DVDcoinBank >nul 2>&1
taskkill /F /IM python.exe >nul 2>&1
taskkill /F /IM pythonw.exe >nul 2>&1
taskkill /F /IM ngrok.exe >nul 2>&1
timeout /t 3 /nobreak >nul

echo [2/3] Liberando puerto 8000...
for /f "tokens=5" %%a in ('netstat -ano 2^>nul ^| findstr "0.0.0.0:8000 "') do (
    taskkill /f /pid %%a >nul 2>&1
)
timeout /t 2 /nobreak >nul

echo [3/3] Iniciando sistema completo...
call INICIAR_COMO_ADMIN.bat
