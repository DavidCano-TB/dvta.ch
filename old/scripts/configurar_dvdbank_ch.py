#!/usr/bin/env python3
"""
Configura dvdbank.ch automáticamente con Cloudflare Tunnel
"""

import os
import sys
import json
import requests
import subprocess
import time
from pathlib import Path

# Configuración
TOKEN_FILE = Path(__file__).parent / "config" / "cloudflare_token.txt"
TUNNEL_ID = "6c0cb6da-aafe-4e61-89aa-42d9bd2e5b33"
TUNNEL_CNAME = f"{TUNNEL_ID}.cfargotunnel.com"
DOMAIN = "dvdbank.ch"

def print_header(title):
    print()
    print("═" * 70)
    print(f"  {title}")
    print("═" * 70)
    print()

def load_token():
    """Carga el token de Cloudflare."""
    if not TOKEN_FILE.exists():
        print(f"❌ No se encontró el token en: {TOKEN_FILE}")
        return None
    
    token = TOKEN_FILE.read_text().strip()
    if not token:
        print("❌ El archivo de token está vacío")
        return None
    
    print(f"✅ Token cargado correctamente")
    return token

def get_zone_id(token, zone_name):
    """Obtiene el Zone ID de un dominio."""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    url = "https://api.cloudflare.com/client/v4/zones"
    params = {"name": zone_name}
    
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        
        if not data.get("success"):
            print(f"❌ Error de Cloudflare: {data.get('errors')}")
            return None
        
        if not data.get("result"):
            print(f"❌ No se encontró la zona: {zone_name}")
            print(f"⚠️  Asegúrate de haber añadido {zone_name} a Cloudflare")
            print(f"   Ve a: https://dash.cloudflare.com")
            print(f"   Clic en 'Add domain' y añade: {zone_name}")
            return None
        
        zone_id = data["result"][0]["id"]
        print(f"✅ Zone ID de {zone_name}: {zone_id}")
        return zone_id
    
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def list_dns_records(token, zone_id):
    """Lista todos los registros DNS de una zona."""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records"
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        if not data.get("success"):
            print(f"❌ Error: {data.get('errors')}")
            return []
        
        return data.get("result", [])
    
    except Exception as e:
        print(f"❌ Error: {e}")
        return []

