# Deploying your gRPC Service in Kubernetes

> **Guia oficial:** <https://quarkus.io/guides/grpc-kubernetes>  
> **Fuente:** `docs/src/main/asciidoc/grpc-kubernetes.adoc` en [quarkusio/quarkus@3.38.2](https://github.com/quarkusio/quarkus/blob/3.38.2/docs/src/main/asciidoc/grpc-kubernetes.adoc)  
> **Version documentada:** Quarkus 3.38.2 · **Sincronizado:** 2026-08-17 · **Licencia:** Apache-2.0

This page explains how to deploy your gRPC service in Quarkus in Kubernetes.
We’ll continue with the example from [the Getting Started gRPC guide](grpc-getting-started.md).

## Configuring your project to use the Quarkus Kubernetes extension

Add the Quarkus Kubernetes extension to your build file:

**pom.xml**

```xml
<dependency>
    <groupId>io.quarkus</groupId>
    <artifactId>quarkus-kubernetes</artifactId>
</dependency>
```

**build.gradle**

```gradle
implementation("io.quarkus:quarkus-kubernetes")
```

Next, we want to expose our application using the Kubernetes Ingress resource:

```properties
quarkus.kubernetes.ingress.expose=true
```

The Quarkus Kubernetes will bind the HTTP server using the port name `http` and the gRPC server using the port name `grpc`. By default, the Quarkus application will only expose the port name `http`, so only the HTTP server will be publicly accessible. To expose the gRPC server instead, set the `quarkus.kubernetes.ingress.target-port=grpc` property in your application.properties:

```properties
quarkus.kubernetes.ingress.target-port=grpc
```

**💡 TIP**\
If you configure Quarkus to use the same port for both HTTP and gRPC servers with the property `quarkus.grpc.server.use-separate-server=false`, then you don’t need to change the default `target-port`.

Finally, we need to generate the Kubernetes manifests by running the command in a terminal:

**CLI**

```bash
quarkus build
```
**Maven**

```bash
./mvnw install
```
**Gradle**

```bash
./gradlew build
```

Once generated, you can look at the `target/kubernetes` directory:

```txt
target/kubernetes
└── kubernetes.json
└── kubernetes.yml
```

You can find more information about how to deploy the application in Kubernetes in the [the Kubernetes guide](../08-rendimiento-nativo/deploying-to-kubernetes.md#deployment).

## Using gRPC Health probes

By default, the Kubernetes resources do not contain readiness and liveness probes. To add them, import the SmallRye Health extension to your build file:

**pom.xml**

```xml
<dependency>
    <groupId>io.quarkus</groupId>
    <artifactId>quarkus-smallrye-health</artifactId>
</dependency>
```

**build.gradle**

```gradle
implementation("io.quarkus:quarkus-smallrye-health")
```

**💡 TIP**\
More information about the health extension can be found in [the SmallRye Health guide](../06-resiliencia/smallrye-health.md).

By default, this extension will configure the probes to use the HTTP server (which is provided by some extensions like the Quarkus REST (formerly RESTEasy Reactive) extension). Internally, this probe will also use [the generated gRPC Health services](grpc-service-implementation.md#health).

If your application does not use any Quarkus extension that exposes an HTTP server, you can still configure the probes to directly use the gRPC Health service by adding the property `quarkus.kubernetes.readiness-probe.grpc-action-enabled=true` into your configuration:

```properties
quarkus.kubernetes.readiness-probe.grpc-action-enabled=true
```
