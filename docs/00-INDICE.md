# Indice de la documentacion oficial

Documentacion oficial de Quarkus **3.38.2**, sincronizada el **2026-08-17**, convertida a Markdown desde el AsciiDoc original (Apache-2.0).

Las guias escritas para este repositorio (en espanol) estan en [`00-guias-propias/`](00-guias-propias/README.md): ruta de aprendizaje, modelo de ejecucion, chuleta de Mutiny, mejores practicas, antipatrones, matriz de extensiones, checklist de produccion y glosario.

La documentacion oficial de **Mutiny** (la API `Uni`/`Multi` que usa Quarkus) esta en [`11-mutiny/`](11-mutiny/README.md).

## Fundamentos del modelo reactivo

| Guia | De que trata |
| --- | --- |
| [quarkus-reactive-architecture](01-fundamentos/quarkus-reactive-architecture.md) | Quarkus is reactive. It’s even more than this: Quarkus unifies reactive and imperative programming. You don’t even have to choose: you can implement reactive components and imperative components then … |
| [getting-started-reactive](01-fundamentos/getting-started-reactive.md) | Reactive is a set of principles to build robust, efficient, and concurrent applications and systems. These principles let you handle more load than traditional approaches while using the resources (CP… |
| [mutiny-primer](01-fundamentos/mutiny-primer.md) | Mutiny is an intuitive, reactive programming library. It is the primary model to write reactive applications with Quarkus. |
| [vertx](01-fundamentos/vertx.md) | Vert.x is a toolkit for building reactive applications. As described in the Quarkus Reactive Architecture, Quarkus uses Vert.x underneath. |
| [vertx-reference](01-fundamentos/vertx-reference.md) | Vert.x is a toolkit for building reactive applications. As described in the Quarkus Reactive Architecture, Quarkus uses Vert.x underneath. |
| [reactive-event-bus](01-fundamentos/reactive-event-bus.md) | Quarkus allows different beans to interact using asynchronous events, thus promoting loose-coupling. The messages are sent to virtual addresses. It offers 3 types of delivery mechanism: |
| [duplicated-context](01-fundamentos/duplicated-context.md) | When using a traditional, blocking, and synchronous framework, processing of each request is performed in a dedicated thread. So, the same thread is used for the entire processing. You know that this … |
| [context-propagation](01-fundamentos/context-propagation.md) | Traditional blocking code uses ThreadLocal  variables to store contextual objects in order to avoid passing them as parameters everywhere. Many Quarkus extensions require those contextual objects to o… |
| [virtual-threads](01-fundamentos/virtual-threads.md) | This guide explains how to benefit from Java 21+ virtual threads in Quarkus application. |
| [signals](01-fundamentos/signals.md) | Signals allow application components to interact in a loosely coupled fashion, by emitting and receiving signals. A signal is an object -- optionally augmented with qualifiers and metadata -- that is … |
| [cdi](01-fundamentos/cdi.md) | In this guide we’re going to describe the basic principles of the Quarkus programming model that is based on the Jakarta Contexts and Dependency Injection 4.1 specification. The CDI reference guide de… |
| [cdi-reference](01-fundamentos/cdi-reference.md) | Quarkus DI solution (also called ArC) is based on the Jakarta Contexts and Dependency Injection 4.1 specification. It implements the CDI Lite specification, with selected improvements on top, and pass… |
| [lifecycle](01-fundamentos/lifecycle.md) | You often need to execute custom actions when the application starts and clean up everything when the application stops. This guide explains how to: |
| [config-reference](01-fundamentos/config-reference.md) | In this reference guide we’re going to describe various aspects of Quarkus configuration. A Quarkus application and Quarkus itself (core and extensions) are both configured via the same mechanism that… |

## HTTP, REST reactivo y WebSockets

| Guia | De que trata |
| --- | --- |
| [rest](02-web-http/rest.md) | This guide explains how to write REST Services with Quarkus REST in Quarkus. |
| [rest-json](02-web-http/rest-json.md) | JSON is now the lingua franca between microservices. |
| [rest-client](02-web-http/rest-client.md) | This guide explains how to use the REST Client in order to interact with REST APIs. REST Client is the REST Client implementation compatible with Quarkus REST (formerly RESTEasy Reactive). |
| [rest-virtual-threads](02-web-http/rest-virtual-threads.md) | In this guide, we see how you can use virtual threads in a REST application. Because virtual threads are all about I/O, we will also use the REST client. |
| [rest-data-panache](02-web-http/rest-data-panache.md) | A lot of web applications are monotonous CRUD applications with REST APIs that are tedious to write. To streamline this task, REST Data with Panache extension can generate the basic CRUD endpoints for… |
| [rest-migration](02-web-http/rest-migration.md) | Migrating from RESTEasy Classic to Quarkus REST (formerly RESTEasy Reactive) is straightforward in most cases, however there are a few cases that require some attention. This document provides a list … |
| [reactive-routes](02-web-http/reactive-routes.md) | Reactive routes propose an alternative approach to implement HTTP endpoints where you declare and chain routes. This approach became very popular in the JavaScript world, with frameworks like Express.… |
| [http-reference](02-web-http/http-reference.md) | This document clarifies different HTTP functionalities available in Quarkus. |
| [websockets-next-tutorial](02-web-http/websockets-next-tutorial.md) | This guide explains how your Quarkus application can utilize web sockets to create interactive web applications. In this guide, we will develop a very simple chat application using web sockets to rece… |
| [websockets-next-reference](02-web-http/websockets-next-reference.md) | The quarkus-websockets-next extension provides a modern declarative API to define WebSocket server and client endpoints. |
| [websockets](02-web-http/websockets.md) | This guide explains how your Quarkus application can utilize web sockets to create interactive web applications, in the context of an Undertow-based Quarkus application, or if you rely on Jakarta WebS… |
| [resteasy](02-web-http/resteasy.md) | This guide is about RESTEasy Classic, which used to be the default Jakarta REST (formerly known as JAX-RS) implementation until Quarkus 2.8. |
| [resteasy-client](02-web-http/resteasy-client.md) | This guide is about the REST Client compatible with RESTEasy Classic which used to be the default Jakarta REST (formerly known as JAX-RS) implementation until Quarkus 2.8. |
| [resteasy-client-multipart](02-web-http/resteasy-client-multipart.md) | This guide is about the multipart support of the REST Client compatible with RESTEasy Classic which used to be the default Jakarta REST (formerly known as JAX-RS) implementation until Quarkus 2.8. |
| [smallrye-graphql](02-web-http/smallrye-graphql.md) | This guide demonstrates how your Quarkus application can use SmallRye GraphQL, an implementation of the MicroProfile GraphQL specification. |
| [smallrye-graphql-client](02-web-http/smallrye-graphql-client.md) | This guide demonstrates how your Quarkus application can use the GraphQL client library. The client is implemented by the SmallRye GraphQL project. This guide is specifically geared towards the client… |
| [qute](02-web-http/qute.md) | Qute is a templating engine developed specifically for Quarkus. Reflection usage is minimized to reduce the size of native images. The API combines both the imperative and the non-blocking reactive st… |
| [qute-reference](02-web-http/qute-reference.md) | Qute is a templating engine designed specifically to meet the Quarkus needs. The usage of reflection is minimized to reduce the size of native images. The API combines both the imperative and the non-… |
| [security-cors](02-web-http/security-cors.md) | Enable and configure CORS in Quarkus to specify allowed origins, methods, and headers, guiding browsers in handling cross-origin requests safely. |
| [validation](02-web-http/validation.md) | This guide covers how to use Hibernate Validator/Bean Validation for: |
| [openapi-swaggerui](02-web-http/openapi-swaggerui.md) | This guide explains how your Quarkus application can expose its API description through an OpenAPI specification and how you can test it via a user-friendly UI named Swagger UI. |

## Acceso a datos no bloqueante

| Guia | De que trata |
| --- | --- |
| [reactive-sql-clients](03-datos/reactive-sql-clients.md) | The Reactive SQL Clients have a straightforward API focusing on scalability and low-overhead. Currently, the following database servers are supported: |
| [hibernate-reactive](03-datos/hibernate-reactive.md) | Hibernate Reactive is a reactive API for Hibernate ORM, supporting non-blocking database drivers and a reactive style of interaction with the database. |
| [hibernate-reactive-panache](03-datos/hibernate-reactive-panache.md) | Hibernate Reactive is the only reactive Jakarta Persistence (formerly known as JPA) implementation and offers you the full breadth of an Object Relational Mapper allowing you to access your database o… |
| [datasource](03-datos/datasource.md) | Use a unified configuration model to define data sources for Java Database Connectivity (JDBC) and Reactive drivers. |
| [transaction](03-datos/transaction.md) | The quarkus-narayana-jta extension provides a Transaction Manager that coordinates and expose transactions to your applications as described in the Jakarta Transactions specification, formerly known a… |
| [mongodb](03-datos/mongodb.md) | MongoDB is a well known NoSQL Database that is widely used. |
| [mongodb-panache](03-datos/mongodb-panache.md) | MongoDB is a well known NoSQL Database that is widely used, but using its raw API can be cumbersome as you need to express your entities and your queries as a MongoDB Document. |
| [mongodb-dev-services](03-datos/mongodb-dev-services.md) | Quarkus supports a feature called Dev Services that allows you to create various datasources without any config. In the case of MongoDB this support extends to the default MongoDB connection. What tha… |
| [redis](03-datos/redis.md) | This guide demonstrates how your Quarkus application can connect to a Redis server using the Redis Client extension. |
| [redis-reference](03-datos/redis-reference.md) | Redis is an in-memory data store used as a database, cache, streaming engine, and message broker. The Quarkus Redis extension allows integrating Quarkus applications with Redis. |
| [redis-dev-services](03-datos/redis-dev-services.md) | Quarkus supports a feature called Dev Services that allows you to create various datasources without any config. What that means practically, is that if you have docker running and have not configured… |
| [cache](03-datos/cache.md) | In this guide, you will learn how to enable application data caching in any CDI managed bean of your Quarkus application. |
| [cache-redis-reference](03-datos/cache-redis-reference.md) | By default, Quarkus Cache uses Caffeine as backend. It’s possible to use Redis instead. |
| [cache-infinispan-reference](03-datos/cache-infinispan-reference.md) | By default, Quarkus Cache uses Caffeine as backend. It’s possible to use Infinispan instead. |
| [infinispan-client](03-datos/infinispan-client.md) | This guide demonstrates how your Quarkus application can connect to an Infinispan server using the Infinispan Client extension. |
| [infinispan-client-reference](03-datos/infinispan-client-reference.md) | Infinispan is a distributed, in-memory key/value store that provides Quarkus applications with a highly configurable and independently scalable data layer. This extension gives you client functionalit… |
| [cassandra](03-datos/cassandra.md) | Apache Cassandra® is a free and open-source, distributed, wide column store, NoSQL database management system designed to handle large amounts of data across many commodity servers, providing high ava… |
| [elasticsearch](03-datos/elasticsearch.md) | Elasticsearch is a well known full text search engine and NoSQL datastore. |
| [databases-dev-services](03-datos/databases-dev-services.md) | When testing or running in dev mode Quarkus can provide you with a zero-config database out of the box, a feature we refer to as Dev Services. Depending on your database type you may need Docker insta… |
| [flyway](03-datos/flyway.md) | Flyway is a popular database migration tool that is commonly used in JVM environments. |
| [liquibase](03-datos/liquibase.md) | Liquibase is an open source tool for database schema change management. |

## Mensajeria reactiva y streaming

| Guia | De que trata |
| --- | --- |
| [messaging](04-mensajeria/messaging.md) | Event-driven messaging systems have become the backbone of most modern applications, enabling the building of message-driven microservices or complex data streaming pipelines. |
| [messaging-virtual-threads](04-mensajeria/messaging-virtual-threads.md) | This guide explains how to benefit from Java virtual threads when writing message processing applications in Quarkus. |
| [kafka-getting-started](04-mensajeria/kafka-getting-started.md) | In this guide, you will build two applications that exchange messages through Apache Kafka using Quarkus Messaging: a producer that sends quote requests and a processor that replies with prices. |
| [kafka](04-mensajeria/kafka.md) | This reference guide demonstrates how your Quarkus application can utilize Quarkus Messaging to interact with Apache Kafka. |
| [kafka-streams](04-mensajeria/kafka-streams.md) | This guide demonstrates how your Quarkus application can utilize the Apache Kafka Streams API to implement stream processing applications based on Apache Kafka. |
| [kafka-dev-services](04-mensajeria/kafka-dev-services.md) | If any Kafka-related extension is present (e.g. quarkus-messaging-kafka), Dev Services for Kafka automatically starts a Kafka broker in dev mode and when running tests. So, you don’t have to start a b… |
| [kafka-dev-ui](04-mensajeria/kafka-dev-ui.md) | If any Kafka-related extension is present (e.g. quarkus-messaging-kafka), the Quarkus Dev UI is extended with a Kafka broker management UI. It is connected automatically to the Kafka broker configured… |
| [kafka-schema-registry-avro](04-mensajeria/kafka-schema-registry-avro.md) | This guide shows how your Quarkus application can use Apache Kafka, Avro serialized records, and connect to a schema registry (such as the Confluent Schema Registry or Apicurio Registry). |
| [kafka-schema-registry-json-schema](04-mensajeria/kafka-schema-registry-json-schema.md) | This guide shows how your Quarkus application can use Apache Kafka, JSON Schema serialized records, and connect to a schema registry (such as the Confluent Schema Registry or Apicurio Registry). |
| [amqp](04-mensajeria/amqp.md) | This guide demonstrates how your Quarkus application can utilize Quarkus Messaging to interact with AMQP 1.0. |
| [amqp-reference](04-mensajeria/amqp-reference.md) | This guide is the companion from the Getting Started with AMQP 1.0. It explains in more details the configuration and usage of the AMQP connector for reactive messaging. |
| [amqp-dev-services](04-mensajeria/amqp-dev-services.md) | Dev Services for AMQP automatically starts an AMQP 1.0 broker in dev mode and when running tests. So, you don’t have to start a broker manually. The application is configured automatically. |
| [rabbitmq](04-mensajeria/rabbitmq.md) | This guide demonstrates how your Quarkus application can utilize Quarkus Messaging to interact with RabbitMQ. |
| [rabbitmq-reference](04-mensajeria/rabbitmq-reference.md) | This guide is the companion from the Getting Started with RabbitMQ. It explains in more details the configuration and usage of the RabbitMQ connector for reactive messaging. |
| [rabbitmq-dev-services](04-mensajeria/rabbitmq-dev-services.md) | Dev Services for RabbitMQ automatically starts a RabbitMQ broker in dev mode and when running tests. So, you don’t have to start a broker manually. The application is configured automatically. |
| [pulsar-getting-started](04-mensajeria/pulsar-getting-started.md) | This guide demonstrates how your Quarkus application can utilize Quarkus Messaging to interact with Apache Pulsar. |
| [pulsar](04-mensajeria/pulsar.md) | This reference guide demonstrates how your Quarkus application can utilize Quarkus Messaging to interact with Apache Pulsar. |
| [pulsar-dev-services](04-mensajeria/pulsar-dev-services.md) | With Quarkus Messaging Pulsar extension (quarkus-messaging-pulsar) Dev Services for Pulsar automatically starts a Pulsar broker in dev mode and when running tests. So, you don’t have to start a broker… |
| [jms](04-mensajeria/jms.md) | This guide demonstrates how your Quarkus application can use JMS messaging via the Apache Qpid JMS AMQP client, or alternatively the Apache ActiveMQ Artemis JMS client. |
| [mailer](04-mensajeria/mailer.md) | This guide demonstrates how your Quarkus application can send emails using an SMTP server. This is a getting started guide. Check the Quarkus Mailer Reference documentation for more complete explanati… |
| [mailer-reference](04-mensajeria/mailer-reference.md) | This guide is the companion from the Mailer Getting Started Guide. It explains in more details the configuration and usage of the Quarkus Mailer. |

## gRPC reactivo

| Guia | De que trata |
| --- | --- |
| [grpc](05-grpc/grpc.md) | gRPC is a high-performance RPC framework. It can efficiently connect services implemented using various languages and frameworks. It is also applicable in the last mile of distributed computing to con… |
| [grpc-getting-started](05-grpc/grpc-getting-started.md) | This page explains how to start using gRPC in your Quarkus application. While this page describes how to configure it with Maven, it is also possible to use Gradle. |
| [grpc-service-implementation](05-grpc/grpc-service-implementation.md) | gRPC service implementations exposed as CDI beans are automatically registered and served by quarkus-grpc. |
| [grpc-service-consumption](05-grpc/grpc-service-consumption.md) | gRPC clients can be injected in your application code. |
| [grpc-reference](05-grpc/grpc-reference.md) | If you need to implement a gRPC service or consume it, you need the quarkus-grpc extension. It handles both sides. |
| [grpc-generation-reference](05-grpc/grpc-generation-reference.md) | This reference guide explains how to configure gRPC code generation. It is recommended to read the official gRPC guide first. |
| [grpc-virtual-threads](05-grpc/grpc-virtual-threads.md) | This guide explains how to benefit from Java virtual threads when implementing a gRPC service. |
| [grpc-kubernetes](05-grpc/grpc-kubernetes.md) | This page explains how to deploy your gRPC service in Quarkus in Kubernetes. We’ll continue with the example from the Getting Started gRPC guide. |
| [grpc-xds](05-grpc/grpc-xds.md) | This page explains how to enable xDS gRPC usage in your Quarkus application. |
| [grpc-cli](05-grpc/grpc-cli.md) | This page explains how to use gRPC CLI -- a grpcurl-like tool. |

## Resiliencia, service discovery y scheduling

| Guia | De que trata |
| --- | --- |
| [smallrye-fault-tolerance](06-resiliencia/smallrye-fault-tolerance.md) | One of the challenges brought by the distributed nature of microservices is that communication with external systems is inherently unreliable. This increases demand on resiliency of applications. To s… |
| [stork](06-resiliencia/stork.md) | The essence of distributed systems resides in the interaction between services. In modern architecture, you often have multiple instances of your service to share the load or improve the resilience by… |
| [stork-reference](06-resiliencia/stork-reference.md) | This guide is the companion from the Stork Getting Started Guide. It explains the configuration and usage of SmallRye Stork integration in Quarkus. |
| [stork-registration](06-resiliencia/stork-registration.md) | This guide explains how to enable automatic registration and deregistration of a Quarkus application using SmallRye Stork and Consul, with minimal or no configuration. |
| [stork-manual-service-registration](06-resiliencia/stork-manual-service-registration.md) | This guide explains how to implement a custom service registrar for SmallRye Stork and use it to programmatically register service instances at startup. |
| [stork-kubernetes](06-resiliencia/stork-kubernetes.md) | This guide explains how to use Stork with Kubernetes for service discovery and load balancing. |
| [load-shedding-reference](06-resiliencia/load-shedding-reference.md) | This technology is considered experimental. |
| [smallrye-health](06-resiliencia/smallrye-health.md) | This guide demonstrates how your Quarkus application can use SmallRye Health an implementation of the MicroProfile Health specification. |
| [scheduler](06-resiliencia/scheduler.md) | Modern applications often need to run specific tasks periodically. In this guide, you learn how to schedule periodic tasks. |
| [scheduler-reference](06-resiliencia/scheduler-reference.md) | Modern applications often need to run specific tasks periodically. There are two scheduler extensions in Quarkus. The quarkus-scheduler extension brings the API and a lightweight in-memory scheduler i… |
| [quartz](06-resiliencia/quartz.md) | Modern applications often need to run specific tasks periodically. In this guide, you learn how to schedule periodic clustered tasks using the Quartz extension. |
| [lra](06-resiliencia/lra.md) | The LRA (short for Long Running Action) participant extension is useful in microservice based designs where different services can benefit from a relaxed notion of distributed consistency. |
| [lra-dev-services](06-resiliencia/lra-dev-services.md) | If the Narayana LRA extension is present (quarkus-narayana-lra), the Dev Services for Narayana LRA coordinator automatically starts the Narayana LRA coordinator in dev mode and when running tests. So,… |
| [software-transactional-memory](06-resiliencia/software-transactional-memory.md) | Software Transactional Memory (STM) has been around in research environments since the late 1990’s and has relatively recently started to appear in products and various programming languages. We won’t… |

## Observabilidad de aplicaciones reactivas

| Guia | De que trata |
| --- | --- |
| [observability](07-observabilidad/observability.md) | Observability can be defined as the capability to allow a human to ask and answer questions about a system. |
| [opentelemetry](07-observabilidad/opentelemetry.md) | This guide explains how your Quarkus application can utilize OpenTelemetry (OTel) to provide Observability for interactive web applications. |
| [opentelemetry-tracing](07-observabilidad/opentelemetry-tracing.md) | This guide explains how your Quarkus application can utilize OpenTelemetry (OTel) to provide distributed tracing for interactive web applications. |
| [opentelemetry-metrics](07-observabilidad/opentelemetry-metrics.md) | This guide explains how your Quarkus application can utilize OpenTelemetry (OTel) to provide metrics for interactive web applications. |
| [opentelemetry-logging](07-observabilidad/opentelemetry-logging.md) | This guide explains how your Quarkus application can utilize OpenTelemetry (OTel) to provide structured, contextual, vendor-neutral and centralised logging for interactive web applications. |
| [telemetry-micrometer](07-observabilidad/telemetry-micrometer.md) | Micrometer provides an abstraction layer for metrics collection. It defines an API for basic meter types, like counters, gauges, timers, and distribution summaries, along with a MeterRegistry API that… |
| [telemetry-micrometer-tutorial](07-observabilidad/telemetry-micrometer-tutorial.md) | Create an application that uses the Micrometer metrics library to collect runtime, extension and application metrics and expose them as a Prometheus (OpenMetrics) endpoint. |
| [telemetry-micrometer-to-opentelemetry](07-observabilidad/telemetry-micrometer-to-opentelemetry.md) | This extension provides support for both Micrometer and OpenTelemetry in Quarkus applications. It streamlines integration by incorporating both extensions along with a bridge that enables sending Micr… |
| [logging](07-observabilidad/logging.md) | Read about the use of logging API in Quarkus, configuring logging output, and using logging adapters to unify the output from other logging APIs. |
| [centralized-log-management](07-observabilidad/centralized-log-management.md) | This guide explains how you can send your logs to a centralized log management system like Graylog, Logstash (inside the Elastic Stack or ELK - Elasticsearch, Logstash, Kibana) or Fluentd (inside EFK … |
| [observability-devservices](07-observabilidad/observability-devservices.md) | We are already familiar with Dev Service concept, but in the case of Observability we need a way to orchestrate and connect more than a single Dev Service, usually a whole stack of them; e.g. a metric… |
| [observability-devservices-lgtm](07-observabilidad/observability-devservices-lgtm.md) | This Dev Service provides the Grafana OTel-LGTM, an all-in-one Docker image containing an OpenTelemetry Collector receiving and then forwarding telemetry data to Prometheus (metrics), Tempo (traces) a… |
| [jfr](07-observabilidad/jfr.md) | This guide explains how Flight Recorder can be extended to provide additional insight into your Quarkus application. JFR records various information from the Java standard API and JVM as events. By ad… |

## Rendimiento, nativo y despliegue

| Guia | De que trata |
| --- | --- |
| [performance-measure](08-rendimiento-nativo/performance-measure.md) | All of our tests are run on the same hardware for a given batch. It goes without saying, but it’s better when you say it. |
| [native-reference](08-rendimiento-nativo/native-reference.md) | This guide is a companion to the Building a Native Executable, Using SSL With Native Images, and Writing Native Applications, guides. It explores advanced topics that help users diagnose issues, incre… |
| [building-native-image](08-rendimiento-nativo/building-native-image.md) | This guide takes as input the application developed in the Getting Started Guide. |
| [writing-native-applications-tips](08-rendimiento-nativo/writing-native-applications-tips.md) | This guide contains various tips and tricks for getting around problems that might arise when attempting to run Java applications as native executables. |
| [class-loading-reference](08-rendimiento-nativo/class-loading-reference.md) | This document explains the Quarkus class loading architecture. It is intended for extension authors and advanced users who want to understand exactly how Quarkus works. |
| [container-image](08-rendimiento-nativo/container-image.md) | Quarkus provides extensions for building (and pushing) container images. Currently, it supports: |
| [deploying-to-kubernetes](08-rendimiento-nativo/deploying-to-kubernetes.md) | Quarkus offers the ability to automatically generate Kubernetes resources based on sane defaults and user-supplied configuration using dekorate. It currently supports generating resources for vanilla … |
| [management-interface-reference](08-rendimiento-nativo/management-interface-reference.md) | Various Quarkus extensions contribute non-application endpoints that provide different kinds of information about the application. Examples of such extensions are the health, metrics, OpenAPI and info… |
| [tls-registry-reference](08-rendimiento-nativo/tls-registry-reference.md) | The TLS Registry is a Quarkus extension that centralizes TLS configuration, making it easier to manage and maintain secure connections across your application. |

## Testing de codigo reactivo

| Guia | De que trata |
| --- | --- |
| [getting-started-testing](09-testing/getting-started-testing.md) | Learn how to test your Quarkus Application. This guide covers: |
| [continuous-testing](09-testing/continuous-testing.md) | Learn how to use continuous testing in your Quarkus Application. |
| [testing-components](09-testing/testing-components.md) | The component model of Quarkus is built on top CDI. Therefore, Quarkus provides QuarkusComponentTestExtension - a JUnit extension that makes it easy to test the components/CDI beans and mock their dep… |
| [tests-with-coverage](09-testing/tests-with-coverage.md) | Learn how to measure the test coverage of your application. This guide covers: |
| [dev-services](09-testing/dev-services.md) | Quarkus supports the automatic provisioning of unconfigured services in development and test mode. We refer to this capability as Dev Services. If you include an extension and don’t configure it then … |
| [getting-started-dev-services](09-testing/getting-started-dev-services.md) | This tutorial shows you how to create an application which writes to and reads from a database. You will use Dev Services, so you will not actually download, configure, or even start the database your… |
| [dev-ui](09-testing/dev-ui.md) | Quarkus Dev UI is a developer-friendly user interface that comes to life when you run your application in development mode (./mvnw quarkus:dev).  It serves as a powerful portal for exploring, debuggin… |

## Puntos de entrada y utilidades

| Guia | De que trata |
| --- | --- |
| [getting-started](10-extras/getting-started.md) | In this guide, you’ll create a REST endpoint, see live coding in action, add a service with dependency injection, and write tests. You won’t write any boilerplate, and you won’t have to restart the ap… |
| [cli-tooling](10-extras/cli-tooling.md) | The quarkus command lets you create projects, manage extensions and do essential build and development tasks using the underlying project build tool. |
| [maven-tooling](10-extras/maven-tooling.md) | Use Maven to create a new project, add or remove extensions, launch development mode, debug your application, and build your application into a jar, native executable, or container-friendly executable… |
| [gradle-tooling](10-extras/gradle-tooling.md) | Use Gradle to create a new project, add or remove extensions, launch development mode, debug your application, and build your application into a jar, native executable, or container-friendly executabl… |
| [config](10-extras/config.md) | Hardcoded values in your code are a no-go (even if we all did it at some point ;-)). In this guide, we will learn how to configure a Quarkus application. |
| [config-mappings](10-extras/config-mappings.md) | With config mappings it is possible to group multiple configuration properties in a single interface that share the same prefix. |
| [config-yaml](10-extras/config-yaml.md) | You can use a YAML file,application.yaml, to configure your Quarkus application instead of the standard Java properties file, application.properties. |
| [update-quarkus](10-extras/update-quarkus.md) | You can update or upgrade your Quarkus projects to the latest version of Quarkus by using an update command. |
| [extension-maturity-matrix](10-extras/extension-maturity-matrix.md) | What makes a good Quarkus extension? What capabilities is a Quarkus extension expected to provide? Of course, it depends on the extension you are building. But, we found a set of attributes common to … |
| [all-config](10-extras/all-config.md) |  |
