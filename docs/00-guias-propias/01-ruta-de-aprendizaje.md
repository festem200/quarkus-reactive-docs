# Ruta de aprendizaje: Quarkus reactivo con Java

Orden de lectura recomendado. Cada punto enlaza a la documentación oficial ya
incluida en este repositorio. Los tiempos son orientativos para alguien con
experiencia previa en Java y Jakarta EE / Spring.

## Nivel 0 — Antes de empezar (30 min)

Requisitos reales para que lo demás tenga sentido:

- Java 17 o superior (Quarkus 3.x exige JDK 17+; para hilos virtuales, JDK 21+).
- Maven 3.9+ o Gradle, y preferiblemente la [CLI de Quarkus](../10-extras/cli-tooling.md).
- Docker o Podman en local: casi todas las guías reactivas usan
  [Dev Services](../09-testing/dev-services.md) para levantar Postgres, Kafka o Redis solos.

Lectura: [Getting Started](../10-extras/getting-started.md) — aunque sea imperativo,
fija el vocabulario de extensiones, `dev mode` y configuración.

## Nivel 1 — El porqué del modelo reactivo (2-3 h)

1. [Arquitectura reactiva de Quarkus](../01-fundamentos/quarkus-reactive-architecture.md) —
   qué significa "reactivo" aquí: no es solo una API, es el motor (Vert.x) sobre el que
   corre todo Quarkus, también el código imperativo.
2. [Getting Started with Reactive](../01-fundamentos/getting-started-reactive.md) —
   la primera aplicación CRUD no bloqueante de punta a punta.
3. [Mutiny primer](../01-fundamentos/mutiny-primer.md) — `Uni` y `Multi`, el modelo de
   eventos que sustituye a `CompletableFuture`/`Flux`.
4. [Modelo de ejecución](02-modelo-de-ejecucion.md) (guía propia) — la regla que más
   errores evita: qué hilo ejecuta tu método y qué puedes hacer en él.

Al terminar deberías poder responder: *¿por qué bloquear un event loop tumba el
rendimiento de toda la aplicación, no solo el de esa petición?*

## Nivel 2 — Mutiny en serio (4-6 h)

Es el nivel donde más gente se atasca; merece la inversión.

1. [Hello Mutiny](../11-mutiny/tutoriales/hello-mutiny.md) y los tutoriales de
   [creación de pipelines Uni](../11-mutiny/tutoriales/creating-uni-pipelines.md) /
   [Multi](../11-mutiny/tutoriales/creating-multi-pipelines.md).
2. [Transformar items](../11-mutiny/tutoriales/transforming-items.md) y
   [transformarlos de forma asíncrona](../11-mutiny/tutoriales/transforming-items-asynchronously.md) —
   la diferencia entre `transform` y `transformToUni` es el 80 % de los bugs de novato.
3. [Gestión de fallos](../11-mutiny/tutoriales/handling-failures.md) y
   [reintentos](../11-mutiny/tutoriales/retrying.md).
4. [De imperativo a reactivo](../11-mutiny/guias/imperative-to-reactive.md) y
   [de reactivo a imperativo](../11-mutiny/guias/reactive-to-imperative.md).
5. [emitOn vs runSubscriptionOn](../11-mutiny/guias/emit-on-vs-run-subscription-on.md) —
   control explícito de hilos.
6. [Errores frecuentes al "volverse reactivo"](../11-mutiny/referencia/going-reactive-a-few-pitfalls.md).

Apoyo rápido durante el desarrollo: [chuleta de Mutiny](03-mutiny-chuleta.md) (guía propia).

## Nivel 3 — La capa web (4-6 h)

1. [Quarkus REST](../02-web-http/rest.md) — el runtime REST reactivo por defecto
   (antes RESTEasy Reactive). Presta atención a la sección *Execution model, blocking, non-blocking*.
2. [REST + JSON](../02-web-http/rest-json.md) y [cliente REST](../02-web-http/rest-client.md).
3. [Reactive Routes](../02-web-http/reactive-routes.md) — cuando JAX-RS sobra y quieres
   ir directo al router de Vert.x.
