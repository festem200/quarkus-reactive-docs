# Infinispan Cache

> **Guia oficial:** <https://quarkus.io/guides/cache-infinispan-reference>  
> **Fuente:** `docs/src/main/asciidoc/cache-infinispan-reference.adoc` en [quarkusio/quarkus@3.38.2](https://github.com/quarkusio/quarkus/blob/3.38.2/docs/src/main/asciidoc/cache-infinispan-reference.adoc)  
> **Version documentada:** Quarkus 3.38.2 · **Sincronizado:** 2026-08-17 · **Licencia:** Apache-2.0

By default, Quarkus Cache uses Caffeine as backend.
It’s possible to use Infinispan instead.

<dl><dt><strong><a name="extension-status-note"></a>📌 NOTE</strong></dt><dd>

This technology is considered preview.

## Infinispan as cache backend

When using Infinispan as the backend for Quarkus cache, each cached item will be stored in Infinispan:

* The backend uses the _&lt;default>_ Infinispan client (unless configured differently), so ensure its configuration is
set up accordingly (or use the [Infinispan Dev Service](https://quarkus.io/guides/infinispan-dev-services))
* Both the key and the value are marshalled using Protobuf with Protostream.

## Use the Infinispan backend

First, add the `quarkus-infinispan-cache` extension to your project:

**pom.xml**

```xml
<dependency>
    <groupId>io.quarkus</groupId>
    <artifactId>quarkus-infinispan-cache</artifactId>
</dependency>
```

**build.gradle**

```gradle
implementation("io.quarkus:quarkus-infinispan-cache")
```

Then, use the `@CacheResult` and other cache annotations as detailed in the [Quarkus Cache guide](cache.md):

```java
@GET
@Path("/{keyElement1}/{keyElement2}/{keyElement3}")
@CacheResult(cacheName = "expensiveResourceCache")
public ExpensiveResponse getExpensiveResponse(@PathParam("keyElement1") @CacheKey String keyElement1,
        @PathParam("keyElement2") @CacheKey String keyElement2, @PathParam("keyElement3") @CacheKey String keyElement3,
        @QueryParam("foo") String foo) {
    invocations.incrementAndGet();
    ExpensiveResponse response = new ExpensiveResponse();
    response.setResult(keyElement1 + " " + keyElement2 + " " + keyElement3 + " too!");
    return response;
}

@POST
@CacheInvalidateAll(cacheName = "expensiveResourceCache")
public void invalidateAll() {

}
```

## Configure the Infinispan backend

The Infinispan backend uses the `<default>` Infinispan client.
Refer to the [Infinispan reference](infinispan-client-reference.md) for configuring the access to Infinispan.

**💡 TIP**\
In dev mode, you can use the [Infinispan Dev Service](https://quarkus.io/guides/infinispan-dev-services).

If you want to use another Infinispan for your cache, configure the `client-name` as follows:

```properties
quarkus.cache.infinispan.client-name=another
```

## Marshalling

When interacting with Infinispan in Quarkus, you can easily serialize and deserialize Java primitive types when storing or retrieving data from the cache. No additional marshalling configuration is required for Infinispan.

```java
@CacheResult(cacheName = "weather-cache") //<1>
public String getDailyForecast(String dayOfWeek, int dayOfMonth, String city) { //<2>
    return dayOfWeek + " will be " + getDailyResult(dayOfMonth % 4) + " in " + city;
}
```
1. Ask this method execution to be cached in the 'weather-cache'
2. The key combines `String` dayOfWeek, `int` dayOfMonth and `String` city. The associated value is of type `String`.

Quarkus uses Protobuf for data serialization in Infinispan by default. Infinispan recommends using Protobuf as the preferred
way to structure data. Therefore, when working with Plain Old Java Objects (POJOs), users need
to supply the schema for marshalling in Infinispan.

### Marshalling Java types

Let’s say we want a composite Key using `java.time.LocalDate`.

```java
@CacheResult(cacheName = "weather-cache") //<1>
public String getDailyForecast(LocalDate date, String city) { //<2>
    return date.getDayOfWeek() + " will be " + getDailyResult(date.getDayOfMonth() % 4) + " in " + city;
}
```
1. Request that the response of this method execution be cached in 'weather-cache'
2. The key combines a `java.util.LocalDate` date and a `String` city. The associated value is of type 'String'.

Since Infinispan serializes data by default using Protobuf in Quarkus, executing the code will result in the following error:

```bash
java.lang.IllegalArgumentException:
No marshaller registered for object of Java type java.time.LocalDate
```

Protobuf does not inherently know how to marshal `java.time.LocalDate`. Fortunately, Protostream provides a straightforward solution to this problem using `@ProtoAdapter` and `@ProtoSchema`.

```java
@ProtoAdapter(LocalDate.class)
public class LocalDateAdapter {
    @ProtoFactory
    LocalDate create(String localDate) {
        return LocalDate.parse(localDate);
    }

    @ProtoField(1)
    String getLocalDate(LocalDate localDate) {
        return localDate.toString();
    }
}

@ProtoSchema(includeClasses = LocalDateAdapter.class, schemaPackageName = "quarkus")
public interface Schema extends GeneratedSchema {
}
```

### Marshalling your POJOs

Just like with Java types, when using your POJOs as keys or values, you can follow this approach:

```java
@CacheResult(cacheName = "my-cache") //<1>
public ExpensiveResponse requestApi(String id) { //<2>
    // very expensive call

    return new ExpensiveResponse(...);
}
```
1. Request that the response of this method execution be cached in 'my-cache'
2. The key is a `String`. The associated value is of type `org.acme.ExpensiveResponse`.

In this case, you’ll need to define the schema for your Java type using `@Proto` and `@ProtoSchema`. This schema can encompass all types and adapters used in your Quarkus application.

```java
@Proto
public record ExpensiveResponse(String result) {
}

@ProtoSchema(includeClasses = { ExpensiveResponse.class })
interface Schema extends GeneratedSchema {
}
```

Read more about it in the [Infinispan reference](infinispan-client-reference.md) in the Annotation
based serialization section.

## Expiration

You have the option to configure two properties for data expiration: **lifespan** and **max-idle**.

### Lifespan

In Infinispan, **lifespan** refers to a configuration parameter that determines the maximum time an
entry (or an object) can remain in the cache since it was created or last accessed before it is
considered expired and removed from the cache.

When you configure the **lifespan** parameter for entries in an Infinispan cache,
you specify a time duration. After an entry has been added to the cache or accessed
(read or written), it starts its lifespan countdown. If the time since the entry
was created or last accessed exceeds the specified "lifespan" duration, the entry
is considered expired and becomes eligible for eviction from the cache.

```properties
quarkus.cache.infinispan.my-cache.lifespan=10s
```

### Max Idle
When you configure the **max-idle** parameter for entries in an Infinispan cache, you specify a time
duration. After an entry has been accessed (read or written) in the cache, if there are no subsequent
accesses to that entry within the specified duration, it is considered idle. Once the idle time
exceeds the **max-idle** duration, the entry is considered expired and eligible for eviction from
the cache.

```properties
quarkus.cache.infinispan.my-cache.max-idle=100s
```

**📌 NOTE**\
La tabla de configuracion generada `quarkus-infinispan-cache` se produce al construir la documentacion y no existe en el codigo fuente. Consulta la referencia de configuracion en https://quarkus.io/guides/all-config
