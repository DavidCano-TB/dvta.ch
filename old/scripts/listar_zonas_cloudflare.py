#!/usr/bin/env python3
"""
Lista todas las zonas en tu cuenta de Cloudflare
"""

import sys
import json
import requests

def print_header(title):
    print()
    print("═" * 70)
    print(f"  {title}")
    print("═" * 70)
    print()

def list_zones(token):
    """Lista todas las zonas en la cuenta."""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    url = "https://api.cloudflare.com/client/v4/zones"
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        result = response.json()
        
        if result.get("success"):
            zones = result.get("result", [])
            if zones:
                print(f"✅ Zonas encontradas ({len(zones)}):")
                print()
                for zone in zones:
                    print(f"━" * 70)
                    print(f"   Nombre: {zone.get('name')}")
                    print(f"   Zone ID: {zone.get('id')}")
                    print(f"   Estado: {zone.get('status')}")
                    print(f"   Plan: {zone.get('plan', {}).get('name')}")
                    print(f"   Nameservers: {', '.join(zone.get('name_servers', []))}")
                    print(f"   Nameservers originales: {', '.join(zone.get('original_name_servers', []))}")
                    print()
                print(f"━" * 70)
                return True
            else:
                print("⚠️  No se encontraron zonas en tu cuenta.")
                return False
        else:
            errors = result.get('errors', [])
            print(f"❌ Error al listar zonas:")
            print(json.dumps(errors, indent=2))
            return False
    
    except requests.exceptions.HTTPError as e:
        print(f"❌ Error HTTP: {e}")
        try:
            error_detail = e.response.json()
            print(f"📋 Detalles del error:")
            print(json.dumps(error_detail, indent=2))
        except:
            pass
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    print_header("🔍 LISTANDO ZONAS DE CLOUDFLARE")
    
    # Intentar obtener el token del argumento o pedirlo
    if len(sys.argv) > 1:
        token = sys.argv[1].strip()
    else:
        print("Necesito tu token de Cloudflare.")
        print()
        token = input("Pega tu token de Cloudflare aquí: ").strip()
    
    if not token:
        print("❌ Token vacío. Abortando.")
        return 1
    
    print()
    print("━" * 70)
    print("CONSULTANDO API DE CLOUDFLARE")
    print("━" * 70)
    print()
    
    success = list_zones(token)
    
    if success:
        print_header("✅ CONSULTA COMPLETADA")
        return 0
    else:
        print_header("❌ ERROR EN LA CONSULTA")
        print("Verifica que:")
        print("  • El token sea correcto")
        print("  • El token tenga permisos de lectura de zonas")
        print("  • Tu cuenta de Cloudflare tenga zonas configuradas")
        print()
        return 1

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
