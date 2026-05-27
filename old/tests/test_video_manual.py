"""
Test manual simplificado para verificar videollamadas.
Abre dos ventanas de navegador y te guía paso a paso.

Requisitos:
    pip install playwright
    playwright install chromium

Uso:
    python test_video_manual.py
"""

import asyncio
from playwright.async_api import async_playwright
import time

BASE_URL = "https://striking-symphony-mummify.ngrok-free.dev"

async def main():
    print("=" * 70)
    print("🎥 TEST MANUAL DE VIDEOLLAMADA")
    print("=" * 70)
    print("\nEste script abrirá dos ventanas de navegador.")
    print("Sigue las instrucciones en pantalla.\n")
    
    input("Presiona ENTER para comenzar...")
    
    async with async_playwright() as p:
        # Lanzar navegador con permisos automáticos
        browser = await p.chromium.launch(
            headless=False,
            args=[
                '--use-fake-ui-for-media-stream',
                '--use-fake-device-for-media-stream',
            ]
        )
        
        # Crear dos contextos (simula dos navegadores)
        print("\n🚀 Abriendo navegadores...")
        context1 = await browser.new_context(
            permissions=['camera', 'microphone'],
            viewport={'width': 1000, 'height': 800}
        )
        context2 = await browser.new_context(
            permissions=['camera', 'microphone'],
            viewport={'width': 1000, 'height': 800}
        )
        
        page1 = await context1.new_page()
        page2 = await context2.new_page()
        
        # Abrir la aplicación en ambas ventanas
        print("📱 Cargando aplicación...")
        await page1.goto(BASE_URL)
        await page2.goto(BASE_URL)
        
        print("\n" + "=" * 70)
        print("✅ NAVEGADORES LISTOS")
        print("=" * 70)
        print("\n📋 INSTRUCCIONES:")
        print("\n1️⃣  En la VENTANA 1 (izquierda):")
        print("   - Haz login con el Usuario A")
        print("   - Ve a 'Social'")
        print("   - Crea una sala llamada 'test'")
        print("   - Deberías ver TU video")
        
        print("\n2️⃣  En la VENTANA 2 (derecha):")
        print("   - Haz login con el Usuario B (diferente)")
        print("   - Ve a 'Social'")
        print("   - Únete a la sala 'test'")
        print("   - Deberías ver TU video")
        
        print("\n3️⃣  VERIFICAR:")
        print("   ✅ Usuario A ve el video de Usuario B")
        print("   ✅ Usuario B ve el video de Usuario A")
        print("   ✅ Ambos escuchan el audio del otro")
        
        print("\n4️⃣  DIAGNÓSTICO (si no funciona):")
        print("   - Presiona F12 en cualquier ventana")
        print("   - En la consola, escribe: _videoDiagnostic()")
        print("   - Busca errores con ❌")
        
        print("\n" + "=" * 70)
        print("⏸️  Los navegadores permanecerán abiertos.")
        print("   Presiona ENTER cuando termines de probar...")
        print("=" * 70)
        
        input()
        
        print("\n🧹 Cerrando navegadores...")
        await browser.close()
        
        print("\n" + "=" * 70)
        print("❓ ¿FUNCIONÓ EL VIDEO?")
        print("=" * 70)
        result = input("\n¿Ambos usuarios vieron el video del otro? (s/n): ").lower()
        
        if result == 's':
            print("\n✅ ¡EXCELENTE! El video funciona correctamente.")
        else:
            print("\n❌ El video no funcionó. Pasos para debuggear:")
            print("\n1. Ejecuta el test de nuevo")
            print("2. Abre la consola (F12) en ambas ventanas")
            print("3. Busca mensajes con ❌ (errores)")
            print("4. Ejecuta: _videoDiagnostic()")
            print("5. Copia los logs y revisa:")
            print("   - connectionState debe ser 'connected'")
            print("   - remoteTracks no debe estar vacío")
            print("   - WebSocket state debe ser 1 (OPEN)")
            print("\n6. Si sigue sin funcionar, revisa:")
            print("   - Permisos de cámara/micrófono en el navegador")
            print("   - Firewall o antivirus bloqueando WebRTC")
            print("   - Probar en otro navegador (Chrome, Firefox, Edge)")

if __name__ == "__main__":
    asyncio.run(main())
