# Script simple para ejecutar la generación
import subprocess
import sys

resultado = subprocess.run(
    [sys.executable, r"c:\dvdcoin\generar_preguntas_pasapalabra.py"],
    capture_output=True,
    text=True,
    timeout=30
)

print(resultado.stdout)
if resultado.stderr:
    print("ERRORES:", resultado.stderr)
print("Código de salida:", resultado.returncode)
