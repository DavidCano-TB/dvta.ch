# ============================================================================
# GESTOR DE SERVICIOS WINDOWS - DVDcoin Platform
# ============================================================================
# Script para gestionar servicios Windows de DVDcoin
# ============================================================================

param(
    [Parameter(Mandatory=$false)]
    [ValidateSet('start', 'stop', 'restart', 'status', 'logs')]
    [string]$Action = 'status',
    
    [Parameter(Mandatory=$false)]
    [string]$ServiceName = 'all'
)

function Show-Menu {
    Write-Host ""
    Write-Host "═══════════════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
    Write-Host "  GESTOR DE SERVICIOS WINDOWS - DVDcoin Platform" -ForegroundColor Cyan
    Write-Host "═══════════════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "1. Ver estado de servicios" -ForegroundColor White
    Write-Host "2. Iniciar todos los servicios" -ForegroundColor White
    Write-Host "3. Detener todos los servicios" -ForegroundColor White
    Write-Host "4. Reiniciar todos los servicios" -ForegroundColor White
    Write-Host "5. Ver logs recientes" -ForegroundColor White
    Write-Host "6. Gestionar servicio individual" -ForegroundColor White
    Write-Host "0. Salir" -ForegroundColor White
    Write-Host ""
}

function Get-DVDcoinServices {
    return Get-Service -Name "DVDcoin-*" -ErrorAction SilentlyContinue
}

function Show-ServiceStatus {
    $services = Get-DVDcoinServices
    
    if ($services.Count -eq 0) {
        Write-Host "⚠️  No se encontraron servicios DVDcoin instalados" -ForegroundColor Yellow
        Write-Host "Ejecuta 'install_services.ps1' para instalarlos" -ForegroundColor Cyan
        return
    }
    
    Write-Host ""
    Write-Host "Estado de servicios DVDcoin:" -ForegroundColor Yellow
    Write-Host ""
    
    foreach ($svc in $services) {
        $statusColor = if ($svc.Status -eq 'Running') { 'Green' } else { 'Red' }
        $statusIcon = if ($svc.Status -eq 'Running') { '✅' } else { '❌' }
        
        Write-Host "  $statusIcon " -NoNewline -ForegroundColor $statusColor
        Write-Host "$($svc.DisplayName)" -NoNewline -ForegroundColor White
        Write-Host " [$($svc.Status)]" -ForegroundColor $statusColor
    }
    
    Write-Host ""
}

function Start-DVDcoinServices {
    param([string]$Name = 'all')
    
    $services = if ($Name -eq 'all') {
        Get-DVDcoinServices
    } else {
        Get-Service -Name $Name -ErrorAction SilentlyContinue
    }
    
    if ($services.Count -eq 0) {
        Write-Host "❌ No se encontraron servicios" -ForegroundColor Red
        return
    }
    
    Write-Host ""
    Write-Host "Iniciando servicios..." -ForegroundColor Yellow
    
    foreach ($svc in $services) {
        Write-Host "  • $($svc.DisplayName)..." -NoNewline
        try {
            Start-Service -Name $svc.Name -ErrorAction Stop
            Start-Sleep -Seconds 1
            Write-Host " ✅" -ForegroundColor Green
        } catch {
            Write-Host " ❌ $($_.Exception.Message)" -ForegroundColor Red
        }
    }
    
    Write-Host ""
}

function Stop-DVDcoinServices {
    param([string]$Name = 'all')
    
    $services = if ($Name -eq 'all') {
        Get-DVDcoinServices
    } else {
        Get-Service -Name $Name -ErrorAction SilentlyContinue
    }
    
    if ($services.Count -eq 0) {
        Write-Host "❌ No se encontraron servicios" -ForegroundColor Red
        return
    }
    
    Write-Host ""
    Write-Host "Deteniendo servicios..." -ForegroundColor Yellow
    
    foreach ($svc in $services) {
        if ($svc.Status -eq 'Running') {
            Write-Host "  • $($svc.DisplayName)..." -NoNewline
            try {
                Stop-Service -Name $svc.Name -Force -ErrorAction Stop
                Start-Sleep -Seconds 1
                Write-Host " ✅" -ForegroundColor Green
            } catch {
                Write-Host " ❌ $($_.Exception.Message)" -ForegroundColor Red
            }
        }
    }
    
    Write-Host ""
}

