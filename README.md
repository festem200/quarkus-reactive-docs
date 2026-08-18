# Quarkus reactivo con Java — documentación completa y organizada

Repositorio de documentación **completa, oficial y actualizada** sobre programación
reactiva con Quarkus y Java, en Markdown y organizada para poder estudiarla y consultarla
sin depender de la web.

| | |
| --- | --- |
| **Quarkus documentado** | 3.38.2 (último release estable, publicado el 13 ago 2026) |
| **Mutiny documentado** | 3.3.0 |
| **Última sincronización** | 2026-08-17 |
| **Contenido** | 140 guías oficiales de Quarkus + 54 documentos oficiales de Mutiny + 8 guías propias en español |
| **Fuentes** | [quarkusio/quarkus](https://github.com/quarkusio/quarkus) y [smallrye/smallrye-mutiny](https://github.com/smallrye/smallrye-mutiny), ambas Apache-2.0 |

## Por dónde empezar

1. **[Índice general](docs/00-INDICE.md)** — todas las guías por categoría, con una línea
   de resumen cada una.
2. **[Guías propias](docs/00-guias-propias/README.md)** — escritas en español para este
   repositorio: ruta de aprendizaje, modelo de ejecución, chuleta de Mutiny, mejores
   prácticas, antipatrones, matriz de extensiones, checklist de producción y glosario.
3. Si nunca has trabajado con Quarkus reactivo, sigue la
   **[ruta de aprendizaje](docs/00-guias-propias/01-ruta-de-aprendizaje.md)**.
4. Si ya trabajas con él y buscas algo concreto, usa la búsqueda del repositorio
   (`grep -ri "término" docs/`) o el índice.

## Estructura

```
docs/
├── 00-INDICE.md                  Índice general generado automáticamente
├── 00-guias-propias/             Material propio en español (no oficial)
├── 01-fundamentos/               Arquitectura reactiva, Mutiny, Vert.x, contexto, hilos virtuales
├── 02-web-http/                  Quarkus REST, cliente REST, reactive routes, WebSockets, GraphQL, Qute
├── 03-datos/                     Clientes SQL reactivos, Hibernate Reactive, MongoDB, Redis, caché
├── 04-mensajeria/                Reactive Messaging, Kafka, AMQP, RabbitMQ, Pulsar, mailer
├── 05-grpc/                      gRPC reactivo de punta a punta
├── 06-resiliencia/               Fault tolerance, Stork, load shedding, scheduler, health
├── 07-observabilidad/            OpenTelemetry, Micrometer, logging, JFR
├── 08-rendimiento-nativo/        Medición, compilación nativa, despliegue, TLS, management
├── 09-testing/                   Testing, testing continuo, Dev Services, Dev UI
├── 10-extras/                    Getting started, CLI, Maven/Gradle, configuración
├── 11-mutiny/                    Documentación oficial de Mutiny (tutoriales, guías, referencia)
└── _assets/                      Imágenes referenciadas por las guías
scripts/                          Herramientas de sincronización y verificación
SNAPSHOT.json                     Versiones exactas y fecha del último volcado
```

Cada documento oficial conserva en su cabecera el enlace a la guía publicada, el fichero
AsciiDoc de origen, la versión concreta y la fecha de sincronización, para que siempre
puedas contrastar contra la fuente.

## Mantenerlo actualizado

La documentación no está copiada a mano: se genera con un pipeline reproducible. Para
volver a sincronizar con la última versión publicada:

```bash
./scripts/actualizar.sh
```

Para fijar versiones concretas (por ejemplo la LTS 3.33 en lugar del último release):

```bash
./scripts/actualizar.sh 3.33.2 3.3.0
```

Qué hace el pipeline:

1. `scripts/build_docs.py` — clona en modo *sparse* y *shallow* el repositorio de Quarkus
   en el tag indicado, resuelve los atributos AsciiDoc contra las propiedades Maven reales
   de esa versión (por eso los comandos muestran `3.38.2` y no `${project.version}`),
   resuelve los `include::` para no perder contenido, convierte a Markdown con
   [downdoc](https://www.npmjs.com/package/downdoc), evalúa los condicionales que quedan,
   reescribe los enlaces cruzados a rutas de este repositorio y copia las imágenes.
2. `scripts/build_mutiny.py` — hace lo propio con la documentación de Mutiny, que ya está
   en Markdown, resolviendo las macros de MkDocs (`{{ insert(...) }}`) para incrustar el
   código real de los ejemplos.
3. `scripts/verificar_enlaces.py` — comprueba que no queda ningún enlace interno roto.

Requisitos: Python 3.9+, Node.js 18+ y Git.

## Alcance y límites

- **Qué incluye**: las 140 guías oficiales relevantes para programación reactiva
  (catálogo curado en [`scripts/catalogo.py`](scripts/catalogo.py)), la documentación
  completa de Mutiny y el material propio de organización.
- **Qué no incluye**: las tablas de configuración generadas en tiempo de compilación
  (`quarkus.*` propiedad por propiedad). No existen en el código fuente: se generan al
  construir el sitio. Donde aparecían, el documento lo indica y remite a
  [la referencia de configuración](https://quarkus.io/guides/all-config).
- Las guías oficiales están **en inglés**, como el original; el material propio y la
  organización están en español. No se traduce el contenido oficial para no introducir
  errores ni divergencias con la fuente.

## ¿No existía ya un repositorio así?

Se comprobó antes de construirlo:

- La documentación oficial vive en **AsciiDoc** dentro de
  [`quarkusio/quarkus/docs/src/main/asciidoc/`](https://github.com/quarkusio/quarkus/tree/main/docs/src/main/asciidoc),
  no en Markdown, y mezclada con el código del framework (más de 290 ficheros sin
  agrupación temática por paradigma).
- [`quarkusio/quarkusio.github.io`](https://github.com/quarkusio/quarkusio.github.io) es
  el sitio web: HTML generado, tampoco Markdown reutilizable.
- La documentación de Mutiny sí está en Markdown, pero en formato MkDocs con macros que no
  se renderizan fuera de su generador (los bloques de código aparecen como
  `{{ insert(...) }}`).
- No se encontró ningún repositorio de terceros que reúna documentación reactiva de
  Quarkus en Markdown, curada y sincronizada con la versión actual. Los que existen son
  colecciones de ejemplos de código (por ejemplo los
  [quickstarts oficiales](https://github.com/quarkusio/quarkus-quickstarts)), no
  documentación.

De ahí este repositorio: no reemplaza a la fuente oficial, la **reempaqueta** en un
formato consultable, con enlaces cruzados que funcionan en local y un mecanismo de
actualización de un solo comando.

## Licencia y atribución

Ver [ATRIBUCION.md](ATRIBUCION.md). Resumen: el contenido oficial es de sus autores
(Red Hat y colaboradores de Quarkus / SmallRye) bajo licencia **Apache-2.0**; se
redistribuye aquí conservando la licencia y la atribución en cada fichero. El material
propio de `docs/00-guias-propias/` se publica bajo la misma licencia.
