#!/usr/bin/env python3
"""
Arregla la configuración DNS en Cloudflare eliminando registros A incorrectos
y verificando que los CNAME del túnel estén correctos.
"""

import os
import sys
import json
import requests
from pathlib import Path

# Configuración
ZONE_NAME = "david.ch"
SUBDOMINIOS = ["dvdbank.david.ch", "app.david.ch", "localhost.david.ch"]
TUNNEL_ID = "6c0cb6da-aafe-4e61-89aa-42d9bd2e5b33"
TUNNEL_CNAME = f"{TUNNEL_ID}.cfargotunnel.com"
IP_INCORRECTA = "80.74.152.80"

def cargar_token():
    """Carga el token de Cloudflare desde el archivo de configuración."""
    token_file = Path(__file__).parent / "config" / "cloudflare_token.txt"
    if not token_file.exists():
        print("❌ No se encontró el archivo de token:")
        print(f"   {token_file}")
        print()
        print("Por favor:")
        print("1. Ve a: https://dash.cloudflare.com/profile/api-tokens")
        print("2. Crea un token con permisos 'Edit zone DNS' para david.ch")
        print("3. Guarda el token en:")
        print(f"   {token_file}")
        return None
    
    token = token_file.read_text().strip()
    if not token:
        print("❌ El archivo de token está vacío")
        return None
    
    return token

def obtener_zone_id(token):
    """Obtiene el Zone ID de david.ch."""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    url = "https://api.cloudflare.com/client/v4/zones"
    params = {"name": ZONE_NAME}
    
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        
        if not data.get("success"):
            print(f"❌ Error de Cloudflare: {data.get('errors')}")
            return None
        
        if not data.get("result"):
            print(f"❌ No se encontró la zona: {ZONE_NAME}")
            return None
        
        zone_id = data["result"][0]["id"]
        print(f"✅ Zone ID encontrado: {zone_id}")
        return zone_id
    
    except requests.exceptions.RequestException as e:
        print(f"❌ Error al conectar con Cloudflare: {e}")
        return None

def listar_registros_dns(token, zone_id):
    """Lista todos los registros DNS de la zona."""
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
    
    except requests.exceptions.RequestException as e:
        print(f"❌ Error: {e}")
        return []

def eliminar_registro(token, zone_id, record_id, nombre, tipo, contenido):
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
            print(f"   ✅ Eliminado: {nombre} ({tipo} → {contenido})")
            return True
        else:
            print(f"   ❌ Error al eliminar {nombre}: {data.get('errors')}")
            return False
    
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Error: {e}")
        return False

def verificar_cname(token, zone_id, nombre):
    """Verifica que existe un CNAME correcto para el subdominio."""
    registros = listar_registros_dns(token, zone_id)
    
    for r in registros:
        if r["name"] == nombre and r["type"] == "CNAME":
            if r["content"] == TUNNEL_CNAME:
                print(f"   ✅ CNAME correcto: {nombre} → {TUNNEL_CNAME}")
                if not r.get("proxied"):
                    print(f"   ⚠️  Advertencia: {nombre} no está proxied (naranja)")
                return True
            else:
                print(f"   ⚠️  CNAME incorrecto: {nombre} → {r['content']}")
                return False
    
    print(f"   ❌ No existe CNAME para: {nombre}")
    print(f"      Ejecuta: cloudflared tunnel route dns dvdcoin {nombre}")
    return False

def main():
    print()
    print("═" * 63)
    print("  🔧 ARREGLANDO DNS EN CLOUDFLARE")
    print("═" * 63)
    print()
    
    # Cargar token
    print("1. Cargando token de Cloudflare...")
    token = cargar_token()
    if not token:
        return 1
    print("   ✅ Token cargado")
    print()
    
    # Obtener Zone ID
    print("2. Obteniendo Zone ID...")
    zone_id = obtener_zone_id(token)
    if not zone_id:
        return 1
    print()
    
    # Listar registros DNS
    print("3. Listando registros DNS...")
    registros = listar_registros_dns(token, zone_id)
    print(f"   ✅ Encontrados {len(registros)} registros")
    print()
    
    # Buscar y eliminar registros A incorrectos
    print("4. Buscando registros A incorrectos...")
    eliminados = 0
    for r in registros:
        if r["type"] == "A" and r["name"] in SUBDOMINIOS:
            if r["content"] == IP_INCORRECTA:
                print(f"   ⚠️  Encontrado registro A incorrecto: {r['name']} → {IP_INCORRECTA}")
                if eliminar_registro(token, zone_id, r["id"], r["name"], r["type"], r["content"]):
                    eliminados += 1
    
    if eliminados == 0:
        print("   ✅ No se encontraron registros A incorrectos")
    else:
        print(f"   ✅ Eliminados {eliminados} registros incorrectos")
    print()
    
    # Verificar CNAMEs
    print("5. Verificando CNAMEs del túnel...")
    for subdominio in SUBDOMINIOS:
        verificar_cname(token, zone_id, subdominio)
    print()
    
    print("═" * 63)
    print("  ✅ PROCESO COMPLETADO")
    print("═" * 63)
    print()
    print("Espera 1-2 minutos para que los cambios DNS se propaguen.")
    print("Luego ejecuta: PROBAR_TODAS_URLS.bat")
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
