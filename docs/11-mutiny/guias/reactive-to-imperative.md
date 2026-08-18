# From reactive to imperative

> **Documentacion oficial:** <https://smallrye.io/smallrye-mutiny/latest/guides/reactive-to-imperative>  
> **Fuente:** `documentation/docs/guides/reactive-to-imperative.md` en [smallrye/smallrye-mutiny@3.3.0](https://github.com/smallrye/smallrye-mutiny/blob/3.3.0/documentation/docs/guides/reactive-to-imperative.md)  
> **Version documentada:** Mutiny 3.3.0 · **Sincronizado:** 2026-08-17 · **Licencia:** Apache-2.0

There are use cases where you need the items in an imperative manner instead of asynchronous.
Typically, when you serve an HTTP request from a worker thread, you can block.

Mutiny provides the ability to block until you get the items.

## Awaiting on Uni's item

When dealing with a `Uni,` you can block and await the item using:

```java
T t = uni.await().indefinitely();
```

This method blocks the caller thread until the observed `uni` emits the item.
Note that the returned item can be `null` if the `uni` emits `null.`
If the `uni` fails, it throws the exception, wrapped in the `CompletionException` for _checked_ exception.

Blocking forever may not be a great idea.
You can use `uni.await().atMost(Duration)` to pass a deadline.
When the deadline is reached, a `TimeoutException` is thrown:

```java
T t = uni.await().atMost(Duration.ofSeconds(1));
```

## Iterating over Multi's items

When dealing with a `Multi,` you may want to iterate over the items using a simple "foreach."
You can achieve this using `multi.subscribe().asIterable()`:

```java
Iterable<T> iterable = multi.subscribe().asIterable();
for (T item : iterable) {
    doSomethingWithItem(item);
}
```

The returned `iterable` is blocking.
It waits for the next items, and during that time, blocks the caller thread.

The iteration ends once the last item is consumed.
If the `multi` emits a failure, an exception is thrown.

Similar to `asIterable()`, the `asStream` method lets you retrieve a `java.util.stream.Stream`:

```java
Stream<T> stream = multi.subscribe().asStream();
stream.forEach(this::doSomethingWithItem);
```
