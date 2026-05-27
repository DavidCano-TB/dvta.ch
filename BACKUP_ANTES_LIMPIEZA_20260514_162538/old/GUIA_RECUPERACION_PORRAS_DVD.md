# 🔄 Guía de Recuperación de Porras para DVD

## ¡Sistema de Recuperación Implementado! ✅

---

## 📋 ¿Qué es esto?

Ahora puedes **recuperar porras eliminadas** de dos formas:

1. **Interfaz Web** - Fácil y visual
2. **Script Python** - Rápido y directo

---

## 🌐 MÉTODO 1: Interfaz Web (Recomendado)

### Paso 1: Accede al Sistema de Apuestas
- Abre el sistema de apuestas en tu navegador
- Asegúrate de estar logueado como **DVD**

### Paso 2: Ve a la Pestaña "Deleted"
- Verás una nueva pestaña: **🗑️ Deleted**
- Esta pestaña **solo es visible para ti (DVD)**
- Haz clic en ella

### Paso 3: Visualiza las Porras Eliminadas
Verás todas las porras eliminadas con:
- ❌ Borde rojo (para identificarlas fácilmente)
- 📝 Título y descripción
- 👤 Creador
- 🗑️ Fecha de eliminación
- 📅 Fecha de creación
- 🎯 Tipo de apuesta
- 📊 Estado cuando fue eliminada

### Paso 4: Restaurar una Porra
Cada porra eliminada tiene dos botones:

#### 🔄 Botón "Restore"
- Haz clic en **"🔄 Restore"**
- Confirma la restauración
- ✅ ¡La porra vuelve a estar visible para todos!

#### 👁️ Botón "View Details"
- Haz clic en **"👁️ View Details"**
- Verás todos los detalles:
  - ID de la porra
  - Todas las opciones de apuesta
  - Fechas completas
  - Información del creador

---

## 💻 MÉTODO 2: Script Python (Alternativo)

### Para Recuperar la Porra de Italia (Lluvia)

Ejecuta este comando en la terminal:

```bash
python restore_italy_porra_direct.py
```

### ¿Qué hace el script?

1. 🔍 Busca porras eliminadas sobre "lluvia", "italia" o "milán"
2. 📋 Muestra todas las que encuentra
3. 🔄 Las restaura automáticamente
4. ✅ Confirma que fueron restauradas

### Salida del Script

```
============================================================
RESTORING ITALY RAIN PORRA - DIRECT SQL METHOD
============================================================

🔍 Searching for deleted porras about rain/Italy/Milan...

✅ Found 1 deleted porra(s) about rain/Italy/Milan:

ID: 42
Title: ¿Lloverá mañana en Milán?
Description: Apuesta sobre el clima en Italia
Creator: dvd
Status: abierta
Deleted: 2026-05-05 10:30:00
------------------------------------------------------------

🔄 RESTORING PORRA ID 42...
✅ Porra ID 42 restored successfully!
   Title: ¿Lloverá mañana en Milán?
   It is now visible again in the betting system.

============================================================
PROCESS COMPLETED
============================================================
```

---

## 🎯 Características del Sistema

### ✅ Ventajas

1. **No se pierde nada** - Las porras eliminadas se guardan
2. **Recuperación fácil** - Un clic y vuelven
3. **Solo para DVD** - Nadie más puede ver o restaurar
4. **Información completa** - Ves todos los detalles antes de restaurar
5. **Seguro** - Pide confirmación antes de restaurar

### 🔒 Seguridad

- ✅ Solo **DVD** puede ver porras eliminadas
- ✅ Solo **DVD** puede restaurar porras
- ✅ Los usuarios normales no ven nada
- ✅ Las porras eliminadas están ocultas en todas las listas

---

## 📊 Estados de las Porras

### Porra Activa (Normal)
- ✅ Visible para todos
- ✅ Aparece en las listas normales
- ✅ Los usuarios pueden apostar

### Porra Eliminada (Soft-Delete)
- ❌ Invisible para usuarios normales
- ✅ Visible solo para DVD en pestaña "Deleted"
- 🔄 Puede ser restaurada
- 💾 Todos los datos se conservan

### Porra Restaurada
- ✅ Vuelve a estar visible para todos
- ✅ Aparece en las listas normales
- ✅ Mantiene todo su historial
- ✅ Los usuarios pueden volver a apostar (si está abierta)

---

## 🚀 Casos de Uso

### Caso 1: Eliminaste una porra por error
1. Ve a la pestaña "🗑️ Deleted"
2. Encuentra la porra
3. Haz clic en "🔄 Restore"
4. ¡Listo! Vuelve a estar activa

### Caso 2: Quieres revisar una porra antes de restaurarla
1. Ve a la pestaña "🗑️ Deleted"
2. Haz clic en "👁️ View Details"
3. Revisa toda la información
4. Si quieres restaurarla, haz clic en "🔄 Restore"

### Caso 3: Necesitas restaurar rápidamente desde terminal
1. Ejecuta: `python restore_italy_porra_direct.py`
2. El script busca y restaura automáticamente
3. ¡Listo en segundos!

---

## ❓ Preguntas Frecuentes

### ¿Puedo ver quién eliminó una porra?
Sí, en los detalles verás el creador y la fecha de eliminación.

### ¿Se pierden las apuestas cuando elimino una porra?
No, todo se conserva. Al restaurar, las apuestas siguen ahí.

### ¿Puedo eliminar permanentemente una porra?
Actualmente no. Todas las eliminaciones son "soft-delete" (recuperables).

### ¿Los usuarios normales pueden ver porras eliminadas?
No, solo DVD puede verlas y restaurarlas.

### ¿Qué pasa si restauro una porra finalizada?
Vuelve a estar visible con su estado "finalizada" y los ganadores ya pagados.

---

## 🛠️ Solución de Problemas

### No veo la pestaña "Deleted"
- ✅ Verifica que estás logueado como **DVD**
- ✅ Recarga la página
- ✅ Limpia la caché del navegador

### El botón "Restore" no funciona
- ✅ Verifica tu conexión a internet
- ✅ Mira la consola del navegador (F12)
- ✅ Verifica que el servidor esté corriendo

### El script Python da error
- ✅ Verifica que estás en el directorio correcto
- ✅ Verifica que existe `data/apuestas.db`
- ✅ Ejecuta: `python --version` (debe ser Python 3)

---

## 📞 Soporte

Si tienes problemas:

1. Revisa esta guía
2. Verifica los logs del servidor
3. Usa el script Python como alternativa
4. Contacta al equipo de desarrollo

---

## 🎉 ¡Disfruta del Sistema de Recuperación!

Ahora nunca más perderás una porra por error. Todo está guardado y puede ser recuperado fácilmente.

**¡Feliz gestión de apuestas!** 🎲💰

---

**Fecha de Implementación:** 5 de Mayo, 2026
**Versión:** 1.0
**Estado:** ✅ Producción
