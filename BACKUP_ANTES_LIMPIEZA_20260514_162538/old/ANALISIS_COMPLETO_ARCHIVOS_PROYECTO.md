# 📋 ANÁLISIS COMPLETO DE ARCHIVOS DEL PROYECTO DVDCOIN

**Fecha de análisis:** Mayo 11, 2026  
**Proyecto:** DVDcoin Bank v4.0  
**Propósito:** Identificar archivos activos, obsoletos y dependencias

---

## 🎯 RESUMEN EJECUTIVO

### Estadísticas Generales
- **Archivos Python ejecutables:** ~80
- **Scripts BAT (Windows):** ~50
- **Archivos de documentación (MD):** ~120
- **Archivos de configuración:** ~15
- **Archivos de juegos (HTML):** ~10
- **Archivos obsoletos identificados:** ~60%

### Archivos Críticos Activos
1. **main.py** (raíz) - Servidor principal FastAPI
2. **start.py** - Launcher con ngrok
3. **service_launcher.py** - Servicio Windows
4. **requirements.txt** - Dependencias

---

## 📁 CATEGORIZACIÓN DE ARCHIVOS

### ✅ ARCHIVOS ACTIVOS Y ESENCIALES

#### 1. SERVIDOR PRINCIPAL
| Archivo | Llamado por | Propósito | Estado |
|---------|-------------|-----------|--------|
| **main.py** | start.py, startdvdcoin.bat, ARRANCAR.bat | Servidor FastAPI principal | ✅ ACTIVO |
| **start.py** | ARRANCAR.bat, service_launcher.py | Launcher con ngrok | ✅ ACTIVO |
| **service_launcher.py** | Servicio Windows (nssm) | Launcher para servicio | ✅ ACTIVO |
| **requirements.txt** | pip install | Dependencias del proyecto | ✅ ACTIVO |

#### 2. SCRIPTS DE ARRANQUE (BAT)
| Archivo | Propósito | Estado |
|---------|-----------|--------|
| **ARRANCAR.bat** | Inicia el servidor completo | ✅ ACTIVO |
| **ABRIR_APUESTAS.bat** | Abre sistema de apuestas | ✅ ACTIVO |
| **startdvdcoin.bat** | Alternativa de arranque | ✅ ACTIVO |
| **START_SERVER.bat** | Arranque simple | ✅ ACTIVO |
| **REINICIAR_TODO.bat** | Reinicio completo | ✅ ACTIVO |

#### 3. CONFIGURACIÓN
| Archivo | Propósito | Estado |
|---------|-----------|--------|
| **config/ngrok_config.txt** | Token y dominio ngrok | ✅ ACTIVO |
| **config/jwt_secret.txt** | Secret para JWT | ✅ ACTIVO |
| **config/master.txt** | Password maestro | ✅ ACTIVO |
| **.gitignore** | Exclusiones git | ✅ ACTIVO |

#### 4. BASES DE DATOS
| Archivo | Propósito | Estado |
|---------|-----------|--------|
| **data/users.db** | Usuarios y balances | ✅ ACTIVO |
| **data/transactions.db** | Transacciones | ✅ ACTIVO |
| **data/apuestas.db** | Sistema de apuestas | ✅ ACTIVO |
| **data/rights.db** | Permisos y roles | ✅ ACTIVO |
| **data/stats.db** | Estadísticas | ✅ ACTIVO |
| **data/opo.db** | Oposiciones | ✅ ACTIVO |
| **data/messages.db** | Mensajes y videollamadas | ✅ ACTIVO |

