# Script de reinicio automático con privilegios elevados
param([switch]$Elevated)

function Test-Admin {
    $currentUser = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
    $currentUser.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

if (-not $Elevated) {
    # Relanzar como administrador
    Start-Process powershell.exe -ArgumentList ("-NoProfile -ExecutionPolicy Bypass -File `"$PSCommandPath`" -Elevated") -Verb RunAs
    exit
}

# Ahora corriendo como administrador
Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host " 🔧 REINICIO AUTOMÁTICO DEL SISTEMA" -ForegroundColor Green
Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# Cambiar al directorio correcto
Set-Location "C:\dvdcoin"

Write-Host "[1/5] Matando procesos Python..." -ForegroundColor Yellow
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2

Write-Host "[2/5] Matando procesos Cloudflare..." -ForegroundColor Yellow
Get-Process cloudflared -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2

Write-Host "[3/5] Verificando puertos liberados..." -ForegroundColor Yellow
$port8000 = netstat -ano | findstr ":8000" | findstr "LISTENING"
if ($port8000) {
    Write-Host "  ⚠ Puerto 8000 aún ocupado, forzando..." -ForegroundColor Yellow
    $pid = ($port8000 -split '\s+')[-1]
    Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 2
}

Write-Host "  ✅ Puertos liberados" -ForegroundColor Green

Write-Host "[4/5] Iniciando servidor Bank (puerto 8000)..." -ForegroundColor Yellow
Start-Process -FilePath "python" -ArgumentList "main.py" -WindowStyle Minimized -WorkingDirectory "C:\dvdcoin"
Start-Sleep -Seconds 10

Write-Host "[5/5] Iniciando túnel Cloudflare..." -ForegroundColor Yellow
Start-Process -FilePath "cloudflared.exe" -ArgumentList "tunnel --config cloudflare-dvta-config.yml run" -WindowStyle Minimized -WorkingDirectory "C:\dvdcoin"
Start-Sleep -Seconds 5

Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host " ✅ VERIFICACIÓN" -ForegroundColor Green
Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

Write-Host "Servidores corriendo:" -ForegroundColor Yellow
Get-Process python -ErrorAction SilentlyContinue | Select-Object Id, ProcessName | Format-Table
Get-Process cloudflared -ErrorAction SilentlyContinue | Select-Object Id, ProcessName | Format-Table

Write-Host "Puertos escuchando:" -ForegroundColor Yellow
netstat -ano | findstr ":8000 :8001" | findstr "LISTENING"

Write-Host ""
Write-Host "Probando servidor..." -ForegroundColor Yellow
Start-Sleep -Seconds 3

try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -TimeoutSec 5 -ErrorAction Stop
    Write-Host "  ✅ Servidor Bank respondiendo: $($response.StatusCode)" -ForegroundColor Green
} catch {
    Write-Host "  ⚠ Servidor Bank no responde aún (puede tardar unos segundos)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host " 🎉 REINICIO COMPLETADO" -ForegroundColor Green
Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""
Write-Host "URLs disponibles:" -ForegroundColor Yellow
Write-Host "  • http://localhost:8000" -ForegroundColor White
Write-Host "  • http://localhost:8000/bank" -ForegroundColor White
Write-Host "  • https://dvta.ch" -ForegroundColor White
Write-Host "  • https://dvta.ch/bank" -ForegroundColor White
Write-Host ""
Write-Host "Presiona cualquier tecla para cerrar..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
