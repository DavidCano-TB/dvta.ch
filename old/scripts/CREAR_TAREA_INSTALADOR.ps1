# Script para crear la tarea de instalación automática
# Debe ejecutarse como Administrador

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "Creando tarea de instalación automática..." -ForegroundColor Cyan
Write-Host ""

try {
    # Eliminar tareas antiguas
    Write-Host "[1/2] Eliminando tareas antiguas..."
    @("DVDcoin-Instalador", "DVDcoin-Autostart", "DVDcoin-ngrok", "DVDcoin", "DVDcoin-Cloudflare") | ForEach-Object {
        try {
            Unregister-ScheduledTask -TaskName $_ -Confirm:$false -ErrorAction SilentlyContinue
        } catch {}
    }
    Write-Host "      ✓ Tareas antiguas eliminadas" -ForegroundColor Green
    
    # Crear nueva tarea
    Write-Host ""
    Write-Host "[2/2] Creando tarea DVDcoin-Instalador..."
    
    $action = New-ScheduledTaskAction -Execute "c:\dvdcoin\INSTALACION_AUTOMATICA_CLOUDFLARE.bat"
    $trigger = New-ScheduledTaskTrigger -AtLogOn
    $trigger.Delay = "PT5S"  # 5 segundos de delay
    $principal = New-ScheduledTaskPrincipal -UserId "$env:USERDOMAIN\$env:USERNAME" -LogonType Interactive -RunLevel Highest
    $settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable
    
    Register-ScheduledTask -TaskName "DVDcoin-Instalador" -Action $action -Trigger $trigger -Principal $principal -Settings $settings -Force | Out-Null
    
    Write-Host "      ✓ Tarea creada correctamente" -ForegroundColor Green
    
    # Verificar
    Write-Host ""
    Write-Host "Verificando tarea..."
    $task = Get-ScheduledTask -TaskName "DVDcoin-Instalador" -ErrorAction Stop
    Write-Host "      ✓ Tarea verificada: $($task.TaskName)" -ForegroundColor Green
    Write-Host "      Estado: $($task.State)" -ForegroundColor Yellow
    
    Write-Host ""
    Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Green
    Write-Host "✓ CONFIGURACIÓN COMPLETADA" -ForegroundColor Green
    Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Green
    Write-Host ""
    Write-Host "Al reiniciar Windows, se ejecutará automáticamente:" -ForegroundColor Cyan
    Write-Host "  INSTALACION_AUTOMATICA_CLOUDFLARE.bat" -ForegroundColor White
    Write-Host ""
    
    exit 0
    
} catch {
    Write-Host ""
    Write-Host "✗ ERROR: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
    exit 1
}
