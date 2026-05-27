@echo off
setlocal EnableDelayedExpansion

set SRC=C:\DvDcoin\data\dvdcoin.db
set DEST=C:\Users\PC\Documents\dvdcoin backup\data
set LOG=C:\DvDcoin\logs\watchdog.log

if not exist "!DEST!" mkdir "!DEST!"

if not exist "!SRC!" (
    for /f "tokens=*" %%t in ('powershell -NoProfile -Command "Get-Date -Format \"yyyy-MM-dd HH:mm:ss\""') do set NOW=%%t
    echo [!NOW!] ERROR: dvdcoin.db not found >> "!LOG!"
    exit /b 1
)

for /f "tokens=*" %%d in ('powershell -NoProfile -Command "Get-Date -Format \"yyyy-MM-dd_HH-mm\""') do set TS=%%d

copy /Y "!SRC!" "!DEST!\dvdcoin_!TS!.db" >nul

for /f "skip=48 tokens=*" %%F in ('dir "!DEST!\dvdcoin_*.db" /b /o-d 2^>nul') do (
    del "!DEST!\%%F" >nul 2>nul
)

for /f "tokens=*" %%t in ('powershell -NoProfile -Command "Get-Date -Format \"yyyy-MM-dd HH:mm:ss\""') do set NOW=%%t
echo [!NOW!] DB backup: dvdcoin_!TS!.db >> "!LOG!"
