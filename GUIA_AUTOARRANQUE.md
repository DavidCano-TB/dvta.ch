# 🔄 Guía de Auto-Arranque del Sistema DVDcoin

## 📋 Descripción

El sistema DVDcoin puede configurarse para iniciarse automáticamente al arrancar Windows, garantizando que los servicios estén siempre disponibles sin intervención manual.

---

## 🎯 Métodos de Auto-Arranque

Para máxima confiabilidad, el sistema utiliza **3 métodos diferentes**:

### 1. Tarea Programada de Windows (Principal)
- **Prioridad**: Alta
- **Confiabilidad**: ⭐⭐⭐⭐⭐
- **Descripción**: Usa el Programador de Tareas de Windows
- **Ventajas**:
  - Más robusto y profesional
  - Permite configuración avanzada
  - Se ejecuta incluso si el usuario no inicia sesión
  - Permite retrasos configurables

### 2. Registro de Windows (Respaldo)
- **Prioridad**: Media
- **Confiabilidad**: ⭐⭐⭐⭐
- **Descripción**: Añade entrada en el registro de Windows
- **Ventajas**:
  - Método tradicional y confiable
  - Se ejecuta al iniciar sesión
  - Fácil de verificar

### 3. Carpeta de Inicio (Adicional)
- **Prioridad**: Baja
- **Confiabilidad**: ⭐⭐⭐
- **Descripción**: Acceso directo en carpeta de Inicio
- **Ventajas**:
  - Método más simple
  - Visible para el usuario
  - Fácil de activar/desactivar manualmente

---

## 🚀 Configurar Auto-Arranque

### Paso 1: Ejecutar Script de Configuración

1. Haz clic derecho en: `CONFIGURAR_AUTOARRANQUE_COMPLETO.bat`
2. Selecciona: **"Ejecutar como administrador"**
3. Sigue las instrucciones en pantalla
4. Espera a que se configuren los 3 métodos

### Paso 2: Verificar Configuración

Ejecuta: `VERIFICAR_AUTOARRANQUE.bat`

Deberías ver:
```
✅ Tarea Programada: CONFIGURADA
✅ Registro de Windows: CONFIGURADO
✅ Carpeta de Inicio: CONFIGURADA

Métodos activos: 3 de 3
✅ AUTO-ARRANQUE COMPLETAMENTE CONFIGURADO
```

### Paso 3: Probar

**Opción A: Reiniciar Windows**
1. Reinicia tu PC
2. Espera ~1 minuto después del login
3. Verifica que se abran 2 ventanas:
   - "DVDExams Server - dvta.ch"
   - "Cloudflare Tunnel - dvta.ch"
4. Accede a: https://dvta.ch

**Opción B: Ejecutar Tarea Manualmente**
1. Abre: Programador de tareas (taskschd.msc)
2. Busca: "DVDcoin_AutoStart"
3. Haz clic derecho → Ejecutar
4. Verifica que se inicie correctamente

---

## 🛑 Desactivar Auto-Arranque

### Eliminar Completamente

1. Haz clic derecho en: `ELIMINAR_AUTOARRANQUE_COMPLETO.bat`
2. Selecciona: **"Ejecutar como administrador"**
3. Confirma la eliminación
4. Verifica con: `VERIFICAR_AUTOARRANQUE.bat`

### Desactivar Temporalmente

**Método 1: Deshabilitar Tarea**
1. Abre: Programador de tareas (taskschd.msc)
2. Busca: "DVDcoin_AutoStart"
3. Haz clic derecho → Deshabilitar

**Método 2: Eliminar Acceso Directo**
1. Presiona: Win + R
2. Escribe: `shell:startup`
3. Elimina: "DVDcoin System.lnk"

---

## ⏱️ Comportamiento del Auto-Arranque

### Secuencia de Inicio

1. **Login en Windows** → Sistema operativo carga
2. **+30 segundos** → Espera para que Windows termine de cargar
3. **Inicio de servicios** → Se ejecuta `ACTIVAR_DVTA_CH_AHORA.bat`
4. **+15-30 segundos** → Servicios se inician
5. **Total: ~1 minuto** → Sistema completamente operativo

### Ventanas que se Abren

- **"DVDExams Server - dvta.ch"**: Servidor Exams (puerto 8001)
- **"Cloudflare Tunnel - dvta.ch"**: Tunnel de Cloudflare

**Importante**: NO cierres estas ventanas. Puedes minimizarlas.

---

## 🔧 Solución de Problemas

### Problema: Auto-arranque no funciona

