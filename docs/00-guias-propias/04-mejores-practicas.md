# Mejores prácticas en Quarkus reactivo

Reglas destiladas de la documentación oficial incluida en este repositorio. Cada una
enlaza a la guía que la respalda, para que puedas comprobarla y profundizar.

## 1. Decide el estilo por servicio, no por moda

Reactivo no es "mejor" en abstracto: gana cuando hay **mucha concurrencia con I/O y poco
CPU** (gateways, agregadores de APIs, streaming, colas). Para un CRUD interno con 30
usuarios, el modelo imperativo con JDBC es más simple y perfectamente válido — y en
Quarkus sigue corriendo sobre el mismo motor reactivo por debajo
([arquitectura reactiva](../01-fundamentos/quarkus-reactive-architecture.md)).

Un criterio práctico: si vas a introducir Mutiny en el equipo, asegúrate de que al menos
dos personas entienden el [modelo de ejecución](02-modelo-de-ejecucion.md). Un pipeline
reactivo mal entendido es más caro de mantener que un método bloqueante.

## 2. Nunca mezcles bloqueante y no bloqueante por accidente

- Un solo `DriverManager`, `JdbcTemplate`, `RestTemplate` o `Thread.sleep()` en un event
  loop anula el beneficio de toda la cadena.
- Si necesitas una librería bloqueante, aíslala con `@Blocking`, `@RunOnVirtualThread` o
  `runSubscriptionOn(Infrastructure.getDefaultWorkerPool())`.
- Vigila los logs de `BlockedThreadChecker` en dev y en pre-producción: son la señal
  temprana de esta mezcla ([vertx-reference](../01-fundamentos/vertx-reference.md)).

## 3. En datos, elige un único paradigma por unidad de persistencia

`quarkus-jdbc-postgresql` y `quarkus-reactive-pg-client` pueden convivir, pero mezclarlos
sobre la misma entidad y transacción es fuente de bugs sutiles. Concretamente:

- No mezcles `@Transactional` (JTA) con `@WithTransaction`/`@WithSession` de Panache
  reactivo: la propia documentación advierte que el resultado es una
  `UnsupportedOperationException`
  ([hibernate-reactive-panache](../03-datos/hibernate-reactive-panache.md)).
- Los métodos de entidades Panache reactivas deben ejecutarse dentro de una
  `Mutiny.Session`, es decir, bajo `@WithSession`, `@WithSessionOnDemand` o
  `@WithTransaction`.
- Dimensiona el pool reactivo explícitamente (`quarkus.datasource.reactive.max-size`,
  20 por defecto): en reactivo el cuello de botella se desplaza del número de hilos al
  número de conexiones ([datasource](../03-datos/datasource.md)).

## 4. Devuelve el `Uni`, no lo consumas

En un endpoint, `return uni;` deja que Quarkus gestione suscripción, cancelación y
propagación de contexto. Si haces `uni.await().indefinitely()` para "simplificar", estás
convirtiendo código asíncrono en bloqueante en el peor sitio posible. La conversión a
imperativo está documentada como caso excepcional
([reactive-to-imperative](../11-mutiny/guias/reactive-to-imperative.md)).

Corolario: cancelar importa. Si el cliente HTTP corta la conexión, Quarkus cancela la
suscripción y tu pipeline debería dejar de trabajar. Eso solo funciona si la cadena es
realmente reactiva de punta a punta.

## 5. Trata los fallos como eventos de primera clase

- Define siempre un `onFailure()` explícito en los pipelines que cruzan la red.
- Reintenta con backoff, no en bucle cerrado:
  `retry().withBackOff(Duration.ofMillis(200), Duration.ofSeconds(5)).atMost(5)`
  ([retrying](../11-mutiny/tutoriales/retrying.md)).
- Filtra qué reintentas: un `400` no mejora reintentando; un `503` sí.
- Combina reintentos con `@CircuitBreaker` y `@Timeout` de
  [SmallRye Fault Tolerance](../06-resiliencia/smallrye-fault-tolerance.md), que soporta
  métodos que devuelven `Uni`.
