@echo off
chcp 65001 >nul
cd /d "%~dp0"
python VERIFICAR_CONFIGURACION.py
pause
