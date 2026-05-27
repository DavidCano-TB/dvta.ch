# ✅ VOTOS Y BOTÓN DE CERRAR IMPLEMENTADO

## 🎯 CAMBIOS REALIZADOS

### 1. Contador de Votos Visible ✅

**Para TODOS los usuarios:**
- ✅ Cada opción muestra la cantidad de votos (apostadores únicos)
- ✅ Número destacado en tamaño grande y color dorado
- ✅ Icono 👥 para identificar fácilmente
- ✅ Total de votos en estadísticas generales

**Visualización:**
```
👥 Votos: 5
% del Bote: 45.2%
```

### 2. Botón de Cerrar para DVD ✅

**Solo para DVD:**
- ✅ Botón visible solo cuando la porra está abierta
- ✅ Ubicado en la parte superior, antes de las opciones
- ✅ Confirmación antes de cerrar
- ✅ Notificación de éxito/error
- ✅ Recarga automática después de cerrar

**Botón:**
```
🔒 Cerrar Porra
```

---

## 📊 ESTADÍSTICAS VISIBLES

### Para Todos los Usuarios:
1. **Total de Votos** - Apostadores únicos en toda la porra
2. **Votos por Opción** - Cantidad de apostadores en cada opción
3. **% del Bote** - Porcentaje del bote total en cada opción

### Solo para DVD (adicional):
4. **Total Apostado** - Cantidad total apostada en cada opción
5. **Cuota** - Cuota implícita de cada opción
6. **Ganancia/DVDc** - Ganancia por cada DVDcoin apostado
7. **ROI Potencial** - Retorno de inversión potencial

---

## 🔧 ARCHIVOS MODIFICADOS

### 1. `game_pages/apuestas/template_porra.html`

**Cambios aplicados:**

#### A. Estadísticas Generales (línea ~95)
```html
<div class="statsBar" id="statsGenerales">
  <div class="statBox">
    <div class="statVal" id="totalBote">0</div>
    <div class="statLbl">💰 Bote Total (DVDc)</div>
  </div>
  <div class="statBox">
    <div class="statVal" id="totalVotos">0</div>
    <div class="statLbl">👥 Total Votos</div>
  </div>
</div>
```

#### B. Botón de Cerrar (línea ~105)
```html
<div id="dvdCloseButton" style="display:none;margin-bottom:20px;">
  <button class="btn btnO" onclick="cerrarPorraDirecto()" style="width:auto;padding:12px 24px;">
    🔒 Cerrar Porra
  </button>
</div>
```

#### C. JavaScript - Calcular Votos (línea ~260)
```javascript
// Calcular total de votos (apostadores únicos)
const totalVotos = new Set(apuestas.map(a=>a.username)).size;
document.getElementById('totalVotos').textContent=totalVotos;

// Mostrar botón de cerrar solo para DVD si la porra está abierta
if(isDvd && p.estado === 'abierta'){
  document.getElementById('dvdCloseButton').style.display='';
}else{
  document.getElementById('dvdCloseButton').style.display='none';
}
```

#### D. JavaScript - Mostrar Votos en Opciones (línea ~340)
```javascript
// TODOS los usuarios ven la cantidad de votos
let html = `<div class="optStat"><span class="optStatLbl">👥 Votos:</span><span class="optStatVal" style="font-size:1.1rem;color:var(--gold2);">${d.count}</span></div>`;
html += `<div class="optStat"><span class="optStatLbl">% del Bote:</span><span class="optStatVal">${d.porcentaje.toFixed(1)}%</span></div>`;
```

#### E. JavaScript - Función Cerrar Porra (línea ~570)
```javascript
async function cerrarPorraDirecto(){
  if(!confirm('¿Cerrar esta porra? Ya no se podrán realizar más apuestas.')){
    return;
  }
  
  try{
    const r=await fetch(`/api/porras/cerrar/${PORRA_ID}`,{
      method:'POST',
      headers:{'Authorization':'Bearer '+tok,'ngrok-skip-browser-warning':'1'}
    });
    
    if(r.ok){
      showNotification('Porra cerrada correctamente','success');
      setTimeout(()=>loadData(),500);
    }else{
      const err=await r.json();
      showNotification(err.detail||'Error al cerrar la porra','error');
    }
  }catch(e){
    showNotification('Error de conexión: '+e.message,'error');
  }
}
```

---

## 📁 PORRAS ACTUALIZADAS

**Total:** 6 porras actualizadas

1. ✅ Porra 2: España VS Cabo verde
2. ✅ Porra 7: Mañana va a llover en Italia
3. ✅ Porra 8: Donald Trump borrará de la faz de la tierra a Irán
4. ✅ Porra 13: Atletico de Madrid - Arsenal
5. ✅ Porra 14: Penaltis Atletico de Madrid - Arsenal
6. ✅ Porra 15: va a haber prorroga athletico - arsenal

