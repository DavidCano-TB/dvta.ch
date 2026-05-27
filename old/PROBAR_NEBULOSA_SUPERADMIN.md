# 🧪 Guía de Pruebas - Nebulosa Superadmin

## ✅ Cambios Aplicados

Todos los cambios para convertir a nebulosa en superadmin han sido aplicados exitosamente.

---

## 🔄 Paso 1: Reiniciar el Servidor

**IMPORTANTE:** Debes reiniciar el servidor para que los cambios surtan efecto.

```bash
# Si el servidor está corriendo:
# 1. Presiona Ctrl+C para detenerlo
# 2. Espera a que se detenga completamente
# 3. Inicia el servidor nuevamente:
python main.py
```

---

## 🧪 Paso 2: Probar los Privilegios

### 2.1 Iniciar Sesión como Nebulosa

1. Abre el navegador
2. Ve a la aplicación DVDcoin
3. Si nebulosa ya está conectada, **cierra sesión primero**
4. Inicia sesión como **nebulosa**

### 2.2 Verificar Panel de Administración

**Qué buscar:**
- Deberías ver una pestaña o sección de "Admin" o "Administración"
- El panel debe mostrar opciones avanzadas

**Qué probar:**
1. Ir a la sección de administración
2. Verificar que puedes ver:
   - 👥 Lista completa de usuarios
   - 🔑 Gestión de administradores
   - 📊 Estadísticas avanzadas (DVD Stats Panel)
   - 🎮 Panel de gestión de OPO

### 2.3 Verificar Gestión de Usuarios

**Qué probar:**
1. En el panel de administración, busca "Gestión de Usuarios"
2. Deberías poder ver:
   - Lista de TODOS los usuarios (no solo miembros)
   - Estado online/offline de cada usuario
   - Botones para bloquear/desbloquear usuarios
   - Opción para modificar balances

**Prueba específica:**
1. Busca un usuario de prueba
2. Intenta ver su perfil completo
3. Verifica que puedes ver su balance y transacciones

### 2.4 Verificar Acceso a OPO

**Qué probar:**
1. Ve a la sección de juegos
2. Haz clic en "OPO" (simulacro de examen)
3. Deberías poder:
   - ✅ Entrar al juego sin restricciones
   - ✅ Ver un botón o sección de "Gestión" o "Admin"
   - ✅ Ver resultados de TODOS los usuarios (no solo los tuyos)

**Prueba específica:**
1. En OPO, busca la sección de "Leaderboard" o "Resultados"
2. Deberías ver resultados de todos los jugadores
3. Busca opciones para añadir/eliminar jugadores

### 2.5 Verificar Gestión de Administradores

**Qué probar:**
1. En el panel de administración, busca "Gestión de Administradores"
2. Deberías ver:
   - Lista de administradores actuales
   - Opción para añadir nuevos administradores
   - Opción para eliminar administradores (excepto dvd y nebulosa)

**Prueba específica:**
1. Intenta añadir un usuario como administrador temporal
2. Verifica que aparece en la lista
3. Elimínalo de nuevo

### 2.6 Verificar Estadísticas Avanzadas

**Qué probar:**
1. En el panel de administración o en la pestaña "Historial"
2. Busca "Estadísticas Avanzadas" o "DVD Stats Panel"
3. Deberías ver:
   - Gráficos de actividad del sistema
   - Estadísticas de todos los usuarios
   - Información detallada de transacciones

### 2.7 Verificar Gestión de Videollamadas

**Qué probar:**
1. Ve a la sección de videollamadas
2. Como superadmin, deberías poder:
   - Crear salas de video
   - Ver todas las salas activas
   - Gestionar participantes

---

## 🎯 Checklist de Verificación

Marca cada item cuando lo hayas verificado:

### Acceso Básico
- [ ] Puedo iniciar sesión como nebulosa
- [ ] Veo el panel de administración
- [ ] El sistema me reconoce como superadmin

### Gestión de Usuarios
- [ ] Puedo ver lista completa de usuarios
- [ ] Puedo ver quién está online
- [ ] Puedo bloquear/desbloquear usuarios
- [ ] Puedo modificar balances

### Gestión de Administradores
- [ ] Puedo ver lista de administradores
- [ ] Puedo añadir administradores
- [ ] Puedo eliminar administradores (excepto dvd/nebulosa)

### Acceso a OPO
- [ ] Puedo entrar al juego OPO
- [ ] Puedo ver resultados de todos los usuarios
- [ ] Puedo gestionar jugadores de OPO
- [ ] No puedo ser eliminada de OPO

