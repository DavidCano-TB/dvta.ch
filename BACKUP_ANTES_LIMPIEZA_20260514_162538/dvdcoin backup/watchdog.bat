@echo off
:: =============================================================================
:: DVDcoin Watchdog v2.5
:: DEFINITIVE REBOOT LOOP FIX: Uses system uptime instead of lock files.
::
:: Root cause of the loop: the "every 5 min" Repeat task fired while the boot
:: task was still in its grace period. Lock files and boot flags were racey.
::
:: Solution: query actual system uptime via PowerShell Get-CimInstance.
::   Uptime < 3 min  -> PC just booted; open STATUS.bat + toast, skip checks
::   Uptime < 25 min -> service still starting; skip silently, log only
::   Uptime >= 25 min -> run all checks normally
::
:: No lock files. No flag files. No race conditions. Ever.
::
:: Checks performed (uptime >= 25 min only):
::   CHECK1 : ngrok.exe process is running
::   CHECK2 : ngrok URL returns HTTP 200 and body contains "DVDcoin"
::
:: Failure logic:
::   1 failure  -> warning toast, wait for next 5-min check
::   2 failures -> reboot (reboot counter +1)
::   2 reboots both failed -> CLEAN RESTORE from backup then reboot
:: =============================================================================
setlocal EnableDelayedExpansion

set "APP_DIR=C:\DvDcoin"
set "BACKUP_DIR=C:\Users\PC\Documents\dvdcoin backup"
set "LOG=%APP_DIR%\logs\watchdog.log"
set "FAIL_FILE=%APP_DIR%\logs\fail_count.txt"
set "REBOOT_FILE=%APP_DIR%\logs\reboot_count.txt"
set "CHECK_TMP=%TEMP%\dvd_check_result.txt"
set "NGROK_URL=https://nonflying-unstiffened-oakley.ngrok-free.dev/"

:: Ensure logs directory exists
if not exist "%APP_DIR%\logs" mkdir "%APP_DIR%\logs" >nul 2>&1

:: ── Timestamp ────────────────────────────────────────────────────────────────
for /f "tokens=*" %%T in ('powershell -NoProfile -Command "Get-Date -Format \"yyyy-MM-dd HH:mm:ss\""') do set "NOW=%%T"

