# From imperative to reactive

> **Documentacion oficial:** <https://smallrye.io/smallrye-mutiny/latest/guides/imperative-to-reactive>  
> **Fuente:** `documentation/docs/guides/imperative-to-reactive.md` en [smallrye/smallrye-mutiny@3.3.0](https://github.com/smallrye/smallrye-mutiny/blob/3.3.0/documentation/docs/guides/imperative-to-reactive.md)  
> **Version documentada:** Mutiny 3.3.0 · **Sincronizado:** 2026-08-17 · **Licencia:** Apache-2.0

If you use Mutiny, there is a good chance you may want to avoid blocking the caller thread.

In a _pure_ reactive application, the application logic is executed on one of the few I/O threads, and blocking one of these would have dramatic consequences.
So, here is the big question: _how do you deal with blocking code?_

Let's imagine you have blocking code (e.g., connecting to a database using JDBC, reading a file from the file system...), and you want to integrate that into your reactive pipelines while avoiding blocking.
You would need to isolate such blocking parts of your code and run these parts on worker threads.

Mutiny provides two operators to customize the threads used to handle events:

* `runSubscriptionOn` - to configure the thread used to execute the code happening at subscription-time
* `emitOn` - to configure the thread used to dispatch events downstream

## Running blocking code on subscription

It is very usual to deal with the blocking call during the subscription.
In this case, the `runSubscription` operator is what you need:

```java
Uni<String> uni = Uni.createFrom()
        .item(this::invokeRemoteServiceUsingBlockingIO)
        .runSubscriptionOn(Infrastructure.getDefaultWorkerPool());
```

The code above creates a Uni that will supply the item using a blocking call, here the `invokeRemoteServiceUsingBlockingIO` method.
To avoid blocking the subscriber thread, it uses `runSubscriptionOn` which switches the thread and call `invokeRemoteServiceUsingBlockingIO` on another thread.
Here we pass the default worker thread pool, but you can use your own executor.

> **💡 CONSEJO**
>
> What's that default worker pool?
>
> In the previous snippet, you may wonder about `Infrastructure.getDefaultWorkerPool()`.
> Mutiny allows the underlying platform to provide a default worker pool.
> `Infrastructure.getDefaultWorkerPool()` provides access to this pool.

If the underlying platform does not provide a pool, a default one is used.

Note that `runSubscriptionOn` does not subscribe to the Uni.
It specifies the executor to use when a subscription happens.

While the snippet above uses `Uni`, you can also use `runSubscriptionOn` on a `Multi`.

## Executing blocking calls on event

Using `runSubscriptionOn` works when the blocking operation happens at subscription time.
But, when dealing with `Multi` and need to execute blocking operations for each item, you need to use `emitOn`.

While `runSubscriptionOn` runs the subscription on the given executor, `emitOn` configures the executor used to propagate downstream the items, failure and completion events:

```java
Multi<String> multi = Multi.createFrom().items("john", "jack", "sue")
        .emitOn(Infrastructure.getDefaultWorkerPool())
        .onItem().transform(this::invokeRemoteServiceUsingBlockingIO);
```

`emitOn` is also available on `Uni`.

> **⚠️ AVISO**
>
> Be careful as this operator can lead to concurrency problems with non thread-safe objects such as CDI request-scoped beans.
> It might also break reactive-streams semantics with items being emitted concurrently.
>
