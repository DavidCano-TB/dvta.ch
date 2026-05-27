@echo off
chcp 65001 >nul 2>&1
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo ERREUR: Executer en tant qu'Administrateur
    pause
    exit /b 1
)
echo Restauration des reglages Windows par defaut...
powercfg /change standby-timeout-ac 30
powercfg /change standby-timeout-dc 10
powercfg /change hibernate-timeout-ac 60
powercfg /change hibernate-timeout-dc 30
powercfg /change monitor-timeout-ac 15
powercfg /change monitor-timeout-dc 10
schtasks /delete /tn "DVDcoin-KeepAwake" /f >nul 2>&1
echo Reglages restaures.
pause
