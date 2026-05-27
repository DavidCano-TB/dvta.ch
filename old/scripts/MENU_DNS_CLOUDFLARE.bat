@echo off
chcp 65001 >nul

:MENU
cls
echo ═══════════════════════════════════════════════════════════
echo   🌐 MENÚ DE GESTIÓN DNS CLOUDFLARE - dvta.ch
echo ═══════════════════════════════════════════════════════════
echo.
echo   1. Verificar registros DNS actuales
echo   2. Configurar registros de EMAIL automáticamente
echo   3. Ver registros guardados de Infomaniak
echo   4. Abrir dashboard de Cloudflare
echo   5. Ayuda y documentación
echo.
echo   0. Salir
echo.
echo ═══════════════════════════════════════════════════════════
echo.

set /p opcion="Selecciona una opción (0-5): "

if "%opcion%"=="1" goto VERIFICAR
if "%opcion%"=="2" goto CONFIGURAR
if "%opcion%"=="3" goto VER_BACKUP
if "%opcion%"=="4" goto ABRIR_CLOUDFLARE
if "%opcion%"=="5" goto AYUDA
if "%opcion%"=="0" goto SALIR

echo.
echo ❌ Opción inválida
timeout /t 2 >nul
goto MENU

:VERIFICAR
cls
echo ═══════════════════════════════════════════════════════════
echo   🔍 VERIFICAR REGISTROS DNS
echo ═══════════════════════════════════════════════════════════
echo.
call VERIFICAR_DNS_CLOUDFLARE.bat
goto MENU

:CONFIGURAR
cls
echo ═══════════════════════════════════════════════════════════
echo   🚀 CONFIGURAR REGISTROS DE EMAIL
echo ═══════════════════════════════════════════════════════════
echo.
call CONFIGURAR_DNS_AUTOMATICO.bat
goto MENU

:VER_BACKUP
cls
echo ═══════════════════════════════════════════════════════════
echo   📋 REGISTROS DNS GUARDADOS DE INFOMANIAK
echo ═══════════════════════════════════════════════════════════
echo.
if exist "REGISTROS_DNS_INFOMANIAK_DVTA_CH.txt" (
    type REGISTROS_DNS_INFOMANIAK_DVTA_CH.txt
) else (
    echo ❌ No se encuentra el archivo de backup
)
echo.
pause
goto MENU

:ABRIR_CLOUDFLARE
cls
echo ═══════════════════════════════════════════════════════════
echo   🌐 ABRIENDO CLOUDFLARE
echo ═══════════════════════════════════════════════════════════
echo.
echo Abriendo el dashboard de Cloudflare en tu navegador...
echo.
start https://dash.cloudflare.com
echo.
echo ✅ Dashboard abierto
echo.
echo Para gestionar DNS:
echo   1. Selecciona el dominio: dvta.ch
echo   2. Ve a: DNS ^> Records
echo.
pause
goto MENU

:AYUDA
cls
echo ═══════════════════════════════════════════════════════════
echo   📖 AYUDA Y DOCUMENTACIÓN
echo ═══════════════════════════════════════════════════════════
echo.
echo ESTADO ACTUAL:
echo   • Nameservers: Configurados en Cloudflare
echo   • Dominio: dvta.ch
echo   • Zona ID: a0353c3d6ad85c54e8ed8f31237538b9
echo.
echo REGISTROS NECESARIOS PARA EMAIL:
echo   • MX: Servidor de correo (mta-gw.infomaniak.ch)
echo   • SPF: Autorización de envío
echo   • DKIM: Firma digital de emails
echo   • DMARC: Política de seguridad
echo   • Autoconfig: Configuración automática (Thunderbird)
echo   • Autodiscover: Configuración automática (Outlook)
echo.
echo CÓMO USAR ESTE MENÚ:
echo.
echo   1. VERIFICAR (Opción 1):
echo      Muestra todos los registros DNS actuales en Cloudflare
echo      Indica qué registros faltan
echo.
echo   2. CONFIGURAR (Opción 2):
echo      Configura automáticamente TODOS los registros de email
echo      Necesitas un token de Cloudflare con permisos de DNS
echo.
echo   3. VER BACKUP (Opción 3):
echo      Muestra los registros que tenías en Infomaniak
echo      Útil para verificar que no falta nada
echo.
echo   4. ABRIR CLOUDFLARE (Opción 4):
echo      Abre el dashboard de Cloudflare en tu navegador
echo      Para gestionar DNS manualmente
echo.
echo CREAR TOKEN DE CLOUDFLARE:
echo   1. Ve a: https://dash.cloudflare.com/profile/api-tokens
echo   2. Clic en [Create Token]
echo   3. Usa el template: "Edit zone DNS"
echo   4. Selecciona la zona: dvta.ch
echo   5. Copia el token generado
echo.
echo GUARDAR TOKEN (OPCIONAL):
echo   Para no tener que ingresarlo cada vez:
echo   set CLOUDFLARE_API_TOKEN=tu_token_aqui
echo.
echo ARCHIVOS IMPORTANTES:
echo   • configurar_dns_cloudflare_dvta.py (script de configuración)
echo   • verificar_dns_cloudflare.py (script de verificación)
echo   • REGISTROS_DNS_INFOMANIAK_DVTA_CH.txt (backup)
echo.
echo ═══════════════════════════════════════════════════════════
echo.
pause
goto MENU

:SALIR
cls
echo.
echo ═══════════════════════════════════════════════════════════
echo   👋 Hasta luego
echo ═══════════════════════════════════════════════════════════
echo.
echo Para volver a este menú, ejecuta: MENU_DNS_CLOUDFLARE.bat
echo.
timeout /t 2 >nul
exit /b 0
