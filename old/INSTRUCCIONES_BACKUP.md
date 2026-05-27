# Sistema de Backup Automático de Bases de Datos

## 📋 Descripción

Sistema automático de backup que:
- ✅ Realiza copias de seguridad de todas las bases de datos
- ✅ Guarda los backups en la carpeta `backup/`
- ✅ Mantiene solo los últimos 7 días de backups
- ✅ Purga automáticamente los backups más antiguos
- ✅ Se ejecuta automáticamente una vez al día (3:00 AM)
- ✅ Verifica la integridad de las bases de datos antes y después del backup

## 🚀 Configuración Inicial

### Paso 1: Configurar el Backup Automático

1. **Ejecutar como Administrador**: `CONFIGURAR_BACKUP_AUTOMATICO.bat`
   - Haz clic derecho → "Ejecutar como administrador"
   - Esto creará una tarea programada en Windows
   - El backup se ejecutará automáticamente todos los días a las 3:00 AM

### Paso 2: Limpiar Backups Antiguos del Directorio Principal

1. **Ejecutar**: `LIMPIAR_BACKUPS_ANTIGUOS.bat`
   - Esto eliminará los archivos de backup antiguos de la carpeta `data/`
   - Te pedirá confirmación antes de eliminar
   - Liberará espacio en disco

## 📁 Estructura de Backups

```
dvdcoin/
├── backup/                    # Carpeta de backups (nueva)
│   ├── 2026-05-14/           # Backup del 14 de mayo
│   │   ├── dvdcoin.db
│   │   ├── users.db
│   │   ├── apuestas.db
│   │   └── ...
│   ├── 2026-05-13/           # Backup del 13 de mayo
│   └── ...                   # Hasta 7 días atrás
├── data/                      # Bases de datos activas
│   ├── dvdcoin.db            # Base de datos principal
│   ├── users.db              # Usuarios
│   └── ...
└── logs/
    └── backup.log            # Log de operaciones de backup
```

## 🔧 Uso Manual

### Ejecutar Backup Manualmente

```batch
EJECUTAR_BACKUP_MANUAL.bat
```

Esto ejecutará el backup inmediatamente sin esperar a la tarea programada.

### Limpiar Backups Antiguos

```batch
LIMPIAR_BACKUPS_ANTIGUOS.bat
```

Elimina archivos de backup antiguos del directorio `data/`:
- `dvdcoin_2026-03-20_09-39.db` (backups con fecha)
- `messages - Copie.db` (copias)
- `users_backup.db` (backups explícitos)

## 📊 Bases de Datos Respaldadas

El sistema hace backup de las siguientes bases de datos:

1. `dvdcoin.db` - Base de datos principal
2. `users.db` - Usuarios
3. `apuestas.db` - Sistema de apuestas
4. `messages.db` - Mensajes
5. `opo.db` - Oposiciones
6. `oposiciones.db` - Datos de oposiciones
7. `rights.db` - Permisos
8. `stats.db` - Estadísticas
9. `transactions.db` - Transacciones
10. `votaciones.db` - Votaciones

## 🔍 Verificación

### Ver el Estado de la Tarea Programada

```cmd
schtasks /Query /TN "DVDCoin_Backup_Diario" /V /FO LIST
```

### Ejecutar la Tarea Manualmente

```cmd
schtasks /Run /TN "DVDCoin_Backup_Diario"
```

### Ver el Log de Backups

El archivo `logs/backup.log` contiene el historial de todas las operaciones de backup.

## 🛠️ Gestión de la Tarea Programada

### Modificar la Hora de Ejecución

Si deseas cambiar la hora de ejecución (por defecto 3:00 AM):

1. Abre el Programador de Tareas de Windows
2. Busca la tarea: `DVDCoin_Backup_Diario`
3. Haz clic derecho → Propiedades
4. En la pestaña "Desencadenadores", modifica la hora

### Desactivar el Backup Automático

```cmd
schtasks /Delete /TN "DVDCoin_Backup_Diario" /F
```

### Reactivar el Backup Automático

Ejecuta nuevamente: `CONFIGURAR_BACKUP_AUTOMATICO.bat` como Administrador

## 📈 Características Avanzadas

### Verificación de Integridad

El sistema verifica automáticamente:
- ✅ Integridad de la base de datos original antes de copiar
- ✅ Integridad de la copia después de realizar el backup
- ✅ Si una base de datos está corrupta, se registra en el log y se omite

### Retención de 7 Días

- Los backups se organizan por fecha (YYYY-MM-DD)
- Cada día se crea una carpeta nueva
- Los backups con más de 7 días se eliminan automáticamente
- Esto mantiene el espacio en disco bajo control

### Logs Detallados

El archivo `logs/backup.log` incluye:
- Fecha y hora de cada operación
- Bases de datos respaldadas exitosamente
- Errores encontrados
- Backups purgados
- Espacio utilizado

## ⚠️ Notas Importantes

1. **Permisos de Administrador**: La configuración inicial requiere permisos de administrador para crear la tarea programada.

2. **Espacio en Disco**: Asegúrate de tener suficiente espacio. Con 10 bases de datos de ~10MB cada una, necesitarás aproximadamente 700MB para 7 días de backups.

3. **Bases de Datos en Uso**: El sistema puede hacer backup incluso si las bases de datos están en uso (SQLite permite lecturas concurrentes).

4. **Restauración**: Para restaurar un backup, simplemente copia el archivo `.db` desde la carpeta `backup/YYYY-MM-DD/` a la carpeta `data/` (asegúrate de detener el servidor primero).

## 🆘 Solución de Problemas

### El backup no se ejecuta automáticamente

1. Verifica que la tarea programada existe:
   ```cmd
   schtasks /Query /TN "DVDCoin_Backup_Diario"
   ```

2. Revisa el log de backups: `logs/backup.log`

3. Ejecuta manualmente para ver errores: `EJECUTAR_BACKUP_MANUAL.bat`

### Error de permisos

- Asegúrate de que el usuario que ejecuta la tarea tiene permisos de lectura en `data/` y escritura en `backup/`

### Base de datos corrupta

- El sistema detectará bases de datos corruptas y las omitirá
- Revisa el log para identificar cuál base de datos tiene problemas
- Considera restaurar desde un backup anterior

## 📞 Soporte

Para más información, revisa:
- `logs/backup.log` - Log de operaciones
- `scripts/backup_databases.py` - Script principal de backup
- `scripts/configurar_backup_automatico.py` - Configuración de tarea programada
