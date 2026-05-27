#!/usr/bin/env python3
"""
Verifica el estado de propagación DNS de dvta.ch
"""

import socket
import requests
import sys

DOMAIN = "dvta.ch"

def print_header(title):
    print()
    print("═" * 70)
    print(f"  {title}")
    print("═" * 70)
    print()

def check_dns_resolution():
    """Verifica si el dominio resuelve."""
    print(f"Verificando resolución DNS de {DOMAIN}...")
    print()
    
    try:
        ip = socket.gethostbyname(DOMAIN)
        print(f"✅ {DOMAIN} resuelve a: {ip}")
        return True, ip
    except socket.gaierror:
        print(f"❌ {DOMAIN} aún no resuelve (DNS_PROBE_POSSIBLE)")
        print("   Esto es normal, los nameservers están propagando.")
        return False, None

def check_cloudflare_nameservers():
    """Verifica los nameservers actuales."""
    print("Verificando nameservers...")
    print()
    
    try:
        import dns.resolver
        
        answers = dns.resolver.resolve(DOMAIN, 'NS')
        nameservers = [str(rdata) for rdata in answers]
        
        print("Nameservers actuales:")
        for ns in nameservers:
            print(f"  • {ns}")
            if "cloudflare" in ns.lower():
                print("    ✅ Nameserver de Cloudflare")
            else:
                print("    ⚠️  No es de Cloudflare")
        
        return nameservers
    
    except ImportError:
        print("⚠️  Módulo 'dnspython' no instalado")
        print("   No se puede verificar nameservers")
        return []
    except Exception as e:
        print(f"⚠️  No se pudieron obtener nameservers: {e}")
        return []

def check_online_dns():
    """Verifica DNS usando servicios online."""
    print("Verificando DNS en diferentes ubicaciones...")
    print()
    
    # Usar Google DNS
    try:
        import dns.resolver
        resolver = dns.resolver.Resolver()
        resolver.nameservers = ['8.8.8.8']  # Google DNS
        
        answers = resolver.resolve(DOMAIN, 'A')
        ips = [str(rdata) for rdata in answers]
        
        print("✅ Google DNS (8.8.8.8) resuelve:")
        for ip in ips:
            print(f"   → {ip}")
        
        return True
    
    except ImportError:
        print("⚠️  No se puede verificar con Google DNS (dnspython no instalado)")
        return False
    except Exception as e:
        print(f"❌ Google DNS aún no resuelve: {e}")
        return False

def check_cloudflare_dns():
    """Verifica DNS usando Cloudflare DNS."""
    print("Verificando con Cloudflare DNS (1.1.1.1)...")
    print()
    
    try:
        import dns.resolver
        resolver = dns.resolver.Resolver()
        resolver.nameservers = ['1.1.1.1']  # Cloudflare DNS
        
        answers = resolver.resolve(DOMAIN, 'A')
        ips = [str(rdata) for rdata in answers]
        
        print("✅ Cloudflare DNS (1.1.1.1) resuelve:")
        for ip in ips:
            print(f"   → {ip}")
        
        return True
    
    except ImportError:
        return False
    except Exception as e:
        print(f"❌ Cloudflare DNS aún no resuelve: {e}")
        return False

def main():
    print_header(f"🔍 VERIFICACIÓN DE PROPAGACIÓN DNS - {DOMAIN}")
    
    print("Esta herramienta verifica si tu dominio ya está propagado.")
    print()
    
    # Verificar resolución local
    print("━" * 70)
    print("1. Resolución DNS local")
    print("━" * 70)
    print()
    
    resolved, ip = check_dns_resolution()
    
    print()
    
    # Verificar nameservers
    print("━" * 70)
    print("2. Nameservers")
    print("━" * 70)
    print()
    
    nameservers = check_cloudflare_nameservers()
    
    print()
    
    # Verificar DNS públicos
    print("━" * 70)
    print("3. DNS públicos")
    print("━" * 70)
    print()
    
    google_ok = check_online_dns()
    print()
    cloudflare_ok = check_cloudflare_dns()
    
    print()
    
    # Resumen
    print_header("📊 RESUMEN")
    
    if resolved:
        print(f"✅ Tu dominio {DOMAIN} YA ESTÁ PROPAGADO")
        print()
        print(f"Puedes acceder a: https://{DOMAIN}")
        print()
        print("Si el túnel está corriendo, tu sitio debería funcionar.")
    else:
        print(f"⏳ Tu dominio {DOMAIN} AÚN ESTÁ PROPAGANDO")
        print()
        print("Esto es normal y puede tardar:")
        print("  • Mínimo: 1-2 horas")
        print("  • Normal: 2-4 horas")
        print("  • Máximo: 24 horas")
        print()
        print("¿Qué hacer mientras tanto?")
        print("  1. Deja el túnel corriendo (INICIAR_TUNNEL_DVTA.bat)")
        print("  2. Verifica que tu servidor Python esté corriendo (puerto 8000)")
        print("  3. Espera y vuelve a verificar en 1-2 horas")
        print()
        print("Para verificar de nuevo, ejecuta:")
        print("  python verificar_dns_propagacion.py")
    
    print()
    
    return 0 if resolved else 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n❌ Cancelado")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
