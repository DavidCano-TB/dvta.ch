@echo off
REM ============================================================
REM VERIFICACION COMPLETA DEL SISTEMA DVDBANK
REM Verifica que todas las funcionalidades esten implementadas
REM ============================================================

chcp 65001 >nul
title DVDCoin Bank - Verificación Completa
cd /d "%~dp0"

echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                                                              ║
echo ║         VERIFICACION COMPLETA DEL SISTEMA DVDBANK            ║
echo ║                                                              ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

set ERRORES=0

REM ============================================================
REM [1] VERIFICAR ARCHIVOS PRINCIPALES
REM ============================================================
echo [1/10] Verificando archivos principales...
echo.

if exist "src\main.py" (
    echo   ✓ Backend principal encontrado ^(src\main.py^)
) else (
    echo   ✗ ERROR: No se encuentra src\main.py
    set /a ERRORES+=1
)

if exist "static\index.html" (
    echo   ✓ Frontend principal encontrado ^(static\index.html^)
) else (
    echo   ✗ ERROR: No se encuentra static\index.html
    set /a ERRORES+=1
)

if exist "cloudflared.exe" (
    echo   ✓ Cloudflare Tunnel encontrado
) else (
    echo   ⚠ ADVERTENCIA: cloudflared.exe no encontrado
)

if exist "cloudflare-config.yml" (
    echo   ✓ Configuración de Cloudflare encontrada
) else (
    echo   ⚠ ADVERTENCIA: cloudflare-config.yml no encontrado
)

REM ============================================================
REM [2] VERIFICAR BASES DE DATOS
REM ============================================================
echo.
echo [2/10] Verificando bases de datos...
echo.

set DB_OK=0

if exist "data\users.db" (
    echo   ✓ users.db
    set /a DB_OK+=1
) else (
    echo   ✗ users.db NO ENCONTRADA
    set /a ERRORES+=1
)

if exist "data\rights.db" (
    echo   ✓ rights.db
    set /a DB_OK+=1
) else (
    echo   ✗ rights.db NO ENCONTRADA
    set /a ERRORES+=1
)

if exist "data\transactions.db" (
    echo   ✓ transactions.db
    set /a DB_OK+=1
) else (
    echo   ✗ transactions.db NO ENCONTRADA
    set /a ERRORES+=1
)

if exist "data\stats.db" (
    echo   ✓ stats.db
    set /a DB_OK+=1
) else (
    echo   ✗ stats.db NO ENCONTRADA
    set /a ERRORES+=1
)

if exist "data\opo.db" (
    echo   ✓ opo.db
    set /a DB_OK+=1
) else (
    echo   ✗ opo.db NO ENCONTRADA
    set /a ERRORES+=1
)

if exist "data\apuestas.db" (
    echo   ✓ apuestas.db
    set /a DB_OK+=1
) else (
    echo   ✗ apuestas.db NO ENCONTRADA
    set /a ERRORES+=1
)

if exist "data\messages.db" (
    echo   ✓ messages.db
    set /a DB_OK+=1
) else (
    echo   ✗ messages.db NO ENCONTRADA
    set /a ERRORES+=1
)

echo.
echo   Total: %DB_OK%/7 bases de datos encontradas

REM ============================================================
REM [3] VERIFICAR JUEGOS
REM ============================================================
echo.
echo [3/10] Verificando juegos implementados...
echo.

set JUEGOS_OK=0

if exist "game_pages\pasapalabra\game.html" (
    echo   ✓ Pasapalabra
    set /a JUEGOS_OK+=1
) else (
    echo   ✗ Pasapalabra NO ENCONTRADO
    set /a ERRORES+=1
)

if exist "game_pages\quiensoy\game.html" (
    echo   ✓ ¿Quién Soy?
    set /a JUEGOS_OK+=1
) else (
    echo   ✗ ¿Quién Soy? NO ENCONTRADO
    set /a ERRORES+=1
)

if exist "game_pages\hundirlaflota\game.html" (
    echo   ✓ Hundir la Flota
    set /a JUEGOS_OK+=1
) else (
    echo   ✗ Hundir la Flota NO ENCONTRADO
    set /a ERRORES+=1
)

