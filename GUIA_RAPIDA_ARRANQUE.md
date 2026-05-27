# 🚀 GUÍA RÁPIDA DE ARRANQUE - DVDcoin Platform

## ✅ Verificación Previa

Antes de arrancar, verifica que todo esté OK:

```bash
VERIFICAR_SISTEMA_COMPLETO.bat
```

---

## 🎯 Arranque Rápido (Recomendado)

### Opción 1: Arrancar TODO (Bank + Exams)

```bash
ARRANCAR_TODO.bat
```

Esto inicia:
- ✅ Bank en puerto 8000
- ✅ Exams en puerto 8001

### Opción 2: Arrancar solo Bank

```bash
ARRANCAR.bat
```

### Opción 3: Arrancar solo Exams

```bash
INICIAR_EXAMS.bat
```

---

## 🌐 Acceso Externo (Cloudflare Tunnel)

### Para dvta.ch (Exams)

```bash
INICIAR_TUNNEL_DVTA.bat
```

Esto expone:
- ✅ https://dvta.ch → localhost:8001

### Para múltiples dominios (Futuro)

```bash
INICIAR_TUNNEL_MULTI.bat
```

Esto expone:
- ✅ https://dvdbank.com → localhost:8000
- ✅ https://dvta.ch → localhost:8001
- ✅ https://games.dvdbank.com → localhost:8002

---

## 📍 URLs de Acceso

### Local
- **Bank**: http://localhost:8000
- **Exams**: http://localhost:8001

### Externo (con tunnel)
- **Bank**: https://dvdbank.com
- **Exams**: https://dvta.ch

---

## 🔧 Solución de Problemas

### Error: Python no encontrado
```bash
# Instalar Python 3.11+
https://www.python.org/downloads/
```

### Error: Dependencias faltantes
```bash
pip install -r requirements.txt
cd modules\exams
pip install -r requirements.txt
```

### Error: Puerto ocupado
```bash
# Detener procesos anteriores
taskkill /F /IM python.exe
```

### Error: Cloudflare Tunnel no funciona
```bash
# Verificar cloudflared
cloudflared.exe --version

# Verificar configuración
type cloudflare-dvta-config.yml
```

---

## 🛑 Detener Servidores

### Opción 1: Cerrar ventanas
Cierra las ventanas de consola de los servidores

### Opción 2: Comando
```bash
taskkill /F /IM python.exe
taskkill /F /IM cloudflared.exe
```

---

## 🔄 Actualizar desde Git

```bash
# 1. Detener servidores
taskkill /F /IM python.exe

# 2. Hacer pull
git pull

# 3. Actualizar dependencias (si hay cambios)
pip install -r requirements.txt

# 4. Reiniciar
ARRANCAR_TODO.bat
```

---

## 📦 Deploy Automático (GitHub Actions)

Cada vez que haces `git push`:

1. ✅ GitHub Actions ejecuta tests
2. ✅ Verifica sintaxis de todos los módulos
3. ✅ Instala dependencias
4. ✅ Envía email de confirmación
5. ✅ Listo para pull en servidor

Para aplicar cambios en servidor:
```bash
git pull
ARRANCAR_TODO.bat
```

---

## 🎯 Flujo de Trabajo Diario

### Desarrollo Local
```bash
# 1. Arrancar servidores
ARRANCAR_TODO.bat

# 2. Desarrollar y probar
# Acceder a http://localhost:8000 y http://localhost:8001

# 3. Commit y push
git add .
git commit -m "Descripción de cambios"
git push

# 4. GitHub Actions valida automáticamente
```

### Aplicar en Producción
```bash
# En el servidor
git pull
taskkill /F /IM python.exe
ARRANCAR_TODO.bat
INICIAR_TUNNEL_DVTA.bat
```

---

## ⚙️ Configuración Avanzada

### Cambiar Puerto de Bank
Editar `main.py`:
```python
uvicorn.run(app, host="0.0.0.0", port=8000)  # Cambiar 8000
```

### Cambiar Puerto de Exams
Editar `modules/exams/app_exams.py`:
```python
uvicorn.run(app, host="0.0.0.0", port=8001)  # Cambiar 8001
```

### Añadir Nuevo Dominio a Cloudflare
Editar `config/tunnels/cloudflare-multi.yml`:
```yaml
ingress:
  - hostname: nuevo-dominio.com
    service: http://127.0.0.1:8003
```

---

## 📞 Ayuda

### Verificar Estado
```bash
VERIFICAR_SISTEMA_COMPLETO.bat
```

### Ver Logs
Los servidores muestran logs en sus ventanas de consola

### Documentación Completa
- `RESUMEN_ARQUITECTURA_MODULAR.md`
- `modules/exams/README.md`
- `PLAN_ARQUITECTURA_MODULAR.md`

---

## ✅ Checklist Pre-Deploy

Antes de hacer push a GitHub:

- [ ] Código funciona localmente
- [ ] Sin errores de sintaxis
- [ ] Dependencias actualizadas en requirements.txt
- [ ] Bases de datos funcionan
- [ ] Tests pasan (si existen)
- [ ] Documentación actualizada

---

**Última actualización**: 27 Mayo 2026
**Versión**: 2.0 (Arquitectura Modular)
