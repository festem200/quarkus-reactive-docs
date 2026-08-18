# Using the legacy REST Client

> **Guia oficial:** <https://quarkus.io/guides/resteasy-client>  
> **Fuente:** `docs/src/main/asciidoc/resteasy-client.adoc` en [quarkusio/quarkus@3.38.2](https://github.com/quarkusio/quarkus/blob/3.38.2/docs/src/main/asciidoc/resteasy-client.adoc)  
> **Version documentada:** Quarkus 3.38.2 · **Sincronizado:** 2026-08-17 · **Licencia:** Apache-2.0

<dl><dt><strong>⚠️ WARNING</strong></dt><dd>

This guide is about the REST Client compatible with [RESTEasy Classic](https://resteasy.dev) which used to be the default Jakarta REST (formerly known as JAX-RS) implementation until Quarkus 2.8.

It is now recommended to use Quarkus REST (formerly RESTEasy Reactive), which supports equally well traditional blocking workloads and reactive workloads.
For more information about Quarkus REST,
please see the [REST Client guide](rest-client.md) and, for the server side, the [introductory REST JSON guide](rest-json.md) or the more detailed [Quarkus REST guide](rest.md).
</dd></dl>

This guide explains how to use the RESTEasy REST Client in order to interact with REST APIs
with very little effort.

**💡 TIP**\
there is another guide if you need to write server [JSON REST APIs](rest-json.md).

## Prerequisites

To complete this guide, you need:

* Roughly 15 minutes
* An IDE
* JDK 17+ installed with `JAVA_HOME` configured appropriately
* Apache Maven 3.9.16
* Optionally the [Quarkus CLI](../10-extras/cli-tooling.md) if you want to use it
* Optionally Mandrel or GraalVM installed and [configured appropriately](../08-rendimiento-nativo/building-native-image.md#configuring-graalvm) if you want to build a native executable (or Docker if you use a native container build)

## Solution

We recommend that you follow the instructions in the next sections and create the application step by step.
However, you can go right to the completed example.

Clone the Git repository: `git clone https://github.com/quarkusio/quarkus-quickstarts.git`, or download an [archive](https://github.com/quarkusio/quarkus-quickstarts/archive/main.zip).

The solution is located in the `resteasy-client-quickstart` [directory](https://github.com/quarkusio/quarkus-quickstarts/tree/main/resteasy-client-quickstart).

## Creating the Maven project

First, we need a new project. Create a new project with the following command:

**CLI**

```bash
quarkus create app org.acme:resteasy-client-quickstart \
    --extension='resteasy,resteasy-jackson,resteasy-client,resteasy-client-jackson' \
    --no-code
cd resteasy-client-quickstart
```

To create a Gradle project, add the `--gradle` or `--gradle-kotlin-dsl` option.

For more information about how to install and use the Quarkus CLI, see the [Quarkus CLI](../10-extras/cli-tooling.md) guide.

**Maven**

```bash
mvn io.quarkus.platform:quarkus-maven-plugin:3.38.2:create \
    -DprojectGroupId=org.acme \
    -DprojectArtifactId=resteasy-client-quickstart \
    -Dextensions='resteasy,resteasy-jackson,resteasy-client,resteasy-client-jackson' \
    -DnoCode
cd resteasy-client-quickstart
```

To create a Gradle project, add the `-DbuildTool=gradle` or `-DbuildTool=gradle-kotlin-dsl` option.

For Windows users:

* If using cmd, (don’t use backward slash `\` and put everything on the same line)
* If using Powershell, wrap `-D` parameters in double quotes e.g. `"-DprojectArtifactId=resteasy-client-quickstart"`

This command generates the Maven project with a REST endpoint and imports:

* the `resteasy` and `resteasy-jackson` extensions for the REST server support;
* the `resteasy-client` and `resteasy-client-jackson` extensions for the REST client support.

If you already have your Quarkus project configured, you can add the `resteasy-client` and the `resteasy-client-jackson` extensions
to your project by running the following command in your project base directory:

**CLI**

```bash
quarkus extension add resteasy-client,resteasy-client-jackson
```
**Maven**

```bash
./mvnw quarkus:add-extension -Dextensions='resteasy-client,resteasy-client-jackson'
```
**Gradle**

```bash
./gradlew addExtension --extensions='resteasy-client,resteasy-client-jackson'
```

This will add the following to your `pom.xml`:

**pom.xml**

```xml
<dependency>
    <groupId>io.quarkus</groupId>
    <artifactId>quarkus-resteasy-client</artifactId>
</dependency>
<dependency>
    <groupId>io.quarkus</groupId>
    <artifactId>quarkus-resteasy-client-jackson</artifactId>
</dependency>
```

**build.gradle**

```gradle
implementation("io.quarkus:quarkus-resteasy-client")
implementation("io.quarkus:quarkus-resteasy-client-jackson")
```

## Setting up the model

In this guide we will be demonstrating how to consume part of the REST API supplied by the [stage.code.quarkus.io](https://stage.code.quarkus.io) service.
Our first order of business is to set up the model we will be using, in the form of an `Extension` POJO.

Create a `src/main/java/org/acme/rest/client/Extension.java` file and set the following content:

```java
package org.acme.rest.client;

import java.util.List;

public class Extension {

    public String id;
    public String name;
    public String shortName;
    public List<String> keywords;

}
```

The model above is only a subset of the fields provided by the service, but it suffices for the purposes of this guide.

## Create the interface

Using the RESTEasy REST Client is as simple as creating an interface using the proper Jakarta REST and MicroProfile annotations. In our case the interface should be created at `src/main/java/org/acme/rest/client/ExtensionsService.java` and have the following content:

```java
package org.acme.rest.client;

import org.eclipse.microprofile.rest.client.inject.RegisterRestClient;
import org.jboss.resteasy.annotations.jaxrs.QueryParam;

import jakarta.ws.rs.GET;
import jakarta.ws.rs.Path;
import jakarta.ws.rs.QueryParam;
import java.util.Set;

@Path("/extensions")
@RegisterRestClient
public interface ExtensionsService {

    @GET
    Set<Extension> getById(@QueryParam String id);
}
```

The `getById` method gives our code the ability to get an extension by id from the Code Quarkus API. The client will handle all the networking and marshalling leaving our code clean of such technical details.

The purpose of the annotations in the code above is the following:

* `@RegisterRestClient` allows Quarkus to know that this interface is meant to be available for
CDI injection as a REST Client
* `@Path`, `@GET` and `@QueryParam` are the standard Jakarta REST annotations used to define how to access the service

<dl><dt><strong>📌 NOTE</strong></dt><dd>

When a JSON extension is installed such as `quarkus-resteasy-client-jackson` or `quarkus-resteasy-client-jsonb`, Quarkus will use the `application/json` media type
by default for most return values, unless the media type is explicitly set via
`@Produces` or `@Consumes` annotations (there are some exceptions for well known types, such as `String` and `File`, which default to `text/plain` and `application/octet-stream`
respectively).

If you don’t want JSON by default you can set `quarkus.resteasy-json.default-json=false` and the default will change back to being auto-negotiated. If you set this
you will need to add `@Produces(MediaType.APPLICATION_JSON)` and `@Consumes(MediaType.APPLICATION_JSON)` to your endpoints in order to use JSON.

If you don’t rely on the JSON default, it is heavily recommended to annotate your endpoints with the `@Produces` and `@Consumes` annotations to define precisely the expected content-types.
It will allow to narrow down the number of Jakarta REST providers (which can be seen as converters) included in the native executable.
</dd></dl>

### Path Parameters

If the GET request requires path parameters you can leverage the `@PathParam("parameter-name")` annotation instead of (or in addition to) the `@QueryParam`. Path and query parameters can be combined, as required, as illustrated in a mock example below.

```java
package org.acme.rest.client;

import org.eclipse.microprofile.rest.client.inject.RegisterRestClient;
import org.jboss.resteasy.annotations.jaxrs.PathParam;
import org.jboss.resteasy.annotations.jaxrs.QueryParam;

import jakarta.ws.rs.GET;
import jakarta.ws.rs.Path;
import java.util.Set;

@Path("/extensions")
@RegisterRestClient
public interface ExtensionsService {

    @GET
    @Path("/stream/{stream}")
    Set<Extension> getByStream(@PathParam String stream, @QueryParam("id") String id);
}
```

## Create the configuration

In order to determine the base URL to which REST calls will be made, the REST Client uses configuration from `application.properties`.
The name of the property needs to follow a certain convention which is best displayed in the following code:

```properties
# Your configuration properties
quarkus.rest-client."org.acme.rest.client.ExtensionsService".url=https://stage.code.quarkus.io/api # // ①
quarkus.rest-client."org.acme.rest.client.ExtensionsService".scope=jakarta.inject.Singleton # // ②
```

1. Having this configuration means that all requests performed using `ExtensionsService` will use `https://stage.code.quarkus.io` as the base URL.
Using the configuration above, calling the `getById` method of `ExtensionsService` with a value of `io.quarkus:quarkus-resteasy-client` would result in an HTTP GET request being made to `https://stage.code.quarkus.io/api/extensions?id=io.quarkus:quarkus-rest-client`.
2. Having this configuration means that the default scope of `ExtensionsService` will be `@Singleton`. Supported scope values are `@Singleton`, `@Dependent`, `@ApplicationScoped` and `@RequestScoped`. The default scope is `@Dependent`.
The default scope can also be defined on the interface.

Note that `org.acme.rest.client.ExtensionsService` _must_ match the fully qualified name of the `ExtensionsService` interface we created in the previous section.

<dl><dt><strong>📌 NOTE</strong></dt><dd>

The standard MicroProfile Rest Client properties notation can also be used to configure the client:

```properties
org.acme.rest.client.ExtensionsService/mp-rest/url=https://stage.code.quarkus.io/api
org.acme.rest.client.ExtensionsService/mp-rest/scope=jakarta.inject.Singleton
```

If a property is specified via both the Quarkus notation and the MicroProfile notation, the Quarkus notation takes a precedence.
</dd></dl>

To facilitate the configuration, you can use the `@RegisterRestClient` `configKey` property that allows to use another configuration root than the fully qualified name of your interface.

```java

@RegisterRestClient(configKey="extensions-api")
public interface ExtensionsService {
    [...]
}
```

```properties
# Your configuration properties
quarkus.rest-client.extensions-api.url=https://stage.code.quarkus.io/api
quarkus.rest-client.extensions-api.scope=jakarta.inject.Singleton
```

### Disabling Hostname Verification

To disable the SSL hostname verification for a specific REST client, add the following property to your configuration:

```properties
quarkus.rest-client.extensions-api.verify-host=false
```
<dl><dt><strong>⚠️ WARNING</strong></dt><dd>

This setting should not be used in production as it will disable the SSL hostname verification.
</dd></dl>

Moreover, you can configure a REST client to use your custom hostname verify strategy. All you need to do is to provide a class that implements the interface `javax.net.ssl.HostnameVerifier` and add the following property to your configuration:

```properties
quarkus.rest-client.extensions-api.hostname-verifier=<full qualified custom hostname verifier class name>
```

<dl><dt><strong>📌 NOTE</strong></dt><dd>

Quarkus REST client provides an embedded hostname verifier strategy to disable the hostname verification called `io.quarkus.restclient.NoopHostnameVerifier`.
</dd></dl>

### Disabling SSL verifications

To disable all SSL verifications, add the following property to your configuration:

```properties
quarkus.tls.trust-all=true
```
<dl><dt><strong>⚠️ WARNING</strong></dt><dd>

This setting should not be used in production as it will disable any kind of SSL verification.
</dd></dl>

## Create the Jakarta REST resource

Create the `src/main/java/org/acme/rest/client/ExtensionsResource.java` file with the following content:

```java
package org.acme.rest.client;

import org.eclipse.microprofile.rest.client.inject.RestClient;
import org.jboss.resteasy.annotations.jaxrs.PathParam;

import jakarta.inject.Inject;
import jakarta.ws.rs.GET;
import jakarta.ws.rs.Path;
import java.util.Set;

@Path("/extension")
public class ExtensionsResource {

    @Inject
    @RestClient
    ExtensionsService extensionsService;

    @GET
    @Path("/id/{id}")
    public Set<Extension> id(@PathParam String id) {
        return extensionsService.getById(id);
    }
}
```

Note that in addition to the standard CDI `@Inject` annotation, we also need to use the MicroProfile `@RestClient` annotation to inject `ExtensionsService`.

## Update the test

We also need to update the functional test to reflect the changes made to the endpoint.
Edit the `src/test/java/org/acme/rest/client/ExtensionsResourceTest.java` file and change the content of the `testExtensionIdEndpoint` method to:

```java
package org.acme.rest.client;

import static io.restassured.RestAssured.given;
import static org.hamcrest.CoreMatchers.hasItem;
import static org.hamcrest.CoreMatchers.is;
import static org.hamcrest.Matchers.greaterThan;

import org.acme.rest.client.resources.WireMockExtensionsResource;
import org.junit.jupiter.api.Test;

import io.quarkus.test.common.QuarkusTestResource;
import io.quarkus.test.junit.QuarkusTest;

@QuarkusTest
@QuarkusTestResource(WireMockExtensionsResource.class)
public class ExtensionsResourceTest {

    @Test
    public void testExtensionsIdEndpoint() {
        given()
            .when().get("/extension/id/io.quarkus:quarkus-rest-client")
            .then()
            .statusCode(200)
            .body("$.size()", is(1),
                "[0].id", is("io.quarkus:quarkus-rest-client"),
                "[0].name", is("REST Client Classic"),
                "[0].keywords.size()", greaterThan(1),
                "[0].keywords", hasItem("rest-client"));
    }
}
```

The code above uses [REST Assured](https://rest-assured.io/)'s [json-path](https://github.com/rest-assured/rest-assured/wiki/GettingStarted#jsonpath) capabilities.

## Redirection

A HTTP server can redirect a response to another location by sending a response with a status code that starts with "3" and a HTTP header "Location" holding the URL to be redirected to. When the REST Client receives a redirection response from a HTTP server, it won’t automatically perform another request to the new location. However, you can enable the automatic redirection by enabling the "follow-redirects" property:

* `quarkus.rest-client.follow-redirects` to enable redirection for all REST clients.
* `quarkus.rest-client.<client-prefix>.follow-redirects` to enable redirection for a specific REST client.

If this property is true, then REST Client will perform a new request that it receives a redirection response from the HTTP server.

Additionally, we can limit the number of redirections using the property "max-redirects".

One important note is that according to the [RFC2616](https://www.rfc-editor.org/rfc/rfc2616#section-10.3.8) specs, by default the redirection will only happen for GET or HEAD methods.

## Async Support

The rest client supports asynchronous rest calls.
Async support comes in 2 flavors: you can return a `CompletionStage` or a `Uni` (requires the `quarkus-resteasy-client-mutiny` extension).
Let’s see it in action by adding a `getByIdAsync` method in our `ExtensionsService` REST interface. The code should look like:

```java
package org.acme.rest.client;

import java.util.Set;
import java.util.concurrent.CompletionStage;

import jakarta.ws.rs.GET;
import jakarta.ws.rs.Path;

import org.eclipse.microprofile.rest.client.inject.RegisterRestClient;
import org.jboss.resteasy.annotations.jaxrs.QueryParam;

@Path("/extensions")
@RegisterRestClient
public interface ExtensionsService {

    @GET
    Set<Extension> getById(@QueryParam String id);

    @GET
    CompletionStage<Set<Extension>> getByIdAsync(@QueryParam String id);

}
```

Open the `src/main/java/org/acme/rest/client/ExtensionsResource.java` file and update it with the following content:

```java
package org.acme.rest.client;

import java.util.Set;
import java.util.concurrent.CompletionStage;

import jakarta.inject.Inject;
import jakarta.ws.rs.GET;
import jakarta.ws.rs.Path;

import org.eclipse.microprofile.rest.client.inject.RestClient;
import org.jboss.resteasy.annotations.jaxrs.PathParam;

@Path("/extension")
public class ExtensionsResource {

    @Inject
    @RestClient
    ExtensionsService extensionsService;

    @GET
    @Path("/id/{id}")
    public Set<Extension> id(@PathParam String id) {
        return extensionsService.getById(id);
    }

    @GET
    @Path("/id-async/{id}")
    public CompletionStage<Set<Extension>> idAsync(@PathParam String id) {
        return extensionsService.getByIdAsync(id);
    }

}
```

To test asynchronous methods, add the test method below in `ExtensionsResourceTest`:
```java
@Test
public void testExtensionIdAsyncEndpoint() {
    given()
        .when().get("/extension/id-async/io.quarkus:quarkus-rest-client")
        .then()
        .statusCode(200)
        .body("$.size()", is(1),
            "[0].id", is("io.quarkus:quarkus-rest-client"),
            "[0].name", is("REST Client Classic"),
            "[0].keywords.size()", greaterThan(1),
            "[0].keywords", hasItem("rest-client"));
}
```

The `Uni` version is very similar:

```java
package org.acme.rest.client;

import java.util.Set;
import java.util.concurrent.CompletionStage;

import jakarta.ws.rs.GET;
import jakarta.ws.rs.Path;

import org.eclipse.microprofile.rest.client.inject.RegisterRestClient;
import org.jboss.resteasy.annotations.jaxrs.QueryParam;

import io.smallrye.mutiny.Uni;

@Path("/extensions")
@RegisterRestClient
public interface ExtensionsService {

    // ...

    @GET
    Uni<Set<Extension>> getByIdAsUni(@QueryParam String id);
}
```

The `ExtensionsResource` becomes:

```java
package org.acme.rest.client;

import java.util.Set;
import java.util.concurrent.CompletionStage;

import jakarta.inject.Inject;
import jakarta.ws.rs.GET;
import jakarta.ws.rs.Path;

import org.eclipse.microprofile.rest.client.inject.RestClient;
import org.jboss.resteasy.annotations.jaxrs.PathParam;

import io.smallrye.mutiny.Uni;

@Path("/extension")
public class ExtensionsResource {

    @Inject
    @RestClient
    ExtensionsService extensionsService;

    // ...

    @GET
    @Path("/id-uni/{id}")
    public Uni<Set<Extension>> idMutiny(@PathParam String id) {
        return extensionsService.getByIdAsUni(id);
    }
}
```

<dl><dt><strong>💡 TIP: Mutiny</strong></dt><dd>

The previous snippet uses Mutiny reactive types.
If you are not familiar with Mutiny, check [Mutiny - an intuitive reactive programming library](../01-fundamentos/mutiny-primer.md).
</dd></dl>

When returning a `Uni`, every _subscription_ invokes the remote service.
It means you can re-send the request by re-subscribing on the `Uni`, or use a `retry` as follows:

```java

@Inject @RestClient ExtensionsService extensionsService;

// ...

extensionsService.getByIdAsUni(id)
    .onFailure().retry().atMost(10);
```

If you use a `CompletionStage`, you would need to call the service’s method to retry.
This difference comes from the laziness aspect of Mutiny and its subscription protocol.
More details about this can be found in [the Mutiny documentation](https://smallrye.io/smallrye-mutiny/latest/reference/uni-and-multi/).

## Custom headers support

The MicroProfile REST client allows amending request headers by registering a `ClientHeadersFactory` with the `@RegisterClientHeaders` annotation.

Let’s see it in action by adding a `@RegisterClientHeaders` annotation pointing to a `RequestUUIDHeaderFactory` class in our `ExtensionsService` REST interface:

```java
package org.acme.rest.client;

import java.util.Set;
import java.util.concurrent.CompletionStage;

import jakarta.ws.rs.GET;
import jakarta.ws.rs.Path;

import org.eclipse.microprofile.rest.client.annotation.RegisterClientHeaders;
import org.eclipse.microprofile.rest.client.inject.RegisterRestClient;
import org.jboss.resteasy.annotations.jaxrs.QueryParam;

import io.smallrye.mutiny.Uni;

@Path("/extensions")
@RegisterRestClient
@RegisterClientHeaders(RequestUUIDHeaderFactory.class)
public interface ExtensionsService {

    @GET
    Set<Extension> getById(@QueryParam String id);

    @GET
    CompletionStage<Set<Extension>> getByIdAsync(@QueryParam String id);

    @GET
    Uni<Set<Extension>> getByIdAsUni(@QueryParam String id);
}
```

And the `RequestUUIDHeaderFactory` would look like:

```java
package org.acme.rest.client;

import org.eclipse.microprofile.rest.client.ext.ClientHeadersFactory;

import jakarta.enterprise.context.ApplicationScoped;
import jakarta.ws.rs.core.MultivaluedHashMap;
import jakarta.ws.rs.core.MultivaluedMap;
import java.util.UUID;

@ApplicationScoped
public class RequestUUIDHeaderFactory implements ClientHeadersFactory {

    @Override
    public MultivaluedMap<String, String> update(MultivaluedMap<String, String> incomingHeaders, MultivaluedMap<String, String> clientOutgoingHeaders) {
        MultivaluedMap<String, String> result = new MultivaluedHashMap<>();
        result.add("X-request-uuid", UUID.randomUUID().toString());
        return result;
    }
}
```

As you see in the example above, you can make your `ClientHeadersFactory` implementation a CDI bean by
annotating it with a scope-defining annotation, such as `@Singleton`, `@ApplicationScoped`, etc.

### Default header factory

You can also use `@RegisterClientHeaders` annotation without any custom factory specified. In that case the `DefaultClientHeadersFactoryImpl` factory will be used and all headers listed in `org.eclipse.microprofile.rest.client.propagateHeaders` configuration property will be amended. Individual header names are comma-separated.
```java
@Path("/extensions")
@RegisterRestClient
@RegisterClientHeaders
public interface ExtensionsService {

    @GET
    Set<Extension> getById(@QueryParam String id);

    @GET
    CompletionStage<Set<Extension>> getByIdAsync(@QueryParam String id);

    @GET
    Uni<Set<Extension>> getByIdAsUni(@QueryParam String id);
}

```

```properties
org.eclipse.microprofile.rest.client.propagateHeaders=Authorization,Proxy-Authorization
```

## Package and run the application

Run the application with:

**CLI**

```bash
quarkus dev
```
**Maven**

```bash
./mvnw quarkus:dev
```
**Gradle**

```bash
./gradlew --console=plain quarkusDev
```

Open your browser to http://localhost:8080/extension/id/io.quarkus:quarkus-rest-client.

You should see a JSON object containing some basic information about the REST Client extension.

As usual, the application can be packaged using:

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

And executed with `java -jar target/quarkus-app/quarkus-run.jar`.

You can also generate the native executable with:

**CLI**

```bash
quarkus build --native
```
**Maven**

```bash
./mvnw install -Dnative
```
**Gradle**

```bash
./gradlew build -Dquarkus.native.enabled=true
```

## REST Client and RESTEasy interactions

In Quarkus, the REST Client extension and [the RESTEasy extension](rest-json.md) share the same infrastructure.
One important consequence of this consideration is that they share the same list of providers (in the Jakarta REST meaning of the word).

For instance, if you declare a `WriterInterceptor`, it will by default intercept both the servers calls and the client calls,
which might not be the desired behavior.

However, you can change this default behavior and constrain a provider to:

* only consider **client** calls by adding the `@ConstrainedTo(RuntimeType.CLIENT)` annotation to your provider;
* only consider **server** calls by adding the `@ConstrainedTo(RuntimeType.SERVER)` annotation to your provider.

## Using a Mock HTTP Server for tests

In some cases you may want to mock the remote endpoint - the HTTP server - instead of mocking the client itself.
This may be especially useful for native tests, or for programmatically created clients.

You can easily mock an HTTP Server with Wiremock.
The [Wiremock section of the Quarkus - Using the REST Client](rest-client.md#using-a-mock-http-server-for-tests)
describes how to set it up in detail.

## Further reading

* [MicroProfile Rest Client specification](https://download.eclipse.org/microprofile/microprofile-rest-client-2.0/microprofile-rest-client-spec-2.0.html)

## Configuration Reference

**📌 NOTE**\
La tabla de configuracion generada `quarkus-rest-client-config` se produce al construir la documentacion y no existe en el codigo fuente. Consulta la referencia de configuracion en https://quarkus.io/guides/all-config
