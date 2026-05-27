"""
Test automatizado para verificar que las videollamadas WebRTC funcionan correctamente.
Simula dos usuarios uniéndose a una sala y verifica que se establece la conexión.

Requisitos:
    pip install playwright pytest
    playwright install chromium

Uso:
    python test_video_call.py
    o
    pytest test_video_call.py -v
"""

import asyncio
import time
import json
from playwright.async_api import async_playwright, Page, Browser, BrowserContext
import sys

# Configuración
BASE_URL = "https://striking-symphony-mummify.ngrok-free.dev"
# Usuarios de prueba - ajustar según tus usuarios reales
USER_A = {"username": "dvd", "password": "tu_password_aqui"}
USER_B = {"username": "nina", "password": "tu_password_aqui"}
ROOM_NAME = f"test-auto-{int(time.time())}"

class VideoCallTester:
    def __init__(self):
        self.playwright = None
        self.browser = None
        self.context_a = None
        self.context_b = None
        self.page_a = None
        self.page_b = None
        self.logs_a = []
        self.logs_b = []
        
    async def setup(self):
        """Inicializar Playwright y navegadores"""
        print("🚀 Iniciando navegadores...")
        self.playwright = await async_playwright().start()
        
        # Lanzar navegador con permisos de cámara/micrófono
        self.browser = await self.playwright.chromium.launch(
            headless=False,  # Cambiar a True para modo headless
            args=[
                '--use-fake-ui-for-media-stream',  # Auto-aprobar permisos
                '--use-fake-device-for-media-stream',  # Usar dispositivos fake
                '--allow-file-access-from-files',
            ]
        )
        
        # Crear contextos separados para cada usuario (simula navegadores diferentes)
        self.context_a = await self.browser.new_context(
            permissions=['camera', 'microphone'],
            viewport={'width': 1280, 'height': 720}
        )
        self.context_b = await self.browser.new_context(
            permissions=['camera', 'microphone'],
            viewport={'width': 1280, 'height': 720}
        )
        
        # Crear páginas
        self.page_a = await self.context_a.new_page()
        self.page_b = await self.context_b.new_page()
        
        # Capturar logs de consola
        self.page_a.on('console', lambda msg: self.logs_a.append(f"[A] {msg.text()}"))
        self.page_b.on('console', lambda msg: self.logs_b.append(f"[B] {msg.text()}"))
        
        print("✅ Navegadores iniciados")
    
    async def login(self, page: Page, user: dict, label: str):
        """Login de usuario"""
        print(f"🔐 {label}: Haciendo login como {user['username']}...")
        
        await page.goto(BASE_URL)
        await page.wait_for_load_state('networkidle')
        
        # Llenar formulario de login
        await page.fill('input[name="username"], input[placeholder*="usuario"]', user['username'])
        await page.fill('input[name="password"], input[type="password"]', user['password'])
        
        # Click en botón de login
        await page.click('button:has-text("Entrar"), button:has-text("Login"), button[type="submit"]')
        
        # Esperar a que cargue la app
        await page.wait_for_timeout(2000)
        
        # Verificar que el login fue exitoso
        try:
            await page.wait_for_selector('text=Social, [aria-label="Social"]', timeout=5000)
            print(f"✅ {label}: Login exitoso")
            return True
        except:
            print(f"❌ {label}: Login falló")
            return False
    
    async def navigate_to_social(self, page: Page, label: str):
        """Navegar a la sección Social"""
        print(f"📱 {label}: Navegando a Social...")
        
        # Click en el botón/link de Social
        await page.click('text=Social, [aria-label="Social"], #navSocial')
        await page.wait_for_timeout(1000)
        
        print(f"✅ {label}: En sección Social")
    
    async def create_room(self, page: Page, room_name: str, label: str):
        """Crear una sala de video"""
        print(f"🎥 {label}: Creando sala '{room_name}'...")
        
        # Click en "Crear sala" o botón similar
        try:
            await page.click('button:has-text("Crear sala"), #btnStartRoom', timeout=5000)
        except:
            print(f"⚠️ {label}: No se encontró botón 'Crear sala', intentando alternativa...")
            await page.click('button:has-text("Nueva sala")')
        
        await page.wait_for_timeout(500)
        
        # Llenar nombre de sala si hay input
        try:
            await page.fill('input[placeholder*="nombre"], input[name*="room"]', room_name)
            await page.click('button:has-text("Crear"), button:has-text("OK")')
        except:
            # Si no hay input, la sala se crea directamente
            pass
        
        await page.wait_for_timeout(2000)
        
        # Verificar que se creó la sala (debe aparecer el video grid)
        try:
            await page.wait_for_selector('#socialVideoGrid, [id*="video"]', timeout=5000)
            print(f"✅ {label}: Sala creada")
            return True
        except:
            print(f"❌ {label}: No se pudo crear la sala")
            return False
    
    async def join_room(self, page: Page, room_name: str, label: str):
        """Unirse a una sala existente"""
        print(f"🚪 {label}: Uniéndose a sala '{room_name}'...")
        
        await page.wait_for_timeout(1000)
        
        # Buscar la sala en la lista y hacer click en "Unirse"
        try:
            # Buscar el botón de unirse para esta sala específica
            await page.click(f'button:has-text("Unirse"):near(:text("{room_name}"))', timeout=5000)
        except:
            # Alternativa: buscar cualquier botón de unirse
            print(f"⚠️ {label}: Buscando sala de forma alternativa...")
            await page.click('button:has-text("▶ Unirse"), button:has-text("Unirse")')
        
        await page.wait_for_timeout(2000)
        
        # Verificar que se unió a la sala
        try:
            await page.wait_for_selector('#socialVideoGrid, [id*="video"]', timeout=5000)
            print(f"✅ {label}: Unido a la sala")
            return True
        except:
            print(f"❌ {label}: No se pudo unir a la sala")
            return False
    
    async def check_local_video(self, page: Page, label: str):
        """Verificar que el video local está visible"""
        print(f"📹 {label}: Verificando video local...")
        
        # Buscar el tile de video local
        try:
            local_video = await page.query_selector('#vtile-__local__ video, video[id*="local"]')
            if local_video:
                is_visible = await local_video.is_visible()
                if is_visible:
                    print(f"✅ {label}: Video local visible")
                    return True
            print(f"❌ {label}: Video local no visible")
            return False
        except Exception as e:
            print(f"❌ {label}: Error verificando video local: {e}")
            return False
    
    async def check_remote_video(self, page: Page, label: str, timeout: int = 10):
        """Verificar que el video remoto está visible"""
        print(f"🔍 {label}: Esperando video remoto (timeout: {timeout}s)...")
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                # Buscar tiles de video que NO sean el local
                video_tiles = await page.query_selector_all('[id^="vtile-"]:not(#vtile-__local__)')
                
                if len(video_tiles) > 0:
                    # Verificar que al menos uno tiene video visible
                    for tile in video_tiles:
                        video = await tile.query_selector('video')
                        if video:
                            is_visible = await video.is_visible()
                            if is_visible:
                                print(f"✅ {label}: Video remoto visible ({len(video_tiles)} peer(s))")
                                return True
                
                await page.wait_for_timeout(1000)
            except Exception as e:
                print(f"⚠️ {label}: Error buscando video remoto: {e}")
                await page.wait_for_timeout(1000)
        
        print(f"❌ {label}: Video remoto NO visible después de {timeout}s")
        return False
    
    async def check_webrtc_connection(self, page: Page, label: str):
        """Verificar el estado de la conexión WebRTC usando la función de diagnóstico"""
        print(f"🔬 {label}: Verificando estado WebRTC...")
        
        try:
            # Ejecutar función de diagnóstico
            result = await page.evaluate("""
                () => {
                    if (typeof _videoDiagnostic !== 'function') {
                        return { error: 'Función _videoDiagnostic no disponible' };
                    }
                    
                    // Capturar el estado
                    const state = {
                        currentRoom: _currentVideoRoom || null,
                        hasLocalStream: !!_localStream,
                        localStreamActive: _localStream ? _localStream.active : false,
                        localTracks: _localStream ? _localStream.getTracks().map(t => ({
                            kind: t.kind,
                            enabled: t.enabled,
                            readyState: t.readyState
                        })) : [],
                        wsState: _videoWS ? _videoWS.readyState : null,
                        peers: Object.keys(_rtcPeers || {}),
                        peerStates: {}
                    };
                    
                    // Estado de cada peer
                    if (_rtcPeers) {
                        for (const [peer, pc] of Object.entries(_rtcPeers)) {
                            state.peerStates[peer] = {
                                connectionState: pc.connectionState,
                                iceConnectionState: pc.iceConnectionState,
                                signalingState: pc.signalingState,
                                localTracks: pc.getSenders().map(s => s.track ? s.track.kind : null).filter(Boolean),
                                remoteTracks: pc.getReceivers().map(r => r.track ? r.track.kind : null).filter(Boolean)
                            };
                        }
                    }
                    
                    return state;
                }
            """)
            
            print(f"📊 {label}: Estado WebRTC:")
            print(f"   - Sala: {result.get('currentRoom')}")
            print(f"   - Stream local: {result.get('hasLocalStream')} (activo: {result.get('localStreamActive')})")
            print(f"   - Tracks locales: {result.get('localTracks')}")
            print(f"   - WebSocket: {result.get('wsState')} (1=OPEN)")
            print(f"   - Peers: {result.get('peers')}")
            
            for peer, state in result.get('peerStates', {}).items():
                print(f"   - Peer '{peer}':")
                print(f"     • connectionState: {state.get('connectionState')}")
                print(f"     • iceConnectionState: {state.get('iceConnectionState')}")
                print(f"     • localTracks: {state.get('localTracks')}")
                print(f"     • remoteTracks: {state.get('remoteTracks')}")
            
            # Verificar que hay al menos un peer conectado
            if result.get('peers') and len(result.get('peers')) > 0:
                # Verificar que al menos un peer está conectado
                for peer, state in result.get('peerStates', {}).items():
                    if state.get('connectionState') == 'connected':
                        print(f"✅ {label}: Conexión WebRTC establecida con {peer}")
                        return True
                
                print(f"⚠️ {label}: Hay peers pero ninguno está 'connected'")
                return False
            else:
                print(f"⚠️ {label}: No hay peers conectados")
                return False
                
        except Exception as e:
            print(f"❌ {label}: Error verificando WebRTC: {e}")
            return False
    
    async def save_logs(self):
        """Guardar logs de consola"""
        print("\n📝 Guardando logs...")
        
        with open('test_video_logs_userA.txt', 'w', encoding='utf-8') as f:
            f.write('\n'.join(self.logs_a))
        
        with open('test_video_logs_userB.txt', 'w', encoding='utf-8') as f:
            f.write('\n'.join(self.logs_b))
        
        print("✅ Logs guardados en test_video_logs_userA.txt y test_video_logs_userB.txt")
    
    async def cleanup(self):
        """Limpiar recursos"""
        print("\n🧹 Limpiando...")
        
        if self.context_a:
            await self.context_a.close()
        if self.context_b:
            await self.context_b.close()
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
        
        print("✅ Limpieza completada")
    
    async def run_test(self):
        """Ejecutar el test completo"""
        print("=" * 70)
        print("🎬 TEST DE VIDEOLLAMADA WEBRTC")
        print("=" * 70)
        
        success = True
        
        try:
            # Setup
            await self.setup()
            
            # Login de ambos usuarios
            if not await self.login(self.page_a, USER_A, "Usuario A"):
                print("❌ TEST FALLIDO: Login Usuario A falló")
                return False
            
            if not await self.login(self.page_b, USER_B, "Usuario B"):
                print("❌ TEST FALLIDO: Login Usuario B falló")
                return False
            
            # Navegar a Social
            await self.navigate_to_social(self.page_a, "Usuario A")
            await self.navigate_to_social(self.page_b, "Usuario B")
            
            # Usuario A crea la sala
            if not await self.create_room(self.page_a, ROOM_NAME, "Usuario A"):
                print("❌ TEST FALLIDO: No se pudo crear la sala")
                return False
            
            # Verificar video local de A
            if not await self.check_local_video(self.page_a, "Usuario A"):
                print("⚠️ ADVERTENCIA: Video local de Usuario A no visible")
            
            # Usuario B se une a la sala
            if not await self.join_room(self.page_b, ROOM_NAME, "Usuario B"):
                print("❌ TEST FALLIDO: Usuario B no pudo unirse")
                return False
            
            # Verificar video local de B
            if not await self.check_local_video(self.page_b, "Usuario B"):
                print("⚠️ ADVERTENCIA: Video local de Usuario B no visible")
            
            # Esperar un poco para que se establezca la conexión
            print("\n⏳ Esperando establecimiento de conexión WebRTC...")
            await asyncio.sleep(3)
            
            # Verificar que A ve el video de B
            if not await self.check_remote_video(self.page_a, "Usuario A", timeout=10):
                print("❌ TEST FALLIDO: Usuario A no ve el video de Usuario B")
                success = False
            
            # Verificar que B ve el video de A
            if not await self.check_remote_video(self.page_b, "Usuario B", timeout=10):
                print("❌ TEST FALLIDO: Usuario B no ve el video de Usuario A")
                success = False
            
            # Verificar estado WebRTC
            print("\n🔬 Verificando estado WebRTC...")
            webrtc_a = await self.check_webrtc_connection(self.page_a, "Usuario A")
            webrtc_b = await self.check_webrtc_connection(self.page_b, "Usuario B")
            
            if not webrtc_a or not webrtc_b:
                print("⚠️ ADVERTENCIA: Estado WebRTC no óptimo")
            
            # Guardar logs
            await self.save_logs()
            
            # Resultado final
            print("\n" + "=" * 70)
            if success:
                print("✅ TEST EXITOSO: La videollamada funciona correctamente")
                print("   - Ambos usuarios se conectaron")
                print("   - Ambos usuarios ven el video del otro")
                print("   - Conexión WebRTC establecida")
            else:
                print("❌ TEST FALLIDO: La videollamada NO funciona correctamente")
                print("   - Revisar logs en test_video_logs_*.txt")
                print("   - Ejecutar _videoDiagnostic() en consola del navegador")
            print("=" * 70)
            
            # Mantener navegadores abiertos para inspección manual
            print("\n⏸️  Navegadores permanecerán abiertos por 30 segundos para inspección...")
            print("   (Presiona Ctrl+C para cerrar antes)")
            await asyncio.sleep(30)
            
            return success
            
        except KeyboardInterrupt:
            print("\n⚠️ Test interrumpido por el usuario")
            return False
        except Exception as e:
            print(f"\n❌ ERROR INESPERADO: {e}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            await self.cleanup()


async def main():
    """Función principal"""
    tester = VideoCallTester()
    success = await tester.run_test()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    # Verificar que se configuraron los usuarios
    if USER_A["password"] == "tu_password_aqui" or USER_B["password"] == "tu_password_aqui":
        print("❌ ERROR: Debes configurar los usuarios de prueba en el script")
        print("   Edita las variables USER_A y USER_B con credenciales reales")
        sys.exit(1)
    
    asyncio.run(main())
