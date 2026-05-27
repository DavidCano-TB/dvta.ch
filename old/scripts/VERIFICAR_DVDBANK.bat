@echo off
chcp 65001 >nul
title 🔍 Verificar dvdbank.ch
color 0B

echo.
echo ═══════════════════════════════════════════════════════════
echo   🔍 VERIFICANDO dvdbank.ch
echo ═══════════════════════════════════════════════════════════
echo.

cd /d "%~dp0"

echo 1. Verificando DNS de dvdbank.ch...
echo.
nslookup dvdbank.ch
echo.

echo ═══════════════════════════════════════════════════════════
echo.
echo 2. Verificando servidor Python...
echo.
netstat -ano | findstr ":8000"
echo.

echo ═══════════════════════════════════════════════════════════
echo.
echo 3. Verificando túnel Cloudflare...
echo.
tasklist | findstr cloudflared.exe
echo.

echo ═══════════════════════════════════════════════════════════
echo   📋 INTERPRETACIÓN
echo ═══════════════════════════════════════════════════════════
echo.
echo DNS:
echo   ✅ Si ves una IP de Cloudflare → DNS configurado
echo   ❌ Si no ves IP o error → DNS no propagado aún
echo.
echo Servidor:
echo   ✅ Si ves "LISTENING 8000" → Servidor corriendo
echo   ❌ Si no ves nada → Servidor no está corriendo
echo.
echo Túnel:
echo   ✅ Si ves "cloudflared.exe" → Túnel activo
echo   ❌ Si no ves nada → Túnel no está corriendo
echo.
echo ═══════════════════════════════════════════════════════════
echo.
pause
