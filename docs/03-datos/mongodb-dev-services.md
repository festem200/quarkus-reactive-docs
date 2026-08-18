# Dev Services for MongoDB

> **Guia oficial:** <https://quarkus.io/guides/mongodb-dev-services>  
> **Fuente:** `docs/src/main/asciidoc/mongodb-dev-services.adoc` en [quarkusio/quarkus@3.38.2](https://github.com/quarkusio/quarkus/blob/3.38.2/docs/src/main/asciidoc/mongodb-dev-services.adoc)  
> **Version documentada:** Quarkus 3.38.2 · **Sincronizado:** 2026-08-17 · **Licencia:** Apache-2.0

Quarkus supports a feature called Dev Services that allows you to create various datasources without any config. In the case of MongoDB this support extends to the default MongoDB connection.
What that means practically, is that if you have not configured `quarkus.mongodb.connection-string` nor `quarkus.mongodb.hosts`, Quarkus will automatically start a MongoDB container when
running tests or in dev mode, and automatically configure the connection.

MongoDB Dev Services is based on [Testcontainers MongoDB module](https://www.testcontainers.org/modules/databases/mongodb/) that will start a single node replicaset.

When running the production version of the application, the MongoDB connection need to be configured as normal, so if you want to include a production database config in your
`application.properties` and continue to use Dev Services we recommend that you use the `%prod.` profile to define your MongoDB settings.

## Shared server

Most of the time you need to share the server between applications.
Dev Services for MongoDB implements a _service discovery_ mechanism for your multiple Quarkus applications running in _dev_ mode to share a single server.

**📌 NOTE**\
Dev Services for MongoDB starts the container with the `quarkus-dev-service-mongodb` label which is used to identify the container.

If you need multiple (shared) servers, you can configure the `quarkus.mongodb.devservices.service-name` attribute and indicate the server name.
It looks for a container with the same value, or starts a new one if none can be found.
The default service name is `mongodb`.

Sharing is enabled by default in dev mode, but disabled in test mode.
You can disable the sharing with `quarkus.mongodb.devservices.shared=false`.

## Compose

The MongoDB Dev Services supports [Compose Dev Services](https://quarkus.io/guides/compose-dev-services).
It relies on a `compose-devservices.yml`, such as:

```yaml
name: <application name>
services:
  mongo:
    image: docker.io/library/mongo:7.0
    ports:
      - "27017"
```

## Configuration reference

**📌 NOTE**\
La tabla de configuracion generada `quarkus-mongodb-client_quarkus.mongodb.devservices` se produce al construir la documentacion y no existe en el codigo fuente. Consulta la referencia de configuracion en https://quarkus.io/guides/all-config
