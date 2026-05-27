@echo off
setlocal EnableDelayedExpansion
chcp 65001 >nul 2>&1
cd /d "%~dp0"
title DVDcoin Bank — Status

set APP_DIR=C:\DvDcoin
set PORT=8000
set SVC_NAME=DVDcoinBank

echo.
echo  ╔══════════════════════════════════════════════════════╗
echo  ║           DVDcoin Bank — Status Check                ║
echo  ╚══════════════════════════════════════════════════════╝
echo.

:: Service status
echo  [SERVER]
sc query %SVC_NAME% >nul 2>&1
if %errorlevel% equ 0 (
    for /f "tokens=3" %%s in ('sc query %SVC_NAME% ^| findstr "STATE"') do echo    Service:  %%s
) else (
    echo    Service:  NOT INSTALLED
)

:: Port check
netstat -aon 2>nul | findstr ":%PORT% " | findstr "LISTENING" >nul 2>&1
if %errorlevel% equ 0 (
    echo    Port %PORT%: OPEN
) else (
    echo    Port %PORT%: CLOSED
)

:: Health endpoint
echo    Health:
curl -s http://localhost:%PORT%/api/health 2>nul
echo.

:: ngrok status
echo.
echo  [NGROK]
tasklist /FI "IMAGENAME eq ngrok.exe" 2>nul | findstr "ngrok" >nul 2>&1
if %errorlevel% equ 0 (
    echo    Process: RUNNING
    set URL_OK=0
    for /f "delims=" %%u in ('powershell -NoProfile -Command "try{(Invoke-WebRequest http://localhost:4040/api/tunnels -UseBasicParsing|ConvertFrom-Json).tunnels|Where{$_.public_url -like 'https*'}|Select -First 1 -Exp public_url}catch{}" 2^>nul') do (
        echo    URL:     %%u
        echo    %%u > "%APP_DIR%\logs\current_url.txt"
        set URL_OK=1
    )
    if !URL_OK!==0 echo    URL:     (tunnel starting up, wait a moment)
) else (
    echo    Process: NOT RUNNING
    if exist "%APP_DIR%\logs\current_url.txt" (
        echo    Last URL: (may be expired)
        type "%APP_DIR%\logs\current_url.txt"
    ) else (
        echo    No URL saved yet. Run start_ngrok.bat manually.
    )
)

:: Log tail
echo.
echo  [LOGS] Last 6 lines of app.log:
powershell -NoProfile -Command "Get-Content '%APP_DIR%\logs\app.log' -Tail 6 -ErrorAction SilentlyContinue" 2>nul

echo.
echo  ──────────────────────────────────────────────────────
echo  Quick actions:
echo    start_ngrok.bat  — start/restart ngrok tunnel
echo    kill.bat         — stop everything
echo    INSTALL.bat      — reinstall auto-start (run as Admin)
echo  ──────────────────────────────────────────────────────
echo.
pause
