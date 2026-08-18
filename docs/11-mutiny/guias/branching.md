# How to do branching in a reactive pipeline?

> **Documentacion oficial:** <https://smallrye.io/smallrye-mutiny/latest/guides/branching>  
> **Fuente:** `documentation/docs/guides/branching.md` en [smallrye/smallrye-mutiny@3.3.0](https://github.com/smallrye/smallrye-mutiny/blob/3.3.0/documentation/docs/guides/branching.md)  
> **Version documentada:** Mutiny 3.3.0 · **Sincronizado:** 2026-08-17 · **Licencia:** Apache-2.0

Mutiny and similar reactive programming libraries do not have _branching_ operators similar to `if / else` and `switch/case` statements in Java.

This does not mean that we can't express _branching_ in a reactive pipeline, and the most classic way is to use a transformation to a `Uni` (also called `flatMap` in functional programming).

## Expressing branches as Uni operations

Suppose that we have a pipeline where a `Uni` is created from a random value, and suppose that we want to have a different processing pipeline depending on whether the value is odd or even.
Let's have these 2 `Uni`-returning methods to model different behaviors:

```java
Uni<String> evenOperation(int n) {
    return Uni.createFrom().item("Even number: " + n)
            .onItem().invoke(() -> System.out.println("(even branch)"));
}

Uni<String> oddOperation(int n) {
    return Uni.createFrom().item("Odd number: " + n)
            .onItem().invoke(() -> System.out.println("(odd branch)"));
}
```

We can use the `transformToUni` operator to plug either method depending on the random number:

```java
Random random = new Random();
Uni.createFrom().item(() -> random.nextInt(100))
        .onItem().transformToUni(n -> {
            if (n % 2 == 0) {
                return evenOperation(n);
            } else {
                return oddOperation(n);
            }
        })
        .subscribe().with(System.out::println);
```

Having such a mapping function is a common pattern: it has conditional logic and each branch returns a `Uni` that represents the "sub-pipeline" of what each branch shall do.

Note that such constructs are primarily relevant when asynchronous I/O are involved and that such asynchronous I/O operations are typically `Uni`-returning methods such as those found in the [Mutiny Vert.x bindings](https://smallrye.io/smallrye-mutiny-vertx-bindings/).

> **💡 CONSEJO**
>
> There are other ways to express the "result" of a branch.
> You could wrap results in a custom type or a container like `java.util.Optional`.
>
> You could also return a failed `Uni`, and later react by continuing with another `Uni`, another value, or retrying (which would model a loop!).

## Branching in a Multi

The case of `Multi` is even more interesting because a `null`-completed `Uni` is discarded from the stream by any of the `transformToUni{...}` methods:

```java
Random random = new Random();
Multi.createBy().repeating().supplier(random::nextInt).atMost(20)
        .onItem().transformToUniAndMerge(n -> {
            System.out.println("----");
            if (n < 0) {
                return drop();
            } else if (n % 2 == 0) {
                return evenOperation(n);
            } else {
                return oddOperation(n);
            }
        })
        .subscribe().with(str -> System.out.println("=> " + str));
```

where `drop()` is as follows:

```java
Uni<String> drop() {
    return Uni.createFrom().<String>nullItem()
            .onItem().invoke(() -> System.out.println("(dropping negative value)"));
}
```

Any negative value is discarded in this `Multi` pipeline, while the positive even and odd numbers get forwarded to the subscriber.
