# How can I integrate Mutiny with my framework?

> **Documentacion oficial:** <https://smallrye.io/smallrye-mutiny/latest/guides/framework-integration>  
> **Fuente:** `documentation/docs/guides/framework-integration.md` en [smallrye/smallrye-mutiny@3.3.0](https://github.com/smallrye/smallrye-mutiny/blob/3.3.0/documentation/docs/guides/framework-integration.md)  
> **Version documentada:** Mutiny 3.3.0 · **Sincronizado:** 2026-08-17 · **Licencia:** Apache-2.0

Sometimes, Mutiny needs to execute tasks on other threads, such as monitoring time or delaying actions.
Most operators relying on such capacity let you pass either a `ScheduledExecutorService` or an `ExecutorService`.

By default, Mutiny uses the a _cached_ thread pool as default executor, that creates new threads as needed, but reuse previously constructed threads when they are available.
A `ScheduledExecutorService` is also created but delegates the execution of the delayed/scheduled tasks to the default executor.

In the case you want to integrate Mutiny with a thread pool managed by a platform, you can configure it using `Infrastructure.setDefaultExecutor()` method:

```java
Uni<Integer> uni1 = Uni.createFrom().item(1)
        .emitOn(Infrastructure.getDefaultExecutor());

Uni<Integer> uni2 = Uni.createFrom().item(2)
        .onItem().delayIt()
            .onExecutor(Infrastructure.getDefaultWorkerPool())
            .by(Duration.ofMillis(10));
```

You can configure the default executor using the `Infrastructure.setDefaultExecutor` method:

```java
Infrastructure.setDefaultExecutor(executor);
```

> **💡 CONSEJO**
>
> If you are using Quarkus, the default executor is already configured to use the Quarkus worker thread pool.
> Logging is also configured correctly.
