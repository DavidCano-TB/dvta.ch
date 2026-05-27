@echo off
:: =============================================================================
:: DVDcoin Bank - KILL ALL PROCESSES
:: Run this to stop server + ngrok cleanly when needed
:: =============================================================================
cd /d "%~dp0"
echo.
echo  Stopping DVDcoin Bank...
echo.

:: Kill by port 8000
echo  [1] Freeing port 8000...
for /f "tokens=5" %%i in ('netstat -aon 2^>nul ^| findstr ":8000 " ^| findstr "LISTENING"') do (
    echo      Killing PID %%i
    taskkill /PID %%i /F >nul 2>&1
)

:: Kill uvicorn
echo  [2] Stopping uvicorn...
taskkill /IM uvicorn.exe /F >nul 2>&1

:: Kill python running uvicorn
for /f "tokens=2" %%i in ('tasklist /FI "IMAGENAME eq python.exe" /NH 2^>nul') do (
    taskkill /PID %%i /F >nul 2>&1
)

:: Kill ngrok
echo  [3] Stopping ngrok...
taskkill /IM ngrok.exe /F >nul 2>&1

:: Kill by window title
taskkill /FI "WINDOWTITLE eq DVDcoin*" /F >nul 2>&1

:: Kill NSSM service if installed
echo  [4] Stopping service (if installed)...
sc query DVDcoinBank >nul 2>&1
if %errorlevel% equ 0 (
    net stop DVDcoinBank >nul 2>&1
    echo      Service stopped.
) else (
    echo      Service not installed, skipping.
)

timeout /t 2 /nobreak >nul

:: Verify port is free
netstat -aon 2>nul | findstr ":8000 " | findstr "LISTENING" >nul 2>&1
if %errorlevel% equ 0 (
    echo.
    echo  [!!] Port 8000 still in use. Try running as Administrator.
) else (
    echo.
    echo  [OK] All DVDcoin processes stopped.
    echo  [OK] Port 8000 is free.
)

echo.
echo  Data preserved at: %~dp0data\dvdcoin.db
echo.
pause
