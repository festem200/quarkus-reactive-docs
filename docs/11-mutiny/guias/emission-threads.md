# How to change the emission thread?

> **Documentacion oficial:** <https://smallrye.io/smallrye-mutiny/latest/guides/emission-threads>  
> **Fuente:** `documentation/docs/guides/emission-threads.md` en [smallrye/smallrye-mutiny@3.3.0](https://github.com/smallrye/smallrye-mutiny/blob/3.3.0/documentation/docs/guides/emission-threads.md)  
> **Version documentada:** Mutiny 3.3.0 · **Sincronizado:** 2026-08-17 · **Licencia:** Apache-2.0

Except indicated otherwise, Mutiny invokes the next _stage_ using the thread emitting the event from upstream.
So, in the following code, the _transform_ stage is invoked from the thread emitting the event.

```java
Uni<String> uni = Uni.createFrom().<String>emitter(emitter ->
        new Thread(() ->
                emitter.complete("hello from "
                        + Thread.currentThread().getName())
        ).start()
)
        .onItem().transform(item -> {
            // Called on the emission thread.
            return item.toUpperCase();
        });
```

You can switch to another thread using the `emitOn` operator.
The `emitOn` operator lets you switch the thread used to dispatch (upstream -> downstream) events, so items, failure and completion events.
Just pass the _executor_ you want to use.

```java
String res0 = uni.emitOn(executor)
        .onItem()
        .invoke(s -> System.out.println("Received item `" + s + "` on thread: "
                + Thread.currentThread().getName()))
        .await().indefinitely();

String res1 = multi.emitOn(executor)
        .onItem()
        .invoke(s -> System.out.println("Received item `" + s + "` on thread: "
                + Thread.currentThread().getName()))
        .collect().first()
        .await().indefinitely();
```

> **📌 NOTA**
>
> You cannot pass a specific thread, but you can implement a simple `Executor` dispatching on that specific thread, or use a _single threaded executor_.

> **⚠️ AVISO**
>
> Be careful as this operator can lead to concurrency problems with non thread-safe objects such as CDI request-scoped beans.
> It might also break reactive-streams semantics with items being emitted concurrently.
