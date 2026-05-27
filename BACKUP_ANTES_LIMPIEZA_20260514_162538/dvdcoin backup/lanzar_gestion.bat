@echo off
title DVDcoin - Gestion de Usuarios
cd /d "C:\DvDcoin"

:: Activar venv para tener bcrypt disponible
if exist "venv\Scripts\activate.bat" (
    call "venv\Scripts\activate.bat"
)

echo [SISTEMA] Abriendo panel de gestion...
python gestion_usuarios.py

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Hubo un problema. Asegurate de tener 'bcrypt' instalado.
    echo Ejecuta: pip install bcrypt
    pause
)