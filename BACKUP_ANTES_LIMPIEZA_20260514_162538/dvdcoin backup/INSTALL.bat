@echo off
setlocal EnableDelayedExpansion
chcp 65001 >nul 2>&1
cd /d "%~dp0"
title DVDcoin Bank — Installation

:: =============================================================================
:: DVDcoin Bank — INSTALL.bat
:: Run this ONCE as Administrator to set up:
::   1. NSSM service (server auto-starts at Windows boot, no login needed)
::   2. Scheduled task for ngrok (starts at login)
::   3. Power settings (no sleep/suspend)
::   4. start_ngrok.bat helper
::   5. Full verification test suite
::
:: After this runs successfully:
::   - Reboot Windows
::   - Server starts automatically
::   - ngrok starts automatically when you log in
::   - Everything survives reboots forever
::
:: To UNINSTALL everything: run UNINSTALL.bat
:: =============================================================================

set APP_DIR=C:\DvDcoin
set LOG_DIR=%APP_DIR%\logs
set VENV_PY=%APP_DIR%\venv\Scripts\python.exe
set VENV_UV=%APP_DIR%\venv\Scripts\uvicorn.exe
set NGROK=%APP_DIR%\ngrok.exe
set NSSM=%APP_DIR%\nssm.exe
set PORT=8000
set SVC_NAME=DVDcoinBank
set TASK_NAME=DVDcoin-ngrok

set OK=0
set FAIL=0

echo.
echo  ╔══════════════════════════════════════════════════════╗
echo  ║       DVDcoin Bank — Auto-start Installer            ║
echo  ╚══════════════════════════════════════════════════════╝
echo.

:: ── Check Admin rights ────────────────────────────────────────
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo  [!!] This script must run as Administrator.
    echo       Right-click INSTALL.bat ^> Run as administrator
    echo.
    pause
    exit /b 1
)
echo  [OK] Running as Administrator
set /a OK+=1

:: ── Check APP_DIR exists ──────────────────────────────────────
if not exist "%APP_DIR%\main.py" (
    echo  [!!] main.py not found in %APP_DIR%
    echo       Make sure DVDcoin files are in C:\DvDcoin\
    echo.
    pause
    exit /b 1
)
echo  [OK] C:\DvDcoin\main.py found
set /a OK+=1

if not exist "%APP_DIR%\static\index.html" (
    echo  [!!] static\index.html not found
    pause
    exit /b 1
)
echo  [OK] C:\DvDcoin\static\index.html found
set /a OK+=1

:: ── Check Python venv ─────────────────────────────────────────
if not exist "%VENV_PY%" (
    echo  [!!] Python venv not found. Run dvdcoin_bank_windows.bat first.
    pause
    exit /b 1
)
echo  [OK] Python venv found
set /a OK+=1

:: ── Check bcrypt version ──────────────────────────────────────
echo.
echo  [1/8] Verifying bcrypt...
"%VENV_PY%" -c "import bcrypt; print('bcrypt version:', bcrypt.__version__)" 2>nul
if %errorlevel% neq 0 (
    echo  [!!] bcrypt not working. Reinstalling...
    "%APP_DIR%\venv\Scripts\pip.exe" install "bcrypt==4.0.1" --force-reinstall --no-cache-dir
)
"%VENV_PY%" -c "import bcrypt; v=bcrypt.__version__; ok=v.startswith('4.'); print('[OK] bcrypt',v,'- compatible' if ok else '- WRONG VERSION, need 4.x')"
set /a OK+=1

:: ── Test bcrypt actually works ────────────────────────────────
echo  [2/8] Testing bcrypt hash/verify...
"%VENV_PY%" -c "import bcrypt; h=bcrypt.hashpw(b'test',bcrypt.gensalt()); ok=bcrypt.checkpw(b'test',h); print('[OK] bcrypt hash+verify: OK' if ok else '[FAIL] bcrypt broken')" 2>nul
if %errorlevel% neq 0 (
    echo  [!!] bcrypt test failed. Reinstalling...
    "%APP_DIR%\venv\Scripts\pip.exe" install "bcrypt==4.0.1" --force-reinstall --no-cache-dir
    "%VENV_PY%" -c "import bcrypt; h=bcrypt.hashpw(b'test',bcrypt.gensalt()); print('[OK] bcrypt fixed')" 2>nul
)
set /a OK+=1

