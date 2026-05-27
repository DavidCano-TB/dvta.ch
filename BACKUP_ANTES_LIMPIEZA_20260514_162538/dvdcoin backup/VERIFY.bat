@echo off
chcp 65001 >nul 2>&1
echo.
echo  DVDcoin Bank - Verification
echo  ============================

set LOCAL=http://localhost:8000
set NGROK=https://nonflying-unstiffened-oakley.ngrok-free.dev

echo.
echo  [1] Serveur local: %LOCAL%
powershell -NoProfile -Command "try{$r=Invoke-WebRequest -Uri $env:LOCAL -UseBasicParsing -TimeoutSec 8;if($r.StatusCode -eq 200 -and $r.Content -like '*DVDcoin*'){Write-Host '     OK - HTTP 200 + DVDcoin trouve' -ForegroundColor Green}else{Write-Host ('     ATTENTION - HTTP '+$r.StatusCode) -ForegroundColor Yellow}}catch{Write-Host ('     ECHEC - '+$_.Exception.Message) -ForegroundColor Red}"

echo.
echo  [2] Health endpoint: %LOCAL%/api/health
powershell -NoProfile -Command "try{$r=Invoke-WebRequest -Uri ($env:LOCAL+'/api/health') -UseBasicParsing -TimeoutSec 8;$j=$r.Content|ConvertFrom-Json;$v=$j.version;$n=if($v -eq '3.3'){'(OK)'}else{'(!) METTRE A JOUR main.py v3.3'};Write-Host ('     status='+$j.status+' | v'+$v+' '+$n+' | users='+$j.users+' | txs='+$j.transactions) -ForegroundColor $(if($v -eq '3.3'){'Green'}else{'Yellow'})}catch{Write-Host ('     ECHEC - '+$_.Exception.Message) -ForegroundColor Red}"

echo.
echo  [3] Galerie: %LOCAL%/api/gallery
powershell -NoProfile -Command "try{$r=Invoke-WebRequest -Uri ($env:LOCAL+'/api/gallery') -UseBasicParsing -TimeoutSec 8;$j=$r.Content|ConvertFrom-Json;Write-Host ('     OK - '+$j.Count+' image(s) trouvee(s)') -ForegroundColor Green}catch{$m=$_.Exception.Message;if($m -like '*404*'){Write-Host '     ECHEC 404 - main.py v3.3 pas installe. Copier main.py et redemarrer le service.' -ForegroundColor Red}else{Write-Host ('     ECHEC - '+$m) -ForegroundColor Red}}"

echo.
echo  [4] URL publique ngrok: %NGROK%
powershell -NoProfile -Command "try{$r=Invoke-WebRequest -Uri $env:NGROK -UseBasicParsing -TimeoutSec 25 -MaximumRedirection 10;$b=$r.Content;if($b -like '*DVDcoin*'){Write-Host '     OK - DVDcoin trouve - accessible depuis internet' -ForegroundColor Green}elseif($b -like '*ngrok*'){Write-Host '     OK - Page avertissement ngrok (normal plan gratuit). Cliquer Visit Site une fois.' -ForegroundColor Yellow}else{Write-Host ('     HTTP '+$r.StatusCode+' - verifier manuellement') -ForegroundColor Yellow}}catch{Write-Host ('     ECHEC - '+$_.Exception.Message) -ForegroundColor Red}"

echo.
echo  [5] Processus ngrok.exe:
tasklist /FI "IMAGENAME eq ngrok.exe" 2>nul | findstr /i "ngrok.exe" >nul 2>&1
if %errorlevel% equ 0 (
    echo       EN COURS D'EXECUTION
) else (
    echo       NON TROUVE - lancer start_ngrok.bat
)

echo.
echo  [6] Service Windows DVDcoinBank:
powershell -NoProfile -Command "try{$s=Get-Service -Name DVDcoinBank -ErrorAction Stop;$c=if($s.Status -eq 'Running'){'Green'}else{'Red'};Write-Host ('     '+$s.Status) -ForegroundColor $c}catch{Write-Host '     Service non trouve (verifier INSTALL.bat)' -ForegroundColor Yellow}"

echo.
echo  ============================
echo  Si CHECK 3 = 404 : copier main.py v3.3 dans C:\DvDcoin\ puis redemarrer
echo  Si CHECK 4 = page ngrok : normal, cliquer Visit Site une fois
echo.
pause
