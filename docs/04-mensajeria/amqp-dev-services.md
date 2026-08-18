# Dev Services for AMQP

> **Guia oficial:** <https://quarkus.io/guides/amqp-dev-services>  
> **Fuente:** `docs/src/main/asciidoc/amqp-dev-services.adoc` en [quarkusio/quarkus@3.38.2](https://github.com/quarkusio/quarkus/blob/3.38.2/docs/src/main/asciidoc/amqp-dev-services.adoc)  
> **Version documentada:** Quarkus 3.38.2 · **Sincronizado:** 2026-08-17 · **Licencia:** Apache-2.0

Dev Services for AMQP automatically starts an AMQP 1.0 broker in dev mode and when running tests.
So, you don’t have to start a broker manually.
The application is configured automatically.

## Enabling / Disabling Dev Services for AMQP

Dev Services for AMQP is automatically enabled unless:

* `quarkus.amqp.devservices.enabled` is set to `false`
* the `amqp-host` or `amqp-port` are configured
* all the Reactive Messaging AMQP channels have the `host` or `port` attributes set

Dev Services for AMQP relies on Docker to start the broker.
If your environment does not support Docker, you will need to start the broker manually, or connect to an already running broker.
You can configure the broker access using the `amqp-host`, `amqp-port`, `amqp-user` and `amqp-password` properties.

## Shared broker

Most of the time, you need to share the broker between applications.
Dev Services for AMQP implements a _service discovery_ mechanism for your multiple Quarkus applications running in _dev_ mode to share a single broker.

**📌 NOTE**\
Dev Services for AMQP starts the container with the `quarkus-dev-service-amqp` label which is used to identify the container.

If you need multiple (shared) brokers, you can configure the `quarkus.amqp.devservices.service-name` attribute and indicate the broker name.
It looks for a container with the same value, or starts a new one if none can be found.
The default service name is `amqp`.

Sharing is enabled by default in dev mode, but disabled in test mode.
You can disable the sharing with `quarkus.amqp.devservices.shared=false`.

## Setting the port

By default, Dev Services for AMQP picks a random port and configures the application.
You can set the port by configuring the `quarkus.amqp.devservices.port` property.

## Configuring the image

Dev Services for AMQP uses [activemq-artemis-broker](https://quay.io/repository/artemiscloud/activemq-artemis-broker) images.
You can configure the image and version using the `quarkus.amqp.devservices.image-name` property:

```properties
quarkus.amqp.devservices.image-name=quay.io/arkmq-org/arkmq-org-broker:artemis.2.55.0
```

**❗ IMPORTANT**\
The configured image must be _compatible_ with the `activemq-artemis-broker` one.
The container is launched with the `AMQ_USER`, `AMQ_PASSWORD` and `AMQ_EXTRA_ARGS` environment variables.
The ports 5672 and 8161 (web console) are exposed.

## Compose

Dev Services for AMQP supports [Compose Dev Services](https://quarkus.io/guides/compose-dev-services).
It relies on a `compose-devservices.yml`, such as:

```yaml
name: <application name>
services:
  artemis:
    image: quay.io/arkmq-org/arkmq-org-broker:artemis.2.55.0
    ports:
      - "5672"
      - "8161"
    environment:
      AMQ_USER: quarkus
      AMQ_PASSWORD: quarkus
      AMQ_EXTRA_ARGS: --no-autotune --mapped --no-fsync --relax-jolokia
```

## Configuration reference

**📌 NOTE**\
La tabla de configuracion generada `quarkus-messaging-amqp_quarkus.amqp.devservices` se produce al construir la documentacion y no existe en el codigo fuente. Consulta la referencia de configuracion en https://quarkus.io/guides/all-config
