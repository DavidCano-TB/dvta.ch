@echo off
setlocal EnableDelayedExpansion
chcp 65001 >nul 2>&1
cd /d C:\DvDcoin
title DVDcoin — ngrok tunnel

set PORT=8000
set LOG_DIR=C:\DvDcoin\logs
set NGROK=C:\DvDcoin\ngrok.exe

if not exist "%NGROK%" set NGROK=ngrok

:: ── Wait for server to be ready (max 60s) ─────────────────────
echo Waiting for DVDcoin server...
set /a tries=0
:wait_loop
powershell -NoProfile -Command "try{$null=(Invoke-WebRequest 'http://localhost:%PORT%/api/health' -UseBasicParsing -TimeoutSec 2);exit 0}catch{exit 1}" >nul 2>&1
if %errorlevel% equ 0 goto :start_ngrok
set /a tries+=1
if %tries% geq 30 (
    echo Server not ready after 60s. Starting ngrok anyway...
    goto :start_ngrok
)
echo  Attempt %tries%/30...
timeout /t 2 /nobreak >nul
goto :wait_loop

:start_ngrok
echo Server ready. Starting ngrok...

:: Kill any previous ngrok
taskkill /IM ngrok.exe /F >nul 2>&1
timeout /t 2 /nobreak >nul

:: Start ngrok minimized
start /MIN "" "%NGROK%" http %PORT%

:: Wait for tunnel
echo Waiting for tunnel...
for /l %%i in (1,1,20) do (
    timeout /t 2 /nobreak >nul
    for /f "delims=" %%u in ('powershell -NoProfile -Command "try{(Invoke-WebRequest http://localhost:4040/api/tunnels -UseBasicParsing|ConvertFrom-Json).tunnels|Where{$_.public_url -like 'https*'}|Select -First 1 -Exp public_url}catch{}" 2^>nul') do (
        echo.
        echo  ┌──────────────────────────────────────────────┐
        echo  │  DVDcoin PUBLIC URL:                         │
        echo  │  %%u
        echo  └──────────────────────────────────────────────┘
        echo  %%u > "%LOG_DIR%\current_url.txt"
        echo %date% %time%: %%u >> "%LOG_DIR%\ngrok_url.log"
        goto :done
    )
    echo  Waiting... (%%i/20)
)
echo  Tunnel timeout. Check ngrok manually at http://localhost:4040
goto :exit

:done
echo.
echo  URL saved to: %LOG_DIR%\current_url.txt
echo  Share this URL with your Clubhouse members!
echo.
echo  Note: URL changes on every restart (free ngrok plan).
echo        Run STATUS.bat anytime to see the current URL.

:exit
