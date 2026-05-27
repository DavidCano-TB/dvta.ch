#!/usr/bin/env python3
"""
Script para añadir el panel de estadísticas de DVD a todas las páginas de porras.
"""

import os
import re

# Directorio de porras
PORRAS_DIR = "game_pages/apuestas/porras"

# Código del panel de DVD para insertar (después de <div id="resultPanel">)
DVD_PANEL_HTML = '''
  <!-- Panel de Estadísticas Completas - SOLO DVD -->
  <div id="dvdStatsPanel" style="display:none;"></div>
'''

# Código JavaScript del panel de DVD (para insertar antes de "// Update options stats")
DVD_PANEL_JS = '''    // Panel de Estadísticas Completas - SOLO DVD
    if(isDvd && apuestas.length > 0){
      let dvdHtml = `
        <div class="section" style="background:linear-gradient(135deg,var(--n2),var(--n3));border:3px solid var(--gold);box-shadow:0 0 30px rgba(212,168,67,.3);">
          <div style="text-align:center;margin-bottom:24px;">
            <div style="font-family:'Playfair Display',serif;font-size:2rem;color:var(--gold2);margin-bottom:8px;">
              👑 PANEL DE CONTROL DVD
            </div>
            <div style="font-size:.8rem;color:var(--text3);letter-spacing:.1em;">
              ESTADÍSTICAS COMPLETAS Y MOVIMIENTOS DE LA PORRA
            </div>
          </div>
          
          <!-- SECCIÓN 1: RESUMEN FINANCIERO -->
          <div style="background:var(--n4);border:2px solid var(--gold);border-radius:10px;padding:20px;margin-bottom:20px;">
            <div style="font-size:1.1rem;color:var(--gold2);font-weight:700;margin-bottom:16px;display:flex;align-items:center;gap:8px;">
              <span>💰</span> RESUMEN FINANCIERO
            </div>
            <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px;">
              <div style="background:var(--n3);border:1px solid var(--gold);border-radius:8px;padding:16px;text-align:center;">
                <div style="font-size:2rem;color:var(--gold2);font-weight:700;">${stats.total_bote.toFixed(1)}</div>
                <div style="font-size:.7rem;color:var(--text3);margin-top:4px;">BOTE TOTAL</div>
              </div>
              <div style="background:var(--n3);border:1px solid var(--orange);border-radius:8px;padding:16px;text-align:center;">
                <div style="font-size:2rem;color:var(--orange);font-weight:700;">${(stats.total_bote * p.comision).toFixed(1)}</div>
                <div style="font-size:.7rem;color:var(--text3);margin-top:4px;">COMISIÓN (${(p.comision*100).toFixed(0)}%)</div>
              </div>
              <div style="background:var(--n3);border:1px solid var(--green);border-radius:8px;padding:16px;text-align:center;">
                <div style="font-size:2rem;color:var(--green);font-weight:700;">${(stats.total_bote * (1-p.comision)).toFixed(1)}</div>
                <div style="font-size:.7rem;color:var(--text3);margin-top:4px;">BOTE NETO</div>
              </div>
              <div style="background:var(--n3);border:1px solid var(--border);border-radius:8px;padding:16px;text-align:center;">
                <div style="font-size:2rem;color:var(--text);font-weight:700;">${apuestas.length}</div>
                <div style="font-size:.7rem;color:var(--text3);margin-top:4px;">TOTAL APUESTAS</div>
              </div>
              <div style="background:var(--n3);border:1px solid var(--blue);border-radius:8px;padding:16px;text-align:center;">
                <div style="font-size:2rem;color:var(--blue);font-weight:700;">${new Set(apuestas.map(a=>a.username)).size}</div>
                <div style="font-size:.7rem;color:var(--text3);margin-top:4px;">APOSTADORES</div>
              </div>
            </div>
          </div>
          
          <!-- SECCIÓN 2: DISTRIBUCIÓN POR OPCIÓN -->
          <div style="background:var(--n4);border:2px solid var(--blue);border-radius:10px;padding:20px;margin-bottom:20px;">
            <div style="font-size:1.1rem;color:var(--blue);font-weight:700;margin-bottom:16px;display:flex;align-items:center;gap:8px;">
              <span>📊</span> DISTRIBUCIÓN POR OPCIÓN
            </div>
      `;
      
      // Distribución detallada por opción
      Object.entries(stats.distribucion).forEach(([valor, d]) => {
        const optName = p.opciones.find(o => o.valor === valor)?.nombre || valor;
        const isWinner = p.estado === 'finalizada' && p.resultado === valor;
        const borderColor = isWinner ? 'var(--green)' : 'var(--border)';
        
        dvdHtml += `
          <div style="background:var(--n3);border:2px solid ${borderColor};border-radius:8px;padding:16px;margin-bottom:12px;${isWinner ? 'box-shadow:0 0 20px rgba(56,184,122,.3);' : ''}">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;">
              <div style="font-size:1rem;color:var(--gold2);font-weight:700;">
                ${isWinner ? '🏆 ' : ''}${e(optName)}
              </div>
              <div style="font-size:1.3rem;color:var(--gold2);font-weight:700;">
                ${d.total.toFixed(1)} DVDc
              </div>
            </div>
            <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(120px,1fr));gap:10px;">
              <div style="background:var(--glass);padding:8px;border-radius:6px;text-align:center;">
                <div style="font-size:.7rem;color:var(--text3);">Apostadores</div>
                <div style="font-size:1.1rem;color:var(--text);font-weight:600;">${d.count}</div>
              </div>
              <div style="background:var(--glass);padding:8px;border-radius:6px;text-align:center;">
                <div style="font-size:.7rem;color:var(--text3);">% del Bote</div>
                <div style="font-size:1.1rem;color:var(--gold2);font-weight:600;">${d.porcentaje.toFixed(1)}%</div>
              </div>
              <div style="background:var(--glass);padding:8px;border-radius:6px;text-align:center;">
                <div style="font-size:.7rem;color:var(--text3);">Cuota</div>
                <div style="font-size:1.1rem;color:var(--text);font-weight:600;">${d.cuota_implicita > 0 ? d.cuota_implicita.toFixed(2) + 'x' : '-'}</div>
              </div>
            </div>
          </div>
        `;
      });
      
      dvdHtml += `
          </div>
          
          <!-- SECCIÓN 3: REGISTRO DE MOVIMIENTOS (TODAS LAS APUESTAS) -->
          <div style="background:var(--n4);border:2px solid var(--red);border-radius:10px;padding:20px;margin-bottom:20px;">
            <div style="font-size:1.1rem;color:var(--red);font-weight:700;margin-bottom:16px;display:flex;align-items:center;justify-content:space-between;">
              <div style="display:flex;align-items:center;gap:8px;">
                <span>📋</span> REGISTRO DE MOVIMIENTOS
              </div>
              <div style="font-size:.75rem;color:var(--text3);font-weight:400;">
                ${apuestas.length} apuestas registradas
              </div>
            </div>
            <div style="background:var(--n3);border-radius:8px;padding:12px;margin-bottom:12px;">
              <div style="font-size:.75rem;color:var(--text3);text-align:center;">
                Todas las apuestas ordenadas cronológicamente (más recientes primero)
              </div>
            </div>
            <div style="max-height:600px;overflow-y:auto;padding-right:8px;">
      `;
      
      // Ordenar apuestas por fecha (más recientes primero)
      const sortedApuestas = [...apuestas].sort((a,b) => new Date(b.fecha) - new Date(a.fecha));
      
      sortedApuestas.forEach((a, index) => {
        const fecha = new Date(a.fecha).toLocaleString('es-ES', {
          year: 'numeric',
          month: '2-digit',
          day: '2-digit',
          hour: '2-digit',
          minute: '2-digit',
          second: '2-digit'
        });
        
        const optName = p.opciones.find(o => o.valor === a.opcion)?.nombre || a.opcion;
        const isWinner = p.estado === 'finalizada' && a.opcion === p.resultado;
        const statusColor = isWinner ? 'var(--green)' : (p.estado === 'finalizada' ? 'var(--red)' : 'var(--blue)');
        const statusIcon = isWinner ? '🏆' : (p.estado === 'finalizada' ? '❌' : '⏳');
        const statusText = isWinner ? 'GANADOR' : (p.estado === 'finalizada' ? 'PERDEDOR' : 'PENDIENTE');
        
        dvdHtml += `
          <div style="background:var(--n3);border-left:5px solid ${statusColor};border-radius:8px;padding:14px;margin-bottom:10px;transition:all .2s;" onmouseover="this.style.background='rgba(212,168,67,.08)'" onmouseout="this.style.background='var(--n3)'">
            <!-- Cabecera -->
            <div style="display:flex;justify-content:space-between;align-items:start;margin-bottom:10px;">
              <div>
                <div style="font-size:.95rem;color:var(--text);font-weight:700;margin-bottom:4px;">
                  ${statusIcon} @${e(a.username)}
                </div>
                <div style="font-size:.7rem;color:var(--text3);">
                  📅 ${fecha}
                </div>
              </div>
              <div style="text-align:right;">
                <div style="font-size:1.1rem;color:var(--gold2);font-weight:700;">
                  ${a.cantidad.toFixed(1)} DVDc
                </div>
                <div style="font-size:.7rem;color:${statusColor};font-weight:600;margin-top:2px;">
                  ${statusText}
                </div>
              </div>
            </div>
            
            <!-- Detalles de la Apuesta -->
            <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:8px;margin-bottom:10px;">
              <div style="background:var(--glass);padding:8px 12px;border-radius:6px;">
                <div style="font-size:.65rem;color:var(--text3);margin-bottom:3px;">OPCIÓN ELEGIDA</div>
                <div style="font-size:.8rem;color:var(--gold2);font-weight:600;">${e(optName)}</div>
              </div>
              <div style="background:var(--glass);padding:8px 12px;border-radius:6px;">
                <div style="font-size:.65rem;color:var(--text3);margin-bottom:3px;">CANTIDAD</div>
                <div style="font-size:.8rem;color:var(--text);font-weight:600;">${a.cantidad.toFixed(1)} DVDc</div>
              </div>
              ${a.pagado ? `
                <div style="background:${isWinner ? 'rgba(56,184,122,.15)' : 'rgba(200,48,96,.15)'};padding:8px 12px;border-radius:6px;border:1px solid ${isWinner ? 'rgba(56,184,122,.4)' : 'rgba(200,48,96,.4)'};">
                  <div style="font-size:.65rem;color:var(--text3);margin-bottom:3px;">GANANCIA</div>
                  <div style="font-size:.8rem;color:${statusColor};font-weight:700;">${a.ganancia.toFixed(1)} DVDc</div>
                </div>
                <div style="background:var(--glass);padding:8px 12px;border-radius:6px;">
                  <div style="font-size:.65rem;color:var(--text3);margin-bottom:3px;">BENEFICIO</div>
                  <div style="font-size:.8rem;color:${statusColor};font-weight:700;">
                    ${(a.ganancia - a.cantidad >= 0 ? '+' : '')}${(a.ganancia - a.cantidad).toFixed(1)} DVDc
                  </div>
                </div>
                <div style="background:var(--glass);padding:8px 12px;border-radius:6px;">
                  <div style="font-size:.65rem;color:var(--text3);margin-bottom:3px;">ROI</div>
                  <div style="font-size:.8rem;color:${statusColor};font-weight:700;">
                    ${(((a.ganancia - a.cantidad) / a.cantidad * 100).toFixed(1))}%
                  </div>
                </div>
              ` : `
                <div style="background:var(--glass);padding:8px 12px;border-radius:6px;">
                  <div style="font-size:.65rem;color:var(--text3);margin-bottom:3px;">ESTADO</div>
                  <div style="font-size:.8rem;color:var(--blue);font-weight:600;">En juego</div>
                </div>
              `}
            </div>
            
            <!-- Número de Movimiento -->
            <div style="text-align:right;font-size:.65rem;color:var(--text3);">
              Movimiento #${sortedApuestas.length - index}
            </div>
          </div>
        `;
      });
      
      dvdHtml += `
            </div>
          </div>
          
          <!-- SECCIÓN 4: ANÁLISIS POR USUARIO -->
          <div style="background:var(--n4);border:2px solid var(--orange);border-radius:10px;padding:20px;">
            <div style="font-size:1.1rem;color:var(--orange);font-weight:700;margin-bottom:16px;display:flex;align-items:center;gap:8px;">
              <span>👥</span> ANÁLISIS POR USUARIO
            </div>
            <div style="overflow-x:auto;">
              <table style="width:100%;border-collapse:collapse;">
                <thead>
                  <tr style="border-bottom:2px solid var(--border2);">
                    <th style="text-align:left;padding:12px;font-size:.75rem;color:var(--text3);background:var(--n3);">USUARIO</th>
                    <th style="text-align:center;padding:12px;font-size:.75rem;color:var(--text3);background:var(--n3);">APUESTAS</th>
                    <th style="text-align:right;padding:12px;font-size:.75rem;color:var(--text3);background:var(--n3);">TOTAL APOSTADO</th>
                    <th style="text-align:left;padding:12px;font-size:.75rem;color:var(--text3);background:var(--n3);">OPCIONES</th>
                  </tr>
                </thead>
                <tbody>
      `;
      
      // Agrupar apuestas por usuario
      const userStats = {};
      apuestas.forEach(a => {
        if(!userStats[a.username]){
          userStats[a.username] = {
            count: 0,
            total: 0,
            opciones: new Set()
          };
        }
        userStats[a.username].count++;
        userStats[a.username].total += a.cantidad;
        userStats[a.username].opciones.add(p.opciones.find(o => o.valor === a.opcion)?.nombre || a.opcion);
      });
      
      // Ordenar por total apostado
      const sortedUsers = Object.entries(userStats).sort((a,b) => b[1].total - a[1].total);
      
      sortedUsers.forEach(([username, stats], index) => {
        const bgColor = index % 2 === 0 ? 'var(--n3)' : 'transparent';
        dvdHtml += `
          <tr style="border-bottom:1px solid var(--border);background:${bgColor};">
            <td style="padding:12px;font-size:.85rem;color:var(--text);font-weight:700;">@${e(username)}</td>
            <td style="text-align:center;padding:12px;font-size:.8rem;color:var(--text2);">${stats.count}</td>
            <td style="text-align:right;padding:12px;font-size:.85rem;color:var(--gold2);font-weight:700;">${stats.total.toFixed(1)} DVDc</td>
            <td style="padding:12px;font-size:.75rem;color:var(--text3);">${Array.from(stats.opciones).join(', ')}</td>
          </tr>
        `;
      });
      
      dvdHtml += `
                </tbody>
              </table>
            </div>
          </div>
        </div>
      `;
      
      document.getElementById('dvdStatsPanel').innerHTML = dvdHtml;
      document.getElementById('dvdStatsPanel').style.display = '';
    } else {
      document.getElementById('dvdStatsPanel').style.display = 'none';
    }
    
'''

