# Actualizaciones manuales de aplicaciones

El flujo **Add manual app update** permite añadir una versión a una ficha que ya existe en `source.json`. Nunca crea una aplicación nueva.

## Desde GitHub

1. Abre la pestaña **Actions** del repositorio.
2. Selecciona **Add manual app update**.
3. Pulsa **Run workflow**.
4. Rellena el Bundle ID exacto, la versión, el número de compilación y la URL HTTPS directa del IPA.
5. Opcionalmente, indica fecha, tamaño en bytes, versión mínima, descripción y si es beta.
6. Ejecuta el flujo. Si las validaciones pasan, se añade la versión y se publica un commit.

## Reglas de seguridad

- El Bundle ID debe corresponder exactamente a una ficha ya existente.
- Si no existe o aparece duplicado, la operación se cancela.
- La nueva versión se coloca al principio de `versions`.
- Se conservan el historial y todos los demás campos de la ficha, incluidos icono, descripción, capturas y permisos.
- Una versión idéntica (versión + build + URL) no se puede insertar dos veces.
- La URL debe usar HTTPS y la fecha debe ser válida en formato `YYYY-MM-DD`.

## Desde un ordenador con Python

Desde la raíz del repositorio:

```bash
python scripts/update_manual_app.py \
  --bundle-id "com.google.ios.youtube" \
  --version "21.11.0" \
  --build-version "123789" \
  --date "2026-11-11" \
  --download-url "https://example.com/YouTube.ipa" \
  --size 123456789 \
  --min-os-version "16.0"
```

Sustituye los valores de ejemplo por los datos reales del IPA. No uses este ejemplo como enlace de descarga.

## Aplicaciones automáticas y manuales

El sincronizador automático solo procesa los Bundle ID definidos en `scripts/sync_catalog.py`. Las demás fichas, incluidas las que añadas tú manualmente, no se modifican con ese sincronizador. Spotify continúa fuera de la sincronización automática.
