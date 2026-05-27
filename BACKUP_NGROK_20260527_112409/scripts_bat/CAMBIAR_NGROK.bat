@echo off
title Cambiar Configuracion de ngrok - DVDcoin Bank
cd /d "%~dp0"

echo ============================================
echo  CAMBIAR CONFIGURACION DE NGROK
echo ============================================
echo.

REM Verificar si existe el archivo de configuracion
if not exist "config\ngrok_config.txt" (
    echo [ERROR] No se encontro config\ngrok_config.txt
    echo.
    echo Creando archivo de configuracion...
    mkdir config 2>nul
    (
        echo # Configuracion de ngrok para DVDcoin Bank
        echo # Este archivo contiene el token y dominio reservado de ngrok
        echo # Formato: VARIABLE=valor ^(sin espacios alrededor del =^)
        echo.
        echo NGROK_TOKEN=
        echo NGROK_DOMAIN=
    ) > config\ngrok_config.txt
    echo [OK] Archivo creado: config\ngrok_config.txt
    echo.
)

echo Configuracion actual:
echo ----------------------------------------
type config\ngrok_config.txt
echo ----------------------------------------
echo.

echo.
echo OPCIONES:
echo   1. Editar configuracion manualmente
echo   2. Cambiar token y dominio ahora
echo   3. Solo cambiar token
echo   4. Solo cambiar dominio
echo   5. Ver documentacion
echo   6. Salir
echo.

set /p OPCION="Selecciona una opcion (1-6): "

if "%OPCION%"=="1" goto EDITAR
if "%OPCION%"=="2" goto CAMBIAR_TODO
if "%OPCION%"=="3" goto CAMBIAR_TOKEN
if "%OPCION%"=="4" goto CAMBIAR_DOMINIO
if "%OPCION%"=="5" goto DOCUMENTACION
if "%OPCION%"=="6" goto FIN

echo Opcion invalida
pause
exit /b 1

:EDITAR
echo.
echo Abriendo archivo de configuracion...
notepad config\ngrok_config.txt
echo.
echo [OK] Archivo editado
echo.
echo IMPORTANTE: Reinicia el servidor para aplicar cambios
echo   - Si esta corriendo: detenerlo (Ctrl+C) y ejecutar ARRANCAR.bat
echo   - O reinicia Windows (arranque automatico aplicara cambios)
echo.
pause
exit /b 0

:CAMBIAR_TODO
echo.
echo ============================================
echo  CAMBIAR TOKEN Y DOMINIO
echo ============================================
echo.
set /p NUEVO_TOKEN="Ingresa el nuevo token de ngrok: "
set /p NUEVO_DOMINIO="Ingresa el nuevo dominio (o deja vacio para URL aleatoria): "

if "%NUEVO_TOKEN%"=="" (
    echo [ERROR] El token no puede estar vacio
    pause
    exit /b 1
)

echo.
echo Actualizando configuracion...
(
    echo # Configuracion de ngrok para DVDcoin Bank
    echo # Este archivo contiene el token y dominio reservado de ngrok
    echo # Formato: VARIABLE=valor ^(sin espacios alrededor del =^)
    echo.
    echo NGROK_TOKEN=%NUEVO_TOKEN%
    if not "%NUEVO_DOMINIO%"=="" (
        echo NGROK_DOMAIN=%NUEVO_DOMINIO%
    ) else (
        echo # NGROK_DOMAIN=
    )
) > config\ngrok_config.txt

echo [OK] Configuracion actualizada
echo.
echo Nueva configuracion:
echo ----------------------------------------
type config\ngrok_config.txt
echo ----------------------------------------
echo.
echo IMPORTANTE: Reinicia el servidor para aplicar cambios
pause
exit /b 0

:CAMBIAR_TOKEN
echo.
echo ============================================
echo  CAMBIAR SOLO TOKEN
echo ============================================
echo.
set /p NUEVO_TOKEN="Ingresa el nuevo token de ngrok: "

if "%NUEVO_TOKEN%"=="" (
    echo [ERROR] El token no puede estar vacio
    pause
    exit /b 1
)

REM Leer dominio actual
set DOMINIO_ACTUAL=
for /f "tokens=2 delims==" %%a in ('findstr "^NGROK_DOMAIN=" config\ngrok_config.txt 2^>nul') do set DOMINIO_ACTUAL=%%a

echo.
echo Actualizando token...
(
    echo # Configuracion de ngrok para DVDcoin Bank
    echo # Este archivo contiene el token y dominio reservado de ngrok
    echo # Formato: VARIABLE=valor ^(sin espacios alrededor del =^)
    echo.
    echo NGROK_TOKEN=%NUEVO_TOKEN%
    if not "%DOMINIO_ACTUAL%"=="" (
        echo NGROK_DOMAIN=%DOMINIO_ACTUAL%
    ) else (
        echo # NGROK_DOMAIN=
    )
) > config\ngrok_config.txt

echo [OK] Token actualizado
echo.
echo Nueva configuracion:
echo ----------------------------------------
type config\ngrok_config.txt
echo ----------------------------------------
echo.
echo IMPORTANTE: Reinicia el servidor para aplicar cambios
pause
exit /b 0

:CAMBIAR_DOMINIO
echo.
echo ============================================
echo  CAMBIAR SOLO DOMINIO
echo ============================================
echo.
set /p NUEVO_DOMINIO="Ingresa el nuevo dominio (o deja vacio para URL aleatoria): "

REM Leer token actual
set TOKEN_ACTUAL=
for /f "tokens=2 delims==" %%a in ('findstr "^NGROK_TOKEN=" config\ngrok_config.txt 2^>nul') do set TOKEN_ACTUAL=%%a

if "%TOKEN_ACTUAL%"=="" (
    echo [ERROR] No se encontro token actual en la configuracion
    pause
    exit /b 1
)

echo.
echo Actualizando dominio...
(
    echo # Configuracion de ngrok para DVDcoin Bank
    echo # Este archivo contiene el token y dominio reservado de ngrok
    echo # Formato: VARIABLE=valor ^(sin espacios alrededor del =^)
    echo.
    echo NGROK_TOKEN=%TOKEN_ACTUAL%
    if not "%NUEVO_DOMINIO%"=="" (
        echo NGROK_DOMAIN=%NUEVO_DOMINIO%
    ) else (
        echo # NGROK_DOMAIN=
    )
) > config\ngrok_config.txt

echo [OK] Dominio actualizado
echo.
echo Nueva configuracion:
echo ----------------------------------------
type config\ngrok_config.txt
echo ----------------------------------------
echo.
echo IMPORTANTE: Reinicia el servidor para aplicar cambios
pause
exit /b 0

:DOCUMENTACION
echo.
echo Abriendo documentacion...
if exist "config\README_NGROK_CONFIG.md" (
    notepad config\README_NGROK_CONFIG.md
) else (
    echo [ERROR] No se encontro la documentacion
    echo Busca: config\README_NGROK_CONFIG.md
)
pause
exit /b 0

:FIN
echo.
echo Saliendo...
exit /b 0