function Restart-DVDcoinServices {
    param([string]$Name = 'all')
    
    Write-Host ""
    Write-Host "Reiniciando servicios..." -ForegroundColor Yellow
    Stop-DVDcoinServices -Name $Name
    Start-Sleep -Seconds 2
    Start-DVDcoinServices -Name $Name
}

function Show-ServiceLogs {
    Write-Host ""
    Write-Host "Logs recientes de servicios DVDcoin:" -ForegroundColor Yellow
    Write-Host ""
    
    try {
        $logs = Get-EventLog -LogName Application -Source "DVDcoin-*" -Newest 20 -ErrorAction SilentlyContinue
        
        if ($logs.Count -eq 0) {
            Write-Host "No se encontraron logs recientes" -ForegroundColor Yellow
        } else {
            foreach ($log in $logs) {
                $typeColor = switch ($log.EntryType) {
                    'Error' { 'Red' }
                    'Warning' { 'Yellow' }
                    default { 'White' }
                }
                
                Write-Host "[$($log.TimeGenerated)] " -NoNewline -ForegroundColor Cyan
                Write-Host "$($log.Source): " -NoNewline -ForegroundColor White
                Write-Host "$($log.Message)" -ForegroundColor $typeColor
            }
        }
    } catch {
        Write-Host "⚠️  No se pudieron leer los logs: $($_.Exception.Message)" -ForegroundColor Yellow
    }
    
    Write-Host ""
}

function Manage-IndividualService {
    $services = Get-DVDcoinServices
    
    if ($services.Count -eq 0) {
        Write-Host "❌ No se encontraron servicios" -ForegroundColor Red
        return
    }
    
    Write-Host ""
    Write-Host "Servicios disponibles:" -ForegroundColor Yellow
    $i = 1
    foreach ($svc in $services) {
        Write-Host "$i. $($svc.DisplayName) [$($svc.Status)]" -ForegroundColor White
        $i++
    }
    Write-Host ""
    
    $selection = Read-Host "Selecciona un servicio (1-$($services.Count))"
    
    try {
        $selectedService = $services[$selection - 1]
        
        Write-Host ""
        Write-Host "Servicio: $($selectedService.DisplayName)" -ForegroundColor Cyan
        Write-Host "Estado: $($selectedService.Status)" -ForegroundColor White
        Write-Host ""
        Write-Host "1. Iniciar" -ForegroundColor White
        Write-Host "2. Detener" -ForegroundColor White
        Write-Host "3. Reiniciar" -ForegroundColor White
        Write-Host ""
        
        $action = Read-Host "Selecciona una acción (1-3)"
        
        switch ($action) {
            '1' { Start-DVDcoinServices -Name $selectedService.Name }
            '2' { Stop-DVDcoinServices -Name $selectedService.Name }
            '3' { Restart-DVDcoinServices -Name $selectedService.Name }
        }
    } catch {
        Write-Host "❌ Selección inválida" -ForegroundColor Red
    }
}

# Modo interactivo si no se pasan parámetros
if ($PSBoundParameters.Count -eq 0) {
    while ($true) {
        Show-Menu
        $choice = Read-Host "Selecciona una opción"
        
        switch ($choice) {
            '1' { Show-ServiceStatus }
            '2' { Start-DVDcoinServices }
            '3' { Stop-DVDcoinServices }
            '4' { Restart-DVDcoinServices }
            '5' { Show-ServiceLogs }
            '6' { Manage-IndividualService }
            '0' { exit 0 }
            default { Write-Host "Opción inválida" -ForegroundColor Red }
        }
        
        Write-Host ""
        Read-Host "Presiona Enter para continuar"
    }
} else {
    # Modo comando
    switch ($Action) {
        'status' { Show-ServiceStatus }
        'start' { Start-DVDcoinServices -Name $ServiceName }
        'stop' { Stop-DVDcoinServices -Name $ServiceName }
        'restart' { Restart-DVDcoinServices -Name $ServiceName }
        'logs' { Show-ServiceLogs }
    }
}
