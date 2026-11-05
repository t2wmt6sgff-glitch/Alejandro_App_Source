import datetime
import os
import json
import plistlib
import re
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


def signed_entitlements(bundle_path):
    result = subprocess.run(
        ["codesign", "-d", "--entitlements", ":-", str(bundle_path)],
        capture_output=True,
    )
    output = result.stdout + b"\n" + result.stderr
    if result.returncode != 0:
        fail(f"No se pudo verificar la firma de {bundle_path.name}; catálogo sin cambios.")
    starts = [pos for marker in (b"<?xml", b"<plist") if (pos := output.find(marker)) >= 0]
    if not starts:
        return {}
    start = min(starts)
    end = output.find(b"</plist>", start)
    if end < 0:
        fail(f"Entitlements incompletos en {bundle_path.name}.")
    value = plistlib.loads(output[start:end + len(b"</plist>")])
    if not isinstance(value, dict):
        fail(f"Entitlements no válidos en {bundle_path.name}.")
    return value


def inspect_ipa(ipa_path, extraction_root):
    with zipfile.ZipFile(ipa_path) as archive:
        damaged_member = archive.testzip()
        if damaged_member is not None:
            fail(f"El IPA está dañado (fallo de integridad en {damaged_member}); catálogo sin cambios.")
        names = archive.namelist()
        main_infos = [
            path for path in names
            if path.startswith("Payload/") and path.endswith(".app/Info.plist") and path.count("/") == 2
        ]
        if len(main_infos) != 1:
            fail("El IPA debe contener una sola app principal en Payload.")
        main_info_path = main_infos[0]
        main_info = plistlib.loads(archive.read(main_info_path))
        main_root = main_info_path[:-len("Info.plist")]
        roots = [main_root]
        for path in names:
            if ".appex/Info.plist" in path:
                root = path[:path.index("Info.plist")]
                if root not in roots:
                    roots.append(root)

        privacy = {}
        entitlements = set()
        app_path = None
        for root in roots:
            posix_root = PurePosixPath(root)
            bundle_path = extraction_root.joinpath(*posix_root.parts)
            bundle_resolved = bundle_path.resolve()
            for member in names:
                if not member.startswith(root):
                    continue
                relative = PurePosixPath(member)
                target = extraction_root.joinpath(*relative.parts)
                if not target.resolve().is_relative_to(bundle_resolved):
                    fail("Ruta insegura dentro del IPA; no se extrajo ningún dato.")
                if member.endswith("/"):
                    target.mkdir(parents=True, exist_ok=True)
                else:
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_bytes(archive.read(member))
            info_path = root + "Info.plist"
            if info_path not in names:
                fail(f"Falta Info.plist en {root}.")
            bundle_info = plistlib.loads(archive.read(info_path))
            for key, value in bundle_info.items():
                if key.endswith("UsageDescription") and isinstance(value, str):
                    if key in privacy and privacy[key] != value:
                        fail(f"Descripción de privacidad contradictoria para {key}; catálogo sin cambios.")
                    privacy[key] = value
            if root == main_root:
                app_path = bundle_path
            for key in signed_entitlements(bundle_path):
                if key not in IGNORED_ENTITLEMENTS:
                    entitlements.add(key)

        if app_path is None:
            fail("No se encontró la app principal.")
        icon = primary_icon(archive, names, main_root, main_info)
        return {
            "info": main_info,
            "entitlements": sorted(entitlements),
            "privacy": dict(sorted(privacy.items())),
            "icon": icon,
        }


def primary_icon(archive, names, app_root, info):
    icons = info.get("CFBundleIcons", {}).get("CFBundlePrimaryIcon", {}).get("CFBundleIconFiles", [])
    for stem in icons:
        possible = [
            app_root + stem + "@2x~ipad.png",
            app_root + stem + "@3x.png",
            app_root + stem + "@2x.png",
            app_root + stem + ".png",
        ]
        for candidate in possible:
            if candidate in names:
                data = archive.read(candidate)
                if data.startswith(b"\x89PNG\r\n\x1a\n"):
                    return data
    fail("No se encontró el icono PNG principal dentro del IPA.")


