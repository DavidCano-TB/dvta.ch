@echo off
chcp 65001 >nul
title Limpieza de Archivos Innecesarios - DVDBank
color 0A

echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo   🧹 LIMPIEZA DE ARCHIVOS INNECESARIOS - DVDBANK
echo ═══════════════════════════════════════════════════════════════════════════
echo.
echo Este script eliminará TODOS los archivos innecesarios del proyecto:
echo.
echo   • Documentación antigua (.txt)
echo   • Scripts de ngrok (obsoletos)
echo   • Scripts de configuración duplicados
echo   • Archivos de log antiguos
echo   • Archivos temporales
echo   • Backups de configuración
echo.
echo ⚠️  IMPORTANTE: Esta acción NO se puede deshacer
echo.
pause

echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo PASO 1: Creando carpeta OLD para archivos obsoletos
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
if not exist "OLD" mkdir OLD
if not exist "OLD\docs" mkdir OLD\docs
if not exist "OLD\ngrok" mkdir OLD\ngrok
if not exist "OLD\scripts" mkdir OLD\scripts
if not exist "OLD\logs" mkdir OLD\logs
echo ✅ Carpetas OLD creadas

echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo PASO 2: Moviendo documentación antigua a OLD\docs
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

REM Mover todos los archivos .txt de documentación
for %%f in (
    CHECKLIST_*.txt
    COMO_USAR_*.txt
    CONFIGURACION_*.txt
    DATOS_*.txt
    DECISION_*.txt
    DVDBANK_*.txt
    ESTADO_*.txt
    GUIA_*.txt
    INFORME_*.txt
    INICIO_RAPIDO_*.txt
    INSTALACION_*.txt
    INSTRUCCIONES_*.txt
    LEEME_*.txt
    LEER_*.txt
    MIGRACION_*.txt
    PASOS_*.txt
    README_*.txt
    RESULTADO_*.txt
    RESUMEN_*.txt
    SISTEMA_*.txt
    SOLUCION_*.txt
    TODO_*.txt
    TU_URL_*.txt
    URLS_*.txt
    URL_*.txt
    VERIFICACION_*.txt
) do (
    if exist "%%f" (
        move /Y "%%f" "OLD\docs\" >nul 2>&1
        echo   ✅ Movido: %%f
    )
)

echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo PASO 3: Moviendo archivos de ngrok obsoletos a OLD\ngrok
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

REM Mover archivos de ngrok
for %%f in (
    ACTUALIZAR_URL_NGROK.bat
    actualizar_url_ngrok.py
    ARREGLAR_NGROK_AHORA.bat
    CAMBIAR_NGROK.bat
    CONFIGURAR_NGROK.bat
    DIAGNOSTICAR_NGROK.bat
    GENERAR_URL_TEMPORAL.bat
    generar_url_ahora.py
    INICIAR_COMO_ADMIN_NGROK_OLD.bat
    LIMPIAR_ARCHIVOS_NGROK.bat
    MANTENER_URL_ESTABLE.bat
    MOVER_ARCHIVOS_NGROK_A_OLD.bat
    ngrok.exe
    ngrok.log
    ngrok_*.log
    ngrok_*.json
    ngrok_config_manager.py
    OBTENER_URL.bat
    OBTENER_URL_PUBLICA.bat
    PROBAR_ACTUALIZACION_URL.bat
    PROBAR_TODAS_URLS.bat
    REINICIAR_NGROK_CORRECTAMENTE.bat
    SOLUCIONAR_NGROK_DEFINITIVO.bat
    update_ngrok_yml.py
    url_encontrada.txt
    url_temp.log
    VERIFICAR_DOMINIO_NGROK.bat
    VERIFICAR_TOKEN_NGROK.bat
    VER_ESTADO_NGROK.bat
) do (
    if exist "%%f" (
        move /Y "%%f" "OLD\ngrok\" >nul 2>&1
        echo   ✅ Movido: %%f
    )
)

echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo PASO 4: Moviendo scripts duplicados/obsoletos a OLD\scripts
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

