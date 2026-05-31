"""
Script para corregir el meta de anuncios existentes que no tienen creator/created_at.
Específicamente: "BUSCO AMANTE BANDIDO" publicado por yumazurman el 31/05/2026 a las 13:30.

Ejecutar una sola vez en el servidor:
    python fix_anuncio_meta.py
"""
import json
import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
META_PATH = os.path.join(BASE_DIR, "static", "anuncios", ".meta.json")
ANUNCIOS_DIR = os.path.join(BASE_DIR, "static", "anuncios")


def load_meta():
    try:
        if os.path.exists(META_PATH):
            with open(META_PATH, encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    return {"masked": [], "enabled": False}


def save_meta(meta):
    os.makedirs(ANUNCIOS_DIR, exist_ok=True)
    with open(META_PATH, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)


def main():
    meta = load_meta()

    # List all announcement files
    if not os.path.exists(ANUNCIOS_DIR):
        print("No existe el directorio de anuncios:", ANUNCIOS_DIR)
        return

    supported = {".docx", ".odt", ".txt"}
    files = [f for f in os.listdir(ANUNCIOS_DIR)
             if os.path.splitext(f)[1].lower() in supported
             and not f.startswith("~") and not f.startswith(".")]

    if not files:
        print("No hay anuncios publicados.")
        return

    print(f"Anuncios encontrados: {len(files)}")
    for f in files:
        print(f"  - {f}")

    # Ensure creators and created_at dicts exist
    if "creators" not in meta:
        meta["creators"] = {}
    if "created_at" not in meta:
        meta["created_at"] = {}

    # Fix: assign yumazurman as creator and 2026-05-31 13:30 as date
    # for any file that doesn't have a creator yet
    for f in files:
        if f not in meta["creators"]:
            meta["creators"][f] = "yumazurman"
            print(f"  -> Asignado creator 'yumazurman' a: {f}")
        if f not in meta["created_at"]:
            meta["created_at"][f] = "2026-05-31 13:30"
            print(f"  -> Asignado created_at '2026-05-31 13:30' a: {f}")

    save_meta(meta)
    print("\n OK Meta actualizado correctamente:")
    print(json.dumps(meta, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
