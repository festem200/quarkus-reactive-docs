# Stork Reference Guide

> **Guia oficial:** <https://quarkus.io/guides/stork-reference>  
> **Fuente:** `docs/src/main/asciidoc/stork-reference.adoc` en [quarkusio/quarkus@3.38.2](https://github.com/quarkusio/quarkus/blob/3.38.2/docs/src/main/asciidoc/stork-reference.adoc)  
> **Version documentada:** Quarkus 3.38.2 · **Sincronizado:** 2026-08-17 · **Licencia:** Apache-2.0

This guide is the companion from the [Stork Getting Started Guide](stork.md).
It explains the configuration and usage of SmallRye Stork integration in Quarkus.

<dl><dt><strong><a name="extension-status-note"></a>📌 NOTE</strong></dt><dd>

This technology is considered preview.

## Supported clients

The current integration of Stork supports:

* the REST Client
* the gRPC clients (using the Vert.x gRPC client is recommended)

Warning: The gRPC client integration does not support statistic-based load balancers.

## Available service discovery and selection

Check the [SmallRye Stork website](https://smallrye.io/smallrye-stork) to find more about the provided service discovery and selection.

## Using Stork in Kubernetes

Stork provides a service discovery support for Kubernetes, which goes beyond what Kubernetes provides by default.
It looks for all the pods backing up a Kubernetes service, but instead of applying a round-robin (as Kubernetes would do), it gives you the option to select the pod using a Stork load-balancer.

To use this feature, add the following dependency to your project:

**pom.xml**

```xml
<dependency>
    <groupId>io.smallrye.stork</groupId>
    <artifactId>stork-service-discovery-kubernetes</artifactId>
</dependency>
```

**build.gradle**

```gradle
implementation("io.smallrye.stork:stork-service-discovery-kubernetes")
```

For each service expected to be exposed as a Kubernetes Service, configure the lookup:

```properties
quarkus.stork.my-service.service-discovery.type=kubernetes
quarkus.stork.my-service.service-discovery.k8s-namespace=my-namespace
```

Stork looks for the Kubernetes Service with the given name (`my-service` in the previous example) in the specified namespace.
Instead of using the Kubernetes Service IP directly and let Kubernetes handle the selection and balancing, Stork inspects the service and retrieves the list of pods providing the service. Then, it can select the instance.

For a full example of using Stork with Kubernetes, please read the [Using Stork with Kubernetes guide](stork-kubernetes.md).

## Extending Stork

Stork is extensible.
You can implement your own service discovery or service selection provider.

To learn about custom service discovery and service selection, check:

* [Implement a custom service discover provider](https://smallrye.io/smallrye-stork/latest/service-discovery/custom-service-discovery/)
* [Implement a custom service selection provider](https://smallrye.io/smallrye-stork/latest/load-balancer/custom-load-balancer/)

## Configure Stork observability

### Enable metrics

Stork metrics are automatically enabled when the application also uses the [`quarkus-micrometer`](../07-observabilidad/telemetry-micrometer.md) extension.

Micrometer collects the metrics of rest/grpc clients using Stork and the client using Stork programmatically.

As an example, if you export the metrics to Prometheus, you will get:

```text
# HELP stork_service_selection_failures_total The number of failures during service selection.
# TYPE stork_service_selection_failures_total counter
stork_service_selection_failures_total{service_name="hello-service",} 0.0
# HELP stork_service_selection_duration_seconds The duration of the selection operation
# TYPE stork_service_selection_duration_seconds summary
stork_service_selection_duration_seconds_count{service_name="hello-service",} 13.0
stork_service_selection_duration_seconds_sum{service_name="hello-service",} 0.001049291
# HELP stork_service_selection_duration_seconds_max The duration of the selection operation
# TYPE stork_service_selection_duration_seconds_max gauge
stork_service_selection_duration_seconds_max{service_name="hello-service",} 0.0
# HELP stork_overall_duration_seconds_max The total duration of the Stork service discovery and selection operations
# TYPE stork_overall_duration_seconds_max gauge
stork_overall_duration_seconds_max{service_name="hello-service",} 0.0
# HELP stork_overall_duration_seconds The total duration of the Stork service discovery and selection operations
# TYPE stork_overall_duration_seconds summary
stork_overall_duration_seconds_count{service_name="hello-service",} 13.0
stork_overall_duration_seconds_sum{service_name="hello-service",} 0.001049291
# HELP stork_service_discovery_failures_total The number of failures during service discovery
# TYPE stork_service_discovery_failures_total counter
stork_service_discovery_failures_total{service_name="hello-service",} 0.0
# HELP stork_service_discovery_duration_seconds_max The duration of the discovery operation
# TYPE stork_service_discovery_duration_seconds_max gauge
stork_service_discovery_duration_seconds_max{service_name="hello-service",} 0.0
# HELP stork_service_discovery_duration_seconds The duration of the discovery operation
# TYPE stork_service_discovery_duration_seconds summary
stork_service_discovery_duration_seconds_count{service_name="hello-service",} 13.0
stork_service_discovery_duration_seconds_sum{service_name="hello-service",} 6.585046209
# HELP stork_service_discovery_instances_count_total The number of service instances discovered
# TYPE stork_service_discovery_instances_count_total counter
stork_service_discovery_instances_count_total{service_name="hello-service",} 26.0
```

The Stork service name can be found in the _tags_.

The metrics contain both the service discovery (`stork_service_discovery_*`) and the metrics about the service selection (`stork_service_selection_*`) such as the number of service instances, failures, and durations.

### Disable metrics

To disable the Stork metrics when `quarkus-micrometer` is used, add the following property to the application configuration:

```properties
quarkus.micrometer.binder.stork.enabled=false
```

## Configuration reference

**📌 NOTE**\
La tabla de configuracion generada `quarkus-smallrye-stork` se produce al construir la documentacion y no existe en el codigo fuente. Consulta la referencia de configuracion en https://quarkus.io/guides/all-config
