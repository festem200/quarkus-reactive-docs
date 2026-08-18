# Dev Services for Redis

> **Guia oficial:** <https://quarkus.io/guides/redis-dev-services>  
> **Fuente:** `docs/src/main/asciidoc/redis-dev-services.adoc` en [quarkusio/quarkus@3.38.2](https://github.com/quarkusio/quarkus/blob/3.38.2/docs/src/main/asciidoc/redis-dev-services.adoc)  
> **Version documentada:** Quarkus 3.38.2 · **Sincronizado:** 2026-08-17 · **Licencia:** Apache-2.0

Quarkus supports a feature called Dev Services that allows you to create various datasources without any config.
What that means practically, is that if you have docker running and have not configured `quarkus.redis.hosts`,
Quarkus will automatically start a Redis container when running tests or dev mode, and automatically configure the connection.

When running the production version of the application, the Redis connection need to be configured as normal,
so if you want to include a production database config in your `application.properties` and continue to use Dev Services
we recommend that you use the `%prod.` profile to define your Redis settings.

Dev Services for Redis relies on Docker to start the server.
If your environment does not support Docker, you will need to start the server manually, or connect to an already running server.

**❗ IMPORTANT**\
If you want to use Redis Stack _modules_ (bloom, graph, search...), set the image-name to `redis/redis-stack:latest`

## Shared server

Most of the time you need to share the server between applications.
Dev Services for Redis implements a _service discovery_ mechanism for your multiple Quarkus applications running in _dev_ mode to share a single server.

**📌 NOTE**\
Dev Services for Redis starts the container with the `quarkus-dev-service-redis` label which is used to identify the container.

If you need multiple (shared) servers, you can configure the `quarkus.redis.devservices.service-name` attribute and indicate the server name.
It looks for a container with the same value, or starts a new one if none can be found.
The default service name is `redis`.

Sharing is enabled by default in dev mode, but disabled in test mode.
You can disable the sharing with `quarkus.redis.devservices.shared=false`.

## Configuration reference

**📌 NOTE**\
La tabla de configuracion generada `quarkus-redis-client_quarkus.redis.devservices` se produce al construir la documentacion y no existe en el codigo fuente. Consulta la referencia de configuracion en https://quarkus.io/guides/all-config
