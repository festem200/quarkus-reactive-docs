# Replaying Multis

> **Documentacion oficial:** <https://smallrye.io/smallrye-mutiny/latest/guides/replaying-multis>  
> **Fuente:** `documentation/docs/guides/replaying-multis.md` en [smallrye/smallrye-mutiny@3.3.0](https://github.com/smallrye/smallrye-mutiny/blob/3.3.0/documentation/docs/guides/replaying-multis.md)  
> **Version documentada:** Mutiny 3.3.0 · **Sincronizado:** 2026-08-17 · **Licencia:** Apache-2.0

A `Multi` is a _cold-source_: no processing happens until you subscribe.

While the `broadcast` operator can be used so that multiple subscribers consume a `Multi` events _at the same time_, it does not support replaying items for _late subscribers_: when a subscriber joins after the `Multi` has completed (or failed), then it won't receive any item.

This is where _replaying_ can be useful.

## Replaying all events

Replaying all events from an upstream `Multi` works as follows:

```java
Multi<Integer> upstream = Multi.createFrom().range(0, 10);

Multi<Integer> replay = Multi.createBy().replaying().ofMulti(upstream);

List<Integer> items_1 = replay.collect().asList().await().indefinitely();
List<Integer> items_2 = replay.collect().asList().await().indefinitely();
```

Both `item_1` and `item_2` trigger new subscriptions, and both lists contain the following elements:

```
[0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
```

Replaying works by turning `upstream` into a _hot-stream_, meaning that it gets requested `Long.MAX_VALUE` elements.
This is done when the first subscription happens.

The replay operator stores the items in an internal _replay log_, and then each subscriber gets to replay them.

> **❗ IMPORTANTE**
>
> Subscribers demand and cancellation requests are honored while replaying, but `upstream` cannot be cancelled.
>
> Be careful with unbounded streams as you can exhaust memory!
>
> In such cases or when you need to replay large amounts of data, you might opt to use some eventing middleware rather than Mutiny replays.

## Replaying the last 'n' events

You can limit the number of elements to replay by using the `upTo` method:

```java
Multi<Integer> upstream = Multi.createFrom().range(0, 10);

Multi<Integer> replay = Multi.createBy().replaying().upTo(3).ofMulti(upstream);

List<Integer> items_1 = replay.collect().asList().await().indefinitely();
List<Integer> items_2 = replay.collect().asList().await().indefinitely();
```

Each new subscriber gets to replay the last `n` elements from where the replay log is at subscription time.
For instance the first subscriber can observe all events, while a subscriber that joins 2 seconds later might not observe the earlier events.

Since `Multi.createFrom().range(0, 10)` is an _immediate_ stream, both `item_1` and `item_2` lists contain the last items:

```
[7, 8, 9]
```

## Prepending with seed data

In some cases you might want to prepend some _seed_ data that will be available for replay before the upstream starts emitting.

You can do so using an `Iterable` to provide such seed data:

```java
Multi<Integer> upstream = Multi.createFrom().range(0, 10);
Iterable<Integer> seed = Arrays.asList(-10, -5, -1);

Multi<Integer> replay = Multi.createBy().replaying().ofSeedAndMulti(seed, upstream);

List<Integer> items_1 = replay.collect().asList().await().indefinitely();
List<Integer> items_2 = replay.collect().asList().await().indefinitely();
```

In which case subscribers can observe the following events:

```
[-10, -5, -1, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
```

## Replay of failures and completions

Subscribers get to observe not just items but also the failure and completion events:

```java
Multi<Integer> upstream = Multi.createBy().concatenating().streams(
        Multi.createFrom().range(0, 10),
        Multi.createFrom().failure(() -> new IOException("boom"))
);

Multi<Integer> replay = Multi.createBy().replaying().upTo(3).ofMulti(upstream);

replay.subscribe().with(
        n -> System.out.println(" -> " + n),
        failure -> System.out.println("Failed: " + failure.getMessage()),
        () -> System.out.println("Completed"));
```

Running this code yields the following output for any subscriber:

```
-> 7
-> 8
-> 9
Failed: boom
```