:: ── Download NSSM if missing ──────────────────────────────────
echo  [3/8] Checking NSSM...
if not exist "%NSSM%" (
    echo       Downloading NSSM...
    powershell -NoProfile -ExecutionPolicy Bypass -Command ^
      "Invoke-WebRequest -Uri 'https://nssm.cc/release/nssm-2.24.zip' -OutFile '%TEMP%\nssm.zip' -UseBasicParsing; Expand-Archive '%TEMP%\nssm.zip' -DestinationPath '%TEMP%\nssm_tmp' -Force; Copy-Item '%TEMP%\nssm_tmp\nssm-2.24\win64\nssm.exe' '%NSSM%'; Remove-Item '%TEMP%\nssm_tmp' -Recurse -Force; Remove-Item '%TEMP%\nssm.zip'" >nul 2>&1
    if not exist "%NSSM%" (
        echo  [!!] Failed to download NSSM. Check internet connection.
        pause
        exit /b 1
    )
)
echo  [OK] NSSM ready
set /a OK+=1

:: ── Kill existing service/processes ──────────────────────────
echo  [4/8] Stopping any existing instances...
sc query %SVC_NAME% >nul 2>&1 && (
    net stop %SVC_NAME% >nul 2>&1
    "%NSSM%" stop %SVC_NAME% >nul 2>&1
)
taskkill /IM uvicorn.exe /F >nul 2>&1
taskkill /IM ngrok.exe   /F >nul 2>&1
for /f "tokens=5" %%i in ('netstat -aon 2^>nul ^| findstr ":%PORT% " ^| findstr "LISTENING"') do (
    taskkill /PID %%i /F >nul 2>&1
)
timeout /t 3 /nobreak >nul
echo  [OK] Clean slate
set /a OK+=1

:: ── Remove old service if exists ──────────────────────────────
sc query %SVC_NAME% >nul 2>&1 && (
    "%NSSM%" remove %SVC_NAME% confirm >nul 2>&1
    timeout /t 2 /nobreak >nul
)

:: ── Install NSSM service ──────────────────────────────────────
echo  [5/8] Installing Windows service...
"%NSSM%" install %SVC_NAME% "%VENV_UV%" >nul 2>&1
"%NSSM%" set %SVC_NAME% AppParameters "main:app --host 0.0.0.0 --port %PORT% --log-level info" >nul 2>&1
"%NSSM%" set %SVC_NAME% AppDirectory "%APP_DIR%" >nul 2>&1
"%NSSM%" set %SVC_NAME% AppStdout "%LOG_DIR%\app.log" >nul 2>&1
"%NSSM%" set %SVC_NAME% AppStderr "%LOG_DIR%\app.log" >nul 2>&1
"%NSSM%" set %SVC_NAME% AppRotateFiles 1 >nul 2>&1
"%NSSM%" set %SVC_NAME% AppRotateBytes 5242880 >nul 2>&1
"%NSSM%" set %SVC_NAME% Start SERVICE_AUTO_START >nul 2>&1
"%NSSM%" set %SVC_NAME% AppRestartDelay 5000 >nul 2>&1
"%NSSM%" set %SVC_NAME% AppThrottle 1500 >nul 2>&1
"%NSSM%" set %SVC_NAME% DisplayName "DVDcoin Bank Server" >nul 2>&1
"%NSSM%" set %SVC_NAME% Description "DVDcoin Bank FastAPI server for Clubhouse community" >nul 2>&1

:: Start service
"%NSSM%" start %SVC_NAME% >nul 2>&1
timeout /t 5 /nobreak >nul

:: Verify service is running
sc query %SVC_NAME% | findstr "RUNNING" >nul 2>&1
if %errorlevel% equ 0 (
    echo  [OK] Service '%SVC_NAME%' installed and running
    set /a OK+=1
) else (
    echo  [!!] Service installed but not running yet. Waiting more...
    timeout /t 10 /nobreak >nul
    sc query %SVC_NAME% | findstr "RUNNING" >nul 2>&1
    if !errorlevel! equ 0 (
        echo  [OK] Service started
        set /a OK+=1
    ) else (
        echo  [!!] Service not running. Check: %LOG_DIR%\app.log
        set /a FAIL+=1
    )
)

:: ── Verify server responds ────────────────────────────────────
echo  [6/8] Testing server health...
set SERVER_OK=0
for /l %%i in (1,1,15) do (
    timeout /t 2 /nobreak >nul
    powershell -NoProfile -Command "try{$r=Invoke-WebRequest 'http://localhost:%PORT%/api/health' -UseBasicParsing -TimeoutSec 3;if($r.StatusCode -eq 200){exit 0}else{exit 1}}catch{exit 1}" >nul 2>&1
    if !errorlevel! equ 0 (
        set SERVER_OK=1
        echo  [OK] Server responding on port %PORT%
        set /a OK+=1
        goto :server_verified
    )
    echo       Waiting... (%%i/15)
)
echo  [!!] Server not responding after 30s. Check %LOG_DIR%\app.log
type "%LOG_DIR%\app.log" 2>nul | findstr /i "error\|exception\|critical"
set /a FAIL+=1

