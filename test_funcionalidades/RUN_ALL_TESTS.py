#!/usr/bin/env python3
"""
🧪 EJECUTAR TODOS LOS TESTS
Script principal que ejecuta todos los tests funcionales
"""
import os
import sys
import subprocess
import time
from pathlib import Path
from datetime import datetime
import json

def print_header(text):
    """Imprimir encabezado"""
    print("\n" + "=" * 80)
    print(f"  {text}")
    print("=" * 80 + "\n")

def print_section(text):
    """Imprimir sección"""
    print("\n" + "-" * 80)
    print(f"  {text}")
    print("-" * 80)

def run_test(test_path, test_name):
    """Ejecutar un test individual"""
    print(f"\n🧪 Ejecutando: {test_name}...")
    
    try:
        result = subprocess.run(
            [sys.executable, test_path],
            capture_output=True,
            text=True,
            timeout=300  # 5 minutos máximo por test
        )
        
        success = result.returncode == 0
        
        if success:
            print(f"✅ {test_name}: EXITOSO")
        else:
            print(f"❌ {test_name}: FALLIDO")
            # Mostrar las primeras líneas del error para diagnóstico
            if result.stdout:
                lines = result.stdout.split('\n')
                error_lines = [l for l in lines if 'ERROR' in l or 'FAIL' in l or '❌' in l]
                if error_lines:
                    print(f"   Errores detectados:")
                    for line in error_lines[:3]:  # Mostrar máximo 3 líneas de error
                        print(f"   {line[:100]}")
        
        return success, result.stdout, result.stderr
    
    except subprocess.TimeoutExpired:
        print(f"⏱️  {test_name}: TIMEOUT (>5 min)")
        return False, "", "Timeout"
    
    except Exception as e:
        print(f"💥 {test_name}: ERROR - {str(e)}")
        return False, "", str(e)

def main():
    """Función principal"""
    print_header("🧪 SUITE DE TESTS FUNCIONALES - DVDcoin Bank")
    
    start_time = datetime.now()
    
    # Directorio base
    base_dir = Path(__file__).parent
    
    # Lista de tests a ejecutar
    tests = [
        ("15_autenticacion/test_autenticacion.py", "Autenticación y Sesiones"),
        ("01_transferencias/test_transferencias.py", "Transferencias"),
        ("02_opo/test_opo.py", "OPO (Oposiciones)"),
        ("03_millonario/test_millonario.py", "Millonario"),
        ("04_video/test_video.py", "Video (WebRTC)"),
        ("05_cifras_letras/test_cifras_letras.py", "Cifras y Letras"),
        ("06_pasapalabra/test_pasapalabra.py", "Pasapalabra"),
        ("07_hundir_flota/test_hundir_flota.py", "Hundir la Flota"),
        ("08_mensajes/test_mensajes.py", "Mensajes"),
        ("09_apuestas/test_apuestas.py", "Apuestas"),
        ("10_votaciones/test_votaciones.py", "Votaciones"),
        ("11_cuentos/test_cuentos.py", "Cuentos"),
        ("12_quien_soy/test_quien_soy.py", "¿Quién Soy?"),
        ("13_admin/test_admin.py", "Administración"),
        ("14_galeria/test_galeria.py", "Galería"),
    ]
    
    results = []
    
    print_section("Ejecutando Tests")
    
    for i, (test_file, test_name) in enumerate(tests, 1):
        test_path = base_dir / test_file
        
        if not test_path.exists():
            print(f"⚠️  {test_name}: ARCHIVO NO ENCONTRADO - {test_file}")
            results.append((test_name, False, "No encontrado"))
            continue
        
        success, stdout, stderr = run_test(test_path, test_name)
        results.append((test_name, success, stdout if success else stderr))
        
        # Pequeño delay entre tests para evitar sobrecarga
        if i < len(tests):  # No esperar después del último test
            time.sleep(2)  # 2 segundos entre tests
    
    # Resumen final
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    print_header("📊 RESUMEN FINAL")
    
    total_tests = len(results)
    passed_tests = sum(1 for _, success, _ in results if success)
    failed_tests = total_tests - passed_tests
    success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
    
    print(f"Total de tests:     {total_tests}")
    print(f"✅ Tests exitosos:  {passed_tests}")
    print(f"❌ Tests fallidos:  {failed_tests}")
    print(f"📈 Tasa de éxito:   {success_rate:.1f}%")
    print(f"⏱️  Tiempo total:    {duration:.1f}s")
    
    print("\n" + "-" * 80)
    print("Detalle por test:")
    print("-" * 80)
    
    for test_name, success, _ in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"  {status}  {test_name}")
    
    # Guardar resumen en JSON
    summary_file = base_dir / "logs" / f"test_summary_{start_time.strftime('%Y-%m-%d_%H-%M-%S')}.json"
    summary_file.parent.mkdir(exist_ok=True)
    
    summary_data = {
        "timestamp": start_time.isoformat(),
        "duration_seconds": duration,
        "total_tests": total_tests,
        "passed": passed_tests,
        "failed": failed_tests,
        "success_rate": success_rate,
        "results": [
            {
                "name": name,
                "success": success,
                "output": output[:1000] if output else ""
            }
            for name, success, output in results
        ]
    }
    
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n📄 Resumen guardado en: {summary_file}")
    
    print("\n" + "=" * 80)
    
    # Retornar código de salida
    sys.exit(0 if failed_tests == 0 else 1)

if __name__ == "__main__":
    main()
