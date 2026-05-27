@echo off
setlocal EnableDelayedExpansion
chcp 65001 >nul 2>&1
cd /d "%~dp0"
title DVDcoin — Watchdog + Backup Installer v2.4

echo.
echo  ╔══════════════════════════════════════════════════════╗
echo  ║   DVDcoin — Watchdog + Backup Installer v2.4        ║
echo  ╚══════════════════════════════════════════════════════╝
echo.

net session >nul 2>&1
if %errorlevel% neq 0 (
    echo  [ERROR] Run as Administrator.
    pause & exit /b 1
)
echo  [OK] Administrator

if not exist "C:\DvDcoin\watchdog.bat" (
    echo  [ERROR] C:\DvDcoin\watchdog.bat not found
    pause & exit /b 1
)
echo  [OK] watchdog.bat found

if not exist "C:\DvDcoin\backup_db.bat" (
    echo  [ERROR] C:\DvDcoin\backup_db.bat not found
    echo         Copy backup_db.bat to C:\DvDcoin\ first.
    pause & exit /b 1
)
echo  [OK] backup_db.bat found

if not exist "C:\DvDcoin\logs"                           mkdir "C:\DvDcoin\logs"
if not exist "C:\Users\PC\Documents\dvdcoin backup\data" mkdir "C:\Users\PC\Documents\dvdcoin backup\data"
echo  [OK] Folders ready

echo.
echo  Removing old tasks...
schtasks /delete /tn "DVDcoin-Watchdog-Boot"   /f >nul 2>&1
schtasks /delete /tn "DVDcoin-Watchdog-Repeat" /f >nul 2>&1
schtasks /delete /tn "DVDcoin-DB-Backup"       /f >nul 2>&1
echo  [OK] Done

:: =============================================================================
:: Create watchdog_boot_launcher.bat
:: =============================================================================
echo.
echo  [1/3] Creating boot launcher...

del "C:\DvDcoin\watchdog_boot_launcher.bat" >nul 2>&1
>>C:\DvDcoin\watchdog_boot_launcher.bat echo @echo off
>>C:\DvDcoin\watchdog_boot_launcher.bat echo ^>C:\DvDcoin\logs\.watchdog_boot echo 1
>>C:\DvDcoin\watchdog_boot_launcher.bat echo timeout /t 10 /nobreak ^>nul
>>C:\DvDcoin\watchdog_boot_launcher.bat echo call C:\DvDcoin\watchdog.bat

if exist "C:\DvDcoin\watchdog_boot_launcher.bat" (
    echo  [OK] watchdog_boot_launcher.bat created
) else (
    echo  [ERROR] Failed to create boot launcher
    pause & exit /b 1
)

:: =============================================================================
:: TASK 1 — Boot task
:: =============================================================================
echo  [2/3] Installing scheduled tasks...

schtasks /create /tn "DVDcoin-Watchdog-Boot" /tr "cmd /c C:\DvDcoin\watchdog_boot_launcher.bat" /sc onstart /ru SYSTEM /rl HIGHEST /f >nul 2>&1
if %errorlevel% equ 0 (
    echo  [OK] DVDcoin-Watchdog-Boot
) else (
    schtasks /create /tn "DVDcoin-Watchdog-Boot" /tr "cmd /c C:\DvDcoin\watchdog_boot_launcher.bat" /sc onstart /ru SYSTEM /f >nul 2>&1
    if !errorlevel! equ 0 (echo  [OK] DVDcoin-Watchdog-Boot) else (echo  [FAIL] DVDcoin-Watchdog-Boot)
)

:: TASK 2 — Repeat every 5 minutes
schtasks /create /tn "DVDcoin-Watchdog-Repeat" /tr "cmd /c C:\DvDcoin\watchdog.bat" /sc minute /mo 5 /ru SYSTEM /f >nul 2>&1
if %errorlevel% equ 0 (echo  [OK] DVDcoin-Watchdog-Repeat) else (echo  [FAIL] DVDcoin-Watchdog-Repeat)

:: TASK 3 — Hourly DB backup
schtasks /create /tn "DVDcoin-DB-Backup" /tr "cmd /c C:\DvDcoin\backup_db.bat" /sc hourly /ru SYSTEM /f >nul 2>&1
if %errorlevel% equ 0 (echo  [OK] DVDcoin-DB-Backup) else (echo  [FAIL] DVDcoin-DB-Backup)

