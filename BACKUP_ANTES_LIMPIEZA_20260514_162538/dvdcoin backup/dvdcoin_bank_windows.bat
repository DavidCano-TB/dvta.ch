@echo off
setlocal EnableDelayedExpansion
chcp 65001 >nul 2>&1

:: =============================================================================
:: DVDcoin Bank v3.1 - Windows Launcher
:: =============================================================================
:: This script:
::   1. Forces working directory to this script's folder (fixes Run-As-Admin bug)
::   2. Kills any previous instance on port 8000
::   3. Installs Python packages if needed
::   4. Configures ngrok token (once)
::   5. Starts the server (main.py)
::   6. Starts ngrok tunnel
::   7. Opens browser
::
:: FILES NEEDED IN THE SAME FOLDER AS THIS .BAT:
::   main.py          <- backend (already in this folder)
::   static\          <- folder with index.html
::   (Python packages are installed automatically)
::
:: LOGS:
::   logs\app.log     <- server output
::   logs\ngrok.log   <- ngrok output
::   logs\setup.log   <- this script log
::
:: ADD A NEW ADMIN: edit main.py, find ADMINS = {"dvd",...} and add the username
:: =============================================================================

:: ---------------------------------------------------------------------------
:: CRITICAL FIX: force working dir to script location (fixes Run-As-Admin bug
:: that opens C:\Windows\System32 in Explorer instead of running the script)
:: %~dp0 = drive + path of this .bat file, always correct regardless of how
:: the script was launched
:: ---------------------------------------------------------------------------
cd /d "%~dp0"

title DVDcoin Bank v3.1

:: Shorthand for PowerShell
set PS=powershell -NoProfile -ExecutionPolicy Bypass -Command

:: All paths relative to this folder
set APP_DIR=%~dp0
set LOG_DIR=%APP_DIR%logs
set DATA_DIR=%APP_DIR%data
set CONF_DIR=%APP_DIR%conf
set STATIC_DIR=%APP_DIR%static
set VENV_DIR=%APP_DIR%venv

set LOG_APP=%LOG_DIR%\app.log
set LOG_NGROK=%LOG_DIR%\ngrok.log
set LOG_SETUP=%LOG_DIR%\setup.log
set TOKEN_FILE=%CONF_DIR%\.ngrok_token
set PORT=8000

:: Create directories
for %%D in ("%LOG_DIR%" "%DATA_DIR%" "%CONF_DIR%" "%STATIC_DIR%") do (
    if not exist "%%~D" mkdir "%%~D"
)

echo. >> "%LOG_SETUP%"
echo ============================================== >> "%LOG_SETUP%"
echo DVDcoin Bank started %date% %time% >> "%LOG_SETUP%"
echo ============================================== >> "%LOG_SETUP%"

:: ---------------------------------------------------------------------------
:: Show system info
:: ---------------------------------------------------------------------------
cls
echo.
echo  ============================================================
echo   DVDcoin Bank v3.1 - Windows
echo  ============================================================
echo.

for /f "tokens=2 delims=\" %%i in ('whoami 2^>nul') do set SYS_USER=%%i
for /f "tokens=2 delims=:" %%i in ('ipconfig ^| findstr /i "IPv4" ^| findstr /v "169.254"') do (
    set LOCAL_IP=%%i
    set LOCAL_IP=!LOCAL_IP: =!
    goto :got_ip
)
:got_ip

echo   User:     %SYS_USER%
echo   Local IP: %LOCAL_IP%
echo   Folder:   %APP_DIR%
echo.

:: ---------------------------------------------------------------------------
:: STEP 1: Free port 8000
:: ---------------------------------------------------------------------------
echo [1/7] Freeing port %PORT%...
echo [%time%] Freeing port %PORT% >> "%LOG_SETUP%"

for /f "tokens=5" %%i in ('netstat -aon 2^>nul ^| findstr ":%PORT% " ^| findstr "LISTENING"') do (
    if not "%%i"=="0" (
        echo       Killing PID %%i
        taskkill /PID %%i /F >nul 2>&1
    )
)
taskkill /FI "WINDOWTITLE eq DVDcoin-Server" /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq DVDcoin-Ngrok"  /F >nul 2>&1
taskkill /IM ngrok.exe /F >nul 2>&1
timeout /t 2 /nobreak >nul
echo       Port %PORT% free.

