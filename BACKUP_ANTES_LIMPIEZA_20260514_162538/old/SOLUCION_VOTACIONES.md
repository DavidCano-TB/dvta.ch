# Solución al Error de Votaciones

## Problema
Al intentar cargar las votaciones, se producía el error:
```
Error al cargar las votaciones: no such column: fecha_creacion
```

## Causa
La tabla `votaciones` en la base de datos tenía las columnas `created_at` y `finalized_at`, pero el código del backend estaba buscando las columnas `fecha_creacion` y `fecha_cierre`.

## Solución Aplicada

### 1. Identificación del problema
- La base de datos correcta es `data/apuestas.db` (no `apuestas.db` en la raíz)
- La tabla `votaciones` existía pero con nombres de columnas diferentes
- Faltaban las columnas `fecha_creacion` y `fecha_cierre`

### 2. Corrección de la base de datos
Se ejecutó el script `corregir_votaciones_final.py` que:
- Agregó la columna `fecha_creacion` a la tabla `votaciones`
- Copió los valores de `created_at` a `fecha_creacion`
- Agregó la columna `fecha_cierre` (si no existía)
- Copió los valores de `finalized_at` a `fecha_cierre`

### 3. Verificación de tablas relacionadas
Se verificó que las tablas `votaciones_opciones` y `votos` existieran con las columnas correctas:
- `votos` debe tener la columna `username` (no `usuario`)
- Todas las tablas fueron creadas correctamente por el script `crear_tablas_votaciones.py`

## Estado Final

### Estructura de la tabla `votaciones`
```sql
CREATE TABLE votaciones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    creador TEXT NOT NULL,
    titulo TEXT NOT NULL,
    descripcion TEXT DEFAULT '',
    estado TEXT DEFAULT 'abierta',
    multiple INTEGER DEFAULT 0,
    anonima INTEGER DEFAULT 0,
    opciones_json TEXT,
    resultado_json TEXT,
    created_at TEXT,
    finalized_at TEXT,
    fecha_cierre TIMESTAMP,
    fecha_creacion TIMESTAMP
)
```

### Estructura de la tabla `votaciones_opciones`
```sql
CREATE TABLE votaciones_opciones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    votacion_id INTEGER NOT NULL,
    opcion TEXT NOT NULL,
    FOREIGN KEY (votacion_id) REFERENCES votaciones(id) ON DELETE CASCADE
)
```

### Estructura de la tabla `votos`
```sql
CREATE TABLE votos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    votacion_id INTEGER NOT NULL,
    username TEXT NOT NULL,
    opcion TEXT NOT NULL,
    fecha TEXT,
    FOREIGN KEY (votacion_id) REFERENCES votaciones(id) ON DELETE CASCADE
)
```

## Verificación
El script `test_votaciones_completo.py` confirma que:
- ✅ Todas las columnas requeridas existen
- ✅ Las tres tablas están correctamente creadas
- ✅ La consulta SQL del backend funciona correctamente
- ✅ Existe una votación de prueba con 2 opciones

## Uso del Sistema

### Para crear una votación:
1. Accede a http://localhost:8000/votaciones
2. Haz clic en "➕ Crear Nueva Votación"
3. Completa el formulario:
   - Título (requerido)
   - Descripción (opcional)
   - Al menos 2 opciones
   - Opciones de configuración (múltiples votos, anónima)
4. Haz clic en "Crear Votación"

### Para votar:
1. Haz clic en una votación de la lista
2. Selecciona una opción y haz clic en "Votar por esta opción"
3. Puedes eliminar tu voto si cambias de opinión

### Para administrar (solo admins):
- **Finalizar votación**: Cierra la votación y calcula resultados
- **Eliminar votación**: Elimina la votación y todos sus votos

## Archivos Creados/Modificados

### Scripts de corrección:
- `corregir_votaciones_final.py` - Agrega las columnas faltantes
- `test_votaciones_completo.py` - Verifica el estado del sistema
- `crear_tablas_votaciones.py` - Crea todas las tablas necesarias

### Archivos del sistema:
- `game_pages/votaciones/votaciones.html` - Interfaz de usuario completa
- `main.py` - Backend con todos los endpoints necesarios
- `data/apuestas.db` - Base de datos con las tablas corregidas

## Conclusión
El sistema de votaciones está completamente funcional y listo para usar. Todas las votaciones se mostrarán correctamente en el panel con sus fechas de creación y cierre.
