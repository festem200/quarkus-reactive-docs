# Filtering items from Multi

> **Documentacion oficial:** <https://smallrye.io/smallrye-mutiny/latest/guides/filtering-items>  
> **Fuente:** `documentation/docs/guides/filtering-items.md` en [smallrye/smallrye-mutiny@3.3.0](https://github.com/smallrye/smallrye-mutiny/blob/3.3.0/documentation/docs/guides/filtering-items.md)  
> **Version documentada:** Mutiny 3.3.0 · **Sincronizado:** 2026-08-17 · **Licencia:** Apache-2.0

When observing a `Multi`, you may not want to forward all the received items to the downstream.

Use the `multi.select()` group to select items.

```java
List<Integer> list = multi
        .select().where(i -> i > 6)
        .collect().asList()
        .await().indefinitely();
```

To _select_ items passing a given predicate, use `multi.select().where(predicate)`:

`where` accepts a predicate called for each item.
If the predicate returns `true`, the item propagated downstream.
Otherwise, it drops the item.

The predicate passed to `where` is synchronous.
The `when` method provides an asynchronous version:

```java
List<Integer> list2 = multi
        .select().when(i -> Uni.createFrom().item(i > 6))
        .collect().asList()
        .await().indefinitely();
```

`when` accepts a function called for each item.

Unlike `where` where the predicate returns a boolean synchronously, the function returns a `Uni<Boolean>`.
It forwards the item downstream if the `uni` produced by the function emits `true`.
Otherwise, it drops the item.