:: ---------------------------------------------------------------------------
:: STEP 2: Check Python
:: ---------------------------------------------------------------------------
echo [2/7] Checking Python...
echo [%time%] Checking Python >> "%LOG_SETUP%"

set PYTHON_CMD=
python --version >nul 2>&1
if %errorlevel% equ 0 set PYTHON_CMD=python & goto :python_ok
py -3 --version >nul 2>&1
if %errorlevel% equ 0 set PYTHON_CMD=py -3 & goto :python_ok

echo.
echo  [ERROR] Python not found.
echo.
echo  Please install Python manually:
echo    1. Go to: https://www.python.org/downloads/
echo    2. Click the big yellow Download button
echo    3. Run the installer
echo    4. IMPORTANT: check the box "Add Python to PATH"
echo    5. Click Install Now
echo    6. After install, close this window and run the .bat again
echo.
echo [%time%] ERROR: Python not found >> "%LOG_SETUP%"
pause
exit /b 1

:python_ok
for /f "tokens=*" %%i in ('!PYTHON_CMD! --version 2^>^&1') do set PYVER=%%i
echo       !PYVER!
echo [%time%] Python OK: !PYVER! >> "%LOG_SETUP%"

:: ---------------------------------------------------------------------------
:: STEP 3: Virtual environment and packages
:: ---------------------------------------------------------------------------
echo [3/7] Setting up Python environment...
echo [%time%] Setting up venv >> "%LOG_SETUP%"

if not exist "%VENV_DIR%\Scripts\activate.bat" (
    echo       Creating virtual environment...
    !PYTHON_CMD! -m venv "%VENV_DIR%" >> "%LOG_SETUP%" 2>&1
    if !errorlevel! neq 0 (
        echo  [ERROR] Failed to create venv. Check: %LOG_SETUP%
        pause & exit /b 1
    )
)
call "%VENV_DIR%\Scripts\activate.bat"

echo       Installing packages (first time may take 1-2 minutes)...
python -m pip install --quiet --upgrade pip >> "%LOG_SETUP%" 2>&1
python -m pip install --quiet ^
    "fastapi==0.104.1" ^
    "uvicorn[standard]==0.24.0" ^
    "passlib[bcrypt]==1.7.4" ^
    "python-jose[cryptography]==3.3.0" ^
    "python-multipart==0.0.6" ^
    "aiosqlite==0.19.0" ^
    "slowapi==0.1.9" >> "%LOG_SETUP%" 2>&1

if !errorlevel! neq 0 (
    echo  [ERROR] Package install failed. Check: %LOG_SETUP%
    pause & exit /b 1
)
echo       Packages ready.
echo [%time%] Packages OK >> "%LOG_SETUP%"

:: ---------------------------------------------------------------------------
:: STEP 4: ngrok install and token
:: ---------------------------------------------------------------------------
echo [4/7] Setting up ngrok...
echo [%time%] Setting up ngrok >> "%LOG_SETUP%"

set NGROK_EXE=
set NGROK_TOKEN=

:: Check for ngrok
if exist "%APP_DIR%ngrok.exe" set NGROK_EXE=%APP_DIR%ngrok.exe & goto :ngrok_found
ngrok version >nul 2>&1 & if !errorlevel! equ 0 set NGROK_EXE=ngrok & goto :ngrok_found

:: Try to install via winget
echo       Trying to install ngrok via winget...
winget install --id Ngrok.Ngrok --silent --accept-package-agreements --accept-source-agreements >nul 2>&1
ngrok version >nul 2>&1
if !errorlevel! equ 0 set NGROK_EXE=ngrok & goto :ngrok_found

:: Download directly
echo       Downloading ngrok...
%PS% "try{Invoke-WebRequest -Uri 'https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-windows-amd64.zip' -OutFile '%TEMP%\ngrok.zip' -UseBasicParsing; Expand-Archive '%TEMP%\ngrok.zip' -DestinationPath '%APP_DIR%' -Force; Remove-Item '%TEMP%\ngrok.zip'}catch{Write-Error $_}" >> "%LOG_SETUP%" 2>&1
if exist "%APP_DIR%ngrok.exe" set NGROK_EXE=%APP_DIR%ngrok.exe & goto :ngrok_found

