import hashlib
import json
import plistlib
import subprocess
import tempfile
import urllib.request
import zipfile
from pathlib import Path, PurePosixPath

APPS = [
    ("PPSSPP", "https://github.com/hrydgard/ppsspp/releases/download/v1.20.4/PPSSPP-iOS-v1.20.4.ipa"),
]
IGNORED = {"application-identifier", "com.apple.developer.team-identifier"}


def inspect(name, url, temp):
    temp.mkdir(parents=True, exist_ok=True)
    request = urllib.request.Request(url, headers={"User-Agent": "AltStore-source-official-audit"})
    ipa = temp / (name.replace(" ", "_") + ".ipa")
    with urllib.request.urlopen(request, timeout=240) as response, ipa.open("wb") as output:
        output.write(response.read())
        final_host = response.geturl().split("/", 3)[2].lower()
    if final_host != "github.com" and not final_host.endswith(".githubusercontent.com") and not final_host.endswith(".altstore.io"):
        raise ValueError("descarga redirigida a un dominio inesperado")
    digest = hashlib.sha256(ipa.read_bytes()).hexdigest()
    with zipfile.ZipFile(ipa) as archive:
        damaged_member = archive.testzip()
        if damaged_member is not None:
            raise ValueError(f"archivo IPA dañado: fallo CRC en {damaged_member}")
        names = archive.namelist()
        main = [p for p in names if p.startswith("Payload/") and p.endswith(".app/Info.plist") and p.count("/") == 2]
        if len(main) != 1:
            raise ValueError("no hay exactamente una app principal en Payload")
        root = main[0][:-len("Info.plist")]
        info = plistlib.loads(archive.read(main[0]))
        roots = [root]
        for p in names:
            if ".appex/Info.plist" in p:
                extroot = p[:p.index("Info.plist")]
                if extroot not in roots:
                    roots.append(extroot)
        privacy, entitlements = {}, set()
        for bundle_root in roots:
            bundle_path = temp.joinpath(*PurePosixPath(bundle_root).parts)
            bundle_resolved = bundle_path.resolve()
            for member in names:
                if member.startswith(bundle_root):
                    target = temp.joinpath(*PurePosixPath(member).parts)
                    if not target.resolve().is_relative_to(bundle_resolved):
                        raise ValueError("ruta insegura en el IPA")
                    if member.endswith("/"):
                        target.mkdir(parents=True, exist_ok=True)
                    else:
                        target.parent.mkdir(parents=True, exist_ok=True)
                        target.write_bytes(archive.read(member))
            plist_path = bundle_root + "Info.plist"
            bundle_info = plistlib.loads(archive.read(plist_path))
            for key, value in bundle_info.items():
                if key.endswith("UsageDescription") and isinstance(value, str):
                    if key in privacy and privacy[key] != value:
                        raise ValueError(f"descripciones de privacidad contradictorias para {key}")
                    privacy[key] = value
            result = subprocess.run(["codesign", "-d", "--entitlements", ":-", str(bundle_path)], capture_output=True)
            output = result.stdout + b"\n" + result.stderr
            if result.returncode:
                raise ValueError(f"codesign no pudo verificar firma de {bundle_root}")
            plist_starts = [n for marker in (b"<?xml", b"<plist") if (n := output.find(marker)) >= 0]
            if plist_starts:
                start = min(plist_starts)
                end = output.find(b"</plist>", start)
                if end < 0:
                    raise ValueError("plist de entitlements incompleto")
                values = plistlib.loads(output[start:end + len(b"</plist>")])
                entitlements.update(k for k in values if k not in IGNORED)
        family = info.get("UIDeviceFamily", [])
        return {
            "name": name, "url": url, "sha256": digest, "size": ipa.stat().st_size,
            "bundleIdentifier": info.get("CFBundleIdentifier"),
            "version": info.get("CFBundleShortVersionString"),
            "buildVersion": info.get("CFBundleVersion"),
            "minOSVersion": info.get("MinimumOSVersion"),
            "supportsIpadFamily": 2 in family,
            "ipadOS26RuntimeVerified": False,
            "entitlements": sorted(entitlements),
            "privacy": dict(sorted(privacy.items())),
        }


def main():
    results = []
    with tempfile.TemporaryDirectory() as folder:
        temp = Path(folder)
        for name, url in APPS:
            try:
                results.append({"status": "VERIFIED IPA AND SIGNED PERMISSIONS", **inspect(name, url, temp / name.replace(" ", "_"))})
            except Exception as exc:
                results.append({"name": name, "url": url, "status": "NOT VERIFIED", "error": str(exc)})
    report = json.dumps(results, ensure_ascii=False, indent=2)
    print(report)
    summary = Path(__import__("os").environ["GITHUB_STEP_SUMMARY"])
    summary.write_text("# Auditoría de IPA oficiales\n\n" + report + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
