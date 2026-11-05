import datetime
import json
import os
import plistlib
import subprocess
import tempfile
import urllib.request
import zipfile
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "source.json"
IGNORED_ENTITLEMENTS = {"application-identifier", "com.apple.developer.team-identifier"}


def fail(message):
    raise SystemExit("ERROR: " + message)


def plist_from_codesign(bundle_path):
    result = subprocess.run(
        ["codesign", "-d", "--entitlements", ":-", str(bundle_path)],
        capture_output=True,
    )
    output = result.stdout + b"\n" + result.stderr
    if result.returncode != 0:
        fail(f"No se pudieron verificar los entitlements de {bundle_path.name}. El catálogo no se ha modificado.")
    # codesign may prepend a diagnostic line before the XML plist.
    starts = [position for marker in (b"<?xml", b"<plist") if (position := output.find(marker)) >= 0]
    if not starts:
        # A valid signed binary may have no entitlements.
        return {}
    start = min(starts)
    end = output.find(b"</plist>", start)
    if end < 0:
        fail(f"codesign devolvió entitlements incompletos para {bundle_path.name}.")
    try:
        value = plistlib.loads(output[start:end + len(b"</plist>")])
    except Exception as exc:
        fail(f"No se pudieron interpretar los entitlements de {bundle_path.name}: {exc}")
    if not isinstance(value, dict):
        fail(f"Entitlements inesperados en {bundle_path.name}.")
    return value


def app_roots(archive, main_info):
    app_root = main_info[:-len("Info.plist")]
    roots = [app_root]
    seen = {app_root}
    for name in archive.namelist():
        if ".appex/Info.plist" in name:
            root = name[:name.index("Info.plist")]
            if root not in seen:
                roots.append(root)
                seen.add(root)
    return roots


def main():
    assets = json.loads(os.environ["RELEASE_ASSETS"])
    ipas = [asset for asset in assets if asset.get("name", "").lower().endswith(".ipa")]
    if len(ipas) != 1:
        fail("El Release debe contener exactamente un archivo .ipa.")
    asset = ipas[0]
    download_url = asset.get("browser_download_url", "")
    if not download_url.startswith("https://github.com/") or not isinstance(asset.get("size"), int) or asset["size"] <= 0:
        fail("El IPA no tiene una descarga pública HTTPS o un tamaño válido.")

    with tempfile.TemporaryDirectory() as temp:
        ipa = Path(temp) / "app.ipa"
        request = urllib.request.Request(download_url, headers={"User-Agent": "AltStore-source-builder"})
        with urllib.request.urlopen(request, timeout=180) as response, ipa.open("wb") as output:
            output.write(response.read())
            final_host = response.geturl().split("/", 3)[2].lower()
        if final_host != "github.com" and not final_host.endswith(".githubusercontent.com"):
            fail("La descarga del IPA redirigió a un host inesperado.")
        if ipa.stat().st_size != asset["size"]:
            fail("El tamaño descargado no coincide con el tamaño anunciado por GitHub.")

        try:
            with zipfile.ZipFile(ipa) as archive:
                names = archive.namelist()
                main_infos = [name for name in names if name.startswith("Payload/") and name.endswith(".app/Info.plist") and name.count("/") == 2]
                if len(main_infos) != 1:
                    fail("El IPA debe contener exactamente una app principal dentro de Payload.")
                main_info_path = main_infos[0]
                info = plistlib.loads(archive.read(main_info_path))
                privacy = {}
                entitlements = set()
                roots = app_roots(archive, main_info_path)
                for root in roots:
                    info_path = root + "Info.plist"
                    if info_path not in names:
                        fail(f"Falta Info.plist en el bundle {root}.")
                    bundle_info = plistlib.loads(archive.read(info_path))
                    for key, value in bundle_info.items():
                        if key.endswith("UsageDescription") and isinstance(value, str):
                            privacy[key] = value
                    bundle_path = Path(temp) / PurePosixPath(root)
                    bundle_path.parent.mkdir(parents=True, exist_ok=True)
                    # Extract only this signed bundle; never extract archive paths outside the temporary directory.
                    for member in names:
                        if member.startswith(root):
                            target = Path(temp) / PurePosixPath(member)
                            if member.endswith("/"):
                                target.mkdir(parents=True, exist_ok=True)
                            else:
                                target.parent.mkdir(parents=True, exist_ok=True)
                                target.write_bytes(archive.read(member))
                    signed = plist_from_codesign(bundle_path)
                    entitlements.update(key for key in signed if key not in IGNORED_ENTITLEMENTS)
        except (zipfile.BadZipFile, KeyError, plistlib.InvalidFileException) as exc:
            fail("El IPA está dañado o sus Info.plist no se pueden leer: " + str(exc))

    bundle = info.get("CFBundleIdentifier")
    version = info.get("CFBundleShortVersionString")
    build = info.get("CFBundleVersion")
    minimum = info.get("MinimumOSVersion")
    if not all(isinstance(value, str) and value.strip() for value in (bundle, version, build, minimum)):
        fail("Faltan Bundle ID, versión, compilación o MinimumOSVersion en la app principal.")
    name = os.environ.get("RELEASE_NAME", "").strip()
    description = os.environ.get("RELEASE_BODY", "").strip()
    if not name or not description:
        fail("Escribe el nombre en el título del Release y la descripción en su texto.")

    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    apps = source.setdefault("apps", [])
    ids = [app.get("bundleIdentifier") for app in apps]
    if len(ids) != len(set(ids)):
        fail("source.json ya contiene Bundle ID duplicados. No se ha modificado.")
    matches = [app for app in apps if app.get("bundleIdentifier") == bundle]
    if len(matches) > 1:
        fail("La fuente contiene más de una entrada para este Bundle ID. No se ha modificado.")
    entry = matches[0] if matches else {
        "bundleIdentifier": bundle,
        "versions": [],
    }
    entry.update({
        "name": name,
        "bundleIdentifier": bundle,
        "developerName": info.get("CFBundleName", name),
        "localizedDescription": description,
        "appPermissions": {
            "entitlements": sorted(entitlements),
            "privacy": dict(sorted(privacy.items())),
        },
        "versions": [{
            "version": version,
            "buildVersion": build,
            "date": datetime.date.today().isoformat(),
            "downloadURL": download_url,
            "size": asset["size"],
            "minOSVersion": minimum,
        }],
    })
    if not matches:
        apps.append(entry)

    # Validate the complete result before touching source.json.
    final_ids = [app.get("bundleIdentifier") for app in apps]
    if len(final_ids) != len(set(final_ids)):
        fail("La actualización produciría Bundle ID duplicados; source.json no se ha modificado.")
    rendered = json.dumps(source, ensure_ascii=False, indent=2) + "\n"
    json.loads(rendered)
    SOURCE.write_text(rendered, encoding="utf-8")
    print(f"IPA verificado con codesign: {bundle} {version} ({build}); entitlements y privacidad de app/extensiones incorporados.")


if __name__ == "__main__":
    main()
