@echo off
cd /d "C:\DvDcoin"
:: Ejecuta con permisos de administrador si es necesario
echo [SISTEMA] Iniciando borrado verificado...
python borrar_interactivo.py
if %errorlevel% neq 0 (
    echo [ERROR] Hubo un problema con Python.
    pause
)