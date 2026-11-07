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
FEEDS = [
    ("https://provenance-emu.com/apps.json", {
        "com.provenance-emu.provenance",
        "com.provenance-emu.provenance.alpha",
        "com.joemattiello.iCube",
        "com.provenance.ifly",
    }),
    ("https://apps.manicemu.site/altstore", {"com.aoshuang.manicemu"}),
]
GITHUB_RELEASES = {
    "org.ppsspp.ppsspp": {
        "repo": "hrydgard/ppsspp",
        "asset": r"PPSSPP-iOS-.*\.ipa$",
    },
    "com.theboisclub.gen1recompplusplus": {
        "repo": "bryanthaboi/gen1recomp",
        "asset": r".*ios.*\.ipa$",
    },
    "com.stossy11.MeloCafe": {
        "repo": "stossy11/MeloCafe",
        "asset": r"MeloCafe\.ipa$",
    },
}
VERSION_FIELDS = (
    "version", "buildVersion", "date", "downloadURL", "size",
    "minOSVersion", "localizedDescription", "platform", "isBeta",
    "betaNumber", "marketingVersion",
)

def fetch_json(url):
    request = urllib.request.Request(url, headers={
        "User-Agent": "Alejandro-App-Source-AutoUpdater/1.0",
        "Accept": "application/json",
    })
    with urllib.request.urlopen(request, timeout=60) as response:
        return json.loads(response.read().decode("utf-8"))

def app_map(data):
    apps = data.get("apps", []) if isinstance(data, dict) else []
    return {a.get("bundleIdentifier"): a for a in apps if isinstance(a, dict) and a.get("bundleIdentifier")}

def clean_version(item):
    if not isinstance(item, dict):
        raise ValueError("La versión recibida no es un objeto.")
    result = {k: item[k] for k in VERSION_FIELDS if k in item}
    if not result.get("version") or not result.get("downloadURL"):
        raise ValueError("La versión no contiene version o downloadURL.")
    if not str(result["downloadURL"]).startswith("https://"):
        raise ValueError("La descarga no usa HTTPS.")
    if "size" in result and (not isinstance(result["size"], int) or result["size"] <= 0):
        raise ValueError("El tamaño de la descarga no es válido.")
    return result

def version_identity(v):
    return (str(v.get("version", "")), str(v.get("buildVersion", "")), str(v.get("downloadURL", "")))

def github_candidate(bundle, config, temp):
    data = fetch_json(f"https://api.github.com/repos/{config['repo']}/releases/latest")
    pattern = re.compile(config["asset"], re.I)
    asset = next((a for a in data.get("assets", []) if pattern.fullmatch(a.get("name", ""))), None)
    if not asset:
        raise ValueError("El último release estable no contiene el IPA de iOS esperado.")
    url, size = asset.get("browser_download_url", ""), asset.get("size")
    tag = str(data.get("tag_name", "")).removeprefix("v")
    if not url.startswith("https://github.com/") or not isinstance(size, int) or size <= 0 or not tag:
        raise ValueError("Metadatos del release de GitHub incompletos.")
    safe_name = re.sub(r"[^A-Za-z0-9]+", "_", bundle)
    report = inspect(safe_name, url, temp / safe_name)
    if report.get("bundleIdentifier") != bundle:
        raise ValueError(f"Bundle ID inesperado: {report.get('bundleIdentifier')!r}.")
    if not report.get("supportsIpadFamily"):
        raise ValueError("El IPA no declara soporte para iPad.")
    if report.get("size") != size:
        raise ValueError("El tamaño descargado no coincide con el asset de GitHub.")
    if str(report.get("version")) != tag:
        raise ValueError(f"La versión del IPA ({report.get('version')}) no coincide con el tag ({tag}).")
    return clean_version({
        "version": report["version"],
        "buildVersion": report["buildVersion"],
        "date": (data.get("published_at") or "")[:10],
        "downloadURL": url,
        "size": size,
        "minOSVersion": report["minOSVersion"],
    })

def merge_versions(existing, incoming):
    merged = []
    seen = set()
    for item in incoming + existing:
        version = clean_version(item)
        identity = version_identity(version)
        if identity not in seen:
            seen.add(identity)
            merged.append(version)
    return merged

def main():
    publish = os.environ.get("PUBLISH_UPDATE", "false").lower() == "true"
    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    entries = {a.get("bundleIdentifier"): a for a in source.get("apps", [])}
    incoming = {}
    errors = []
    results = []

    for url, bundles in FEEDS:
        try:
            feed_apps = app_map(fetch_json(url))
            for bundle in bundles:
                upstream = feed_apps.get(bundle)
                if not upstream:
                    raise ValueError(f"El feed {url} no contiene {bundle}.")
                versions = upstream.get("versions", [])
                if not versions:
                    raise ValueError(f"{bundle}: el feed no ofrece versiones.")
                incoming[bundle] = [clean_version(v) for v in versions]
        except Exception as exc:
            errors.append(f"Feed {url}: {exc}")

    with tempfile.TemporaryDirectory() as folder:
        temp = Path(folder)
        for bundle, config in GITHUB_RELEASES.items():
            try:
                incoming[bundle] = [github_candidate(bundle, config, temp)]
            except Exception as exc:
                errors.append(f"{bundle}: {exc}")

    changed = False
    for bundle, versions in incoming.items():
        entry = entries.get(bundle)
        if not entry:
            errors.append(f"{bundle}: la app no existe en source.json.")
            continue
        existing = entry.get("versions", [])
        merged = merge_versions(existing, versions)
        if [version_identity(v) for v in merged] != [version_identity(v) for v in existing]:
            results.append({"bundleIdentifier": bundle, "status": "UPDATE", "versions": len(merged)})
            if publish:
                entry["versions"] = merged
                changed = True
        else:
            results.append({"bundleIdentifier": bundle, "status": "UP TO DATE", "versions": len(existing)})

    report = {"published": publish, "changed": changed, "results": results, "errors": errors}
    rendered = json.dumps(report, ensure_ascii=False, indent=2)
    print(rendered)
    summary = Path(os.environ.get("GITHUB_STEP_SUMMARY", "/tmp/summary.md"))
    summary.write_text("# Sincronización automática del catálogo\n\n\x60\x60\x60json\n" + rendered + "\n\x60\x60\x60\n", encoding="utf-8")
    output = Path(os.environ.get("GITHUB_OUTPUT", "/tmp/github-output"))
    with output.open("a", encoding="utf-8") as stream:
        stream.write(f"changed={str(changed).lower()}\n")
    if errors:
        raise SystemExit("Hubo errores; se conservaron los datos existentes de las apps afectadas.")
    if publish and changed:
        rendered_source = json.dumps(source, ensure_ascii=False, indent=2) + "\n"
        json.loads(rendered_source)
        temporary = SOURCE.with_name(SOURCE.name + ".tmp")
        temporary.write_text(rendered_source, encoding="utf-8")
        temporary.replace(SOURCE)

if __name__ == "__main__":
    main()
