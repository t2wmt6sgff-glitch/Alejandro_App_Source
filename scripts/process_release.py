import datetime, json, os, plistlib, tempfile, urllib.request, zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'source.json'

def fail(message):
    raise SystemExit('ERROR: ' + message)

def main():
    assets = json.loads(os.environ['RELEASE_ASSETS'])
    ipas = [a for a in assets if a.get('name', '').lower().endswith('.ipa')]
    if len(ipas) != 1:
        fail('El Release debe contener exactamente un archivo .ipa.')
    asset = ipas[0]
    url = asset.get('browser_download_url', '')
    if not url.startswith('https://github.com/') or not asset.get('size'):
        fail('El IPA no tiene una URL pública o un tamaño válido.')
    with tempfile.TemporaryDirectory() as folder:
        ipa = Path(folder) / 'app.ipa'
        request = urllib.request.Request(url, headers={'User-Agent': 'AltStore-source-builder'})
        with urllib.request.urlopen(request, timeout=180) as response, ipa.open('wb') as output:
            output.write(response.read())
        if ipa.stat().st_size != asset['size']:
            fail('El tamaño descargado no coincide con el de GitHub.')
        try:
            with zipfile.ZipFile(ipa) as archive:
                infos = [n for n in archive.namelist() if n.endswith('.app/Info.plist') and n.count('/') == 2]
                if not infos:
                    fail('El archivo no contiene una app iOS reconocible.')
                info_path = infos[0]
                info = plistlib.loads(archive.read(info_path))
                prefix = info_path.rsplit('/', 1)[0] + '/'
                privacy = {}
                for path in archive.namelist():
                    if path.startswith(prefix) and path.endswith('Info.plist'):
                        try:
                            data = plistlib.loads(archive.read(path))
                        except Exception:
                            continue
                        privacy.update({k: v for k, v in data.items() if k.endswith('UsageDescription') and isinstance(v, str)})
        except (zipfile.BadZipFile, KeyError, plistlib.InvalidFileException) as exc:
            fail('IPA inválido o no se pudo leer Info.plist: ' + str(exc))
    bundle, version, build = (info.get(k) for k in ('CFBundleIdentifier', 'CFBundleShortVersionString', 'CFBundleVersion'))
    minimum = info.get('MinimumOSVersion')
    if not all(isinstance(v, str) and v.strip() for v in (bundle, version, build, minimum)):
        fail('El IPA debe declarar Bundle ID, versión, compilación y MinimumOSVersion.')
    name = os.environ.get('RELEASE_NAME', '').strip()
    description = os.environ.get('RELEASE_BODY', '').strip()
    if not name or not description:
        fail('Usa el título del Release para el nombre y su descripción para la descripción de la app.')
    source = json.loads(SOURCE.read_text(encoding='utf-8'))
    apps = source.setdefault('apps', [])
    entry = next((a for a in apps if a.get('bundleIdentifier') == bundle), None)
    if entry is None:
        entry = {'name': name, 'bundleIdentifier': bundle, 'developerName': info.get('CFBundleName', name), 'localizedDescription': description, 'versions': [], 'appPermissions': {'entitlements': [], 'privacy': privacy}}
        apps.append(entry)
    else:
        entry.update(name=name, localizedDescription=description)
        entry.setdefault('appPermissions', {'entitlements': [], 'privacy': {}})['privacy'] = privacy
    entry['versions'] = [{'version': version, 'buildVersion': build, 'date': datetime.date.today().isoformat(), 'downloadURL': url, 'size': asset['size'], 'minOSVersion': minimum}]
    SOURCE.write_text(json.dumps(source, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f'Validated {bundle} {version} ({build}); source.json updated.')

if __name__ == '__main__':
    main()
