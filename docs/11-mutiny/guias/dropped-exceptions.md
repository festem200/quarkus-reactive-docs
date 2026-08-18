# How to deal with dropped exceptions?

> **Documentacion oficial:** <https://smallrye.io/smallrye-mutiny/latest/guides/dropped-exceptions>  
> **Fuente:** `documentation/docs/guides/dropped-exceptions.md` en [smallrye/smallrye-mutiny@3.3.0](https://github.com/smallrye/smallrye-mutiny/blob/3.3.0/documentation/docs/guides/dropped-exceptions.md)  
> **Version documentada:** Mutiny 3.3.0 · **Sincronizado:** 2026-08-17 · **Licencia:** Apache-2.0

There are a few corner cases where Mutiny cannot propagate an exception to a `Uni` or a `Multi` subscriber.

Consider the following example:

```java
Cancellable cancellable = Uni.createFrom()
        .emitter(this::emitter)
        .onCancellation().call(() -> Uni.createFrom().failure(new IOException("boom")))
        .subscribe().with(this::onItem, this::onFailure);

cancellable.cancel();
```

The `onCancellation().call(...)` method is called when the `Uni` subscription is cancelled.
The returned `Uni` is failed with a `IOException`, but since the subscription itself has been cancelled then there is no way to catch the exception.

By default Mutiny reports such dropped exceptions to the standard error stream along with the corresponding stack trace.
You can change how these exceptions are handled using `Infrastructure.setDroppedExceptionHandler`.

The following logs dropped exceptions to a logger:

```java
Infrastructure.setDroppedExceptionHandler(err ->
        log(Level.SEVERE, "Mutiny dropped exception", err)
);
```
