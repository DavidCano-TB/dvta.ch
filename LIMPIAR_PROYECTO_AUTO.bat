@echo off
chcp 65001 >nul
title Limpieza Automática - DVDBank
color 0A

echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo   🧹 LIMPIEZA AUTOMÁTICA DE ARCHIVOS INNECESARIOS
echo ═══════════════════════════════════════════════════════════════════════════
echo.

REM Crear carpetas OLD
if not exist "OLD" mkdir OLD
if not exist "OLD\docs" mkdir OLD\docs
if not exist "OLD\ngrok" mkdir OLD\ngrok
if not exist "OLD\scripts" mkdir OLD\scripts
if not exist "OLD\logs" mkdir OLD\logs
echo ✅ Carpetas OLD creadas
echo.

echo Moviendo archivos innecesarios...
echo.

REM Mover documentación
move /Y CHECKLIST_*.txt OLD\docs\ >nul 2>&1
move /Y COMO_USAR_*.txt OLD\docs\ >nul 2>&1
move /Y CONFIGURACION_*.txt OLD\docs\ >nul 2>&1
move /Y DATOS_*.txt OLD\docs\ >nul 2>&1
move /Y DECISION_*.txt OLD\docs\ >nul 2>&1
move /Y DVDBANK_*.txt OLD\docs\ >nul 2>&1
move /Y ESTADO_*.txt OLD\docs\ >nul 2>&1
move /Y GUIA_*.txt OLD\docs\ >nul 2>&1
move /Y INFORME_*.txt OLD\docs\ >nul 2>&1
move /Y INICIO_RAPIDO_*.txt OLD\docs\ >nul 2>&1
move /Y INSTALACION_*.txt OLD\docs\ >nul 2>&1
move /Y INSTRUCCIONES_*.txt OLD\docs\ >nul 2>&1
move /Y LEEME_*.txt OLD\docs\ >nul 2>&1
move /Y LEER_*.txt OLD\docs\ >nul 2>&1
move /Y MIGRACION_*.txt OLD\docs\ >nul 2>&1
move /Y PASOS_*.txt OLD\docs\ >nul 2>&1
move /Y README_*.txt OLD\docs\ >nul 2>&1
move /Y RESULTADO_*.txt OLD\docs\ >nul 2>&1
move /Y RESUMEN_*.txt OLD\docs\ >nul 2>&1
move /Y SISTEMA_*.txt OLD\docs\ >nul 2>&1
move /Y SOLUCION_*.txt OLD\docs\ >nul 2>&1
move /Y TODO_*.txt OLD\docs\ >nul 2>&1
move /Y TU_URL_*.txt OLD\docs\ >nul 2>&1
move /Y URLS_*.txt OLD\docs\ >nul 2>&1
move /Y URL_*.txt OLD\docs\ >nul 2>&1
move /Y VERIFICACION_*.txt OLD\docs\ >nul 2>&1
move /Y CONFIGURAR_DNS_AHORA.txt OLD\docs\ >nul 2>&1
echo ✅ Documentación movida

