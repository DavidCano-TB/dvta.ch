# 🔧 Instrucciones para Probar el Login

## Problema Actual
El botón de login no responde al hacer clic en https://dvta.ch/bank

## Solución Implementada

### 1. **Correcciones Realizadas**
- ✅ Rutas del frontend actualizadas a `/bank/api/*`
- ✅ Aliases agregados en backend para compatibilidad con `/api/*`
- ✅ Logs de depuración agregados a `doLogin()`
- ✅ Service Worker actualizado para limpiar cache
- ✅ Página de test creada para diagnóstico

### 2. **Cómo Probar**

#### Opción A: Página de Test (Recomendado)
1. Abre tu navegador
2. Ve a: **http://localhost:8000/bank/test-login**
3. Verás una página de diagnóstico con varios botones de test
4. Haz clic en "Test Servidor" para verificar conectividad
5. Ingresa tu usuario y contraseña
6. Haz clic en "Test Login" para probar el endpoint principal
7. Revisa el log en la parte inferior de la página

#### Opción B: Limpiar Cache y Probar Login Normal
1. Abre https://dvta.ch/bank
2. Presiona **Ctrl + Shift + Delete** (o Cmd + Shift + Delete en Mac)
3. Selecciona "Cached images and files" y "Cookies and other site data"
4. Haz clic en "Clear data"
5. Cierra y vuelve a abrir el navegador
6. Ve a https://dvta.ch/bank
7. Intenta hacer login

#### Opción C: Modo Incógnito
1. Abre una ventana de incógnito/privada
2. Ve a https://dvta.ch/bank
3. Intenta hacer login
4. Esto evita problemas de cache

### 3. **Verificar en Consola del Navegador**

1. Abre las herramientas de desarrollador (F12)
2. Ve a la pestaña "Console"
3. Intenta hacer login
4. Deberías ver logs como:
   ```
   [DEBUG] doLogin called
   [DEBUG] Username: tu_usuario Password length: X
   [DEBUG] Calling API: /bank/api/login
   [DEBUG] Login response: {token: "...", username: "..."}
   ```

### 4. **Posibles Problemas y Soluciones**

#### Problema: "No pasa nada al hacer clic"
**Causa:** Cache del navegador con versión antigua
**Solución:** Limpia el cache (Opción B arriba) o usa modo incógnito

#### Problema: Error "Failed to fetch"
**Causa:** Servidor no está corriendo
**Solución:** 
```cmd
cd c:\dvdcoin
python src\main.py
```

#### Problema: Error 401 "Invalid credentials"
**Causa:** Usuario o contraseña incorrectos
**Solución:** Verifica tus credenciales o regístrate primero

#### Problema: Error 404 en /bank/api/login
**Causa:** Servidor no tiene los aliases configurados
**Solución:** Reinicia el servidor para cargar los cambios

### 5. **Verificar que el Servidor Está Corriendo**

```cmd
netstat -ano | findstr ":8000"
```

Deberías ver algo como:
```
TCP    0.0.0.0:8000           0.0.0.0:0              LISTENING       12345
```

Si no ves nada, inicia el servidor:
```cmd
cd c:\dvdcoin
python src\main.py
```

### 6. **Reiniciar el Servidor**

Si hiciste cambios en el código, reinicia el servidor:

1. Encuentra el proceso:
   ```cmd
   netstat -ano | findstr ":8000"
   ```

2. Mata el proceso (reemplaza 12345 con el PID real):
   ```cmd
   taskkill /F /PID 12345
   ```

3. Inicia de nuevo:
   ```cmd
   cd c:\dvdcoin
   python src\main.py
   ```

### 7. **Archivos Modificados**

- `static/index.html` - Frontend con rutas corregidas y logs de debug
- `static/sw.js` - Service Worker actualizado (v2-20260527)
- `src/main.py` - Backend con aliases agregados
- `TEST_LOGIN.html` - Página de diagnóstico
- `CORRECCION_LOGIN_SISTEMA.md` - Documentación completa

### 8. **Próximos Pasos**

Una vez que confirmes que el login funciona:

1. Puedes remover los logs de debug de `doLogin()` si quieres
2. La página de test quedará disponible en `/bank/test-login` para futuras pruebas
3. Los aliases en el backend garantizan compatibilidad con todos los archivos HTML

---

**¿Necesitas ayuda?**
- Revisa la consola del navegador (F12 → Console)
- Usa la página de test en `/bank/test-login`
- Verifica que el servidor esté corriendo en el puerto 8000
