# Kotlin integration

> **Documentacion oficial:** <https://smallrye.io/smallrye-mutiny/latest/guides/kotlin>  
> **Fuente:** `documentation/docs/guides/kotlin.md` en [smallrye/smallrye-mutiny@3.3.0](https://github.com/smallrye/smallrye-mutiny/blob/3.3.0/documentation/docs/guides/kotlin.md)  
> **Version documentada:** Mutiny 3.3.0 · **Sincronizado:** 2026-08-17 · **Licencia:** Apache-2.0

The module `mutiny-kotlin` provides an integration with Kotlin for use with coroutines and convenient language features.

There are extension methods available for converting between Mutiny and Kotlin (coroutine) types.
For implementation details please have also a look to these methods' documentation.

## Dependency coordinates

The coroutine extension functions are shipped in the package `io.smallrye.mutiny.coroutines`.

```kotlin
import io.smallrye.mutiny.coroutines.asFlow
import io.smallrye.mutiny.coroutines.asMulti
import io.smallrye.mutiny.coroutines.asUni
import io.smallrye.mutiny.coroutines.awaitSuspending
```

You need to add the following dependency to your project:

=== "Maven"

    ```xml
    <dependency>
        <groupId>io.smallrye.reactive</groupId>
        <artifactId>mutiny-kotlin</artifactId>
        <version>3.3.0</version>
    </dependency>
    ```

=== "Gradle (Kotlin)"

    ```kotlin
    implementation("io.smallrye.reactive:mutiny-kotlin:3.3.0")
    ```

=== "Gradle (Groovy)"

    ```groovy
    implementation "io.smallrye.reactive:mutiny-kotlin:3.3.0"
    ```

## Awaiting a Uni in coroutines

Within a coroutine or suspend function you can easily await Uni events in a suspended way:

```kotlin
val uni: Uni<String> = Uni.createFrom().item("Mutiny ❤ Kotlin")
try {
    // Available within suspend function and CoroutineScope
    val item: String = uni.awaitSuspending()
} catch (failure: Throwable) {
    // onFailure event happened
}
```

## Processing a Multi as Flow

The coroutine `Flow` type matches `Multi` semantically, even though it isn't a feature complete reactive streams implementation.
You can process a `Multi` as `Flow` as follows:

```kotlin
val multi: Multi<String> = Multi.createFrom().items("Mutiny", "❤", "Kotlin")
val flow: Flow<String> = multi.asFlow()
```

> **📌 NOTA**
>
> There's no flow control availabe for Kotlin's `Flow`. Published items are buffered for consumption using a coroutine `Channel`.
> The buffer size and overflow strategy of that `Channel` can be configured using optional arguments:
> `Multi.asFlow(bufferCapacity = Channel.UNLIMITED, bufferOverflowStrategy = BufferOverflow.SUSPEND)`,
> for more details please consult the method documentation.

## Providing a Deferred value as Uni

The other way around is also possible, let a Deferred become a Uni:

```kotlin
val deferred: Deferred<String> = GlobalScope.async { "Kotlin ❤ Mutiny" }
val uni: Uni<String> = deferred.asUni()
```

## Creating a Multi from a Flow

Finally, creating a Multi from a Flow is also possible:

```kotlin
val flow: Flow<String> = flowOf("Kotlin", "❤", "Mutiny")
val multi: Multi<String> = flow.asMulti()
```

## Awaiting Multi results in coroutines

You can consume `Multi` results directly from suspend functions without converting to `Flow` first:

```kotlin
val multi = Multi.createFrom().items("a", "b", "c")
val list: List<String> = multi.awaitList()
```

```kotlin
val multi = Multi.createFrom().items(1, 2, 3)
val first: Int? = multi.awaitFirst()
val firstOrThrow: Int = multi.awaitFirstOrThrow()
```

```kotlin
val multi = Multi.createFrom().items(1, 2, 3)
val last: Int? = multi.awaitLast()
val lastOrThrow: Int = multi.awaitLastOrThrow()
```

```kotlin
val multi = Multi.createFrom().items(1, 2, 3)
multi.awaitEach { item ->
    println("Processing $item")
}
```

## Language convenience

### Unit instead of Void (null) value

Kotlin has a special value type `Unit` similar to Java's `Void`.
While regular `Uni<Void>` holds a `null` item, you can get a `Unit` by using the extension function `replaceWithUnit()`:

```kotlin
// import io.smallrye.mutiny.replaceWithUnit
val unitUni : Uni<Unit> = uni.replaceWithUnit()
assert(unitUni.await().indefinitely() === Unit)
```

### Uni builder

Building a `Uni` from Kotlin code can easily be achieved using the following builders available as regular or coroutine variant:

```kotlin
// import io.smallrye.mutiny.uni
val uni: Uni<String> = uni { "λ 🚧" }
```

```kotlin
// import io.smallrye.mutiny.coroutines.uni
coroutineScope {
    val uni: Uni<String> = uni { "λ 🚧" }
}
```

### Multi builder

Building a `Multi` from Kotlin code can be achieved using the `multi` builder, available as regular or coroutine variant:

```kotlin
// import io.smallrye.mutiny.multi
val multi = multi<Int> {
    emit(1)
    emit(2)
    emit(3)
}
```

The builder accepts an optional back-pressure strategy:

```kotlin
// import io.smallrye.mutiny.multi
val multi = multi<Int>(backPressure = BackPressureStrategy.DROP) {
    emit(1)
    emit(2)
    emit(3)
}
```

A coroutine variant allows suspend calls within the builder:

```kotlin
// import io.smallrye.mutiny.coroutines.multi
val queryResult = fetchResults()
coroutineScope {
    val multi = multiSuspend(context = this) {
        queryResult.forEach { result -> emit(result.download()) }
    }
}
```

### Tuple destructuring

Mutiny's `Tuple2` through `Tuple9` support Kotlin destructuring declarations:

```kotlin
// import io.smallrye.mutiny.component1
// import io.smallrye.mutiny.component2
val uni = Uni.combine().all()
    .unis(
        Uni.createFrom().item("Alice"),
        Uni.createFrom().item(30)
    ).asTuple()

val (name, age) = uni.await().indefinitely()
assert(name == "Alice")
assert(age == 30)
```

### Typed failure handling

Use reified generics for concise failure type matching on both `Uni` and `Multi`:

```kotlin
// import io.smallrye.mutiny.onFailure
val uni = Uni.createFrom().failure<String>(IOException("disk full"))
val recovered: Uni<String> = uni.onFailure<String, IOException>()
    .recoverWithItem("recovered")
```

```kotlin
// import io.smallrye.mutiny.onFailure
val multi = Multi.createFrom().failure<String>(IOException("disk full"))
val recovered: Multi<String> = multi.onFailure<String, IOException>()
    .recoverWithItem("recovered")
```
