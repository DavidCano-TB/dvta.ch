# Migración de DVDcoin Bank: / → /bank

## ✅ Cambios Completados

### 1. Backend Python (main.py y src/main.py)
- ✅ Todas las rutas FastAPI actualizadas con prefijo `/bank`
- ✅ Montaje de archivos estáticos: `/static` → `/bank/static`
- ✅ Total de rutas actualizadas: ~165

### 2. Frontend JavaScript
- ✅ `static/js/unified-nav.js` - Sistema de navegación actualizado
- ✅ `static/js/i18n.js` - Rutas de traducción actualizadas
- ✅ `src/static/js/unified-nav.js` - Copia actualizada

### 3. Frontend HTML
- ✅ Todos los archivos HTML actualizados (266 archivos)
- ✅ Referencias a `/static/` → `/bank/static/`
- ✅ Referencias a `/api/` → `/bank/api/`
- ✅ Service Worker registration actualizado

### 4. Service Worker
- ✅ Creado `static/sw.js` con soporte para rutas `/bank`
- ✅ Cache de assets estáticos configurado
- ✅ Network-first para HTML, cache-first para assets

### 5. Archivos de Juegos
- ✅ game_pages/apuestas/
- ✅ game_pages/cifrasletras/
- ✅ game_pages/hundirlaflota/
- ✅ game_pages/messages/
- ✅ game_pages/millonario/
- ✅ game_pages/pasapalabra/
- ✅ game_pages/quiensoy/
- ✅ game_pages/votaciones/

## 📊 Estadísticas de Migración

- **Archivos analizados:** 7,442
- **Archivos modificados:** 266
- **Total de cambios:** 1,709

## ⚠️ Pasos Pendientes

### 1. Configuración de Cloudflare Tunnel

Tienes dos opciones:

#### Opción A: Path Routing en Cloudflare (Recomendado)
Configurar Cloudflare para que:
- `dvta.ch/` → Nueva aplicación (futuro)
- `dvta.ch/bank` → Aplicación actual (127.0.0.1:8000)

**Ventajas:**
- Permite tener múltiples aplicaciones en el mismo dominio
- No requiere cambios en el backend
- Más flexible para el futuro

**Configuración en Cloudflare Dashboard:**
1. Ir a Zero Trust > Access > Tunnels
2. Editar el tunnel `dvta.ch`
3. Añadir regla de path:
   - Path: `/bank`
   - Service: `http://127.0.0.1:8000`

#### Opción B: Mantener configuración actual
Si mantienes la configuración actual de Cloudflare (todo el tráfico a 127.0.0.1:8000), el backend ya está preparado para manejar las rutas `/bank`.

### 2. Verificación y Pruebas

Antes de desplegar, verifica:

```bash
# 1. Iniciar el servidor
python main.py

# 2. Probar endpoints clave:
# - http://localhost:8000/bank (página principal)
# - http://localhost:8000/bank/api/health (health check)
# - http://localhost:8000/bank/static/js/unified-nav.js (assets estáticos)

# 3. Verificar en el navegador:
# - Login/Register funciona
# - Navegación entre secciones funciona
# - Assets estáticos se cargan correctamente
# - Service Worker se registra sin errores
```

### 3. Actualizar URLs en Documentación

Si tienes documentación o enlaces externos, actualízalos:
- `dvta.ch` → `dvta.ch/bank`
- `dvta.ch/api/...` → `dvta.ch/bank/api/...`

## 🔍 Verificación de Cambios

Para revisar todos los cambios realizados:

```bash
# Ver resumen de archivos modificados
git status

# Ver cambios en un archivo específico
git diff main.py
git diff static/js/unified-nav.js
git diff static/index.html

# Ver todos los cambios
git diff
```

## 🚀 Despliegue

Una vez verificado que todo funciona:

```bash
# 1. Hacer commit de los cambios
git add .
git commit -m "Migrar aplicación de / a /bank para nueva estructura"

# 2. Push a GitHub
git push origin main

# 3. Reiniciar el servidor
# (El GitHub Actions workflow se ejecutará automáticamente)
```

## 📝 Notas Importantes

1. **Tokens JWT:** Los tokens existentes seguirán funcionando, no es necesario que los usuarios vuelvan a hacer login.

2. **Bases de datos:** No se requieren cambios en las bases de datos, solo las rutas HTTP cambiaron.

3. **Cloudflare Tunnel:** El tunnel seguirá funcionando, solo necesitas decidir si quieres path routing o no.

4. **Service Worker:** Los usuarios pueden necesitar hacer Ctrl+F5 (hard refresh) la primera vez para cargar el nuevo Service Worker.

5. **Compatibilidad hacia atrás:** Si necesitas mantener las rutas antiguas temporalmente, puedes añadir redirects en FastAPI:

```python
@app.get("/")
async def redirect_root():
    return RedirectResponse(url="/bank")

@app.get("/api/{path:path}")
async def redirect_api(path: str):
    return RedirectResponse(url=f"/bank/api/{path}")
```

## 🎯 Próximos Pasos

1. ✅ Migración completada
2. ⏳ Probar localmente
3. ⏳ Configurar Cloudflare (si es necesario)
4. ⏳ Desplegar a producción
5. ⏳ Crear nueva aplicación en `dvta.ch/`

## 🆘 Solución de Problemas

### Problema: Assets no se cargan (404)
**Solución:** Verificar que `app.mount("/bank/static", ...)` esté correctamente configurado en main.py

### Problema: API calls fallan
**Solución:** Verificar que todas las llamadas fetch usen `/bank/api/...` en lugar de `/api/...`

### Problema: Service Worker no se actualiza
**Solución:** 
1. Abrir DevTools (F12)
2. Application > Service Workers
3. Click en "Unregister"
4. Recargar la página (Ctrl+F5)

### Problema: Navegación no funciona
**Solución:** Verificar que `unified-nav.js` tenga todas las rutas con prefijo `/bank`

---

**Fecha de migración:** 27 de mayo de 2026
**Script utilizado:** `migrate_to_bank.py`
**Versión:** DVDcoin Bank v4.0
