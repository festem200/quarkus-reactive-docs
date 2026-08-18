# Using xDS gRPC

> **Guia oficial:** <https://quarkus.io/guides/grpc-xds>  
> **Fuente:** `docs/src/main/asciidoc/grpc-xds.adoc` en [quarkusio/quarkus@3.38.2](https://github.com/quarkusio/quarkus/blob/3.38.2/docs/src/main/asciidoc/grpc-xds.adoc)  
> **Version documentada:** Quarkus 3.38.2 · **Sincronizado:** 2026-08-17 · **Licencia:** Apache-2.0

This page explains how to enable xDS gRPC usage in your Quarkus application.

**❗ IMPORTANT**\
This Quarkus xDS gRPC integration currently doesn’t support building native executables due to the issues
with shaded grpc-netty library while running native IT tests.

## Configuring your project

Add the Quarkus gRPC xDS extension to your build file:

**pom.xml**

```xml
<dependency>
    <groupId>io.quarkus</groupId>
    <artifactId>quarkus-grpc-xds</artifactId>
</dependency>
```

**build.gradle**

```gradle
implementation("io.quarkus:quarkus-grpc-xds")
```

**📌 NOTE**\
This transitively adds `io.quarkus:quarkus-grpc` extension dependency.

## Server configuration

**📌 NOTE**\
La tabla de configuracion generada `quarkus-grpc_quarkus.grpc.server.xds` se produce al construir la documentacion y no existe en el codigo fuente. Consulta la referencia de configuracion en https://quarkus.io/guides/all-config

## Server configuration example

To enable server xDS, use the following configuration.

xDS must be explicitly enabled on the server, then verify you use it on the right xDS server port (default is 9000).
If you want to use `XdsServerCredentials` set `xds.secure` to `true`.

```properties
quarkus.grpc.server.xds.enabled=true
#quarkus.grpc.server.xds.secure=true
quarkus.grpc.server.port=30051
```

**📌 NOTE**\
When xDS is configured, `plain-text` is automatically disabled.

## Client configuration

**📌 NOTE**\
La tabla de configuracion generada `quarkus-grpc_quarkus.grpc.clients.-client-name-.xds` se produce al construir la documentacion y no existe en el codigo fuente. Consulta la referencia de configuracion en https://quarkus.io/guides/all-config

**📌 NOTE**\
When xDS target property is used, name resolver, host, and port are not used

## Client configuration example

To enable client xDS, use the following configuration.

You can either explicitly enable xDS or you use `xds` name resolver,
and make sure you point it to the right xDS server port (default is 9000).
If you want to use `XdsChannelCredentials` set `xds.secure` to `true`.

```properties
#quarkus.grpc.clients.<client-name>.xds.enabled=true
#quarkus.grpc.clients.<client-name>.xds.secure=true
quarkus.grpc.clients.<client-name>.name-resolver=xds
quarkus.grpc.clients.<client-name>.port=30051
```

**📌 NOTE**\
When xDS is configured, `plain-text` is automatically disabled.

## Kubernetes configuration example

Below is an example of (required) additional configuration when using xDS gRPC with the Istio Service Mesh in Kubernetes.

```properties
quarkus.kubernetes.ports.grpc.container-port=30051
quarkus.kubernetes.annotations."inject.istio.io/templates"=grpc-agent
quarkus.kubernetes.annotations."proxy.istio.io/config"={"holdApplicationUntilProxyStarts": true}
```
