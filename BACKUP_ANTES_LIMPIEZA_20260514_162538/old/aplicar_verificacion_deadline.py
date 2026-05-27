#!/usr/bin/env python3
"""
Script para aplicar verificación de deadline en tiempo real a todas las porras
"""

import os
import re
from pathlib import Path

def aplicar_verificacion_deadline(filepath):
    """Aplica verificación de deadline en tiempo real"""
    
    print(f"📝 Actualizando: {filepath}")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Buscar el patrón de verificación simple
    pattern_simple = r"(document\.getElementById\('estadoBadge'\)\.textContent=traducirEstado\(p\.estado\);[\s\S]*?document\.getElementById\('totalBote'\)\.textContent=stats\.total_bote\.toFixed\(1\);[\s\S]*?)(?:const|let|var)\s+porraCerrada\s*=\s*p\.estado\s*===\s*'cerrada'"
    
    replacement = r"""\1// VERIFICAR DEADLINE EN TIEMPO REAL
    let porraCerrada = p.estado === 'cerrada' || p.estado === 'finalizada' || p.estado === 'cancelada';
    let mensajeCierre = '';
    
    // Si está "abierta", verificar si el deadline ya pasó
    if(p.estado === 'abierta' && p.fecha_limite){
      try{
        const ahora = new Date();
        const limite = new Date(p.fecha_limite);
        
        if(ahora >= limite){
          porraCerrada = true;
          mensajeCierre = 'La fecha límite ha pasado. Las apuestas están cerradas.';
          console.log('⏰ Deadline pasado, bloqueando apuestas');
        }
      }catch(e){
        console.error('Error verificando deadline:', e);
      }
    }
    
    // Determinar mensaje según estado
    if(!mensajeCierre){
      if(p.estado === 'cerrada'){
        mensajeCierre = 'Esperando resolución del resultado.';
      }else if(p.estado === 'finalizada'){
        mensajeCierre = 'La porra ha sido finalizada.';
      }else if(p.estado === 'cancelada'){
        mensajeCierre = 'La porra ha sido cancelada.';
      }
    }
    
    // Verificar si la porra está cerrada"""
    
    if re.search(pattern_simple, content):
        content = re.sub(pattern_simple, replacement, content)
        print(f"   ✅ Aplicada verificación de deadline (patrón simple)")
    else:
        # Buscar patrón alternativo
        pattern_alt = r"(document\.getElementById\('totalBote'\)\.textContent=stats\.total_bote\.toFixed\(1\);[\s\S]*?)(?:const|let|var)\s+porraCerrada\s*="
        
        if re.search(pattern_alt, content):
            replacement_alt = r"""\1
    // VERIFICAR DEADLINE EN TIEMPO REAL
    let porraCerrada = p.estado === 'cerrada' || p.estado === 'finalizada' || p.estado === 'cancelada';
    let mensajeCierre = '';
    
    // Si está "abierta", verificar si el deadline ya pasó
    if(p.estado === 'abierta' && p.fecha_limite){
      try{
        const ahora = new Date();
        const limite = new Date(p.fecha_limite);
        
        if(ahora >= limite){
          porraCerrada = true;
          mensajeCierre = 'La fecha límite ha pasado. Las apuestas están cerradas.';
          console.log('⏰ Deadline pasado, bloqueando apuestas');
        }
      }catch(e){
        console.error('Error verificando deadline:', e);
      }
    }
    
    // Determinar mensaje según estado
    if(!mensajeCierre){
      if(p.estado === 'cerrada'){
        mensajeCierre = 'Esperando resolución del resultado.';
      }else if(p.estado === 'finalizada'){
        mensajeCierre = 'La porra ha sido finalizada.';
      }else if(p.estado === 'cancelada'){
        mensajeCierre = 'La porra ha sido cancelada.';
      }
    }
    
    let porraCerrada ="""
            
            content = re.sub(pattern_alt, replacement_alt, content)
            print(f"   ✅ Aplicada verificación de deadline (patrón alternativo)")
        else:
            print(f"   ⚠️  No se encontró el patrón para actualizar")
            return False
    
    # Actualizar el mensaje en el panel cerrado para usar la variable mensajeCierre
    old_message = r"\$\{p\.estado === 'cerrada' \? 'Esperando resolución del resultado\.' : \s*p\.estado === 'finalizada' \? 'La porra ha sido finalizada\.' : \s*'La porra ha sido cancelada\.'\}"
    new_message = "${mensajeCierre}"
    
    if re.search(old_message, content):
        content = re.sub(old_message, new_message, content)
        print(f"   ✅ Actualizado mensaje dinámico")
    
    # Guardar archivo
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"   ✅ Archivo actualizado exitosamente\n")
    return True

def main():
    """Aplica verificación de deadline a todas las porras"""
    
    print("🚀 Aplicando verificación de deadline en tiempo real\n")
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
    errores = 0
    
    for porra_file in sorted(porra_files):
        try:
            if aplicar_verificacion_deadline(porra_file):
                actualizados += 1
        except Exception as e:
            print(f"   ❌ Error al actualizar {porra_file}: {e}\n")
            errores += 1
    
    print("=" * 60)
    print("\n📊 RESUMEN:")
    print(f"   ✅ Actualizados: {actualizados}")
    print(f"   ❌ Errores: {errores}")
    print(f"   📁 Total procesados: {len(porra_files)}")
    
    if actualizados > 0:
        print("\n🎉 ¡Actualización completada!")
        print("\n📝 Cambios aplicados:")
        print("   1. ✅ Verificación de deadline en tiempo real")
        print("   2. ✅ Bloqueo automático si pasó el deadline")
        print("   3. ✅ Mensaje claro: 'La fecha límite ha pasado'")
        print("   4. ✅ Panel de apuestas bloqueado")
    
    print("\n" + "=" * 60)

if __name__ == '__main__':
    main()
