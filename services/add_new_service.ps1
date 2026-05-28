# ============================================================================
# AÑADIR NUEVO SERVICIO - DVDcoin Platform
# ============================================================================
# Script para añadir un nuevo servicio Windows para una nueva funcionalidad
# ============================================================================

param(
    [Parameter(Mandatory=$true)]
    [string]$ServiceName,
    
    [Parameter(Mandatory=$true)]
    [string]$DisplayName,
    
    [Parameter(Mandatory=$true)]
    [string]$Description,
    
    [Parameter(Mandatory=$true)]
    [string]$WorkingDir,
    
    [Parameter(Mandatory=$true)]
    [string]$Script,
    
    [Parameter(Mandatory=$true)]
    [int]$Port
)

# Verificar privilegios de administrador
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "ERROR: Este script requiere privilegios de administrador" -ForegroundColor Red
    exit 1
}

Write-Host "═══════════════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  AÑADIR NUEVO SERVICIO - DVDcoin Platform" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

$baseDir = Split-Path -Parent $PSScriptRoot
$pythonExe = "python.exe"

Write-Host "Configuración del nuevo servicio:" -ForegroundColor Yellow
Write-Host "  • Nombre: $ServiceName" -ForegroundColor White
Write-Host "  • Nombre completo: $DisplayName" -ForegroundColor White
Write-Host "  • Descripción: $Description" -ForegroundColor White
Write-Host "  • Directorio: $WorkingDir" -ForegroundColor White
Write-Host "  • Script: $Script" -ForegroundColor White
Write-Host "  • Puerto: $Port" -ForegroundColor White
Write-Host ""

$confirm = Read-Host "¿Continuar con la instalación? (S/N)"
if ($confirm -ne 'S' -and $confirm -ne 's') {
    Write-Host "Operación cancelada" -ForegroundColor Yellow
    exit 0
}

# Crear wrapper
Write-Host ""
Write-Host "[1/3] Creando wrapper del servicio..." -ForegroundColor Yellow

$wrapperPath = "$baseDir\services\$ServiceName-wrapper.py"
$wrapperContent = @"
import win32serviceutil
import win32service
import win32event
import servicemanager
import subprocess
import os
import sys
import time

class DVDcoinService(win32serviceutil.ServiceFramework):
    _svc_name_ = '$ServiceName'
    _svc_display_name_ = '$DisplayName'
    _svc_description_ = '$Description'
    
    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.stop_event = win32event.CreateEvent(None, 0, 0, None)
        self.process = None
        
    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.stop_event)
        if self.process:
            self.process.terminate()
            self.process.wait()
        
    def SvcDoRun(self):
        servicemanager.LogMsg(
            servicemanager.EVENTLOG_INFORMATION_TYPE,
            servicemanager.PYS_SERVICE_STARTED,
            (self._svc_name_, '')
        )
        self.main()
        
    def main(self):
        os.chdir('$WorkingDir')
        
        while True:
            if win32event.WaitForSingleObject(self.stop_event, 0) == win32event.WAIT_OBJECT_0:
                break
                
            try:
                self.process = subprocess.Popen(
                    [sys.executable, '$Script'],
                    cwd='$WorkingDir',
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                
                while True:
                    if win32event.WaitForSingleObject(self.stop_event, 1000) == win32event.WAIT_OBJECT_0:
                        break
                    
                    if self.process.poll() is not None:
                        servicemanager.LogErrorMsg(f'{self._svc_name_} process died, restarting...')
                        time.sleep(5)
                        break
                        
            except Exception as e:
                servicemanager.LogErrorMsg(f'{self._svc_name_} error: {str(e)}')
                time.sleep(10)

if __name__ == '__main__':
    if len(sys.argv) == 1:
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(DVDcoinService)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        win32serviceutil.HandleCommandLine(DVDcoinService)
"@

Set-Content -Path $wrapperPath -Value $wrapperContent -Encoding UTF8
Write-Host "  ✅ Wrapper creado: $wrapperPath" -ForegroundColor Green

# Instalar servicio
Write-Host ""
Write-Host "[2/3] Instalando servicio Windows..." -ForegroundColor Yellow

try {
    & $pythonExe $wrapperPath install
    Set-Service -Name $ServiceName -DisplayName $DisplayName -Description $Description -StartupType Automatic
    Write-Host "  ✅ Servicio instalado" -ForegroundColor Green
} catch {
    Write-Host "  ❌ Error: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Iniciar servicio
Write-Host ""
Write-Host "[3/3] Iniciando servicio..." -ForegroundColor Yellow

try {
    Start-Service -Name $ServiceName
    Start-Sleep -Seconds 2
    
    $service = Get-Service -Name $ServiceName
    if ($service.Status -eq 'Running') {
        Write-Host "  ✅ Servicio iniciado" -ForegroundColor Green
    } else {
        Write-Host "  ⚠️  Estado: $($service.Status)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "  ❌ Error: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  ✅ SERVICIO AÑADIDO CORRECTAMENTE" -ForegroundColor Green
Write-Host "═══════════════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""
Write-Host "El servicio '$DisplayName' está ahora instalado y corriendo" -ForegroundColor Green
Write-Host "Se iniciará automáticamente con Windows" -ForegroundColor Green
Write-Host ""
Write-Host "Para gestionar el servicio:" -ForegroundColor Yellow
Write-Host "  • Ejecuta: GESTIONAR_SERVICIOS.bat" -ForegroundColor White
Write-Host "  • O usa: services.msc" -ForegroundColor White
Write-Host ""
