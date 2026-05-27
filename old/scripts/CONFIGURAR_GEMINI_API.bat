@echo off
title Configurar Google Gemini API Key
cd /d "%~dp0"

echo.
echo ============================================================
echo   CONFIGURAR GOOGLE GEMINI API KEY
echo ============================================================
echo.
echo Este script configurara la API key de Google Gemini
echo para que la IA funcione correctamente en DVDBank.
echo.
echo ============================================================
echo   PASO 1: OBTENER TU API KEY
echo ============================================================
echo.
echo 1. Ve a: https://aistudio.google.com/apikey
echo 2. Inicia sesion con tu cuenta de Google
echo 3. Haz clic en "Create API Key"
echo 4. Selecciona un proyecto o crea uno nuevo
echo 5. Copia la clave (empieza con AIza...)
echo.
echo IMPORTANTE: Gemini tiene un tier gratuito generoso
echo Mas info: https://ai.google.dev/pricing
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
echo %API_KEY% | findstr /C:"AIza" >nul
if errorlevel 1 (
    echo.
    echo ADVERTENCIA: La API key no parece tener el formato correcto
    echo Deberia empezar con: AIza...
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

REM Guardar en config/.gemini_key (nombre usado por el código)
echo %API_KEY%> config\.gemini_key
echo [OK] Guardada en: config\.gemini_key

REM También guardar en config/.google_key (por compatibilidad)
echo %API_KEY%> config\.google_key
echo [OK] Guardada en: config\.google_key

REM Configurar variable de entorno
setx GEMINI_API_KEY "%API_KEY%" >nul 2>&1
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
    
    REM Crear test simple inline
    python -c "from ai_helper import get_gemini; ai = get_gemini(); print('✅ Gemini configurado correctamente' if ai.api_key else '❌ No se pudo cargar la API key')"
    
    if errorlevel 1 (
        echo.
        echo ⚠️  Hubo un problema al verificar la configuracion
        echo    Pero la API key fue guardada correctamente.
    )
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
echo   Ver: GUIA_CONFIGURAR_GEMINI_API.md
echo.
echo SOPORTE:
echo   - Docs: https://ai.google.dev/docs
echo   - API Keys: https://aistudio.google.com/apikey
echo.
pause
