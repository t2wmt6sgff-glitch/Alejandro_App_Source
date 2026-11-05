# Fuente personal de AltStore Classic para Feather

Añade en Feather la URL pública de la fuente:

https://raw.githubusercontent.com/t2wmt6sgff-glitch/Alejandro_App_Source/main/source.json

El nombre exacto del repositorio es `Alejandro_App_Source` (con guiones bajos).

## Incorporar una app propia mediante GitHub Releases

1. En GitHub, abre **Releases → Draft a new release**.
2. Crea una etiqueta nueva para esta versión, por ejemplo `mi-app-1.2`. No reutilices etiquetas.
3. En el título del Release, escribe el nombre que aparecerá en Feather.
4. En el texto del Release, escribe la descripción en español.
5. Adjunta exactamente un IPA que tengas permiso para publicar. No adjuntes certificados, perfiles de aprovisionamiento ni contraseñas.
6. Publica el Release. Actions descarga el IPA y ejecuta la inspección en un runner macOS. Lee los metadatos y el icono del propio IPA, verifica los entitlements firmados de la app y de sus extensiones con `codesign`, y recopila las claves `*UsageDescription` de los `Info.plist`.
7. Solo si todas las comprobaciones pasan, actualiza `source.json` y añade el icono pequeño a `icons/`. Abre **Actions** para ver el resultado y el error si falla.

Un Bundle ID identifica una sola entrada. Para cambiar el nombre o la descripción, publícala de nuevo en un Release para el mismo Bundle ID. Cada versión debe usar etiqueta nueva. Para reintentar tras corregir un fallo, abre el flujo **Add or update app from a release** en **Actions → Run workflow** e indica la etiqueta del Release ya publicado.

Las URLs de descarga apuntan al activo del Release. El catálogo representa una versión publicada, pero no actualiza por sí solo las apps ya instaladas en Feather; la actualización se inicia desde Feather.

## Verificación de las cuatro candidatas

La auditoría **Audit official IPA candidates** descarga los IPA enlazados desde los Releases oficiales y genera un informe de Bundle ID, versión, build, mínimo de iOS, permisos firmados, permisos de privacidad, hash SHA-256 y soporte declarado para iPad. El informe indica por separado que la ejecución real en iPadOS 26 no se ha probado. La fuente no incluye apps mientras no se haya completado y revisado ese informe.

Los enlaces del catálogo deben seguir apuntando a las páginas/activos oficiales para evitar espejar IPA sin autorización. Que una IPA aparezca en GitHub no supone por sí mismo un permiso general para que otra persona la vuelva a alojar. El procedimiento de Release propio sirve para artefactos cuya publicación está autorizada.

## Límites

La inspección de firma comprueba los permisos de la IPA recibida, pero no prueba su ejecución en un iPad. Compatibilidad de CPU, funciones que dependen de JIT y comportamiento de iPadOS 26 deben verificarse aparte. No se importan automáticamente versiones desde otros proyectos ni se actualizan automáticamente las instalaciones existentes.

La fuente inicial permanece vacía hasta que la auditoría confirme los permisos de los IPA concretos y se revise cada URL oficial de descarga y su derecho de redistribución.
