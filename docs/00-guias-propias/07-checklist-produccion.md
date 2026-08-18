# Checklist antes de llevar a producción una aplicación Quarkus reactiva

Lista de verificación pensada para revisión previa a despliegue. Cada punto enlaza a la
guía oficial correspondiente.

## Modelo de ejecución

- [ ] Ningún endpoint que devuelva `Uni`/`Multi` llama a JDBC, JTA, `Thread.sleep`,
      ficheros o SDKs bloqueantes sin `@Blocking` o `@RunOnVirtualThread`.
- [ ] Los logs de pruebas de carga no muestran avisos de `BlockedThreadChecker`
      (`Thread blocked ... time limit is 2000 ms`).
- [ ] Las llamadas bloqueantes inevitables están aisladas en el worker pool y ese pool
      está dimensionado (`quarkus.thread-pool.max-threads`).
- [ ] Se ha revisado el efecto de `@Transactional` sobre el modelo de ejecución en cada
      endpoint. → [modelo de ejecución](02-modelo-de-ejecucion.md)

## Datos

- [ ] `quarkus.datasource.reactive.max-size` fijado a un valor razonado, no al valor por
      defecto por inercia. → [datasource](../03-datos/datasource.md)
- [ ] Ese valor es compatible con `max_connections` del servidor de base de datos
      multiplicado por el número de réplicas del servicio.
- [ ] Todo método Panache reactivo se ejecuta bajo `@WithSession` / `@WithTransaction`.
- [ ] No se mezclan `@Transactional` (JTA) y anotaciones reactivas de Panache.
- [ ] Las migraciones (Flyway/Liquibase) están contempladas: usan JDBC, no el cliente
      reactivo. → [flyway](../03-datos/flyway.md)

## Resiliencia

- [ ] Toda llamada remota tiene timeout explícito (`ifNoItem().after(...)` o `@Timeout`).
- [ ] Los reintentos usan backoff y filtran por tipo de error.
- [ ] Hay `@CircuitBreaker` en las integraciones que pueden degradarse.
      → [fault tolerance](../06-resiliencia/smallrye-fault-tolerance.md)
- [ ] Existe una respuesta degradada definida para cada dependencia crítica.
- [ ] Se ha evaluado [load shedding](../06-resiliencia/load-shedding-reference.md) si el
      servicio recibe picos.

## Mensajería (si aplica)

- [ ] Estrategia de commit y de ack/nack decidida explícitamente por canal, no por defecto.
- [ ] Configurado el comportamiento ante fallo (`failure-strategy`: `fail`, `ignore`,
      `dead-letter-queue`). → [kafka](../04-mensajeria/kafka.md)
- [ ] Paralelismo por canal ajustado (`@Blocking(ordered = false)`, `max-inflight-messages`).
- [ ] Monitorizado el *lag* del consumidor.
- [ ] Probado el comportamiento con el broker caído y al recuperarse.

## Contexto y seguridad

- [ ] No hay `new Thread()`, `CompletableFuture.supplyAsync()` sin ejecutor gestionado ni
      pools propios en el camino de la petición.
      → [duplicated context](../01-fundamentos/duplicated-context.md)
- [ ] Los beans `@RequestScoped` funcionan en las rutas asíncronas (test explícito).
- [ ] La identidad de seguridad se propaga en todo el pipeline.
- [ ] El `traceId` aparece en los logs incluso después de saltos de hilo.

## Observabilidad

- [ ] Métricas de event loop, worker pool y pool de conexiones exportadas.
- [ ] Trazas distribuidas activas y verificadas de extremo a extremo.
      → [opentelemetry](../07-observabilidad/opentelemetry.md)
- [ ] Health checks de liveness y readiness que **no** dependen de servicios externos
      lentos. → [smallrye-health](../06-resiliencia/smallrye-health.md)
- [ ] Alertas sobre p99, no solo sobre la media.

## Rendimiento

- [ ] Prueba de carga ejecutada con concurrencia realista, midiendo p99 y memoria.
      → [performance-measure](../08-rendimiento-nativo/performance-measure.md)
- [ ] Comparativa contra la línea base anterior (si se migró desde imperativo).
- [ ] Límites de memoria del contenedor ajustados a lo medido, no a una estimación.
- [ ] Si se compila a nativo: build y tests de integración nativos en CI.
      → [native-reference](../08-rendimiento-nativo/native-reference.md)

## Testing

- [ ] Tests de los pipelines con `UniAssertSubscriber` / `AssertSubscriber`.
      → [testing Mutiny](../11-mutiny/guias/testing.md)
- [ ] Tests de integración con Dev Services (base de datos y broker reales).
      → [dev-services](../09-testing/dev-services.md)
- [ ] Al menos un test que verifique el comportamiento ante timeout y ante fallo del
      servicio remoto.
- [ ] Test de cancelación: el cliente corta y el trabajo se detiene.

## Configuración y despliegue

- [ ] Secretos fuera del `application.properties` versionado.
      → [config-reference](../01-fundamentos/config-reference.md)
- [ ] Perfiles (`%dev`, `%test`, `%prod`) revisados; nada de Dev Services en producción.
- [ ] `quarkus.http.limits.*` y timeouts HTTP ajustados.
      → [http-reference](../02-web-http/http-reference.md)
- [ ] Interfaz de management separada si se exponen métricas y health.
      → [management-interface-reference](../08-rendimiento-nativo/management-interface-reference.md)
- [ ] TLS gestionado con el TLS registry.
      → [tls-registry-reference](../08-rendimiento-nativo/tls-registry-reference.md)
