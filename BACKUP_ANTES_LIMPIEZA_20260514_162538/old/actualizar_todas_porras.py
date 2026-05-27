#!/usr/bin/env python3
"""
Script para actualizar todas las porras HTML con la nueva lógica de:
1. Bloqueo de apuestas cuando está cerrada
2. Mensaje claro de estado
3. Traducción de badges
"""

import os
import re
from pathlib import Path

def actualizar_porra_html(filepath):
    """Actualiza un archivo HTML de porra con la nueva lógica"""
    
    print(f"📝 Actualizando: {filepath}")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Verificar si ya tiene la nueva lógica
    if 'traducirEstado' in content and 'Apuestas Cerradas' in content:
        print(f"   ✅ Ya tiene la nueva lógica, saltando...")
        return False
    
    # 1. Buscar y reemplazar la lógica de mostrar/ocultar panel de apuestas
    old_pattern = r"document\.getElementById\('betPanel'\)\.style\.display=p\.estado==='abierta'\?'':'none';"
    
    new_logic = """// Verificar si la porra está cerrada o finalizada
    const porraCerrada = p.estado === 'cerrada' || p.estado === 'finalizada' || p.estado === 'cancelada';
    
    // Mostrar panel de apuestas solo si está abierta
    const betPanel = document.getElementById('betPanel');
    if(porraCerrada){
      // Mostrar mensaje de porra cerrada
      betPanel.innerHTML = `
        <div class="betTitle">⏰ Apuestas Cerradas</div>
        <div style="text-align:center;padding:20px;color:var(--text2);font-size:.9rem;">
          <p style="margin-bottom:10px;">Esta porra ya no acepta más apuestas.</p>
          <p style="color:var(--text3);font-size:.8rem;">
            ${p.estado === 'cerrada' ? 'Esperando resolución del resultado.' : 
              p.estado === 'finalizada' ? 'La porra ha sido finalizada.' : 
              'La porra ha sido cancelada.'}
          </p>
        </div>
      `;
      betPanel.style.display = '';
    }else{
      // Restaurar panel de apuestas original si está abierta
      betPanel.innerHTML = `
        <div class="betTitle">💰 Realizar Apuesta</div>
        <div style="margin-bottom:14px;font-size:.8rem;color:var(--text2);text-align:center;">
          Selecciona una opción arriba e introduce la cantidad a apostar.<br>
          <strong style="color:var(--gold2);">✨ Puedes apostar múltiples veces en diferentes opciones</strong>
        </div>
        <input type="number" class="betInput" id="betAmount" placeholder="Cantidad en DVDcoins" min="1" step="1">
        <button class="btn btnG" id="betBtn" onclick="realizarApuesta()" disabled>💸 Apostar Ahora</button>
      `;
      betPanel.style.display = '';
    }"""
    
    if re.search(old_pattern, content):
        content = re.sub(old_pattern, new_logic, content)
        print(f"   ✅ Actualizada lógica de panel de apuestas")
    else:
        print(f"   ⚠️  No se encontró el patrón antiguo de panel de apuestas")
    
    # 2. Agregar función traducirEstado si no existe
    if 'function traducirEstado' not in content:
        # Buscar el final de la función render (antes de la siguiente función)
        render_end = content.find('function selectOption')
        if render_end == -1:
            render_end = content.find('function realizarApuesta')
        
        if render_end != -1:
            traducir_function = """

// Función para traducir estados
function traducirEstado(estado){
  const traducciones = {
    'abierta': 'Abierta',
    'cerrada': 'Cerrada',
    'finalizada': 'Finalizada',
    'cancelada': 'Cancelada'
  };
  return traducciones[estado] || estado;
}

"""
            content = content[:render_end] + traducir_function + content[render_end:]
            print(f"   ✅ Agregada función traducirEstado")
    
    # 3. Actualizar el badge para usar traducirEstado
    old_badge = r"document\.getElementById\('estadoBadge'\)\.textContent=p\.estado;"
    new_badge = "document.getElementById('estadoBadge').textContent=traducirEstado(p.estado);"
    
    if re.search(old_badge, content):
        content = re.sub(old_badge, new_badge, content)
        print(f"   ✅ Actualizado badge para usar traducción")
    
    # Guardar archivo actualizado
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"   ✅ Archivo actualizado exitosamente\n")
    return True

def main():
    """Actualiza todas las porras HTML"""
    
    print("🚀 Iniciando actualización de todas las porras HTML\n")
    print("=" * 60)
    
    porras_dir = Path('game_pages/apuestas/porras')
    
    if not porras_dir.exists():
        print(f"❌ Error: No se encontró el directorio {porras_dir}")
        return
    
    # Buscar todos los archivos HTML de porras
    porra_files = list(porras_dir.glob('porra_*.html'))
    
    if not porra_files:
        print(f"❌ No se encontraron archivos de porras en {porras_dir}")
        return
    
    print(f"📁 Encontrados {len(porra_files)} archivos de porras\n")
    
    actualizados = 0
    saltados = 0
    errores = 0
    
    for porra_file in sorted(porra_files):
        try:
            if actualizar_porra_html(porra_file):
                actualizados += 1
            else:
                saltados += 1
        except Exception as e:
            print(f"   ❌ Error al actualizar {porra_file}: {e}\n")
            errores += 1
    
    print("=" * 60)
    print("\n📊 RESUMEN:")
    print(f"   ✅ Actualizados: {actualizados}")
    print(f"   ⏭️  Saltados (ya actualizados): {saltados}")
    print(f"   ❌ Errores: {errores}")
    print(f"   📁 Total procesados: {len(porra_files)}")
    
    if actualizados > 0:
        print("\n🎉 ¡Actualización completada!")
        print("\n📝 Cambios aplicados:")
        print("   1. ✅ Bloqueo de apuestas cuando está cerrada")
        print("   2. ✅ Mensaje '⏰ Apuestas Cerradas' con explicación")
        print("   3. ✅ Traducción de badges al español")
        print("   4. ✅ Panel de apuestas dinámico según estado")
    
    print("\n" + "=" * 60)

if __name__ == '__main__':
    main()
