# Merging and Concatenating Streams

> **Documentacion oficial:** <https://smallrye.io/smallrye-mutiny/latest/guides/merging-and-concatenating-streams>  
> **Fuente:** `documentation/docs/guides/merging-and-concatenating-streams.md` en [smallrye/smallrye-mutiny@3.3.0](https://github.com/smallrye/smallrye-mutiny/blob/3.3.0/documentation/docs/guides/merging-and-concatenating-streams.md)  
> **Version documentada:** Mutiny 3.3.0 · **Sincronizado:** 2026-08-17 · **Licencia:** Apache-2.0

Merging or concatenating streams is a frequent operation which consists in taking multiple streams and creating a new `Multi` out of them.
Such an operation observes the items emitted by the different streams and produces a new `Multi` emitting the events.

All the streams merged or concatenated this way should emit the same type of items.

## The difference between merge and concatenate

Understanding the difference between _merge_ and _concatenate_ is essential.

When _merging_ streams, it observes the different upstreams and emits the items as they come.
If the streams emit their items concurrently, the items from the different streams are interleaved.

```mermaid
sequenceDiagram
    autonumber
    participant A as Stream A
    participant B as Stream B
    participant M as Merged stream
    
    M-->>A: subscribe
    M-->>B: subscribe    
    A-->>M: onSubscribe(s)
    
    A->>M: onItem(1)
    
    B-->>M: onSubscribe(s)

    A->>M: onItem(2)
    B->>M: onItem(a)    
    A->>M: onItem(3)
    B->>M: onItem(b)
    B->>M: onItem(c)
```

When using _merge_, failures are also propagated to the merged stream, and no more items are emitted after that failure.
The _completion_ event is only emitted by the merged stream when all the observed streams are completed.

But if we want to keep the order of the observed stream, we need to _concatenate_.

When _concatenating_, it waits for the first stream to complete before subscribing to the second one. Thus, it ensures that all the items from the first stream have been emitted before emitting the second stream items. It preserves an order corresponding to the source:

```mermaid
sequenceDiagram
    autonumber
    participant A as Stream A
    participant B as Stream B
    participant C as Concatenated stream
    
    C-->>A: subscribe
    A-->>C: onSubscribe(s)

    A->>C: onItem(1)
    A->>C: onItem(2)
    A->>C: onItem(3)
    
    A-->>C: onCompletion()
    
    C-->>B: subscribe
    B-->>C: onSubscribe(s)
    
    B->>C: onItem(a)    
    B->>C: onItem(b)
    B->>C: onItem(c)
```

When the first stream emits the completion event, it switches to the second stream, and so on.
When the last stream completes, the concatenated stream sends the completion event.
As for _merge_, if a stream fails then there won't be further events.

## Merging Multis

To create a new `Multi` from the _merge_ of multiple `Multi` streams use:

```java
Multi<T> multi1 = getFirstMulti();
Multi<T> multi2 = getSecondMulti();

Multi<T> merged = Multi.createBy().merging().streams(multi1, multi2);
```

For example, we can merge multiple streams emitting periodical events:

```java
Multi<String> first = Multi.createFrom().ticks().every(Duration.ofMillis(10))
        .onItem().transform(l -> "Stream 1 - " + l);

Multi<String> second = Multi.createFrom().ticks().every(Duration.ofMillis(15))
        .onItem().transform(l -> "Stream 2 - " + l);

Multi<String> third = Multi.createFrom().ticks().every(Duration.ofMillis(5))
        .onItem().transform(l -> "Stream 3 - " + l);

Cancellable cancellable = Multi.createBy().merging().streams(first, second, third)
        .subscribe().with(s -> System.out.println("Got item: " + s));
```

and the output would be similar to:

```text
Got item: Stream 1 - 0
Got item: Stream 2 - 0
Got item: Stream 3 - 0
Got item: Stream 3 - 1
Got item: Stream 1 - 1
Got item: Stream 3 - 2
Got item: Stream 2 - 1
Got item: Stream 3 - 3
Got item: Stream 1 - 2
Got item: Stream 3 - 4
Got item: Stream 3 - 5
```

## Concatenating Multis

To create a new `Multi` from the _concatenation_ of multiple `Multi` streams use:

```java
Multi<T> multi1 = getFirstMulti();
Multi<T> multi2 = getSecondMulti();

Multi<T> concatenated = Multi.createBy().concatenating().streams(multi1, multi2);
```

Don't forget that the streams order matters in this case, as `(streamA, streamB)` does not provide the same result as `(streamB, streamA)`:

```java
Multi<String> first = Multi.createFrom().items("A1", "A2", "A3");
Multi<String> second = Multi.createFrom().items("B1", "B2", "B3");

Multi.createBy().concatenating().streams(first, second)
        .subscribe().with(item -> System.out.print(item)); // "A1A2A3B1B2B3"

Multi.createBy().concatenating().streams(second, first)
        .subscribe().with(item -> System.out.print(item)); // "B1B2B3A1A2A3"
```

> **❗ IMPORTANTE**
>
> If one of the concatenated streams is unbounded (infinite), the next streams in the list won't be consumed!
>
