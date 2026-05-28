@echo off
chcp 65001 >nul
title SETUP - DVDcoin Platform
color 0E

echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo   🔧 SETUP INICIAL - DVDcoin Platform (dvta.ch)
echo ═══════════════════════════════════════════════════════════════════════════
echo.
echo   Este script configura un PC nuevo para ejecutar la plataforma.
echo   Solo necesitas ejecutarlo UNA VEZ por PC.
echo.
echo   Requisitos previos:
echo     - Python 3.11+ instalado y en PATH
echo     - Git instalado
echo     - cloudflared.exe en PATH o en este directorio
echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo.
pause

cd /d "%~dp0"

echo.
echo [1/5] Instalando dependencias Python...
echo.
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ❌ Error instalando dependencias
    pause
    exit /b 1
)
echo ✅ Dependencias instaladas
echo.

echo [2/5] Creando directorios necesarios...
if not exist "data" mkdir data
if not exist "config" mkdir config
if not exist "credentials" mkdir credentials
if not exist "modules\exams\data" mkdir modules\exams\data
if not exist "modules\exams\config" mkdir modules\exams\config
if not exist "modules\bank\data" mkdir modules\bank\data
if not exist "modules\bank\config" mkdir modules\bank\config
echo ✅ Directorios creados
echo.

echo [3/5] Configurando Cloudflare Tunnel...
echo.
echo   El túnel de Cloudflare conecta este PC con dvta.ch.
echo   Si ya tienes las credenciales (credentials/*.json), puedes saltar este paso.
echo.

if exist "credentials\b75039b1-7b54-4da0-b2ab-0a338bfccdc5.json" (
    echo ✅ Credenciales del túnel ya existen. Saltando...
) else (
    echo   No se encontraron credenciales del túnel.
    echo.
    echo   OPCIÓN A: Si tienes acceso a la cuenta Cloudflare de dvta.ch:
    echo     1. Ejecuta: cloudflared tunnel login
    echo     2. Copia el archivo .json generado a: credentials\
    echo.
    echo   OPCIÓN B: Copia el archivo de credenciales desde el PC original:
    echo     Desde: C:\Users\PC\.cloudflared\b75039b1-7b54-4da0-b2ab-0a338bfccdc5.json
    echo     Hacia: credentials\b75039b1-7b54-4da0-b2ab-0a338bfccdc5.json
    echo.
    echo   ⚠️  Sin este archivo, el túnel NO funcionará y dvta.ch no será accesible.
    echo.
)

echo [4/5] Verificando que los servidores arrancan...
echo.
python -c "import fastapi; print('FastAPI OK:', fastapi.__version__)"
python -c "import uvicorn; print('Uvicorn OK:', uvicorn.__version__)"
python -c "import httpx; print('httpx OK:', httpx.__version__)"
python -c "import bcrypt; print('bcrypt OK')"
python -c "import websockets; print('websockets OK:', websockets.__version__)"
echo.
echo ✅ Todas las dependencias verificadas
echo.

echo [5/5] Verificando sintaxis del código...
python -m py_compile main.py
python -m py_compile modules\exams\app_exams.py
python -m py_compile modules\bank\app_bank.py
echo ✅ Código sin errores de sintaxis
echo.

echo ═══════════════════════════════════════════════════════════════════════════
echo   ✅ SETUP COMPLETADO
echo ═══════════════════════════════════════════════════════════════════════════
echo.
echo   Para arrancar todo:
echo     ARRANCAR_TODO_PARALELO.bat
echo.
echo   Servicios:
echo     Puerto 8000 → Bank principal (main.py)
echo     Puerto 8001 → Exams + OPO (modules/exams/app_exams.py)
echo     Puerto 8002 → Bank Proxy (modules/bank/app_bank.py)
echo.
echo   URLs (requiere túnel Cloudflare activo):
echo     https://dvta.ch/       → Página principal
echo     https://dvta.ch/opo    → Tests OPO
echo     https://dvta.ch/bank   → Bank completo
echo     https://bank.dvta.ch/  → Bank directo
echo.
echo   Para desplegar cambios desde otro PC:
echo     1. Haz cambios y push a GitHub
echo     2. En este PC: git pull
echo     3. Reinicia: ARRANCAR_TODO_PARALELO.bat
echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo.
pause