### Estadísticas
- [ ] Puedo ver estadísticas avanzadas
- [ ] Puedo ver gráficos del sistema
- [ ] Puedo ver transacciones de todos los usuarios

### Gestión de Porras
- [ ] Puedo crear porras
- [ ] Puedo resolver porras
- [ ] Puedo ver estadísticas globales

### Videollamadas
- [ ] Puedo crear salas de video
- [ ] Puedo gestionar participantes

---

## ❌ Problemas Comunes y Soluciones

### Problema 1: No veo el panel de administración

**Solución:**
1. Cierra sesión completamente
2. Cierra el navegador
3. Abre el navegador de nuevo
4. Inicia sesión como nebulosa
5. Si persiste, verifica que el servidor se reinició correctamente

### Problema 2: No puedo acceder a OPO

**Solución:**
1. Ejecuta el script de verificación:
   ```bash
   python verificar_nebulosa_superadmin.py
   ```
2. Verifica que nebulosa está en `opo_players`
3. Si no está, ejecuta:
   ```bash
   python restore_nebulosa_superadmin.py
   ```
4. Reinicia el servidor

### Problema 3: No veo estadísticas avanzadas

**Solución:**
1. Verifica que el servidor reconoce a nebulosa como superadmin
2. Busca en los logs del servidor mensajes como:
   ```
   User nebulosa logged in (superadmin)
   ```
3. Si no aparece, ejecuta:
   ```bash
   python verificar_nebulosa_superadmin.py
   ```

### Problema 4: Cambios no se aplican

**Solución:**
1. Asegúrate de haber reiniciado el servidor
2. Limpia la caché del navegador (Ctrl+Shift+Delete)
3. Cierra sesión y vuelve a iniciar sesión
4. Si persiste, ejecuta:
   ```bash
   python restore_nebulosa_superadmin.py
   python verificar_nebulosa_superadmin.py
   ```

---

## 🔍 Verificación Técnica

Si quieres verificar técnicamente que todo está correcto:

### Verificar en el Código
```bash
# Buscar SUPERADMINS en main.py
grep "SUPERADMINS" main.py
# Debería mostrar: SUPERADMINS = {"dvd", "nebulosa"}
```

### Verificar en la Base de Datos
```bash
# Ejecutar script de verificación
python verificar_nebulosa_superadmin.py
# Todos los checks deberían estar en ✅
```

### Verificar en el Frontend
```bash
# Buscar nebulosa en archivos HTML
grep -r "nebulosa" static/*.html
# Debería encontrar múltiples referencias
```

---

## 📊 Resultados Esperados

Después de completar todas las pruebas, deberías poder confirmar:

✅ **Nebulosa es SUPERADMIN**
- Tiene acceso total al sistema
- Puede gestionar usuarios y administradores
- Puede ver estadísticas avanzadas

✅ **Nebulosa tiene acceso permanente a OPO**
- Puede jugar sin restricciones
- Puede ver resultados de todos
- Puede gestionar jugadores
- No puede ser eliminada

✅ **Nebulosa puede gestionar conexiones**
- Ve usuarios online
- Gestiona salas de video
- Controla permisos de acceso

---

## 📝 Reportar Resultados

Después de probar, documenta:

1. **¿Todos los checks pasaron?** Sí / No
2. **¿Encontraste algún problema?** Describe
3. **¿Qué funcionalidades probaste?** Lista
4. **¿Alguna sugerencia de mejora?** Comenta

---

## ✅ Confirmación Final

Una vez que hayas verificado todo:

```
✅ Nebulosa puede iniciar sesión
✅ Nebulosa ve panel de administración
✅ Nebulosa puede gestionar usuarios
✅ Nebulosa tiene acceso a OPO
✅ Nebulosa puede ver estadísticas avanzadas
✅ Nebulosa puede gestionar administradores
✅ Nebulosa puede gestionar conexiones

🎉 ¡TODO FUNCIONA CORRECTAMENTE!
```

---

## 🆘 Soporte

Si encuentras problemas que no puedes resolver:

1. Revisa los logs del servidor
2. Ejecuta `python verificar_nebulosa_superadmin.py`
3. Revisa la documentación completa en `NEBULOSA_SUPERADMIN_RESTAURADO.md`
4. Consulta las instrucciones en `INSTRUCCIONES_NEBULOSA.md`

---

**¡Buena suerte con las pruebas!** 🚀