#### 5. JUEGOS IMPLEMENTADOS
| Juego | Archivos | Estado |
|-------|----------|--------|
| **Apuestas/Porras** | game_pages/apuestas/*.html | ✅ ACTIVO |
| **Millonario** | game_pages/millonario/game.html | ✅ ACTIVO |
| **Hundir la Flota** | game_pages/hundirlaflota/*.html | ✅ ACTIVO |
| **Pasapalabra** | game_pages/pasapalabra/game.html | ✅ ACTIVO |
| **Quién Soy** | game_pages/quiensoy/game.html | ✅ ACTIVO |
| **Cifras y Letras** | game_pages/cifrasletras/game.html | ✅ ACTIVO |
| **Votaciones** | game_pages/votaciones/votaciones.html | ✅ ACTIVO |

#### 6. WATCHDOG Y MONITOREO
| Archivo | Llamado por | Propósito | Estado |
|---------|-------------|-----------|--------|
| **watchdog_monitor.py** | Tarea programada | Monitor de servidor | ⚠️ OPCIONAL |
| **watchdog.py** | Manual | Monitor alternativo | ⚠️ OPCIONAL |
| **INSTALAR_WATCHDOG.bat** | Manual | Instala watchdog | ⚠️ OPCIONAL |
| **VER_ESTADO_WATCHDOG.bat** | Manual | Estado watchdog | ⚠️ OPCIONAL |

---

### ⚠️ ARCHIVOS DE UTILIDAD (Uso Ocasional)

#### 1. SCRIPTS DE VERIFICACIÓN
| Archivo | Propósito | Uso | Estado |
|---------|-----------|-----|--------|
| **verificar_sistema_votaciones.py** | Verifica votaciones | Manual | ⚠️ ÚTIL |
| **verificar_sistema_pagos.py** | Verifica pagos | Manual | ⚠️ ÚTIL |
| **verificar_todas_porras.py** | Verifica porras | Manual | ⚠️ ÚTIL |
| **verificar_nebulosa_superadmin.py** | Verifica permisos | Manual | ⚠️ ÚTIL |
| **check_bets.py** | Verifica apuestas | Manual | ⚠️ ÚTIL |
| **diagnostico_votaciones.py** | Diagnóstico votaciones | Manual | ⚠️ ÚTIL |

#### 2. SCRIPTS DE LIMPIEZA
| Archivo | Propósito | Uso | Estado |
|---------|-----------|-----|--------|
| **limpiar_archivos_huerfanos.py** | Limpia HTML huérfanos | Manual | ⚠️ ÚTIL |
| **limpiar_archivos_huerfanos_auto.py** | Limpieza automática | Manual | ⚠️ ÚTIL |
| **limpiar_porras_no_utilizadas.py** | Limpia porras | Manual | ⚠️ ÚTIL |
| **limpiar_votaciones.py** | Limpia votaciones | Manual | ⚠️ ÚTIL |

#### 3. SCRIPTS DE REPARACIÓN
| Archivo | Propósito | Uso | Estado |
|---------|-----------|-----|--------|
| **restore_nebulosa_superadmin.py** | Restaura permisos | Manual | ⚠️ ÚTIL |
| **remove_nebulosa_privileges.py** | Elimina permisos | Manual | ⚠️ ÚTIL |
| **fix_fstrings.py** | Corrige f-strings | Manual | ⚠️ ÚTIL |
| **corregir_sintaxis_transacciones.py** | Corrige sintaxis | Manual | ⚠️ ÚTIL |

#### 4. SCRIPTS DE GENERACIÓN
| Archivo | Propósito | Uso | Estado |
|---------|-----------|-----|--------|
| **generar_preguntas_pasapalabra.py** | Genera preguntas | Manual | ⚠️ ÚTIL |
| **generar_preguntas_dificiles_millonario.py** | Genera preguntas | Manual | ⚠️ ÚTIL |
| **generar_1000_preguntas_millonario.py** | Genera preguntas | Manual | ⚠️ ÚTIL |
| **generar_100_bloques_millonario.py** | Genera bloques | Manual | ⚠️ ÚTIL |

---

### ❌ ARCHIVOS OBSOLETOS (Pueden eliminarse)

#### 1. SCRIPTS DE ACTUALIZACIÓN (Ya aplicados)
| Archivo | Razón de obsolescencia |
|---------|------------------------|
| **actualizar_porras_con_votos_y_boton.py** | Cambios ya aplicados en main.py |
| **actualizar_porras_dvd.py** | Cambios ya aplicados |
| **actualizar_porras_v2.py** | Versión antigua |
| **actualizar_todas_porras.py** | Ya ejecutado |
| **actualizar_transacciones.py** | Ya aplicado |
| **actualizar_validacion_deadline.py** | Ya aplicado |
| **aplicar_cambios_transacciones_final.py** | Ya aplicado |
| **aplicar_verificacion_deadline.py** | Ya aplicado |
| **agregar_columnas_fecha_votaciones.py** | Ya aplicado |

#### 2. SCRIPTS DE MIGRACIÓN (Ya ejecutados)
| Archivo | Razón de obsolescencia |
|---------|------------------------|
| **crear_tabla_millonario_tracking.py** | Tabla ya creada |
| **crear_tabla_votaciones.py** | Tabla ya creada |
| **crear_tablas_votaciones.py** | Tablas ya creadas |
| **crear_nombres_descriptivos_porras_existentes.py** | Ya ejecutado |
| **implement_soft_delete.py** | Ya implementado |

#### 3. SCRIPTS DE RECUPERACIÓN (Casos específicos resueltos)
| Archivo | Razón de obsolescencia |
|---------|------------------------|
| **recuperar_porra_7.py** | Caso específico resuelto |
| **recuperar_porra_7_final.py** | Caso específico resuelto |
| **recuperar_porra_italia.py** | Caso específico resuelto |
| **restore_italy_porra_direct.py** | Caso específico resuelto |
| **restore_porra_7_complete.py** | Caso específico resuelto |
| **corregir_porras_pasadas.py** | Ya ejecutado |
| **corregir_votaciones_final.py** | Ya ejecutado |
| **fix_porra_7.py** | Caso específico resuelto |

#### 4. SCRIPTS DE AUDITORÍA (Una sola vez)
| Archivo | Razón de obsolescencia |
|---------|------------------------|
| **auditoria_completa_apuestas.py** | Auditoría completada |
| **pagar_ganadores_pendientes.py** | Pagos completados |
| **verificar_ganadores_reales.py** | Verificación completada |
| **verificar_balances_completo.py** | Verificación completada |
| **check_apuestas_table.py** | Verificación completada |
| **check_votaciones_table.py** | Verificación completada |
| **verify_porra_7.py** | Caso específico resuelto |

#### 5. SCRIPTS DE TEST (Desarrollo)
| Archivo | Razón de obsolescencia |
|---------|------------------------|
| **test_admin_panel.py** | Test de desarrollo |
| **test_apuestas_page.py** | Test de desarrollo |
| **test_cerrar_resolver.py** | Test de desarrollo |
| **test_hundirlaflota_setup.py** | Test de desarrollo |
| **test_mis_apuestas.py** | Test de desarrollo |
| **test_porra.py** | Test de desarrollo |
| **test_sistemas_completo.py** | Test de desarrollo |
| **test_voting_system.py** | Test de desarrollo |

#### 6. SCRIPTS DE SINCRONIZACIÓN (Ya sincronizados)
| Archivo | Razón de obsolescencia |
|---------|------------------------|
| **sincronizar_y_limpiar_main.py** | Archivos ya sincronizados |
| **forzar_recarga_servidor.py** | No necesario con reinicio normal |

#### 7. SCRIPTS BAT OBSOLETOS
| Archivo | Razón de obsolescencia |
|---------|------------------------|
| **APLICAR_CAMBIOS.bat** | Cambios ya aplicados |
| **APLICAR_CAMBIOS_NEBULOSA.bat** | Cambios ya aplicados |
| **APLICAR_CAMBIOS_VOTACIONES.bat** | Cambios ya aplicados |
| **REGENERAR_PORRAS.bat** | Ya ejecutado |
| **REGENERAR_PORRAS_URGENTE.bat** | Ya ejecutado |
| **PROBAR_NEBULOSA_SUPERADMIN.md** | Prueba completada |
| **PROBAR_VIDEO_GRUPAL.bat** | Prueba completada |
| **PROBAR_HUNDIR_LA_FLOTA.bat** | Prueba completada |
| **TEST_APUESTAS.bat** | Test completado |

---

### 📄 DOCUMENTACIÓN

#### 1. DOCUMENTACIÓN ACTIVA (Referencia)
| Archivo | Propósito | Estado |
|---------|-----------|--------|
| **README.md** | Documentación principal | ✅ ACTIVO |
| **QUICK_START.md** | Guía rápida | ✅ ACTIVO |
| **INSTRUCCIONES_ARRANQUE.md** | Instrucciones de inicio | ✅ ACTIVO |
| **GUIA_COMPLETA_APUESTAS_USUARIOS.md** | Guía de apuestas | ✅ ACTIVO |
| **README_SISTEMA_APUESTAS.md** | Sistema de apuestas | ✅ ACTIVO |
| **INDICE_MAESTRO_DOCUMENTACION.md** | Índice general | ✅ ACTIVO |

#### 2. DOCUMENTACIÓN DE IMPLEMENTACIÓN (Histórica)
Estos archivos documentan cambios ya aplicados. Son útiles para entender el historial pero no son necesarios para el funcionamiento:

| Categoría | Archivos | Estado |
|-----------|----------|--------|
| **Hundir la Flota** | HUNDIR_LA_FLOTA_*.md (15 archivos) | 📚 HISTÓRICO |
| **Votaciones** | VOTACIONES_*.md (10 archivos) | 📚 HISTÓRICO |
| **Apuestas** | APUESTAS_*.md, SISTEMA_APUESTAS_*.md (20 archivos) | 📚 HISTÓRICO |
| **Millonario** | MILLONARIO_*.md (5 archivos) | 📚 HISTÓRICO |
| **Nebulosa** | NEBULOSA_*.md (5 archivos) | 📚 HISTÓRICO |
| **Verificaciones** | VERIFICACION_*.md (10 archivos) | 📚 HISTÓRICO |
| **Resúmenes** | RESUMEN_*.md (25 archivos) | 📚 HISTÓRICO |
| **Cambios** | CAMBIOS_*.md (15 archivos) | 📚 HISTÓRICO |

**Total documentos históricos:** ~120 archivos MD

---

### 🗂️ ARCHIVOS DE SISTEMA

#### 1. ARCHIVOS GIT
| Archivo/Carpeta | Propósito | Estado |
|-----------------|-----------|--------|
| **.git/** | Repositorio git | ✅ SISTEMA |
| **.gitignore** | Exclusiones | ✅ ACTIVO |
| **.github/** | GitHub Actions | ✅ ACTIVO |

#### 2. ARCHIVOS IDE
| Archivo/Carpeta | Propósito | Estado |
|-----------------|-----------|--------|
| **.vscode/** | Configuración VS Code | ✅ SISTEMA |
| **.vs/** | Configuración Visual Studio | ✅ SISTEMA |
| **.kiro/** | Configuración Kiro | ✅ SISTEMA |

#### 3. ENTORNO VIRTUAL
| Archivo/Carpeta | Propósito | Estado |
|-----------------|-----------|--------|
| **venv/** | Entorno virtual Python | ✅ SISTEMA |
| **__pycache__/** | Cache Python | ✅ SISTEMA |

#### 4. LOGS
| Archivo | Propósito | Estado |
|---------|-----------|--------|
| **server.log** | Log del servidor | ✅ ACTIVO |
| **ngrok_*.log** | Logs de ngrok (23 archivos) | ⚠️ LIMPIAR |
| **watchdog.log** | Log watchdog | ⚠️ OPCIONAL |
| **no_sleep.log** | Log no-sleep | ⚠️ OPCIONAL |

#### 5. EJECUTABLES
| Archivo | Propósito | Estado |
|---------|-----------|--------|
| **ngrok.exe** | Cliente ngrok | ✅ ACTIVO |
| **nssm.exe** | Gestor servicios Windows | ✅ ACTIVO |
| **tools/ngrok.exe** | Copia ngrok | ⚠️ DUPLICADO |
| **tools/nssm.exe** | Copia nssm | ⚠️ DUPLICADO |

---

## 🔗 MAPA DE DEPENDENCIAS

### Flujo de Arranque Principal
```
Usuario ejecuta → ARRANCAR.bat
                    ↓
                 start.py
                    ↓
        ┌───────────┴───────────┐
        ↓                       ↓
    main.py                 ngrok.exe
    (servidor)              (túnel)
        ↓
    FastAPI + Uvicorn
        ↓
    ┌───┴───┬───────┬────────┬────────┐
    ↓       ↓       ↓        ↓        ↓
  users.db  tx.db  bets.db  opo.db  stats.db
```

### Archivos que Llaman a main.py
1. **start.py** - Launcher principal
2. **startdvdcoin.bat** - Arranque directo
3. **ARRANCAR.bat** - Vía start.py
4. **service_launcher.py** - Servicio Windows
5. **_do_restart.py** - Reinicio automático
6. **_restart_all.py** - Reinicio completo
7. **watchdog.py** - Monitor
8. **REINICIAR_TODO.bat** - Reinicio manual

### Archivos que NO son Llamados por Nadie
- Todos los scripts de actualización (actualizar_*.py)
- Todos los scripts de recuperación (recuperar_*.py)
- Todos los scripts de test (test_*.py)
- Todos los scripts de verificación (verificar_*.py)
- Todos los scripts de limpieza (limpiar_*.py)
- Todos los scripts de generación (generar_*.py)

**Estos archivos son herramientas de mantenimiento que se ejecutan manualmente cuando se necesitan.**

---

## 📊 ESTADÍSTICAS DE OBSOLESCENCIA

### Por Tipo de Archivo
| Tipo | Total | Activos | Útiles | Obsoletos | % Obsoleto |
|------|-------|---------|--------|-----------|------------|
| Python (.py) | ~80 | 10 | 25 | 45 | 56% |
| BAT (.bat) | ~50 | 15 | 10 | 25 | 50% |
| Markdown (.md) | ~120 | 10 | 0 | 110 | 92% |
| HTML | ~10 | 10 | 0 | 0 | 0% |
| Config | ~15 | 15 | 0 | 0 | 0% |

### Por Categoría
| Categoría | Archivos | Estado |
|-----------|----------|--------|
| **Esenciales** | 20 | ✅ Mantener |
| **Útiles ocasionales** | 45 | ⚠️ Mantener |
| **Obsoletos** | 180 | ❌ Pueden eliminarse |
| **Sistema** | 50 | ✅ No tocar |

---

## 🎯 RECOMENDACIONES

### 1. ARCHIVOS A MANTENER (Esenciales)
```
main.py
start.py
service_launcher.py
requirements.txt
ARRANCAR.bat
ABRIR_APUESTAS.bat
startdvdcoin.bat
config/
data/
game_pages/
static/
```

### 2. ARCHIVOS A MANTENER (Útiles)
```
verificar_*.py (todos)
limpiar_*.py (todos)
generar_*.py (todos)
restore_nebulosa_superadmin.py
check_*.py (todos)
```

### 3. ARCHIVOS A ELIMINAR (Obsoletos)
```
actualizar_*.py (todos)
aplicar_*.py (todos)
recuperar_*.py (todos)
crear_tabla_*.py (todos)
fix_*.py (todos)
test_*.py (todos)
corregir_*.py (todos)
*_COMPLETO.md (todos)
*_FINAL.md (todos)
*_IMPLEMENTADO.md (todos)
RESUMEN_*.md (todos)
CAMBIOS_*.md (todos)
ngrok_*.log (23 archivos)
```

### 4. DOCUMENTACIÓN A CONSOLIDAR
Crear un único archivo de documentación que reemplace los ~110 archivos MD históricos:
- **DOCUMENTACION_COMPLETA.md** - Guía unificada
- **HISTORIAL_CAMBIOS.md** - Resumen de cambios importantes

### 5. LIMPIEZA DE LOGS
```bash
# Eliminar logs antiguos de ngrok
del ngrok_*.log

# Mantener solo:
server.log (actual)
watchdog.log (si se usa)
```

---

## 📝 NOTAS IMPORTANTES

### Archivos Duplicados
1. **main.py** existe en raíz y en **src/main.py**
   - El activo es el de la raíz
   - src/main.py es un backup sincronizado
   - Recomendación: Eliminar src/main.py

2. **start.py** existe en raíz y en **src/start.py**
   - El activo es el de la raíz
   - src/start.py es una copia
   - Recomendación: Eliminar src/start.py

3. **ngrok.exe** y **nssm.exe** están duplicados en tools/
   - Recomendación: Mantener solo en raíz

### Proyecto Raspberry Pi
La carpeta **dvdcoin_pi/** contiene una versión completa del proyecto para Raspberry Pi:
- Estado: ✅ ACTIVO
- Propósito: Despliegue en Raspberry Pi
- Mantener: Sí, es una versión independiente

### Bases de Datos Legacy
- **dvdcoin.db** → Renombrado a **dvdcoin.db.migrated**
- **apuestas.db** (raíz) → Duplicado de data/apuestas.db
- Recomendación: Eliminar duplicados

---

## ✅ CONCLUSIÓN

### Resumen de Limpieza Propuesta
- **Archivos a eliminar:** ~180 (60% del total)
- **Espacio a liberar:** ~50-100 MB (principalmente logs y docs)
- **Archivos a mantener:** ~115 (40% del total)

### Impacto de la Limpieza
- ✅ Proyecto más limpio y mantenible
- ✅ Más fácil de navegar
- ✅ Documentación consolidada
- ✅ Sin pérdida de funcionalidad
- ✅ Historial preservado en git

### Próximos Pasos
1. Hacer backup completo del proyecto
2. Crear rama git para limpieza
3. Eliminar archivos obsoletos
4. Consolidar documentación
5. Limpiar logs antiguos
6. Actualizar .gitignore
7. Probar que todo funciona
8. Merge a main

---

**Generado por:** Kiro AI  
**Fecha:** Mayo 11, 2026  
**Versión:** 1.0