def actualizar_porra(filepath):
    """Actualiza una página de porra con el panel de DVD."""
    print(f"Procesando: {filepath}")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 1. Añadir el div del panel de DVD si no existe
    if '<div id="dvdStatsPanel"' not in content:
        # Buscar <div id="resultPanel" y añadir después
        content = content.replace(
            '<div id="resultPanel" style="display:none;"></div>',
            '<div id="resultPanel" style="display:none;"></div>\n' + DVD_PANEL_HTML
        )
        print(f"  ✓ Añadido div dvdStatsPanel")
    else:
        print(f"  - Ya tiene div dvdStatsPanel")
    
    # 2. Añadir el código JavaScript del panel si no existe
    if '// Panel de Estadísticas Completas - SOLO DVD' not in content or 'PANEL DE CONTROL DVD' not in content:
        # Buscar el marcador y añadir el código
        marker = "// Update options stats"
        if marker in content:
            content = content.replace(marker, DVD_PANEL_JS + marker)
            print(f"  ✓ Añadido código JavaScript del panel DVD")
        else:
            print(f"  ⚠ No se encontró el marcador para insertar JS")
    else:
        print(f"  - Ya tiene código JavaScript del panel DVD")
    
    # 3. Guardar el archivo
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"  ✅ Completado\n")

def main():
    """Procesa todas las páginas de porras."""
    print("=" * 70)
    print("ACTUALIZANDO TODAS LAS PÁGINAS DE PORRAS CON PANEL DVD")
    print("=" * 70)
    print()
    
    # Obtener todas las páginas de porras
    porras = [f for f in os.listdir(PORRAS_DIR) if f.startswith('porra_') and f.endswith('.html')]
    porras.sort()
    
    print(f"Encontradas {len(porras)} páginas de porras:\n")
    for porra in porras:
        print(f"  - {porra}")
    print()
    
    # Procesar cada porra
    for porra in porras:
        filepath = os.path.join(PORRAS_DIR, porra)
        actualizar_porra(filepath)
    
    print("=" * 70)
    print("✅ PROCESO COMPLETADO")
    print("=" * 70)
    print()
    print(f"Se han actualizado {len(porras)} páginas de porras.")
    print("Todas las porras ahora tienen el panel de estadísticas de DVD.")
    print()

if __name__ == "__main__":
    main()
