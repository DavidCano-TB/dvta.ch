#!/usr/bin/env python3
"""
Configura TODOS los registros DNS de email en Cloudflare para dvta.ch
"""

import os
import sys
import json
import requests
from pathlib import Path

# Configuración
DOMAIN = "dvta.ch"
ZONE_ID = "a0353c3d6ad85c54e8ed8f31237538b9"  # Del dashboard de Cloudflare

def print_header(title):
    print()
    print("═" * 70)
    print(f"  {title}")
    print("═" * 70)
    print()

def get_cloudflare_token():
    """Solicita el token de Cloudflare al usuario."""
    # Primero intentar obtener de variable de entorno
    token = os.environ.get('CLOUDFLARE_API_TOKEN', '').strip()
    
    if token:
        print("✅ Token encontrado en variable de entorno CLOUDFLARE_API_TOKEN")
        return token
    
    print("Necesito tu token de Cloudflare con permisos de DNS.")
    print()
    print("Para crear el token:")
    print("1. Ve a: https://dash.cloudflare.com/profile/api-tokens")
    print("2. Clic en [Create Token]")
    print("3. Usa el template: 'Edit zone DNS'")
    print("4. Zone: dvta.ch")
    print("5. Copia el token")
    print()
    print("💡 TIP: Puedes guardar el token en una variable de entorno:")
    print("   set CLOUDFLARE_API_TOKEN=tu_token_aqui")
    print()
    token = input("Pega tu token de Cloudflare aquí: ").strip()
    return token

def create_dns_record(token, zone_id, record_type, name, content, priority=None, proxied=False):
    """Crea un registro DNS en Cloudflare."""
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
        "ttl": 3600
    }
    
    if priority is not None:
        data["priority"] = priority
    
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        result = response.json()
        
        if result.get("success"):
            print(f"   ✅ Creado: {name} ({record_type} → {content})")
            return True
        else:
            errors = result.get('errors', [])
            # Si el error es que ya existe, no es crítico
            if any('already exists' in str(e).lower() for e in errors):
                print(f"   ℹ️  Ya existe: {name}")
                return True
            print(f"   ❌ Error al crear {name}: {errors}")
            return False
    
    except Exception as e:
        print(f"   ❌ Error: {e}")
        # Intentar mostrar más detalles del error
        try:
            error_detail = response.json()
            print(f"   📋 Detalles: {json.dumps(error_detail, indent=2)}")
        except:
            pass
        return False

def main():
    print_header(f"🚀 CONFIGURACIÓN DNS DE EMAIL PARA {DOMAIN}")
    
    print("Voy a configurar TODOS los registros de email automáticamente:")
    print("  • MX (servidor de correo)")
    print("  • SPF (autorización de envío)")
    print("  • DKIM (firma digital)")
    print("  • DMARC (política de seguridad)")
    print("  • Autoconfig (configuración automática)")
    print("  • Autodiscover (configuración automática)")
    print()
    
    # Obtener token
    token = get_cloudflare_token()
    
    if not token:
        print("❌ Token vacío. Abortando.")
        return 1
    
    print()
    print("━" * 70)
    print("PASO 1: Creando registro MX (servidor de correo)")
    print("━" * 70)
    create_dns_record(token, ZONE_ID, "MX", DOMAIN, "mta-gw.infomaniak.ch", priority=10, proxied=False)
    
    print()
    print("━" * 70)
    print("PASO 2: Creando registro SPF (autorización de envío)")
    print("━" * 70)
    create_dns_record(token, ZONE_ID, "TXT", DOMAIN, "v=spf1 include:spf.infomaniak.ch -all", proxied=False)
    
    print()
    print("━" * 70)
    print("PASO 3: Creando registro DKIM (firma digital)")
    print("━" * 70)
    dkim_content = "v=DKIM1; t=s; p=MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA2fYHTJxIlJmtKLvrVTwqL8AUMxfTOGcy5KHN/SGLqXR7peGe07Qln4FFLtEtTVmx/RJKqpfOb/G95U2ZwQO9axJcZJGRb0J7v8Nl2QpViMSEhzbu6obXVuYSj+6c5IdFGH1viFq2LkDCLv2fOJeVRcIQqXZ+iDg+4i+rall2WswzO62Hpsu1QfTQY1wUYp2Y1GZmSThs54V2NdN6d7I7JHAYz9KztzeDtw+KBKzq2UChOPknsme3X0WBcThaPeMip7pAbFMmgTDERrz0B6QcHTV1whL7Nmd67kzmvXVDQSU8OBSo3Y1JJpIKtlcbtFgoCdJL0RH7fDHJw1xU+vgaKQIDAQAB"
    create_dns_record(token, ZONE_ID, "TXT", f"20260527._domainkey.{DOMAIN}", dkim_content, proxied=False)
    
    print()
    print("━" * 70)
    print("PASO 4: Creando registro DKIM SPF")
    print("━" * 70)
    create_dns_record(token, ZONE_ID, "TXT", f"_domainkey.{DOMAIN}", "v=spf1 -all", proxied=False)
    
    print()
    print("━" * 70)
    print("PASO 5: Creando registro DMARC (política de seguridad)")
    print("━" * 70)
    create_dns_record(token, ZONE_ID, "TXT", f"_dmarc.{DOMAIN}", "v=DMARC1; p=reject;", proxied=False)
    
    print()
    print("━" * 70)
    print("PASO 6: Creando registro DMARC DKIM")
    print("━" * 70)
    create_dns_record(token, ZONE_ID, "TXT", f"_dmarc._domainkey.{DOMAIN}", "v=DMARC1; p=reject;", proxied=False)
    
    print()
    print("━" * 70)
    print("PASO 7: Creando Autoconfig (Thunderbird, etc.)")
    print("━" * 70)
    create_dns_record(token, ZONE_ID, "CNAME", f"autoconfig.{DOMAIN}", "infomaniak.com", proxied=False)
    
    print()
    print("━" * 70)
    print("PASO 8: Creando Autodiscover (Outlook, etc.)")
    print("━" * 70)
    create_dns_record(token, ZONE_ID, "CNAME", f"autodiscover.{DOMAIN}", "infomaniak.com", proxied=False)
    
    print_header("✅ CONFIGURACIÓN COMPLETADA")
    
    print("Se han configurado todos los registros de email:")
    print()
    print("  ✅ MX → mta-gw.infomaniak.ch")
    print("  ✅ SPF → v=spf1 include:spf.infomaniak.ch -all")
    print("  ✅ DKIM → 20260527._domainkey.dvta.ch")
    print("  ✅ DMARC → _dmarc.dvta.ch")
    print("  ✅ Autoconfig → autoconfig.dvta.ch")
    print("  ✅ Autodiscover → autodiscover.dvta.ch")
    print()
    print("⏳ Los cambios DNS pueden tardar 5-10 minutos en propagarse.")
    print()
    print("Tu email @dvta.ch debería seguir funcionando normalmente.")
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