REM Mover archivos ngrok
move /Y ACTUALIZAR_URL_NGROK.bat OLD\ngrok\ >nul 2>&1
move /Y actualizar_url_ngrok.py OLD\ngrok\ >nul 2>&1
move /Y ARREGLAR_NGROK_AHORA.bat OLD\ngrok\ >nul 2>&1
move /Y CAMBIAR_NGROK.bat OLD\ngrok\ >nul 2>&1
move /Y CONFIGURAR_NGROK.bat OLD\ngrok\ >nul 2>&1
move /Y DIAGNOSTICAR_NGROK.bat OLD\ngrok\ >nul 2>&1
move /Y GENERAR_URL_TEMPORAL.bat OLD\ngrok\ >nul 2>&1
move /Y generar_url_ahora.py OLD\ngrok\ >nul 2>&1
move /Y INICIAR_COMO_ADMIN_NGROK_OLD.bat OLD\ngrok\ >nul 2>&1
move /Y LIMPIAR_ARCHIVOS_NGROK.bat OLD\ngrok\ >nul 2>&1
move /Y MANTENER_URL_ESTABLE.bat OLD\ngrok\ >nul 2>&1
move /Y MOVER_ARCHIVOS_NGROK_A_OLD.bat OLD\ngrok\ >nul 2>&1
move /Y ngrok.exe OLD\ngrok\ >nul 2>&1
move /Y ngrok.log OLD\ngrok\ >nul 2>&1
move /Y ngrok_*.log OLD\ngrok\ >nul 2>&1
move /Y ngrok_*.json OLD\ngrok\ >nul 2>&1
move /Y ngrok_config_manager.py OLD\ngrok\ >nul 2>&1
move /Y OBTENER_URL.bat OLD\ngrok\ >nul 2>&1
move /Y OBTENER_URL_PUBLICA.bat OLD\ngrok\ >nul 2>&1
move /Y PROBAR_ACTUALIZACION_URL.bat OLD\ngrok\ >nul 2>&1
move /Y PROBAR_TODAS_URLS.bat OLD\ngrok\ >nul 2>&1
move /Y REINICIAR_NGROK_CORRECTAMENTE.bat OLD\ngrok\ >nul 2>&1
move /Y SOLUCIONAR_NGROK_DEFINITIVO.bat OLD\ngrok\ >nul 2>&1
move /Y update_ngrok_yml.py OLD\ngrok\ >nul 2>&1
move /Y url_encontrada.txt OLD\ngrok\ >nul 2>&1
move /Y url_temp.log OLD\ngrok\ >nul 2>&1
move /Y VERIFICAR_DOMINIO_NGROK.bat OLD\ngrok\ >nul 2>&1
move /Y VERIFICAR_TOKEN_NGROK.bat OLD\ngrok\ >nul 2>&1
move /Y VER_ESTADO_NGROK.bat OLD\ngrok\ >nul 2>&1
echo ✅ Archivos ngrok movidos

