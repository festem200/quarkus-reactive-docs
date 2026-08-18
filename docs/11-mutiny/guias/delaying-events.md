# How to delay events?

> **Documentacion oficial:** <https://smallrye.io/smallrye-mutiny/latest/guides/delaying-events>  
> **Fuente:** `documentation/docs/guides/delaying-events.md` en [smallrye/smallrye-mutiny@3.3.0](https://github.com/smallrye/smallrye-mutiny/blob/3.3.0/documentation/docs/guides/delaying-events.md)  
> **Version documentada:** Mutiny 3.3.0 · **Sincronizado:** 2026-08-17 · **Licencia:** Apache-2.0

## Delaying Uni's item

When you have a `Uni`, you can delay the item emission using `onItem().delayIt().by(...)`:

```java
Uni<String> delayed = Uni.createFrom().item("hello")
        .onItem().delayIt().by(Duration.ofMillis(10));
```

You pass a duration.
When the item is received, it _waits for_  that duration before propagating it to the downstream consumer.

You can also delay the item's emission based on another _companion_ `Uni`:

```java
Uni<String> delayed = Uni.createFrom().item("hello")
        // The write method returns a Uni completed
        // when the operation is done.
        .onItem().delayIt().until(this::write);
```

The item is propagated downstream when the `Uni` returned by the function emits an item (possibly `null`).
If the function emits a failure (or throws an exception), this failure is propagated downstream.

## Throttling a Multi

Multi does not have a _delayIt_ operator because applying the same delay to all items is rarely what you want to do.
However, there are several ways to apply a delay in a `Multi`.

First, you can use the `onItem().call()`, which delays the emission until the `Uni` produced the `call` emits an item.
For example, the following snippet delays all the items by 10 ms:

```java
Multi<Integer> delayed = multi
    .onItem().call(i ->
        // Delay the emission until the returned uni emits its item
        Uni.createFrom().nullItem().onItem().delayIt().by(Duration.ofMillis(10))
    );
```

In general, you don't want to apply the same delay to all the items.
You can combine `call` with a random delay as follows:

```java
Random random = new Random();
Multi<Integer> delayed = Multi.createFrom().items(1, 2, 3, 4, 5)
        .onItem().call(i -> {
            Duration delay = Duration.ofMillis(random.nextInt(100) + 1);
            return Uni.createFrom().nullItem().onItem().delayIt().by(delay);
        });
```

Finally, you may want to throttle the items.
For example, you can introduce a (minimum) one-second delay between each item.
To achieve this, combine `Multi.createFrom().ticks()` and the multi to throttled:

```java
// Introduce a one second delay between each item
Multi<Long> ticks = Multi.createFrom().ticks().every(Duration.ofSeconds(1))
        .onOverflow().drop();
Multi<Integer> delayed = Multi.createBy().combining().streams(ticks, multi)
        .using((x, item) -> item);
```

> **💡 CONSEJO**
>
> The `onOverflow().drop()` is used to avoid the _ticks_ to fail if the other stream (`multi`) is too slow.

## Delaying other types of events

We have looked at how to delay items, but you may need to delay other events, such as subscription or failure.
For these, use the `call` approach, and return a `Uni` that delay the event's propagation.
