# 🚀 INICIO RÁPIDO - Tests DVDcoin Bank

## ⚡ 3 Pasos para Empezar

### 1️⃣ Preparar Tests (IMPORTANTE - Primera vez)
```bash
PREPARAR_TESTS.bat
```
Este script copia `test_utils.py` y `config.json` a cada carpeta de test.

### 2️⃣ Instalar Dependencias
```bash
INSTALAR_DEPENDENCIAS.bat
```

### 3️⃣ Configurar
Edita `config.json` con tus credenciales:
```json
{
  "server": {
    "base_url": "http://localhost:8000"
  },
  "credentials": {
    "admin": {
      "username": "dvd",
      "password": "tu_password"
    }
  }
}
```

### 4️⃣ Ejecutar
```bash
EJECUTAR_TODOS_LOS_TESTS.bat
```

---

## 🔍 Verificar Configuración

Antes de ejecutar los tests, verifica que todo esté listo:

```bash
VERIFICAR_CONFIGURACION.bat
```

Esto comprobará:
- ✅ Versión de Python
- ✅ Dependencias instaladas
- ✅ Archivo de configuración
- ✅ Conexión con el servidor
- ✅ Archivos de test

---

## 📁 Estructura

```
test_funcionalidades/
├── 📄 INICIO_RAPIDO.md              ← Estás aquí
├── 📄 RESUMEN_COMPLETO.md           ← Documentación completa
├── 📄 INSTRUCCIONES.md              ← Guía detallada
│
├── 🔧 config.json                   ← Configuración
├── 🔧 test_utils.py                 ← Utilidades comunes
│
├── ▶️ INSTALAR_DEPENDENCIAS.bat     ← Instalar Python packages
├── ▶️ VERIFICAR_CONFIGURACION.bat   ← Verificar setup
├── ▶️ EJECUTAR_TODOS_LOS_TESTS.bat  ← Ejecutar todos
│
└── 📂 [15 carpetas de tests]
    ├── 15_autenticacion/
    ├── 01_transferencias/
    ├── 02_opo/
    ├── 03_millonario/
    ├── 04_video/
    ├── 05_cifras_letras/
    ├── 06_pasapalabra/
    ├── 07_hundir_flota/
    ├── 08_mensajes/
    ├── 09_apuestas/
    ├── 10_votaciones/
    ├── 11_cuentos/
    ├── 12_quien_soy/
    ├── 13_admin/
    └── 14_galeria/
```

---

## 🎯 Tests Disponibles

| # | Módulo | Descripción | Tests |
|---|--------|-------------|-------|
| 15 | **Autenticación** | Login, tokens, sesiones | 15 |
| 01 | **Transferencias** | DVDcoins, transacciones | 10 |
| 02 | **OPO** | Sistema de oposiciones | 10 |
| 03 | **Millonario** | Juego con preguntas | 11 |
| 04 | **Video** | WebRTC, videollamadas | 12 |
| 05 | **Cifras y Letras** | Juego de palabras/números | 10 |
| 06 | **Pasapalabra** | Rosco de letras | 9 |
| 07 | **Hundir la Flota** | Juego naval | 8 |
| 08 | **Mensajes** | Chat y mensajería | 10 |
| 09 | **Apuestas** | Porras y apuestas | 11 |
| 10 | **Votaciones** | Sistema de votaciones | 10 |
| 11 | **Cuentos** | Gestión de historias | 10 |
| 12 | **¿Quién Soy?** | Juego con IA | 11 |
| 13 | **Admin** | Panel de administración | 13 |
| 14 | **Galería** | Imágenes | 6 |

**Total:** 15 módulos, ~150+ tests

---

## 📊 Ejemplo de Salida

```
================================================================================
  🧪 EJECUTAR TODOS LOS TESTS FUNCIONALES
================================================================================

🧪 Ejecutando: Autenticación y Sesiones...
✅ Autenticación y Sesiones: EXITOSO

🧪 Ejecutando: Transferencias...
✅ Transferencias: EXITOSO

🧪 Ejecutando: OPO (Oposiciones)...
✅ OPO (Oposiciones): EXITOSO

...

================================================================================
📊 RESUMEN FINAL
================================================================================
Total de tests:     15
✅ Tests exitosos:  15
❌ Tests fallidos:  0
📈 Tasa de éxito:   100.0%
⏱️  Tiempo total:    45.3s
================================================================================
```

---

## 📝 Logs

Cada test genera un log en su carpeta:

```
01_transferencias/test_transferencias_2026-05-11_10-30-15.log
```

Contenido del log:
```
2026-05-11 10:30:15 | INFO     | ================================================================================
2026-05-11 10:30:15 | INFO     | 🧪 INICIANDO TEST: TRANSFERENCIAS
2026-05-11 10:30:15 | INFO     | ================================================================================
2026-05-11 10:30:16 | INFO     | ✅ Login exitoso como dvd
2026-05-11 10:30:17 | INFO     | ✅ Transferencia básica: Status 200 ✓
...
2026-05-11 10:30:45 | INFO     | ================================================================================
2026-05-11 10:30:45 | INFO     | 📊 RESUMEN DEL TEST
2026-05-11 10:30:45 | INFO     | ================================================================================
2026-05-11 10:30:45 | INFO     | ✅ Tests exitosos:  45
2026-05-11 10:30:45 | INFO     | ❌ Tests fallidos:  0
2026-05-11 10:30:45 | INFO     | 📈 Tasa de éxito:   100.0%
```

---

## 🔧 Solución Rápida de Problemas

### ❌ "No se pudo conectar al servidor"
**Solución:** Inicia el servidor con `ARRANCAR.bat`

### ❌ "Login fallido"
**Solución:** Verifica las credenciales en `config.json`

### ❌ "ModuleNotFoundError"
**Solución:** Ejecuta `INSTALAR_DEPENDENCIAS.bat`

### ❌ "WebSocket no conecta"
**Solución:** Verifica que `ws_url` en `config.json` sea correcto

---

## 📚 Más Información

- **Documentación completa:** `RESUMEN_COMPLETO.md`
- **Guía detallada:** `INSTRUCCIONES.md`
- **README general:** `README.md`

---

## 🎓 Comandos Útiles

```bash
# Verificar configuración
VERIFICAR_CONFIGURACION.bat

# Instalar dependencias
INSTALAR_DEPENDENCIAS.bat

# Ejecutar todos los tests
EJECUTAR_TODOS_LOS_TESTS.bat

# Ejecutar un test específico
cd 01_transferencias
EJECUTAR_TEST.bat

# Ver logs
notepad 01_transferencias\test_transferencias_*.log
```

---

## ✅ Checklist Pre-Ejecución

- [ ] Python 3.8+ instalado
- [ ] Dependencias instaladas (`pip install requests websocket-client pillow`)
- [ ] Servidor corriendo (`ARRANCAR.bat`)
- [ ] `config.json` configurado con credenciales correctas
- [ ] Usuarios de prueba creados (test_user, test_user2)

---

**¡Listo para empezar! 🚀**

Ejecuta `VERIFICAR_CONFIGURACION.bat` para asegurarte de que todo está correcto.
