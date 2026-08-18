# Uni and Multi

> **Documentacion oficial:** <https://smallrye.io/smallrye-mutiny/latest/reference/uni-and-multi>  
> **Fuente:** `documentation/docs/reference/uni-and-multi.md` en [smallrye/smallrye-mutiny@3.3.0](https://github.com/smallrye/smallrye-mutiny/blob/3.3.0/documentation/docs/reference/uni-and-multi.md)  
> **Version documentada:** Mutiny 3.3.0 · **Sincronizado:** 2026-08-17 · **Licencia:** Apache-2.0

Mutiny defines two _reactive_ types:

* `Multi` - represents streams of _0..*_ items (potentially unbounded)
* `Uni` - represents streams receiving either an item or a failure

> **💡 CONSEJO**
>
> The Mutiny name comes from the contraction of `Multi` and `Uni` names

Both `Uni` and `Multi` are asynchronous types.
They receive and fire events at any time.

You may wonder why we make the distinction between `Uni` and `Multi.`
Conceptually, a `Uni` is a `Multi,` right?

In practice, you don't use `Unis` and `Multis` the same way.
The use cases and operations are different.

* `Uni` does not need the complete ceremony presented above as the _request_ does not make sense.
* The `subscribe` event expresses the interest and triggers the computation, no need for an additional _request_.
* `Uni` can handle items having a `null` value (and has specific methods to handle this case).
* `Multi` does not allow it (because the Reactive Streams specification forbids it).
* Having a `Uni` implementing `Publisher` would be a bit like having `Optional` implementing `Iterable`.

In other words, `Uni`:

* can receive at most 1 `item` event, or a `failure` event
* cannot receive a `completion` event (`null` in the case of 0 items)
* cannot receive a `request` event

The following snippet shows how you can use `Uni` and `Multi`:

```java
Multi.createFrom().items("a", "b", "c")
  .onItem().transform(String::toUpperCase)
  .subscribe().with(
    item -> System.out.println("Received: " + item),
    failure -> System.out.println("Failed with " + failure)
);

Uni.createFrom().item("a")
  .onItem().transform(String::toUpperCase)
  .subscribe().with(
    item -> System.out.println("Received: " + item),
    failure -> System.out.println("Failed with " + failure)
);
```
