# Creating `Multi` pipelines

> **Documentacion oficial:** <https://smallrye.io/smallrye-mutiny/latest/tutorials/creating-multi-pipelines>  
> **Fuente:** `documentation/docs/tutorials/creating-multi-pipelines.md` en [smallrye/smallrye-mutiny@3.3.0](https://github.com/smallrye/smallrye-mutiny/blob/3.3.0/documentation/docs/tutorials/creating-multi-pipelines.md)  
> **Version documentada:** Mutiny 3.3.0 · **Sincronizado:** 2026-08-17 · **Licencia:** Apache-2.0

A `Multi` represents a _stream_ of data.
A stream can emit 0, 1, n, or an infinite number of items.

You will rarely create instances of `Multi` yourself but instead use a reactive client that exposes a Mutiny API.
Still, just like `Uni` there exists a rich API for creating `Multi` objects.

## The Multi type

A `Multi<T>` is a data stream that:

- emits `0..n` item events
- emits a failure event
- emits a completion event for bounded streams

> **⚠️ AVISO**
>
> Failures are terminal events: after having received a failure no further item will be emitted.

`Multi<T>` provides many operators that create, transform, and orchestrate `Multi` sequences.
The operators can be used to define a processing pipeline.
The events flow in this pipeline, and each operator can process or transform the events.

`Multis` are lazy by nature.
To trigger the computation, you must subscribe.

The following snippet provides a simple example of pipeline using `Multi`:

```java
Multi.createFrom().items(1, 2, 3, 4, 5)
        .onItem().transform(i -> i * 2)
        .select().first(3)
        .onFailure().recoverWithItem(0)
        .subscribe().with(System.out::println);
```

## Subscribing to a Multi

Remember, if you don't subscribe, nothing is going to happen.
Also, the pipeline is materialized for each _subscription_.

When subscribing to a `Multi,` you can pass an item callback (invoked when the item is emitted), or pass two callbacks, one receiving the item and one receiving the failure, or three callbacks to handle respectively the item, failure and completion events.

```java
Cancellable cancellable = multi
        .subscribe().with(
                item -> System.out.println(item),
                failure -> System.out.println("Failed with " + failure),
                () -> System.out.println("Completed"));
```

Note the returned `Cancellable`: this object allows canceling the stream if need be.

## Creating Multi from items

There are many ways to create `Multi` instances.
See `Multi.createFrom()` to see all the possibilities.

For instance, you can create a `Multi` from known items or from an `Iterable`:

```java
Multi<Integer> multiFromItems = Multi.createFrom().items(1, 2, 3, 4);
Multi<Integer> multiFromIterable = Multi.createFrom().iterable(Arrays.asList(1, 2, 3, 4, 5));
```

Every subscriber receives the same set of items (`1`, `2`... `5`) just after the subscription.

You can also use `Suppliers`:

```java
AtomicInteger counter = new AtomicInteger();
Multi<Integer> multi = Multi.createFrom().items(() ->
        IntStream.range(counter.getAndIncrement(), counter.get() * 2).boxed());
```

The `Supplier` is called for every subscriber, so each of them will get different values.

> **💡 CONSEJO**
>
> You can create ranges using `Multi.createFrom().range(start, end)`.

## Creating failing Multis

Streams can also fail.

Failures are used to indicate to the downstream subscribers that the source encountered a terrible error and cannot continue emitting items.
Create failed `Multi` instances with:

```java
// Pass an exception directly:
Multi<Integer> failed1 = Multi.createFrom().failure(new Exception("boom"));

// Pass a supplier called for every subscriber:
Multi<Integer> failed2 = Multi.createFrom().failure(() -> new Exception("boom"));
```

## Creating empty Multis

Unlike `Uni,` `Multi` streams don't send `null` items (this is forbidden in _reactive streams_).

Instead `Multi` streams send completion events indicating that there are no more items to consume.
Of course, the completion event can happen even if there are no items, creating an empty stream.

You can create such a stream using:

```java
Multi<String> multi = Multi.createFrom().empty();
```

## Creating Multis using an emitter (_advanced_)

You can create a `Multi` using an emitter.
This approach is useful when integrating callback-based APIs:

```java
Multi<Integer> multi = Multi.createFrom().emitter(em -> {
    em.emit(1);
    em.emit(2);
    em.emit(3);
    em.complete();
});
```

The emitter can also send a failure.
It can also get notified of cancellation to, for example, stop the work in progress.

## Creating Multis from _ticks_ (_advanced_)

You can create a stream that emit a _ticks_ periodically:

```java
Multi<Long> ticks = Multi.createFrom().ticks().every(Duration.ofMillis(100));
```

The downstream receives a `long,` which is a counter.
For the first tick, it's 0, then 1, then 2, and so on.

## Creating Multis from a generator (_advanced_)

You can create a stream from some _initial state_, and a _generator function_:

```java
Multi<Object> sequence = Multi.createFrom().generator(() -> 1, (n, emitter) -> {
    int next = n + (n / 2) + 1;
    if (n < 50) {
        emitter.emit(next);

    } else {
        emitter.complete();
    }
    return next;
});
```

The initial state is given through a supplier (here `() -> 1`).
The generator function accepts 2 arguments:

- the current state,
- an emitter that can emit a new item, emit a failure, or emit a completion.

The generator function return value is the next _current state_.
Running the previous example gives the following number suite: `{2, 4, 7, 11, 17, 26, 40, 61}`.
