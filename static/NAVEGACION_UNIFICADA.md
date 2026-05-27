# Sistema de Navegación Unificada - DVDcoin Bank

## 📋 Descripción

Sistema centralizado de navegación que se adapta automáticamente según el rol del usuario (miembro, admin, superadmin, dvd) y muestra las pestañas correspondientes en todas las páginas HTML del proyecto.

## 🎯 Características

- **Adaptación por roles**: Muestra pestañas diferentes según el rol del usuario
- **Detección dinámica**: Oculta/muestra pestañas de juegos según su estado (habilitado/deshabilitado)
- **Consistencia total**: Todas las páginas HTML usan el mismo sistema
- **Responsive**: Se adapta a móviles y desktop
- **Sticky navigation**: La barra permanece visible al hacer scroll
- **Marca pestaña activa**: Resalta automáticamente la página actual

## 📁 Archivos del Sistema

```
static/
├── css/
│   └── unified-nav.css          # Estilos de la navegación
├── js/
│   └── unified-nav.js           # Lógica de navegación
└── _nav-include.html            # Snippet de referencia
```

## 🔧 Implementación en Páginas HTML

Cada página HTML debe incluir:

### 1. En el `<head>`:
```html
<link rel="stylesheet" href="/static/css/unified-nav.css">
```

### 2. En el `<body>` (añadir clase):
```html
<body class="has-unified-nav">
```

### 3. Justo después del `<body>`:
```html
<!-- Navegación Unificada -->
<div id="unifiedNavContainer"></div>
```

### 4. Antes del `</body>`:
```html
<!-- Sistema de Navegación Unificada -->
<script src="/static/js/unified-nav.js"></script>
```

## 👥 Configuración de Pestañas por Rol

### 🔹 Miembros (usuarios normales)
- 🏦 Inicio
- 💸 Transferir
- 📜 Historial
- 🖼️ Galería
- 📖 Cuentos (si está habilitado)
- 💬 Social (si está habilitado)
- 🎥 Video (si está habilitado)
- 🎯 Pasapalabra (si está habilitado)
- 💰 Millonario (si está habilitado)
- 🎭 ¿Quién soy? (si está habilitado)
- 🔤 Cifras y Letras (si está habilitado)
- ⚓ Hundir la Flota (si está habilitado)
- 🎲 Apuestas
- 🗳️ Votaciones

### 🔸 Admins
- 🏦 Inicio
- 💸 Transferir
- 📜 Historial
- 🖼️ Galería
- 📖 Cuentos (panel admin)
- 💬 Mensajes (panel admin)
- 🎥 Video (panel admin)
- 🎯 Pasapalabra (panel admin)
- 💰 Millonario (panel admin)
- 🎭 ¿Quién soy? (panel admin)
- 🔤 Cifras y Letras (panel admin)
- 🎲 Apuestas (panel admin)
- 🗳️ Votaciones (panel admin)
- ⚙️ Admin

### 🔶 Superadmins
Todo lo de Admin +
- 📊 Stats

### 🔷 DVD (usuario especial)
Todo lo de Superadmin +
- 🎓 OPO

## 🎮 Detección Dinámica de Juegos

El sistema verifica automáticamente el estado de cada juego/feature mediante endpoints:

```javascript
{
  id: 'pasapalabra',
  checkEndpoint: '/api/pasapalabra/status',
  // Se muestra solo si status.enabled === true
}
```

Endpoints verificados:
- `/api/cuentos/status`
- `/api/messages/status`
- `/api/rooms/status`
- `/api/pasapalabra/status`
- `/api/millonario/status`
- `/api/quiensoy/status`
- `/api/cifrasletras/status`
- `/api/hundirlaflota/status`

## 🔄 API Pública

El sistema expone una API global `window.UnifiedNav`:

```javascript
// Inicializar manualmente (se auto-inicializa al cargar)
UnifiedNav.init();

// Refrescar navegación (útil después de cambios de estado)
UnifiedNav.refresh();
```

## 🎨 Personalización de Estilos

Los estilos están en `static/css/unified-nav.css` y usan variables CSS:

```css
.unified-nav {
  --nav-bg: rgba(4, 4, 10, 0.97);
  --nav-border: rgba(212, 168, 67, 0.14);
  --nav-text: rgba(154, 144, 112, 0.7);
  --nav-text-hover: rgba(240, 200, 102, 1);
  --nav-active-bg: rgba(212, 168, 67, 0.15);
}
```

## 📱 Responsive

### Desktop (> 768px)
- Muestra iconos + labels
- Scroll horizontal si hay muchas pestañas

### Tablet (481px - 768px)
- Iconos + labels más compactos

### Mobile (≤ 480px)
- Solo iconos (labels ocultos)
- Pestañas más grandes para touch

## 🛠️ Mantenimiento

### Añadir una nueva pestaña

Editar `static/js/unified-nav.js`:

```javascript
const NAV_CONFIG = {
  member: [
    // ... pestañas existentes
    {
      id: 'nueva-feature',
      icon: '🆕',
      label: 'Nueva Feature',
      href: '/nueva-feature.html',
      dynamic: true,  // opcional
      checkEndpoint: '/api/nueva-feature/status'  // opcional
    }
  ]
};
```

### Actualizar archivos HTML existentes

Si añades nuevos archivos HTML o modificas existentes, ejecuta:

```bash
python scripts/add_unified_nav.py
```

Este script:
- ✅ Detecta archivos HTML sin navegación
- ✅ Añade automáticamente CSS, contenedor y script
- ✅ Añade clase `has-unified-nav` al body
- ✅ Omite archivos que ya tienen navegación

## 🐛 Troubleshooting

### La navegación no aparece
1. Verificar que existe `<div id="unifiedNavContainer"></div>`
2. Verificar que se carga `/static/js/unified-nav.js`
3. Abrir consola del navegador y buscar errores

### Las pestañas no se muestran correctamente
1. Verificar que el usuario está autenticado (token en localStorage)
2. Verificar que `/api/me` devuelve datos correctos
3. Verificar endpoints de estado para features dinámicas

### La pestaña activa no se marca
1. Verificar que los atributos `data-tab-href` y `data-tab-hash` son correctos
2. Verificar que la URL actual coincide con alguna pestaña

## 📊 Estadísticas

- **Archivos procesados**: 43 archivos HTML
- **Líneas de código**: ~500 líneas (JS + CSS)
- **Roles soportados**: 4 (miembro, admin, superadmin, dvd)
- **Pestañas totales**: ~20 pestañas únicas

## 🔐 Seguridad

- ✅ Verificación de token en cada petición
- ✅ Validación de roles en backend
- ✅ No expone información sensible en frontend
- ✅ Endpoints protegidos por autenticación

## 📝 Notas

- El sistema se auto-inicializa cuando el DOM está listo
- Compatible con navegación por hash (#) y por ruta
- No interfiere con navegación existente en index.html
- Mantiene compatibilidad con sistema de pestañas legacy

---

**Última actualización**: 2026-05-14  
**Versión**: 1.0.0  
**Autor**: Sistema DVDcoin Bank