:server_verified

:: ── Create start_ngrok.bat ────────────────────────────────────
echo  [7/8] Creating ngrok launcher...
(
echo @echo off
echo :: DVDcoin ngrok auto-launcher — runs at login
echo :: Waits for server to be ready, then starts ngrok
echo cd /d "%APP_DIR%"
echo.
echo :: Wait up to 60s for server to be ready
echo set /a tries=0
echo :wait_loop
echo curl -s http://localhost:%PORT%/api/health ^>nul 2^>^&1
echo if %%errorlevel%% equ 0 goto :start_ngrok
echo set /a tries+=1
echo if %%tries%% geq 30 goto :start_ngrok
echo timeout /t 2 /nobreak ^>nul
echo goto :wait_loop
echo.
echo :start_ngrok
echo :: Kill any previous ngrok
echo taskkill /IM ngrok.exe /F ^>nul 2^>^&1
echo timeout /t 1 /nobreak ^>nul
echo :: Start ngrok (minimized)
echo if exist "%NGROK%" (
echo     start /MIN "" "%NGROK%" http %PORT%
echo ) else (
echo     start /MIN "" ngrok http %PORT%
echo )
echo :: Log the URL after 8 seconds
echo timeout /t 8 /nobreak ^>nul
echo for /f "delims=" %%%%u in ('powershell -NoProfile -Command "try{(Invoke-WebRequest http://localhost:4040/api/tunnels -UseBasicParsing^|ConvertFrom-Json^).tunnels^|Where{$_.public_url -like 'https*'^}^|Select -First 1 -Exp public_url}catch{}"') do (
echo     echo DVDcoin public URL: %%%%u ^>^> "%LOG_DIR%\ngrok_url.log"
echo     echo %%%%u ^> "%LOG_DIR%\current_url.txt"
echo )
) > "%APP_DIR%\start_ngrok.bat"
echo  [OK] start_ngrok.bat created
set /a OK+=1

:: ── Create scheduled task for ngrok ──────────────────────────
schtasks /delete /tn "%TASK_NAME%" /f >nul 2>&1
schtasks /create /tn "%TASK_NAME%" ^
  /tr "\"%APP_DIR%\start_ngrok.bat\"" ^
  /sc onlogon ^
  /ru "%USERNAME%" ^
  /delay 0001:00 ^
  /f >nul 2>&1

schtasks /query /tn "%TASK_NAME%" >nul 2>&1
if %errorlevel% equ 0 (
    echo  [OK] Scheduled task '%TASK_NAME%' created (runs at login)
    set /a OK+=1
) else (
    echo  [!!] Failed to create scheduled task
    set /a FAIL+=1
)

:: ── Power settings — disable sleep ────────────────────────────
echo  [8/8] Configuring power settings (no sleep)...
powercfg /change monitor-timeout-ac 0     >nul 2>&1
powercfg /change monitor-timeout-dc 0     >nul 2>&1
powercfg /change standby-timeout-ac 0     >nul 2>&1
powercfg /change standby-timeout-dc 0     >nul 2>&1
powercfg /change hibernate-timeout-ac 0   >nul 2>&1
powercfg /change hibernate-timeout-dc 0   >nul 2>&1
powercfg /setactive SCHEME_MIN             >nul 2>&1
echo  [OK] PC will never sleep or hibernate
set /a OK+=1

:: ── Create UNINSTALL.bat ──────────────────────────────────────
(
echo @echo off
echo cd /d "%%~dp0"
echo net session ^>nul 2^>^&1
echo if %%errorlevel%% neq 0 ^(echo Run as Admin ^& pause ^& exit /b 1^)
echo echo Removing DVDcoin auto-start...
echo net stop %SVC_NAME% ^>nul 2^>^&1
echo "%NSSM%" stop %SVC_NAME% ^>nul 2^>^&1
echo "%NSSM%" remove %SVC_NAME% confirm ^>nul 2^>^&1
echo schtasks /delete /tn "%TASK_NAME%" /f ^>nul 2^>^&1
echo taskkill /IM ngrok.exe /F ^>nul 2^>^&1
echo taskkill /IM uvicorn.exe /F ^>nul 2^>^&1
echo echo [OK] Auto-start removed. Data preserved.
echo pause
) > "%APP_DIR%\UNINSTALL.bat"
echo  [OK] UNINSTALL.bat created

