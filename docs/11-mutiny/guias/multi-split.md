# Splitting a Multi into several Multi

> **Documentacion oficial:** <https://smallrye.io/smallrye-mutiny/latest/guides/multi-split>  
> **Fuente:** `documentation/docs/guides/multi-split.md` en [smallrye/smallrye-mutiny@3.3.0](https://github.com/smallrye/smallrye-mutiny/blob/3.3.0/documentation/docs/guides/multi-split.md)  
> **Version documentada:** Mutiny 3.3.0 · **Sincronizado:** 2026-08-17 · **Licencia:** Apache-2.0

It is possible to split a `Multi` into several `Multi` streams.

## Using the split operator

Suppose that we have a stream of strings that represent _signals_, and that we want a `Multi` for each kind of signal:

- `?foo`, `?bar` are _input_ signals,
- `!foo`, `!bar` are _output_ signals,
- `foo`, `bar` are _other_ signals.

To do that, we need a function that maps each item of the stream to its target stream.
The splitter API needs a Java enumeration to define keys, as in:

```java
enum Signals {
    INPUT,
    OUTPUT,
    OTHER
}
```

Now we can use the `split` operator that provides a splitter object, and fetch individual `Multi` for each split stream using the `get` method:

```java
Multi<String> multi = Multi.createFrom().items(
        "!a", "?b", "!c", "!d", "123", "?e"
);

var splitter = multi.split(Signals.class, s -> {
    if (s.startsWith("?")) {
        return Signals.INPUT;
    } else if (s.startsWith("!")) {
        return Signals.OUTPUT;
    } else {
        return Signals.OTHER;
    }
});

splitter.get(Signals.INPUT)
        .onItem().transform(s -> s.substring(1))
        .subscribe().with(signal -> System.out.println("input - " + signal));

splitter.get(Signals.OUTPUT)
        .onItem().transform(s -> s.substring(1))
        .subscribe().with(signal -> System.out.println("output - " + signal));

splitter.get(Signals.OTHER)
        .subscribe().with(signal -> System.out.println("other - " + signal));
```

This prints the following console output:

```
output - a
input - b
output - c
output - d
other - 123
input - e
```

## Notes on using splits

- Items flow when all splits have a subscriber.
- The flow stops when either of the subscribers cancels, or when any subscriber has a no outstanding demand.
- The flow resumes when all splits have a subscriber again, and when all subscribers have outstanding demand.
- Only one subscriber can be active for a given split. Other subscription attempts will receive an error.
- When a subscriber cancels, then a new subscription attempt on its corresponding split can succeed.
- Subscribing to an already completed or errored split results in receiving the terminal signal (`onComplete()` or `onFailure(err)`).
- The upstream `Multi` gets subscribed to when the first split subscription happens, no matter which split it is.
- The first split subscription passes its context, if any, to the upstream `Multi`. It is expected that all split subscribers share the same context object, or the behavior of your code will most likely be incorrect.
