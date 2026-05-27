# Script para matar procesos bloqueados con privilegios de administrador
Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host " MATANDO PROCESOS BLOQUEADOS" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# Matar proceso Python en puerto 8000
Write-Host "[1/2] Matando proceso Python (PID 10764)..." -ForegroundColor Yellow
try {
    Stop-Process -Id 10764 -Force -ErrorAction Stop
    Write-Host "✅ Proceso Python eliminado" -ForegroundColor Green
} catch {
    Write-Host "⚠ Error: $_" -ForegroundColor Yellow
    Write-Host "Intentando con taskkill..." -ForegroundColor Yellow
    taskkill /F /PID 10764 2>$null
}

Start-Sleep -Seconds 1

# Matar proceso Cloudflare
Write-Host ""
Write-Host "[2/2] Matando proceso Cloudflare (PID 6788)..." -ForegroundColor Yellow
try {
    Stop-Process -Id 6788 -Force -ErrorAction Stop
    Write-Host "✅ Proceso Cloudflare eliminado" -ForegroundColor Green
} catch {
    Write-Host "⚠ Error: $_" -ForegroundColor Yellow
    Write-Host "Intentando con taskkill..." -ForegroundColor Yellow
    taskkill /F /PID 6788 2>$null
}

Start-Sleep -Seconds 2

Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host " VERIFICACIÓN" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

Write-Host "Puerto 8000:" -ForegroundColor Yellow
$port8000 = netstat -ano | findstr ":8000" | findstr "LISTENING"
if ($port8000) {
    Write-Host "❌ Puerto 8000 aún ocupado" -ForegroundColor Red
    Write-Host $port8000
} else {
    Write-Host "✅ Puerto 8000 liberado" -ForegroundColor Green
}

Write-Host ""
Write-Host "Procesos Cloudflare:" -ForegroundColor Yellow
$cf = tasklist | findstr "cloudflared"
if ($cf) {
    Write-Host "⚠ Cloudflare aún corriendo" -ForegroundColor Yellow
    Write-Host $cf
} else {
    Write-Host "✅ Cloudflare detenido" -ForegroundColor Green
}

Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host " SIGUIENTE PASO" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""
Write-Host "Ejecuta ahora: REINICIAR_SERVIDOR_FORZADO.bat" -ForegroundColor Green
Write-Host ""
Write-Host "Presiona cualquier tecla para continuar..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
