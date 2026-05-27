@echo off
chcp 65001 >nul
cd /d "C:\dvdcoin\"
start /min "" "C:\dvdcoin\dvdcoin_bank_windows\venv\Scripts\python.exe" "C:\dvdcoin\watchdog_monitor.py"
