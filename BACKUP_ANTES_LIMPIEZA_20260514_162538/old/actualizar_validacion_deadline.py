#!/usr/bin/env python3
"""Script para añadir validación de deadline en todas las páginas de porras."""

import os
import re

PORRAS_DIR = "game_pages/apuestas/porras"

def actualizar_porra(filepath):
    """Actualiza una página de porra con validación de deadline mejorada."""
    print(f"Procesando: {filepath}")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Verificar si ya tiene la validación mejorada
    if 'Ya no se puede apostar más' in content:
        print(f"  ✓ Ya tiene validación mejorada\n")
        return 0
    
    # Patrón 1: Buscar validación simple
    pattern1 = r"(\s+)// Mostrar panel de apuestas solo si está abierta\s+document\.getElementById\('betPanel'\)\.style\.display=p\.estado==='abierta'\?'':'none';"
    
    # Patrón 2: Buscar validación en porras con estadísticas personales (porra_2, porra_3)
    pattern2 = r"(\s+)// SIEMPRE mostrar panel de apuestas si la porra está abierta \(permite múltiples apuestas\)\s+document\.getElementById\('betPanel'\)\.style\.display=p\.estado==='abierta'\?'':'none';"
    
    replacement1 = r"""\1// VALIDACIÓN CRÍTICA: Verificar si la deadline ha pasado
\1let porraCerrada = p.estado === 'cerrada' || p.estado === 'finalizada' || p.estado === 'cancelada';
\1let mensajeCierre = '';
\1
\1// Verificar deadline SIEMPRE, incluso si el estado es "abierta"
\1if(p.fecha_limite){
\1  try{
\1    const ahora = new Date();
\1    const limite = new Date(p.fecha_limite);
\1    
\1    if(ahora >= limite){
\1      porraCerrada = true;
\1      const fechaFormateada = limite.toLocaleString('es-ES', {
\1        day: '2-digit',
\1        month: '2-digit',
\1        year: 'numeric',
\1        hour: '2-digit',
\1        minute: '2-digit'
\1      });
\1      mensajeCierre = `La fecha límite (${fechaFormateada}) ha pasado.`;
\1      console.log('⏰ Deadline pasada:', fechaFormateada);
\1    }
\1  }catch(e){
\1    console.error('Error verificando deadline:', e);
\1  }
\1}
\1
\1// Determinar mensaje según el estado
\1if(!mensajeCierre){
\1  if(p.estado === 'cerrada'){
\1    mensajeCierre = 'Esperando resolución del resultado.';
\1  }else if(p.estado === 'finalizada'){
\1    mensajeCierre = 'La porra ha sido finalizada.';
\1  }else if(p.estado === 'cancelada'){
\1    mensajeCierre = 'La porra ha sido cancelada.';
\1  }
\1}
\1
\1// Mostrar panel de apuestas solo si está abierta Y no ha pasado la deadline
\1const betPanel = document.getElementById('betPanel');
\1if(porraCerrada){
\1  // Mostrar mensaje claro: YA NO SE PUEDE APOSTAR MÁS
\1  betPanel.innerHTML = `
\1    <div class="betTitle" style="color:var(--red);">⏰ Ya no se puede apostar más</div>
\1    <div style="text-align:center;padding:20px;color:var(--text2);font-size:.9rem;">
\1      <p style="margin-bottom:10px;font-size:1rem;color:var(--text);">Esta porra ya no acepta apuestas.</p>
\1      <p style="color:var(--text3);font-size:.85rem;margin-top:12px;">
\1        ${mensajeCierre}
\1      </p>
\1    </div>
\1  `;
\1  betPanel.style.display = '';
\1}else{
\1  // Panel de apuestas activo
\1  document.getElementById('betPanel').style.display = '';
\1}"""
    
    # Intentar con patrón 1
    if re.search(pattern1, content):
        content = re.sub(pattern1, replacement1, content)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  ✅ Validación mejorada añadida (patrón 1)\n")
        return 1
    
    # Intentar con patrón 2 (porras con estadísticas personales)
    if re.search(pattern2, content):
        content = re.sub(pattern2, replacement1, content)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  ✅ Validación mejorada añadida (patrón 2)\n")
        return 1
    
    print(f"  ⏭️  Patrón no encontrado o ya actualizado\n")
    return 0

def main():
    print("=" * 70)
    print("ACTUALIZANDO VALIDACIÓN DE DEADLINE - VERSIÓN MEJORADA")
    print("=" * 70)
    print()
    
    porras = [f for f in os.listdir(PORRAS_DIR) if f.startswith('porra_') and f.endswith('.html')]
    porras.sort()
    
    print(f"Encontradas {len(porras)} páginas\n")
    
    total = 0
    for porra in porras:
        total += actualizar_porra(os.path.join(PORRAS_DIR, porra))
    
    print("=" * 70)
    print(f"✅ Completado: {total} páginas actualizadas")
    print("=" * 70)
    print()
    print("Mensaje: 'Ya no se puede apostar más' implementado")
    print()

if __name__ == "__main__":
    main()
