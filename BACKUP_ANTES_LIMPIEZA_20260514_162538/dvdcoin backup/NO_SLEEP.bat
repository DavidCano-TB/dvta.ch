@echo off
chcp 65001 >nul 2>&1
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo ERREUR: Executer en tant qu'Administrateur
    echo Clic droit sur le fichier, puis Executer en tant qu'administrateur
    pause
    exit /b 1
)

echo.
echo  DVDcoin Bank - Configuration alimentation
echo  ==========================================
echo.
echo  [1] Veille secteur : desactivee
powercfg /change standby-timeout-ac 0
echo  [2] Veille batterie : desactivee
powercfg /change standby-timeout-dc 0
echo  [3] Hibernation secteur : desactivee
powercfg /change hibernate-timeout-ac 0
echo  [4] Hibernation batterie : desactivee
powercfg /change hibernate-timeout-dc 0
echo  [5] Couvercle ferme = ne rien faire...
powercfg /setacvalueindex SCHEME_CURRENT 4f971e89-eebd-4455-a8de-9e59040e7347 5ca83367-6e45-459f-a27b-476b1d01c936 0
powercfg /setdcvalueindex SCHEME_CURRENT 4f971e89-eebd-4455-a8de-9e59040e7347 5ca83367-6e45-459f-a27b-476b1d01c936 0
powercfg /setactive SCHEME_CURRENT
echo  [6] Ecran : extinction apres 30 min
powercfg /change monitor-timeout-ac 30
powercfg /change monitor-timeout-dc 30
echo  [7] Demarrage rapide : desactive
reg add "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Power" /v HiberbootEnabled /t REG_DWORD /d 0 /f >nul 2>&1
echo  [8] Tache Keep-Awake : installation...
schtasks /delete /tn "DVDcoin-KeepAwake" /f >nul 2>&1
schtasks /create /tn "DVDcoin-KeepAwake" /tr "powershell.exe -NonInteractive -WindowStyle Hidden -Command \"while($true){[System.Threading.Thread]::Sleep(55000)}\"" /sc onstart /ru SYSTEM /rl HIGHEST /f >nul 2>&1
echo.
echo  ==========================================
echo  DONE - PC ne se mettra plus en veille.
echo  Couvercle ferme = aucun effet.
echo  Pour annuler : RESTORE_SLEEP.bat
echo.
pause
