#!/usr/bin/env python3
"""
Configura TODO automáticamente: DNS, certificados, túnel para dvdbank.ch
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

# Dominios a configurar
DOMAINS = {
    "david.ch": {
        "subdomains": ["dvdbank", "app", "localhost"],
        "zone_id": None  # Se obtendrá automáticamente
    }
}

def print_header(title):
    print()
    print("═" * 70)
    print(f"  {title}")
    print("═" * 70)
    print()

def print_step(step, title):
    print(f"\n{'='*70}")
    print(f"PASO {step}: {title}")
    print('='*70)

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
            print(f"   ❌ Error al crear {name}: {result.get('errors')}")
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
            print(f"   ✅ SSL/TLS configurado en modo Full para {zone_name}")
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
            print(f"   ✅ Always Use HTTPS activado para {zone_name}")
        else:
            print(f"   ⚠️  No se pudo activar Always Use HTTPS: {result.get('errors')}")
    except Exception as e:
        print(f"   ⚠️  Error al activar Always Use HTTPS: {e}")

def configure_tunnel_routes():
    """Configura las rutas del túnel Cloudflare."""
    print("\n   Configurando rutas del túnel...")
    
    domains_to_route = [
        "dvdbank.david.ch",
        "app.david.ch",
        "localhost.david.ch"
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
    print_header("🚀 CONFIGURACIÓN AUTOMÁTICA COMPLETA")
    
    print("Voy a configurar TODO automáticamente:")
    print("  • Eliminar registros DNS incorrectos")
    print("  • Crear registros CNAME correctos")
    print("  • Activar proxy de Cloudflare (naranja)")
    print("  • Configurar SSL/TLS en modo Full")
    print("  • Activar Always Use HTTPS")
    print("  • Configurar rutas del túnel")
    print()
    
    # Paso 1: Cargar token
    print_step(1, "Cargando token de Cloudflare")
    token = load_token()
    if not token:
        return 1
    
    # Paso 2: Obtener Zone IDs
    print_step(2, "Obteniendo Zone IDs")
    for zone_name in DOMAINS:
        zone_id = get_zone_id(token, zone_name)
        if zone_id:
            DOMAINS[zone_name]["zone_id"] = zone_id
        else:
            print(f"❌ No se pudo obtener Zone ID de {zone_name}")
            return 1
    
    # Paso 3: Limpiar registros DNS incorrectos
    print_step(3, "Limpiando registros DNS incorrectos")
    
    for zone_name, config in DOMAINS.items():
        zone_id = config["zone_id"]
        print(f"\n📍 Procesando zona: {zone_name}")
        
        records = list_dns_records(token, zone_id)
        print(f"   Encontrados {len(records)} registros DNS")
        
        # Eliminar registros A incorrectos
        for subdomain in config["subdomains"]:
            full_domain = f"{subdomain}.{zone_name}"
            
            for record in records:
                if record["name"] == full_domain and record["type"] == "A":
                    print(f"\n   ⚠️  Encontrado registro A incorrecto: {full_domain} → {record['content']}")
                    delete_dns_record(token, zone_id, record["id"], record["name"], record["type"], record["content"])
    
    # Paso 4: Crear/verificar registros CNAME
    print_step(4, "Creando/verificando registros CNAME")
    
    for zone_name, config in DOMAINS.items():
        zone_id = config["zone_id"]
        print(f"\n📍 Procesando zona: {zone_name}")
        
        records = list_dns_records(token, zone_id)
        
        for subdomain in config["subdomains"]:
            full_domain = f"{subdomain}.{zone_name}"
            
            # Buscar si ya existe un CNAME
            cname_exists = False
            for record in records:
                if record["name"] == full_domain and record["type"] == "CNAME":
                    cname_exists = True
                    if record["content"] == TUNNEL_CNAME:
                        if record["proxied"]:
                            print(f"   ✅ CNAME correcto y proxied: {full_domain}")
                        else:
                            print(f"   ⚠️  CNAME correcto pero no proxied: {full_domain}")
                            print(f"      Activando proxy...")
                            update_dns_record(token, zone_id, record["id"], proxied=True)
                            print(f"   ✅ Proxy activado para: {full_domain}")
                    else:
                        print(f"   ⚠️  CNAME incorrecto: {full_domain} → {record['content']}")
                        print(f"      Debería apuntar a: {TUNNEL_CNAME}")
                    break
            
            if not cname_exists:
                print(f"\n   ⚠️  No existe CNAME para: {full_domain}")
                print(f"      Creando CNAME...")
                create_dns_record(token, zone_id, "CNAME", full_domain, TUNNEL_CNAME, proxied=True)
    
    # Paso 5: Configurar SSL/TLS
    print_step(5, "Configurando SSL/TLS")
    
    for zone_name, config in DOMAINS.items():
        zone_id = config["zone_id"]
        print(f"\n📍 Configurando SSL para: {zone_name}")
        configure_ssl(token, zone_id, zone_name)
    
    # Paso 6: Configurar rutas del túnel
    print_step(6, "Configurando rutas del túnel Cloudflare")
    configure_tunnel_routes()
    
    # Resumen final
    print_header("✅ CONFIGURACIÓN COMPLETADA")
    
    print("Se han configurado los siguientes dominios:")
    print()
    for zone_name, config in DOMAINS.items():
        for subdomain in config["subdomains"]:
            full_domain = f"{subdomain}.{zone_name}"
            print(f"  ✅ https://{full_domain}")
            print(f"     → {TUNNEL_CNAME}")
            print(f"     → Proxy: 🟠 ON")
            print(f"     → SSL: Full")
            print()
    
    print("⏳ Los cambios DNS pueden tardar 2-5 minutos en propagarse.")
    print()
    print("Prueba las URLs:")
    print("  • https://dvdbank.david.ch")
    print("  • https://app.david.ch")
    print("  • https://localhost.david.ch")
    print()
    print("Si no funcionan inmediatamente, espera 2-5 minutos y prueba de nuevo.")
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
