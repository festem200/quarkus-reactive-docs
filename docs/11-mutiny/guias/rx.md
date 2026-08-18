# Using map, flatMap and concatMap

> **Documentacion oficial:** <https://smallrye.io/smallrye-mutiny/latest/guides/rx>  
> **Fuente:** `documentation/docs/guides/rx.md` en [smallrye/smallrye-mutiny@3.3.0](https://github.com/smallrye/smallrye-mutiny/blob/3.3.0/documentation/docs/guides/rx.md)  
> **Version documentada:** Mutiny 3.3.0 · **Sincronizado:** 2026-08-17 · **Licencia:** Apache-2.0

If you are a seasoned reactive developer, you may miss the `map`, `flatMap`, `concatMap` methods.

The Mutiny API is quite different from the _standard_ reactive eXtensions API.

There are multiple reasons for this choice.
Typically, _flatMap_ is not necessarily well understood by every developer, leading to potentially catastrophic consequences.

That being said, Mutiny provides the _map_, _flatMap_ and _concatMap_ methods, implementing the most common variant for each:

```java
int result = uni
        .map(i -> i + 1)
        .await().indefinitely();

int result2 = uni
        .flatMap(i -> Uni.createFrom().item(i + 1))
        .await().indefinitely();

List<Integer> list = multi
        .map(i -> i + 1)
        .collect().asList()
        .await().indefinitely();

List<Integer> list2 = multi
        .flatMap(i -> Multi.createFrom().items(i, i))
        .collect().asList()
        .await().indefinitely();

List<Integer> list3 = multi
        .concatMap(i -> Multi.createFrom().items(i, i))
        .collect().asList()
        .await().indefinitely();
```

The Mutiny equivalents are:

* `map -> onItem().transform()`
* `flatMap -> onItem().transformToUniAndMerge` and `onItem().transformToMultiAndMerge`
* `concatMap -> onItem().transformToUniAndConcatenate` and `onItem().transformToMultiAndConcatenate`

The following snippet demonstrates how to uses these methods:

```java
int result = uni
        .onItem().transform(i -> i + 1)
        .await().indefinitely();

int result2 = uni
        .onItem().transformToUni(i -> Uni.createFrom().item(i + 1))
        .await().indefinitely();

// Shortcut for .onItem().transformToUni
int result3 = uni
        .chain(i -> Uni.createFrom().item(i + 1))
        .await().indefinitely();

List<Integer> list = multi
        .onItem().transform(i -> i + 1)
        .collect().asList()
        .await().indefinitely();

List<Integer> list2 = multi
        .onItem().transformToMultiAndMerge(i -> Multi.createFrom().items(i, i))
        .collect().asList()
        .await().indefinitely();

// Equivalent to transformToMultiAndMerge but let you configure the flattening process,
// failure management, concurrency...
List<Integer> list3 = multi
        .onItem().transformToMulti(i -> Multi.createFrom().items(i, i)).merge()
        .collect().asList()
        .await().indefinitely();

List<Integer> list4 = multi
        .onItem().transformToMultiAndConcatenate(i -> Multi.createFrom().items(i, i))
        .collect().asList()
        .await().indefinitely();

// Equivalent to transformToMultiAndConcatenate but let you configure the flattening process,
// failure management...
List<Integer> list5 = multi
        .onItem().transformToMulti(i -> Multi.createFrom().items(i, i)).concatenate()
        .collect().asList()
        .await().indefinitely();
```
