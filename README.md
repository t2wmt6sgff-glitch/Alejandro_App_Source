# Apps de EL ALE :)

Catálogo personal de aplicaciones para Feather.

**Fuente:**  
https://raw.githubusercontent.com/t2wmt6sgff-glitch/Alejandro_App_Source/main/source.json

## Estado del catálogo

- **PPSSPP 1.20.4**: IPA oficial enlazado directamente desde el release del proyecto. El procesamiento comprobó el Bundle ID, metadatos, tamaño, estructura, firma oficial y permisos. No se ha probado su instalación en un iPad con iPadOS 26.
- **Spotify 9.1.92**: entrada ya presente en la fuente. Esta revisión no ha auditado el IPA ni sus condiciones; se ha dejado intacta.
- **Gen1Recomp 0.4.1**: IPA oficial del release upstream enlazado directamente. Se inspeccionó el IPA de la ejecución oficial de GitHub Actions: Bundle ID, versión/build, compatibilidad con iPad, mínimo de iOS, permisos firmados y privacidad. Requiere HealthKit y declara `get-task-allow`; la instalación dependerá de que el certificado/perfil utilizado permita ese entitlement. No se ha probado en el iPad de destino.
- **iCube 1.0.0 (build 458)**: compilación alpha oficial de iCube, publicada el 5 de noviembre de 2026. La descarga apunta al release inmutable `alpha-458` de Provenance-Emu. Es una versión de prueba y puede contener errores. Se ha copiado únicamente la entrada de iCube, no el catálogo completo de Provenance.
- **MeloCafe 1.1 (build 3)**: IPA oficial del release `1.1` de Stossy11. Los metadatos se contrastaron con la configuración del proyecto en ese tag y con el registro del asset publicado. La app declara el entitlement `com.apple.developer.kernel.increased-memory-limit` y permisos de cámara y micrófono. El IPA binario no se pudo descargar e inspeccionar de forma independiente en esta revisión; se documenta esa limitación en la sección MeloCafe.
- **Manic EMU**: se instala añadiendo su fuente oficial por separado: [https://apps.manicemu.site/altstore](https://apps.manicemu.site/altstore). No duplicamos su IPA ni sus metadatos aquí para que las actualizaciones sigan bajo control del equipo de Manic EMU.

No hay ROMs ni datos de juegos en este repositorio. Utiliza copias de juegos obtenidas legalmente.

## MeloCafe

La entrada apunta al IPA oficial publicado por Stossy11 en el release `1.1` del 31 de octubre de 2026.

- Bundle ID: `com.stossy11.MeloCafe`.
- Versión/build: `1.1 / 3`.
- Mínimo de iOS de la app principal: `15.0`.
- La extensión `MeloCafeRamDonor` tiene deployment target `26.0`; las funciones asociadas a esa extensión requieren iOS/iPadOS 26 o posterior.
- Tamaño del IPA publicado: 23.558.287 bytes.
- SHA-256 publicado por GitHub para el asset: `595c8c307206c789e607836e670a9290dbacc0c51a224934fd2fde002b190fce`.
- Entitlement declarado por el target principal: `com.apple.developer.kernel.increased-memory-limit`.
- Permisos de privacidad: `NSCameraUsageDescription` y `NSMicrophoneUsageDescription`.
- Descarga: [IPA oficial MeloCafe 1.1](https://github.com/stossy11/MeloCafe/releases/download/1.1/MeloCafe.ipa).
- Release: [stossy11/MeloCafe 1.1](https://github.com/stossy11/MeloCafe/releases/tag/1.1).

**Alcance de la comprobación:** el Bundle ID, versión, build, deployment targets, entitlement y cadenas de privacidad se contrastaron con el proyecto Xcode del tag `1.1`; el tamaño, SHA-256, fecha y URL se contrastaron con los metadatos del asset de GitHub. En esta revisión no fue posible descargar y abrir el IPA binario para comparar su `Info.plist` y su firma con esos datos. Por eso no se afirma que los entitlements estén presentes en la firma distribuida, solo que están declarados en el proyecto. El certificado usado para volver a firmar debe admitir Increased Memory Limit para conservar esa capacidad.

MeloCafe es un emulador de Wii U basado en Cemu. No incluye juegos; importa únicamente copias propias. El README oficial indica que para obtener el mejor rendimiento se necesita Increased Memory Limit y que hay que asignar el Universal Script en StikDebug para JIT. En iOS 26, la guía oficial recomienda StikDebug para activar JIT.

## iCube

La entrada utiliza la compilación **alpha 458** publicada por el proyecto el 5 de noviembre de 2026.

- Bundle ID: `com.joemattiello.iCube`.
- Versión/build: `1.0.0 / 458`.
- Mínimo de iOS declarado por el feed oficial: `17.0`.
- Tamaño del IPA: 104.593.144 bytes.
- Descarga: [release oficial alpha-458](https://github.com/Provenance-Emu/iCube/releases/tag/alpha-458).
- Fuente oficial: [https://icube-emu.com/api/altstore](https://icube-emu.com/api/altstore).

Se ha copiado únicamente la ficha de iCube a este catálogo para reunirla con las demás aplicaciones. La fuente oficial de iCube sigue siendo la referencia para futuras versiones: esta ficha personal no se actualiza automáticamente cuando el desarrollador publica otra compilación. La alpha es una versión de prueba. iCube emula GameCube y Wii y no incluye juegos; importa únicamente copias propias.

## Gen1Recomp

La entrada utiliza el IPA oficial **0.4.1** publicado por el proyecto, no la compilación personalizada sin firma que se generó en la auditoría anterior.

- Bundle ID: `com.theboisclub.gen1recompplusplus`.
- Versión/build: `0.4.1 / 401`.
- Mínimo de iOS: `15.0`.
- Tamaño: 44.734.536 bytes.
- SHA-256 oficial: `5de10fab829699f3037112783874cd855c15201519dce7ffcea66c66c5190f50`.
- Entitlements de la app: `com.apple.developer.healthkit` y `get-task-allow`.
- Privacidad: `NSHealthShareUsageDescription`, con el texto incluido por el desarrollador.

El IPA se obtuvo del artefacto de la ejecución oficial de GitHub Actions y se inspeccionaron su `Info.plist`, el perfil integrado y los entitlements de la firma Mach-O. El perfil declara HealthKit y el binario firmado contiene el entitlement HealthKit. Por tanto, el certificado/perfil con el que se vuelva a firmar debe ser compatible con HealthKit. Feather puede rechazar la instalación si el certificado no admite esa capacidad; no se ha probado con el certificado que se utilizará ni en el iPad de destino.

La función Pokéwalker puede solicitar acceso a los pasos mediante HealthKit. Gen1Recomp no incluye ROMs: cada usuario debe importar su propia copia legal. La descarga apunta directamente al [release oficial v0.4.1](https://github.com/bryanthaboi/gen1recomp/releases/tag/v0.4.1).

## Manic EMU

Manic EMU se instalará desde la fuente oficial del desarrollador:

**Fuente AltStore:** https://apps.manicemu.site/altstore

Así evitamos mantener una copia de sus metadatos y enlaces de descarga en este catálogo. El equipo de Manic EMU controla las versiones y actualizaciones de su propia fuente. Su código es abierto bajo AGPL-3.0, pero no hace falta copiar ni compilar el proyecto para instalar la versión oficial.

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
- [iCube alpha 458](https://github.com/Provenance-Emu/iCube/releases/tag/alpha-458)
- [MeloCafe 1.1](https://github.com/stossy11/MeloCafe/releases/tag/1.1)
- [Licencia y condiciones adicionales de Gen1Recomp](https://github.com/bryanthaboi/gen1recomp/blob/dev/LICENSE.MD)
- [R.swift: plugins y aprobación en Xcode](https://github.com/mac-cain13/R.swift)