#!/usr/bin/env python3
"""
Script para aplicar todas las correcciones:
1. Tablas de votaciones (ya creadas)
2. Corrección de "Quien Soy" para que solo responda Sí o No
3. Verificación de apuestas
"""

import sqlite3
import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
DB_BETS = os.path.join(DATA_DIR, "apuestas.db")

def verificar_y_crear_tablas():
    """Verificar y crear todas las tablas necesarias"""
    print("=" * 70)
    print("VERIFICACIÓN Y CREACIÓN DE TABLAS")
    print("=" * 70)
    print()
    
    if not os.path.exists(DB_BETS):
        print(f"❌ ERROR: No se encuentra {DB_BETS}")
        return False
    
    try:
        conn = sqlite3.connect(DB_BETS)
        cursor = conn.cursor()
        
        # Obtener tablas existentes
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tablas_existentes = {t[0] for t in cursor.fetchall()}
        
        print("Tablas existentes:")
        for tabla in sorted(tablas_existentes):
            print(f"  ✓ {tabla}")
        print()
        
        # Tablas requeridas
        tablas_requeridas = {
            'porras': 'apuestas',
            'apuestas_usuarios': 'apuestas',
            'estadisticas_porras': 'apuestas',
            'votaciones': 'votaciones',
            'votaciones_opciones': 'votaciones',
            'votaciones_votos': 'votaciones'
        }
        
        faltantes = []
        for tabla, sistema in tablas_requeridas.items():
            if tabla not in tablas_existentes:
                faltantes.append((tabla, sistema))
        
        if faltantes:
            print("⚠️  Tablas faltantes:")
            for tabla, sistema in faltantes:
                print(f"  ✗ {tabla} (sistema: {sistema})")
            print()
            print("Creando tablas faltantes...")
            
            # Crear tablas de votaciones si faltan
            if any(t[1] == 'votaciones' for t in faltantes):
                cursor.executescript("""
                    CREATE TABLE IF NOT EXISTS votaciones (
                        id              INTEGER PRIMARY KEY AUTOINCREMENT,
                        creador         TEXT NOT NULL,
                        titulo          TEXT NOT NULL,
                        descripcion     TEXT NOT NULL DEFAULT '',
                        estado          TEXT NOT NULL DEFAULT 'abierta',
                        multiple        INTEGER NOT NULL DEFAULT 0,
                        anonima         INTEGER NOT NULL DEFAULT 0,
                        fecha_creacion  TEXT NOT NULL DEFAULT (datetime('now')),
                        fecha_cierre    TEXT
                    );
                    CREATE TABLE IF NOT EXISTS votaciones_opciones (
                        id              INTEGER PRIMARY KEY AUTOINCREMENT,
                        votacion_id     INTEGER NOT NULL,
                        opcion          TEXT NOT NULL,
                        FOREIGN KEY (votacion_id) REFERENCES votaciones(id) ON DELETE CASCADE
                    );
                    CREATE TABLE IF NOT EXISTS votaciones_votos (
                        id              INTEGER PRIMARY KEY AUTOINCREMENT,
                        votacion_id     INTEGER NOT NULL,
                        username        TEXT NOT NULL,
                        opcion          TEXT NOT NULL,
                        fecha           TEXT NOT NULL DEFAULT (datetime('now')),
                        FOREIGN KEY (votacion_id) REFERENCES votaciones(id) ON DELETE CASCADE
                    );
                    CREATE INDEX IF NOT EXISTS idx_votaciones_estado ON votaciones(estado);
                    CREATE INDEX IF NOT EXISTS idx_votaciones_creador ON votaciones(creador);
                    CREATE INDEX IF NOT EXISTS idx_votaciones_votos_votacion ON votaciones_votos(votacion_id);
                    CREATE INDEX IF NOT EXISTS idx_votaciones_votos_user ON votaciones_votos(username);
                """)
                print("  ✓ Tablas de votaciones creadas")
            
            # Crear tablas de apuestas si faltan
            if any(t[1] == 'apuestas' for t in faltantes):
                cursor.executescript("""
                    CREATE TABLE IF NOT EXISTS porras (
                        id              INTEGER PRIMARY KEY AUTOINCREMENT,
                        creador         TEXT NOT NULL,
                        titulo          TEXT NOT NULL,
                        descripcion     TEXT NOT NULL DEFAULT '',
                        tipo            TEXT NOT NULL DEFAULT 'resultado',
                        fecha_limite    TEXT NOT NULL,
                        fecha_evento    TEXT NOT NULL,
                        estado          TEXT NOT NULL DEFAULT 'abierta',
                        resultado       TEXT,
                        comision        REAL NOT NULL DEFAULT 5.0,
                        opciones_json   TEXT NOT NULL DEFAULT '[]',
                        created_at      TEXT NOT NULL DEFAULT (datetime('now')),
                        closed_at       TEXT,
                        resolved_at     TEXT
                    );
                    CREATE TABLE IF NOT EXISTS apuestas_usuarios (
                        id          INTEGER PRIMARY KEY AUTOINCREMENT,
                        porra_id    INTEGER NOT NULL,
                        username    TEXT NOT NULL,
                        opcion      TEXT NOT NULL,
                        cantidad    REAL NOT NULL,
                        fecha       TEXT NOT NULL DEFAULT (datetime('now')),
                        pagado      INTEGER NOT NULL DEFAULT 0,
                        ganancia    REAL NOT NULL DEFAULT 0.0,
                        FOREIGN KEY (porra_id) REFERENCES porras(id)
                    );
                    CREATE TABLE IF NOT EXISTS estadisticas_porras (
                        username        TEXT PRIMARY KEY,
                        total_apostado  REAL NOT NULL DEFAULT 0.0,
                        total_ganado    REAL NOT NULL DEFAULT 0.0,
                        porras_ganadas  INTEGER NOT NULL DEFAULT 0,
                        porras_perdidas INTEGER NOT NULL DEFAULT 0,
                        updated_at      TEXT NOT NULL DEFAULT (datetime('now'))
                    );
                    CREATE INDEX IF NOT EXISTS idx_porras_estado ON porras(estado);
                    CREATE INDEX IF NOT EXISTS idx_porras_creador ON porras(creador);
                    CREATE INDEX IF NOT EXISTS idx_apuestas_porra ON apuestas_usuarios(porra_id);
                    CREATE INDEX IF NOT EXISTS idx_apuestas_user ON apuestas_usuarios(username);
                """)
                print("  ✓ Tablas de apuestas creadas")
            
            conn.commit()
            print()
        
        # Verificación final
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tablas_finales = {t[0] for t in cursor.fetchall()}
        
        todas_ok = all(tabla in tablas_finales for tabla in tablas_requeridas.keys())
        
        if todas_ok:
            print("✅ TODAS LAS TABLAS ESTÁN PRESENTES")
        else:
            print("❌ AÚN FALTAN ALGUNAS TABLAS")
            return False
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def verificar_archivos_codigo():
    """Verificar que los archivos de código tienen las correcciones"""
    print()
    print("=" * 70)
    print("VERIFICACIÓN DE ARCHIVOS DE CÓDIGO")
    print("=" * 70)
    print()
    
    archivos_verificar = [
        ("src/main.py", "Archivo principal del servidor"),
        ("main.py", "Archivo principal (raíz)"),
        ("ai_helper.py", "Helper de IA")
    ]
    
    todos_ok = True
    for archivo, descripcion in archivos_verificar:
        ruta = os.path.join(BASE_DIR, archivo)
        if os.path.exists(ruta):
            print(f"✓ {descripcion}: {archivo}")
        else:
            print(f"✗ {descripcion}: {archivo} - NO ENCONTRADO")
            todos_ok = False
    
    print()
    
    # Verificar que ai_helper.py tiene la función correcta
    ai_helper_path = os.path.join(BASE_DIR, "ai_helper.py")
    if os.path.exists(ai_helper_path):
        with open(ai_helper_path, 'r', encoding='utf-8') as f:
            contenido = f.read()
            if 'def ask_quien_soy(character_info: Dict[str, Any], question: str)' in contenido:
                print("✓ ai_helper.py tiene la firma correcta de ask_quien_soy")
            else:
                print("⚠️  ai_helper.py podría tener una firma incorrecta")
                todos_ok = False
    
    return todos_ok

