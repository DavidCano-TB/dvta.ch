@echo off
chcp 65001 >nul
cd /d "%~dp0"

cls
echo.
echo ═══════════════════════════════════════════════════════════════
echo  CONFIGURACIÓN RÁPIDA - 2 PASOS
echo ═══════════════════════════════════════════════════════════════
echo.
echo  Se abrirán 2 páginas. Copia los valores y pégalos aquí.
echo.
pause

REM Abrir páginas
start https://myaccount.google.com/apppasswords
timeout /t 2 /nobreak >nul
start https://github.com/settings/tokens/new?scopes=repo,workflow^&description=DVDBank

echo.
echo ═══════════════════════════════════════════════════════════════
echo  PASO 1: GitHub Token
echo ═══════════════════════════════════════════════════════════════
echo.
echo  En la página de GitHub que se abrió:
echo  1. Haz clic en "Generate token" (abajo)
echo  2. Copia el token que aparece
echo  3. Pégalo aquí:
echo.
set /p GITHUB_TOKEN="Token de GitHub: "

echo.
echo ═══════════════════════════════════════════════════════════════
echo  PASO 2: Gmail App Password
echo ═══════════════════════════════════════════════════════════════
echo.
echo  En la página de Gmail que se abrió:
echo  1. Selecciona "Correo" y "Otro (nombre personalizado)"
echo  2. Escribe: GitHub DVDBank
echo  3. Haz clic en "Generar"
echo  4. Copia la contraseña (16 caracteres, sin espacios)
echo  5. Pégala aquí:
echo.
set /p GMAIL_PASSWORD="Contraseña de Gmail: "

echo.
echo Configurando secrets...
python configurar_secrets_auto.py "%GITHUB_TOKEN%" "%GMAIL_PASSWORD%"

if errorlevel 1 (
    echo.
    echo Error configurando secrets.
    pause
    exit /b 1
)

echo.
echo ═══════════════════════════════════════════════════════════════
echo  ✅ CONFIGURACIÓN COMPLETADA
echo ═══════════════════════════════════════════════════════════════
echo.
echo  Haciendo push para probar...
echo.

git add .
git commit -m "Configurar deploy automático" 2>nul
git push origin master

echo.
echo  Revisa tu email en 2-3 minutos: davidcano.ch@gmail.com
echo.
pause
