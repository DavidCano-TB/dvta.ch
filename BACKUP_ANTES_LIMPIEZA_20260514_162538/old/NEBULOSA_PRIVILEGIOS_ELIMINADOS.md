# Eliminación de Privilegios Especiales de Nebulosa

## Resumen
Se han eliminado todos los privilegios especiales de superadmin del usuario "nebulosa", convirtiéndola en un usuario normal del sistema.

## Cambios Realizados

### 1. Backend (src/main.py)

#### Constantes Globales
- **ADMINS**: Eliminada "nebulosa" de la lista
- **SUPERADMINS**: Eliminada "nebulosa", solo queda "dvd"
- **OPO_USERS**: Eliminada "nebulosa" del conjunto inicial

#### Funciones Modificadas
- `_load_opo_users()`: Ya no incluye "nebulosa" por defecto
- `_load_admins_from_db()`: Eliminada "nebulosa" de la lista base
- Validaciones de OPO: Cambiado de `{"dvd","nebulosa"}` a `{"dvd"}`

### 2. Frontend - Archivos HTML/JavaScript

#### static/pages/index.html
- Eliminada "nebulosa" de `ADMINS` array
- Actualizado texto: "Solo dvd puede gestionar administradores"
- Eliminadas verificaciones `p.username === 'nebulosa'`
- Actualizado comentario: "DVD STATS PANEL (dvd only)"

#### static/index.html
- Mismos cambios que static/pages/index.html

#### static/pasapalabra/index.html
- Eliminada "nebulosa" de verificaciones de superadmin
- Actualizado texto de gestión de admins
- Actualizado comentario de panel de estadísticas

#### static/opo/game.html
- Eliminada "nebulosa" de `OPO_USERS`
- Eliminado código especial de sonidos para nebulosa
- Actualizado comentario: "dvd always" en lugar de "dvd+nebulosa always"
- Eliminada de lista de superadmins en leaderboard
- Actualizado `isDvdNeb` para solo verificar "dvd"

#### static/opo/game - Copie.html
- Mismos cambios que static/opo/game.html

#### static/webrtc-video.html
- Eliminada "nebulosa" de `ADMINS` array
- Actualizado comentario: "host + dvd" en lugar de "host + dvd/nebulosa"

#### static/pages/webrtc-video.html
- Mismos cambios que static/webrtc-video.html

### 3. Tests

#### tests/test_video_call.py
- Cambiado USER_B de "nebulosa" a "nina"

### 4. Scripts de Base de Datos

#### remove_nebulosa_privileges.py
Script Python creado para:
- Eliminar "nebulosa" de la tabla `roles` en rights.db
- Verificar estado en todas las bases de datos
- Mantener a "nebulosa" como usuario normal en users.db
- Opción `--status` para ver el estado actual

#### remove_nebulosa_privileges.sql
Script SQL con comandos comentados para:
- Eliminar de roles de admin
- Eliminar de opo_players
- Opcionalmente eliminar completamente del sistema

## Privilegios Eliminados

### Antes
- ✓ Superadmin (acceso total al sistema)
- ✓ Gestión de administradores
- ✓ Acceso a estadísticas avanzadas (DVD Stats Panel)
- ✓ Control de salas de video (cerrar cualquier sala)
- ✓ Acceso automático a OPO
- ✓ Sonidos especiales en juegos
- ✓ Ver resultados de todos los usuarios
- ✓ Bypass de restricciones de juegos

### Después
- ✗ Usuario normal
- ✗ Sin privilegios administrativos
- ✗ Sin acceso a gestión de admins
- ✗ Sin acceso a estadísticas avanzadas
- ✗ Sin control especial de salas
- ✗ Acceso a OPO solo si se añade manualmente
- ✗ Sin privilegios especiales en juegos

## Cómo Aplicar los Cambios

### 1. Actualizar Base de Datos
```bash
# Ver estado actual
python remove_nebulosa_privileges.py --status

# Ejecutar cambios
python remove_nebulosa_privileges.py
```

### 2. Reiniciar el Servidor
```bash
# Detener el servidor actual
# Luego iniciar de nuevo
python -m uvicorn src.main:app --reload
```

### 3. Verificar Cambios
- Iniciar sesión como "nebulosa"
- Verificar que no aparecen opciones de admin
- Verificar que no puede acceder a estadísticas avanzadas
- Verificar que no puede gestionar administradores

## Notas Importantes

1. **Usuario Mantenido**: "nebulosa" sigue existiendo como usuario normal en la base de datos con su balance y datos intactos.

2. **Acceso a OPO**: Si "nebulosa" necesita acceso a OPO, debe ser añadida manualmente por un superadmin (dvd).

3. **Transacciones**: Todas las transacciones históricas de "nebulosa" se mantienen intactas.

4. **Sesiones**: El historial de sesiones de "nebulosa" se mantiene en la base de datos.

5. **Reversión**: Para revertir los cambios, añadir "nebulosa" de vuelta a las constantes ADMINS y SUPERADMINS en el código y ejecutar:
   ```sql
   INSERT INTO roles (username, role, granted_by) 
   VALUES ('nebulosa', 'admin', 'dvd');
   ```

## Archivos Modificados

### Backend
- `src/main.py`

### Frontend
- `static/pages/index.html`
- `static/index.html`
- `static/pasapalabra/index.html`
- `static/opo/game.html`
- `static/opo/game - Copie.html`
- `static/webrtc-video.html`
- `static/pages/webrtc-video.html`

### Tests
- `tests/test_video_call.py`

### Scripts Nuevos
- `remove_nebulosa_privileges.py`
- `remove_nebulosa_privileges.sql`
- `NEBULOSA_PRIVILEGIOS_ELIMINADOS.md` (este archivo)

## Fecha de Cambios
2026-05-05

## Autor
Cambios realizados mediante asistente de código Kiro
