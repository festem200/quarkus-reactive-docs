# Joining several unis

> **Documentacion oficial:** <https://smallrye.io/smallrye-mutiny/latest/guides/joining-unis>  
> **Fuente:** `documentation/docs/guides/joining-unis.md` en [smallrye/smallrye-mutiny@3.3.0](https://github.com/smallrye/smallrye-mutiny/blob/3.3.0/documentation/docs/guides/joining-unis.md)  
> **Version documentada:** Mutiny 3.3.0 · **Sincronizado:** 2026-08-17 · **Licencia:** Apache-2.0

A `Uni` represents an operation that either emits a value or a failure.
Examples of operations that fit into a `Uni` include: HTTP client requests, database `insert` queries, sending messages to a broker, etc.

It is common to trigger several _concurrent_ operations, then _join_ on the results.
For instance you can make HTTP requests to 3 different HTTP APIs, then collect all HTTP responses.
Or you can just take the response from the one who was the fastest.

`Uni` offers the `join` group to assemble all results from a list of `Uni`, pick the first one that terminates, or pick the first one that terminates with a value.

## Joining multiple unis

Given multiple `Uni`, you can join them all and obtain a `Uni` that emits a list of values:

```java
Uni<Integer> a = Uni.createFrom().item(1);
Uni<Integer> b = Uni.createFrom().item(2);
Uni<Integer> c = Uni.createFrom().item(3);

Uni<List<Integer>> res = Uni.join().all(a, b, c).andCollectFailures();
```

The assembled values are in the same order as the list of unis.
The last call to `.andCollectFailures()` specifies that if one or several `Uni` fail, then the failures are assembled in a `CompositeException`.

Sometimes you just want to _fail fast_ if any of the `Uni` fails, and not wait for all unis to terminate:

```java
res = Uni.join().all(a, b, c).andFailFast();
```

When any `Uni` fails, then the failure is directly forwarded as a failure of `res`.

## Joining on the first Uni

In some cases you do not want to have all the results but just that of the first `Uni` to respond.
There are actually 2 different cases, depending on whether you want the result of the first `Uni` that emits a value, or just the result of the first `Uni` to terminate.

If you want to get the first `Uni` that terminates:

```java
Uni<Integer> res = Uni.join().first(a, b, c).toTerminate();
```

If you want to have the first `Uni` that emits a value (and forget the first failures), then:

```java
res = Uni.join().first(a, b, c).withItem();
```

When all unis fail then `res` fails with a `CompositeException` that reports all failures.

## Using a builder object

There are situations where it can be more convenient to gather the unis to join in an iterative fashion.
For this purpose you can use a builder object, as in:

```java
UniJoin.Builder<Integer> builder = Uni.join().builder();

while (someCondition) {
    Uni<Integer> uni = supplier.get();
    builder.add(uni);
}

Uni<List<Integer>> all = builder.joinAll().andFailFast();

Uni<Integer> first = builder.joinFirst().withItem();
```

The builder offers `joinAll()` and `joinFirst()` methods.
