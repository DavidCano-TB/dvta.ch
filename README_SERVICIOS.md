# 🔧 Servicios Windows - DVDcoin Platform

## 🚀 Inicio Rápido

### Instalación (Una sola vez)

1. **Ejecutar como Administrador**:
   ```
   INSTALAR_SERVICIOS.bat
   ```

2. **¡Listo!** Los servicios se iniciarán automáticamente con Windows

### Gestión Diaria

```
GESTIONAR_SERVICIOS.bat
```

---

## 📋 Servicios Disponibles

| Servicio | Puerto | Auto-inicio | Descripción |
|----------|--------|-------------|-------------|
| **DVDcoin-Bank** | 8000 | ✅ | Sistema bancario principal |
| **DVDcoin-Exams** | 8001 | ✅ | Exámenes y oposiciones |
| **DVDcoin-Tunnel** | - | ✅ | Cloudflare Tunnel (dvta.ch) |

---

## 🎯 Ventajas

✅ **Inicio automático** con Windows  
✅ **Reinicio automático** si falla  
✅ **Sin ventanas** molestas  
✅ **Gestión centralizada**  
✅ **Logs del sistema**  

---

## 📦 Scripts Disponibles

| Script | Descripción |
|--------|-------------|
| `INSTALAR_SERVICIOS.bat` | Instalar todos los servicios |
| `DESINSTALAR_SERVICIOS.bat` | Eliminar todos los servicios |
| `GESTIONAR_SERVICIOS.bat` | Menú interactivo de gestión |

---

## ➕ Añadir Nuevo Servicio

Cuando crees una nueva funcionalidad:

```powershell
# Abrir PowerShell como Administrador
cd C:\dvdcoin\services

.\add_new_service.ps1 `
    -ServiceName "DVDcoin-NuevoModulo" `
    -DisplayName "DVDcoin Nuevo Módulo" `
    -Description "Descripción del módulo (Puerto 8002)" `
    -WorkingDir "C:\dvdcoin\modules\nuevo_modulo" `
    -Script "start_nuevo_modulo.py" `
    -Port 8002
```

**¡Automáticamente se creará y configurará el servicio!**

---

## 🔧 Comandos Rápidos

### PowerShell

```powershell
# Ver estado
Get-Service -Name "DVDcoin-*"

# Iniciar todos
Start-Service -Name "DVDcoin-*"

# Detener todos
Stop-Service -Name "DVDcoin-*" -Force

# Reiniciar todos
Restart-Service -Name "DVDcoin-*"

# Ver logs
Get-EventLog -LogName Application -Source "DVDcoin-*" -Newest 20
```

---

## 📖 Documentación Completa

Ver: [SERVICIOS_WINDOWS_GUIA.md](SERVICIOS_WINDOWS_GUIA.md)

---

## 🆘 Solución de Problemas

### Servicio no inicia

```powershell
# Ver logs
Get-EventLog -LogName Application -Source "DVDcoin-Bank" -Newest 10

# Verificar puerto
netstat -ano | findstr ":8000"

# Probar manualmente
cd C:\dvdcoin
python main.py
```

### Reinstalar todo

```
1. DESINSTALAR_SERVICIOS.bat
2. Reiniciar Windows
3. INSTALAR_SERVICIOS.bat
```

---

## 🏗️ Arquitectura

```
Windows Service
    ↓
Python Wrapper (pywin32)
    ↓
subprocess.Popen()
    ↓
FastAPI Application (uvicorn)
    ↓
HTTP Server (puerto 8000/8001/...)
```

**Cada servicio es independiente y se auto-reinicia si falla**

---

## ✅ Checklist Nueva Funcionalidad

- [ ] Crear módulo en `modules/[nombre]/`
- [ ] Crear `start_[nombre].py`
- [ ] Probar manualmente
- [ ] Ejecutar `add_new_service.ps1`
- [ ] Verificar servicio corriendo
- [ ] Actualizar Cloudflare Tunnel si necesario
- [ ] Documentar
- [ ] Commit y push

---

**¡Sistema robusto y profesional con servicios Windows!** 🚀
