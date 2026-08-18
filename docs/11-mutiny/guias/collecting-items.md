# Collecting items from Multi

> **Documentacion oficial:** <https://smallrye.io/smallrye-mutiny/latest/guides/collecting-items>  
> **Fuente:** `documentation/docs/guides/collecting-items.md` en [smallrye/smallrye-mutiny@3.3.0](https://github.com/smallrye/smallrye-mutiny/blob/3.3.0/documentation/docs/guides/collecting-items.md)  
> **Version documentada:** Mutiny 3.3.0 · **Sincronizado:** 2026-08-17 · **Licencia:** Apache-2.0

There are cases where you want to accumulate the items from a `Multi` and produce a `Uni` as a final result.
This is also called a _reduction_ in functional programming.

The `Uni` fires its item when the `Multi` completes.
Mutiny provides multiple operators to deal with that scenario.
They are available from the `collect()` group.
For example, you can store the items in a list, emit the list on completion, or use a Java `Collector` to customize the aggregation.

> **🚨 PELIGRO**
>
> Don't collect items from infinite streams or you will likely end with an out-of-memory failure!

## Collecting items into a list

One of the most common approaches to collect items is to store them in a list (`Uni<List<T>>`)
It emits the final list when the `Multi` completes.

```mermaid
sequenceDiagram
    autonumber
    participant M as Multi
    participant O as Collect operator
    participant D as Subscriber
    
    M->>O: onItem(1)
    M->>O: onItem(2)
    M->>O: onItem(3)
    
    O->>D: onItem([1, 2, 3])
```

How to achieve this with Mutiny?

```java
Multi<String> multi = getMulti();
Uni<List<String>> uni = multi.collect().asList();
```

It's important to note that the returned type is a `Uni`.
It emits the list when the multi completes.

## Collecting items into a map

You can also collect the items into a `Map`.
In this case, you need to provide a function to compute the key for each item:

```java
Multi<String> multi = getMulti();
Uni<Map<String, String>> uni =
        multi.collect()
                .asMap(item -> getUniqueKeyForItem(item));
```

If the key mapper function returns the same key for multiple items, the last one with that key is stored in the final `Map`.
You can collect items in a _multimap_ to handle items with the same keys.

## Collecting items into a multimap

A multimap is a `Map<K, List<T>>.`
In the case of a conflicting key, it stores all the items in a list associated with that key.

```java
Multi<String> multi = getMulti();
Uni<Map<String, Collection<String>>> uni =
        multi.collect()
                .asMultiMap(item -> getKeyForItem(item));
```

## Using a custom accumulator

You can also use a custom _accumulator_ function:

```java
Multi<String> multi = getMulti();
Uni<MyCollection> uni = multi.collect()
        .in(MyCollection::new, (col, item) -> col.add(item));
```

The `in` method receives two arguments:

1. a supplier providing the new instance of your collection/container
2. the accumulator function

You can also use a Java `Collector`.
For example, in the next example, count the number of items, and produce the final count as item:

```java
Uni<Long> count = multi.collect()
        .with(Collectors.counting());
```

## Getting the first and last items

While they are not strictly speaking collecting items, `collect().first()` and `collect().last()` allow retrieving the first and last item from a `Multi`:

```java
Uni<String> first = multi.collect().first();
Uni<String> last = multi.collect().last();
```