:: =============================================================================
:: Verification
:: =============================================================================
echo.
echo  -- Verification -------------------------------------------------
schtasks /query /tn "DVDcoin-Watchdog-Boot"   >nul 2>&1 && (echo  [PASS] DVDcoin-Watchdog-Boot)   || (echo  [FAIL] DVDcoin-Watchdog-Boot)
schtasks /query /tn "DVDcoin-Watchdog-Repeat" >nul 2>&1 && (echo  [PASS] DVDcoin-Watchdog-Repeat) || (echo  [FAIL] DVDcoin-Watchdog-Repeat)
schtasks /query /tn "DVDcoin-DB-Backup"       >nul 2>&1 && (echo  [PASS] DVDcoin-DB-Backup)       || (echo  [FAIL] DVDcoin-DB-Backup)

:: =============================================================================
:: [3/3] Run first backup test
:: =============================================================================
echo.
echo  [3/3] Running first DB backup...
call "C:\DvDcoin\backup_db.bat"
if %errorlevel% equ 0 (
    echo  [OK] First backup completed
    for /f "tokens=*" %%F in ('dir "C:\Users\PC\Documents\dvdcoin backup\data\dvdcoin_*.db" /b /o-d 2^>nul') do (
        echo  [OK] File: %%F
        goto :backup_done
    )
    :backup_done
) else (
    echo  [WARN] Backup skipped - dvdcoin.db not found
)

:: Run watchdog test
echo.
echo  Running watchdog test...
call "C:\DvDcoin\watchdog.bat"
if %errorlevel% equ 0 (
    echo  [OK] Watchdog test: ALL CHECKS PASSED
) else (
    echo  [WARN] Watchdog: checks failed (normal if ngrok not running)
    echo         See: C:\DvDcoin\logs\watchdog.log
)

:: Create UNINSTALL
del "C:\DvDcoin\UNINSTALL_WATCHDOG.bat" >nul 2>&1
>>C:\DvDcoin\UNINSTALL_WATCHDOG.bat echo @echo off
>>C:\DvDcoin\UNINSTALL_WATCHDOG.bat echo net session ^>nul 2^>^&1 ^|^| (echo Run as Admin ^& pause ^& exit /b 1)
>>C:\DvDcoin\UNINSTALL_WATCHDOG.bat echo schtasks /delete /tn "DVDcoin-Watchdog-Boot"   /f
>>C:\DvDcoin\UNINSTALL_WATCHDOG.bat echo schtasks /delete /tn "DVDcoin-Watchdog-Repeat" /f
>>C:\DvDcoin\UNINSTALL_WATCHDOG.bat echo schtasks /delete /tn "DVDcoin-DB-Backup"       /f
>>C:\DvDcoin\UNINSTALL_WATCHDOG.bat echo del "C:\DvDcoin\logs\.watchdog_fails"   ^>nul 2^>^&1
>>C:\DvDcoin\UNINSTALL_WATCHDOG.bat echo del "C:\DvDcoin\logs\.watchdog_reboots" ^>nul 2^>^&1
>>C:\DvDcoin\UNINSTALL_WATCHDOG.bat echo del "C:\DvDcoin\logs\.watchdog_boot"    ^>nul 2^>^&1
>>C:\DvDcoin\UNINSTALL_WATCHDOG.bat echo echo [OK] Watchdog removed.
>>C:\DvDcoin\UNINSTALL_WATCHDOG.bat echo pause

echo.
echo  ════════════════════════════════════════════════════════
echo   Installation complete!
echo  ════════════════════════════════════════════════════════
echo.
echo   Tasks:
echo     DVDcoin-Watchdog-Boot    at Windows start
echo     DVDcoin-Watchdog-Repeat  every 5 minutes
echo     DVDcoin-DB-Backup        every hour
echo.
echo   Restore folder:
echo     C:\Users\PC\Documents\dvdcoin backup\
echo.
echo   DB backups:
echo     C:\Users\PC\Documents\dvdcoin backup\data\
echo     (48 max = 48 hours)
echo.
echo   Log:      C:\DvDcoin\logs\watchdog.log
echo   Uninstall:C:\DvDcoin\UNINSTALL_WATCHDOG.bat (as Admin)
echo  ════════════════════════════════════════════════════════
echo.
pause
