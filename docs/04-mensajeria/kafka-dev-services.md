# Dev Services for Kafka

> **Guia oficial:** <https://quarkus.io/guides/kafka-dev-services>  
> **Fuente:** `docs/src/main/asciidoc/kafka-dev-services.adoc` en [quarkusio/quarkus@3.38.2](https://github.com/quarkusio/quarkus/blob/3.38.2/docs/src/main/asciidoc/kafka-dev-services.adoc)  
> **Version documentada:** Quarkus 3.38.2 · **Sincronizado:** 2026-08-17 · **Licencia:** Apache-2.0

If any Kafka-related extension is present (e.g. `quarkus-messaging-kafka`), Dev Services for Kafka automatically starts a Kafka broker in dev mode and when running tests.
So, you don’t have to start a broker manually.
The application is configured automatically.

**❗ IMPORTANT**\
By default, Dev Services for Kafka uses the [Apache Kafka native](https://hub.docker.com/r/apache/kafka-native) image which starts in ~1 second.

## Enabling / Disabling Dev Services for Kafka

Dev Services for Kafka is automatically enabled unless:

* `quarkus.kafka.devservices.enabled` is set to `false`
* the `kafka.bootstrap.servers` is configured
* all the Reactive Messaging Kafka channels have the `bootstrap.servers` attribute set

Dev Services for Kafka relies on Docker to start the broker.
If your environment does not support Docker, you will need to start the broker manually, or connect to an already running broker.
You can configure the broker address using `kafka.bootstrap.servers`.

## Shared broker

Most of the time you need to share the broker between applications.
Dev Services for Kafka implements a _service discovery_ mechanism for your multiple Quarkus applications running in _dev_ mode to share a single broker.

**📌 NOTE**\
Dev Services for Kafka starts the container with the `quarkus-dev-service-kafka` label which is used to identify the container.

If you need multiple (shared) brokers, you can configure the `quarkus.kafka.devservices.service-name` attribute and indicate the broker name.
It looks for a container with the same value, or starts a new one if none can be found.
The default service name is `kafka`.

Sharing is enabled by default in dev mode, but disabled in test mode.
You can disable the sharing with `quarkus.kafka.devservices.shared=false`.

## Setting the port

By default, Dev Services for Kafka picks a random port and configures the application.
You can set the port by configuring the `quarkus.kafka.devservices.port` property.

Note that the Kafka advertised address is automatically configured with the chosen port.

## Configuring the image

Dev Services for Kafka supports the following container providers:

***upstream-kafka-native*** (default) uses the official [Apache Kafka native](https://hub.docker.com/r/apache/kafka-native) image, compiled with GraalVM for fast startup.

***upstream-kafka*** uses the official [Apache Kafka](https://hub.docker.com/r/apache/kafka) JVM image.

```properties
quarkus.kafka.devservices.provider=upstream-kafka
```

***Redpanda*** is a Kafka compatible event streaming platform.
You can select any version from https://hub.docker.com/r/redpandadata/redpanda.

```properties
quarkus.kafka.devservices.provider=redpanda
```

***Strimzi*** provides container images and Operators for running Apache Kafka on Kubernetes.
While Strimzi is optimized for Kubernetes, the images work perfectly in classic container environments.
Strimzi container images run a Kafka broker on JVM, which is slower to start.

```properties
quarkus.kafka.devservices.provider=strimzi
```

For Strimzi, you can select any image with a Kafka version which has Kraft support (2.8.1 and higher) from https://quay.io/repository/strimzi-test-container/test-container?tab=tags

```properties
quarkus.kafka.devservices.image-name=quay.io/strimzi-test-container/test-container:0.115.0-kafka-4.2.0
```

## Configuring Kafka topics

You can configure the Dev Services for Kafka to create topics once the broker is started.
Topics are created with given number of partitions and 1 replica.
The syntax is the following:

```properties
quarkus.kafka.devservices.topic-partitions.<topic-name>=<number-of-partitions>
```

The following example creates a topic named `test` with three partitions, and a second topic named `messages` with two partitions.

```properties
quarkus.kafka.devservices.topic-partitions.test=3
quarkus.kafka.devservices.topic-partitions.messages=2
```

If a topic already exists with the given name, the creation is skipped,
without trying to re-partition the existing topic to a different number of partitions.

You can configure timeout for Kafka admin client calls used in topic creation using `quarkus.kafka.devservices.topic-partitions-timeout`, it defaults to 2 seconds.

## Transactional and Idempotent producers support

By default, the Redpanda broker is configured to enable transactions and idempotence features.
You can disable those using:

```properties
quarkus.kafka.devservices.redpanda.transaction-enabled=false
```

**📌 NOTE**\
Redpanda transactions does not support exactly-once processing.

## Compose

The Kafka Dev Services supports [Compose Dev Services](https://quarkus.io/guides/compose-dev-services).
It relies on a `compose-devservices.yml`, such as:

```yaml
name: <application name>
services:
  kafka:
    image: apache/kafka-native:4.2.0
    restart: "no"
    ports:
      - '9092'
    labels:
      io.quarkus.devservices.compose.exposed_ports: /etc/kafka/docker/ports
    environment:
      KAFKA_NODE_ID: 1
      KAFKA_PROCESS_ROLES: broker,controller
      KAFKA_LISTENERS: PLAINTEXT://:9092,CONTROLLER://:9093
      KAFKA_CONTROLLER_LISTENER_NAMES: CONTROLLER
      KAFKA_CONTROLLER_QUORUM_VOTERS: 1@localhost:9093
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
      KAFKA_TRANSACTION_STATE_LOG_REPLICATION_FACTOR: 1
      KAFKA_TRANSACTION_STATE_LOG_MIN_ISR: 1
      KAFKA_GROUP_INITIAL_REBALANCE_DELAY_MS: 0
      KAFKA_NUM_PARTITIONS: 3
    command: "/kafka.sh"
    volumes:
      - './kafka.sh:/kafka.sh'
```

For the broker to advertise its externally accessible address to clients, it requires an additional file `kafka.sh` as described in [Exposing port mappings to running containers](https://quarkus.io/guides/compose-dev-services#exposing-port-mappings-to-running-containers).

## Configuration reference

**📌 NOTE**\
La tabla de configuracion generada `quarkus-kafka-client_quarkus.kafka.devservices` se produce al construir la documentacion y no existe en el codigo fuente. Consulta la referencia de configuracion en https://quarkus.io/guides/all-config
