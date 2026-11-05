import json
import os
import re
import tempfile
import urllib.request
from pathlib import Path

try:
    from .audit_official import inspect
except ImportError:
    from audit_official import inspect

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "source.json"
OFFICIAL = {
    "PPSSPP": {
        "bundle": "org.ppsspp.ppsspp",
        "kind": "github",
        "url": "https://api.github.com/repos/hrydgard/ppsspp/releases/latest",
        "asset": "PPSSPP-iOS-.*\\.ipa$",
    },
}


def fetch_json(url):
    request = urllib.request.Request(url, headers={"User-Agent": "Alejandro-App-Source-update-check"})
    with urllib.request.urlopen(request, timeout=45) as response:
        return json.loads(response.read())


def resolve_latest(name):
    config = OFFICIAL[name]
    data = fetch_json(config["url"])
    assets = data.get("assets", [])
    asset = next((item for item in assets if re.fullmatch(config["asset"], item.get("name", ""), re.I)), None)
    if not asset:
        raise ValueError("El último release oficial no incluye el IPA esperado para iOS.")
    url = asset.get("browser_download_url", "")
    size = asset.get("size")
    release_date = data.get("published_at", "")
    label = data.get("tag_name", "").removeprefix("v")
    if not url.startswith("https://github.com/") or not isinstance(size, int) or size <= 0 or not release_date or not label:
        raise ValueError("El enlace, tamaño, fecha o versión de la descarga oficial no es válido.")
    return {"url": url, "size": size, "date": release_date[:10], "label": label}


def version_tuple(value):
    match = re.fullmatch(r"v?(\d+(?:\.\d+)*)(?:[-+].*)?", str(value or ""))
    if not match:
        raise ValueError(f"Formato de versión no reconocido: {value!r}.")
    return tuple(int(part) for part in match.group(1).split("."))


def write_source_atomically(source):
    rendered = json.dumps(source, ensure_ascii=False, indent=2) + chr(10)
    json.loads(rendered)
    temporary = SOURCE.with_name(SOURCE.name + ".tmp")
    try:
        with temporary.open("w", encoding="utf-8") as output:
            output.write(rendered)
            output.flush()
            os.fsync(output.fileno())
        temporary.replace(SOURCE)
    finally:
        if temporary.exists():
            temporary.unlink()


def main():
    requested = os.environ.get("APP_SELECTION", "all")
    publish = os.environ.get("PUBLISH_UPDATE", "false").lower() == "true"
    names = list(OFFICIAL) if requested in ("", "all") else [requested]
    if any(name not in OFFICIAL for name in names):
        raise SystemExit("ERROR: elige PPSSPP o Todas las aplicaciones del catálogo.")
    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    results = []
    changed = False
    with tempfile.TemporaryDirectory() as folder:
        temp = Path(folder)
        for name in names:
            config = OFFICIAL[name]
            entries = [app for app in source.get("apps", []) if app.get("bundleIdentifier") == config["bundle"]]
            if len(entries) != 1:
                results.append({"app": name, "status": "ERROR", "detail": "La app ya no está en el catálogo o hay entradas duplicadas."})
                continue
            entry = entries[0]
            current = entry.get("versions", [{}])[0].get("version")
            try:
                candidate = resolve_latest(name)
                comparison = (version_tuple(candidate["label"]) > version_tuple(current)) - (version_tuple(candidate["label"]) < version_tuple(current))
                if comparison < 0:
                    raise ValueError("El release oficial es más antiguo que la versión del catálogo; no se permite retroceder.")
                if comparison == 0:
                    results.append({"app": name, "status": "AL DÍA", "version": current, "url": candidate["url"]})
                    continue
                report = inspect(name, candidate["url"], temp / name)
                if report.get("bundleIdentifier") != config["bundle"]:
                    raise ValueError("El Bundle ID del IPA no coincide con el proyecto.")
                if not report.get("supportsIpadFamily"):
                    raise ValueError("El IPA no declara soporte para iPad.")
                if report.get("size") != candidate["size"]:
                    raise ValueError("El tamaño del IPA no coincide con la fuente oficial.")
                if version_tuple(report.get("version")) != version_tuple(candidate["label"]):
                    raise ValueError("La versión declarada dentro del IPA no coincide con el release.")
                result = {
                    "app": name, "status": "NUEVO IPA OFICIAL VERIFICADO",
                    "version": report["version"], "buildVersion": report["buildVersion"],
                    "minOSVersion": report["minOSVersion"], "sha256": report["sha256"],
                    "url": candidate["url"], "entitlements": report["entitlements"], "privacy": report["privacy"],
                }
                if publish:
                    entry["appPermissions"] = {"entitlements": report["entitlements"], "privacy": report["privacy"]}
                    entry["versions"] = [{
                        "version": report["version"], "buildVersion": report["buildVersion"],
                        "date": candidate["date"], "downloadURL": candidate["url"],
                        "size": report["size"], "minOSVersion": report["minOSVersion"],
                    }]
                    changed = True
                    result["status"] = "PUBLICADO TRAS VERIFICACIÓN"
                results.append(result)
            except Exception as exc:
                results.append({"app": name, "status": "NO VERIFICADO", "detail": str(exc)})
    output = json.dumps(results, ensure_ascii=False, indent=2)
    print(output)
    Path(os.environ["GITHUB_STEP_SUMMARY"]).write_text("# Comprobación oficial de actualizaciones\n\n" + output + "\n", encoding="utf-8")
    with Path(os.environ["GITHUB_OUTPUT"]).open("a", encoding="utf-8") as stream:
        stream.write(f"changed={str(changed).lower()}\n")
    if any(item["status"] in ("ERROR", "NO VERIFICADO") for item in results):
        raise SystemExit("No se modificó el catálogo para las apps que no pudieron verificarse.")
    if publish and changed:
        write_source_atomically(source)


if __name__ == "__main__":
    main()
