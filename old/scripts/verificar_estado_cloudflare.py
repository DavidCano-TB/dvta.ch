#!/usr/bin/env python3
"""
Verifica el estado del dominio dvta.ch en Cloudflare
"""

import sys
import json
import requests

DOMAIN = "dvta.ch"
ZONE_ID = "a0353c3d6ad85c54e8ed8f31237538b9"

def print_header(title):
    print()
    print("═" * 70)
    print(f"  {title}")
    print("═" * 70)
    print()

def check_zone_status(token):
    """Verifica el estado de la zona en Cloudflare."""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    url = f"https://api.cloudflare.com/client/v4/zones/{ZONE_ID}"
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        result = response.json()
        
        if result.get("success"):
            zone = result.get("result", {})
            print("✅ Información de la zona:")
            print(f"   • Nombre: {zone.get('name')}")
            print(f"   • Estado: {zone.get('status')}")
            print(f"   • Tipo: {zone.get('type')}")
            print(f"   • Nameservers originales: {zone.get('original_name_servers', [])}")
            print(f"   • Nameservers de Cloudflare: {zone.get('name_servers', [])}")
            print()
            
            status = zone.get('status')
            if status == 'pending':
                print("⚠️  ESTADO: PENDING")
                print()
                print("El dominio está esperando que los nameservers se propaguen.")
                print("Esto puede tardar entre 1 y 24 horas.")
                print()
                print("NO PUEDES añadir registros DNS hasta que el estado sea 'active'.")
                print()
                print("Verifica el estado en:")
                print(f"https://dash.cloudflare.com/{ZONE_ID}/{DOMAIN}")
                print()
                return False
            elif status == 'active':
                print("✅ ESTADO: ACTIVE")
                print()
                print("El dominio está activo y listo para añadir registros DNS.")
                print()
                return True
            else:
                print(f"⚠️  ESTADO DESCONOCIDO: {status}")
                return False
        else:
            print(f"❌ Error al obtener información: {result.get('errors')}")
            return False
    
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def list_dns_records(token):
    """Lista los registros DNS actuales."""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    url = f"https://api.cloudflare.com/client/v4/zones/{ZONE_ID}/dns_records"
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        result = response.json()
        
        if result.get("success"):
            records = result.get("result", [])
            if records:
                print(f"📋 Registros DNS actuales ({len(records)}):")
                print()
                for record in records:
                    print(f"   • {record.get('type'):6} {record.get('name'):40} → {record.get('content')}")
                print()
            else:
                print("📋 No hay registros DNS configurados todavía.")
                print()
            return True
        else:
            print(f"❌ Error al listar registros: {result.get('errors')}")
            return False
    
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    print_header(f"🔍 VERIFICACIÓN DE ESTADO: {DOMAIN}")
    
    # Intentar obtener el token del argumento o pedirlo
    if len(sys.argv) > 1:
        token = sys.argv[1].strip()
    else:
        print("Necesito tu token de Cloudflare para verificar el estado.")
        print()
        token = input("Pega tu token de Cloudflare aquí: ").strip()
    
    if not token:
        print("❌ Token vacío. Abortando.")
        return 1
    
    print()
    print("━" * 70)
    print("VERIFICANDO ESTADO DE LA ZONA")
    print("━" * 70)
    print()
    
    is_active = check_zone_status(token)
    
    print()
    print("━" * 70)
    print("LISTANDO REGISTROS DNS ACTUALES")
    print("━" * 70)
    print()
    
    list_dns_records(token)
    
    if is_active:
        print_header("✅ TODO LISTO")
        print("Puedes ejecutar: CONFIGURAR_EMAIL_CLOUDFLARE.bat")
        print()
        return 0
    else:
        print_header("⏳ ESPERANDO PROPAGACIÓN")
        print("Debes esperar a que los nameservers se propaguen.")
        print()
        print("Verifica el estado periódicamente con este script.")
        print()
        print("Cuando el estado sea 'active', podrás añadir los registros DNS.")
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
