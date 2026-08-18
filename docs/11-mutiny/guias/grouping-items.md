# Grouping items from Multi

> **Documentacion oficial:** <https://smallrye.io/smallrye-mutiny/latest/guides/grouping-items>  
> **Fuente:** `documentation/docs/guides/grouping-items.md` en [smallrye/smallrye-mutiny@3.3.0](https://github.com/smallrye/smallrye-mutiny/blob/3.3.0/documentation/docs/guides/grouping-items.md)  
> **Version documentada:** Mutiny 3.3.0 · **Sincronizado:** 2026-08-17 · **Licencia:** Apache-2.0

Mutiny provides several operators to group items from a `Multi` stream. 
You can group items by a key function (similar to SQL's `GROUP BY`), split items into fixed-size chunks, or create time-based windows.

The grouping operators are available from the `group()` method on `Multi`.

## Grouping into Lists

The `group().intoLists()` operator allows you to collect items into lists based on size or time.

### Fixed-size lists

Use `group().intoLists().of(size)` to create fixed-size lists from the stream:

```java
Multi<List<Integer>> grouped = Multi.createFrom().range(0, 10)
        .group().intoLists().of(3);  // Group every 3 items into a list

List<List<Integer>> lists = grouped
        .collect().asList()
        .await().indefinitely();

assertThat(lists).containsExactly(
        List.of(0, 1, 2),
        List.of(3, 4, 5),
        List.of(6, 7, 8),
        List.of(9)
);
```

The last list may contain fewer items if the stream doesn't divide evenly.

### Time-based lists

You can create time-based lists using `group().intoLists().every(Duration)`:

```java
Multi<List<Long>> timeWindows = Multi.createFrom()
        .ticks().every(Duration.ofMillis(10))
        .group().intoLists().every(Duration.ofMillis(100));

// Each list contains items emitted within a 100ms window
```

### Size and time-based lists

You can combine both size and time constraints using `group().intoLists().of(size, Duration)`:

```java
Multi<List<Long>> combined = Multi.createFrom()
        .ticks().every(Duration.ofMillis(10))
        .group().intoLists().of(5, Duration.ofMillis(100));

// Emits a list when either 5 items are collected OR 100ms expires,
// whichever happens first
```

This will emit a list when either the size limit is reached or the duration expires, whichever comes first.

## Grouping into Multi Streams

The `group().intoMultis()` operator allows you to create separate `Multi` streams from your data. Unlike `intoLists()` which materializes all items into memory, `intoMultis()` keeps items as streams, which is better for:

- Applying stream transformations to each group
- Processing large groups without loading everything into memory
- Composing with other reactive operators

### Fixed-size Multi streams

Use `group().intoMultis().of(size)` to create `Multi` streams of a fixed size:

```java
Multi<Multi<Integer>> grouped = Multi.createFrom().range(0, 7)
        .group().intoMultis().of(2);  // Group every 2 items into a Multi

// Process each Multi independently - for example, join each group
Multi<String> sums = grouped
        .onItem().transformToUniAndConcatenate(multi ->
                multi.collect().asList()
                        .onItem().transform(couple -> couple.stream()
                                .map(Objects::toString)
                                .collect(Collectors.joining("-"))));

List<String> results = sums.collect().asList().await().indefinitely();
assertThat(results).containsExactly("0-1", "2-3", "4-5", "6");
```

### Time-based Multi streams

You can create time-based windows using `group().intoMultis().every(Duration)`:

```java
Multi<Multi<Long>> timeWindows = Multi.createFrom()
        .ticks().every(Duration.ofMillis(10))
        .group().intoMultis().every(Duration.ofMillis(100));

// Each Multi contains items emitted within a 100ms window
```

## Grouping by a key function

The `group().by()` operator groups items based on a key function, emitting a `Multi<GroupedMulti<K, V>>` where each `GroupedMulti` represents a group of items sharing the same key.

```java
Multi<GroupedMulti<Integer, Integer>> groups = Multi.createFrom().range(1, 10)
        .group().by(i -> i % 3); // Group by modulo 3

// Process each group separately
Uni<List<String>> result = groups
        .onItem().transformToUniAndConcatenate(group ->
                group.onItem().transform(Objects::toString)
                        .collect().asList()
                        .onItem().transform(l -> group.key() + "(" + String.join(",", l) + ")"))
        .collect().asList();

List<String> lists = result.await().indefinitely();
assertThat(lists).containsExactly("1(1,4,7)", "2(2,5,8)", "0(3,6,9)");
```

Each `GroupedMulti` has a `key()` method that returns the key for that group.
Items are distributed to groups based on the key function result.

### Using both key and value mappers

You can transform items while grouping them by providing both a key mapper and a value mapper:

```java
Multi<GroupedMulti<Boolean, String>> groups = Multi.createFrom().range(1, 10)
        .group().by(
                i -> i % 2 == 0,           // Key: true for even, false for odd
                i -> "Number: " + i        // Value: transform to string
        );

Uni<List<List<String>>> result = groups
        .onItem().transformToUniAndMerge(group ->
                group.collect().asList()
        )
        .collect().asList();

List<List<String>> lists = result.await().indefinitely();
assertThat(lists).hasSize(2);
```

## Processing groups with merge vs concatenate

When processing groups, you need to decide how to combine the results back into a single stream. Similar to [transforming items asynchronously](../tutoriales/transforming-items-asynchronously.md), you can use either **merge** or **concatenate**:

### Using merge

With merge, groups are processed concurrently - items from different groups can interleave in the output stream:

```java
Multi<String> results = Multi.createFrom().range(1, 100)
        .group().by(i -> i % 10)  // Create 10 groups (0-9)
        .onItem().transformToMulti(
                group -> group.onItem().transform(i -> "Group " + group.key() + ": " + i)
        )
        .merge(10);  // Set concurrency to at least the number of groups

List<String> items = results.collect().asList().await().indefinitely();
assertThat(items).hasSize(99);
```

> **Upstream request starvation with merge**
>
> When using `.merge(concurrency)` or similar merge operations after `group().by()`,
> **the concurrency parameter must be greater than or equal to the number of groups that are created but not terminated**.
>
> If you create more groups than the concurrency limit allows, some groups cannot make progress while waiting for others to complete.
> This leads to a **request starvation** where the upstream won't receive requests for emitting new items.

#### Example causing request starvation

```java
// Creating 10 groups but limiting concurrency to only 2
Multi<String> dangerous = Multi.createFrom().ticks().every(Duration.ofMillis(10))
        .group().by(i -> i % 10)  // Creates 10 groups
        .onItem().transformToMulti(
                group -> group.onItem().transform(i -> "Group " + group.key() + ": " + i)
        )
        .merge(2);  // Only 2 groups can be processed concurrently

// This may hang because groups 3-10 cannot make progress
// while waiting for groups 1-2 to complete
AssertSubscriber<String> sub = dangerous.subscribe()
        .withSubscriber(AssertSubscriber.create(Long.MAX_VALUE));

sub.awaitFailure(t -> assertThat(t).isInstanceOf(BackPressureFailure.class));
```

In this example, 10 groups are created but only 2 can be processed concurrently.
Groups 3-10 cannot make progress because the downstream subscriber is busy with groups 1-2.
Meanwhile, groups 1-2 may not complete because they're waiting for backpressure signals from the full pipeline.
The problem is even more exacerbated with infinite streams and infinite groups.

#### How to avoid request starvation

1. **Set concurrency >= number of groups**: If you know the maximum number of groups in advance, set the concurrency parameter to at least that number using `.merge(n)`
2. **Use unbounded concurrency**: Call `.merge(Integer.MAX_VALUE)` to allow unlimited number of concurrent groups
3. **Use concatenate instead**: Process groups sequentially (see below)

### Using concatenate

With concatenate, groups are processed sequentially - each group must fully terminate before the next group can start processing:

```java
// Safe alternative: use concatenate to process groups sequentially
Multi<String> safe = Multi.createFrom().range(1, 100)
        .invoke(i -> System.out.println("emit " + i))
        .group().by(i -> i % 10)
        .onItem().transformToMultiAndConcatenate(
                group -> group.onItem().transform(i -> "Group " + group.key() + ": " + i)
                        .invoke(i -> System.out.println("group " + i))
        );
// Groups are processed one at a time, so no deadlock

List<String> items = safe.collect().asList().await().indefinitely();
assertThat(items).hasSize(99);
```

## Choosing between group().by() and split()

Mutiny provides both `group().by()` and `split()` operators. Here's when to use each:

- **Use `group().by()`** when you don't know the keys in advance and the number of groups is dynamic.
- **Use `split()`** when you know all possible keys upfront (defined by an enum) and you want individual `Multi` instances for each split.

See the [splitting guide](multi-split.md) for more details on `split()`.