- Ponle un timeout a cada llamada remota: `ifNoItem().after(...)`. Sin timeout, la
  contrapresión se convierte en acumulación de memoria.

## 6. Respeta la contrapresión en los `Multi`

- `collect().asList()` sobre un stream ilimitado es una fuga de memoria con otro nombre.
- Para lotes usa `group().intoLists().of(n)` o ventanas temporales
  ([grouping-items](../11-mutiny/guias/grouping-items.md)).
- En Kafka, el paralelismo y el ack se controlan por canal
  (`@Blocking(ordered = false)`, `max-inflight-messages`, estrategias de commit):
  revisa la sección de rendimiento de la [guía de Kafka](../04-mensajeria/kafka.md).
- Si un productor es más rápido que el consumidor, decide la política de forma explícita
  (`onOverflow().buffer(n)`, `.drop()`, `.dropPreviousItems()`) en lugar de dejar el
  buffer por defecto ([controlling-demand](../11-mutiny/guias/controlling-demand.md)).

## 7. Cuida el contexto (logs, seguridad, trazas)

- No lances trabajo con `new Thread()`, `CompletableFuture.supplyAsync()` sin ejecutor o
  pools propios: pierdes el contexto duplicado y con él `@RequestScoped`, la identidad de
  seguridad y el `traceId` ([duplicated context](../01-fundamentos/duplicated-context.md)).
- Usa los ejecutores de `Infrastructure` o la
  [propagación de contexto](../01-fundamentos/context-propagation.md).
- Verifica en un entorno real que las trazas de OpenTelemetry cruzan los saltos de hilo
  ([opentelemetry](../07-observabilidad/opentelemetry.md)).

## 8. Hilos virtuales: úsalos donde encajan

`@RunOnVirtualThread` permite escribir código imperativo con coste de hilo casi nulo, y
es una buena salida cuando el equipo no quiere pipelines. Pero:

- No elimina la necesidad de contrapresión en streaming; para eso sigue estando `Multi`.
- Ojo con el *pinning* (bloques `synchronized` sobre operaciones de I/O) y con librerías
  que usan `ThreadLocal` de forma intensiva.
- Sigue habiendo un límite real: el pool de conexiones a base de datos.

Detalles y limitaciones actuales: [virtual-threads](../01-fundamentos/virtual-threads.md)
y [rest-virtual-threads](../02-web-http/rest-virtual-threads.md).

## 9. Testea el comportamiento asíncrono, no solo el resultado

- Usa `UniAssertSubscriber` / `AssertSubscriber` para afirmar sobre eventos, no solo
  sobre el valor final ([testing](../11-mutiny/guias/testing.md)).
- Apóyate en [Dev Services](../09-testing/dev-services.md) para tener Postgres, Kafka o
  Redis reales en los tests en lugar de mocks que ocultan el comportamiento de I/O.
- Añade al menos un test de carga simple: los problemas de modelo de ejecución solo se
  ven con concurrencia ([performance-measure](../08-rendimiento-nativo/performance-measure.md)).

## 10. Observa lo que importa en reactivo

Métricas que de verdad predicen incidentes en este modelo:

| Métrica | Por qué |
| --- | --- |
| Tiempo de ejecución en event loop / avisos de `BlockedThreadChecker` | Detecta bloqueos antes de que se noten en latencia |
| Uso del pool de conexiones reactivo (en uso / espera) | El nuevo cuello de botella tras eliminar hilos |
| Tamaño de colas y buffers de mensajería, *lag* de consumidor | Señal temprana de contrapresión |
| Latencia p99, no la media | El modelo reactivo mejora la cola de la distribución; ahí se ve |
| Uso del worker pool | Indica cuánto código "reactivo" acaba en realidad en el worker |

Ver [observabilidad](../07-observabilidad/observability.md) y
[Micrometer](../07-observabilidad/telemetry-micrometer.md).
