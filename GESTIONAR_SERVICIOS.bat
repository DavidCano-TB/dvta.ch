@echo off
chcp 65001 >nul
title Gestionar Servicios Windows - DVDcoin
color 0A

cd /d "%~dp0"

powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0services\manage_services.ps1"
