# How to use polling?

> **Documentacion oficial:** <https://smallrye.io/smallrye-mutiny/latest/guides/polling>  
> **Fuente:** `documentation/docs/guides/polling.md` en [smallrye/smallrye-mutiny@3.3.0](https://github.com/smallrye/smallrye-mutiny/blob/3.3.0/documentation/docs/guides/polling.md)  
> **Version documentada:** Mutiny 3.3.0 · **Sincronizado:** 2026-08-17 · **Licencia:** Apache-2.0

There are many poll-based API around us.
Sometimes you need to use these APIs to generate a stream from the polled values.

To do this, use the `repeat()` feature:

```java
PollableDataSource source = new PollableDataSource();
// First creates a uni that emit the polled item.
// Because `poll` blocks, let's use a specific executor
Uni<String> pollItemFromSource = Uni.createFrom().item(source::poll)
        .runSubscriptionOn(executor);
// To get the stream of items, just repeat the uni indefinitely
Multi<String> stream = pollItemFromSource.repeat().indefinitely();

Cancellable cancellable = stream.subscribe().with(item -> System.out.println("Polled item: " + item));
```

You can also stop the repetition using the `repeat().until()` method which will continue the repetition until the given predicate returns `true`, and/or directly create a `Multi` using `Multi.createBy().repeating()`:

```java
PollableDataSource source = new PollableDataSource();
Multi<String> stream = Multi.createBy().repeating()
            .supplier(source::poll)
            .until(s -> s == null)
        .runSubscriptionOn(executor);

stream.subscribe().with(item -> System.out.println("Polled item: " + item));
```
