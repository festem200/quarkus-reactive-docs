# How to use paginated APIs?

> **Documentacion oficial:** <https://smallrye.io/smallrye-mutiny/latest/guides/pagination>  
> **Fuente:** `documentation/docs/guides/pagination.md` en [smallrye/smallrye-mutiny@3.3.0](https://github.com/smallrye/smallrye-mutiny/blob/3.3.0/documentation/docs/guides/pagination.md)  
> **Version documentada:** Mutiny 3.3.0 · **Sincronizado:** 2026-08-17 · **Licencia:** Apache-2.0

There are many REST / HTTP APIs using pagination, _i.e._ return only a subset of the results and you need to request the next _page_ to get the next batch.
Each batch contains a list of item(s).

To use this kind of API and generate a continuous stream of items, you need to use the `Multi.createBy().repeating()` function.
However, we need to pass a cursor / state to advance and avoid requesting again and again the same page.
Fortunately, `repeating` provides methods to pass a shared state.
So by combining these methods and `disjoint` you can generate streams from these pages:

```java
PaginatedApi api = new PaginatedApi();

Multi<String> stream = Multi.createBy().repeating()
        .completionStage(
                () -> new AtomicInteger(),
                state -> api.getPage(state.getAndIncrement()))
        .until(list -> list.isEmpty())
        .onItem().disjoint();
```

First, you create a `Multi` containing the items emitted by the `CompletionStage` supplier and pass a state supplier to progress among the pages.

Then, use `until` to call the paginated API until we have all the items.
At the point we have a stream of list of item such as `["a", "b", "c"], ["d", "e"], []`.
However, we want the following stream: `"a", "b", "c", "d", "e"`.
The `disjoint` method does exactly this.
It gets the items from the lists and passes them downstream:

```mermaid
sequenceDiagram
    autonumber
    participant M as Multi
    participant O as Disjoint operator
    participant D as Subscriber
    
    M->>O: onItem([a,b,c])
    O->>D: onItem(a)
    O->>D: onItem(b)
    O->>D: onItem(c)
    M->>O: onItem([d,e])
    O->>D: onItem(d)
    O->>D: onItem(e)
```

`Multi.createBy().repeating()` lets you choose the number of iterations using:

- `atMost` - exact number of repetitions (or failure happens before reaching that number)
- `until` - the repetition is stopped if the item emitted by the `Uni` **passes** a test (predicate).
  It does not propagate the item that did pass the check, and it stops the repetition.
  The check verifies if the current item does not contain valid data.
- `whilst` - the repetition is stopped if the item emitted by the `Uni` **does not pass** a test (predicate).
  It does propagate the item downstream even if the check does not pass.
  However, it stops the repetition.
  The test verifies if there is a _next_ batch to be retrieved.

The following code illustrates the usage of `whilst`:

```java
PaginatedApi api = new PaginatedApi();

Multi<Page> stream = Multi.createBy().repeating()
        .uni(
                () -> new AtomicInteger(),
                state -> api.retrieve(state.getAndIncrement()))
        .whilst(page -> page.hasNext());
```