**Verificar**:
```bash
VERIFICAR_AUTOARRANQUE.bat
```

**Soluciones**:
1. Ejecuta: `CONFIGURAR_AUTOARRANQUE_COMPLETO.bat` (como admin)
2. Verifica permisos de administrador
3. Verifica que el archivo `ACTIVAR_DVTA_CH_AHORA.bat` existe
4. Revisa logs del Programador de Tareas

### Problema: Servicios no se inician correctamente

**Verificar**:
```bash
STATUS_DVTA.bat
```

**Soluciones**:
1. Verifica dependencias: `pip install -r modules\exams\requirements.txt`
2. Verifica puertos libres: `netstat -ano | findstr ":8001"`
3. Ejecuta manualmente: `ACTIVAR_DVTA_CH_AHORA.bat`
4. Revisa logs en las ventanas de servidor

### Problema: Múltiples instancias se inician

**Causa**: Los 3 métodos se ejecutan simultáneamente

**Solución**: El script detecta instancias existentes y no inicia duplicados

**Verificar**:
```bash
tasklist | findstr "python.exe"
tasklist | findstr "cloudflared.exe"
```

Si hay múltiples instancias:
```bash
taskkill /F /IM python.exe
taskkill /F /IM cloudflared.exe
ACTIVAR_DVTA_CH_AHORA.bat
```

---

## 📊 Verificación de Estado

### Comandos Útiles

**Ver estado de servicios**:
```bash
STATUS_DVTA.bat
```

**Monitor en tiempo real**:
```bash
MONITOR_SISTEMA.bat
```

**Test completo**:
```bash
TEST_COMPLETO_SISTEMA.bat
```

**Verificar auto-arranque**:
```bash
VERIFICAR_AUTOARRANQUE.bat
```

### Verificación Manual

**Tarea Programada**:
1. Abre: `taskschd.msc`
2. Busca: "DVDcoin_AutoStart"
3. Verifica: Estado = "Listo"

**Registro**:
1. Abre: `regedit`
2. Ve a: `HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run`
3. Busca: "DVDcoin_System"

**Carpeta de Inicio**:
1. Presiona: Win + R
2. Escribe: `shell:startup`
3. Busca: "DVDcoin System.lnk"

---

## 💡 Recomendaciones

### Para Uso en Producción

1. ✅ **Configura auto-arranque** con los 3 métodos
2. ✅ **Verifica después de cada reinicio** que todo funciona
3. ✅ **Configura monitoreo** con `MONITOR_SISTEMA.bat`
4. ✅ **Haz backups regulares** con `BACKUP_COMPLETO.bat`

### Para Desarrollo

1. ⚠️ **Considera desactivar auto-arranque** para evitar conflictos
2. ✅ **Inicia manualmente** con `ACTIVAR_DVTA_CH_AHORA.bat`
3. ✅ **Usa monitor** para ver logs en tiempo real

### Para Testing

1. ✅ **Desactiva auto-arranque temporalmente**
2. ✅ **Inicia servicios manualmente** cuando necesites
3. ✅ **Reactiva después de testing**

---

## 🔐 Seguridad

### Permisos Requeridos

- **Administrador**: Requerido para configurar/eliminar auto-arranque
- **Usuario normal**: Suficiente para ejecutar servicios manualmente

### Consideraciones

- Los scripts se ejecutan con los permisos del usuario que inicia sesión
- Las ventanas de servidor son visibles (no ocultas)
- Los logs son accesibles para debugging
- No se almacenan contraseñas en los scripts

---

## 📞 Ayuda Adicional

### Scripts Relacionados

- `CONFIGURAR_AUTOARRANQUE_COMPLETO.bat` - Configurar auto-arranque
- `ELIMINAR_AUTOARRANQUE_COMPLETO.bat` - Eliminar auto-arranque
- `VERIFICAR_AUTOARRANQUE.bat` - Verificar configuración
- `ACTIVAR_DVTA_CH_AHORA.bat` - Iniciar servicios manualmente
- `STATUS_DVTA.bat` - Ver estado de servicios

### Documentación

- `INICIO_AQUI.txt` - Guía de inicio rápido
- `LISTO_PARA_USAR.txt` - Guía visual
- `README_DVTA_CH.md` - Guía completa de dvta.ch
- `RESUMEN_EJECUTIVO_FINAL.md` - Resumen ejecutivo

---

**Última actualización**: 27 Mayo 2026  
**Versión**: 2.0  
**Estado**: ✅ Documentado y probado
