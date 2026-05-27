@echo off
title Configurar Claude (Anthropic) API Key
cd /d "%~dp0"

echo.
echo ============================================================
echo   CONFIGURAR CLAUDE (ANTHROPIC) API KEY
echo ============================================================
echo.
echo Este script configurara la API key de Claude/Anthropic
echo para que la IA funcione correctamente en DVDBank.
echo.
echo ============================================================
echo   PASO 1: OBTENER TU API KEY
echo ============================================================
echo.
echo 1. Ve a: https://console.anthropic.com/
echo 2. Inicia sesion o crea una cuenta
echo 3. Ve a "API Keys" en el menu lateral
echo 4. Haz clic en "Create Key"
echo 5. Copia la clave (empieza con sk-ant-api03-...)
echo.
echo IMPORTANTE: Necesitas anadir creditos (minimo $5 USD)
echo en: https://console.anthropic.com/settings/billing
echo.
echo ============================================================
echo.

set /p API_KEY="Pega tu API Key aqui: "

if "%API_KEY%"=="" (
    echo.
    echo ERROR: No ingresaste ninguna API key
    echo.
    pause
    exit /b 1
)

REM Verificar formato básico
echo %API_KEY% | findstr /C:"sk-ant-" >nul
if errorlevel 1 (
    echo.
    echo ADVERTENCIA: La API key no parece tener el formato correcto
    echo Deberia empezar con: sk-ant-api03-...
    echo.
    set /p CONTINUE="Continuar de todas formas? (S/N): "
    if /i not "%CONTINUE%"=="S" (
        echo Operacion cancelada.
        pause
        exit /b 1
    )
)

echo.
echo ============================================================
echo   GUARDANDO API KEY
echo ============================================================
echo.

REM Crear carpeta config si no existe
if not exist "config" mkdir config

REM Guardar en config/.groq_key (nombre usado por el código)
echo %API_KEY%> config\.groq_key
echo [OK] Guardada en: config\.groq_key

REM También guardar en config/.anthropic_key (por compatibilidad)
echo %API_KEY%> config\.anthropic_key
echo [OK] Guardada en: config\.anthropic_key

REM Configurar variable de entorno
setx ANTHROPIC_API_KEY "%API_KEY%" >nul 2>&1
if errorlevel 1 (
    echo [WARN] No se pudo configurar variable de entorno del sistema
) else (
    echo [OK] Variable de entorno configurada
)

echo.
echo ============================================================
echo   VERIFICANDO CONFIGURACION
echo ============================================================
echo.

REM Ejecutar test si existe Python
where python >nul 2>&1
if not errorlevel 1 (
    echo Ejecutando test de API...
    echo.
    python test_ai_simple.py
) else (
    echo Python no encontrado. Saltando test automatico.
    echo.
    echo Para verificar manualmente:
    echo 1. Ejecuta: ARRANCAR.bat
    echo 2. Ve a: http://localhost:8000/quiensoy.html
    echo 3. Inicia un juego y haz una pregunta
)

echo.
echo ============================================================
echo   CONFIGURACION COMPLETADA
echo ============================================================
echo.
echo La API key ha sido guardada correctamente.
echo.
echo PROXIMOS PASOS:
echo   1. REINICIA el servidor si estaba corriendo
echo   2. Ejecuta: ARRANCAR.bat
echo   3. Prueba el juego "Quien Soy" con IA
echo.
echo DOCUMENTACION COMPLETA:
echo   Ver: GUIA_CONFIGURAR_CLAUDE_API.md
echo.
echo SOPORTE:
echo   - Docs: https://docs.anthropic.com/
echo   - Console: https://console.anthropic.com/
echo.
pause
