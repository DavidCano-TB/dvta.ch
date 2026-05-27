#!/usr/bin/env python3
"""
Verifica los registros DNS actuales en Cloudflare para dvta.ch
"""

import os
import sys
import json
import requests

# Configuración
DOMAIN = "dvta.ch"
ZONE_ID = "a0353c3d6ad85c54e8ed8f31237538b9"

def print_header(title):
    print()
    print("═" * 70)
    print(f"  {title}")
    print("═" * 70)
    print()

def get_cloudflare_token():
    """Obtiene el token de Cloudflare."""
    token = os.environ.get('CLOUDFLARE_API_TOKEN', '').strip()
    
    if token:
        print("✅ Token encontrado en variable de entorno")
        return token
    
    print("Necesito tu token de Cloudflare.")
    print()
    token = input("Pega tu token aquí: ").strip()
    return token

def list_dns_records(token, zone_id):
    """Lista todos los registros DNS de la zona."""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records"
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        result = response.json()
        
        if result.get("success"):
            return result.get("result", [])
        else:
            print(f"❌ Error: {result.get('errors')}")
            return []
    
    except Exception as e:
        print(f"❌ Error al obtener registros: {e}")
        return []

def main():
    print_header(f"🔍 VERIFICACIÓN DNS DE {DOMAIN}")
    
    # Obtener token
    token = get_cloudflare_token()
    
    if not token:
        print("❌ Token vacío. Abortando.")
        return 1
    
    print()
    print("Obteniendo registros DNS...")
    print()
    
    records = list_dns_records(token, ZONE_ID)
    
    if not records:
        print("❌ No se pudieron obtener los registros DNS")
        return 1
    
    # Categorizar registros
    email_records = {
        'MX': [],
        'TXT_SPF': [],
        'TXT_DKIM': [],
        'TXT_DMARC': [],
        'CNAME_AUTO': []
    }
    
    other_records = []
    
    for record in records:
        name = record.get('name', '')
        rtype = record.get('type', '')
        content = record.get('content', '')
        
        if rtype == 'MX':
            email_records['MX'].append(record)
        elif rtype == 'TXT' and 'spf' in content.lower():
            email_records['TXT_SPF'].append(record)
        elif rtype == 'TXT' and 'dkim' in content.lower():
            email_records['TXT_DKIM'].append(record)
        elif rtype == 'TXT' and 'dmarc' in content.lower():
            email_records['TXT_DMARC'].append(record)
        elif 'dkim' in name.lower() or 'dmarc' in name.lower():
            email_records['TXT_DKIM'].append(record)
        elif rtype == 'CNAME' and ('autoconfig' in name or 'autodiscover' in name):
            email_records['CNAME_AUTO'].append(record)
        else:
            other_records.append(record)
    
    # Mostrar registros de email
    print("━" * 70)
    print("📧 REGISTROS DE EMAIL")
    print("━" * 70)
    print()
    
    print("MX (Servidor de correo):")
    if email_records['MX']:
        for r in email_records['MX']:
            print(f"  ✅ {r['name']} → {r['content']} (prioridad: {r.get('priority', 'N/A')})")
    else:
        print("  ❌ No configurado")
    print()
    
    print("SPF (Autorización de envío):")
    if email_records['TXT_SPF']:
        for r in email_records['TXT_SPF']:
            print(f"  ✅ {r['name']}")
            print(f"     {r['content'][:80]}...")
    else:
        print("  ❌ No configurado")
    print()
    
    print("DKIM (Firma digital):")
    if email_records['TXT_DKIM']:
        for r in email_records['TXT_DKIM']:
            print(f"  ✅ {r['name']}")
            content_preview = r['content'][:60] + "..." if len(r['content']) > 60 else r['content']
            print(f"     {content_preview}")
    else:
        print("  ❌ No configurado")
    print()
    
    print("DMARC (Política de seguridad):")
    if email_records['TXT_DMARC']:
        for r in email_records['TXT_DMARC']:
            print(f"  ✅ {r['name']} → {r['content']}")
    else:
        print("  ❌ No configurado")
    print()
    
    print("Autoconfig/Autodiscover:")
    if email_records['CNAME_AUTO']:
        for r in email_records['CNAME_AUTO']:
            print(f"  ✅ {r['name']} → {r['content']}")
    else:
        print("  ❌ No configurado")
    print()
    
    # Mostrar otros registros
    print("━" * 70)
    print("🌐 OTROS REGISTROS DNS")
    print("━" * 70)
    print()
    
    if other_records:
        for r in other_records:
            rtype = r.get('type', '')
            name = r.get('name', '')
            content = r.get('content', '')
            proxied = "🟠 Proxied" if r.get('proxied') else "⚪ DNS only"
            
            content_preview = content[:50] + "..." if len(content) > 50 else content
            print(f"  {rtype:6} {name:30} → {content_preview:50} {proxied}")
    else:
        print("  (ninguno)")
    
    print()
    print_header("✅ VERIFICACIÓN COMPLETADA")
    
    # Resumen
    total_email = sum(len(v) for v in email_records.values())
    print(f"Total de registros de email: {total_email}")
    print(f"Total de otros registros: {len(other_records)}")
    print(f"Total general: {len(records)}")
    print()
    
    # Verificar si falta algo
    missing = []
    if not email_records['MX']:
        missing.append("MX")
    if not email_records['TXT_SPF']:
        missing.append("SPF")
    if not email_records['TXT_DKIM']:
        missing.append("DKIM")
    if not email_records['TXT_DMARC']:
        missing.append("DMARC")
    if not email_records['CNAME_AUTO']:
        missing.append("Autoconfig/Autodiscover")
    
    if missing:
        print("⚠️  Registros faltantes:")
        for m in missing:
            print(f"   • {m}")
        print()
        print("Para configurarlos, ejecuta: CONFIGURAR_DNS_AUTOMATICO.bat")
    else:
        print("✅ Todos los registros de email están configurados")
    
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
