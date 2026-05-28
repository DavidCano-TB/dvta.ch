# ============================================================================
# DESINSTALADOR DE SERVICIOS WINDOWS - DVDcoin Platform
# ============================================================================
# Este script elimina todos los servicios Windows de DVDcoin
# Requiere ejecutarse como Administrador
# ============================================================================

# Verificar privilegios de administrador
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "ERROR: Este script requiere privilegios de administrador" -ForegroundColor Red
    Write-Host "Haz clic derecho y selecciona 'Ejecutar como administrador'" -ForegroundColor Yellow
    pause
    exit 1
}

Write-Host "═══════════════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  DESINSTALADOR DE SERVICIOS WINDOWS - DVDcoin Platform" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

$baseDir = Split-Path -Parent $PSScriptRoot
$pythonExe = "python.exe"

# Obtener todos los servicios DVDcoin
$services = Get-Service -Name "DVDcoin-*" -ErrorAction SilentlyContinue

if ($services.Count -eq 0) {
    Write-Host "No se encontraron servicios DVDcoin instalados" -ForegroundColor Yellow
    pause
    exit 0
}

Write-Host "Servicios encontrados:" -ForegroundColor Yellow
$services | Format-Table Name, DisplayName, Status -AutoSize
Write-Host ""

$confirm = Read-Host "¿Deseas desinstalar todos estos servicios? (S/N)"
if ($confirm -ne 'S' -and $confirm -ne 's') {
    Write-Host "Operación cancelada" -ForegroundColor Yellow
    pause
    exit 0
}

Write-Host ""
Write-Host "Desinstalando servicios..." -ForegroundColor Yellow
Write-Host ""

foreach ($svc in $services) {
    Write-Host "  • Desinstalando $($svc.DisplayName)..." -ForegroundColor Cyan
    
    try {
        # Detener servicio
        if ($svc.Status -eq 'Running') {
            Write-Host "    Deteniendo servicio..." -ForegroundColor Yellow
            Stop-Service -Name $svc.Name -Force -ErrorAction SilentlyContinue
            Start-Sleep -Seconds 2
        }
        
        # Desinstalar servicio
        $wrapperPath = "$baseDir\services\$($svc.Name)-wrapper.py"
        if (Test-Path $wrapperPath) {
            & $pythonExe $wrapperPath remove
            Write-Host "    ✅ Servicio desinstalado" -ForegroundColor Green
            
            # Eliminar wrapper
            Remove-Item $wrapperPath -Force -ErrorAction SilentlyContinue
        } else {
            Write-Host "    ⚠️  Wrapper no encontrado, usando sc delete..." -ForegroundColor Yellow
            sc.exe delete $svc.Name
        }
        
    } catch {
        Write-Host "    ❌ Error: $($_.Exception.Message)" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  ✅ DESINSTALACIÓN COMPLETADA" -ForegroundColor Green
Write-Host "═══════════════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# Verificar servicios restantes
$remainingServices = Get-Service -Name "DVDcoin-*" -ErrorAction SilentlyContinue
if ($remainingServices.Count -eq 0) {
    Write-Host "Todos los servicios han sido desinstalados correctamente" -ForegroundColor Green
} else {
    Write-Host "⚠️  Algunos servicios no pudieron ser desinstalados:" -ForegroundColor Yellow
    $remainingServices | Format-Table Name, Status -AutoSize
}

Write-Host ""
pause
