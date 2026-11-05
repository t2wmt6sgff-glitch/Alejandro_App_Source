# Fuente personal de AltStore Classic para Feather

Añade esta fuente en Feather:

https://raw.githubusercontent.com/t2wmt6sgff-glitch/Alejandro_App_Source/main/source.json

## Aplicaciones publicadas

| Aplicación | Versión | Bundle ID | Descripción publicada |
|---|---:|---|---|
| Delta | 1.7.1 (139) | `com.rileytestut.Delta` | Emulador para iPad de NES, SNES, Nintendo 64, Game Boy, Game Boy Color, Game Boy Advance y Nintendo DS. Ofrece controles táctiles y para mandos, partidas guardadas y sincronización en la nube. No incluye juegos. |
| PPSSPP | 1.20.4 | `org.ppsspp.ppsspp` | Emulador de PlayStation Portable para iPad. Permite cargar copias de juegos, configurar controles y mandos y ajustar gráficos y rendimiento. No requiere BIOS y no incluye juegos. |

IPA oficial descargado y analizado en macOS para ambas apps; firma, permisos, mínimo de iOS y familia iPad verificados. Las descripciones completas en español y los avisos para usar únicamente copias que tengas derecho a utilizar aparecen en la fuente.

Las dos descargas apuntan directamente a los proveedores oficiales ([Delta en la fuente de AltStore](https://apps.altstore.io/) y [PPSSPP en su release](https://github.com/hrydgard/ppsspp/releases/tag/v1.20.4)); este repositorio no vuelve a alojar sus IPA. Las versiones, IDs y permisos de `source.json` salen del archivo IPA. Las claves de privacidad se conservan en el idioma que usa el IPA. El análisis no prueba que la app se ejecute en iPadOS 26 ni que cada juego funcione.

## Candidatas comprobadas y no publicadas

| Candidata | Resultado | Motivo |
|---|---|---|
| Manic EMU 2.0.2 (build 5) | IPA oficial válido, firmado, versión iPad; análisis de permisos completo. | Declara entitlements de kernel, ejecución sostenida, notificaciones y contenedores iCloud. No se ha verificado que la firma habitual que se usa en Feather pueda satisfacerlos, así que no la publico como instalación normal. |
| Gen1Recomp 0.4.0 (build 400) | IPA oficial válido, firmado, versión iPad; análisis de permisos completo. | Declara HealthKit, cuya capacidad de firma no está verificada para Feather. Además, la licencia oficial impone condiciones específicas al launcher incluido y exige atribución. El proyecto requiere que aportes tu propia ROM; no incluye ROM. |

Ambas candidatas tienen IPA verificables, pero eso por sí solo no confirma que se puedan instalar sin capacidades especiales. No incluí una aplicación hasta resolver ese punto. No redistribuimos sus IPA.

## Añadir o actualizar una aplicación desde GitHub

Necesitas tener permiso para publicar el IPA:

1. Abre este repositorio en GitHub y pulsa **Releases → Draft a new release**.
2. Crea una etiqueta nueva y única, por ejemplo `mi-app-1.2`. Para un cambio de descripción o una nueva versión de la misma app, la etiqueta debe ser nueva.
3. En el título del Release escribe el nombre que quieres que aparezca en Feather.
4. En el texto del Release escribe la descripción en español.
5. Arrastra un único archivo `.ipa` al apartado de archivos adjuntos. No incluyas certificados, perfiles de aprovisionamiento ni contraseñas.
6. Pulsa **Publish release**. GitHub Actions descargará el IPA en un runner macOS, analizará la app y todas sus extensiones, y validará firma, Bundle ID, versión, build, versión mínima, soporte iPad, privacidad, icono y tamaño.
7. Si todas las comprobaciones pasan, Actions actualiza `source.json` y el icono. Si falla algo, el catálogo no se actualiza; abre la ejecución fallida en **Actions** para leer el error en español.

El Bundle ID del IPA identifica la entrada. Publicar otra versión con el mismo Bundle ID la actualiza y conserva ese identificador. Un Bundle ID ya existente no crea una entrada duplicada. Si el primer procesamiento falla, corrige el Release y vuelve a ejecutarlo desde **Actions → Add or update app from a release → Run workflow**, indicando la etiqueta ya publicada.

Los IPA añadidos de esta forma se guardan como activos del Release, no dentro del historial Git. Las aplicaciones de terceros incluidas en el catálogo usan sus enlaces oficiales. El registro de la fuente no actualiza por sí solo una app ya instalada: comprueba las actualizaciones desde Feather.

## Cambiar el nombre o la descripción sin volver a subir el IPA

1. Abre **Actions → Edit app name and description → Run workflow**.
2. Escribe el nombre actual tal como aparece en la fuente, el nombre nuevo y la descripción nueva.
3. Ejecuta el flujo. GitHub actualiza y confirma `source.json`; el Bundle ID, la versión, el enlace y los permisos permanecen iguales.

Si hay varias apps con el mismo nombre o el nombre actual no coincide exactamente, el flujo falla sin cambiar el catálogo. Para actualizar el IPA y los datos técnicos, usa el procedimiento de Release anterior.

## Comprobar actualizaciones oficiales

## Auditoría y límites

El flujo **Audit official IPA candidates** descarga versiones concretas de los cuatro proyectos candidatos desde sus fuentes oficiales, calcula SHA-256 y verifica los metadatos del IPA y los entitlements firmados de la app y sus extensiones mediante `codesign`. También recopila todas las claves `*UsageDescription` de los `Info.plist`. El job de macOS auditó los cuatro IPA oficiales y completó las pruebas automatizadas del procesador y los flujos de metadatos. El informe completo queda en el resumen del job de GitHub Actions. El informe completo queda en el resumen del job de GitHub Actions.

AltStore exige que `appPermissions` coincida exactamente con los permisos de la descarga; rechaza apps cuyos permisos no coinciden. El procesador incluye los entitlements de la app y de las extensiones y sus claves de privacidad, y falla si no puede comprobar la firma.

`Check official app updates` consulta semanalmente las fuentes oficiales de Delta y PPSSPP. Si hay una versión nueva, descarga su IPA, compara el Bundle ID y el tamaño, extrae los permisos firmados en macOS y verifica el soporte para iPad. La ejecución programada solo genera un informe. Para publicar una versión verificada, abre **Actions → Check official app updates → Run workflow**, elige la app y marca **Publish update**. Ese paso manual actualiza los metadatos de la fuente; no actualiza las instalaciones existentes en Feather. Manic EMU y Gen1Recomp no se monitorizan mientras permanezcan fuera del catálogo.
