# 🔧 Solución Rápida: OPO - Acceso Denegado

## ❌ Problema

Aparece esta pantalla al intentar acceder a OPO:

```
🔒 Acceso requerido
Conéctate al DVDcoin Bank para acceder.
← Ir al banco
```

## ✅ Solución en 3 Pasos

### 1️⃣ Ejecutar el Gestor de Acceso

```bash
GESTIONAR_ACCESO_OPO.bat
```

O directamente:

```bash
AGREGAR_USUARIO_OPO.bat <nombre_usuario>
```

### 2️⃣ Agregar el Usuario

Ejemplo para agregar al usuario "nina":

```bash
AGREGAR_USUARIO_OPO.bat nina
```

### 3️⃣ Reiniciar el Servidor

**IMPORTANTE:** Los cambios NO se aplican hasta reiniciar el servidor.

```bash
# Detener el servidor (Ctrl+C en la ventana del servidor)
# Luego reiniciar:
ARRANCAR.bat
```

O si usas el script de reinicio:

```bash
KILL_ALL_AND_RESTART.bat
```

## 🎯 ¿Por Qué Pasa Esto?

- ✅ El usuario **SÍ está autenticado** (tiene sesión válida)
- ❌ El usuario **NO tiene permisos** para acceder a OPO
- 🔐 OPO requiere que el usuario esté en la lista de `opo_players`

## 📋 Comandos Útiles

### Ver quién tiene acceso OPO:

```bash
python -c "import sqlite3; conn = sqlite3.connect('data/rights.db'); rows = conn.execute('SELECT username FROM opo_players').fetchall(); [print(f'  - {r[0]}') for r in rows]; conn.close()"
```

### Ver todos los usuarios del sistema:

```bash
python -c "import sqlite3; conn = sqlite3.connect('data/users.db'); rows = conn.execute('SELECT username FROM users ORDER BY username').fetchall(); [print(f'  - {r[0]}') for r in rows]; conn.close()"
```

### Agregar usuario manualmente:

```bash
python add_opo_user.py <nombre_usuario>
```

## 🚨 Errores Comunes

### Error: "User not found"
- El usuario no existe en el sistema
- Primero debe registrarse en el DVDcoin Bank

### Error: "User already has OPO access"
- El usuario ya está en la lista
- El problema puede ser que no se reinició el servidor

### Sigue sin funcionar después de agregar
- ⚠️ **¿Reiniciaste el servidor?** Este es el error más común
- Los cambios en `opo_players` solo se cargan al inicio del servidor

## 📚 Documentación Completa

Para más detalles, ver: `docs/FIX_OPO_ACCESO_DENEGADO.md`

## 🆘 Soporte

Si el problema persiste:

1. Verifica que el usuario existe: `GESTIONAR_ACCESO_OPO.bat` → Opción 2
2. Verifica que el usuario está en OPO: `GESTIONAR_ACCESO_OPO.bat` → Opción 1
3. Verifica que reiniciaste el servidor
4. Revisa los logs del servidor para ver errores específicos
