@echo off
chcp 65001 >nul
cd /d "%~dp0"

cls
echo.
echo ═══════════════════════════════════════════════════════════════
echo  CONFIGURACIÓN AUTOMÁTICA COMPLETA
echo ═══════════════════════════════════════════════════════════════
echo.
echo  Este script configurará los secrets de GitHub automáticamente.
echo.
echo  Necesitas 2 cosas:
echo  1. Token de GitHub (se creará ahora)
echo  2. Contraseña de aplicación de Gmail (se creará ahora)
echo.
pause

REM Abrir páginas
echo.
echo Abriendo páginas necesarias...
start "https://github.com/settings/tokens/new?scopes=repo,workflow&description=DVDBank"
timeout /t 2 /nobreak >nul
start "https://myaccount.google.com/apppasswords"
timeout /t 2 /nobreak >nul

echo.
echo ═══════════════════════════════════════════════════════════════
echo  INSTRUCCIONES:
echo ═══════════════════════════════════════════════════════════════
echo.
echo  PÁGINA 1 - GitHub Token:
echo  1. Haz clic en "Generate token" (botón verde abajo)
echo  2. Copia el token que aparece (empieza con ghp_...)
echo.
echo  PÁGINA 2 - Gmail App Password:
echo  1. Si no tienes verificación en 2 pasos, actívala primero
echo  2. Selecciona "Correo" y "Otro (nombre personalizado)"
echo  3. Escribe: DVDBank
echo  4. Haz clic en "Generar"
echo  5. Copia la contraseña (16 caracteres, quita los espacios)
echo.
echo ═══════════════════════════════════════════════════════════════
echo.
pause

REM Pedir token de GitHub
echo.
echo Pega el token de GitHub (ghp_...):
set /p GITHUB_TOKEN=
if "%GITHUB_TOKEN%"=="" (
    echo Error: Token vacío
    pause
    exit /b 1
)

REM Pedir contraseña de Gmail
echo.
echo Pega la contraseña de Gmail (16 caracteres sin espacios):
set /p GMAIL_PASSWORD=
if "%GMAIL_PASSWORD%"=="" (
    echo Error: Contraseña vacía
    pause
    exit /b 1
)

REM Configurar secrets
echo.
echo Configurando secrets en GitHub...
python configurar_secrets_auto.py "%GITHUB_TOKEN%" "%GMAIL_PASSWORD%"

if errorlevel 1 (
    echo.
    echo ❌ Error configurando secrets
    pause
    exit /b 1
)

REM Hacer push para probar
echo.
echo ═══════════════════════════════════════════════════════════════
echo  ✅ SECRETS CONFIGURADOS
echo ═══════════════════════════════════════════════════════════════
echo.
echo  Haciendo push para probar el sistema...
echo.

git add .
git commit -m "Test deploy con email configurado" 2>nul
git push origin master

echo.
echo ═══════════════════════════════════════════════════════════════
echo  ✅ SISTEMA COMPLETAMENTE CONFIGURADO
echo ═══════════════════════════════════════════════════════════════
echo.
echo  En 2-3 minutos recibirás un email en:
echo  davidcano.ch@gmail.com
echo.
echo  El email incluirá:
echo  - Detalles del commit
echo  - Estado del deploy (éxito o fallo)
echo  - Enlaces al código
echo.
echo  A partir de ahora, cada vez que hagas push recibirás un email.
echo.
echo ═══════════════════════════════════════════════════════════════
echo.
pause
