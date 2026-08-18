# How can I create a Multi from a non-reactive source?

> **Documentacion oficial:** <https://smallrye.io/smallrye-mutiny/latest/guides/integrate-a-non-reactive-source>  
> **Fuente:** `documentation/docs/guides/integrate-a-non-reactive-source.md` en [smallrye/smallrye-mutiny@3.3.0](https://github.com/smallrye/smallrye-mutiny/blob/3.3.0/documentation/docs/guides/integrate-a-non-reactive-source.md)  
> **Version documentada:** Mutiny 3.3.0 · **Sincronizado:** 2026-08-17 · **Licencia:** Apache-2.0

The `UnicastProcessor` is an implementation of `Multi` that lets you enqueue items in a queue.

The items are then dispatched to the subscriber using the request protocol.
While this pattern is against the idea of back-pressure, it lets you connect sources of data that do not support back-pressure with your subscriber.

In the following example, the `UnicastProcessor` is used by a thread emitting items.
These items are enqueued in the processor and replayed when the subscriber is connected, following the request protocol.

```java
UnicastProcessor<String> processor = UnicastProcessor.create();
Multi<String> multi = processor
        .onItem().transform(String::toUpperCase)
        .onFailure().recoverWithItem("d'oh");

// Create a source of items that does not follow the request protocol
new Thread(() -> {
    for (int i = 0; i < 1000; i++) {
        processor.onNext(Integer.toString(i));
    }
    processor.onComplete();
}).start();
```

By default, the `UnicastProcessor` uses an unbounded queue.
You can also pass a fixed size queue that would reject the items once full.