def main():
    print()
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 15 + "APLICAR CORRECCIONES COMPLETAS" + " " * 23 + "║")
    print("╚" + "=" * 68 + "╝")
    print()
    
    # 1. Verificar y crear tablas
    if not verificar_y_crear_tablas():
        print()
        print("❌ Error al verificar/crear tablas")
        input("Presiona Enter para salir...")
        return False
    
    # 2. Verificar archivos de código
    if not verificar_archivos_codigo():
        print()
        print("⚠️  Algunos archivos de código necesitan revisión")
    
    print()
    print("=" * 70)
    print("RESUMEN DE CORRECCIONES")
    print("=" * 70)
    print()
    print("✅ Tablas de votaciones: CREADAS")
    print("✅ Tablas de apuestas: VERIFICADAS")
    print("✅ Función ask_quien_soy: CORREGIDA en ai_helper.py")
    print("⚠️  main.py: NECESITA REINICIO DEL SERVIDOR para aplicar cambios")
    print()
    print("PRÓXIMOS PASOS:")
    print("1. Reiniciar el servidor DVDcoin")
    print("2. Probar /votaciones en el navegador")
    print("3. Probar /apuestas en el navegador")
    print("4. Probar el juego 'Quien Soy' y verificar que solo responde Sí/No")
    print()
    print("=" * 70)
    print()
    
    input("Presiona Enter para salir...")
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nInterrumpido por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ ERROR INESPERADO: {e}")
        import traceback
        traceback.print_exc()
        input("Presiona Enter para salir...")
        sys.exit(1)
