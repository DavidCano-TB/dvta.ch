# 🚀 Inicio Rápido - DVDcoin Sistema Multi-Servidor

## ⚡ Inicio Rápido (3 pasos)

### 1️⃣ Ejecuta el Script Principal
```cmd
SISTEMA_COMPLETO.bat
```

### 2️⃣ Selecciona Opción 1 (Iniciar TODOS los servidores)

### 3️⃣ ¡Listo! El navegador se abrirá automáticamente

---

## 📋 Menú del Sistema

Cuando ejecutes `SISTEMA_COMPLETO.bat` verás:

```
═══════════════════════════════════════════════════════════════
  🏦 DVDcoin - Sistema de Gestión Completo
═══════════════════════════════════════════════════════════════

  [1] 🚀 Iniciar TODOS los servidores
  [2] 🔍 Verificar estado de servidores
  [3] 🛑 Detener TODOS los servidores
  [4] 🔄 Reiniciar sistema completo
  [5] 🌐 Abrir URLs en navegador
  [6] 📊 Ver logs en tiempo real
  [7] ❌ Salir
```

---

## 🌐 URLs de Acceso

Una vez iniciado el sistema, accede a:

- **Bank (Principal):** https://dvta.ch/bank
- **Exams (Oposiciones):** https://exams.dvta.ch
- **Games (Juegos):** https://games.dvta.ch
- **Social (Chat):** https://social.dvta.ch

---

## 🔧 Scripts Individuales

Si prefieres control manual:

### Iniciar Todo
```cmd
INICIAR_TODOS_SERVIDORES.bat
```

### Verificar Estado
```cmd
VERIFICAR_SERVIDORES.bat
```

### Detener Todo
```cmd
DETENER_TODOS_SERVIDORES.bat
```

---

## 📊 Verificar que Todo Funciona

Después de iniciar, verifica:

```cmd
VERIFICAR_SERVIDORES.bat
```

Deberías ver:
```
✅ Bank está corriendo
✅ Exams está corriendo
✅ Games está corriendo
✅ Social está corriendo
```

---

## 🛠️ Solución Rápida de Problemas

### Problema: "Puerto en uso"
```cmd
DETENER_TODOS_SERVIDORES.bat
```
Luego vuelve a iniciar.

### Problema: "Python no encontrado"
Instala Python desde: https://www.python.org/downloads/

### Problema: "Módulo no encontrado"
```cmd
pip install fastapi uvicorn pydantic bcrypt python-jose
```

---

## 📁 Estructura del Sistema

```
c:\dvdcoin\
│
├── 🎯 SCRIPTS DE GESTIÓN
│   ├── SISTEMA_COMPLETO.bat              ← MENÚ PRINCIPAL
│   ├── INICIAR_TODOS_SERVIDORES.bat     ← Inicia todo
│   ├── DETENER_TODOS_SERVIDORES.bat     ← Detiene todo
│   └── VERIFICAR_SERVIDORES.bat         ← Verifica estado
│
├── 🖥️ SERVIDORES
│   ├── src/main.py                       ← Bank (8000)
│   ├── modules/exams/start_exams.py      ← Exams (8001)
│   ├── modules/games/start_games.py      ← Games (8002)
│   └── modules/social/start_social.py    ← Social (8003)
│
└── 📚 DOCUMENTACIÓN
    ├── INICIO_RAPIDO.md                  ← Este archivo
    ├── SERVIDORES_MULTIPLES_README.md    ← Documentación completa
    └── INSTRUCCIONES_TEST_LOGIN.md       ← Test de login
```

---

## 🎯 Flujo de Trabajo Típico

### Desarrollo Diario
1. Ejecuta `SISTEMA_COMPLETO.bat`
2. Selecciona opción 1 (Iniciar)
3. Trabaja en tu código
4. Los cambios se reflejan automáticamente
5. Al terminar, selecciona opción 3 (Detener)

### Verificación Rápida
1. Ejecuta `SISTEMA_COMPLETO.bat`
2. Selecciona opción 2 (Verificar)
3. Revisa que todos los servidores estén ✅

### Reinicio Completo
1. Ejecuta `SISTEMA_COMPLETO.bat`
2. Selecciona opción 4 (Reiniciar)
3. El sistema se reinicia automáticamente

---

## 💡 Consejos

✅ **Usa el menú principal** (`SISTEMA_COMPLETO.bat`) para todo  
✅ **Verifica el estado** antes de reportar problemas  
✅ **Cada servidor** tiene su propia ventana con logs  
✅ **Cloudflare Tunnel** debe estar corriendo para acceso externo  
✅ **Los puertos** 8000-8003 deben estar libres  

---

## 🆘 Ayuda Rápida

### ¿Los servidores no inician?
```cmd
# 1. Detén todo
DETENER_TODOS_SERVIDORES.bat

# 2. Verifica puertos
netstat -ano | findstr ":8000 :8001 :8002 :8003"

# 3. Inicia de nuevo
INICIAR_TODOS_SERVIDORES.bat
```

### ¿No puedes acceder desde https://dvta.ch?
1. Verifica que Cloudflare Tunnel esté corriendo
2. Busca procesos `cloudflared.exe`
3. Si no está, inícialo desde Cloudflare Dashboard

### ¿Errores de importación?
```cmd
pip install -r requirements.txt
```

---

## 📞 Soporte

- **Documentación completa:** `SERVIDORES_MULTIPLES_README.md`
- **Test de login:** `INSTRUCCIONES_TEST_LOGIN.md`
- **Logs:** Revisa las ventanas de cada servidor

---

**¡Listo para empezar!** 🎉

Ejecuta `SISTEMA_COMPLETO.bat` y selecciona opción 1.