echo       ngrok not available - will run locally only.
echo [%time%] ngrok not available >> "%LOG_SETUP%"
goto :ngrok_done

:ngrok_found
echo       ngrok found.

:: Configure token
if exist "%TOKEN_FILE%" (
    set /p NGROK_TOKEN=<"%TOKEN_FILE%"
    :: Rewrite clean config (NO domain= lines which cause errors)
    if not exist "%LOCALAPPDATA%\ngrok" mkdir "%LOCALAPPDATA%\ngrok"
    (echo authtoken: !NGROK_TOKEN!& echo version: "2") > "%LOCALAPPDATA%\ngrok\ngrok.yml"
    "!NGROK_EXE!" config add-authtoken !NGROK_TOKEN! >nul 2>&1
    echo       Token loaded.
    echo [%time%] ngrok token loaded >> "%LOG_SETUP%"
    goto :ngrok_done
)

echo.
echo  ----------------------------------------------------------------
echo   NGROK SETUP (one time only - token will be saved)
echo  ----------------------------------------------------------------
echo   1. Go to: https://dashboard.ngrok.com/signup
echo   2. Create a free account
echo   3. Go to: https://dashboard.ngrok.com/get-started/your-authtoken
echo   4. Copy your token and paste below
echo  ----------------------------------------------------------------
echo.
set /p "NGROK_TOKEN=  Paste ngrok token (or press Enter to skip): "

if not "!NGROK_TOKEN!"=="" (
    echo !NGROK_TOKEN!> "%TOKEN_FILE%"
    if not exist "%LOCALAPPDATA%\ngrok" mkdir "%LOCALAPPDATA%\ngrok"
    (echo authtoken: !NGROK_TOKEN!& echo version: "2") > "%LOCALAPPDATA%\ngrok\ngrok.yml"
    "!NGROK_EXE!" config add-authtoken !NGROK_TOKEN! >nul 2>&1
    echo       Token saved.
    echo [%time%] ngrok token saved >> "%LOG_SETUP%"
) else (
    echo       Skipped. App will be local only.
    set NGROK_TOKEN=
)

:ngrok_done

:: ---------------------------------------------------------------------------
:: STEP 5: Verify main.py exists
:: ---------------------------------------------------------------------------
echo [5/7] Verifying files...

if not exist "%APP_DIR%main.py" (
    echo  [ERROR] main.py not found in %APP_DIR%
    echo  Make sure main.py is in the same folder as this .bat file.
    echo [%time%] ERROR: main.py missing >> "%LOG_SETUP%"
    pause & exit /b 1
)
if not exist "%APP_DIR%static\index.html" (
    echo  [ERROR] static\index.html not found in %APP_DIR%
    echo  Make sure the static folder is in the same folder as this .bat file.
    echo [%time%] ERROR: index.html missing >> "%LOG_SETUP%"
    pause & exit /b 1
)
echo       main.py OK
echo       static\index.html OK
echo [%time%] Files verified OK >> "%LOG_SETUP%"

:: ---------------------------------------------------------------------------
:: STEP 6: Start the server
:: ---------------------------------------------------------------------------
echo [6/7] Starting server...
echo [%time%] Starting uvicorn >> "%LOG_SETUP%"

call "%VENV_DIR%\Scripts\activate.bat"

start "DVDcoin-Server" /HIGH cmd /c "cd /d "%APP_DIR%" && "%VENV_DIR%\Scripts\activate.bat" && uvicorn main:app --host 0.0.0.0 --port %PORT% --log-level info >> "%LOG_APP%" 2>&1"

:: Wait for server to respond (max 30 seconds)
echo       Waiting for server...
set SERVER_OK=0
for /l %%i in (1,1,15) do (
    timeout /t 2 /nobreak >nul
    %PS% "try{if((Invoke-WebRequest 'http://localhost:%PORT%/api/health' -UseBasicParsing -TimeoutSec 2).StatusCode -eq 200){exit 0}else{exit 1}}catch{exit 1}" >nul 2>&1
    if !errorlevel! equ 0 (
        set SERVER_OK=1
        goto :server_ready
    )
    echo       Still starting... (%%i/15)
)

