# Using OpenTelemetry

> **Guia oficial:** <https://quarkus.io/guides/opentelemetry>  
> **Fuente:** `docs/src/main/asciidoc/opentelemetry.adoc` en [quarkusio/quarkus@3.38.2](https://github.com/quarkusio/quarkus/blob/3.38.2/docs/src/main/asciidoc/opentelemetry.adoc)  
> **Version documentada:** Quarkus 3.38.2 · **Sincronizado:** 2026-08-17 · **Licencia:** Apache-2.0

This guide explains how your Quarkus application can utilize [OpenTelemetry](https://opentelemetry.io/) (OTel) to provide
Observability for interactive web applications.

On this page we show the signal independent features of the extension.

This document is part of the [Observability in Quarkus reference guide](observability.md) which features this and other observability related components.

<dl><dt><strong>📌 NOTE</strong></dt><dd>

* The old OpenTelemetry guide has been split into this generic guide, the [OpenTelemetry Tracing Guide](opentelemetry-tracing.md), the new [OpenTelemetry Metrics Guide](opentelemetry-metrics.md) and the [OpenTelemetry Logging Guide](opentelemetry-logging.md).
* The use of **the [OpenTelemetry Agent](https://opentelemetry.io/docs/instrumentation/java/automatic/) is not needed nor recommended**. Quarkus Extensions and the libraries they provide, are directly instrumented. That agent doesn’t work with native mode.
</dd></dl>

## Introduction
[OpenTelemetry](https://opentelemetry.io/docs/what-is-opentelemetry/) is an Observability framework and toolkit designed to create and manage telemetry data such as traces, metrics, and logs. Crucially, OpenTelemetry is vendor- and tool-agnostic.

Quarkus provides manual and automatic instrumentation for tracing and manual instrumentation capabilities for metrics.

This will allow Quarkus based applications to be observable by tools and services supporting OpenTelemetry.

<dl><dt><strong>📌 NOTE</strong></dt><dd>

Automatic metrics instrumentation in Quarkus is done by the [Quarkus Micrometer extension](telemetry-micrometer.md).

The [quarkus-micrometer-opentelemetry](telemetry-micrometer-to-opentelemetry.md) extension enables the use and export of Micrometer metrics via OpenTelemetry.
</dd></dl>

Quarkus supports the OpenTelemetry Autoconfiguration. The configurations match what you can see at
[OpenTelemetry SDK Autoconfigure](https://opentelemetry.io/docs/languages/java/configuration/)
with the `quarkus.*` prefix.

This guide provides a crosscutting explanation of the OpenTelemetry extension and how to use it. If you need details about any particular signal (tracing or metrics), please refer to the signal specific guide.

With the introduction of OpenTelemetry Metrics, the original, single page guide had to be split according to signal types, as follows:

### [OpenTelemetry Tracing Guide](opentelemetry-tracing.md)

The tracing functionality is supported and **on** by default.

### [OpenTelemetry Metrics Guide](opentelemetry-metrics.md)

#### Enable Metrics
The metrics functionality is tech preview and **off** by default. You will need to activate it by setting:

```properties
quarkus.otel.metrics.enabled=true
```
At build time on your `application.properties` file.

### [OpenTelemetry Logging Guide](opentelemetry-logging.md)

#### Enable Logs
The logging functionality is tech preview and **off** by default. You will need to activate it by setting:

```properties
quarkus.otel.logs.enabled=true
```
At build time on your `application.properties` file.

## Using the extension

If you already have your Quarkus project, you can add the `quarkus-opentelemetry` extension
to it by running the following command in your project base directory:

**CLI**

```bash
quarkus extension add opentelemetry
```
**Maven**

```bash
./mvnw quarkus:add-extension -Dextensions='opentelemetry'
```
**Gradle**

```bash
./gradlew addExtension --extensions='opentelemetry'
```

This will add the following to your build file:

**pom.xml**

```xml
<dependency>
    <groupId>io.quarkus</groupId>
    <artifactId>quarkus-opentelemetry</artifactId>
</dependency>
```

**build.gradle**

```gradle
implementation("io.quarkus:quarkus-opentelemetry")
```

### Create the configuration

By default, the exporters will send out data in batches, using the gRPC protocol and endpoint `http://localhost:4317`.

If you need to change any of the default property values, here is an example on how to configure the default OTLP gRPC Exporter within the application, using the `src/main/resources/application.properties` file:

```properties
quarkus.application.name=myservice // ①
quarkus.otel.exporter.otlp.endpoint=http://localhost:4317 // ②
quarkus.otel.exporter.otlp.headers=authorization=Bearer my_secret // ③
quarkus.log.console.format=%d{HH:mm:ss} %-5p traceId=%X{traceId}, parentId=%X{parentId}, spanId=%X{spanId}, sampled=%X{sampled} [%c{2.}] (%t) %s%e%n  // ④

# Alternative to the console log
quarkus.http.access-log.pattern="...traceId=%{X,traceId} spanId=%{X,spanId}" // ⑤
```

1. All telemetry created from the application will include an OpenTelemetry `Resource` attribute indicating the telemetry was created by the `myservice` application. If not set, it will default to the artifact id.
2. gRPC endpoint to send the telemetry. If not set, it will default to `http://localhost:4317`.
3. Optional gRPC headers commonly used for authentication
4. Add tracing information into log messages.
5. You can also only put the trace info into the access log. In this case you must omit the info in the console log format.

We provide signal agnostic configurations for the connection related properties, meaning that you can use the same properties for both tracing and metrics when you set:
```properties
quarkus.otel.exporter.otlp.endpoint=http://localhost:4317
```
If you need different configurations for each signal, you can use the specific properties:
```properties
quarkus.otel.exporter.otlp.traces.endpoint=http://trace-uri:4317 // ①
quarkus.otel.exporter.otlp.metrics.endpoint=http://metrics-uri:4317 // ②
quarkus.otel.exporter.otlp.logs.endpoint=http://logs-uri:4317 // ③
```
1. The endpoint for the traces exporter.
2. The endpoint for the metrics exporter.
3. The endpoint for the logs exporter.

If you need your spans and logs to be exported directly as they finish
(e.g. in a serverless environment / application), you can set this property to `true`.
This replaces the default batching of data.
```properties
quarkus.otel.simple=true
```

### Disable all or parts of the OpenTelemetry extension

Once you add the dependency, the extension will generate tracing data by default. To enable metrics or disable the OpenTelemetry extension globally or partially these are the properties to use (they are extracted from the config reference below):

| Affected Signal | Property name | Default value | Description |
| --- | --- | --- | --- |
| All | `quarkus.otel.enabled` | true | If false, disable the OpenTelemetry usage at **build** time. |
| All | `quarkus.otel.sdk.disabled` | false | Comes from the OpenTelemetry autoconfiguration. If true, will disable the OpenTelemetry SDK usage at **runtime**. |
| All output | `quarkus.otel.exporter.otlp.enabled` | true | If false, will disable Quarkus default OTLP exporters at **build** time. Telemetry will be generated, contexts will be propagated but no telemetry will be sent out. |
| Traces | `quarkus.otel.traces.enabled` | true | If false, disable the OpenTelemetry tracing usage at **build** time. |
| Traces output | `quarkus.otel.traces.exporter` | cdi | List of exporters to be used for tracing, separated by commas. Has one of the values from _ExporterType_: `otlp`, `cdi`, `none`. This is a **build** time property and setting it to `none` will disable tracing data output. |
| Metrics | `quarkus.otel.metrics.enabled` | false | Metrics are disabled by default at **build** time because they are tech preview. |
| Metrics output | `quarkus.otel.metrics.exporter` | cdi | List of exporters to be used for metrics, separated by commas. Has one of the values from _ExporterType_: `otlp`, `cdi`, `none`. This is a **build** time property and setting it to `none` will disable metrics data output. |
| Logs | `quarkus.otel.logs.enabled` | false | Logs are disabled by default at **build** time because they are tech preview. |
| Logs output | `quarkus.otel.logs.exporter` | cdi | List of exporters to be used for logs, separated by commas. Has one of the values from _ExporterType_: `otlp`, `cdi`, `none`. This is a **build** time property and setting it to `none` will disable logs data output. |
| Logs output | `quarkus.otel.logs.handler.enabled` | true | If false, disable the OpenTelemetry logs handler at **runtime**. This removes the bridge between the Quarkus logging system (JBoss LogManager) and OpenTelemetry logs. |

If you need to enable or disable the exporter at runtime, you can use the [sampler](opentelemetry-tracing.md#sampler) because it has the ability to filter out all the spans if needed.

Particular instrumentation components can be disabled in tracing, like ignore client requests but keep server ones. For more details, please check the [OpenTelemetry Tracing Guide](opentelemetry-tracing.md).

### Resource
A [resource](https://github.com/open-telemetry/opentelemetry-specification/blob/main/specification/overview.md#resources) is a representation
of the entity that is producing telemetry, it adds attributes to the exported trace or metric to characterize who is producing the telemetry. Quarkus follows the [resources auto-configuration](https://opentelemetry.io/docs/languages/java/configuration/#resources) specified by the Java OpenTelemetry SDK.

#### Default
The following attributes are added by default to resources.

| Attribute name | Content example | Origin |
| --- | --- | --- |
| service.name | "opentelemetry-quickstart" | Value comes from the artifactId, from the `quarkus.application.name` property or from `quarkus.otel.resource.attributes=service.name=cart` property. |
| host.name | "myHost" | Resolved at startup |
| service.version | "1.0-SNAPSHOT" | Resolved at build time from the artifact version |
| telemetry.sdk.language | "java" | Static value |
| telemetry.sdk.name | "opentelemetry" | Resolved at build time |
| telemetry.sdk.version | "1.32.0" | Resolved at build time |
| webengine.name | "Quarkus" | Static value |
| webengine.version | "999-SNAPSHOT" | Quarkus version resolved at build time |

#### Using configuration
You can add additional attributes by setting the `quarkus.otel.resource.attributes` config property that is described in the [OpenTelemetry Configuration Reference](#opentelemetry-configuration-reference).
Since this property can be overridden at runtime, the OpenTelemetry extension will pick up its value following the order of precedence that
is described in the [Quarkus Configuration Reference](../01-fundamentos/config-reference.md#configuration-sources).

```properties
quarkus.otel.resource.attributes=deployment.environment=dev,service.name=cart,service.namespace=shopping
```

This will add the attributes for `deployment.environment`, `service.name` and `service.namespace` to the resource and be included in traces and metrics.

#### Using CDI beans
If by any means you need to use a custom resource or one that is provided by one of the [OpenTelemetry SDK Extensions](https://github.com/open-telemetry/opentelemetry-java/tree/main/sdk-extensions)
you can create multiple resource producers. The OpenTelemetry extension will detect the `Resource` CDI beans and will merge them when configuring the OTel SDK.

```java
@ApplicationScoped
public class CustomConfiguration {

    @Produces
    @ApplicationScoped
    public Resource osResource() {
        return OsResource.get();
    }

    @Produces
    @ApplicationScoped
    public Resource ecsResource() {
        return EcsResource.get();
    }
}
```

#### Kubernetes
When running the application in Kubernetes, the [OpenTelemetry Kubernetes resource attributes](https://opentelemetry.io/docs/specs/semconv/resource/k8s/) can be populated in a couple of ways.

##### With the Quarkus Kubernetes extension

When the `quarkus-kubernetes` extension is present, Quarkus automatically adds the following environment variables to the generated Kubernetes manifests:

| Attribute name | Content example | Environment variable | Source |
| --- | --- | --- | --- |
| k8s.namespace.name | "my-namespace" | `QUARKUS_OTEL_K8S_RESOURCE_NAMESPACE` | Kubernetes Downward API: `metadata.namespace`. Falls back to reading the service account namespace file at `/var/run/secrets/kubernetes.io/serviceaccount/namespace`. |
| k8s.pod.name | "my-app-7d6f8b5c9-x2k4m" | `QUARKUS_OTEL_K8S_RESOURCE_POD_NAME` | Kubernetes Downward API: `metadata.name`. |
| k8s.pod.uid | "f4b5c6d7-1234-5678-9abc-def012345678" | `QUARKUS_OTEL_K8S_RESOURCE_POD_UID` | Kubernetes Downward API: `metadata.uid`. |
| k8s.node.name | "node-1" | `QUARKUS_OTEL_K8S_RESOURCE_NODE_NAME` | Kubernetes Downward API: `spec.nodeName`. |
| k8s.container.name | "my-app" | `QUARKUS_OTEL_K8S_RESOURCE_CONTAINER_NAME` | Set to the application name at build time. |
| k8s.deployment.name | "my-app" | `QUARKUS_OTEL_K8S_RESOURCE_DEPLOYMENT_NAME` | Set to `quarkus.kubernetes.name` (or the application name if not configured) at build time. |

The `k8s.cluster.name` attribute is not set automatically because the cluster name is not available through pod metadata.
You can set it manually using `quarkus.otel.resource.attributes=k8s.cluster.name=my-cluster` or by setting the `QUARKUS_OTEL_K8S_RESOURCE_CLUSTER_NAME` environment variable.

##### Without the Quarkus Kubernetes extension

If the `quarkus-kubernetes` extension is **not** used, there’s the need to manually set the environment variables defined in the previous section. The `quarkus-opentelemetry` extension will then be able to populate the Kubernetes resource attributes. This is a partial sample of a deployment manifest setting up the required env. vars.:

```yaml
spec:
  containers:
    - name: my-app
      env:
        - name: QUARKUS_OTEL_K8S_RESOURCE_NAMESPACE
          valueFrom:
            fieldRef:
              fieldPath: metadata.namespace
        - name: QUARKUS_OTEL_K8S_RESOURCE_POD_NAME
          valueFrom:
            fieldRef:
              fieldPath: metadata.name
        - name: QUARKUS_OTEL_K8S_RESOURCE_POD_UID
          valueFrom:
            fieldRef:
              fieldPath: metadata.uid
        - name: QUARKUS_OTEL_K8S_RESOURCE_NODE_NAME
          valueFrom:
            fieldRef:
              fieldPath: spec.nodeName
        - name: QUARKUS_OTEL_K8S_RESOURCE_CONTAINER_NAME
          value: my-app
        - name: QUARKUS_OTEL_K8S_RESOURCE_DEPLOYMENT_NAME
          value: my-app
        - name: QUARKUS_OTEL_K8S_RESOURCE_CLUSTER_NAME
          value: production
```

### Semantic conventions

OpenTelemetry provides a set of [semantic conventions](https://opentelemetry.io/docs/specs/semconv/http/http-spans/) to standardize the data collected by the instrumentation.

When creating manual instrumentation, while naming metrics or attributes you should follow those conventions and not create new names to represent existing conventions. This will make data correlation easier to perform across services.

## Exporters

### The Default

The Quarkus OpenTelemetry extension uses its own signal exporters built on top of Vert.x for optimal performance and maintainability. All **Quarkus built in exporters use the OTLP protocol** through a couple of data senders, using `grpc` (the default) and `http/protobuf`.

The active exporter is automatically wired by CDI, that’s why the `quarkus.otel.traces.exporter`, `quarkus.otel.metrics.exporter` and `quarkus.otel.logs.exporter` properties default value is `cdi`. This is not because of the protocol being used in the data transfer but because of how the exporters are wired.

CDI (Context Dependency Injection) will manage the exporters to use, according to the selected protocol or when applications implement their own CDI exporter, like in tests.

The `quarkus.otel.exporter.otlp.protocol` property instructs Quarkus to switch the senders and defaults to `grpc` but `http/protobuf` can also be used.

**📌 NOTE**\
If you change the protocol, you also need to change the port in the endpoint. The default port for `grpc` is `4317` and for `http/protobuf` is `4318`.

The `quarkus.otel.exporter.otlp.memory-mode` property configures the memory allocation strategy for OTLP exporters.
The default value `immutable-data` creates new serialization objects for each export.
Setting it to `reusable-data` enables object pooling to reduce garbage collection pressure, which can be beneficial in memory-constrained environments.

### Using CDI to produce a test exporter

Leaving the default as CDI is particularly useful for tests. In the following example a Span exporter class is wired with CDI and then the telemetry can be used in test code.

Creating a custom `SpanExporter` bean:

```java
    @ApplicationScoped
    static class InMemorySpanExporterProducer {
        @Produces
        @Singleton
        InMemorySpanExporter inMemorySpanExporter() {
            return InMemorySpanExporter.create();
        }
    }
```

Where `InMemorySpanExporter` is a class from the OpenTelemetry test utilities dependency:

**pom.xml**

```xml
    <dependency>
        <groupId>io.opentelemetry</groupId>
        <artifactId>opentelemetry-sdk-testing</artifactId>
        <scope>test</scope>
    </dependency>
```

**build.gradle**

```gradle
implementation("io.opentelemetry:opentelemetry-sdk-testing")
```

The bean of that class can be injected to access the telemetry data. This is an example to obtain the spans:

```java
    @Inject
    InMemorySpanExporter inMemorySpanExporter;

    //...

    List<SpanData> finishedSpanItems = inMemorySpanExporter.getFinishedSpanItems();
```

If this is used in an integration test, you should access the class from inside the running process and not from the test class.
A viable option could be to expose that data through a REST endpoint method:

```java
    @GET
    @Path("/export")
    public List<SpanData> exportTraces() {
        return inMemorySpanExporter.getFinishedSpanItems()
                .stream()
                .filter(sd -> !sd.getName().contains("export")) ①
                .collect(Collectors.toList());
    }
```
1. This excludes calls to the export endpoint itself.

For more details please take a look at the [ExporterResource](https://github.com/quarkusio/quarkus/blob/main/integration-tests/opentelemetry/src/main/java/io/quarkus/it/opentelemetry/ExporterResource.java) in the Quarkus integration tests.

### The OpenTelemetry OTLP exporter

This is currently not supported in Quarkus. Configuration example for traces: `quarkus.otel.tracing.exporter=otlp`.

However, it’s also not needed because Quarkus own default exporters will send data using the OTLP protocol.

### On Quarkiverse
Additional exporters will be available in the Quarkiverse [quarkus-opentelemetry-exporter](https://docs.quarkiverse.io/quarkus-opentelemetry-exporter/dev/index.html) project.

Currently, are available the following exporters (may be outdated) for:

* Legacy Jaeger
* Microsoft Azure
* Google Cloud

Also on Quarkiverse, the [Quarkus AWS SDK has integration with OpenTelemetry](https://docs.quarkiverse.io/quarkus-amazon-services/dev/opentelemetry.html).

### Logging exporter (for debugging)

You can output all metrics to the console, for debugging/development purposes.

**❗ IMPORTANT**\
Don’t use this in production.

You will need to add the following dependency to your project:
**pom.xml**

```xml
<dependency>
    <groupId>io.opentelemetry</groupId>
    <artifactId>opentelemetry-exporter-logging</artifactId>
</dependency>
```

**build.gradle**

```gradle
implementation("io.opentelemetry:opentelemetry-exporter-logging")
```

Then, setting the exporter to `logging` in the `application.properties` file:
```properties
quarkus.otel.metrics.exporter=logging ①
quarkus.otel.metric.export.interval=10000ms ②
quarkus.otel.traces.exporter=logging ③
```

1. Set the metrics exporter to `logging`. Normally you don’t need to set this. The default is `cdi`.
2. Set the interval to export the metrics. The default is `1m`, which is too long for debugging.
3. Set the traces exporter to `logging`. Normally you don’t need to set this. The default is `cdi`.

## Visualizing the data

A Dev Service can receive your app’s telemetry.

The Grafana-OTel-LGTM Dev Service will start automatically on Dev Mode and data will be automatically sent to it.

* Take a look at: [Getting Started with Grafana-OTel-LGTM](observability-devservices-lgtm.md).

Grafana is used to visualize data, Loki to store logs, Tempo to store traces and Prometheus to store metrics. Also provides and OTel collector to receive the data.

This provides an easy way to visualize all OpenTelemetry data generated by the application.

You can also use the [logging exporter](#logging-exporter-for-debugging) to output all traces and metrics to the console.

## Dev Services for OpenTelemetry with the LGTM stack

The OpenTelemetry extension provides a Dev Service that automatically starts a Grafana OTel LGTM stack when the application is started in development mode. This allows you to easily visualize the telemetry data generated by your application without needing to set up an external observability stack.

### Enabling / Disabling Dev Services for OpenTelemetry

Dev Services for OpenTelemetry is enabled by default. You can disable it by setting the `quarkus.observability.lgtm.enabled=false` or `quarkus.observability.dev-resources=false` properties in your configuration.

### Full Dev Services for OpenTelemetry reference

The Observability Dev Services guide provides a full reference for all the properties related to Dev Services for OpenTelemetry with the LGTM stack. You can find it at [Observability Dev Services with Grafana OTel LGTM](observability-devservices-lgtm.md).

## OpenTelemetry Configuration Reference

Quarkus supports the OpenTelemetry Autoconfiguration for Traces.
The configurations match what you can see at
[OpenTelemetry SDK Autoconfigure](https://opentelemetry.io/docs/languages/java/configuration/)
adding the usual `quarkus.*` prefix.

Quarkus OpenTelemetry configuration properties now have the `quarkus.otel.*` prefix.

**📌 NOTE**\
La tabla de configuracion generada `quarkus-opentelemetry` se produce al construir la documentacion y no existe en el codigo fuente. Consulta la referencia de configuracion en https://quarkus.io/guides/all-config