REM Mover scripts obsoletos
move /Y ABRIR_INSTRUCCIONES.bat OLD\scripts\ >nul 2>&1
move /Y AGREGAR_USUARIO_OPO.bat OLD\scripts\ >nul 2>&1
move /Y AGREGAR_USUARIO_Y_REINICIAR.bat OLD\scripts\ >nul 2>&1
move /Y ANADIR_DVDBANK_A_CLOUDFLARE.bat OLD\scripts\ >nul 2>&1
move /Y APLICAR_*.bat OLD\scripts\ >nul 2>&1
move /Y APLICAR_*.py OLD\scripts\ >nul 2>&1
move /Y ARREGLAR_DNS_CLOUDFLARE.bat OLD\scripts\ >nul 2>&1
move /Y arreglar_dns_cloudflare.py OLD\scripts\ >nul 2>&1
move /Y ARREGLAR_TODO_AHORA.bat OLD\scripts\ >nul 2>&1
move /Y BACKUP_SISTEMA.bat OLD\scripts\ >nul 2>&1
move /Y CANCELAR_INSTALACION_AL_REINICIO.bat OLD\scripts\ >nul 2>&1
move /Y check_db.py OLD\scripts\ >nul 2>&1
move /Y clear_lockouts_and_test.py OLD\scripts\ >nul 2>&1
move /Y cloudflare-config.yml.backup OLD\scripts\ >nul 2>&1
move /Y cloudflare-config.yml.bak OLD\scripts\ >nul 2>&1
move /Y cloudflare_output.txt OLD\scripts\ >nul 2>&1
move /Y completar_preguntas.py OLD\scripts\ >nul 2>&1
move /Y config.yml OLD\scripts\ >nul 2>&1
move /Y CONFIGURAR_ANTHROPIC_API.bat OLD\scripts\ >nul 2>&1
move /Y CONFIGURAR_API_KEY.bat OLD\scripts\ >nul 2>&1
move /Y CONFIGURAR_ARRANQUE_*.bat OLD\scripts\ >nul 2>&1
move /Y CONFIGURAR_BACKUP_*.bat OLD\scripts\ >nul 2>&1
move /Y CONFIGURAR_CLOUDFLARE.bat OLD\scripts\ >nul 2>&1
move /Y CONFIGURAR_DOMINIO_DVD_CH.bat OLD\scripts\ >nul 2>&1
move /Y CONFIGURAR_DVDBANK_CH.bat OLD\scripts\ >nul 2>&1
move /Y configurar_dvdbank_ch.py OLD\scripts\ >nul 2>&1
move /Y CONFIGURAR_DVDBANK_DAVID_CH.bat OLD\scripts\ >nul 2>&1
move /Y CONFIGURAR_DVDBANK_FINAL.bat OLD\scripts\ >nul 2>&1
move /Y CONFIGURAR_DVDBANK_REAL.bat OLD\scripts\ >nul 2>&1
move /Y CONFIGURAR_DVD_CH_COMPLETO.bat OLD\scripts\ >nul 2>&1
move /Y CONFIGURAR_GEMINI_API.bat OLD\scripts\ >nul 2>&1
move /Y CONFIGURAR_INICIO_*.bat OLD\scripts\ >nul 2>&1
move /Y CONFIGURAR_INSTALACION_AL_REINICIO.bat OLD\scripts\ >nul 2>&1
move /Y CONFIGURAR_OPENAI_API.bat OLD\scripts\ >nul 2>&1
move /Y CONFIGURAR_REGISTRO_ARRANQUE.bat OLD\scripts\ >nul 2>&1
move /Y CONFIGURAR_SERVICIO_FINAL.bat OLD\scripts\ >nul 2>&1
move /Y CONFIGURAR_SUBDOMINIO.bat OLD\scripts\ >nul 2>&1
move /Y configurar_todo_automatico.py OLD\scripts\ >nul 2>&1
move /Y CONFIGURAR_TODO_DVDBANK.bat OLD\scripts\ >nul 2>&1
move /Y CORREGIR_*.bat OLD\scripts\ >nul 2>&1
move /Y CREAR_ACCESO_DIRECTO_ESCRITORIO.bat OLD\scripts\ >nul 2>&1
move /Y crear_config_tunnel.py OLD\scripts\ >nul 2>&1
move /Y CREAR_GAME_MEJORADO.bat OLD\scripts\ >nul 2>&1
move /Y CREAR_TABLAS_VOTACIONES.bat OLD\scripts\ >nul 2>&1
move /Y crear_tablas_votaciones.py OLD\scripts\ >nul 2>&1
move /Y CREAR_TAREA_INSTALADOR.ps1 OLD\scripts\ >nul 2>&1
move /Y debug_login.py OLD\scripts\ >nul 2>&1
move /Y DEBUG_OPO.html OLD\scripts\ >nul 2>&1
move /Y DESACTIVAR_*.bat OLD\scripts\ >nul 2>&1
move /Y DESINSTALAR_*.bat OLD\scripts\ >nul 2>&1
move /Y DETENER_*.bat OLD\scripts\ >nul 2>&1
move /Y DIAGNOSTICO_COMPLETO.bat OLD\scripts\ >nul 2>&1
move /Y EJECUTAR_*.bat OLD\scripts\ >nul 2>&1
move /Y ejecutar_*.py OLD\scripts\ >nul 2>&1
move /Y fix_dvd_password.py OLD\scripts\ >nul 2>&1
move /Y force_update_password.py OLD\scripts\ >nul 2>&1
move /Y generar_*.py OLD\scripts\ >nul 2>&1
move /Y GENERAR_*.bat OLD\scripts\ >nul 2>&1
move /Y generate_translations.py OLD\scripts\ >nul 2>&1
move /Y gen_preguntas.py OLD\scripts\ >nul 2>&1
move /Y groq_helper.py OLD\scripts\ >nul 2>&1
move /Y INICIAR_CLOUDFLARE_SIMPLE.bat OLD\scripts\ >nul 2>&1
move /Y INICIAR_CLOUDFLARE_TEMPORAL.bat OLD\scripts\ >nul 2>&1
move /Y INICIAR_CON_CLOUDFLARE.bat OLD\scripts\ >nul 2>&1
move /Y INICIAR_DVD_CH.bat OLD\scripts\ >nul 2>&1
move /Y INICIAR_SERVIDOR.bat OLD\scripts\ >nul 2>&1
move /Y INICIAR_SERVIDOR_QUIEN_SOY.bat OLD\scripts\ >nul 2>&1
move /Y INICIAR_SERVIDOR_SIMPLE.bat OLD\scripts\ >nul 2>&1
move /Y INICIAR_SISTEMA_COMPLETO.bat OLD\scripts\ >nul 2>&1
move /Y INICIAR_WATCHDOG.bat OLD\scripts\ >nul 2>&1
move /Y INICIO.bat OLD\scripts\ >nul 2>&1
move /Y INSTALAR_*.bat OLD\scripts\ >nul 2>&1
move /Y install_autostart.bat OLD\scripts\ >nul 2>&1
move /Y listar_zonas_cloudflare.py OLD\scripts\ >nul 2>&1
move /Y opo_local.html OLD\scripts\ >nul 2>&1
move /Y PREPARAR_PARA_REINICIO.bat OLD\scripts\ >nul 2>&1
move /Y PROBAR_*.bat OLD\scripts\ >nul 2>&1
move /Y PROBAR_*.ps1 OLD\scripts\ >nul 2>&1
move /Y PRUEBA_COMPLETA.bat OLD\scripts\ >nul 2>&1
move /Y REACTIVAR_DEFENDER.bat OLD\scripts\ >nul 2>&1
move /Y REINICIAR_*.bat OLD\scripts\ >nul 2>&1
move /Y reset_*.py OLD\scripts\ >nul 2>&1
move /Y RESTART_*.bat OLD\scripts\ >nul 2>&1
move /Y restart_server.py OLD\scripts\ >nul 2>&1
move /Y restore_passwords_from_backup.py OLD\scripts\ >nul 2>&1
move /Y service_launcher.py OLD\scripts\ >nul 2>&1
move /Y SOLUCION_RAPIDA_TEMPORAL.bat OLD\scripts\ >nul 2>&1
move /Y start.py OLD\scripts\ >nul 2>&1
move /Y startdvdcoin.bat OLD\scripts\ >nul 2>&1
move /Y start_dvdcoin_hidden.vbs OLD\scripts\ >nul 2>&1
move /Y START_SERVER.bat OLD\scripts\ >nul 2>&1
move /Y TEST_BROWSER.html OLD\scripts\ >nul 2>&1
move /Y tunnel_info.json OLD\scripts\ >nul 2>&1
move /Y uninstall_autostart.bat OLD\scripts\ >nul 2>&1
move /Y update_remaining_translations.py OLD\scripts\ >nul 2>&1
move /Y verificacion_final.py OLD\scripts\ >nul 2>&1
move /Y VERIFICAR_*.bat OLD\scripts\ >nul 2>&1
move /Y verificar_*.py OLD\scripts\ >nul 2>&1
move /Y verify_dvd_password.py OLD\scripts\ >nul 2>&1
move /Y VER_*.bat OLD\scripts\ >nul 2>&1
echo ✅ Scripts obsoletos movidos