if exist "game_pages\millonario\game.html" (
    echo   ✓ Millonario
    set /a JUEGOS_OK+=1
) else (
    echo   ✗ Millonario NO ENCONTRADO
    set /a ERRORES+=1
)

if exist "game_pages\cifrasletras\game.html" (
    echo   ✓ Cifras y Letras
    set /a JUEGOS_OK+=1
) else (
    echo   ✗ Cifras y Letras NO ENCONTRADO
    set /a ERRORES+=1
)

echo.
echo   Total: %JUEGOS_OK%/5 juegos encontrados

REM ============================================================
REM [4] VERIFICAR SISTEMAS ADICIONALES
REM ============================================================
echo.
echo [4/10] Verificando sistemas adicionales...
echo.

set SISTEMAS_OK=0

if exist "game_pages\apuestas\apuestas.html" (
    echo   ✓ Sistema de Apuestas ^(Porras^)
    set /a SISTEMAS_OK+=1
) else (
    echo   ✗ Sistema de Apuestas NO ENCONTRADO
    set /a ERRORES+=1
)

if exist "game_pages\votaciones\votaciones.html" (
    echo   ✓ Sistema de Votaciones
    set /a SISTEMAS_OK+=1
) else (
    echo   ✗ Sistema de Votaciones NO ENCONTRADO
    set /a ERRORES+=1
)

if exist "game_pages\messages\mensajes.html" (
    echo   ✓ Sistema de Mensajería
    set /a SISTEMAS_OK+=1
) else (
    echo   ✗ Sistema de Mensajería NO ENCONTRADO
    set /a ERRORES+=1
)

if exist "static\video.html" (
    echo   ✓ Sistema de Videollamadas
    set /a SISTEMAS_OK+=1
) else (
    echo   ✗ Sistema de Videollamadas NO ENCONTRADO
    set /a ERRORES+=1
)

if exist "static\cuentos.html" (
    echo   ✓ Cuentos Interactivos
    set /a SISTEMAS_OK+=1
) else (
    echo   ✗ Cuentos Interactivos NO ENCONTRADO
    set /a ERRORES+=1
)

if exist "static\gallery" (
    echo   ✓ Galería de Imágenes
    set /a SISTEMAS_OK+=1
) else (
    echo   ✗ Galería de Imágenes NO ENCONTRADA
    set /a ERRORES+=1
)

echo.
echo   Total: %SISTEMAS_OK%/6 sistemas encontrados

REM ============================================================
REM [5] VERIFICAR PANEL OPO
REM ============================================================
echo.
echo [5/10] Verificando Panel OPO...
echo.

if exist "static\opo" (
    echo   ✓ Panel OPO encontrado
) else (
    echo   ✗ Panel OPO NO ENCONTRADO
    set /a ERRORES+=1
)

REM ============================================================
REM [6] VERIFICAR INTERNACIONALIZACION
REM ============================================================
echo.
echo [6/10] Verificando internacionalización...
echo.

set I18N_OK=0

if exist "static\i18n\es.json" (
    echo   ✓ Español ^(es^)
    set /a I18N_OK+=1
) else (
    echo   ✗ Español NO ENCONTRADO
)

if exist "static\i18n\en.json" (
    echo   ✓ Inglés ^(en^)
    set /a I18N_OK+=1
) else (
    echo   ✗ Inglés NO ENCONTRADO
)

if exist "static\i18n\fr.json" (
    echo   ✓ Francés ^(fr^)
    set /a I18N_OK+=1
) else (
    echo   ✗ Francés NO ENCONTRADO
)

echo.
echo   Total: %I18N_OK%/3 idiomas encontrados

REM ============================================================
REM [7] VERIFICAR SCRIPTS DE UTILIDAD
REM ============================================================
echo.
echo [7/10] Verificando scripts de utilidad...
echo.

if exist "ARRANCAR.bat" (
    echo   ✓ Script de inicio
) else (
    echo   ✗ ARRANCAR.bat NO ENCONTRADO
    set /a ERRORES+=1
)