def main():
    event = json.loads(Path(os.environ["RELEASE_JSON"]).read_text(encoding="utf-8"))
    assets = event.get("assets", [])
    ipas = [asset for asset in assets if asset.get("name", "").lower().endswith(".ipa")]
    if len(ipas) != 1:
        fail("El Release debe contener exactamente un archivo .ipa.")
    asset = ipas[0]
    download_url = asset.get("browser_download_url", "")
    if not download_url.startswith("https://github.com/") or not isinstance(asset.get("size"), int) or asset["size"] <= 0:
        fail("El IPA no tiene una URL pública HTTPS o un tamaño válido.")

    with tempfile.TemporaryDirectory() as temp:
        temp_root = Path(temp)
        ipa_path = temp_root / "app.ipa"
        request = urllib.request.Request(download_url, headers={"User-Agent": "AltStore-source-builder"})
        with urllib.request.urlopen(request, timeout=180) as response, ipa_path.open("wb") as output:
            output.write(response.read())
            final_host = response.geturl().split("/", 3)[2].lower()
        if final_host != "github.com" and not final_host.endswith(".githubusercontent.com"):
            fail("La descarga redirigió a un host inesperado.")
        if ipa_path.stat().st_size != asset["size"]:
            fail("El tamaño descargado no coincide con GitHub.")
        metadata = inspect_ipa(ipa_path, temp_root / "expanded")

    info = metadata["info"]
    bundle, version, build, minimum = (
        info.get("CFBundleIdentifier"),
        info.get("CFBundleShortVersionString"),
        info.get("CFBundleVersion"),
        info.get("MinimumOSVersion"),
    )
    if not re.fullmatch(r"[A-Za-z0-9.-]+", str(bundle or "")):
        fail("Bundle ID ausente o con formato no admitido.")
    if not all(isinstance(value, str) and value.strip() for value in (version, build, minimum)):
        fail("Faltan versión, build o MinimumOSVersion.")
    if 2 not in info.get("UIDeviceFamily", []):
        fail("El IPA no declara compatibilidad con iPad; catálogo sin cambios.")
    name = (event.get("name") or "").strip()
    description = (event.get("body") or "").strip()
    if not name or not description:
        fail("Escribe el nombre en el título del Release y la descripción en su texto.")

    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    apps = source.setdefault("apps", [])
    ids = [app.get("bundleIdentifier") for app in apps]
    if len(ids) != len(set(ids)):
        fail("source.json contiene Bundle ID duplicados; no se ha modificado.")
    matches = [app for app in apps if app.get("bundleIdentifier") == bundle]
    if len(matches) > 1:
        fail("Hay más de una entrada para el Bundle ID; no se ha modificado.")

    icon_dir = ROOT / "icons"
    icon_dir.mkdir(exist_ok=True)
    (icon_dir / f"{bundle}.png").write_bytes(metadata["icon"])
    entry = matches[0] if matches else {"bundleIdentifier": bundle}
    entry.update({
        "name": name,
        "bundleIdentifier": bundle,
        "developerName": info.get("CFBundleName", name),
        "localizedDescription": description,
        "iconURL": f"https://raw.githubusercontent.com/{os.environ['GITHUB_REPOSITORY']}/main/icons/{bundle}.png",
        "appPermissions": {
            "entitlements": metadata["entitlements"],
            "privacy": metadata["privacy"],
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
    final_ids = [app.get("bundleIdentifier") for app in apps]
    if len(final_ids) != len(set(final_ids)):
        fail("La actualización produciría duplicados; source.json no se ha modificado.")
    rendered = json.dumps(source, ensure_ascii=False, indent=2) + "\n"
    json.loads(rendered)
    temporary_source = SOURCE.with_name(SOURCE.name + ".tmp")
    try:
        with temporary_source.open("w", encoding="utf-8") as output:
            output.write(rendered)
            output.flush()
            os.fsync(output.fileno())
        temporary_source.replace(SOURCE)
    finally:
        if temporary_source.exists():
            temporary_source.unlink()
    print(f"Verificado con codesign: {bundle} {version} ({build}); permisos de app y extensiones incorporados.")


if __name__ == "__main__":
    main()
