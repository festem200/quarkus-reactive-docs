# Management interface reference

> **Guia oficial:** <https://quarkus.io/guides/management-interface-reference>  
> **Fuente:** `docs/src/main/asciidoc/management-interface-reference.adoc` en [quarkusio/quarkus@3.38.2](https://github.com/quarkusio/quarkus/blob/3.38.2/docs/src/main/asciidoc/management-interface-reference.adoc)  
> **Version documentada:** Quarkus 3.38.2 · **Sincronizado:** 2026-08-17 · **Licencia:** Apache-2.0

Various Quarkus extensions contribute non-application endpoints that provide different kinds of information about the application.
Examples of such extensions are the [health](../06-resiliencia/smallrye-health.md), [metrics](../07-observabilidad/telemetry-micrometer.md), [OpenAPI](../02-web-http/openapi-swaggerui.md) and [info](https://quarkus.io/guides/info) extensions.

These non-application endpoints are normally accessible under the `/q` prefix like so:

* `/q/health`
* `/q/metrics`
* `/q/openapi`
* `/q/info`

By default, these management endpoints are served by the same HTTP server as your application endpoints.
This document presents how you can use a separate HTTP server (bound to a different network interface and port) for the management endpoints.
It avoids exposing these endpoints on the main server and, therefore, prevents undesired accesses.

## Enabling the management interface

To enable the management interface, use the following ***build-time*** property:

```properties
quarkus.management.enabled=true
```

By default, management endpoints will be exposed on: `http://0.0.0.0:9000/q`.
For example, if you have `smallrye-health` installed, the readiness probe will be exposed at `http://0.0.0.0:9000/q/health/ready`.

SmallRye Health Checks, Micrometer and Info endpoints will be declared as management endpoints when the management interface is enabled.

**📌 NOTE**\
The management interface is disabled when no extensions relying on it (such as the SmallRye Health or SmallRye OpenAPI extensions) are installed.

## Configure the host, port and scheme

By default, the management interface is exposed on the interface: `0.0.0.0` (all interfaces) and on the port `9000` (`9001` in test mode).
It does not use TLS (`https`) by default.

You can configure the host, ports, and TLS configuration name using the following properties:

* `quarkus.management.host` - the interface / host
* `quarkus.management.port` - the port
* `quarkus.management.test-port` - the port to use in test mode
* `quarkus.management.tls-configuration-name` - the TLS configuration name, [same as for the main HTTP server](../02-web-http/http-reference.md#using-the-tls-centralized-configuration).

Here is a configuration example exposing the management interface on _https://localhost:9002_:

```properties
quarkus.management.enabled=true
quarkus.management.host=localhost
quarkus.management.port=9002
quarkus.management.tls-configuration-name=management

# Your TLS registry configuration
...
```

With this configuration, TLS is enabled and configured as defined in the `management` configuration of the TLS registry.

You can also configure the management interface with the legacy SSL configuration, as for ([the main HTTP server](../02-web-http/http-reference.md#ssl)):

```properties
quarkus.management.enabled=true
quarkus.management.host=localhost
quarkus.management.port=9002
quarkus.management.ssl.certificate.key-store-file=server-keystore.jks
quarkus.management.ssl.certificate.key-store-password=secret
```

Key store, trust store and certificate files can be reloaded periodically.
Configure the `quarkus.management.ssl.certificate.reload-period` property to specify the interval at which the certificates should be reloaded:

```properties
quarkus.http.management.certificate.files=/mount/certs/tls.crt
quarkus.http.management.certificate.key-files=/mount/certs/tls.key
quarkus.http.management.certificate.reload-period=1h
```

The files are reloaded from the same location as they were initially loaded from.
If there is no content change, the reloading is a no-op.
It the reloading fails, the server will continue to use the previous certificates.

**❗ IMPORTANT**\
Unlike the main HTTP server, the management interface does not handle _http_ and _https_ at the same time.
If _https_ is configured, plain HTTP requests will be rejected.

## Configure the root path

Management endpoints are configured differently than standard HTTP endpoints.
They use a unique root path, which is `/q` by default.
This management root path can be configured using the `quarkus.management.root-path property`.
For example, if you want to expose the management endpoints under `/management` use:

```properties
quarkus.management.enabled=true
quarkus.management.root-path=/management
```

The mounting rules of the management endpoints slightly differ from the ones used when using the main HTTP server:

* Management endpoints configured using a _relative_ path (not starting with `/`) will be served from the configured root path.
For example, if the endpoint path is `health` and the root path is `management`, the resulting path is `/management/health`
* Management endpoints configured using an _absolute_ path (starting with `/`) will be served from the root.
For example, if the endpoint path is `/health`, the resulting path is `/health`, regardless of the root path
* The management interface does not use the HTTP root path from the main HTTP server.

<dl><dt><strong>❗ IMPORTANT</strong></dt><dd>

The `quarkus.http.root-path` property is only applied to the main HTTP server and not to the management interface.
In addition, the `quarkus.http.non-application-root-path` property is not used for endpoint exposed on the management interface.
</dd></dl>

## Create a management endpoint in an extension

**📌 NOTE**\
To expose an endpoint on the management interface from the code of an application, refer to [the application section](#exposing-an-endpoint-on-the-management-interface-as-an-application).

SmallRye Health Checks, and Micrometer endpoints will be declared as management endpoints when the management interface is enabled.

**📌 NOTE**\
if you do not enable the management interface, these endpoints will be served using the main HTTP server (under `/q` by default).

Extensions can create a management endpoint by defining a _non application_ route and calling `management()` method:

```java
@BuildStep
void createManagementRoute(BuildProducer<RouteBuildItem> routes,
        NonApplicationRootPathBuildItem nonApplicationRootPathBuildItem,
        MyRecorder recorder) {

    routes.produce(nonApplicationRootPathBuildItem.routeBuilder()
        .management() // Must be called BEFORE the routeFunction method
        .routeFunction("my-path", recorder.route())
        .handler(recorder.getHandler())
        .blockingRoute()
        .build());
    //...
}
```

If the management interface is enabled, the endpoint will be exposed on: `http://0.0.0.0:9000/q/my-path`.
Otherwise, it will be exposed on: `http://localhost:8080/q/my-path`.

**❗ IMPORTANT**\
Management endpoints can only be declared by extensions and not from the application code.

## Exposing an endpoint on the management interface (as an application)

You can expose endpoints on the management interface by registering routes on the management router.
To access the router use the following code:

```java
public void registerManagementRoutes(@Observes ManagementInterface mi) {
       mi.router().get("/admin").handler(rc ->
            rc.response().end("admin it is")
       );
}
```

The `io.quarkus.vertx.http.ManagementInterface` event is fired when the management interface is initialized.
So, if the management interface is not enabled, the method won’t be called.

The `router()` method returns a `io.vertx.ext.web.Router` object which can be used to register routes.
The paths are relative to `/`.
For example, the previous snippet registers a route on `/admin`.
This route is accessible on `http://0.0.0.0:9000/admin`, if you use the default host and port.

More details about the `Router` API can be found on [the Vert.x Web documentation](https://vertx.io/docs/vertx-web/java/).

## Management Interface Configuration

**📌 NOTE**\
La tabla de configuracion generada `quarkus-vertx-http_quarkus.management` se produce al construir la documentacion y no existe en el codigo fuente. Consulta la referencia de configuracion en https://quarkus.io/guides/all-config

## Running behind a reverse proxy

Quarkus can be accessed through proxies that generate headers (e.g. `X-Forwarded-Host`) to preserve information about the original request.
Quarkus can be configured to automatically update information like protocol, host, port and URI to use the values from those headers.

**❗ IMPORTANT**\
Activating this feature can expose the server to security issues like information spoofing.
Activate it only when running behind a reverse proxy.

To set up this feature for the management interface, include the following lines in `src/main/resources/application.properties`:
```properties
quarkus.management.proxy.proxy-address-forwarding=true
```

To constrain this behavior to the standard `Forwarded` header (and ignore `X-Forwarded` variants) by setting `quarkus.management.proxy.allow-forwarded` in `src/main/resources/application.properties`:
```properties
quarkus.management.proxy.allow-forwarded=true
```

Alternatively, you can prefer `X-Forwarded-*` headers using the following configuration in `src/main/resources/application.properties` (note `allow-x-forwarded` instead of `allow-forwarded`):
```properties
quarkus.management.proxy.proxy-address-forwarding=true
quarkus.management.proxy.allow-x-forwarded=true
quarkus.management.proxy.enable-forwarded-host=true
quarkus.management.proxy.enable-forwarded-prefix=true
```

Supported forwarding address headers are:

* `Forwarded`
* `X-Forwarded-Proto`
* `X-Forwarded-Host`
* `X-Forwarded-Port`
* `X-Forwarded-Ssl`
* `X-Forwarded-Prefix`

If both header variants (`Forwarded` and `X-Forwarded-*`) are enabled, the `Forwarded` header will have precedence.

**❗ IMPORTANT**\
Using both `Forwarded` and `X-Forwarded` headers can have security implications as it may allow clients to forge requests with a header that is not overwritten by the proxy.

Ensure that your proxy is configured to strip unexpected `Forwarded` or `X-Forwarded-*` headers from the client request.

## Kubernetes

When Quarkus generates the Kubernetes metadata, it checks if the management interface is enabled and configures the probes accordingly.
The resulting descriptor defines the main HTTP port (named `http`) and the management port (named `management`).
Health probes (using HTTP actions) and Prometheus scrape URLs are configured using the `management` port.

<dl><dt><strong>❗ IMPORTANT: KNative</strong></dt><dd>

Until [KNative#8471](https://github.com/knative/serving/issues/8471) is resolved, you cannot use the management interface, as KNative does not support containers will multiple exposed ports.
</dd></dl>

## CORS filter

To make your Quarkus management interface accessible to another application running on a different domain, you need to configure cross-origin resource sharing (CORS).
For more information about the CORS filter that Quarkus provides, see the Quarkus [CORS filter](../02-web-http/security-cors.md#cors-filter) section of the "Cross-origin resource sharing" guide.

The management interface uses the same CORS filter mechanism as the main HTTP server, but with separate configuration under `quarkus.management.cors.*`.

For example, to allow requests from a specific origin:

```properties
quarkus.management.enabled=true
quarkus.management.cors.enabled=true
quarkus.management.cors.origins=http://example.com
```

When CORS is enabled without configuring specific origins, only same-origin requests are allowed.

## HTTP Host header validation

The management interface supports the same HTTP `Host` header validation as the main HTTP server, but with separate configuration under `quarkus.management.host-validation.*`.

When `quarkus.management.host` is set to a localhost name (`localhost`, `127.0.0.1`, or `[::1]`), host validation is automatically enabled in ***dev*** and ***production*** modes.

<dl><dt><strong>⚠️ WARNING</strong></dt><dd>

This automatic behavior is a change from previous Quarkus versions.
If the management interface is accessed through a reverse proxy or a non-localhost host name, configure the allowed hosts explicitly or disable automatic validation.
</dd></dl>

For example, to restrict requests to specific host names:

```properties
quarkus.management.enabled=true
quarkus.management.host-validation.allowed-hosts=management.example.com
```

To disable automatic localhost validation:

```properties
quarkus.management.enabled=true
quarkus.management.host-validation.require-localhost=false
```

For more details on the available options and reverse proxy considerations, see the [HTTP Host header validation](../02-web-http/http-reference.md#host-header-validation) section in the HTTP reference guide.

**📌 NOTE**\
La tabla de configuracion generada `quarkus-vertx-http_quarkus.management.host-validation` se produce al construir la documentacion y no existe en el codigo fuente. Consulta la referencia de configuracion en https://quarkus.io/guides/all-config

## Security

Security for the management endpoints exposed in the separate HTTP server needs to be enabled explicitly like in the example below:

```properties
quarkus.management.enabled=true
quarkus.management.auth.enabled=true
```

Once enabled, you can use same authentication mechanism you have already configured for the main server, or use a different one.
All of these mechanisms are detailed in the [Authentication mechanisms in Quarkus](https://quarkus.io/guides/security-authentication-mechanisms) guide.

### Use HTTP Security Policy to enable path-based authentication

The following configuration example demonstrates how you can enforce a single selectable authentication mechanism for a given request path:

```properties
quarkus.management.auth.permission.metrics.paths=/q/metrics/*
quarkus.management.auth.permission.metrics.policy=authenticated
quarkus.management.auth.permission.metrics.auth-mechanism=basic ①

quarkus.management.auth.permission.health.paths=/q/health/*
quarkus.management.auth.permission.health.policy=authenticated
quarkus.management.auth.permission.health.auth-mechanism=bearer ②
```
1. The metric endpoints will be only accessible with the [Basic authentication](#basic-authentication).
2. If the Quarkus OIDC extension is present, the health endpoints will be authenticated
by the [OIDC Bearer token authentication](https://quarkus.io/guides/security-oidc-bearer-token-authentication).

### Basic authentication

You can enable _basic_ authentication using the following properties:

```properties
quarkus.management.enabled=true
# Enable basic authentication
quarkus.management.auth.basic=true
# Require all access to /q/* to be authenticated
quarkus.management.auth.permission.all.policy=authenticated
quarkus.management.auth.permission.all.paths=/q/*
```

You can also use different permissions for different paths or use role bindings:

```properties
quarkus.management.enabled=true
# Enable basic authentication
quarkus.management.auth.basic=true
# Configure a management policy if needed, here the policy `management-policy` requires users to have the role `management`.
quarkus.management.auth.policy.management-policy.roles-allowed=management

# For each endpoint you can configure the permissions
# Health used the management-policy (so requires authentication + the `management` role)
quarkus.management.auth.permission.health.paths=/q/health/*
quarkus.management.auth.permission.health.policy=management-policy

# Metrics just requires authentication
quarkus.management.auth.permission.metrics.paths=/q/metrics/*
quarkus.management.auth.permission.metrics.policy=authenticated
```

More details about Basic authentication in Quarkus can be found in the [Basic authentication guide](https://quarkus.io/guides/security-basic-authentication-howto).

## Injecting management URL in tests

When testing your application, you can inject the management URL using the `@TestHTTPResource` annotation:

```java
@TestHTTPResource(value="/management", management=true)
URL management;
```

The `management` attribute is set to `true` to indicate that the injected URL is for the management interface.
The `context-root` is automatically added.
Thus, in the previous example, the injected URL is `http://localhost:9001/q/management`.

`@TestHTTPResource` is particularly useful when setting the management `test-port` to 0, which indicates that the system will assign a random port to the management interface:

```properties
quarkus.management.test-port=0
```
