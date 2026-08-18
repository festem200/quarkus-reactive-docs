# Dev Services for RabbitMQ

> **Guia oficial:** <https://quarkus.io/guides/rabbitmq-dev-services>  
> **Fuente:** `docs/src/main/asciidoc/rabbitmq-dev-services.adoc` en [quarkusio/quarkus@3.38.2](https://github.com/quarkusio/quarkus/blob/3.38.2/docs/src/main/asciidoc/rabbitmq-dev-services.adoc)  
> **Version documentada:** Quarkus 3.38.2 · **Sincronizado:** 2026-08-17 · **Licencia:** Apache-2.0

Dev Services for RabbitMQ automatically starts a RabbitMQ broker in dev mode and when running tests.
So, you don’t have to start a broker manually.
The application is configured automatically.

## Enabling / disabling Dev Services for RabbitMQ

Dev Services for RabbitMQ is automatically enabled unless:

* `quarkus.rabbitmq.devservices.enabled` is set to `false`
* the `rabbitmq-host` or `rabbitmq-port` is configured
* all the Reactive Messaging RabbitMQ channels have the `host` or `port` attributes set

Dev Services for RabbitMQ relies on Docker to start the broker.
If your environment does not support Docker, you must start the broker manually, or connect to an already running broker.
You can configure the broker access by using the `rabbitmq-host`, `rabbitmq-port`, `rabbitmq-username` and `rabbitmq-password` properties.

## Shared broker

Most of the time you want to share the broker between applications.
Dev Services for RabbitMQ implements a _service discovery_ mechanism for your multiple Quarkus applications running in _dev_ mode to share a single broker.

**📌 NOTE**\
Dev Services for RabbitMQ starts the container with the `quarkus-dev-service-rabbitmq` label, which is used to identify the container.

If you need multiple (shared) brokers, you can configure the `quarkus.rabbitmq.devservices.service-name` attribute and indicate the broker name.
It looks for a container with the same value, or starts a new one if none can be found.
The default service name is `rabbitmq`.

Sharing is enabled by default in dev mode, but disabled in test mode.
You can disable the sharing with `quarkus.rabbitmq.devservices.shared=false`.

## Setting the port

By default, Dev Services for RabbitMQ picks a random port and configures the application.
You can set the port by configuring the `quarkus.rabbitmq.devservices.port` property.

## Configuring the image

Dev Services for RabbitMQ uses official images available at https://hub.docker.com/_/rabbitmq.
You can configure the image and version with the `quarkus.rabbitmq.devservices.image-name` property:

```properties
quarkus.rabbitmq.devservices.image-name=docker.io/library/rabbitmq:3.12-management
```

## Access the management UI

By default, Dev Services for RabbitMQ use the official image with the `management` tag. This means you have the [management plugin](https://github.com/docker-library/docs/tree/master/rabbitmq#management-plugin) available. You can use the [Dev UI](../09-testing/dev-ui.md) to find the HTTP port randomly affected
or configure a static one by using `quarkus.rabbitmq.devservices.http-port`.

## Predefined topology

Dev Services for RabbitMQ supports defining topology upon broker start. You can define Virtual Hosts, Exchanges, Queues,
and Bindings through standard Quarkus configuration.

### Defining virtual hosts

RabbitMQ uses a default virtual host of `/`. To define additional RabbitMQ virtual hosts, provide the names
of the virtual hosts in the `quarkus.rabbitmq.devservices.vhosts` key:

```properties
quarkus.rabbitmq.devservices.vhosts=my-vhost-1,my-vhost-2
```

### Defining exchanges

To define a RabbitMQ exchange you provide the exchange’s name after the `quarkus.rabbitmq.devservices.exchanges` key,
followed by one (or more) of the exchange’s properties:

```properties
quarkus.rabbitmq.devservices.exchanges.my-exchange.type=topic            # defaults to 'direct'
quarkus.rabbitmq.devservices.exchanges.my-exchange.auto-delete=false     # defaults to 'false'
quarkus.rabbitmq.devservices.exchanges.my-exchange.durable=true          # defaults to 'false'
quarkus.rabbitmq.devservices.exchanges.my-exchange.vhost=my-vhost        # defaults to '/'
```

Additionally, any additional arguments can be provided to the exchange’s definition by using the `arguments` key:

```properties
quarkus.rabbitmq.devservices.exchanges.my-exchange.arguments.alternate-exchange=another-exchange
```

### Defining queues

To define a RabbitMQ queue you provide the queue’s name after the `quarkus.rabbitmq.devservices.queues` key,
followed by one (or more) of the queue’s properties:

```properties
quarkus.rabbitmq.devservices.queues.my-queue.auto-delete=false          # defaults to 'false'
quarkus.rabbitmq.devservices.queues.my-queue.durable=true               # defaults to 'false'
quarkus.rabbitmq.devservices.queues.my-queue.vhost=my-vhost             # defaults to '/'
```

Additionally, any additional arguments can be provided to the queue’s definition by using the `arguments` key:

```properties
quarkus.rabbitmq.devservices.queues.my-queue.arguments.x-dead-letter-exchange=another-exchange
```

### Defining bindings

To define a RabbitMQ binding you provide the binding’s name after the `quarkus.rabbitmq.devservices.bindings` key,
followed by one (or more) of the binding’s properties:

```properties
quarkus.rabbitmq.devservices.bindings.a-binding.source=my-exchange      # defaults to name of binding
quarkus.rabbitmq.devservices.bindings.a-binding.routing-key=some-key    # defaults to '#'
quarkus.rabbitmq.devservices.bindings.a-binding.destination=my-queue    # defaults to name of binding
quarkus.rabbitmq.devservices.bindings.a-binding.destination-type=queue  # defaults to 'queue'
quarkus.rabbitmq.devservices.bindings.a-binding.vhost=my-vhost          # defaults to '/'
```

**📌 NOTE**\
The name of the binding is only used for the purposes of the Dev Services configuration and is not part of the
binding defined in RabbitMQ.

Additionally, any additional arguments can be provided to the binding’s definition by using the `arguments` key:

```properties
quarkus.rabbitmq.devservices.bindings.a-binding.arguments.non-std-option=value
```

## Configuration reference

**📌 NOTE**\
La tabla de configuracion generada `quarkus-messaging-rabbitmq_quarkus.rabbitmq.devservices` se produce al construir la documentacion y no existe en el codigo fuente. Consulta la referencia de configuracion en https://quarkus.io/guides/all-config
