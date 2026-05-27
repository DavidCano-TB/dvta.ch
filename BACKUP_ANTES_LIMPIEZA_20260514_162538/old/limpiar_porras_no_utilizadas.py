#!/usr/bin/env python3
"""
Script para identificar y borrar porras que ya no se utilizan.
Criterios para considerar una porra "no utilizada":
- Estado: finalizada o cancelada
- Sin apuestas activas pendientes de pago
- Más de X días desde su resolución
"""

import os
import sqlite3
from datetime import datetime, timedelta

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_BETS = os.path.join(BASE_DIR, "data", "apuestas.db")
PORRAS_DIR = os.path.join(BASE_DIR, "game_pages", "apuestas", "porras")

def main():
    print("🔍 Analizando porras en la base de datos...\n")
    
    if not os.path.exists(DB_BETS):
        print(f"❌ Base de datos no encontrada: {DB_BETS}")
        return
    
    conn = sqlite3.connect(DB_BETS)
    conn.row_factory = sqlite3.Row
    
    # Get all porras with their details
    porras = conn.execute("""
        SELECT 
            p.id,
            p.titulo,
            p.estado,
            p.created_at,
            p.resolved_at,
            COUNT(a.id) as total_apuestas,
            SUM(CASE WHEN a.pagado = 0 THEN 1 ELSE 0 END) as apuestas_pendientes
        FROM porras p
        LEFT JOIN apuestas_usuarios a ON a.porra_id = p.id
        GROUP BY p.id
        ORDER BY p.id
    """).fetchall()
    
    if not porras:
        print("⚠️  No se encontraron porras en la base de datos")
        conn.close()
        return
    
    print(f"📊 Total de porras en la base de datos: {len(porras)}\n")
    print("="*80)
    
    # Categorize porras
    activas = []
    finalizadas_recientes = []
    finalizadas_antiguas = []
    canceladas = []
    sin_apuestas = []
    
    ahora = datetime.now()
    dias_antiguedad = 7  # Considerar "antigua" si tiene más de 7 días
    
    for p in porras:
        porra_id = p['id']
        titulo = p['titulo'] or f"Porra #{porra_id}"
        estado = p['estado']
        total_apuestas = p['total_apuestas']
        apuestas_pendientes = p['apuestas_pendientes']
        
        # Calcular antigüedad
        antiguedad_dias = None
        if p['resolved_at']:
            try:
                resolved = datetime.fromisoformat(p['resolved_at'].replace('Z', '+00:00'))
                antiguedad_dias = (ahora - resolved).days
            except:
                pass
        
        info = {
            'id': porra_id,
            'titulo': titulo,
            'estado': estado,
            'total_apuestas': total_apuestas,
            'apuestas_pendientes': apuestas_pendientes,
            'antiguedad_dias': antiguedad_dias
        }
        
        # Categorizar
        if estado in ('abierta', 'cerrada'):
            activas.append(info)
        elif estado == 'cancelada':
            canceladas.append(info)
        elif estado == 'finalizada':
            if antiguedad_dias and antiguedad_dias > dias_antiguedad:
                finalizadas_antiguas.append(info)
            else:
                finalizadas_recientes.append(info)
        
        if total_apuestas == 0:
            sin_apuestas.append(info)
    
    # Show summary
    print("\n📋 RESUMEN DE PORRAS:\n")
    
    print(f"✅ Activas (abiertas/cerradas): {len(activas)}")
    for p in activas:
        print(f"   - Porra {p['id']}: {p['titulo']} [{p['estado']}] - {p['total_apuestas']} apuestas")
    
    print(f"\n🏁 Finalizadas recientes (< {dias_antiguedad} días): {len(finalizadas_recientes)}")
    for p in finalizadas_recientes:
        dias = f"{p['antiguedad_dias']} días" if p['antiguedad_dias'] else "?"
        print(f"   - Porra {p['id']}: {p['titulo']} - {p['total_apuestas']} apuestas - {dias}")
    
    print(f"\n📦 Finalizadas antiguas (> {dias_antiguedad} días): {len(finalizadas_antiguas)}")
    for p in finalizadas_antiguas:
        dias = f"{p['antiguedad_dias']} días" if p['antiguedad_dias'] else "?"
        print(f"   - Porra {p['id']}: {p['titulo']} - {p['total_apuestas']} apuestas - {dias}")
    
    print(f"\n❌ Canceladas: {len(canceladas)}")
    for p in canceladas:
        print(f"   - Porra {p['id']}: {p['titulo']} - {p['total_apuestas']} apuestas")
    
    print(f"\n🚫 Sin apuestas: {len(sin_apuestas)}")
    for p in sin_apuestas:
        print(f"   - Porra {p['id']}: {p['titulo']} [{p['estado']}]")
    
    print("\n" + "="*80)
    
    # Determine which porras to delete
    porras_a_borrar = []
    
    # Criterio 1: Finalizadas antiguas (todas las apuestas ya pagadas)
    for p in finalizadas_antiguas:
        if p['apuestas_pendientes'] == 0:
            porras_a_borrar.append(p)
    
    # Criterio 2: Canceladas (todas las apuestas ya devueltas)
    for p in canceladas:
        if p['apuestas_pendientes'] == 0:
            porras_a_borrar.append(p)
    
    # Criterio 3: Sin apuestas y no activas
    for p in sin_apuestas:
        if p['estado'] not in ('abierta', 'cerrada'):
            if p not in porras_a_borrar:
                porras_a_borrar.append(p)
    
    if not porras_a_borrar:
        print("\n✅ No hay porras que cumplan los criterios para ser borradas")
        print("\nCriterios:")
        print(f"  - Finalizadas hace más de {dias_antiguedad} días (con todas las apuestas pagadas)")
        print("  - Canceladas (con todas las apuestas devueltas)")
        print("  - Sin apuestas y no activas")
        conn.close()
        return
    
    print(f"\n🗑️  PORRAS QUE SE PUEDEN BORRAR: {len(porras_a_borrar)}\n")
    for p in porras_a_borrar:
        dias = f" - {p['antiguedad_dias']} días" if p['antiguedad_dias'] else ""
        print(f"   - Porra {p['id']}: {p['titulo']} [{p['estado']}]{dias}")
    
    print("\n" + "="*80)
    
    # Ask for confirmation
    respuesta = input("\n¿Deseas borrar estas porras? (escribe 'SI' para confirmar): ")
    
    if respuesta.strip().upper() != 'SI':
        print("\n❌ Operación cancelada por el usuario")
        conn.close()
        return
    
    print("\n🗑️  Borrando porras...\n")
    
    borradas = 0
    errores = 0
    
    for p in porras_a_borrar:
        porra_id = p['id']
        titulo = p['titulo']
        
        try:
            # Delete apuestas first
            conn.execute("DELETE FROM apuestas_usuarios WHERE porra_id = ?", (porra_id,))
            
            # Delete porra
            conn.execute("DELETE FROM porras WHERE id = ?", (porra_id,))
            
            conn.commit()
            
            # Delete HTML files
            archivos_borrados = 0
            
            # Delete porra_ID.html
            html_path_id = os.path.join(PORRAS_DIR, f"porra_{porra_id}.html")
            if os.path.exists(html_path_id):
                os.remove(html_path_id)
                archivos_borrados += 1
            
            # Delete porra (Titulo).html (try to find it)
            for filename in os.listdir(PORRAS_DIR):
                if filename.startswith(f"porra (") and filename.endswith(").html"):
                    # Check if it's the same porra by reading the file
                    filepath = os.path.join(PORRAS_DIR, filename)
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            content = f.read()
                            if f"const PORRA_ID={porra_id};" in content:
                                os.remove(filepath)
                                archivos_borrados += 1
                                break
                    except:
                        pass
            
            print(f"✅ Porra {porra_id}: {titulo} - Borrada ({archivos_borrados} archivos HTML)")
            borradas += 1
            
        except Exception as e:
            print(f"❌ Porra {porra_id}: Error al borrar - {e}")
            errores += 1
    
    conn.close()
    
    print("\n" + "="*80)
    print(f"\n📊 RESUMEN FINAL:")
    print(f"   ✅ Porras borradas: {borradas}")
    print(f"   ❌ Errores: {errores}")
    print("="*80)
    
    if borradas > 0:
        print("\n✅ Limpieza completada exitosamente")
    else:
        print("\n⚠️  No se borraron porras")

if __name__ == "__main__":
    main()
