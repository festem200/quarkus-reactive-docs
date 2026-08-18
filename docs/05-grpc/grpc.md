# gRPC

> **Guia oficial:** <https://quarkus.io/guides/grpc>  
> **Fuente:** `docs/src/main/asciidoc/grpc.adoc` en [quarkusio/quarkus@3.38.2](https://github.com/quarkusio/quarkus/blob/3.38.2/docs/src/main/asciidoc/grpc.adoc)  
> **Version documentada:** Quarkus 3.38.2 · **Sincronizado:** 2026-08-17 · **Licencia:** Apache-2.0

[gRPC](https://grpc.io/) is a high-performance RPC framework.
It can efficiently connect services implemented using various languages and frameworks.
It is also applicable in the last mile of distributed computing to connect devices, mobile applications, and browsers to backend services.

In general, gRPC uses HTTP/2, TLS, and [Protobuf (Protocol Buffers)](https://developers.google.com/protocol-buffers).
In a microservice architecture, gRPC is an efficient, type-safe alternative to HTTP.

The Quarkus gRPC extension integrate gRPC in Quarkus application.
It:

* supports implementing gRPC services
* supports consuming gRPC services
* integrates with the reactive engine from Quarkus as well as the reactive development model
* allows plain-text communication as well as TLS, and TLS with mutual authentication
* supports [xDS gRPC](https://grpc.github.io/grpc/core/md_doc_grpc_xds_features.html) integration
* supports [InProcess](https://grpc.github.io/grpc-java/javadoc/io/grpc/inprocess/InProcessServerBuilder.html) gRPC development

Quarkus gRPC is based on [Vert.x gRPC](https://vertx.io/docs/vertx-grpc/java/).

* [Getting Started](grpc-getting-started.md)
* [Implementing a gRPC Service](grpc-service-implementation.md)
* [Consuming a gRPC Service](grpc-service-consumption.md)
* [Deploying your gRPC Service in Kubernetes](grpc-kubernetes.md)
* [Enabling xDS gRPC support](grpc-xds.md)
* [gRPC code generation reference guide](grpc-generation-reference.md)
* [gRPC reference guide](grpc-reference.md)
* [gRPC CLI support](grpc-cli.md)
