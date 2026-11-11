#!/usr/bin/env python3
"""Add a new version to an existing app in source.json; never creates app entries."""
import argparse
import json
import os
import re
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "source.json"


def build_parser():
    parser = argparse.ArgumentParser(
        description="Añade una versión a una app existente sin crear fichas nuevas."
    )
    parser.add_argument("--bundle-id", required=True, help="Bundle ID exacto de la ficha existente")
    parser.add_argument("--version", required=True)
    parser.add_argument("--build-version", required=True)
    parser.add_argument("--download-url", required=True, help="URL HTTPS del IPA")
    parser.add_argument("--date", default=date.today().isoformat(), help="Fecha ISO YYYY-MM-DD")
    parser.add_argument("--size", type=int, help="Tamaño del IPA en bytes")
    parser.add_argument("--min-os-version", help="Versión mínima de iOS/iPadOS")
    parser.add_argument("--description", help="Descripción específica de esta versión")
    parser.add_argument("--platform", default="iOS")
    parser.add_argument("--is-beta", action="store_true")
    return parser


def add_version(data, args):
    apps = data.get("apps")
    if not isinstance(apps, list):
        raise ValueError("source.json no contiene una lista apps válida.")

    matches = [app for app in apps if app.get("bundleIdentifier") == args.bundle_id]
    if len(matches) != 1:
        if not matches:
            raise ValueError(
                f"No existe una app con Bundle ID {args.bundle_id!r}. "
                "Este mecanismo nunca crea fichas nuevas."
            )
        raise ValueError(f"Hay {len(matches)} fichas con ese Bundle ID; se cancela para evitar duplicados.")

    if not args.version.strip() or not args.build_version.strip():
        raise ValueError("La versión y el número de compilación no pueden estar vacíos.")
    if not args.download_url.startswith("https://"):
        raise ValueError("La URL de descarga debe utilizar HTTPS.")
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", args.date):
        raise ValueError("La fecha debe tener formato YYYY-MM-DD.")
    try:
        date.fromisoformat(args.date)
    except ValueError as exc:
        raise ValueError("La fecha indicada no existe.") from exc
    if args.size is not None and args.size <= 0:
        raise ValueError("El tamaño debe ser un número positivo.")

    app = matches[0]
    versions = app.setdefault("versions", [])
    if not isinstance(versions, list):
        raise ValueError("La ficha existente no tiene una lista versions válida.")

    new_version = {
        "version": args.version.strip(),
        "buildVersion": args.build_version.strip(),
        "date": args.date,
        "downloadURL": args.download_url.strip(),
    }
    if args.size is not None:
        new_version["size"] = args.size
    if args.min_os_version:
        new_version["minOSVersion"] = args.min_os_version.strip()
    if args.description:
        new_version["localizedDescription"] = args.description
    if args.platform:
        new_version["platform"] = args.platform
    if args.is_beta:
        new_version["isBeta"] = True

    identity = (
        new_version["version"],
        new_version["buildVersion"],
        new_version["downloadURL"],
    )
    for old in versions:
        old_identity = (
            str(old.get("version", "")),
            str(old.get("buildVersion", "")),
            str(old.get("downloadURL", "")),
        )
        if old_identity == identity:
            raise ValueError("Esta versión ya está registrada en la ficha; no se ha modificado nada.")

    versions.insert(0, new_version)
    return new_version


def main():
    args = build_parser().parse_args()
    data = json.loads(SOURCE.read_text(encoding="utf-8"))
    added = add_version(data, args)
    rendered = json.dumps(data, ensure_ascii=False, indent=2) + "\n"
    json.loads(rendered)
    temporary = SOURCE.with_name(SOURCE.name + ".tmp")
    temporary.write_text(rendered, encoding="utf-8")
    temporary.replace(SOURCE)
    print(
        f"Versión {added['version']} (build {added['buildVersion']}) añadida a "
        f"{args.bundle_id}. La ficha y sus demás campos se han conservado."
    )


if __name__ == "__main__":
    main()