:: ── Get system uptime in whole minutes ───────────────────────────────────────
for /f "tokens=*" %%M in ('powershell -NoProfile -Command ^
  "[int]((Get-Date)-(Get-CimInstance Win32_OperatingSystem).LastBootUpTime).TotalMinutes" ^
  2^>nul') do set "UPTIME=%%M"

:: Default to 99 if PowerShell failed (safe fallback — allows checks to run)
if "!UPTIME!"=="" set "UPTIME=99"

echo [%NOW%] Watchdog v2.5 started. Uptime: !UPTIME! min >> "%LOG%"

:: =============================================================================
:: GRACE PERIOD — skip checks while system is starting up
:: =============================================================================

if !UPTIME! LSS 3 (
    echo [%NOW%] Uptime ^< 3 min. Opening STATUS, skipping checks. >> "%LOG%"
    start "" "%APP_DIR%\STATUS.bat"
    powershell -NoProfile -WindowStyle Hidden -Command ^
      "Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.MessageBox]::Show('DVDcoin Bank is starting up. Health checks will begin in ~25 minutes.','DVDcoin Watchdog','OK','Information')" >nul 2>&1
    exit /b 0
)

if !UPTIME! LSS 25 (
    echo [%NOW%] Grace period active (uptime ^< 25 min). Skipping checks. >> "%LOG%"
    exit /b 0
)

:: =============================================================================
:: CHECK 1 — ngrok.exe process is running
:: =============================================================================

set "C1=PASS"
tasklist /FI "IMAGENAME eq ngrok.exe" 2>nul | find /I "ngrok.exe" >nul
if errorlevel 1 (
    set "C1=FAIL"
    echo [%NOW%] CHECK1 FAIL: ngrok.exe not found in process list. >> "%LOG%"
) else (
    echo [%NOW%] CHECK1 PASS: ngrok.exe is running. >> "%LOG%"
)

:: =============================================================================
:: CHECK 2 — ngrok URL returns HTTP 200 and page contains "DVDcoin"
:: =============================================================================

set "C2=PASS"
powershell -NoProfile -Command ^
  "try { $r = Invoke-WebRequest -Uri '%NGROK_URL%' -TimeoutSec 20 -UseBasicParsing -ErrorAction Stop; if ($r.StatusCode -eq 200 -and $r.Content -match 'DVDcoin') { 'OK' } else { 'FAIL_CONTENT' } } catch { 'FAIL_CONNECT' }" ^
  > "%CHECK_TMP%" 2>&1

set /p URL_RESULT=<"%CHECK_TMP%"
del "%CHECK_TMP%" >nul 2>&1

if not "!URL_RESULT!"=="OK" (
    set "C2=FAIL"
    echo [%NOW%] CHECK2 FAIL: URL result=!URL_RESULT! >> "%LOG%"
) else (
    echo [%NOW%] CHECK2 PASS: URL responding correctly. >> "%LOG%"
)

:: =============================================================================
:: RESULT — both checks passed
:: =============================================================================

if "!C1!"=="PASS" if "!C2!"=="PASS" (
    echo 0 > "%FAIL_FILE%"
    echo [%NOW%] All checks passed. System healthy. >> "%LOG%"
    exit /b 0
)

:: =============================================================================
:: FAILURE HANDLING
:: =============================================================================

:: Read current consecutive failure count (default 0)
set "FAIL_COUNT=0"
if exist "%FAIL_FILE%" (
    set /p FAIL_COUNT=<"%FAIL_FILE%"
    if "!FAIL_COUNT!"=="" set "FAIL_COUNT=0"
)
set /a FAIL_COUNT+=1
echo !FAIL_COUNT! > "%FAIL_FILE%"
echo [%NOW%] Failure #!FAIL_COUNT! (C1=!C1! C2=!C2!) >> "%LOG%"

:: First failure: warn but do NOT reboot yet
if !FAIL_COUNT! LSS 2 (
    echo [%NOW%] First failure — warning user, waiting for next check. >> "%LOG%"
    powershell -NoProfile -WindowStyle Hidden -Command ^
      "Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.MessageBox]::Show('DVDcoin check failed (1/2). Will recheck in 5 minutes.','DVDcoin Warning','OK','Exclamation')" >nul 2>&1
    exit /b 0
)

:: Two or more consecutive failures — time to reboot (or restore)
set "REBOOT_COUNT=0"
if exist "%REBOOT_FILE%" (
    set /p REBOOT_COUNT=<"%REBOOT_FILE%"
    if "!REBOOT_COUNT!"=="" set "REBOOT_COUNT=0"
)

if !REBOOT_COUNT! GEQ 2 (
    echo [%NOW%] 2 reboots both failed. Starting CLEAN RESTORE. >> "%LOG%"
    goto :CLEAN_RESTORE
)

:: Increment reboot counter and reboot
set /a REBOOT_COUNT+=1
echo !REBOOT_COUNT! > "%REBOOT_FILE%"
echo 0 > "%FAIL_FILE%"
echo [%NOW%] Rebooting (reboot #!REBOOT_COUNT!)... >> "%LOG%"
shutdown /r /t 15 /c "DVDcoin watchdog: 2 consecutive check failures. Rebooting."
exit /b 0

:: =============================================================================
:: CLEAN RESTORE — copy all files from backup, restore latest DB, reinstall service
:: =============================================================================
:CLEAN_RESTORE
echo [%NOW%] === CLEAN RESTORE STARTED === >> "%LOG%"

:: Stop all DVDcoin processes
net stop DVDcoinBank >nul 2>&1
timeout /t 2 /nobreak >nul
taskkill /F /IM ngrok.exe   >nul 2>&1
taskkill /F /IM python.exe  >nul 2>&1
timeout /t 3 /nobreak >nul

:: Restore all application files from backup
xcopy /E /Y /I "%BACKUP_DIR%\*" "%APP_DIR%\" >nul 2>&1

:: Restore the most recent DB backup (newest file first)
for /f "tokens=*" %%F in ('dir /B /O-D "%BACKUP_DIR%\data\dvdcoin_*.db" 2^>nul') do (
    copy /Y "%BACKUP_DIR%\data\%%F" "%APP_DIR%\data\dvdcoin.db" >nul 2>&1
    echo [%NOW%] Restored DB from %%F >> "%LOG%"
    goto :DB_RESTORED
)
:DB_RESTORED

:: Reinstall NSSM Windows service
"%APP_DIR%\nssm.exe" stop   DVDcoinBank confirm >nul 2>&1
"%APP_DIR%\nssm.exe" remove DVDcoinBank confirm >nul 2>&1
timeout /t 2 /nobreak >nul
"%APP_DIR%\nssm.exe" install DVDcoinBank python main.py >nul 2>&1
"%APP_DIR%\nssm.exe" set     DVDcoinBank AppDirectory "%APP_DIR%" >nul 2>&1
"%APP_DIR%\nssm.exe" start   DVDcoinBank >nul 2>&1

:: Reset all counters
echo 0 > "%FAIL_FILE%"
echo 0 > "%REBOOT_FILE%"

echo [%NOW%] === CLEAN RESTORE COMPLETE === >> "%LOG%"
shutdown /r /t 20 /c "DVDcoin: clean restore complete. Rebooting."
exit /b 0
