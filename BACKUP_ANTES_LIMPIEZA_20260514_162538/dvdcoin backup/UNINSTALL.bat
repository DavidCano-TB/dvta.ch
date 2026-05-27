@echo off
cd /d "%~dp0"
net session >nul 2>&1
if %errorlevel% neq 0 (echo Run as Admin & pause & exit /b 1)
echo Removing DVDcoin auto-start...
net stop DVDcoinBank >nul 2>&1
"C:\DvDcoin\nssm.exe" stop DVDcoinBank >nul 2>&1
"C:\DvDcoin\nssm.exe" remove DVDcoinBank confirm >nul 2>&1
schtasks /delete /tn "DVDcoin-ngrok" /f >nul 2>&1
taskkill /IM ngrok.exe /F >nul 2>&1
taskkill /IM uvicorn.exe /F >nul 2>&1
echo [OK] Auto-start removed. Data preserved.
pause
