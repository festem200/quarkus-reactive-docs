# Atribución y licencia

## Contenido oficial de Quarkus

Los documentos de `docs/01-fundamentos/` a `docs/10-extras/` son una **obra derivada**
(conversión de formato AsciiDoc → Markdown, reorganización y reescritura de enlaces) de la
documentación oficial del proyecto Quarkus.

- Origen: <https://github.com/quarkusio/quarkus>, directorio `docs/src/main/asciidoc/`
- Versión sincronizada: la indicada en [`SNAPSHOT.json`](SNAPSHOT.json) y en la cabecera
  de cada fichero
- Copyright: Red Hat, Inc. y los colaboradores del proyecto Quarkus
- Licencia: **Apache License 2.0** — <https://www.apache.org/licenses/LICENSE-2.0>

## Contenido oficial de SmallRye Mutiny

Los documentos de `docs/11-mutiny/` son una obra derivada de la documentación oficial de
SmallRye Mutiny (resolución de macros de MkDocs y adaptación de enlaces).

- Origen: <https://github.com/smallrye/smallrye-mutiny>, directorio `documentation/docs/`
- Copyright: Red Hat, Inc. y los colaboradores de SmallRye
- Licencia: **Apache License 2.0**

## Material propio

`docs/00-guias-propias/`, `scripts/`, `README.md` y este fichero son originales de este
repositorio y se publican bajo la misma licencia **Apache-2.0**, para evitar fricción con
el contenido derivado.

## Cómo citar correctamente

La versión autoritativa de la documentación es siempre la publicada en
<https://quarkus.io/guides/> y <https://smallrye.io/smallrye-mutiny/>. Este repositorio es
una copia sincronizada y puede quedar desfasada entre ejecuciones de
`./scripts/actualizar.sh`. La cabecera de cada documento indica la fecha exacta del
volcado y enlaza al original.

## Modificaciones aplicadas al contenido original

Para cumplir con la sección 4(b) de la licencia Apache-2.0, estas son las modificaciones
introducidas respecto al material original:

1. Conversión de AsciiDoc a Markdown (Quarkus) y resolución de macros de MkDocs (Mutiny).
2. Resolución de atributos y de directivas `include::` para producir documentos autónomos.
3. Sustitución de las tablas de configuración generadas en compilación por una nota que
   remite a la referencia de configuración en línea.
4. Reescritura de enlaces cruzados a rutas relativas de este repositorio; los enlaces a
   guías no incluidas apuntan a quarkus.io.
5. Adición de una cabecera de procedencia en cada fichero (guía oficial, fuente, versión,
   fecha, licencia).
6. Reagrupación temática de los ficheros en carpetas por área.
7. Corrección puntual de erratas del original que impedían la conversión (por ejemplo un
   delimitador de bloque escrito como `----]` en `management-interface-reference.adoc`).

No se ha alterado el contenido técnico ni el sentido de ninguna guía.