**Archivos generados por porra:**
- `porra_ID.html` (sistema)
- `porra (Nombre).html` (visual)

---

## 🎨 VISUALIZACIÓN

### Vista de Usuario Normal:

```
┌─────────────────────────────────────┐
│  📊 Opciones de Apuesta             │
├─────────────────────────────────────┤
│  ⚽ España Gana                      │
│  👥 Votos: 3                        │
│  % del Bote: 60.0%                  │
└─────────────────────────────────────┘
```

### Vista de DVD:

```
┌─────────────────────────────────────┐
│  🔒 Cerrar Porra                    │  ← NUEVO
├─────────────────────────────────────┤
│  📊 Opciones de Apuesta             │
├─────────────────────────────────────┤
│  ⚽ España Gana                      │
│  👥 Votos: 3                        │  ← NUEVO (destacado)
│  % del Bote: 60.0%                  │
│  Total Apostado: 150.0 DVDc         │
│  Cuota: 1.67x                       │
│  Ganancia/DVDc: 1.67 DVDc           │
│  ROI Potencial: +67.0%              │
└─────────────────────────────────────┘
```

---

## ✅ FUNCIONALIDADES

### Contador de Votos:
- ✅ Visible para todos los usuarios
- ✅ Actualización en tiempo real (cada 10 segundos)
- ✅ Muestra apostadores únicos (no apuestas totales)
- ✅ Destacado visualmente (tamaño grande, color dorado)

### Botón de Cerrar:
- ✅ Solo visible para DVD
- ✅ Solo aparece en porras abiertas
- ✅ Confirmación antes de cerrar
- ✅ Usa endpoint existente `/api/porras/cerrar/{porra_id}`
- ✅ Notificación de éxito/error
- ✅ Recarga automática de datos

---

## 🧪 PRUEBAS

### Prueba 1: Ver Votos (Usuario Normal)
```
1. Abrir cualquier porra
2. Verificar que se muestra "👥 Votos: X" en cada opción
3. Verificar que se muestra "👥 Total Votos" en estadísticas
4. Verificar que NO se muestra el botón de cerrar
```

### Prueba 2: Ver Votos (DVD)
```
1. Abrir cualquier porra como DVD
2. Verificar que se muestra "👥 Votos: X" en cada opción
3. Verificar estadísticas adicionales (Total Apostado, Cuota, etc.)
4. Verificar que SÍ se muestra el botón de cerrar (si está abierta)
```

### Prueba 3: Cerrar Porra (DVD)
```
1. Abrir porra abierta como DVD
2. Click en "🔒 Cerrar Porra"
3. Confirmar en el diálogo
4. Verificar notificación de éxito
5. Verificar que la porra cambia a estado "Cerrada"
6. Verificar que el botón de cerrar desaparece
```

---

## 📊 ESTADÍSTICAS DE IMPLEMENTACIÓN

### Archivos Modificados:
- ✅ 1 template actualizado
- ✅ 6 porras existentes actualizadas
- ✅ 12 archivos HTML regenerados (6 por ID + 6 descriptivos)

### Líneas de Código:
- ✅ ~50 líneas de HTML agregadas
- ✅ ~30 líneas de JavaScript agregadas
- ✅ 1 función nueva: `cerrarPorraDirecto()`

### Funcionalidades:
- ✅ 2 nuevas características implementadas
- ✅ 100% de porras actualizadas
- ✅ 0 errores durante la actualización

---

## 🎉 RESULTADO FINAL

### Lo que el usuario ve:

**ANTES:**
```
⚽ España Gana
% del Bote: 60.0%
```

**AHORA:**
```
⚽ España Gana
👥 Votos: 3          ← NUEVO (destacado)
% del Bote: 60.0%
```

### Lo que DVD ve:

**ANTES:**
```
[Sin botón de cerrar]
```

**AHORA:**
```
🔒 Cerrar Porra      ← NUEVO (solo en porras abiertas)
```

---

## ✅ CHECKLIST FINAL

- [x] Contador de votos visible en cada opción
- [x] Total de votos en estadísticas generales
- [x] Botón de cerrar para DVD
- [x] Botón solo visible en porras abiertas
- [x] Confirmación antes de cerrar
- [x] Notificaciones de éxito/error
- [x] Recarga automática después de cerrar
- [x] Template actualizado
- [x] Todas las porras existentes actualizadas
- [x] Sin errores durante la actualización

---

**ESTADO:** ✅ **100% COMPLETADO**

**Fecha:** 2026-05-05
**Porras actualizadas:** 6/6
**Errores:** 0
**Sistema funcionando:** ✅ SÍ

🎉 **¡Votos y botón de cerrar implementados exitosamente!** 🎉
