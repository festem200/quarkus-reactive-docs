# Redis Cache

> **Guia oficial:** <https://quarkus.io/guides/cache-redis-reference>  
> **Fuente:** `docs/src/main/asciidoc/cache-redis-reference.adoc` en [quarkusio/quarkus@3.38.2](https://github.com/quarkusio/quarkus/blob/3.38.2/docs/src/main/asciidoc/cache-redis-reference.adoc)  
> **Version documentada:** Quarkus 3.38.2 · **Sincronizado:** 2026-08-17 · **Licencia:** Apache-2.0

By default, Quarkus Cache uses Caffeine as backend.
It’s possible to use Redis instead.

<dl><dt><strong><a name="extension-status-note"></a>📌 NOTE</strong></dt><dd>

This technology is considered preview.

## Redis as cache backend

When using Redis as the backend for Quarkus cache, each cached item will be stored in Redis:

* The backend uses the _&lt;default>_ Redis client (if not configured otherwise), so make sure it’s configured (or use the [Redis Dev Service](redis-dev-services.md))
* the Redis key is built as follows: `cache:{cache-name}:{cache-key}`, where `cache-key` is the key the application uses and `cache:{cache-name}` the prefix.
* the value is encoded to JSON if needed

## Use the Redis backend

First, you need to add the `quarkus-redis-cache` extension to your project:

**pom.xml**

```xml
<dependency>
    <groupId>io.quarkus</groupId>
    <artifactId>quarkus-redis-cache</artifactId>
</dependency>
```

**build.gradle**

```gradle
implementation("io.quarkus:quarkus-redis-cache")
```

Then, use the `@CacheResult` and others cache annotations as explained in the [Quarkus Cache guide](cache.md):

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

## Configure the Redis backend

The Redis backend uses the `<default>` Redis client.
See the [Redis reference](redis-reference.md) to configure the access to Redis.

**💡 TIP**\
In dev mode, you can use the [Redis Dev Service](redis-dev-services.md).

If you want to use another Redis for your cache, configure the `client-name` as follows:

```properties
quarkus.cache.redis.client-name=my-redis-for-cache
```

When writing to Redis or reading from Redis, Quarkus needs to know the type.
Indeed, the objects need to be serialized and deserialized.
For that purpose, you may need to configure type (class names) of the key and value you want to cache.
At build time, Quarkus tries to deduce the types from the application code, but that decision can be overridden using:

```properties
# Default configuration
quarkus.cache.redis.key-type=java.lang.String
quarkus.cache.redis.value-type=org.acme.Person

# Configuration for `expensiveResourceCache`
quarkus.cache.redis.expensiveResourceCache.key-type=java.lang.String
quarkus.cache.redis.expensiveResourceCache.value-type=org.acme.Supes
```

You can also configure the time to live of the cached entries:

```properties
# Default configuration
quarkus.cache.redis.expire-after-write=10s

# Configuration for `expensiveResourceCache`
quarkus.cache.redis.expensiveResourceCache.expire-after-write=1h
```

If the `expire-after-write` is not configured, the entry won’t be evicted.
You would need to invalidate the values using the `@CacheInvalidateAll` or `@CacheInvalidate` annotations.

The following table lists the supported properties:

**📌 NOTE**\
La tabla de configuracion generada `quarkus-redis-cache` se produce al construir la documentacion y no existe en el codigo fuente. Consulta la referencia de configuracion en https://quarkus.io/guides/all-config

## Configure the Redis key

By default, the Redis backend stores the entry using the following keys pattern: `cache:{cache-name}:{cache-key}`, where `cache-key` is the key the application uses and `cache:{cache-name}` the prefix. The variable `{cache-name}` is resolved from the value set in the cache annotations.
So, you can find all the entries for a single cache using the Redis `KEYS` command: `KEYS cache:{cache-name}:*`

The prefix can be configured by using the `prefix` property:

```properties
# Default configuration
quarkus.cache.redis.prefix=my-cache

# Configuration for `expensiveResourceCache`
quarkus.cache.redis.expensiveResourceCache.prefix=my-expensive-cache
```

In these cases, you can find all the keys managed by the default cache using `KEYS my-cache:**`, and all the keys managed by the `expensiveResourceCache` cache using: `KEYS my-expensive-cache:**`.

```
# Default configuration
# The variable "{cache-name}" is resolved from the value set in the cache annotations.
quarkus.cache.redis.prefix=my-cache-{cache-name}
```

In this latest example, you can find all the keys managed by the default cache using `KEYS my-cache-{cache-name}:*`.

## Enable optimistic locking

The access to the cache can be _direct_ or use [optimistic locking](https://redis.io/docs/manual/transactions/#optimistic-locking-using-check-and-set).
By default, optimistic locking is disabled.

You can enable optimistic locking using:
```properties
# Default configuration
quarkus.cache.redis.use-optimistic-locking=true

# Configuration for `expensiveResourceCache`
quarkus.cache.redis.expensiveResourceCache.use-optimistic-locking=true
```

When used, the key is _watched_ and the _SET_ command is executed in a transaction (`MULTI/EXEC`).
