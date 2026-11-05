# Apps de EL ALE :)

Catálogo personal en español para Feather, con aplicaciones verificadas y enlaces a sus publicaciones oficiales.

**Añade la fuente a Feather:**
https://raw.githubusercontent.com/t2wmt6sgff-glitch/Alejandro_App_Source/main/source.json

## Aplicación disponible

| Aplicación | Versión | Para qué sirve |
|---|---:|---|
| [PPSSPP](https://github.com/hrydgard/ppsspp) | 1.20.4 | Emulador de PlayStation Portable con ajustes gráficos y controles configurables. No necesita BIOS ni incluye juegos. |

El IPA de PPSSPP procede del release oficial v1.20.4. Se comprobaron el Bundle ID, la versión, el número de compilación, el requisito mínimo de iOS, el soporte declarado para iPad, el tamaño, la integridad ZIP, los entitlements firmados y las claves de privacidad. La última versión oficial consultada sigue siendo 1.20.4. No se ha probado su ejecución en un iPad con iPadOS 26.

La descripción completa y los permisos técnicos se muestran en la fuente. El catálogo enlaza directamente al IPA oficial; este repositorio no vuelve a alojarlo. Utiliza únicamente copias de juegos obtenidas legalmente.

## Sobre otras aplicaciones investigadas

**Manic EMU 2.0.2** tiene un IPA oficial, pero no está publicado aquí como instalable. El IPA declara App Groups, contenedores y servicios iCloud, además de capacidades de ejecución y kernel. El proyecto indica que App Groups e iCloud deben configurarse para la cuenta que construye la aplicación o quitarse antes de compilarla. Una firma normal de Feather no puede garantizar esos identificadores y servicios. No se deben borrar capacidades del IPA sin verificar el resultado. La alternativa legítima es usar la distribución oficial o disponer de la cuenta de desarrollador y las capacidades correspondientes; no se ha verificado una instalación con Feather.

**Gen1Recomp 0.4.0** también publica un IPA oficial para iOS, pero no está publicado aquí como instalable. El IPA verificado declara HealthKit. El proyecto utiliza esa capacidad para contar pasos en iOS; una firma personal puede no autorizarla y no se ha comprobado en Feather qué ocurre al volver a firmar. No se ha alterado el IPA ni se ha retirado la capacidad. El uso requiere que cada persona aporte su propio archivo de juego legal; este repositorio no contiene ROMs. La publicación oficial tiene condiciones de licencia adicionales para su launcher, por lo que esta fuente enlaza —y no vuelve a distribuir— el archivo oficial.

La presencia de un IPA en un release no prueba por sí sola que Feather pueda instalarlo. No se ha realizado una instalación en un dispositivo para estas candidatas.

## Añadir o actualizar una aplicación desde GitHub

Este proceso utiliza un Release de GitHub. El archivo IPA se guarda como activo del Release, no en el historial normal de archivos.

1. Abre **Releases** en este repositorio y pulsa **Draft a new release**.
2. Crea una etiqueta nueva y única. Para una actualización o un cambio de descripción usa otra etiqueta, por ejemplo 'mi-app-1.2'.
3. Escribe en el título el nombre que quieres mostrar en Feather.
4. Escribe la descripción en español en el texto del Release.
5. Adjunta un único archivo .ipa y pulsa **Publish release**.
6. GitHub Actions comprobará el archivo automáticamente. Si todo pasa, añadirá la app o actualizará la entrada que tenga el mismo Bundle ID. Si algo falla, no se cambia el catálogo; abre **Actions** y consulta el resumen del error.

No incluyas certificados, perfiles de aprovisionamiento, contraseñas ni ROMs. Publica únicamente archivos cuya distribución esté autorizada. El nombre y la descripción que escribas en el Release serán los que aparezcan en la fuente; para cambiar solo esos textos sin volver a subir el IPA, abre **Actions → Edit app name and description → Run workflow** y rellena el formulario.

El procesamiento se ejecuta en macOS. Comprueba la integridad del ZIP, que haya una sola app principal, la firma de la app y sus extensiones, sus entitlements, todas las claves de privacidad *UsageDescription, el icono, el Bundle ID, la versión, el build, la versión mínima de iOS y el soporte declarado para iPad. Rechaza identificadores duplicados, datos incompatibles, archivos dañados y permisos contradictorios. Solo escribe el catálogo tras superar todas las comprobaciones.

## Actualizaciones

La comprobación semanal consulta releases oficiales de las aplicaciones monitorizadas que están en el catálogo. En este momento solo monitoriza PPSSPP. La revisión no publica cambios por sí sola. Para publicar una actualización verificada, abre **Actions → Check official app updates → Run workflow** y marca **Publish update**. Se comprueban el IPA oficial, su firma, Bundle ID, soporte para iPad, versión, tamaño y permisos. El flujo impide reemplazar una versión del catálogo por otra numéricamente más antigua.

La fuente no actualiza automáticamente las apps ya instaladas en Feather; muestra los metadatos y la versión que Feather puede consultar.

## Identidad visual

El icono de la fuente utiliza la imagen adjunta, conservada en JPEG cuadrado de 447 × 447 píxeles. El color verde de acento se eligió para armonizar con la imagen. No se ha añadido un encabezado ni capturas: no hay capturas oficiales de iPad verificadas para esta selección.

## Referencias oficiales

- [Formato de fuentes de AltStore Classic](https://faq.altstore.io/developers/make-a-source)
- [Feather](https://feather.claration.dev/)
- [Release de PPSSPP 1.20.4](https://github.com/hrydgard/ppsspp/releases/tag/v1.20.4)
- [Release de Manic EMU 2.0.2](https://github.com/Manic-EMU/ManicEMU/releases/tag/v2.0.2)
- [Release de Gen1Recomp 0.4.0](https://github.com/bryanthaboi/gen1recomp/releases/tag/v0.4.0)
- [Condiciones de licencia de Gen1Recomp](https://github.com/bryanthaboi/gen1recomp/blob/dev/LICENSE.MD)
