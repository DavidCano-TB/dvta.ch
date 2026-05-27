@echo off
title Cloudflare Tunnel - DVDcoin
cd /d c:\dvdcoin

echo.
echo ============================================================
echo CLOUDFLARE TUNNEL - DVDCOIN
echo ============================================================
echo.
echo Iniciando tunel en http://localhost:8000
echo.

cloudflared tunnel --url http://localhost:8000

pause
