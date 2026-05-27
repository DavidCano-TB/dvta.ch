@echo off
:: Ejecuta el script PowerShell como administrador
powershell -Command "Start-Process powershell -ArgumentList '-ExecutionPolicy Bypass -File \"%~dp0MATAR_PROCESO_ADMIN.ps1\"' -Verb RunAs"
