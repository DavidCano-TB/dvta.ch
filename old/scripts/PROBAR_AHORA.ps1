# Test all URLs
Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  🌐 PROBANDO TODAS LAS URLs" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# Test localhost
Write-Host "1. localhost:8000..." -ForegroundColor Yellow
try {
    $r = Invoke-WebRequest -Uri 'http://127.0.0.1:8000' -Method Get -TimeoutSec 5 -UseBasicParsing
    Write-Host "   ✅ Status: $($r.StatusCode) - Size: $($r.Content.Length) bytes" -ForegroundColor Green
} catch {
    Write-Host "   ❌ Error: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# Test dvdbank.david.ch
Write-Host "2. dvdbank.david.ch..." -ForegroundColor Yellow
try {
    $r = Invoke-WebRequest -Uri 'https://dvdbank.david.ch' -Method Get -TimeoutSec 10 -UseBasicParsing
    Write-Host "   ✅ Status: $($r.StatusCode) - Size: $($r.Content.Length) bytes" -ForegroundColor Green
} catch {
    Write-Host "   ❌ Error: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# Test app.david.ch
Write-Host "3. app.david.ch..." -ForegroundColor Yellow
try {
    $r = Invoke-WebRequest -Uri 'https://app.david.ch' -Method Get -TimeoutSec 10 -UseBasicParsing
    Write-Host "   ✅ Status: $($r.StatusCode) - Size: $($r.Content.Length) bytes" -ForegroundColor Green
} catch {
    Write-Host "   ❌ Error: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# Test localhost.david.ch
Write-Host "4. localhost.david.ch..." -ForegroundColor Yellow
try {
    $r = Invoke-WebRequest -Uri 'https://localhost.david.ch' -Method Get -TimeoutSec 10 -UseBasicParsing
    Write-Host "   ✅ Status: $($r.StatusCode) - Size: $($r.Content.Length) bytes" -ForegroundColor Green
} catch {
    Write-Host "   ❌ Error: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""