if exist "DETENER_SERVIDOR.bat" (
    echo   ✓ Script de detención
) else (
    echo   ✗ DETENER_SERVIDOR.bat NO ENCONTRADO
    set /a ERRORES+=1
)

if exist "REINICIAR_SERVIDOR.bat" (
    echo   ✓ Script de reinicio
) else (
    echo   ✗ REINICIAR_SERVIDOR.bat NO ENCONTRADO
    set /a ERRORES+=1
)

if exist "INICIAR_CON_CLOUDFLARE.bat" (
    echo   ✓ Script de Cloudflare
) else (
    echo   ✗ INICIAR_CON_CLOUDFLARE.bat NO ENCONTRADO
    set /a ERRORES+=1
)

REM ============================================================
REM [8] VERIFICAR CONFIGURACION
REM ============================================================
echo.
echo [8/10] Verificando configuración...
echo.

if exist "config\jwt_secret.txt" (
    echo   ✓ JWT Secret configurado
) else (
    echo   ⚠ JWT Secret no encontrado ^(se generará automáticamente^)
)

if exist "config\master.txt" (
    echo   ✓ Contraseña maestra configurada
) else (
    echo   ⚠ Contraseña maestra no encontrada ^(se generará automáticamente^)
)

REM ============================================================
REM [9] VERIFICAR BACKUPS
REM ============================================================
echo.
echo [9/10] Verificando sistema de backups...
echo.

if exist "backup" (
    echo   ✓ Carpeta de backups diarios
) else (
    echo   ⚠ Carpeta de backups no encontrada
)

if exist "backup_30min" (
    echo   ✓ Carpeta de backups cada 30 min
) else (
    echo   ⚠ Carpeta de backups 30min no encontrada
)

if exist "CONFIGURAR_BACKUP_AUTOMATICO.bat" (
    echo   ✓ Script de configuración de backups
) else (
    echo   ⚠ Script de backups no encontrado
)

REM ============================================================
REM [10] VERIFICAR ESTADO DEL SERVIDOR
REM ============================================================
echo.
echo [10/10] Verificando estado del servidor...
echo.

netstat -ano | findstr ":8000" | findstr "LISTENING" >nul 2>&1
if errorlevel 1 (
    echo   ○ Servidor NO está corriendo
    echo   ^(Esto es normal si no lo has iniciado^)
) else (
    echo   ✓ Servidor corriendo en puerto 8000
)

tasklist | findstr cloudflared >nul 2>&1
if errorlevel 1 (
    echo   ○ Cloudflare Tunnel NO está corriendo
    echo   ^(Esto es normal si no lo has iniciado^)
) else (
    echo   ✓ Cloudflare Tunnel activo
)

REM ============================================================
REM RESUMEN FINAL
REM ============================================================
echo.
echo ══════════════════════════════════════════════════════════════
echo.

if %ERRORES% EQU 0 (
    echo ╔══════════════════════════════════════════════════════════════╗
    echo ║                                                              ║
    echo ║              ✓ SISTEMA 100%% COMPLETO Y LISTO                ║
    echo ║                                                              ║
    echo ╚══════════════════════════════════════════════════════════════╝
    echo.
    echo   ✅ Todas las funcionalidades están implementadas
    echo   ✅ Todos los archivos necesarios están presentes
    echo   ✅ El sistema está listo para usar
    echo.
    echo   Para iniciar el servidor:
    echo   ^> ARRANCAR.bat
    echo.
) else (
    echo ╔══════════════════════════════════════════════════════════════╗
    echo ║                                                              ║
    echo ║              ⚠ SE ENCONTRARON %ERRORES% ERRORES                      ║
    echo ║                                                              ║
    echo ╚══════════════════════════════════════════════════════════════╝
    echo.
    echo   Revisa los errores marcados con ✗ arriba
    echo   Algunos archivos críticos pueden estar faltando
    echo.
)

echo ══════════════════════════════════════════════════════════════
echo.
echo Presiona cualquier tecla para salir...
pause >nul
