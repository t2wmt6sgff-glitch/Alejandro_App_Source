# Apps de EL ALE :)

Catálogo personal de aplicaciones para Feather.

**Fuente:**  
https://raw.githubusercontent.com/t2wmt6sgff-glitch/Alejandro_App_Source/main/source.json

## Estado del catálogo

- **PPSSPP 1.20.4**: IPA oficial enlazado directamente desde el release del proyecto. El procesamiento comprobó el Bundle ID, metadatos, tamaño, estructura, firma oficial y permisos. No se ha probado su instalación en un iPad con iPadOS 26.
- **Spotify 9.1.92**: entrada ya presente en la fuente. Esta revisión no ha auditado el IPA ni sus condiciones; se ha dejado intacta.
- **Manic EMU** y **Gen1Recomp**: no se ofrecen como instalables desde esta fuente. Sus compilaciones personalizadas siguen pendientes de firma compatible y prueba en dispositivo.

No hay ROMs ni datos de juegos en este repositorio. Utiliza copias de juegos obtenidas legalmente.

## Manic EMU

El proyecto oficial permite configurar o retirar App Groups, compras integradas e iCloud al compilar. El esquema oficial ManicEmuSideload ya excluye las compras y la interfaz de sincronización iCloud; BitBop usa una hoja de compartir cuando no dispone de su grupo compartido.

El IPA oficial declara capacidades adicionales, entre ellas App Groups, iCloud y otras capacidades de ejecución. No basta con borrar sus entitlements del IPA oficial: hay que compilar el esquema sideload y comprobar la aplicación resultante. El workflow de auditoría usa Xcode 26 en macOS y el mínimo de iOS 15 del proyecto.

La integración R.swift está como plugin de compilación de Swift Package Manager. Xcode exige aprobar ese plugin; su documentación propone desactivar la validación de huella para CI. Este repositorio no aplica ese ajuste porque omite un control de seguridad. Una prueba anterior que sí lo omitió llegó a fallar compilando una dependencia de dispositivos que declara iOS 12 aunque usa APIs de iOS 13. No se ha producido un IPA personalizado válido con las comprobaciones conservadas, ni se ha firmado o instalado Manic EMU con Feather.

Manic EMU está bajo AGPL-3.0: cualquier distribución de una modificación requiere ofrecer el código fuente correspondiente y conservar avisos y licencia.

## Gen1Recomp

Se verificó una compilación sin firma de la versión oficial **0.4.1** en GitHub Actions, desde el commit 12a2df8332f570194f98e5599ee54079a1771016, con GEN1_DISABLE_HEALTHKIT=1.

Resultados de esa compilación:

- IPA creado y ZIP íntegro; tamaño aproximado: 36 MB.
- Bundle ID: com.theboisclub.gen1recompplusplus.
- Versión/build: 0.4.1 / 401.
- Mínimo de iOS: 15.0.
- Sin extensiones incluidas.
- HealthKit no aparece en los entitlements de la configuración sin firma.
- NSHealthShareUsageDescription permanece en el Info.plist y el puente nativo de pasos permanece compilado. El ajuste oficial elimina la capacidad de firma, pero no elimina por completo el puente ni su texto de privacidad. El juego principal pudo compilar; no se ejecutó en un dispositivo ni se comprobó qué hace el mod Pokéwalker sin HealthKit.

El IPA no se publicó ni se adjuntó como artefacto. La licencia del proyecto permite redistribuir su código GPL con atribución, pero excluye expresamente el launcher propietario de las versiones modificadas. El IPA generado incluye ese launcher y no se puede publicar como variante modificada sin sustituirlo por uno propio conforme a la licencia o recibir permiso. El proyecto pide que cada usuario aporte sus archivos de juego; esta fuente no distribuye ROMs.

Una compilación correcta sin firma no demuestra que Feather pueda volver a firmar o instalar la app. Este equipo Windows no dispone de Xcode ni muestra un iPad conectado. No hay certificado Apple ni perfil disponible para estas pruebas.

## Añadir una aplicación

1. En este repositorio, abre **Releases → Draft a new release**.
2. Elige una etiqueta única.
3. Escribe el nombre que quieras mostrar en el título del Release.
4. Escribe la descripción en español en el cuerpo.
5. Adjunta un único archivo .ipa cuya distribución esté autorizada.
6. Pulsa **Publish release**.

GitHub Actions valida el IPA en macOS y solo actualiza source.json si todas las comprobaciones pasan. Si el Bundle ID ya existe, actualiza esa aplicación en lugar de crear otra entrada. Si una validación falla, el catálogo no se modifica; abre **Actions** para consultar el error.

Para cambiar solo el nombre o la descripción, abre **Actions → Edit app name and description → Run workflow** y completa el formulario. No hace falta subir otro IPA ni editar JSON.

No subas certificados, perfiles de aprovisionamiento, contraseñas ni ROMs. Feather no actualiza silenciosamente las apps instaladas: la fuente expone versiones y metadatos para que el usuario decida qué instalar.

## Auditorías de compilación

En **Actions → Audit custom iOS build feasibility → Run workflow** puedes elegir Manic EMU o Gen1Recomp. La acción compila en un runner macOS, sin certificado y sin publicar artefactos. No demuestra la firma con tu cuenta, la instalación desde Feather ni el funcionamiento en iPadOS 26.

La comprobación semanal de versiones revisa las aplicaciones que están en el catálogo y no publica actualizaciones por sí sola. Delta no figura en el catálogo ni en los monitores activos.

## Icono

La fuente usa la imagen adjunta, conservada como JPEG cuadrado de 447 × 447 píxeles:  
https://raw.githubusercontent.com/t2wmt6sgff-glitch/Alejandro_App_Source/main/assets/source-icon.jpg

## Referencias oficiales

- [Formato de fuentes de AltStore Classic](https://faq.altstore.io/developers/make-a-source)
- [Feather](https://feather.claration.dev/)
- [PPSSPP 1.20.4](https://github.com/hrydgard/ppsspp/releases/tag/v1.20.4)
- [Manic EMU](https://github.com/Manic-EMU/ManicEMU)
- [Gen1Recomp v0.4.1](https://github.com/bryanthaboi/gen1recomp/releases/tag/v0.4.1)
- [Licencia y condiciones adicionales de Gen1Recomp](https://github.com/bryanthaboi/gen1recomp/blob/dev/LICENSE.MD)
- [R.swift: plugins y aprobación en Xcode](https://github.com/mac-cain13/R.swift)