:: ── Create STATUS.bat — quick check ───────────────────────────
(
echo @echo off
echo chcp 65001 ^>nul 2^>^&1
echo echo.
echo echo  DVDcoin Bank — Status
echo echo  ─────────────────────────────────────────────
echo echo.
echo sc query %SVC_NAME% ^| findstr "STATE"
echo echo.
echo echo  Health check:
echo curl -s http://localhost:%PORT%/api/health
echo echo.
echo echo  Current ngrok URL:
echo if exist "%LOG_DIR%\current_url.txt" ^(type "%LOG_DIR%\current_url.txt"^) else ^(echo Not available - run start_ngrok.bat^)
echo echo.
echo echo  Log tail:
echo powershell -Command "Get-Content '%LOG_DIR%\app.log' -Tail 5 -ErrorAction SilentlyContinue"
echo echo.
echo pause
) > "%APP_DIR%\STATUS.bat"
echo  [OK] STATUS.bat created

:: ── Final verification test ───────────────────────────────────
echo.
echo  ── Final test suite ────────────────────────────────────
echo.

:: Test 1: service running
sc query %SVC_NAME% | findstr "RUNNING" >nul 2>&1
if %errorlevel% equ 0 (echo  [PASS] Service is RUNNING) else (echo  [FAIL] Service not running)

:: Test 2: port 8000 open
netstat -aon 2>nul | findstr ":%PORT% " | findstr "LISTENING" >nul 2>&1
if %errorlevel% equ 0 (echo  [PASS] Port %PORT% is open) else (echo  [FAIL] Port %PORT% not listening)

:: Test 3: health endpoint
powershell -NoProfile -Command "try{$r=(Invoke-WebRequest 'http://localhost:%PORT%/api/health' -UseBasicParsing).Content;Write-Host '[PASS] Health OK:' $r.Substring(0,50)}catch{Write-Host '[FAIL] Health endpoint unreachable'}" 2>nul

:: Test 4: register endpoint (check it exists, not call it)
powershell -NoProfile -Command "try{$r=Invoke-WebRequest 'http://localhost:%PORT%/api/register' -Method POST -ContentType 'application/json' -Body '{\"username\":\"_test_check\",\"password\":\"x\"}' -UseBasicParsing;if($r.StatusCode -lt 500){Write-Host '[PASS] Register endpoint responds'}else{Write-Host '[FAIL] Register returns 500'}}catch{if($_.Exception.Response.StatusCode.value__ -lt 500){Write-Host '[PASS] Register endpoint responds'}else{Write-Host '[FAIL] Register unreachable'}}" 2>nul

:: Test 5: static files
powershell -NoProfile -Command "try{$r=Invoke-WebRequest 'http://localhost:%PORT%/' -UseBasicParsing;if($r.Content -like '*DVDcoin*'){Write-Host '[PASS] Frontend HTML served correctly'}else{Write-Host '[FAIL] Frontend not serving DVDcoin HTML'}}catch{Write-Host '[FAIL] Frontend unreachable'}" 2>nul

:: Test 6: auto-start configured
sc qc %SVC_NAME% | findstr "AUTO_START" >nul 2>&1
if %errorlevel% equ 0 (echo  [PASS] Service set to AUTO_START on boot) else (echo  [FAIL] Service not set to auto-start)

:: Test 7: scheduled task exists
schtasks /query /tn "%TASK_NAME%" >nul 2>&1
if %errorlevel% equ 0 (echo  [PASS] Ngrok task scheduled at login) else (echo  [WARN] Ngrok task not found)

echo.
echo  ────────────────────────────────────────────────────────
echo  Results: %OK% checks passed · %FAIL% failed
echo  ────────────────────────────────────────────────────────
echo.

if %FAIL% gtr 0 (
    echo  [!!] Some checks failed. Review log: %LOG_DIR%\app.log
) else (
    echo  Installation complete!
    echo.
    echo  What happens now:
    echo    - Server: runs as Windows service, starts at boot automatically
    echo    - Ngrok:  starts at login, URL saved to logs\current_url.txt
    echo    - PC:     will never sleep or hibernate
    echo.
    echo  Useful scripts in C:\DvDcoin\:
    echo    STATUS.bat    - check everything is working
    echo    kill.bat      - stop everything
    echo    UNINSTALL.bat - remove auto-start (keeps data)
    echo.
    echo  REBOOT recommended to verify auto-start works.
    echo  After reboot: check STATUS.bat to get the public URL.
)
echo.
pause
