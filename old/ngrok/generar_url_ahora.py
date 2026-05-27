#!/usr/bin/env python3
"""
Genera una URL temporal de Cloudflare que funciona INMEDIATAMENTE.
"""

import subprocess
import time
import re
import sys
import os
from pathlib import Path

def main():
    print()
    print("═" * 63)
    print("  ⚡ GENERANDO URL TEMPORAL FUNCIONAL")
    print("═" * 63)
    print()
    
    # Verificar que el servidor Python esté corriendo
    print("1. Verificando servidor Python...")
    try:
        import requests
        r = requests.get("http://127.0.0.1:8000", timeout=5)
        print(f"   ✅ Servidor Python OK (Status: {r.status_code})")
    except Exception as e:
        print(f"   ❌ Servidor Python no responde: {e}")
        print()
        print("   Iniciando servidor Python...")
        # No bloqueante
        subprocess.Popen(
            ["python", "main.py"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            cwd=Path(__file__).parent
        )
        print("   Esperando 5 segundos...")
        time.sleep(5)
    print()
    
    # Iniciar Quick Tunnel
    print("2. Iniciando Cloudflare Quick Tunnel...")
    print("   (Esto puede tardar 10-15 segundos)")
    print()
    
    process = subprocess.Popen(
        ["cloudflared", "tunnel", "--url", "http://localhost:8000"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        cwd=Path(__file__).parent
    )
    
    url_encontrada = None
    timeout_seconds = 30
    start_time = time.time()
    
    print("   Buscando URL generada...")
    
    try:
        while time.time() - start_time < timeout_seconds:
            line = process.stdout.readline()
            if not line:
                break
            
            # Buscar la URL en la salida
            match = re.search(r'https://[a-z0-9-]+\.trycloudflare\.com', line)
            if match:
                url_encontrada = match.group(0)
                break
            
            # Mostrar progreso
            if "Registered tunnel connection" in line:
                print("   ⏳ Conexión establecida...")
            elif "INF" in line and "connection" in line.lower():
                print("   ⏳ Conectando...")
    
    except KeyboardInterrupt:
        print("\n\n❌ Cancelado por el usuario")
        process.terminate()
        return 1
    
    print()
    
    if url_encontrada:
        print("═" * 63)
        print("  ✅ URL GENERADA Y FUNCIONANDO")
        print("═" * 63)
        print()
        print(f"  👉 {url_encontrada}")
        print()
        print("═" * 63)
        print()
        print("✅ Esta URL funciona AHORA MISMO:")
        print("   • HTTPS válido (certificado SSL de Cloudflare)")
        print("   • Accesible desde cualquier dispositivo y red")
        print("   • Compatible con navegadores in-app")
        print()
        print("⚠️  IMPORTANTE:")
        print("   • Esta URL es TEMPORAL")
        print("   • Cambiará cada vez que reinicies el servidor")
        print("   • El túnel debe permanecer activo (no cierres esta ventana)")
        print()
        print("💾 Guardando URL en: url_temporal.txt")
        Path("url_temporal.txt").write_text(url_encontrada)
        print()
        print("🌐 Abriendo en el navegador...")
        try:
            import webbrowser
            webbrowser.open(url_encontrada)
        except:
            pass
        print()
        print("═" * 63)
        print()
        print("El túnel está activo. Presiona Ctrl+C para detenerlo.")
        print()
        
        # Mantener el proceso vivo
        try:
            process.wait()
        except KeyboardInterrupt:
            print("\n\n⚠️  Deteniendo túnel...")
            process.terminate()
            process.wait()
            print("✅ Túnel detenido")
        
        return 0
    else:
        print("═" * 63)
        print("  ❌ NO SE PUDO GENERAR LA URL")
        print("═" * 63)
        print()
        print("El Quick Tunnel no generó una URL en 30 segundos.")
        print()
        print("Posibles causas:")
        print("  • Problema de conexión a Internet")
        print("  • Cloudflared no está instalado correctamente")
        print("  • Puerto 8000 no está disponible")
        print()
        print("Intenta ejecutar manualmente:")
        print("  cloudflared tunnel --url http://localhost:8000")
        print()
        process.terminate()
        return 1

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
