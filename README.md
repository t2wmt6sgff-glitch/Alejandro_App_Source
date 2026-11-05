# Fuente personal de AltStore para Feather

Añade en Feather esta fuente:

https://raw.githubusercontent.com/t2wmt6sgff-glitch/Alejandro_App_Source/main/source.json

El nombre real del repositorio es `Alejandro_App_Source` (subrayado), no `Alejandro-App-Source`.

## Añadir una app

1. En GitHub, entra en **Releases** y pulsa **Draft a new release**.
2. Crea una etiqueta nueva (por ejemplo, `app-1.2`). No reutilices etiquetas.
3. En **Release title**, escribe el nombre que aparecerá en Feather.
4. En la descripción del Release, escribe la descripción que verá la persona usuaria.
5. Adjunta exactamente un `.ipa` con el botón de adjuntar archivos. El IPA debe proceder de una fuente autorizada para su redistribución. No subas certificados, perfiles ni contraseñas.
6. Pulsa **Publish release**. GitHub Actions descarga el IPA, valida que sea legible y extrae Bundle ID, versión, build y MinimumOSVersion de Info.plist. Si valida, actualiza automáticamente `source.json` y conserva una sola entrada por Bundle ID.
7. Consulta la ejecución en **Actions**. Si algo falla, abre el paso marcado en rojo para ver un mensaje comprensible.

Para modificar nombre o descripción, usa el título y texto de un Release nuevo para ese mismo Bundle ID. Para cada actualización usa una etiqueta distinta. La fuente apunta a la versión más reciente procesada. Cambiar la fuente no actualiza las apps ya instaladas en Feather: hay que gestionar esa actualización desde Feather.

## Límites de validación

La automatización verifica estructura ZIP/IPA, descarga pública y tamaño, así como los metadatos técnicos básicos leídos del propio IPA. También recoge las cadenas `*UsageDescription` de los plist incluidos.

**Pendiente antes de considerar completa la compatibilidad AltStore Classic:** AltStore exige que `appPermissions` enumere los entitlements de la app y extensiones y que coincidan con la firma. El script actual no extrae entitlements firmados, por tanto no se deben tratar los IPA procesados como garantizados para instalar. Tampoco se ha probado la instalación en Feather ni en un iPad con iPadOS 26. El catálogo se mantiene vacío hasta disponer de artefactos concretos revisados y verificados.

## Aplicaciones candidatas

No se han incorporado Delta, Manic EMU, Provenance, PPSSPP ni Gen1Recomp: esta implementación no verificó cada IPA concreto junto con bundle ID, permisos firmados, compatibilidad con iPadOS 26 y permiso de redistribución del artefacto. La presencia de un IPA en una página oficial no demuestra por sí sola autorización para alojar una copia propia. Obtén las apps en los canales oficiales y confirma las condiciones del proyecto antes de publicar una copia.

Las nuevas versiones no se importan automáticamente desde fuentes externas. Primero revisa origen y permiso, luego publica un Release propio aprobado. Esto evita que un bot copie automáticamente artefactos que no hayan sido comprobados.
