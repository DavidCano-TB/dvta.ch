@echo off
chcp 65001 >nul
cd /d "%~dp0"

:: Iniciar el watchdog en una ventana minimizada
start /min "" "dvdcoin_bank_windows\venv\Scripts\python.exe" "watchdog_monitor.py"

echo Watchdog iniciado en segundo plano
timeout /t 2 >nul
