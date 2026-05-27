#!/usr/bin/env python3
"""Script para actualizar el archivo de configuración de ngrok"""
import os
from pathlib import Path

# Ruta al archivo de configuración de ngrok
ngrok_config_path = Path(os.environ.get("USERPROFILE", "")) / "AppData" / "Local" / "ngrok" / "ngrok.yml"

# Contenido correcto
content = """authtoken: 3DiuvphN44RTtzn0RiCj6WJa7dD_6bTjNzcsM6sTY38oP3QmU
version: "2"
tunnels:
    dvdcoin:
        proto: http
        addr: 8000
        domain: premium-size-unreached.ngrok-free.dev
"""

try:
    ngrok_config_path.write_text(content, encoding="utf-8")
    print(f"✓ Archivo actualizado: {ngrok_config_path}")
    print(f"✓ Dominio configurado: premium-size-unreached.ngrok-free.dev")
except Exception as e:
    print(f"✗ Error: {e}")
