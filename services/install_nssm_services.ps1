# ============================================================================
# DVDcoin Platform - Instalador de Servicios Windows con NSSM
# ============================================================================
# Usa NSSM (Non-Sucking Service Manager) para crear servicios Windows reales
# que arrancan automaticamente con Windows y se reinician si caen.
#
# Ejecutar como Administrador:
#   powershell -ExecutionPolicy Bypass -File services\install_nssm_services.ps1
# ============================================================================

$ErrorActionPreference = "Stop"

# Verificar admin
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "ERROR: Ejecutar como Administrador" -ForegroundColor Red
    pause; exit 1
}

$baseDir = Split-Path -Parent $PSScriptRoot
$nssmPath = "$baseDir\services\nssm.exe"
$pythonExe = (Get-Command python -ErrorAction SilentlyContinue).Source
if (-not $pythonExe) { $pythonExe = "C:\Users\PC\AppData\Local\Programs\Python\Python311\python.exe" }

Write-Host ""
Write-Host "=== DVDcoin Platform - Instalador de Servicios ===" -ForegroundColor Cyan
Write-Host "Base: $baseDir" -ForegroundColor Gray
Write-Host "Python: $pythonExe" -ForegroundColor Gray
Write-Host ""

# Descargar NSSM si no existe
if (-not (Test-Path $nssmPath)) {
    Write-Host "Descargando NSSM..." -ForegroundColor Yellow
    $nssmUrl = "https://nssm.cc/release/nssm-2.24.zip"
    $zipPath = "$baseDir\services\nssm.zip"
    try {
        Invoke-WebRequest -Uri $nssmUrl -OutFile $zipPath -UseBasicParsing
        Expand-Archive -Path $zipPath -DestinationPath "$baseDir\services\nssm-temp" -Force
        Copy-Item "$baseDir\services\nssm-temp\nssm-2.24\win64\nssm.exe" $nssmPath
        Remove-Item "$baseDir\services\nssm-temp" -Recurse -Force
        Remove-Item $zipPath -Force
        Write-Host "  NSSM descargado OK" -ForegroundColor Green
    } catch {
        Write-Host "  No se pudo descargar NSSM. Usando sc.exe como fallback." -ForegroundColor Yellow
        $nssmPath = $null
    }
}

# Definicion de servicios
$services = @(
    @{
        Name        = "DVDcoin-Bank"
        Display     = "DVDcoin Bank (8000)"
        Description = "Servidor principal DVDcoin Bank - puerto 8000"
        AppDir      = $baseDir
        Script      = "main.py"
    },
    @{
        Name        = "DVDcoin-BankProxy"
        Display     = "DVDcoin Bank Proxy (8002)"
        Description = "Proxy modular del Bank - puerto 8002"
        AppDir      = "$baseDir\modules\bank"
        Script      = "app_bank.py"
    },
    @{
        Name        = "DVDcoin-Exams"
        Display     = "DVDcoin Exams (8001)"
        Description = "Servidor de examenes y oposiciones - puerto 8001"
        AppDir      = "$baseDir\modules\exams"
        Script      = "app_exams.py"
    }
)

