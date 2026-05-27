# Cambios Pendientes - DVDcoin Frontend

## 1. Actualizar archivos de idiomas
- ✅ Añadir traducciones faltantes para "signOut", "votaciones", "apuestas"
- ✅ Añadir traducciones para todos los idiomas: es, en, fr, ca, eu, de, it

## 2. Unificar navegación en TODOS los HTML
Archivos que necesitan navegación unificada:
- static/index.html ✅
- static/pages/index.html
- static/votaciones.html (CREAR/ACTUALIZAR)
- static/apuestas.html (CREAR/ACTUALIZAR)
- static/stats.html
- static/chat.html
- static/mensajes.html
- static/cuentos.html
- static/cuentos_admin.html
- static/cuentos_member.html
- static/opo/game.html
- static/hundirlaflota/game.html (VERIFICAR)

## 3. Permisos de Admin
- Hacer que TODOS los admins puedan:
  - Ver y jugar Pasapalabra
  - Ver y jugar Millonario
  - Ver y jugar ¿Quién soy?
  - Ver y jugar Cifras y Letras
  - Ver y jugar Hundir la Flota
  - Subir cuentos desde la pestaña Cuentos

## 4. Navegación
- Quitar botón "Cuentos" duplicado
- Verificar que solo hay UN icono por pestaña
- Pestañas con iconos duplicados a corregir:
  - Cuentos: 📖
  - Stats: 📊
  - Otros

## 5. Archivos HTML principales a actualizar
1. static/index.html
2. static/pages/index.html
3. static/votaciones.html
4. static/apuestas.html
5. static/stats.html
6. static/chat.html
7. static/mensajes.html
8. static/cuentos.html
9. static/cuentos_admin.html
10. static/cuentos_member.html

## Orden de ejecución:
1. Actualizar archivos i18n (todos los idiomas)
2. Actualizar navegación unificada
3. Actualizar permisos de admin
4. Aplicar cambios a todos los HTML
