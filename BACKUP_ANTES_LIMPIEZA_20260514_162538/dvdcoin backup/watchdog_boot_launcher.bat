@echo off
>C:\DvDcoin\logs\.watchdog_boot echo 1
timeout /t 10 /nobreak >nul
call C:\DvDcoin\watchdog.bat
