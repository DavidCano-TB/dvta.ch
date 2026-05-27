import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
APUESTAS_DIR = os.path.join(BASE_DIR, "game_pages", "apuestas")
VOTACIONES_DIR = os.path.join(BASE_DIR, "game_pages", "votaciones")

print("BASE_DIR:", BASE_DIR)
print("APUESTAS_DIR:", APUESTAS_DIR)
print("VOTACIONES_DIR:", VOTACIONES_DIR)
print()

apuestas_path = os.path.join(APUESTAS_DIR, "apuestas.html")
votaciones_path = os.path.join(VOTACIONES_DIR, "votaciones.html")

print("Apuestas path:", apuestas_path)
print("Apuestas exists:", os.path.exists(apuestas_path))
print()
print("Votaciones path:", votaciones_path)
print("Votaciones exists:", os.path.exists(votaciones_path))
print()

# Listar contenido de los directorios
if os.path.exists(APUESTAS_DIR):
    print("Contenido de APUESTAS_DIR:")
    for item in os.listdir(APUESTAS_DIR):
        print(f"  - {item}")
else:
    print("APUESTAS_DIR no existe!")

print()

if os.path.exists(VOTACIONES_DIR):
    print("Contenido de VOTACIONES_DIR:")
    for item in os.listdir(VOTACIONES_DIR):
        print(f"  - {item}")
else:
    print("VOTACIONES_DIR no existe!")
