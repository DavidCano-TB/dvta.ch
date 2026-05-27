#!/usr/bin/env python3
"""
Script v2 para actualizar TODAS las porras HTML con la lógica completa de:
1. Verificación de deadline
2. Bloqueo de apuestas cuando está cerrada
3. Mensaje claro de estado
4. Traducción de badges
"""

import os
import re
from pathlib import Path

def actualizar_porra_completa(filepath):
    """Actualiza un archivo HTML de porra con la lógica completa"""
    
    print(f"📝 Actualizando: {filepath}")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    cambios = []
    
    # 1. Asegurar que tiene la función traducirEstado
    if 'function traducirEstado' not in content:
        # Buscar donde insertar (antes de selectOption o realizarApuesta)
        insert_pos = content.find('function selectOption')
        if insert_pos == -1:
            insert_pos = content.find('function realizarApuesta')
        
        if insert_pos != -1:
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
            content = content[:insert_pos] + traducir_function + content[insert_pos:]
            cambios.append("Agregada función traducirEstado")
    
    # 2. Actualizar badge para usar traducción
    if "document.getElementById('estadoBadge').textContent=p.estado;" in content:
        content = content.replace(
            "document.getElementById('estadoBadge').textContent=p.estado;",
            "document.getElementById('estadoBadge').textContent=traducirEstado(p.estado);"
        )
        cambios.append("Badge actualizado para usar traducción")
    
    # 3. Buscar y actualizar la lógica del panel de apuestas
    # Patrón 1: Lógica simple de mostrar/ocultar
    pattern1 = r"document\.getElementById\('betPanel'\)\.style\.display=p\.estado==='abierta'\?'':'none';"
    
    if re.search(pattern1, content):
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
            \${p.estado === 'cerrada' ? 'Esperando resolución del resultado.' : 
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
        
        content = re.sub(pattern1, new_logic, content)
        cambios.append("Actualizada lógica de panel de apuestas (patrón simple)")
    
    # Patrón 2: Lógica con verificación de deadline
    # Buscar si ya tiene lógica de deadline pero necesita actualización
    if 'let porraCerrada' in content and 'betPanel.innerHTML' not in content:
        # Tiene la variable pero no el innerHTML dinámico
        # Buscar donde está el manejo del betPanel
        pattern2 = r"(let porraCerrada[^;]+;[\s\S]*?)(document\.getElementById\('betPanel'\)\.style\.display[^;]+;)"
        
        replacement2 = r"""\1
    // Mostrar panel de apuestas solo si está abierta
    const betPanel = document.getElementById('betPanel');
    if(porraCerrada){
      // Mostrar mensaje de porra cerrada
      betPanel.innerHTML = `
        <div class="betTitle">⏰ Apuestas Cerradas</div>
        <div style="text-align:center;padding:20px;color:var(--text2);font-size:.9rem;">
          <p style="margin-bottom:10px;">Esta porra ya no acepta más apuestas.</p>
          <p style="color:var(--text3);font-size:.8rem;">
            \${p.estado === 'cerrada' ? 'Esperando resolución del resultado.' : 
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
        
        if re.search(pattern2, content):
            content = re.sub(pattern2, replacement2, content)
            cambios.append("Actualizada lógica de panel con verificación de deadline")
    
    # Guardar si hubo cambios
    if cambios:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        for cambio in cambios:
            print(f"   ✅ {cambio}")
        print(f"   ✅ Archivo actualizado exitosamente\n")
        return True
    else:
        print(f"   ℹ️  Sin cambios necesarios\n")
        return False

def main():
    """Actualiza todas las porras HTML"""
    
    print("🚀 Iniciando actualización v2 de todas las porras HTML\n")
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
    sin_cambios = 0
    errores = 0
    
    for porra_file in sorted(porra_files):
        try:
            if actualizar_porra_completa(porra_file):
                actualizados += 1
            else:
                sin_cambios += 1
        except Exception as e:
            print(f"   ❌ Error al actualizar {porra_file}: {e}\n")
            errores += 1
    
    print("=" * 60)
    print("\n📊 RESUMEN:")
    print(f"   ✅ Actualizados: {actualizados}")
    print(f"   ℹ️  Sin cambios: {sin_cambios}")
    print(f"   ❌ Errores: {errores}")
    print(f"   📁 Total procesados: {len(porra_files)}")
    
    if actualizados > 0:
        print("\n🎉 ¡Actualización completada!")
        print("\n📝 Cambios aplicados:")
        print("   1. ✅ Función traducirEstado agregada")
        print("   2. ✅ Badges traducidos al español")
        print("   3. ✅ Panel de apuestas dinámico según estado")
        print("   4. ✅ Mensaje '⏰ Apuestas Cerradas' implementado")
    
    print("\n" + "=" * 60)

if __name__ == '__main__':
    main()
