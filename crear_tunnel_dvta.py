#!/usr/bin/env python3
"""
Crea un túnel de Cloudflare para dvta.ch y configura el DNS automáticamente
"""

import os
import sys
import json
import subprocess
import requests
from pathlib import Path

DOMAIN = "dvta.ch"
ZONE_ID = "a0353c3d6ad85c54e8ed8f31237538b9"
ACCOUNT_ID = "bc719d01fe06039b0823aab050e9150a"

def print_header(title):
    print()
    print("═" * 70)
    print(f"  {title}")
    print("═" * 70)
    print()

def check_cloudflared():
    """Verifica si cloudflared está instalado."""
    try:
        result = subprocess.run(["cloudflared", "--version"], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print(f"✅ cloudflared instalado: {result.stdout.strip()}")
            return True
    except:
        pass
    
    print("❌ cloudflared no está instalado")
    print()
    print("Para instalarlo:")
    print("1. Ve a: https://github.com/cloudflare/cloudflared/releases")
    print("2. Descarga: cloudflared-windows-amd64.exe")
    print("3. Renómbralo a: cloudflared.exe")
    print("4. Muévelo a: C:\\Windows\\System32\\")
    print()
    return False

def login_cloudflared():
    """Inicia sesión en Cloudflare con cloudflared."""
    print("Iniciando sesión en Cloudflare...")
    print("Se abrirá tu navegador para autorizar el acceso.")
    print()
    
    try:
        result = subprocess.run(["cloudflared", "tunnel", "login"], 
                              timeout=120)
        if result.returncode == 0:
            print("✅ Sesión iniciada correctamente")
            return True
        else:
            print("❌ Error al iniciar sesión")
            return False
    except subprocess.TimeoutExpired:
        print("⏱️  Tiempo de espera agotado. ¿Autorizaste en el navegador?")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def create_tunnel(tunnel_name):
    """Crea un nuevo túnel de Cloudflare."""
    print(f"Creando túnel: {tunnel_name}...")
    
    try:
        result = subprocess.run(
            ["cloudflared", "tunnel", "create", tunnel_name],
            capture_output=True, text=True, timeout=30
        )
        
        if result.returncode == 0:
            print(f"✅ Túnel '{tunnel_name}' creado correctamente")
            print()
            print(result.stdout)
            
            # Extraer el UUID del túnel
            for line in result.stdout.split('\n'):
                if 'Created tunnel' in line and 'with id' in line:
                    # Formato: "Created tunnel dvta-tunnel with id abc-123-def"
                    parts = line.split('with id')
                    if len(parts) > 1:
                        tunnel_id = parts[1].strip()
                        return tunnel_id
            
            return None
        else:
            if "already exists" in result.stderr.lower():
                print(f"ℹ️  El túnel '{tunnel_name}' ya existe")
                # Intentar obtener el ID del túnel existente
                return get_existing_tunnel_id(tunnel_name)
            else:
                print(f"❌ Error al crear túnel: {result.stderr}")
                return None
    
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def get_existing_tunnel_id(tunnel_name):
    """Obtiene el ID de un túnel existente."""
    try:
        result = subprocess.run(
            ["cloudflared", "tunnel", "list"],
            capture_output=True, text=True, timeout=30
        )
        
        if result.returncode == 0:
            for line in result.stdout.split('\n'):
                if tunnel_name in line:
                    # Extraer el UUID (primer campo)
                    parts = line.split()
                    if len(parts) > 0:
                        return parts[0]
        
        return None
    except:
        return None

def create_config_file(tunnel_id, tunnel_name):
    """Crea el archivo de configuración del túnel."""
    config_path = Path("cloudflare-tunnel-dvta.yml")
    
    # Buscar el archivo de credenciales
    cloudflared_dir = Path.home() / ".cloudflared"
    credentials_file = cloudflared_dir / f"{tunnel_id}.json"
    
    if not credentials_file.exists():
        print(f"⚠️  No se encontró el archivo de credenciales: {credentials_file}")
        print("Buscando en ubicaciones alternativas...")
        
        # Buscar en el directorio actual
        alt_credentials = Path(f"{tunnel_id}.json")
        if alt_credentials.exists():
            credentials_file = alt_credentials
            print(f"✅ Encontrado en: {credentials_file}")
        else:
            print("❌ No se pudo encontrar el archivo de credenciales")
            return False
    
    config_content = f"""# Configuración de Cloudflare Tunnel para {DOMAIN}
tunnel: {tunnel_id}
credentials-file: {str(credentials_file).replace(chr(92), '/')}

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
        return True
    
    except Exception as e:
        print(f"❌ Error al crear archivo de configuración: {e}")
        return False

def route_tunnel(tunnel_id, tunnel_name):
    """Configura las rutas DNS para el túnel."""
    print(f"Configurando rutas DNS para {DOMAIN}...")
    
    # Ruta para el dominio principal
    try:
        result = subprocess.run(
            ["cloudflared", "tunnel", "route", "dns", tunnel_name, DOMAIN],
            capture_output=True, text=True, timeout=30
        )
        
        if result.returncode == 0 or "already exists" in result.stderr.lower():
            print(f"✅ Ruta DNS configurada: {DOMAIN}")
        else:
            print(f"⚠️  Advertencia al configurar {DOMAIN}: {result.stderr}")
    
    except Exception as e:
        print(f"⚠️  Error al configurar ruta para {DOMAIN}: {e}")
    
    # Ruta para www
    try:
        result = subprocess.run(
            ["cloudflared", "tunnel", "route", "dns", tunnel_name, f"www.{DOMAIN}"],
            capture_output=True, text=True, timeout=30
        )
        
        if result.returncode == 0 or "already exists" in result.stderr.lower():
            print(f"✅ Ruta DNS configurada: www.{DOMAIN}")
        else:
            print(f"⚠️  Advertencia al configurar www.{DOMAIN}: {result.stderr}")
    
    except Exception as e:
        print(f"⚠️  Error al configurar ruta para www.{DOMAIN}: {e}")
    
    return True

def main():
    print_header(f"🚀 CREAR TÚNEL DE CLOUDFLARE PARA {DOMAIN}")
    
    # Verificar cloudflared
    if not check_cloudflared():
        return 1
    
    print()
    print("━" * 70)
    print("PASO 1: Iniciar sesión en Cloudflare")
    print("━" * 70)
    
    if not login_cloudflared():
        print("❌ No se pudo iniciar sesión")
        return 1
    
    print()
    print("━" * 70)
    print("PASO 2: Crear túnel")
    print("━" * 70)
    
    tunnel_name = "dvta-tunnel"
    tunnel_id = create_tunnel(tunnel_name)
    
    if not tunnel_id:
        print("❌ No se pudo crear el túnel")
        return 1
    
    print(f"✅ Túnel ID: {tunnel_id}")
    
    print()
    print("━" * 70)
    print("PASO 3: Crear archivo de configuración")
    print("━" * 70)
    
    if not create_config_file(tunnel_id, tunnel_name):
        print("❌ No se pudo crear el archivo de configuración")
        return 1
    
    print()
    print("━" * 70)
    print("PASO 4: Configurar rutas DNS")
    print("━" * 70)
    
    if not route_tunnel(tunnel_id, tunnel_name):
        print("❌ No se pudieron configurar las rutas DNS")
        return 1
    
    print_header("✅ TÚNEL CREADO Y CONFIGURADO CORRECTAMENTE")
    
    print(f"Túnel: {tunnel_name}")
    print(f"ID: {tunnel_id}")
    print(f"Dominio: https://{DOMAIN}")
    print(f"Configuración: cloudflare-tunnel-dvta.yml")
    print()
    print("🎯 SIGUIENTE PASO: Iniciar el túnel")
    print()
    print("Para iniciar el túnel, ejecuta:")
    print(f"   cloudflared tunnel --config cloudflare-tunnel-dvta.yml run {tunnel_name}")
    print()
    print("O usa el script: INICIAR_TUNNEL_DVTA.bat")
    print()
    
    # Guardar información del túnel
    tunnel_info = {
        "tunnel_name": tunnel_name,
        "tunnel_id": tunnel_id,
        "domain": DOMAIN,
        "config_file": "cloudflare-tunnel-dvta.yml",
        "created_date": "2026-05-27"
    }
    
    with open("tunnel_info.json", "w") as f:
        json.dump(tunnel_info, f, indent=2)
    
    print("ℹ️  Información del túnel guardada en: tunnel_info.json")
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
