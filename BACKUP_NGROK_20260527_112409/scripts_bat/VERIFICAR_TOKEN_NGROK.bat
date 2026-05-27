@echo off
REM ============================================================
REM VERIFICAR INTEGRIDAD DEL ARCHIVO DE TOKEN DE NGROK
REM ============================================================

echo ============================================================
echo VERIFICACION DEL ARCHIVO DE TOKEN DE NGROK
echo ============================================================
echo.

if not exist "conf\.ngrok_token" (
    echo [ERROR] El archivo conf\.ngrok_token no existe
    echo.
    echo Debes crear el archivo con tu token de ngrok.
    echo.
    goto :end
)

echo [OK] Archivo conf\.ngrok_token existe
echo.

REM Contar líneas del archivo
set LINE_COUNT=0
for /f %%a in ('type "conf\.ngrok_token" ^| find /c /v ""') do set LINE_COUNT=%%a

echo Numero de lineas en el archivo: %LINE_COUNT%
echo.

REM Verificar contenido
echo Contenido del archivo:
echo ----------------------------------------
type "conf\.ngrok_token"
echo ----------------------------------------
echo.

REM Verificar si hay líneas problemáticas
findstr /C:"NGROK_URL=" "conf\.ngrok_token" >nul 2>&1
if not errorlevel 1 (
    echo [ADVERTENCIA] El archivo contiene lineas NGROK_URL=
    echo Estas lineas NO deben estar en el archivo de token.
    echo.
    echo El archivo debe contener SOLO:
    echo   - El token de ngrok (una linea), o
    echo   - NGROK_TOKEN=... y NGROK_DOMAIN=... (dos lineas)
    echo.
    echo Las URLs temporales se guardan en: ngrok_url.txt
    echo.
    set /p LIMPIAR="Deseas limpiar el archivo? (S/N): "
    if /i "%LIMPIAR%"=="S" goto :limpiar
    goto :end
)

REM Verificar formato correcto
findstr /C:"NGROK_TOKEN=" "conf\.ngrok_token" >nul 2>&1
if not errorlevel 1 (
    echo [OK] Formato con variables detectado
    echo.
    findstr /C:"NGROK_DOMAIN=" "conf\.ngrok_token" >nul 2>&1
    if not errorlevel 1 (
        echo [OK] Token y dominio configurados
    ) else (
        echo [INFO] Solo token configurado (sin dominio personalizado)
    )
) else (
    if %LINE_COUNT%==1 (
        echo [OK] Formato simple detectado (solo token)
    ) else (
        echo [ADVERTENCIA] Formato no reconocido
        echo.
        echo El archivo debe tener:
        echo   - 1 linea: solo el token
        echo   - 2 lineas: NGROK_TOKEN=... y NGROK_DOMAIN=...
        echo.
    )
)

echo.
echo ============================================================
echo VERIFICACION COMPLETADA
echo ============================================================
echo.
goto :end

:limpiar
echo.
echo ============================================================
echo LIMPIANDO ARCHIVO
echo ============================================================
echo.

REM Crear backup
copy "conf\.ngrok_token" "conf\.ngrok_token.backup" >nul 2>&1
echo [OK] Backup creado: conf\.ngrok_token.backup

REM Leer solo las líneas válidas
set NGROK_TOKEN=
set NGROK_DOMAIN=

for /f "tokens=1,2 delims==" %%a in (conf\.ngrok_token) do (
    if "%%a"=="NGROK_TOKEN" set NGROK_TOKEN=%%b
    if "%%a"=="NGROK_DOMAIN" set NGROK_DOMAIN=%%b
)

REM Si no se encontró formato con variables, leer la primera línea como token
if "%NGROK_TOKEN%"=="" (
    for /f "delims=" %%a in (conf\.ngrok_token) do (
        if not defined NGROK_TOKEN set NGROK_TOKEN=%%a
    )
)

REM Reescribir archivo limpio
if not "%NGROK_TOKEN%"=="" (
    if not "%NGROK_DOMAIN%"=="" (
        (
            echo NGROK_TOKEN=%NGROK_TOKEN%
            echo NGROK_DOMAIN=%NGROK_DOMAIN%
        ) > "conf\.ngrok_token"
        echo [OK] Archivo limpiado con token y dominio
    ) else (
        echo %NGROK_TOKEN% > "conf\.ngrok_token"
        echo [OK] Archivo limpiado con solo token
    )
    echo.
    echo Nuevo contenido:
    echo ----------------------------------------
    type "conf\.ngrok_token"
    echo ----------------------------------------
) else (
    echo [ERROR] No se pudo leer el token del archivo
    echo Restaurando backup...
    copy "conf\.ngrok_token.backup" "conf\.ngrok_token" >nul 2>&1
)

echo.
echo ============================================================
echo LIMPIEZA COMPLETADA
echo ============================================================
echo.

:end
pause
