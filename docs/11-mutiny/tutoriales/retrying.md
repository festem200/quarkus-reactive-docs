# Retrying on failures

> **Documentacion oficial:** <https://smallrye.io/smallrye-mutiny/latest/tutorials/retrying>  
> **Fuente:** `documentation/docs/tutorials/retrying.md` en [smallrye/smallrye-mutiny@3.3.0](https://github.com/smallrye/smallrye-mutiny/blob/3.3.0/documentation/docs/tutorials/retrying.md)  
> **Version documentada:** Mutiny 3.3.0 · **Sincronizado:** 2026-08-17 · **Licencia:** Apache-2.0

It is common to want to retry if something terrible happened.

You can retry upon failure.
The [How does retry... retries](https://quarkus.io/blog/uni-retry/) blog post provides a more detailed overview of the retry mechanism.

> **📌 NOTA**
>
> If despite multiple attempts, it still fails, the failure is propagated downstream.

## Retry multiple times

To retry on failure, use `onFailure().retry()`:

```java
Uni<String> u = uni
        .onFailure().retry().atMost(3);
Multi<String> m = multi
        .onFailure().retry().atMost(3);
```

You pass the number of retries as a parameter.

> **❗ IMPORTANTE**
>
> While `.onFailure().retry().indefinitely()` is available, it may never terminate, so use it with caution.

## Introducing delays

By default, `retry` retries immediately.
When using remote services, it is often better to delay a bit the attempts.

Mutiny provides a method to configure an exponential backoff: a growing delay between retries.
Configure the exponential backoff as follows:

```java
Uni<String> u = uni
        .onFailure().retry()
        .withBackOff(Duration.ofMillis(100), Duration.ofSeconds(1))
        .atMost(3);
```

The backoff is configured with the initial and max delay.
Optionally, you can also configure a jitter to add a pinch of randomness to the delay.

When using exponential backoff, you may not want to configure the max number of attempts (`atMost`), but a deadline.
To do so, use either `expireIn` or `expireAt`.

## Deciding to retry

As an alternative to `atMost`, you can also use `until`.
This method accepts a predicate called after every failure.
When used, a backoff should not be used.

If the predicate returned `true,` it retries.
Otherwise, it stops retrying and propagates the last failure downstream:

```java
Uni<String> u = uni
        .onFailure().retry()
        .until(f -> shouldWeRetry(f));
```