REM Mover scripts obsoletos o duplicados
for %%f in (
    ABRIR_INSTRUCCIONES.bat
    AGREGAR_USUARIO_OPO.bat
    AGREGAR_USUARIO_Y_REINICIAR.bat
    ANADIR_DVDBANK_A_CLOUDFLARE.bat
    APLICAR_CAMBIOS.bat
    APLICAR_CAMBIOS_QUIEN_SOY.bat
    APLICAR_CORRECCIONES_COMPLETAS.bat
    APLICAR_CORRECCIONES_COMPLETAS.py
    APLICAR_DNS_AUTOMATICO.bat
    APLICAR_SEGURIDAD_TOKENS.bat
    APLICAR_Y_FORZAR_TODO.bat
    ARREGLAR_DNS_CLOUDFLARE.bat
    arreglar_dns_cloudflare.py
    ARREGLAR_TODO_AHORA.bat
    BACKUP_SISTEMA.bat
    CANCELAR_INSTALACION_AL_REINICIO.bat
    check_db.py
    clear_lockouts_and_test.py
    cloudflare-config.yml.backup
    cloudflare-config.yml.bak
    cloudflare_output.txt
    completar_preguntas.py
    config.yml
    CONFIGURAR_ANTHROPIC_API.bat
    CONFIGURAR_API_KEY.bat
    CONFIGURAR_ARRANQUE_COMPLETO.bat
    CONFIGURAR_ARRANQUE_DISCO_C.bat
    CONFIGURAR_BACKUP_30MIN.bat
    CONFIGURAR_BACKUP_AUTOMATICO.bat
    CONFIGURAR_CLOUDFLARE.bat
    CONFIGURAR_DOMINIO_DVD_CH.bat
    CONFIGURAR_DVDBANK_CH.bat
    configurar_dvdbank_ch.py
    CONFIGURAR_DVDBANK_DAVID_CH.bat
    CONFIGURAR_DVDBANK_FINAL.bat
    CONFIGURAR_DVDBANK_REAL.bat
    CONFIGURAR_DVD_CH_COMPLETO.bat
    CONFIGURAR_GEMINI_API.bat
    CONFIGURAR_INICIO_AUTOMATICO.bat
    CONFIGURAR_INICIO_AUTO_WINDOWS.bat
    CONFIGURAR_INICIO_WINDOWS.bat
    CONFIGURAR_INSTALACION_AL_REINICIO.bat
    CONFIGURAR_OPENAI_API.bat
    CONFIGURAR_REGISTRO_ARRANQUE.bat
    CONFIGURAR_SERVICIO_FINAL.bat
    CONFIGURAR_SUBDOMINIO.bat
    configurar_todo_automatico.py
    CONFIGURAR_TODO_DVDBANK.bat
    CORREGIR_VOTACIONES_APUESTAS_QUIEN_SOY.bat
    CREAR_ACCESO_DIRECTO_ESCRITORIO.bat
    crear_config_tunnel.py
    CREAR_GAME_MEJORADO.bat
    CREAR_TABLAS_VOTACIONES.bat
    crear_tablas_votaciones.py
    CREAR_TAREA_INSTALADOR.ps1
    debug_login.py
    DEBUG_OPO.html
    DESACTIVAR_ANTIVIRUS_Y_ARRANCAR.bat
    DESACTIVAR_INICIO_WINDOWS.bat
    DESACTIVAR_PIN_WINDOWS.bat
    DESINSTALAR_AUTOSTART.bat
    DESINSTALAR_DEFENDER_Y_ARRANCAR.bat
    DESINSTALAR_INICIO_AUTOMATICO.bat
    DESINSTALAR_INICIO_AUTOMATICO_DVD_CH.bat
    DESINSTALAR_WATCHDOG.bat
    DETENER_SERVIDOR.bat
    DETENER_SISTEMA.bat
    DETENER_TODO.bat
    DETENER_WATCHDOG.bat
    DIAGNOSTICO_COMPLETO.bat
    EJECUTAR_BACKUP_30MIN_AHORA.bat
    EJECUTAR_BACKUP_MANUAL.bat
    EJECUTAR_CONFIGURACION_AUTO.bat
    EJECUTAR_ESTO.bat
    ejecutar_generacion.py
    EJECUTAR_GENERACION_PREGUNTAS.bat
    EJECUTAR_LIMPIEZA.bat
    EJECUTAR_MIGRACION_AHORA.bat
    fix_dvd_password.py
    force_update_password.py
    generar_directo.py
    GENERAR_GRAFO_CONOCIMIENTO.bat
    GENERAR_PREGUNTAS.bat
    generar_preguntas_completo.py
    GENERAR_PREGUNTAS_PASAPALABRA.bat
    generar_preguntas_pasapalabra.py
    generate_translations.py
    gen_preguntas.py
    groq_helper.py
    INICIAR_CLOUDFLARE_SIMPLE.bat
    INICIAR_CLOUDFLARE_TEMPORAL.bat
    INICIAR_CON_CLOUDFLARE.bat
    INICIAR_DVD_CH.bat
    INICIAR_SERVIDOR.bat
    INICIAR_SERVIDOR_QUIEN_SOY.bat
    INICIAR_SERVIDOR_SIMPLE.bat
    INICIAR_SISTEMA_COMPLETO.bat
    INICIAR_WATCHDOG.bat
    INICIO.bat
    INSTALAR_AUTOSTART.bat
    INSTALAR_DEPENDENCIAS.bat
    INSTALAR_GRAPHIFY.bat
    INSTALAR_INICIO_AUTOMATICO.bat
    INSTALAR_INICIO_AUTOMATICO_DVD_CH.bat
    INSTALAR_WATCHDOG.bat
    install_autostart.bat
    listar_zonas_cloudflare.py
    opo_local.html
    PREPARAR_PARA_REINICIO.bat
    PROBAR_AHORA.ps1
    PROBAR_CONEXION.bat
    PROBAR_CORRECCIONES.bat
    PROBAR_QUIEN_SOY_AHORA.bat
    PROBAR_QUIEN_SOY_IA.bat
    PROBAR_SCOOBY.bat
    PRUEBA_COMPLETA.bat
    REACTIVAR_DEFENDER.bat
    REINICIAR_AHORA.bat
    REINICIAR_SERVICIO.bat
    REINICIAR_SERVIDOR.bat
    REINICIAR_SERVIDOR_AHORA.bat
    REINICIAR_SERVIDOR_COMPLETO.bat
    REINICIAR_SERVIDOR_FORZADO.bat
    reset_all_passwords.py
    reset_passwords.py
    RESTART_ALL.bat
    RESTART_SERVER.bat
    restart_server.py
    restore_passwords_from_backup.py
    service_launcher.py
    SOLUCION_RAPIDA_TEMPORAL.bat
    start.py
    startdvdcoin.bat
    start_dvdcoin_hidden.vbs
    START_SERVER.bat
    TEST_BROWSER.html
    tunnel_info.json
    uninstall_autostart.bat
    update_remaining_translations.py
    verificacion_final.py
    VERIFICAR_CONEXION.bat
    verificar_config_ngrok.py
    VERIFICAR_CORRECCION_QUIEN_SOY.bat
    VERIFICAR_DNS.bat
    verificar_dns_cloudflare.py
    verificar_dns_propagacion.py
    VERIFICAR_DVDBANK.bat
    VERIFICAR_DVD_CH.bat
    VERIFICAR_ESTADO_BACKUP.bat
    VERIFICAR_ESTADO_CLOUDFLARE.bat
    verificar_estado_cloudflare.py
    VERIFICAR_INSTALACION.bat
    VERIFICAR_MEJORAS_HUNDIR_LA_FLOTA.bat
    VERIFICAR_PROPAGACION.bat
    VERIFICAR_QUIEN_SOY_IA.bat
    VERIFICAR_SERVIDOR.bat
    VERIFICAR_SISTEMA.bat
    verificar_tablas_votaciones.py
    VERIFICAR_TODO.bat
    VERIFICAR_TODO_COMPLETO.bat
    VERIFICAR_Y_APLICAR_TODO.bat
    verify_dvd_password.py
    VER_BACKUPS_30MIN.bat
    VER_ESTADO_SISTEMA.bat
    VER_ESTADO_WATCHDOG.bat
) do (
    if exist "%%f" (
        move /Y "%%f" "OLD\scripts\" >nul 2>&1
        echo   ✅ Movido: %%f
    )
)

echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo PASO 5: Moviendo archivos de log a OLD\logs
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

for %%f in (
    cloudflare_tunnel.log
    cloudflare_tunnel_error.log
    no_sleep.log
    python_server.log
    server.log
) do (
    if exist "%%f" (
        move /Y "%%f" "OLD\logs\" >nul 2>&1
        echo   ✅ Movido: %%f
    )
)

echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo   ✅ LIMPIEZA COMPLETADA
echo ═══════════════════════════════════════════════════════════════════════════
echo.
echo Se han movido todos los archivos innecesarios a la carpeta OLD\
echo.
echo Archivos que SE MANTIENEN (necesarios para el sistema):
echo.
echo   ✅ main.py (servidor principal)
echo   ✅ *.db (bases de datos)
echo   ✅ cloudflared.exe (túnel Cloudflare)
echo   ✅ cloudflare-dvta-config.yml (configuración túnel dvta.ch)
echo   ✅ cloudflare-tunnel-dvta.yml (configuración túnel dvta.ch)
echo   ✅ configurar_dns_cloudflare_dvta.py (script DNS email)
echo   ✅ CONFIGURAR_EMAIL_CLOUDFLARE.bat (configurar email)
echo   ✅ CONFIGURAR_TODO_DVTA.bat (configuración dvta.ch)
echo   ✅ CONFIGURAR_TUNNEL_DVTA.bat (crear túnel)
echo   ✅ crear_tunnel_dvta.py (script crear túnel)
echo   ✅ INICIAR_SISTEMA_DVTA.bat (arranque sistema)
echo   ✅ INICIAR_TUNNEL_DVTA.bat (arranque túnel)
echo   ✅ MENU_PRINCIPAL.bat (menú principal)
echo   ✅ REGISTROS_DNS_INFOMANIAK_DVTA_CH.txt (backup DNS)
echo   ✅ ai_helper.py (asistente IA)
echo   ✅ nssm.exe (gestor de servicios)
echo   ✅ static\ (archivos web)
echo   ✅ src\ (código fuente)
echo   ✅ data\ (bases de datos)
echo   ✅ backup\ (backups diarios)
echo   ✅ backup_30min\ (backups cada 30 min)
echo.
echo Si necesitas recuperar algún archivo, está en la carpeta OLD\
echo.
pause