4. [Referencia HTTP](../02-web-http/http-reference.md) — timeouts, límites de cuerpo, CORS, compresión.
5. [WebSockets Next](../02-web-http/websockets-next-tutorial.md) +
   [su referencia](../02-web-http/websockets-next-reference.md) — la implementación actual;
   [`websockets`](../02-web-http/websockets.md) es la clásica basada en Jakarta WebSockets.

## Nivel 4 — Datos sin bloquear (6-8 h)

Aquí es donde una aplicación "reactiva" se rompe en la práctica: basta un driver JDBC
para anular todo el modelo.

1. [Clientes SQL reactivos](../03-datos/reactive-sql-clients.md) — la base (Vert.x SQL client).
2. [Hibernate Reactive](../03-datos/hibernate-reactive.md) y
   [Hibernate Reactive con Panache](../03-datos/hibernate-reactive-panache.md) —
   fíjate en `@WithSession` / `@WithTransaction`: sin ellas, no hay sesión.
3. [Datasource](../03-datos/datasource.md) — configuración del pool reactivo
   (`quarkus.datasource.reactive.*`).
4. [Transacciones](../03-datos/transaction.md) — por qué `@Transactional` (JTA) marca el
   método como bloqueante y qué usar en su lugar.
5. Según tu stack: [MongoDB](../03-datos/mongodb.md) /
   [MongoDB con Panache](../03-datos/mongodb-panache.md), [Redis](../03-datos/redis.md),
   [Cassandra](../03-datos/cassandra.md), [Elasticsearch](../03-datos/elasticsearch.md).
6. [Caché](../03-datos/cache.md) — soporta métodos que devuelven `Uni`.

## Nivel 5 — Mensajería y streaming (6-10 h)

1. [Reactive Messaging](../04-mensajeria/messaging.md) — el modelo de canales,
   `@Incoming`/`@Outgoing`, ack/nack y contrapresión.
2. [Kafka: primeros pasos](../04-mensajeria/kafka-getting-started.md) y luego
   [la referencia completa](../04-mensajeria/kafka.md) (larga, pero es la fuente de verdad).
3. Alternativas según el broker: [AMQP](../04-mensajeria/amqp.md),
   [RabbitMQ](../04-mensajeria/rabbitmq.md), [Pulsar](../04-mensajeria/pulsar.md).
4. [Kafka Streams](../04-mensajeria/kafka-streams.md) para procesamiento con estado.

## Nivel 6 — Producción (8-12 h)

1. Resiliencia: [SmallRye Fault Tolerance](../06-resiliencia/smallrye-fault-tolerance.md)
   (`@Retry`, `@CircuitBreaker`, `@Timeout` con soporte para `Uni`) y
   [load shedding](../06-resiliencia/load-shedding-reference.md).
2. Descubrimiento y balanceo: [Stork](../06-resiliencia/stork.md) +
   [referencia](../06-resiliencia/stork-reference.md).
3. Observabilidad: [OpenTelemetry](../07-observabilidad/opentelemetry.md),
   [Micrometer](../07-observabilidad/telemetry-micrometer.md),
   [health checks](../06-resiliencia/smallrye-health.md).
4. Rendimiento y nativo: [medir el rendimiento](../08-rendimiento-nativo/performance-measure.md),
   [referencia nativa](../08-rendimiento-nativo/native-reference.md).
5. Testing: [testing básico](../09-testing/getting-started-testing.md),
   [componentes](../09-testing/testing-components.md),
   [testing de Mutiny](../11-mutiny/guias/testing.md).
6. Repasa el [checklist de producción](07-checklist-produccion.md) (guía propia).

## Nivel 7 — Hilos virtuales (2-3 h)

Alternativa al estilo reactivo cuando el equipo prefiere código imperativo:

- [Hilos virtuales en Quarkus](../01-fundamentos/virtual-threads.md)
- [`@RunOnVirtualThread` en REST](../02-web-http/rest-virtual-threads.md)
- [en mensajería](../04-mensajeria/messaging-virtual-threads.md) y
  [en gRPC](../05-grpc/grpc-virtual-threads.md)

No sustituyen a Mutiny en streaming ni en contrapresión, pero sí evitan escribir
pipelines para lógica puramente secuencial. Ojo con el *pinning* y con los pools
de conexiones dimensionados para pocos hilos.
