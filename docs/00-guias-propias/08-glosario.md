# Glosario reactivo (Quarkus / Mutiny / Vert.x)

**Ack / Nack** — Confirmación (o rechazo) del procesamiento de un mensaje en Reactive
Messaging. Determina si el mensaje se marca como consumido o se reencola / envía a DLQ.

**Backpressure (contrapresión)** — Mecanismo por el que el consumidor indica cuántos
elementos puede aceptar, evitando que un productor rápido lo desborde. Es parte del
contrato de Reactive Streams y está implementado en `Multi`.

**Blocking (bloqueante)** — Operación que retiene el hilo hasta completarse. Aceptable en
worker threads e hilos virtuales; prohibida en event loops.

**Contexto duplicado (duplicated context)** — Copia del contexto local de Vert.x asociada
a una petición concreta, que permite tener estado por petición (`@RequestScoped`, MDC,
identidad de seguridad, trazas) aunque varios hilos y varias peticiones compartan el mismo
event loop.

**Dev Services** — Capacidad de Quarkus para arrancar automáticamente en desarrollo y test
los servicios que necesita la aplicación (Postgres, Kafka, Redis…), normalmente vía
contenedores, sin configuración.

**Event loop** — Hilo que atiende eventos de I/O sin bloquearse. Quarkus crea por defecto
uno por núcleo de CPU. Bloquearlo degrada a todas las peticiones que atiende.

**Fluent API** — Estilo de API encadenada que usa Mutiny (`onItem().transform(...)`),
diseñado para que el autocompletado guíe hacia el operador correcto.

**Hilo virtual (virtual thread)** — Hilo ligero gestionado por la JVM (Project Loom,
JDK 21+). Permite escribir código bloqueante con coste muy bajo. En Quarkus se activa por
método con `@RunOnVirtualThread`.

**I/O thread** — Sinónimo de event loop en la terminología de Quarkus.

**Item** — Elemento emitido por un `Uni` o un `Multi`. En Mutiny se habla de eventos
(item, fallo, completado, suscripción, cancelación), no solo de valores.

**Multi&lt;T&gt;** — Tipo de Mutiny que representa un flujo de 0..n items seguidos de un
evento de completado o de fallo. Implementa `Publisher` de Reactive Streams.

**Mutiny** — Biblioteca de programación reactiva de SmallRye, API reactiva principal de
Quarkus. Su diseño es orientado a eventos y explícitamente navegable.

**Operador** — Cada paso de un pipeline (`transform`, `select`, `retry`…). No ejecuta nada
por sí mismo: describe qué hacer cuando llegue un evento.

**Panache** — Capa de Quarkus sobre Hibernate (ORM o Reactive) y MongoDB que reduce el
boilerplate con entidades activas o repositorios. En su variante reactiva devuelve `Uni`.

**Pinning** — Situación en la que un hilo virtual queda "clavado" a su hilo portador (por
ejemplo dentro de un bloque `synchronized` que hace I/O), anulando la ventaja del modelo.

**Pipeline** — Cadena de operadores construida sobre un `Uni` o `Multi`. Es perezosa: no
ocurre nada hasta que hay una suscripción.

**Reactive Messaging** — Especificación (MicroProfile / SmallRye) para conectar métodos a
canales de mensajería mediante `@Incoming`, `@Outgoing` y `@Channel`.

**Reactive Streams** — Estándar que define la interoperabilidad entre librerías reactivas
con contrapresión (`Publisher`, `Subscriber`, `Subscription`, `Processor`). Mutiny lo
implementa y es interoperable con RxJava, Reactor y Flow del JDK.

**RESTEasy Reactive** — Nombre anterior del runtime REST reactivo de Quarkus, hoy llamado
simplemente **Quarkus REST** (`quarkus-rest`).

**Stork** — Librería de descubrimiento de servicios y balanceo de carga del lado del
cliente, integrada con el cliente REST y gRPC de Quarkus.

**Suscripción (subscribe)** — Acto de conectarse a un `Uni`/`Multi` que dispara realmente
la ejecución. En un endpoint Quarkus la realiza el framework, no tu código.

**Uni&lt;T&gt;** — Tipo de Mutiny que representa un resultado asíncrono único: emitirá un
item (posiblemente `null`) o un fallo.

**Vert.x** — Toolkit reactivo sobre Netty que constituye el motor de I/O de Quarkus. Está
presente incluso en aplicaciones puramente imperativas.

**Worker thread** — Hilo de un pool acotado (`quarkus.thread-pool.max-threads`, 20 por
defecto) donde se ejecuta el código bloqueante.
