# Matriz de extensiones: reactivo frente a bloqueante

Guía para elegir extensión sabiendo qué modelo de ejecución impone. Los nombres son los
`artifactId` del grupo `io.quarkus`. Verificados contra la documentación de Quarkus
incluida en este repositorio.

## Capa web

| Necesidad | Extensión reactiva | Alternativa bloqueante | Guía |
| --- | --- | --- | --- |
| API REST | `quarkus-rest` (+ `quarkus-rest-jackson`) | `quarkus-resteasy` (+ `quarkus-resteasy-jackson`) | [rest](../02-web-http/rest.md) |
| Cliente REST | `quarkus-rest-client` (+ `-jackson`) | `quarkus-resteasy-client` | [rest-client](../02-web-http/rest-client.md) |
| Rutas ligeras sobre Vert.x | `quarkus-reactive-routes` | — | [reactive-routes](../02-web-http/reactive-routes.md) |
| WebSockets | `quarkus-websockets-next` | `quarkus-websockets` (Jakarta WebSockets) | [websockets-next](../02-web-http/websockets-next-reference.md) |
| GraphQL | `quarkus-smallrye-graphql` (soporta `Uni`/`Multi`) | — | [smallrye-graphql](../02-web-http/smallrye-graphql.md) |
| gRPC | `quarkus-grpc` (Mutiny stubs por defecto) | — | [grpc](../05-grpc/grpc.md) |

`quarkus-rest` es el runtime REST recomendado y el que se instala por defecto en los
proyectos nuevos; el nombre antiguo era RESTEasy Reactive. `quarkus-resteasy` es la
variante clásica bloqueante, que sigue soportada para aplicaciones imperativas.

## Bases de datos

| Motor | Cliente reactivo | Cliente bloqueante | Guía |
| --- | --- | --- | --- |
| PostgreSQL | `quarkus-reactive-pg-client` | `quarkus-jdbc-postgresql` | [reactive-sql-clients](../03-datos/reactive-sql-clients.md) |
| MySQL / MariaDB | `quarkus-reactive-mysql-client` | `quarkus-jdbc-mysql`, `quarkus-jdbc-mariadb` | idem |
| MS SQL Server | `quarkus-reactive-mssql-client` | `quarkus-jdbc-mssql` | idem |
| Oracle | `quarkus-reactive-oracle-client` | `quarkus-jdbc-oracle` | idem |
| DB2 | `quarkus-reactive-db2-client` | `quarkus-jdbc-db2` | idem |
| ORM | `quarkus-hibernate-reactive`, `quarkus-hibernate-reactive-panache` | `quarkus-hibernate-orm`, `quarkus-hibernate-orm-panache` | [hibernate-reactive](../03-datos/hibernate-reactive.md) |
| REST + datos generado | `quarkus-hibernate-reactive-rest-data-panache` | `quarkus-hibernate-orm-rest-data-panache` | [rest-data-panache](../02-web-http/rest-data-panache.md) |
| MongoDB | `quarkus-mongodb-client` / `quarkus-mongodb-panache` con las variantes `Reactive*` (`ReactivePanacheMongoEntity`, `ReactivePanacheMongoRepository`) | mismas extensiones, API síncrona | [mongodb-panache](../03-datos/mongodb-panache.md) |
| Redis | `quarkus-redis-client` — expone `ReactiveRedisDataSource` y `RedisDataSource` | misma extensión, API síncrona | [redis](../03-datos/redis.md) |
| Cassandra | extensión de Quarkiverse con API reactiva | — | [cassandra](../03-datos/cassandra.md) |
| Elasticsearch | `quarkus-elasticsearch-rest-client` / `quarkus-elasticsearch-java-client` (ambos con API asíncrona) | — | [elasticsearch](../03-datos/elasticsearch.md) |
| Infinispan | `quarkus-infinispan-client` (API Mutiny disponible) | — | [infinispan-client](../03-datos/infinispan-client.md) |

Regla: si el endpoint devuelve `Uni`/`Multi` y por debajo hay una extensión `jdbc-*`,
tienes un bloqueo escondido. O cambias de cliente, o marcas el método `@Blocking`.

## Mensajería

| Broker | Extensión | Guía |
| --- | --- | --- |
| Kafka | `quarkus-messaging-kafka` | [kafka](../04-mensajeria/kafka.md) |
| Kafka Streams | `quarkus-kafka-streams` | [kafka-streams](../04-mensajeria/kafka-streams.md) |
| AMQP 1.0 | `quarkus-messaging-amqp` | [amqp](../04-mensajeria/amqp.md) |
| RabbitMQ | `quarkus-messaging-rabbitmq` | [rabbitmq](../04-mensajeria/rabbitmq.md) |
| Pulsar | `quarkus-messaging-pulsar` | [pulsar](../04-mensajeria/pulsar.md) |
| JMS | `quarkus-qpid-jms` (AMQP) o `quarkus-artemis-jms` — API JMS, modelo **bloqueante** | [jms](../04-mensajeria/jms.md) |
| Correo | `quarkus-mailer` (`ReactiveMailer` y `Mailer`) | [mailer](../04-mensajeria/mailer.md) |

Todas las extensiones `messaging-*` implementan MicroProfile Reactive Messaging con
Mutiny: `@Incoming`, `@Outgoing`, `@Channel`, contrapresión y ack/nack por mensaje.

## Plataforma y transversales

| Necesidad | Extensión | Nota |
| --- | --- | --- |
| Acceso directo a Vert.x | `quarkus-vertx` | Inyecta `io.vertx.mutiny.core.Vertx`, EventBus, timers ([vertx](../01-fundamentos/vertx.md)) |
| Resiliencia | `quarkus-smallrye-fault-tolerance` | `@Retry`, `@Timeout`, `@CircuitBreaker` con soporte para `Uni` |
| Service discovery / balanceo | `quarkus-smallrye-stork` | Integra con REST client y gRPC ([stork](../06-resiliencia/stork.md)) |
| Caché | `quarkus-cache` | Soporta métodos que devuelven `Uni` ([cache](../03-datos/cache.md)) |
| Salud | `quarkus-smallrye-health` | Checks que pueden ser `Uni` |
| Métricas | `quarkus-micrometer-registry-*` / `quarkus-opentelemetry` | [observabilidad](../07-observabilidad/observability.md) |
| Scheduling | `quarkus-scheduler`, `quarkus-quartz` | Métodos `@Scheduled` pueden devolver `Uni` ([scheduler-reference](../06-resiliencia/scheduler-reference.md)) |
| Plantillas | `quarkus-qute`, `quarkus-rest-qute` | Qute renderiza de forma asíncrona ([qute](../02-web-http/qute.md)) |
| Señales entre componentes | `quarkus-signals` | Emisión/recepción desacoplada, ejecución asíncrona ([signals](../01-fundamentos/signals.md)) |

## Cómo comprobarlo en tu propio proyecto

```bash
./mvnw quarkus:list-extensions
```

Y para ver qué se está ejecutando dónde, arranca en modo dev y observa los nombres de
hilo en los logs: `vert.x-eventloop-thread-*` (event loop), `executor-thread-*` (worker),
`quarkus-virtual-thread-*` (hilos virtuales).
