# How can I write unit / integration tests?

> **Documentacion oficial:** <https://smallrye.io/smallrye-mutiny/latest/guides/testing>  
> **Fuente:** `documentation/docs/guides/testing.md` en [smallrye/smallrye-mutiny@3.3.0](https://github.com/smallrye/smallrye-mutiny/blob/3.3.0/documentation/docs/guides/testing.md)  
> **Version documentada:** Mutiny 3.3.0 · **Sincronizado:** 2026-08-17 · **Licencia:** Apache-2.0

Mutiny provides subscribers for `Uni` and `Multi` offering helpful assertion methods.
You can use them to test pipelines.

## Testing a Uni

Here is an example to test a `Uni`:

```java
Uni<Integer> uni = Uni.createFrom().item(63);

UniAssertSubscriber<Integer> subscriber = uni
        .subscribe().withSubscriber(UniAssertSubscriber.create());

subscriber
        .awaitItem()
        .assertItem(63);
```

You can also use predicate-based assertions and item inspection:

```java
Uni<Integer> uni = Uni.createFrom().item(63);

UniAssertSubscriber<Integer> subscriber = uni
        .subscribe().withSubscriber(UniAssertSubscriber.create());

subscriber
        .awaitItem()
        .assertItem(i -> i > 0, "positive number")
        .inspectItem(item -> {
            // use any assertion library here
            assert item == 63;
        });
```

## Testing a Multi

Testing a `Multi` pipeline is similar:

```java
Multi<Integer> multi = Multi.createFrom().range(1, 5)
        .onItem().transform(n -> n * 10);

AssertSubscriber<Integer> subscriber = multi.subscribe().withSubscriber(AssertSubscriber.create(10));

subscriber
        .awaitCompletion()
        .assertItems(10, 20, 30, 40);
```

Predicate-based assertions work on `Multi` too:

```java
Multi<Integer> multi = Multi.createFrom().range(1, 5)
        .onItem().transform(n -> n * 10);

AssertSubscriber<Integer> subscriber = multi
        .subscribe().withSubscriber(AssertSubscriber.create(10));

subscriber
        .awaitCompletion()
        .assertLastItem(i -> i == 40, "last item is 40")
        .assertItemCount(4)
        .inspectItems(items -> {
            // use any assertion library here
            assert items.size() == 4;
        });
```

## Declarative verification with AssertMulti

For multi-item streams, `AssertMulti` provides a declarative step-by-step verifier.
Build a sequence of expectations, then call `verify()`:

```java
Multi<Integer> multi = Multi.createFrom().range(1, 6);

AssertMulti.create(multi)
        .expectNext(1, 2, 3)
        .expectNextMatches(i -> i > 3, "greater than 3")
        .expectNext(5)
        .expectComplete()
        .verify();
```

You can control demand explicitly for backpressure testing:

```java
Multi<Integer> multi = Multi.createFrom().range(1, 4);

AssertMulti.create(multi)
        .thenRequest(10)
        .expectNext(1, 2, 3)
        .expectComplete()
        .verify();
```

## Testing failures

The assertions do not just focus on _good_ outcomes, you can also test failures as in:

```java
Multi<Object> multi = Multi.createFrom().failure(() -> new IOException("Boom"));

AssertSubscriber<Object> subscriber = multi
        .subscribe().withSubscriber(AssertSubscriber.create(10));

subscriber
        .awaitFailure()
        .assertFailedWith(IOException.class, "Boom");
```

With `AssertMulti`:

```java
Multi<Object> multi = Multi.createFrom().failure(new IOException("boom"));

AssertMulti.create(multi)
        .expectFailure(IOException.class, "boom")
        .verify();
```