foreach ($svc in $services) {
    Write-Host "--- $($svc.Display) ---" -ForegroundColor Yellow

    # Detener y eliminar si existe
    $existing = Get-Service -Name $svc.Name -ErrorAction SilentlyContinue
    if ($existing) {
        Write-Host "  Deteniendo servicio existente..." -ForegroundColor Gray
        Stop-Service -Name $svc.Name -Force -ErrorAction SilentlyContinue
        Start-Sleep -Seconds 1
        if ($nssmPath) {
            & $nssmPath remove $svc.Name confirm 2>$null
        } else {
            sc.exe delete $svc.Name 2>$null
        }
        Start-Sleep -Seconds 1
    }

    if ($nssmPath -and (Test-Path $nssmPath)) {
        # Instalar con NSSM
        & $nssmPath install $svc.Name $pythonExe $svc.Script
        & $nssmPath set $svc.Name AppDirectory $svc.AppDir
        & $nssmPath set $svc.Name DisplayName $svc.Display
        & $nssmPath set $svc.Name Description $svc.Description
        & $nssmPath set $svc.Name Start SERVICE_AUTO_START
        & $nssmPath set $svc.Name AppStdout "$baseDir\services\logs\$($svc.Name).log"
        & $nssmPath set $svc.Name AppStderr "$baseDir\services\logs\$($svc.Name).log"
        & $nssmPath set $svc.Name AppRotateFiles 1
        & $nssmPath set $svc.Name AppRotateBytes 5000000
        & $nssmPath set $svc.Name AppRestartDelay 3000
        & $nssmPath set $svc.Name AppExit Default Restart
    } else {
        # Fallback: crear servicio con sc.exe + wrapper bat
        $wrapperBat = "$baseDir\services\$($svc.Name).bat"
        Set-Content -Path $wrapperBat -Value "@echo off`ncd /d `"$($svc.AppDir)`"`n`"$pythonExe`" `"$($svc.Script)`""
        sc.exe create $svc.Name binPath= "`"$pythonExe`" `"$($svc.AppDir)\$($svc.Script)`"" start= auto DisplayName= "$($svc.Display)"
        sc.exe description $svc.Name "$($svc.Description)"
        sc.exe failure $svc.Name reset= 60 actions= restart/3000/restart/5000/restart/10000
    }

    # Iniciar
    Start-Service -Name $svc.Name -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 2
    $status = (Get-Service -Name $svc.Name -ErrorAction SilentlyContinue).Status
    if ($status -eq "Running") {
        Write-Host "  OK - Running" -ForegroundColor Green
    } else {
        Write-Host "  Estado: $status (puede tardar en arrancar)" -ForegroundColor Yellow
    }
    Write-Host ""
}

# Cloudflare Tunnel
Write-Host "--- DVDcoin Cloudflare Tunnel ---" -ForegroundColor Yellow
$tunnelName = "DVDcoin-Tunnel"
$existing = Get-Service -Name $tunnelName -ErrorAction SilentlyContinue
if ($existing) {
    Stop-Service -Name $tunnelName -Force -ErrorAction SilentlyContinue
    if ($nssmPath) { & $nssmPath remove $tunnelName confirm 2>$null } else { sc.exe delete $tunnelName 2>$null }
    Start-Sleep -Seconds 1
}

$cloudflaredExe = (Get-Command cloudflared -ErrorAction SilentlyContinue).Source
if ($cloudflaredExe) {
    $configFile = "$baseDir\cloudflare-dvta-config.yml"
    if ($nssmPath -and (Test-Path $nssmPath)) {
        & $nssmPath install $tunnelName $cloudflaredExe "tunnel --config `"$configFile`" run"
        & $nssmPath set $tunnelName AppDirectory $baseDir
        & $nssmPath set $tunnelName DisplayName "DVDcoin Cloudflare Tunnel"
        & $nssmPath set $tunnelName Description "Tunel Cloudflare para dvta.ch y bank.dvta.ch"
        & $nssmPath set $tunnelName Start SERVICE_AUTO_START
        & $nssmPath set $tunnelName AppRestartDelay 5000
        & $nssmPath set $tunnelName AppExit Default Restart
    } else {
        sc.exe create $tunnelName binPath= "`"$cloudflaredExe`" tunnel --config `"$configFile`" run" start= auto
    }
    Start-Service -Name $tunnelName -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 2
    $status = (Get-Service -Name $tunnelName -ErrorAction SilentlyContinue).Status
    Write-Host "  Estado: $status" -ForegroundColor $(if($status -eq "Running"){"Green"}else{"Yellow"})
} else {
    Write-Host "  cloudflared no encontrado - instalar manualmente" -ForegroundColor Red
}

# Crear directorio de logs
New-Item -ItemType Directory -Path "$baseDir\services\logs" -Force | Out-Null

Write-Host ""
Write-Host "=== Resumen ===" -ForegroundColor Cyan
Get-Service -Name "DVDcoin-*" -ErrorAction SilentlyContinue | Format-Table Name, Status, StartType -AutoSize
Write-Host ""
Write-Host "Los servicios arrancan automaticamente con Windows." -ForegroundColor Green
Write-Host "Si caen, se reinician solos en 3 segundos." -ForegroundColor Green
Write-Host ""
pause
