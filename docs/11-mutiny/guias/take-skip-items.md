# Take/Skip the first or last items

> **Documentacion oficial:** <https://smallrye.io/smallrye-mutiny/latest/guides/take-skip-items>  
> **Fuente:** `documentation/docs/guides/take-skip-items.md` en [smallrye/smallrye-mutiny@3.3.0](https://github.com/smallrye/smallrye-mutiny/blob/3.3.0/documentation/docs/guides/take-skip-items.md)  
> **Version documentada:** Mutiny 3.3.0 · **Sincronizado:** 2026-08-17 · **Licencia:** Apache-2.0

Multi provides the ability to:

- only forward items from the beginning of the observed multi,
- only forward the last items (and discard all the other ones),
- skip items from the beginning of the multi,
- skip the last items.

These actions are available from the `multi.select()` and `multi.skip()` groups, allowing to, respectively, select and skip
items from upstream.

## Selecting items

The `multi.select().first` method forwards on the _n_ **first** items from the multi.
It forwards that amount of items and then sends the completion signal.
It also cancels the upstream subscription.

```java
Multi<Integer> firstThreeItems = multi.select().first(3);
```

> **📌 NOTA**
>
> The `select().first()` method selects only the first item.

If the observed multi emits fewer items, it sends the completion event when the upstream completes.

Similarly, The `multi.select().last` operator forwards on the _n_  **last** items from the multi.
It discards all the items emitted beforehand.

```java
Multi<Integer> lastThreeItems = multi.select().last(3);
```

> **📌 NOTA**
>
> The `select().last()` method selects only the last item.

The `multi.select().first(Predicate)` operator forwards the items while the passed predicate returns `true`:

```java
Multi<Integer> takeWhile = multi.select().first(i -> i < 4);
```

It calls the predicate for each item.
Once the predicate returns `false`, it stops forwarding the items downstream.
It also sends the completion event and cancels the upstream subscription.

Finally,  `multi.select().first(Duration)` operator picks the first items emitted during a given period.
Once the passed duration expires, it sends the completion event and cancels the upstream subscription.
If the observed multi completes before the passed duration, it sends the completion event.

```java
Multi<Integer> takeForDuration = multi.select().first(Duration.ofSeconds(1));
```

## Skipping items

You can also skip items using `multi.skip()`.

The `multi.skip().first(n)` method skips the _n_ **first** items from the multi.
It forwards all the remaining items and sends the completion event when the upstream multi completes.

```java
Multi<Integer> skipThreeItems = multi.skip().first(3);
```

If the observed multi emits fewer items, it sends the completion event without emitting any items.

> **📌 NOTA**
>
> `skip().last()` drops only the very last item.

Similarly, The `multi.skip().last(n)` operator skips on the _n_  **last** items from the multi:

```java
Multi<Integer>  skipLastThreeItems = multi.skip().last(3);
```

The `multi.skip().first(Predicate)` operator skips the items while the passed predicate returns `true`:

```java
Multi<Integer> skipWhile = multi.skip().first(i -> i < 4);
```

It calls the predicate for each item.
Once the predicate returns `false`, it stops discarding the items and starts forwarding downstream.

Finally,  `multi.skip().first(Duration)` operator skips the first items for a given period.
Once the passed duration expires, it sends the items emitted after the deadline downstream.
If the observed multi completes before the passed duration, it sends the completion event.

```java
Multi<Integer> skipForDuration = multi.skip().first(Duration.ofSeconds(1));
```