def delete_dns_record(token, zone_id, record_id, name, record_type, content):
    """Elimina un registro DNS."""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records/{record_id}"
    
    try:
        response = requests.delete(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        if data.get("success"):
            print(f"   ✅ Eliminado: {name} ({record_type} → {content})")
            return True
        else:
            print(f"   ❌ Error al eliminar {name}: {data.get('errors')}")
            return False
    
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def create_dns_record(token, zone_id, record_type, name, content, proxied=True):
    """Crea un registro DNS."""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records"
    
    data = {
        "type": record_type,
        "name": name,
        "content": content,
        "proxied": proxied,
        "ttl": 1 if proxied else 3600
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        result = response.json()
        
        if result.get("success"):
            print(f"   ✅ Creado: {name} ({record_type} → {content})")
            return True
        else:
            errors = result.get('errors', [])
            # Si el error es que ya existe, no es un error crítico
            if any('already exists' in str(e).lower() for e in errors):
                print(f"   ℹ️  Ya existe: {name}")
                return True
            print(f"   ❌ Error al crear {name}: {errors}")
            return False
    
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def update_dns_record(token, zone_id, record_id, proxied=True):
    """Actualiza un registro DNS para activar proxy."""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records/{record_id}"
    
    data = {"proxied": proxied}
    
    try:
        response = requests.patch(url, headers=headers, json=data)
        response.raise_for_status()
        result = response.json()
        
        return result.get("success", False)
    
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def configure_ssl(token, zone_id, zone_name):
    """Configura SSL/TLS en modo Full."""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Configurar SSL/TLS en modo Full
    url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/settings/ssl"
    data = {"value": "full"}
    
    try:
        response = requests.patch(url, headers=headers, json=data)
        response.raise_for_status()
        result = response.json()
        
        if result.get("success"):
            print(f"   ✅ SSL/TLS configurado en modo Full")
        else:
            print(f"   ⚠️  No se pudo configurar SSL: {result.get('errors')}")
    except Exception as e:
        print(f"   ⚠️  Error al configurar SSL: {e}")
    
    # Activar Always Use HTTPS
    url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/settings/always_use_https"
    data = {"value": "on"}
    
    try:
        response = requests.patch(url, headers=headers, json=data)
        response.raise_for_status()
        result = response.json()
        
        if result.get("success"):
            print(f"   ✅ Always Use HTTPS activado")
        else:
            print(f"   ⚠️  No se pudo activar Always Use HTTPS: {result.get('errors')}")
    except Exception as e:
        print(f"   ⚠️  Error al activar Always Use HTTPS: {e}")

def configure_tunnel_routes():
    """Configura las rutas del túnel Cloudflare."""
    print("\n   Configurando rutas del túnel...")
    
    domains_to_route = [
        DOMAIN,
        f"www.{DOMAIN}"
    ]
    
    for domain in domains_to_route:
        try:
            result = subprocess.run(
                ["cloudflared", "tunnel", "route", "dns", "dvdcoin", domain],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0 or "already configured" in result.stdout.lower():
                print(f"   ✅ Ruta configurada: {domain}")
            else:
                print(f"   ⚠️  {domain}: {result.stdout}")
        except Exception as e:
            print(f"   ❌ Error configurando {domain}: {e}")

def main():
    print_header(f"🚀 CONFIGURACIÓN AUTOMÁTICA DE {DOMAIN}")
    
    print("Voy a configurar TODO automáticamente:")
    print("  • Eliminar registros DNS incorrectos")
    print("  • Crear registros CNAME correctos")
    print("  • Activar proxy de Cloudflare (naranja)")
    print("  • Configurar SSL/TLS en modo Full")
    print("  • Activar Always Use HTTPS")
    print("  • Configurar rutas del túnel")
    print()
    
    # Paso 1: Cargar token
    print("━" * 70)
    print("PASO 1: Cargando token de Cloudflare")
    print("━" * 70)
    token = load_token()
    if not token:
        return 1
    
    # Paso 2: Obtener Zone ID
    print("\n" + "━" * 70)
    print(f"PASO 2: Obteniendo Zone ID de {DOMAIN}")
    print("━" * 70)
    zone_id = get_zone_id(token, DOMAIN)
    if not zone_id:
        print()
        print("⚠️  IMPORTANTE:")
        print(f"   1. Ve a: https://dash.cloudflare.com")
        print(f"   2. Clic en 'Add domain'")
        print(f"   3. Añade: {DOMAIN}")
        print(f"   4. Cambia los nameservers en Hoststar")
        print(f"   5. Espera 2-4 horas")
        print(f"   6. Ejecuta este script de nuevo")
        return 1
    
    # Paso 3: Limpiar registros DNS incorrectos
    print("\n" + "━" * 70)
    print("PASO 3: Limpiando registros DNS incorrectos")
    print("━" * 70)
    
    records = list_dns_records(token, zone_id)
    print(f"   Encontrados {len(records)} registros DNS")
    
    # Eliminar registros A que apunten a IPs incorrectas
    for record in records:
        if record["type"] == "A" and record["name"] in [DOMAIN, f"www.{DOMAIN}"]:
            print(f"\n   ⚠️  Encontrado registro A: {record['name']} → {record['content']}")
            delete_dns_record(token, zone_id, record["id"], record["name"], record["type"], record["content"])
    
    # Paso 4: Crear/verificar registros CNAME
    print("\n" + "━" * 70)
    print("PASO 4: Creando/verificando registros CNAME")
    print("━" * 70)
    
    records = list_dns_records(token, zone_id)
    
    domains_to_configure = [DOMAIN, f"www.{DOMAIN}"]
    
    for domain in domains_to_configure:
        # Buscar si ya existe un CNAME
        cname_exists = False
        for record in records:
            if record["name"] == domain and record["type"] == "CNAME":
                cname_exists = True
                if record["content"] == TUNNEL_CNAME:
                    if record["proxied"]:
                        print(f"   ✅ CNAME correcto y proxied: {domain}")
                    else:
                        print(f"   ⚠️  CNAME correcto pero no proxied: {domain}")
                        print(f"      Activando proxy...")
                        update_dns_record(token, zone_id, record["id"], proxied=True)
                        print(f"   ✅ Proxy activado para: {domain}")
                else:
                    print(f"   ⚠️  CNAME incorrecto: {domain} → {record['content']}")
                    print(f"      Debería apuntar a: {TUNNEL_CNAME}")
                break
        
        if not cname_exists:
            print(f"\n   ⚠️  No existe CNAME para: {domain}")
            print(f"      Creando CNAME...")
            create_dns_record(token, zone_id, "CNAME", domain, TUNNEL_CNAME, proxied=True)
    
    # Paso 5: Configurar SSL/TLS
    print("\n" + "━" * 70)
    print("PASO 5: Configurando SSL/TLS")
    print("━" * 70)
    configure_ssl(token, zone_id, DOMAIN)
    
    # Paso 6: Configurar rutas del túnel
    print("\n" + "━" * 70)
    print("PASO 6: Configurando rutas del túnel Cloudflare")
    print("━" * 70)
    configure_tunnel_routes()
    
    # Resumen final
    print_header("✅ CONFIGURACIÓN COMPLETADA")
    
    print("Se han configurado los siguientes dominios:")
    print()
    print(f"  ✅ https://{DOMAIN}")
    print(f"     → {TUNNEL_CNAME}")
    print(f"     → Proxy: 🟠 ON")
    print(f"     → SSL: Full")
    print()
    print(f"  ✅ https://www.{DOMAIN}")
    print(f"     → {TUNNEL_CNAME}")
    print(f"     → Proxy: 🟠 ON")
    print(f"     → SSL: Full")
    print()
    print("⏳ Los cambios DNS pueden tardar 2-5 minutos en propagarse.")
    print()
    print("Prueba las URLs:")
    print(f"  • https://{DOMAIN}")
    print(f"  • https://www.{DOMAIN}")
    print()
    print("Si no funcionan inmediatamente, espera 2-5 minutos y prueba de nuevo.")
    print()
    
    # Guardar URL configurada
    url_file = Path(__file__).parent / "URL_CONFIGURADA.txt"
    url_file.write_text(f"https://{DOMAIN}\nhttps://www.{DOMAIN}\n")
    print(f"✅ URLs guardadas en: {url_file}")
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
