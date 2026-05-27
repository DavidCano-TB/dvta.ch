#!/usr/bin/env python3
"""
Script para actualizar todas las porras existentes con:
1. Contador de votos visible
2. Botón de cerrar para DVD
"""

import os
import sqlite3
import shutil

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_BETS = os.path.join(BASE_DIR, "data", "apuestas.db")
PORRAS_DIR = os.path.join(BASE_DIR, "game_pages", "apuestas", "porras")
TEMPLATE_PATH = os.path.join(BASE_DIR, "game_pages", "apuestas", "template_porra.html")

def main():
    print("🔄 Actualizando porras existentes con votos y botón de cerrar...\n")
    
    if not os.path.exists(DB_BETS):
        print(f"❌ Base de datos no encontrada: {DB_BETS}")
        return
    
    if not os.path.exists(TEMPLATE_PATH):
        print(f"❌ Template no encontrado: {TEMPLATE_PATH}")
        return
    
    # Get all porras from database
    conn = sqlite3.connect(DB_BETS)
    conn.row_factory = sqlite3.Row
    porras = conn.execute("""
        SELECT id, titulo, descripcion, tipo, fecha_limite, fecha_evento, creador, opciones_json
        FROM porras
        ORDER BY id
    """).fetchall()
    conn.close()
    
    if not porras:
        print("⚠️  No se encontraron porras en la base de datos")
        return
    
    print(f"📊 Encontradas {len(porras)} porras en la base de datos\n")
    
    # Read template
    with open(TEMPLATE_PATH, 'r', encoding='utf-8') as f:
        template = f.read()
    
    actualizadas = 0
    errores = 0
    
    for porra in porras:
        porra_id = porra['id']
        titulo = porra['titulo'] or f"Porra #{porra_id}"
        
        try:
            import json
            opciones = json.loads(porra['opciones_json'])
            
            # Generate options HTML
            opciones_html = ""
            colors = ['#38B87A', '#4878D8', '#E07840', '#D4A843', '#C83060', '#6B9BD4', '#E05260', '#8BB3E8']
            icons = [
                '⚽', '🏀', '🎾', '🏈', '⚾', '🏐', '🏓', '🏸',
                '🎯', '🎲', '🎰', '🃏', '🎴', '🀄',
                '🏆', '🥇', '🥈', '🥉', '🏅', '👑',
                '⭐', '✨', '💫', '🌟', '💎', '💰',
                '🔥', '⚡', '💥', '🌈', '🎪', '🎭',
                '🚀', '🎸', '🎬', '📺', '🎮', '🎵',
                '🍕', '🍔', '🍰', '🍺', '☕', '🍷',
                '🌍', '🌙', '☀️', '🌊', '🔔', '📱'
            ]
            
            import random
            random.seed(porra_id)
            shuffled_icons = random.sample(icons, min(len(icons), len(opciones)))
            
            for i, opt in enumerate(opciones):
                color = colors[i % len(colors)]
                nombre = opt.get('nombre', f'Opción {i+1}')
                valor = opt.get('valor', f'opcion_{i+1}')
                icon = shuffled_icons[i] if i < len(shuffled_icons) else '🎯'
                
                opciones_html += f'''
        <div class="optCard" data-valor="{valor}" onclick="selectOption('{valor}')">
          <div class="optIcon" style="background:{color}">{icon}</div>
          <div class="optName">{nombre}</div>
          <div class="optStats" id="stats_{valor}">
            <div class="optStat"><span class="optStatLbl">👥 Votos:</span><span class="optStatVal" style="font-size:1.1rem;color:var(--gold2);">0</span></div>
            <div class="optStat"><span class="optStatLbl">% del Bote:</span><span class="optStatVal">0%</span></div>
          </div>
        </div>'''
            
            # Format dates
            from datetime import datetime as dt
            try:
                fl = dt.fromisoformat(porra['fecha_limite'].replace('Z', '+00:00'))
                fe = dt.fromisoformat(porra['fecha_evento'].replace('Z', '+00:00'))
                fecha_limite_fmt = fl.strftime('%d/%m/%Y %H:%M')
                fecha_evento_fmt = fe.strftime('%d/%m/%Y %H:%M')
            except:
                fecha_limite_fmt = porra['fecha_limite']
                fecha_evento_fmt = porra['fecha_evento']
            
            # Replace placeholders
            html_content = template
            html_content = html_content.replace('${PORRA_ID}', str(porra_id))
            
            replacements = {
                '{PORRA_ID}': str(porra_id),
                '{TITULO}': titulo,
                '{DESCRIPCION}': porra['descripcion'] or '',
                '{CREADOR}': porra['creador'],
                '{FECHA_LIMITE}': fecha_limite_fmt,
                '{FECHA_EVENTO}': fecha_evento_fmt,
                '{TIPO}': porra['tipo'] or 'Deportiva',
                '{OPCIONES_HTML}': opciones_html
            }
            
            for placeholder, value in replacements.items():
                html_content = html_content.replace(placeholder, value)
            
            # Write files
            import re
            titulo_safe = re.sub(r'[<>:"/\|?*]', '', titulo)
            titulo_safe = titulo_safe.strip()[:50]
            
            page_path_id = os.path.join(PORRAS_DIR, f"porra_{porra_id}.html")
            page_path_descriptive = os.path.join(PORRAS_DIR, f'porra ({titulo_safe}).html')
            
            # Backup old file
            if os.path.exists(page_path_id):
                backup_path = page_path_id + '.backup'
                shutil.copy2(page_path_id, backup_path)
            
            # Write new files
            with open(page_path_id, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            with open(page_path_descriptive, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            print(f"✅ Porra {porra_id}: {titulo}")
            actualizadas += 1
            
        except Exception as e:
            print(f"❌ Porra {porra_id}: Error - {e}")
            errores += 1
    
    print("\n" + "="*80)
    print(f"\n📊 RESUMEN:")
    print(f"   ✅ Porras actualizadas: {actualizadas}")
    print(f"   ❌ Errores: {errores}")
    print("="*80)
    
    if actualizadas > 0:
        print("\n✅ Actualización completada exitosamente")
        print("\n📝 CAMBIOS APLICADOS:")
        print("   • Contador de votos visible en cada opción")
        print("   • Botón de cerrar para DVD (solo en porras abiertas)")
        print("   • Total de votos en estadísticas generales")

if __name__ == "__main__":
    main()