REM Mover logs
move /Y cloudflare_tunnel.log OLD\logs\ >nul 2>&1
move /Y cloudflare_tunnel_error.log OLD\logs\ >nul 2>&1
move /Y no_sleep.log OLD\logs\ >nul 2>&1
move /Y python_server.log OLD\logs\ >nul 2>&1
move /Y server.log OLD\logs\ >nul 2>&1
echo ✅ Logs movidos

echo.
echo ═══════════════════════════════════════════════════════════════════════════
echo   ✅ LIMPIEZA COMPLETADA
echo ═══════════════════════════════════════════════════════════════════════════
echo.
echo Todos los archivos innecesarios han sido movidos a OLD\
echo.
echo Archivos mantenidos (necesarios):
echo   • main.py
echo   • *.db (bases de datos)
echo   • cloudflared.exe
echo   • cloudflare-dvta-config.yml
echo   • cloudflare-tunnel-dvta.yml
echo   • configurar_dns_cloudflare_dvta.py
echo   • CONFIGURAR_EMAIL_CLOUDFLARE.bat
echo   • CONFIGURAR_TODO_DVTA.bat
echo   • CONFIGURAR_TUNNEL_DVTA.bat
echo   • crear_tunnel_dvta.py
echo   • INICIAR_SISTEMA_DVTA.bat
echo   • INICIAR_TUNNEL_DVTA.bat
echo   • MENU_PRINCIPAL.bat
echo   • REGISTROS_DNS_INFOMANIAK_DVTA_CH.txt
echo   • ai_helper.py
echo   • nssm.exe
echo   • Carpetas: static, src, data, backup, backup_30min
echo.
