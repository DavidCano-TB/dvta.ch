╔═══════════════════════════════════════════════════════════════════════════╗
║                                                                           ║
║                    🐕 DVDcoin Watchdog Monitor                           ║
║                   Sistema de Monitoreo Automático                        ║
║                                                                           ║
╚═══════════════════════════════════════════════════════════════════════════╝

┌───────────────────────────────────────────────────────────────────────────┐
│  📋 ¿QUÉ HACE?                                                            │
└───────────────────────────────────────────────────────────────────────────┘

  ✅ Verifica el servidor cada 5 minutos
  ✅ Detecta 6 tipos de fallos diferentes
  ✅ Intenta reiniciar el servicio automáticamente
  ✅ Reinicia el PC si detecta 2 fallos consecutivos (10 min)
  ✅ Se inicia automáticamente al arrancar Windows
  ✅ Registra todo en logs detallados


┌───────────────────────────────────────────────────────────────────────────┐
│  🚀 INSTALACIÓN RÁPIDA                                                    │
└───────────────────────────────────────────────────────────────────────────┘

  1. Ejecuta como ADMINISTRADOR:
     
     ► INSTALAR_WATCHDOG.bat

  2. Verifica que funciona:
     
     ► VER_ESTADO_WATCHDOG.bat

  ¡Listo! El watchdog ya está protegiendo tu servidor.


┌───────────────────────────────────────────────────────────────────────────┐
│  🔍 QUÉ VERIFICA                                                          │
└───────────────────────────────────────────────────────────────────────────┘

  1. Puerto 8000           → Servidor escuchando
  2. Procesos Python       → Aplicación corriendo
  3. /api/health           → Servidor respondiendo
  4. /api/ice-servers      → WebRTC funcionando
  5. /api/rooms/list       → Sistema de salas OK
  6. URL Ngrok             → Acceso público activo


┌───────────────────────────────────────────────────────────────────────────┐
│  ⏱️ LÍNEA DE TIEMPO                                                       │
└───────────────────────────────────────────────────────────────────────────┘

  Minuto 0:  ✅ Verificación OK → Esperar 5 minutos
  Minuto 5:  ❌ FALLO (1/2)    → Esperar 5 minutos
  Minuto 10: ❌ FALLO (2/2)    → Intentar reiniciar servicio
                                 ↓
                          ¿Se recuperó?
                                 ↓
                    SÍ → Continuar    NO → REINICIAR PC


┌───────────────────────────────────────────────────────────────────────────┐
│  🎮 COMANDOS DISPONIBLES                                                  │
└───────────────────────────────────────────────────────────────────────────┘

  ► INSTALAR_WATCHDOG.bat      Instalar y configurar
  ► VER_ESTADO_WATCHDOG.bat    Ver estado actual y logs
  ► INICIAR_WATCHDOG.bat       Iniciar manualmente
  ► DETENER_WATCHDOG.bat       Detener temporalmente
  ► DESINSTALAR_WATCHDOG.bat   Desinstalar completamente


┌───────────────────────────────────────────────────────────────────────────┐
│  📝 ARCHIVOS IMPORTANTES                                                  │
└───────────────────────────────────────────────────────────────────────────┘

  watchdog_monitor.py          → Script principal (Python)
  logs/watchdog.log            → Registro de actividad
  INSTRUCCIONES_WATCHDOG.md    → Documentación completa


┌───────────────────────────────────────────────────────────────────────────┐
│  ⚙️ CONFIGURACIÓN                                                         │
└───────────────────────────────────────────────────────────────────────────┘

  Intervalo de verificación:    5 minutos
  Fallos antes de reiniciar:    2 consecutivos
  Tiempo total:                 10 minutos
  Delay de reinicio:            10 segundos
  Usuario de la tarea:          SYSTEM
  Prioridad:                    Alta


┌───────────────────────────────────────────────────────────────────────────┐
│  📊 EJEMPLO DE LOG                                                        │
└───────────────────────────────────────────────────────────────────────────┘

  2026-04-29 19:00:00 [INFO] Iniciando verificación completa...
  2026-04-29 19:00:00 [INFO]   Puerto 8000: ✅ OK
  2026-04-29 19:00:00 [INFO]   Procesos Python: ✅ OK
  2026-04-29 19:00:01 [INFO]   Endpoint /api/health: ✅ OK
  2026-04-29 19:00:01 [INFO]   Endpoint /api/ice-servers: ✅ OK
  2026-04-29 19:00:01 [INFO]   Endpoint /api/rooms/list: ✅ OK
  2026-04-29 19:00:02 [INFO]   URL Ngrok: ✅ OK
  2026-04-29 19:00:02 [INFO] ✅ Todas las verificaciones pasaron
  2026-04-29 19:00:02 [INFO] Próxima verificación en 5 minutos...


┌───────────────────────────────────────────────────────────────────────────┐
│  ⚠️ IMPORTANTE                                                            │
└───────────────────────────────────────────────────────────────────────────┘

  • Requiere permisos de ADMINISTRADOR para instalar
  • El PC se reiniciará automáticamente si detecta fallos
  • Puedes cancelar el reinicio con: shutdown /a
  • Detén el watchdog antes de hacer mantenimiento
  • Los logs pueden crecer, límpialos periódicamente


┌───────────────────────────────────────────────────────────────────────────┐
│  🔧 SOLUCIÓN DE PROBLEMAS                                                 │
└───────────────────────────────────────────────────────────────────────────┘

  Problema: No se inicia automáticamente
  Solución: Reinstalar con DESINSTALAR_WATCHDOG.bat + INSTALAR_WATCHDOG.bat

  Problema: Se detiene solo
  Solución: Revisar logs/watchdog.log para ver errores

  Problema: PC se reinicia sin razón
  Solución: Revisar log antes del reinicio, aumentar MAX_FAILURES

  Problema: No detecta fallos reales
  Solución: Verificar configuración en watchdog_monitor.py


┌───────────────────────────────────────────────────────────────────────────┐
│  📞 SOPORTE                                                               │
└───────────────────────────────────────────────────────────────────────────┘

  1. Revisa el log:
     notepad logs\watchdog.log

  2. Verifica el estado:
     VER_ESTADO_WATCHDOG.bat

  3. Lee la documentación completa:
     INSTRUCCIONES_WATCHDOG.md


┌───────────────────────────────────────────────────────────────────────────┐
│  ✅ CHECKLIST DE INSTALACIÓN                                             │
└───────────────────────────────────────────────────────────────────────────┘

  [ ] Ejecutar INSTALAR_WATCHDOG.bat como administrador
  [ ] Verificar que la tarea programada esté creada
  [ ] Iniciar el watchdog
  [ ] Verificar que el proceso esté corriendo
  [ ] Revisar el log para confirmar que funciona
  [ ] Probar deteniendo el servidor manualmente
  [ ] Verificar que el watchdog detecte el fallo


╔═══════════════════════════════════════════════════════════════════════════╗
║                                                                           ║
║  🎯 El watchdog está diseñado para mantener tu servidor funcionando      ║
║     24/7 sin intervención manual. ¡Instálalo y olvídate!                ║
║                                                                           ║
╚═══════════════════════════════════════════════════════════════════════════╝

Versión: 1.0
Fecha: 29 de abril de 2026
