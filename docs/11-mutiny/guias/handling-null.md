# How to handle null?

> **Documentacion oficial:** <https://smallrye.io/smallrye-mutiny/latest/guides/handling-null>  
> **Fuente:** `documentation/docs/guides/handling-null.md` en [smallrye/smallrye-mutiny@3.3.0](https://github.com/smallrye/smallrye-mutiny/blob/3.3.0/documentation/docs/guides/handling-null.md)  
> **Version documentada:** Mutiny 3.3.0 · **Sincronizado:** 2026-08-17 · **Licencia:** Apache-2.0

The `Uni` type can emit `null` as item.

While there are mixed feelings about `null`, it's part of the Java language and so handled in the `Uni` type.

> **❗ IMPORTANTE**
>
> `Multi` does not support `null` items as it would break the compatibility with the _Reactive Streams_ protocol.

Emitting `null` is convenient when returning `Uni<Void>`.
However, the downstream must expect `null` as item.

Thus, `Uni` provides specific methods to handle `null` item.
`uni.onItem().ifNull()` lets you decide what you want to do when the received item is `null`:

```java
uni.onItem().ifNull().continueWith("hello");
uni.onItem().ifNull().switchTo(() -> Uni.createFrom().item("hello"));
uni.onItem().ifNull().failWith(() -> new Exception("Boom!"));
```

A symmetric group of methods is also available with `ifNotNull` which let you handle the case where the item is _not null_:

```java
uni
    .onItem().ifNotNull().transform(String::toUpperCase)
    .onItem().ifNull().continueWith("yolo!");
```

> **❗ IMPORTANTE**
>
> While supported, emitting `null` should be avoided except for `Uni<Void>`.
