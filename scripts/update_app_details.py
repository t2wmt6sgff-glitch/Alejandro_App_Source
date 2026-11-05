import json
import os
from pathlib import Path
import sys

SOURCE = Path(__file__).resolve().parents[1] / "source.json"


def main():
    if len(sys.argv) != 4:
        raise SystemExit("Uso interno: nombre actual, nombre nuevo y descripción nueva.")
    current_name, new_name, new_description = (value.strip() for value in sys.argv[1:])
    if not current_name or not new_name or not new_description:
        raise SystemExit("ERROR: completa el nombre actual, el nombre nuevo y la descripción.")
    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    apps = source.get("apps", [])
    matches = [app for app in apps if app.get("name") == current_name]
    if len(matches) != 1:
        raise SystemExit("ERROR: debe existir exactamente una app con ese nombre. Comprueba el nombre actual en la fuente.")
    entry = matches[0]
    if not entry.get("bundleIdentifier"):
        raise SystemExit("ERROR: la entrada no tiene Bundle ID y no se ha modificado.")
    if any(app is not entry and app.get("bundleIdentifier") == entry["bundleIdentifier"] for app in apps):
        raise SystemExit("ERROR: hay Bundle ID duplicados; no se ha modificado el catálogo.")
    entry["name"] = new_name
    entry["localizedDescription"] = new_description
    SOURCE.write_text(json.dumps(source, ensure_ascii=False, indent=2) + "\\n", encoding="utf-8")
    print("Nombre y descripción actualizados. Bundle ID conservado:", entry["bundleIdentifier"])


if __name__ == "__main__":
    main()
