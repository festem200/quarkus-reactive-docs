# Dev Services Overview

> **Guia oficial:** <https://quarkus.io/guides/dev-services>  
> **Fuente:** `docs/src/main/asciidoc/dev-services.adoc` en [quarkusio/quarkus@3.38.2](https://github.com/quarkusio/quarkus/blob/3.38.2/docs/src/main/asciidoc/dev-services.adoc)  
> **Version documentada:** Quarkus 3.38.2 · **Sincronizado:** 2026-08-17 · **Licencia:** Apache-2.0

## What Are Dev Services?

Quarkus supports the automatic provisioning of unconfigured services in development and test mode. We refer to this capability
as Dev Services. If you include an extension and don’t configure it then
Quarkus will automatically start the relevant service (usually using [Testcontainers](https://www.testcontainers.org/) behind the scenes) and wire up your
application to use this service.

For a tutorial showing how to get started writing an application with persistence and Dev Services, see [Your Second Quarkus Application](getting-started-dev-services.md).

## Using Dev Services

Dev Services are designed to be frictionless, so they will be automatically started any time you include an extension which supports
Dev Services, as long as you don’t configure a connection to an external service.

**📌 NOTE**\
In order to use most Dev Services you will need a working container environment (remote environments are supported).
If you don’t have a container environment, such as Docker or Podman, installed you will need to configure your services normally.

The default startup timeout for Dev Services is 60s, if this is not enough you can increase it with the `quarkus.devservices.timeout` property.

To configure a production service but continue to use Dev Services in development and test modes, use [configuration profiles](../01-fundamentos/config-reference.md#default-profiles).

For example,

```properties
# configure your datasource
%prod.quarkus.datasource.db-kind = postgresql
%prod.quarkus.datasource.username = prod-admin
%prod.quarkus.datasource.password = super-secret
%prod.quarkus.datasource.jdbc.url = jdbc:postgresql://localhost:5432/mydatabase
```

## Disabling Dev Services

All this functionality is part of the Quarkus `deployment` modules, so does not affect the production application in any
way. If you want to disable all Dev Services you can use the `quarkus.devservices.enabled=false` config property, although
in most cases this is not necessary as simply configuring the service will result in the Dev Service being disabled automatically.

## Compose Dev Services

[Quarkus Compose Dev Services](https://quarkus.io/guides/compose-dev-services) allows you to define custom dev services using the [Compose specification](https://compose-spec.io/).

## Platform Dev Services

This section lists all the Dev Services available in the Quarkus Platform.

### AMQP

The AMQP Dev Service will be enabled when the `quarkus-messaging-amqp` extension is present in your application, and
the broker address has not been explicitly configured. More information can be found in the
[AMQP Dev Services Guide](../04-mensajeria/amqp-dev-services.md).

**📌 NOTE**\
La tabla de configuracion generada `quarkus-messaging-amqp_quarkus.amqp.devservices` se produce al construir la documentacion y no existe en el codigo fuente. Consulta la referencia de configuracion en https://quarkus.io/guides/all-config

### Apicurio Registry

The Apicurio Dev Service will be enabled when the `quarkus-apicurio-registry-avro` extension is present in your application, and it’s
address has not been explicitly configured. More information can be found in the
[Apicurio Registry Dev Services Guide](https://quarkus.io/guides/apicurio-registry-dev-services).

**📌 NOTE**\
La tabla de configuracion generada `quarkus-schema-registry-devservice_quarkus.apicurio-registry.devservices` se produce al construir la documentacion y no existe en el codigo fuente. Consulta la referencia de configuracion en https://quarkus.io/guides/all-config

### Databases

The database Dev Services will be enabled when a reactive or JDBC datasource extension is present in the application,
and the database URL has not been configured. More information can be found in the
[Databases Dev Services Guide](../03-datos/databases-dev-services.md).

Quarkus provides Dev Services for all databases it supports. Most of these are run in a container, except
H2 which is run in-process. Dev Services are supported for both JDBC and reactive drivers.

Those relational databases that are running in a container are started using Testcontainers and support "reusable instances";
this implies that if you add the property `testcontainers.reuse.enable=true` in your Testcontainers configuration file,
a property file named `.testcontainers.properties` in your user home, then the databases will not be stopped aggressively
after each run, and can be reused.

N.B. if you opt in for this feature, Quarkus will not reset the state of the database between runs unless you explicitly configure it to.

**📌 NOTE**\
La tabla de configuracion generada `quarkus-datasource_quarkus.datasource.devservices` se produce al construir la documentacion y no existe en el codigo fuente. Consulta la referencia de configuracion en https://quarkus.io/guides/all-config

### Kafka

The Kafka Dev Service will be enabled when the `quarkus-kafka-client` extension is present in your application, and
the broker address has not been explicitly configured. More information can be found in the
[Kafka Dev Services Guide](../04-mensajeria/kafka-dev-services.md).

**📌 NOTE**\
La tabla de configuracion generada `quarkus-kafka-client_quarkus.kafka.devservices` se produce al construir la documentacion y no existe en el codigo fuente. Consulta la referencia de configuracion en https://quarkus.io/guides/all-config

### Keycloak

The Keycloak Dev Service will be enabled when the `quarkus-oidc` extension is present in your application, and
the server address has not been explicitly configured. More information can be found in the
[OIDC Dev Services Guide](https://quarkus.io/guides/security-openid-connect-dev-services).

**📌 NOTE**\
La tabla de configuracion generada `quarkus-devservices-keycloak_quarkus.keycloak` se produce al construir la documentacion y no existe en el codigo fuente. Consulta la referencia de configuracion en https://quarkus.io/guides/all-config

A lightweight [OIDC Dev Service](#oidc) is also available as an alternative to Keycloak.

### Kubernetes

The Kubernetes Dev Service will be enabled when the `kubernetes-client` extension is present in your application, and
the API server address has not been explicitly configured. More information can be found in the
[Kubernetes Dev Services Guide](https://quarkus.io/guides/kubernetes-dev-services).

**📌 NOTE**\
La tabla de configuracion generada `quarkus-kubernetes-client_quarkus.kubernetes-client.devservices` se produce al construir la documentacion y no existe en el codigo fuente. Consulta la referencia de configuracion en https://quarkus.io/guides/all-config

### LRA

The Narayana LRA Dev Service will be enabled when the `quarkus-narayana-lra` extension is present in your application, and the coordinator URL has not been explicitly configured. More information can be found in the
[Narayana LRA Dev Services Guide](../06-resiliencia/lra-dev-services.md).

**📌 NOTE**\
La tabla de configuracion generada `quarkus-narayana-lra_quarkus.lra.devservices` se produce al construir la documentacion y no existe en el codigo fuente. Consulta la referencia de configuracion en https://quarkus.io/guides/all-config

### MongoDB

The MongoDB Dev Service will be enabled when the `quarkus-mongodb-client` extension is present in your application, and
the server address has not been explicitly configured. More information can be found in the
[MongoDB Guide](../03-datos/mongodb-dev-services.md).

**📌 NOTE**\
La tabla de configuracion generada `quarkus-mongodb-client_quarkus.mongodb.devservices` se produce al construir la documentacion y no existe en el codigo fuente. Consulta la referencia de configuracion en https://quarkus.io/guides/all-config

### OIDC

A standalone OIDC Dev Service is available as a lightweight alternative to [Keycloak](#keycloak).
It is enabled by default when Docker and Podman are not available, or it can be explicitly enabled with `quarkus.oidc.devservices.enabled=true`.
More information can be found in the
[OIDC Dev Services Guide](https://quarkus.io/guides/security-openid-connect-dev-services#dev-services-for-oidc).

**📌 NOTE**\
La tabla de configuracion generada `quarkus-devservices-oidc_quarkus.oidc` se produce al construir la documentacion y no existe en el codigo fuente. Consulta la referencia de configuracion en https://quarkus.io/guides/all-config

### RabbitMQ

The RabbitMQ Dev Service will be enabled when the `quarkus-messaging-rabbitmq` extension is present in your application, and
the broker address has not been explicitly configured. More information can be found in the
[RabbitMQ Dev Services Guide](../04-mensajeria/rabbitmq-dev-services.md).

**📌 NOTE**\
La tabla de configuracion generada `quarkus-messaging-rabbitmq_quarkus.rabbitmq.devservices` se produce al construir la documentacion y no existe en el codigo fuente. Consulta la referencia de configuracion en https://quarkus.io/guides/all-config

### Pulsar

The Pulsar Dev Service will be enabled when the `quarkus-messaging-pulsar` extension is present in your application, and
the broker address has not been explicitly configured. More information can be found in the
[Pulsar Dev Services Guide](../04-mensajeria/pulsar-dev-services.md).

**📌 NOTE**\
La tabla de configuracion generada `quarkus-messaging-pulsar_quarkus.pulsar.devservices` se produce al construir la documentacion y no existe en el codigo fuente. Consulta la referencia de configuracion en https://quarkus.io/guides/all-config

### Redis

The Redis Dev Service will be enabled when the `quarkus-redis-client` extension is present in your application, and
the server address has not been explicitly configured. More information can be found in the
[Redis Dev Services Guide](../03-datos/redis-dev-services.md).

**📌 NOTE**\
La tabla de configuracion generada `quarkus-redis-client_quarkus.redis.devservices` se produce al construir la documentacion y no existe en el codigo fuente. Consulta la referencia de configuracion en https://quarkus.io/guides/all-config

### Vault

The Vault Dev Service will be enabled when the `quarkus-vault` extension is present in your application, and
the server address has not been explicitly configured. More information can be found in the
[Vault Guide](https://docs.quarkiverse.io/quarkus-vault/dev/index.html#dev-services).

### Infinispan

The Infinispan Dev Service will be enabled when the `quarkus-infinispan-client` extension is present in your application, and
the server address has not been explicitly configured. More information can be found in the
[Infinispan Dev Services Guide](https://quarkus.io/guides/infinispan-dev-services).

**📌 NOTE**\
La tabla de configuracion generada `quarkus-infinispan-client_quarkus.infinispan-client.devservices` se produce al construir la documentacion y no existe en el codigo fuente. Consulta la referencia de configuracion en https://quarkus.io/guides/all-config

### Elasticsearch

The Elasticsearch Dev Service will be enabled when one of the Elasticsearch based extensions (Elasticsearch client or Hibernate Search ORM Elasticsearch)
is present in your application, and the server address has not been explicitly configured.
More information can be found in the [Elasticsearch Dev Services Guide](https://quarkus.io/guides/elasticsearch-dev-services).

**📌 NOTE**\
La tabla de configuracion generada `quarkus-elasticsearch-rest-client_quarkus.elasticsearch.devservices` se produce al construir la documentacion y no existe en el codigo fuente. Consulta la referencia de configuracion en https://quarkus.io/guides/all-config

### Observability

The Observability Dev Services will be enabled when the `quarkus-observability-devservices` extension is present in your application, and
there is at least one dev resource on the classpath. More information can be found in the
[Observability Dev Services Guide](../07-observabilidad/observability-devservices.md).

**📌 NOTE**\
La tabla de configuracion generada `quarkus-observability-devservices` se produce al construir la documentacion y no existe en el codigo fuente. Consulta la referencia de configuracion en https://quarkus.io/guides/all-config

## Dev Services beyond the Quarkus Platform

Many Quarkiverse extensions which are not in the Quarkus Platform also offer Dev Services.

Here are some highlights.

### Neo4j

The Neo4j Dev Service will be enabled when the `quarkus-neo4j` extension is present in your application, and
the server address has not been explicitly configured. More information can be found in the
[Neo4j Guide](https://docs.quarkiverse.io/quarkus-neo4j/dev/index.html#dev-services).

### WireMock

The WireMock extension starts WireMock as a Dev Service. It is a test-focussed extension, designed to run in dev and test mode only.
More information can be found in the [WireMock Guide](https://docs.quarkiverse.io/quarkus-wiremock/dev/index.html).

### Microcks

The Microcks Quarkus extension includes a Microcks Dev Service. The Dev Service manages mocks for dependencies and contract-testing your API endpoints.
See the extension [README.md](https://github.com/microcks/microcks-quarkus) for more information.
