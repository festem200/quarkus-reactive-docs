# What is Reactive Programming?

> **Documentacion oficial:** <https://smallrye.io/smallrye-mutiny/latest/reference/what-is-reactive-programming>  
> **Fuente:** `documentation/docs/reference/what-is-reactive-programming.md` en [smallrye/smallrye-mutiny@3.3.0](https://github.com/smallrye/smallrye-mutiny/blob/3.3.0/documentation/docs/reference/what-is-reactive-programming.md)  
> **Version documentada:** Mutiny 3.3.0 · **Sincronizado:** 2026-08-17 · **Licencia:** Apache-2.0

Mutiny is a reactive programming library.
If you look on Wikipedia for reactive programming, you will find the following definition:

> Reactive Programming combines functional programming, the observer pattern, and the iterable pattern.

While correct, we never found this definition very helpful.
It does not convey clearly what's reactive programming is all about.
So, let's make another definition, much more straightforward:

> Reactive programming is about programming with data streams.

That's it.
Reactive programming is about streams and especially, observing them.
It pushes that idea to its limit: with reactive programming, everything is a data stream.

With reactive programming, you observe streams and implement side effects when _something_ flows in the stream:

```mermaid
sequenceDiagram
    participant S1 as Stream
    participant O1 as Observer
    
    participant S2 as Stream
    participant O2 as Observer
    
    S1->>O1: onItem("a")
    S2->>O2: onItem("a")
    
    S1->>O1: onItem("b")
    S2->>O2: onItem("b")
    
    S2->>O2: onItem("c")
    
    S1-XO1: onFailure(err)
    S2->>O2: onCompletion()
```

It's asynchronous by nature as you don't know when the _data_ is going to be seen.
Yet, reactive programming goes beyond this.
It provides a toolbox to compose streams and process events.
