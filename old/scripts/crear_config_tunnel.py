#!/usr/bin/env python3
"""
Crea el archivo de configuración del túnel de Cloudflare
"""

import os
import sys
import json
from pathlib import Path
import glob

DOMAIN = "dvta.ch"

def print_header(title):
    print()
    print("═" * 70)
    print(f"  {title}")
    print("═" * 70)
    print()

def find_tunnel_credentials():
    """Busca el archivo de credenciales del túnel."""
    
    # Buscar en el directorio .cloudflared del usuario
    cloudflared_dir = Path.home() / ".cloudflared"
    
    if cloudflared_dir.exists():
        # Buscar archivos .json (credenciales de túneles)
        json_files = list(cloudflared_dir.glob("*.json"))
        
        # Filtrar cert.pem y buscar solo UUIDs
        tunnel_files = [f for f in json_files if f.name != "cert.pem" and len(f.stem) > 30]
        
        if tunnel_files:
            # Tomar el más reciente
            tunnel_file = max(tunnel_files, key=lambda f: f.stat().st_mtime)
            tunnel_id = tunnel_file.stem
            
            print(f"✅ Encontrado túnel: {tunnel_id}")
            print(f"   Archivo: {tunnel_file}")
            
            return tunnel_id, str(tunnel_file)
    
    print("❌ No se encontró el archivo de credenciales del túnel")
    print()
    print("Asegúrate de haber ejecutado:")
    print("   cloudflared tunnel create dvta-tunnel")
    print()
    return None, None

def create_config_file(tunnel_id, credentials_file):
    """Crea el archivo de configuración del túnel."""
    
    config_path = Path("cloudflare-tunnel-dvta.yml")
    
    # Convertir ruta de Windows a formato compatible
    credentials_file_formatted = credentials_file.replace("\\", "/")
    
    config_content = f"""# Configuración de Cloudflare Tunnel para {DOMAIN}
tunnel: {tunnel_id}
credentials-file: {credentials_file_formatted}

ingress:
  # Dominio principal: {DOMAIN}
  - hostname: {DOMAIN}
    service: http://127.0.0.1:8000
    originRequest:
      noTLSVerify: true
      connectTimeout: 60s
      tlsTimeout: 20s
      tcpKeepAlive: 60s
      keepAliveConnections: 1024
      keepAliveTimeout: 120s
      httpHostHeader: {DOMAIN}
      disableChunkedEncoding: false
      proxyType: http
  
  # Subdominio www
  - hostname: www.{DOMAIN}
    service: http://127.0.0.1:8000
    originRequest:
      noTLSVerify: true
      connectTimeout: 60s
      tlsTimeout: 20s
      tcpKeepAlive: 60s
      keepAliveConnections: 1024
      keepAliveTimeout: 120s
      httpHostHeader: www.{DOMAIN}
      disableChunkedEncoding: false
      proxyType: http
  
  # Catch-all para cualquier otro tráfico
  - service: http_status:404

# Métricas y configuración avanzada
metrics: 127.0.0.1:2000
loglevel: info
protocol: quic
retries: 5
grace-period: 30s
no-autoupdate: false
"""
    
    try:
        with open(config_path, "w", encoding="utf-8") as f:
            f.write(config_content)
        
        print(f"✅ Archivo de configuración creado: {config_path}")
        print()
        
        # Guardar información del túnel
        tunnel_info = {
            "tunnel_id": tunnel_id,
            "domain": DOMAIN,
            "config_file": str(config_path),
            "credentials_file": credentials_file,
            "created_date": "2026-05-27"
        }
        
        with open("tunnel_info.json", "w") as f:
            json.dump(tunnel_info, f, indent=2)
        
        print("✅ Información guardada en: tunnel_info.json")
        
        return True
    
    except Exception as e:
        print(f"❌ Error al crear archivo de configuración: {e}")
        return False

def main():
    print_header(f"📝 CREAR CONFIGURACIÓN DEL TÚNEL PARA {DOMAIN}")
    
    # Buscar credenciales del túnel
    tunnel_id, credentials_file = find_tunnel_credentials()
    
    if not tunnel_id or not credentials_file:
        return 1
    
    # Crear archivo de configuración
    if not create_config_file(tunnel_id, credentials_file):
        return 1
    
    print_header("✅ CONFIGURACIÓN COMPLETADA")
    
    print(f"Túnel ID: {tunnel_id}")
    print(f"Dominio: https://{DOMAIN}")
    print(f"Configuración: cloudflare-tunnel-dvta.yml")
    print()
    print("🎯 SIGUIENTE PASO: Iniciar el túnel")
    print()
    print("Para iniciar el túnel, ejecuta:")
    print("   INICIAR_TUNNEL_DVTA.bat")
    print()
    print("O manualmente:")
    print("   cloudflared tunnel --config cloudflare-tunnel-dvta.yml run")
    print()
    
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n❌ Cancelado por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Error inesperado: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
