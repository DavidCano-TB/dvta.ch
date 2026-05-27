#!/usr/bin/env python3
"""
Script DESHABILITADO - La URL de ngrok se configura MANUALMENTE en config/ngrok_config.txt
Este script ya no actualiza automáticamente la configuración.
Para cambiar la URL, edita manualmente: config/ngrok_config.txt
"""

import urllib.request
import json
import re
from pathlib import Path
import time
import sys

def obtener_url_ngrok():
    """Obtiene la URL pública actual de ngrok desde su API"""
    try:
        response = urllib.request.urlopen("http://localhost:4040/api/tunnels", timeout=5)
        data = json.loads(response.read())
        
        tunnels = data.get("tunnels", [])
        for tunnel in tunnels:
            public_url = tunnel.get("public_url", "")
            if public_url.startswith("https://"):
                # Extraer solo el dominio sin el https://
                domain = public_url.replace("https://", "")
                return domain
        
        return None
    except Exception as e:
        if "--verbose" in sys.argv:
            print(f"❌ Error al obtener URL de ngrok: {e}")
        return None

def actualizar_config(nuevo_dominio):
    """Actualiza el archivo config/ngrok_config.txt con el nuevo dominio"""
    config_path = Path(__file__).parent / "config" / "ngrok_config.txt"
    
    if not config_path.exists():
        if "--verbose" in sys.argv:
            print(f"❌ No se encontró el archivo: {config_path}")
        return False
    
    try:
        # Leer el contenido actual
        contenido = config_path.read_text(encoding='utf-8')
        
        # Buscar y reemplazar la línea NGROK_DOMAIN
        nuevo_contenido = re.sub(
            r'NGROK_DOMAIN=.*',
            f'NGROK_DOMAIN={nuevo_dominio}',
            contenido
        )
        
        # Guardar el archivo actualizado
        config_path.write_text(nuevo_contenido, encoding='utf-8')
        if "--verbose" in sys.argv:
            print(f"✅ Archivo actualizado correctamente")
            print(f"   Nuevo dominio: {nuevo_dominio}")
        return True
        
    except Exception as e:
        if "--verbose" in sys.argv:
            print(f"❌ Error al actualizar el archivo: {e}")
        return False

def main():
    print("=" * 60)
    print("  SCRIPT DESHABILITADO")
    print("=" * 60)
    print()
    print("⚠️  Este script ya no actualiza automáticamente la URL de ngrok")
    print()
    print("La URL de ngrok se configura MANUALMENTE en:")
    print("  config/ngrok_config.txt")
    print()
    print("Para cambiar la URL:")
    print("  1. Abre: config/ngrok_config.txt")
    print("  2. Edita la línea: NGROK_DOMAIN=tu-dominio.ngrok-free.dev")
    print("  3. Guarda el archivo")
    print("  4. Reinicia el servidor")
    print()
    print("=" * 60)
    return 0

if __name__ == "__main__":
    exit(main())
