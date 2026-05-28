$nssm = "C:\dvdcoin\nssm.exe"
$py = "C:\Users\PC\AppData\Local\Programs\Python\Python311\python.exe"
$base = "C:\dvdcoin"
$logs = "C:\dvdcoin\services\logs"

New-Item -ItemType Directory -Path $logs -Force | Out-Null

Write-Host "=== DVDcoin - Instalando Servicios Windows ===" -ForegroundColor Cyan
Write-Host ""

# --- DVDcoin-Bank (8000) ---
Write-Host "[1/4] DVDcoin-Bank (puerto 8000)..." -ForegroundColor Yellow
& $nssm stop DVDcoin-Bank 2>$null
& $nssm remove DVDcoin-Bank confirm 2>$null
Start-Sleep 1
& $nssm install DVDcoin-Bank $py "main.py"
& $nssm set DVDcoin-Bank AppDirectory $base
& $nssm set DVDcoin-Bank DisplayName "DVDcoin Bank (8000)"
& $nssm set DVDcoin-Bank Description "Servidor principal DVDcoin Bank"
& $nssm set DVDcoin-Bank Start SERVICE_AUTO_START
& $nssm set DVDcoin-Bank AppStdout "$logs\bank.log"
& $nssm set DVDcoin-Bank AppStderr "$logs\bank.log"
& $nssm set DVDcoin-Bank AppRotateFiles 1
& $nssm set DVDcoin-Bank AppRotateBytes 5000000
& $nssm set DVDcoin-Bank AppExit Default Restart
& $nssm set DVDcoin-Bank AppRestartDelay 3000
& $nssm start DVDcoin-Bank
Write-Host "  OK" -ForegroundColor Green

# --- DVDcoin-BankProxy (8002) ---
Write-Host "[2/4] DVDcoin-BankProxy (puerto 8002)..." -ForegroundColor Yellow
& $nssm stop DVDcoin-BankProxy 2>$null
& $nssm remove DVDcoin-BankProxy confirm 2>$null
Start-Sleep 1
& $nssm install DVDcoin-BankProxy $py "modules\bank\app_bank.py"
& $nssm set DVDcoin-BankProxy AppDirectory $base
& $nssm set DVDcoin-BankProxy DisplayName "DVDcoin Bank Proxy (8002)"
& $nssm set DVDcoin-BankProxy Description "Proxy modular del Bank DVDcoin"
& $nssm set DVDcoin-BankProxy Start SERVICE_AUTO_START
& $nssm set DVDcoin-BankProxy AppStdout "$logs\bankproxy.log"
& $nssm set DVDcoin-BankProxy AppStderr "$logs\bankproxy.log"
& $nssm set DVDcoin-BankProxy AppRotateFiles 1
& $nssm set DVDcoin-BankProxy AppRotateBytes 5000000
& $nssm set DVDcoin-BankProxy AppExit Default Restart
& $nssm set DVDcoin-BankProxy AppRestartDelay 3000
& $nssm start DVDcoin-BankProxy
Write-Host "  OK" -ForegroundColor Green

# --- DVDcoin-Exams (8001) ---
Write-Host "[3/4] DVDcoin-Exams (puerto 8001)..." -ForegroundColor Yellow
& $nssm stop DVDcoin-Exams 2>$null
& $nssm remove DVDcoin-Exams confirm 2>$null
Start-Sleep 1
& $nssm install DVDcoin-Exams $py "modules\exams\app_exams.py"
& $nssm set DVDcoin-Exams AppDirectory $base
& $nssm set DVDcoin-Exams DisplayName "DVDcoin Exams (8001)"
& $nssm set DVDcoin-Exams Description "Servidor de examenes DVDcoin"
& $nssm set DVDcoin-Exams Start SERVICE_AUTO_START
& $nssm set DVDcoin-Exams AppStdout "$logs\exams.log"
& $nssm set DVDcoin-Exams AppStderr "$logs\exams.log"
& $nssm set DVDcoin-Exams AppRotateFiles 1
& $nssm set DVDcoin-Exams AppRotateBytes 5000000
& $nssm set DVDcoin-Exams AppExit Default Restart
& $nssm set DVDcoin-Exams AppRestartDelay 3000
& $nssm start DVDcoin-Exams
Write-Host "  OK" -ForegroundColor Green

# --- DVDcoin-Tunnel ---
Write-Host "[4/4] DVDcoin-Tunnel (Cloudflare)..." -ForegroundColor Yellow
& $nssm stop DVDcoin-Tunnel 2>$null
& $nssm remove DVDcoin-Tunnel confirm 2>$null
Start-Sleep 1
$cf = (Get-Command cloudflared -ErrorAction SilentlyContinue).Source
if ($cf) {
    & $nssm install DVDcoin-Tunnel $cf "tunnel --config C:\dvdcoin\cloudflare-dvta-config.yml run"
    & $nssm set DVDcoin-Tunnel AppDirectory $base
    & $nssm set DVDcoin-Tunnel DisplayName "DVDcoin Cloudflare Tunnel"
    & $nssm set DVDcoin-Tunnel Description "Tunel Cloudflare para dvta.ch"
    & $nssm set DVDcoin-Tunnel Start SERVICE_AUTO_START
    & $nssm set DVDcoin-Tunnel AppStdout "$logs\tunnel.log"
    & $nssm set DVDcoin-Tunnel AppStderr "$logs\tunnel.log"
    & $nssm set DVDcoin-Tunnel AppExit Default Restart
    & $nssm set DVDcoin-Tunnel AppRestartDelay 5000
    & $nssm start DVDcoin-Tunnel
    Write-Host "  OK" -ForegroundColor Green
} else {
    Write-Host "  cloudflared no encontrado" -ForegroundColor Red
}

Write-Host ""
Write-Host "=== Verificando ===" -ForegroundColor Cyan
Start-Sleep 8
Get-Service DVDcoin-* | Format-Table Name, Status, StartType -AutoSize
netstat -ano | findstr "LISTENING" | findstr ":8000 :8001 :8002"
Write-Host ""
Write-Host "LISTO. Los servicios arrancan con Windows y se reinician si caen." -ForegroundColor Green
