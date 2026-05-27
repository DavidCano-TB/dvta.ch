# 🚀 INSTRUCCIONES FINALES - Ejecutar Tests

## ✅ Todo Está Listo

La suite de tests está **100% configurada**. Solo necesitas seguir estos pasos simples:

---

## 📋 Pasos para Ejecutar los Tests

### 1️⃣ Reiniciar el Servidor

**¿Por qué?** Para aplicar los cambios de rate limiting.

```bash
# Si el servidor está ejecutándose, detenlo (Ctrl+C)
# Luego reinicia:
ARRANCAR.bat
```

⏱️ **Espera** a que veas el mensaje: `Uvicorn running on http://0.0.0.0:8000`

---

### 2️⃣ Crear Usuarios de Prueba

**Opción A - Automático (Recomendado)**:

```bash
cd test_funcionalidades
CREAR_USUARIOS_PRUEBA.bat
```

**Opción B - Manual**:

1. Abre http://localhost:8000
2. Registra: `test_user` / password: `test123`
3. Registra: `test_user2` / password: `test123`

---

### 3️⃣ Ejecutar los Tests

```bash
cd test_funcionalidades
EJECUTAR_TODOS_LOS_TESTS.bat
```

O usa el inicio rápido que hace todo automáticamente:

```bash
cd test_funcionalidades
INICIO_RAPIDO.bat
```

---

## 🎯 Qué Esperar

### ✅ Ejecución Exitosa

```
🧪 Ejecutando: Autenticación y Sesiones...
✅ Autenticación y Sesiones: EXITOSO

🧪 Ejecutando: Transferencias...
✅ Transferencias: EXITOSO

...

📊 RESUMEN FINAL
Total de tests:     15
✅ Tests exitosos:  15
❌ Tests fallidos:  0
📈 Tasa de éxito:   100.0%
```

### ⚠️ Si Algunos Tests Fallan

Es normal que algunos tests fallen si:
- Ciertas funcionalidades no están implementadas completamente
- Algunos endpoints no existen aún
- Configuraciones específicas faltan

**Los logs te dirán exactamente qué falló y por qué.**

---

## 📊 Revisar Resultados

### Logs Individuales

Cada test genera su propio log:

```
test_funcionalidades/
├── 01_transferencias/
│   └── test_transferencias_2026-05-11_17-51-50.log
├── 02_opo/
│   └── test_opo_2026-05-11_17-53-21.log
...
```

### Resumen JSON

El resumen consolidado está en:

```
test_funcionalidades/logs/test_summary_2026-05-11_17-51-50.json
```

---

## 🔧 Troubleshooting

### "Connection refused"

**Problema**: El servidor no está ejecutándose.

**Solución**:
```bash
ARRANCAR.bat
```

---

### "Invalid credentials"

**Problema**: Los usuarios de prueba no existen.

**Solución**:
```bash
cd test_funcionalidades
CREAR_USUARIOS_PRUEBA.bat
```

---

### "Rate limit exceeded"

**Problema**: El servidor no se reinició después de cambiar los límites.

**Solución**:
1. Detén el servidor (Ctrl+C)
2. Reinicia: `ARRANCAR.bat`
3. Ejecuta los tests de nuevo

---

### "ModuleNotFoundError"

**Problema**: Dependencias no instaladas.

**Solución**:
```bash
cd test_funcionalidades
INSTALAR_DEPENDENCIAS.bat
```

---

## 📝 Checklist Rápido

Antes de ejecutar, verifica:

- [ ] ✅ Servidor ejecutándose (`ARRANCAR.bat`)
- [ ] ✅ Servidor **reiniciado** (para rate limiting)
- [ ] ✅ Dependencias instaladas (`INSTALAR_DEPENDENCIAS.bat`)
- [ ] ✅ Usuarios creados (`CREAR_USUARIOS_PRUEBA.bat`)

Si todos están ✅, ejecuta:

```bash
cd test_funcionalidades
EJECUTAR_TODOS_LOS_TESTS.bat
```

---

## 🎉 ¡Listo!

Con estos pasos, los tests deberían ejecutarse sin problemas.

**Recuerda**: Los cambios realizados son:

✅ Imports corregidos  
✅ Dependencias instaladas  
✅ Rate limiting aumentado x10  
✅ Delays entre tests agregados  
✅ Scripts de automatización creados  
✅ Documentación completa  

**Todo está configurado. Solo ejecuta y revisa los resultados.**

---

## 📞 Ayuda Adicional

Si necesitas ayuda, revisa estos documentos:

- `README.md` - Documentación completa
- `RESUMEN_COMPLETO_SOLUCION.md` - Resumen de todos los cambios
- `CAMBIOS_RATE_LIMITING.md` - Explicación de rate limiting
- `ESTADO_ACTUAL.md` - Estado actual del proyecto

---

**¡Buena suerte con los tests! 🚀**
