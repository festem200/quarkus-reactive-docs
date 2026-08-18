# How to handle timeouts?

> **Documentacion oficial:** <https://smallrye.io/smallrye-mutiny/latest/guides/handling-timeouts>  
> **Fuente:** `documentation/docs/guides/handling-timeouts.md` en [smallrye/smallrye-mutiny@3.3.0](https://github.com/smallrye/smallrye-mutiny/blob/3.3.0/documentation/docs/guides/handling-timeouts.md)  
> **Version documentada:** Mutiny 3.3.0 · **Sincronizado:** 2026-08-17 · **Licencia:** Apache-2.0

Unis are often used to represent asynchronous operations, like making an HTTP call.
So, it's not rare to need to add a timeout or a deadline on this kind of operation.
If we don't get a response (receive an item in the Mutiny lingo) before that deadline, we consider that the operation failed.

We can then recover from this failure by using a fallback value, retrying, or any other failure handling strategy.

To configure a timeout use `Uni.ifNoItem().after(Duration)`:

```java
Uni<String> uniWithTimeout = uni
        .ifNoItem().after(Duration.ofMillis(100))
        .recoverWithItem("some fallback item");
```

When the deadline is reached, you can do various actions.
First you can simply fail:

```java
Uni<String> uniWithTimeout = uni
        .ifNoItem().after(Duration.ofMillis(100)).fail();
```

A `TimeoutException` is propagated in this case.
So you can handle it specifically in the downstream:

```java
Uni<String> uniWithTimeout = uni
    .ifNoItem().after(Duration.ofMillis(100)).fail()
    .onFailure(TimeoutException.class).recoverWithItem("we got a timeout");
```

You can also pass a custom exception:

```java
Uni<String> uniWithTimeout = uni
    .ifNoItem().after(Duration.ofMillis(100)).failWith(() -> new ServiceUnavailableException());
```

Failing and recovering might be inconvenient.
So, you can pass a fallback item or `Uni` directly:

```java
Uni<String> uniWithTimeout = uni
        .ifNoItem().after(Duration.ofMillis(100)).recoverWithItem(() -> "fallback");
```

```java
Uni<String> uniWithTimeout = uni
        .ifNoItem().after(Duration.ofMillis(100)).recoverWithUni(() -> someFallbackUni());
```
