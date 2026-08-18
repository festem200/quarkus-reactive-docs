# Dealing with checked exceptions

> **Documentacion oficial:** <https://smallrye.io/smallrye-mutiny/latest/guides/unchecked-exceptions>  
> **Fuente:** `documentation/docs/guides/unchecked-exceptions.md` en [smallrye/smallrye-mutiny@3.3.0](https://github.com/smallrye/smallrye-mutiny/blob/3.3.0/documentation/docs/guides/unchecked-exceptions.md)  
> **Version documentada:** Mutiny 3.3.0 · **Sincronizado:** 2026-08-17 · **Licencia:** Apache-2.0

When implementing your reactive pipeline, you write lots of functions (`java.util.function.Function`), consumers (`java.util.function.Consumer`), suppliers (`java.util.function.Supplier`) and so on.

By default, you cannot throw checked exceptions.

When integrating libraries throwing checked exceptions (like `IOException`) it's not very convenient to add a `try/catch` block and wrap the thrown exception into a runtime exception:

```java
Uni<Integer> uni = item.onItem().transform(i -> {
    try {
        return methodThrowingIoException(i);
    } catch (IOException e) {
        throw new UncheckedIOException(e);
    }
});
```

Mutiny provides utilities to avoid having to do this manually.

If your operation throws a _checked exception_, you can use the [`io.smallrye.mutiny.unchecked.Unchecked`](https://javadoc.io/doc/io.smallrye.reactive/mutiny/latest/io/smallrye/mutiny/unchecked/Unchecked.html) wrappers.

For example, if your synchronous transformation uses a method throwing a checked exception, wrap it using `Unchecked.function`:

```java
Uni<Integer> uni = item.onItem().transform(Unchecked.function(i -> {
    // Can throw checked exception
    return methodThrowingIoException(i);
}));
```
You can also wrap consumers such as in:

```java
Uni<Integer> uni = item.onItem().invoke(Unchecked.consumer(i -> {
    // Can throw checked exception
    throw new IOException("boom");
}));
```

> **💡 CONSEJO**
>
> You can add the following import statement to simplify the usage of the provided methods:
>
> `import static io.smallrye.mutiny.unchecked.Unchecked.*;`