:server_ready
if "!SERVER_OK!"=="0" (
    echo.
    echo  [ERROR] Server did not start. Last log lines:
    %PS% "Get-Content '%LOG_APP%' -Tail 15 -ErrorAction SilentlyContinue"
    echo.
    echo  Check full log: %LOG_APP%
    echo [%time%] ERROR: Server did not start >> "%LOG_SETUP%"
    pause & exit /b 1
)
echo       Server running on port %PORT%
echo [%time%] Server OK >> "%LOG_SETUP%"

:: ---------------------------------------------------------------------------
:: STEP 7: Start ngrok
:: ---------------------------------------------------------------------------
echo [7/7] Starting ngrok tunnel...
echo [%time%] Starting ngrok >> "%LOG_SETUP%"

set PUBLIC_URL=

if defined NGROK_EXE (
    if not "!NGROK_TOKEN!"=="" (
        :: Start WITHOUT --domain flag (avoids "domain does not exist" error)
        start "DVDcoin-Ngrok" /MIN cmd /c ""%NGROK_EXE%" http %PORT% >> "%LOG_NGROK%" 2>&1"

        echo       Waiting for tunnel...
        for /l %%i in (1,1,15) do (
            timeout /t 2 /nobreak >nul
            for /f "delims=" %%u in ('%PS% "try{$t=(Invoke-WebRequest http://localhost:4040/api/tunnels -UseBasicParsing -TimeoutSec 2 | ConvertFrom-Json).tunnels;$u=$t|Where-Object{$_.public_url -like 'https*'}|Select -First 1 -Exp public_url;if($u){Write-Output $u}}catch{}" 2^>nul') do set PUBLIC_URL=%%u
            if not "!PUBLIC_URL!"=="" goto :ngrok_ready
        )
        echo       Tunnel timeout - check %LOG_NGROK%
        goto :show_summary
        :ngrok_ready
        echo       Tunnel: !PUBLIC_URL!
        echo [%time%] ngrok URL: !PUBLIC_URL! >> "%LOG_SETUP%"
    ) else (
        echo       No token - local only.
    )
) else (
    echo       ngrok not available - local only.
)

:: ---------------------------------------------------------------------------
:: SUMMARY
:: ---------------------------------------------------------------------------
:show_summary
title DVDcoin Bank v3.1 - RUNNING

cls
echo.
echo  ============================================================
echo   DVDcoin Bank v3.1 - RUNNING
echo  ============================================================
echo.
echo   LOCAL:   http://localhost:%PORT%
echo            http://%LOCAL_IP%:%PORT%
echo.
if not "!PUBLIC_URL!"=="" (
    echo   PUBLIC:  !PUBLIC_URL!
    echo            ^^ Share this with your Clubhouse members!
    echo.
    echo   NOTE: This URL changes on every restart (free ngrok plan)
    echo.
)
echo   ADMINS:  dvd, nina, victor, yu
echo   First time? Click Register to set your password.
echo.
echo   LOGS:
echo     Server: %LOG_APP%
echo     Ngrok:  %LOG_NGROK%
echo     Setup:  %LOG_SETUP%
echo.
echo   ADD ADMIN: edit main.py, find ADMINS = {....}
echo              add the username and restart this script
echo.
echo  ============================================================
echo.
echo   Press any key to STOP the server and exit.
echo.

:: Open browser automatically
if not "!PUBLIC_URL!"=="" (
    start "" "!PUBLIC_URL!"
) else (
    start "" "http://localhost:%PORT%"
)

echo [%time%] Server ready. Waiting for stop command. >> "%LOG_SETUP%"

:: Wait for keypress
pause >nul

:: Cleanup on exit
echo.
echo   Stopping DVDcoin Bank...
echo [%time%] Shutting down >> "%LOG_SETUP%"
taskkill /FI "WINDOWTITLE eq DVDcoin-Server" /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq DVDcoin-Ngrok"  /F >nul 2>&1
taskkill /IM ngrok.exe /F >nul 2>&1
echo   Stopped. Data preserved in: %DATA_DIR%
echo [%time%] Shutdown complete >> "%LOG_SETUP%"
timeout /t 2 /nobreak >nul
