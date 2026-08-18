# El modelo de ejecución de Quarkus (la regla que hay que interiorizar)

Casi todos los problemas serios en una aplicación Quarkus reactiva se reducen a una
pregunta: **¿en qué hilo se está ejecutando este método y tengo derecho a bloquearlo?**

## Los tres tipos de hilo

| Hilo | Cuántos hay | Qué puede hacer | Cuándo se usa |
| --- | --- | --- | --- |
| **Event loop** (I/O thread, `vert.x-eventloop-thread-N`) | Uno por núcleo de CPU por defecto (`quarkus.vertx.event-loops-pool-size`) | Solo trabajo no bloqueante y de corta duración | Métodos que devuelven `Uni`/`Multi`/`CompletionStage`, o anotados `@NonBlocking` |
| **Worker thread** (`executor-thread-N`) | Hasta `quarkus.thread-pool.max-threads` (20 por defecto) | Puede bloquear: JDBC, JTA, llamadas HTTP síncronas, ficheros | Métodos que devuelven un valor normal, o anotados `@Blocking` / `@Transactional` |
| **Hilo virtual** (JDK 21+) | Prácticamente ilimitados | Puede bloquear (con matices: *pinning*) | Métodos anotados `@RunOnVirtualThread` |

El event loop es el recurso escaso. Si lo bloqueas, no ralentizas *tu* petición:
paralizas **todas** las peticiones asignadas a ese loop. Con 8 núcleos, bloquear un
event loop durante 200 ms deja fuera de juego a 1/8 de la capacidad de la aplicación.

Vert.x lo vigila: si un event loop tarda más de `quarkus.vertx.max-event-loop-execute-time`
(2 s por defecto) verás en el log un aviso del `BlockedThreadChecker` con
`io.vertx.core.VertxException: Thread blocked`. Trátalo siempre como un bug, nunca
como ruido de log.

## Regla de decisión en Quarkus REST

Fuente: [Quarkus REST — Execution model, blocking, non-blocking](../02-web-http/rest.md#execution-model-blocking-non-blocking).

```
¿El método devuelve Uni, Multi o CompletionStage?
├─ Sí  → se ejecuta en el EVENT LOOP
│         └─ salvo que lleve @Blocking o @Transactional → worker thread
└─ No  → se ejecuta en un WORKER THREAD
          └─ salvo que lleve @NonBlocking → event loop
```

Anotaciones (de `io.smallrye.common.annotation`), aplicables a método, clase o a una
subclase de `jakarta.ws.rs.core.Application` para cambiar el comportamiento por defecto
de toda la aplicación:

- `@Blocking` — fuerza worker thread aunque devuelvas `Uni`.
- `@NonBlocking` — fuerza event loop aunque devuelvas un `String`.
- `@RunOnVirtualThread` — ejecuta en un hilo virtual nuevo por petición.

Detalle importante: `@Transactional` (JTA) implica bloqueante, porque JTA y JDBC lo son.
Si mezclas `@Transactional` con `Uni` estás pidiendo problemas; en el mundo reactivo la
transacción se declara con `@WithTransaction` de Hibernate Reactive Panache
([ver guía](../03-datos/hibernate-reactive-panache.md)).

Los filtros de petición se ejecutan normalmente **en el mismo hilo** que el método que
atienden: si el endpoint es `@Blocking`, sus filtros también corren en el worker.

## La misma regla, en otros sitios

- **Reactive Messaging**: los métodos `@Incoming`/`@Outgoing` que devuelven `Uni`/`Multi`
  corren en el event loop; para lógica bloqueante se usa `@Blocking` o
  [`@RunOnVirtualThread`](../04-mensajeria/messaging-virtual-threads.md).
- **gRPC**: mismo criterio, ver [gRPC service implementation](../05-grpc/grpc-service-implementation.md).
- **Scheduler**: `@Scheduled` puede correr en worker o, si es no bloqueante, declararlo
  explícitamente; ver [referencia del scheduler](../06-resiliencia/scheduler-reference.md).
- **Reactive Routes**: siempre event loop salvo `@Blocking`
  ([guía](../02-web-http/reactive-routes.md)).

## Cómo salir del event loop cuando de verdad hace falta

Cuando tienes una librería bloqueante inevitable (un SDK propietario, JDBC, un cálculo
pesado), no la ejecutes en el pipeline reactivo directamente. Opciones, de preferible a
menos preferible:

1. Anotar el método con `@Blocking` y dejar que Quarkus lo mueva al worker pool.
2. Aislarlo dentro del pipeline con `Uni.createFrom().item(...)` +
   `.runSubscriptionOn(Infrastructure.getDefaultWorkerPool())`.
3. Anotar con `@RunOnVirtualThread` si el bloqueo es de I/O (no de CPU) y estás en JDK 21+.

Lo contrario también existe: `emitOn(...)` cambia el hilo en el que se **emiten** los
eventos hacia abajo del pipeline, mientras que `runSubscriptionOn(...)` cambia el hilo
donde ocurre la **suscripción** (es decir, dónde se ejecuta el trabajo de origen).
La distinción está explicada con diagramas en
[emitOn vs runSubscriptionOn](../11-mutiny/guias/emit-on-vs-run-subscription-on.md).

## Contexto duplicado: por qué tu `@RequestScoped` a veces desaparece

En imperativo, "el hilo" identifica la petición, y con eso basta para `ThreadLocal`,
MDC de logs o beans `@RequestScoped`. En reactivo un hilo atiende muchas peticiones, así
que Quarkus usa el **contexto duplicado** (*duplicated context*) de Vert.x: una copia
del contexto local asociada a cada petición, que viaja con la ejecución aunque cambie de
hilo.

Consecuencias prácticas:

- Si saltas a un hilo "ajeno" (un `ExecutorService` propio, un `CompletableFuture`
  lanzado a mano, un `new Thread()`), pierdes el contexto: fallarán los beans de ámbito
  de petición, la propagación de trazas y el MDC de logging.
- La solución soportada es la propagación de contexto
  ([context propagation](../01-fundamentos/context-propagation.md)) y respetar los
  ejecutores de `Infrastructure`.
- Detalles y API en [duplicated context](../01-fundamentos/duplicated-context.md).

## Diagnóstico rápido

| Síntoma | Causa probable | Dónde mirar |
| --- | --- | --- |
| `Thread blocked ... time limit is 2000 ms` | Código bloqueante en event loop | [vertx-reference](../01-fundamentos/vertx-reference.md) |
| `BlockingOperationNotAllowedException` | JDBC/JTA o API bloqueante detectada en I/O thread | [modelo de ejecución REST](../02-web-http/rest.md) |
| Latencia p99 pésima con CPU al 20 % | Pool reactivo pequeño o mezcla de bloqueante y no bloqueante | [datasource](../03-datos/datasource.md) |
| `ContextNotActiveException` con `@RequestScoped` | Salto a un hilo sin contexto duplicado | [duplicated context](../01-fundamentos/duplicated-context.md) |
| Error de "sesión reactiva no disponible" en métodos Panache | Falta `@WithSession` / `@WithTransaction`: los métodos de una entidad Panache reactiva deben ejecutarse dentro de una `Mutiny.Session` | [hibernate-reactive-panache](../03-datos/hibernate-reactive-panache.md) |
| `UnsupportedOperationException` en un pipeline con transacción | Mezcla de `@Transactional` (JTA) con `@WithTransaction`/`@WithSession` | [hibernate-reactive-panache](../03-datos/hibernate-reactive-panache.md) |
