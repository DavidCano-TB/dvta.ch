# ============================================================================
# INSTALADOR DE SERVICIOS WINDOWS - DVDcoin Platform
# ============================================================================
# Este script crea servicios Windows dedicados para cada módulo
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
Write-Host "  INSTALADOR DE SERVICIOS WINDOWS - DVDcoin Platform" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# Configuración
$baseDir = "C:\dvdcoin"
$pythonExe = "python.exe"

# Servicios a crear
$services = @(
    @{
        Name = "DVDcoin-Bank"
        DisplayName = "DVDcoin Bank Server"
        Description = "Servidor principal del sistema bancario DVDcoin (Puerto 8000)"
        WorkingDir = "$baseDir"
        Script = "main.py"
        Port = 8000
    },
    @{
        Name = "DVDcoin-Exams"
        DisplayName = "DVDcoin Exams Server"
        Description = "Servidor de exámenes y oposiciones DVDcoin (Puerto 8001)"
        WorkingDir = "$baseDir\modules\exams"
        Script = "start_exams.py"
        Port = 8001
    },
    @{
        Name = "DVDcoin-BankPanel"
        DisplayName = "DVDcoin Bank Panel Server"
        Description = "Panel de acceso modular del Bank DVDcoin (Puerto 8002)"
        WorkingDir = "$baseDir\modules\bank"
        Script = "app_bank.py"
        Port = 8002
    },
    @{
        Name = "DVDcoin-Tunnel"
        DisplayName = "DVDcoin Cloudflare Tunnel"
        Description = "Túnel Cloudflare para acceso externo a dvta.ch"
        WorkingDir = "$baseDir"
        Script = "cloudflare-dvta-config.yml"
        Port = 0
        IsCloudflare = $true
    }
)

Write-Host "Servicios a instalar:" -ForegroundColor Yellow
foreach ($svc in $services) {
    Write-Host "  • $($svc.DisplayName)" -ForegroundColor White
}
Write-Host ""

# Función para crear wrapper de servicio
function Create-ServiceWrapper {
    param(
        [string]$ServiceName,
        [string]$WorkingDir,
        [string]$Script,
        [bool]$IsCloudflare = $false
    )
    
    $wrapperPath = "$baseDir\services\$ServiceName-wrapper.py"
    
    if ($IsCloudflare) {
        # Wrapper para Cloudflare Tunnel
        $wrapperContent = @"
import win32serviceutil
import win32service
import win32event
import servicemanager
import subprocess
import os
import sys
import time

class CloudflareTunnelService(win32serviceutil.ServiceFramework):
    _svc_name_ = '$ServiceName'
    _svc_display_name_ = '$ServiceName Service'
    _svc_description_ = 'Cloudflare Tunnel for DVDcoin Platform'
    
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
                    ['cloudflared', 'tunnel', '--config', '$Script', 'run'],
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
        servicemanager.PrepareToHostSingle(CloudflareTunnelService)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        win32serviceutil.HandleCommandLine(CloudflareTunnelService)
"@
    } else {
        # Wrapper para servidores Python
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
    _svc_display_name_ = '$ServiceName Service'
    _svc_description_ = 'DVDcoin Platform Service'
    
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
    }
    
    Set-Content -Path $wrapperPath -Value $wrapperContent -Encoding UTF8
    return $wrapperPath
}

# Crear directorio de servicios
if (-not (Test-Path "$baseDir\services")) {
    New-Item -ItemType Directory -Path "$baseDir\services" -Force | Out-Null
}

# Instalar pywin32 si no está instalado
Write-Host "[1/4] Verificando dependencias..." -ForegroundColor Yellow
try {
    & $pythonExe -c "import win32serviceutil" 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "  Instalando pywin32..." -ForegroundColor Cyan
        & $pythonExe -m pip install pywin32 --quiet
        Write-Host "  ✅ pywin32 instalado" -ForegroundColor Green
    } else {
        Write-Host "  ✅ pywin32 ya instalado" -ForegroundColor Green
    }
} catch {
    Write-Host "  ⚠️  Error verificando pywin32, continuando..." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "[2/4] Creando wrappers de servicios..." -ForegroundColor Yellow

foreach ($svc in $services) {
    Write-Host "  • Creando wrapper para $($svc.Name)..." -ForegroundColor Cyan
    $wrapperPath = Create-ServiceWrapper -ServiceName $svc.Name -WorkingDir $svc.WorkingDir -Script $svc.Script -IsCloudflare $svc.IsCloudflare
    Write-Host "    ✅ $wrapperPath" -ForegroundColor Green
}

Write-Host ""
Write-Host "[3/4] Instalando servicios Windows..." -ForegroundColor Yellow

foreach ($svc in $services) {
    Write-Host "  • Instalando $($svc.DisplayName)..." -ForegroundColor Cyan
    
    # Verificar si el servicio ya existe
    $existingService = Get-Service -Name $svc.Name -ErrorAction SilentlyContinue
    if ($existingService) {
        Write-Host "    ⚠️  Servicio ya existe, eliminando..." -ForegroundColor Yellow
        Stop-Service -Name $svc.Name -Force -ErrorAction SilentlyContinue
        & $pythonExe "$baseDir\services\$($svc.Name)-wrapper.py" remove
        Start-Sleep -Seconds 2
    }
    
    # Instalar servicio
    try {
        & $pythonExe "$baseDir\services\$($svc.Name)-wrapper.py" install
        
        # Configurar servicio
        Set-Service -Name $svc.Name -DisplayName $svc.DisplayName -Description $svc.Description -StartupType Automatic
        
        Write-Host "    ✅ Servicio instalado" -ForegroundColor Green
    } catch {
        Write-Host "    ❌ Error: $($_.Exception.Message)" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "[4/4] Iniciando servicios..." -ForegroundColor Yellow

foreach ($svc in $services) {
    Write-Host "  • Iniciando $($svc.DisplayName)..." -ForegroundColor Cyan
    try {
        Start-Service -Name $svc.Name
        Start-Sleep -Seconds 2
        
        $service = Get-Service -Name $svc.Name
        if ($service.Status -eq 'Running') {
            Write-Host "    ✅ Servicio iniciado" -ForegroundColor Green
        } else {
            Write-Host "    ⚠️  Estado: $($service.Status)" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "    ❌ Error: $($_.Exception.Message)" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  ✅ INSTALACIÓN COMPLETADA" -ForegroundColor Green
Write-Host "═══════════════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""
Write-Host "Servicios instalados:" -ForegroundColor Yellow
Get-Service -Name "DVDcoin-*" | Format-Table Name, DisplayName, Status, StartType -AutoSize
Write-Host ""
Write-Host "Los servicios se iniciarán automáticamente con Windows" -ForegroundColor Green
Write-Host ""
Write-Host "Comandos útiles:" -ForegroundColor Yellow
Write-Host "  • Ver servicios:     Get-Service -Name 'DVDcoin-*'" -ForegroundColor White
Write-Host "  • Detener servicio:  Stop-Service -Name 'DVDcoin-Bank'" -ForegroundColor White
Write-Host "  • Iniciar servicio:  Start-Service -Name 'DVDcoin-Bank'" -ForegroundColor White
Write-Host "  • Ver logs:          Get-EventLog -LogName Application -Source 'DVDcoin-*' -Newest 10" -ForegroundColor White
Write-Host ""

pause
