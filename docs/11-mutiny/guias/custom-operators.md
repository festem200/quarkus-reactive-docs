# Can I have custom operators?

> **Documentacion oficial:** <https://smallrye.io/smallrye-mutiny/latest/guides/custom-operators>  
> **Fuente:** `documentation/docs/guides/custom-operators.md` en [smallrye/smallrye-mutiny@3.3.0](https://github.com/smallrye/smallrye-mutiny/blob/3.3.0/documentation/docs/guides/custom-operators.md)  
> **Version documentada:** Mutiny 3.3.0 · **Sincronizado:** 2026-08-17 · **Licencia:** Apache-2.0

Yes, but please write operators responsibly!

Both `Uni` and `Multi` support custom operators using the `plug` operator.
Here is an example where we use a custom `Multi` operator that randomly drops items:

```java
Multi.createFrom()
        .range(1, 101)
        .plug(RandomDrop::new)
        .subscribe().with(System.out::println);
```

with the operator defined as follows:

```java
public class RandomDrop<T> extends AbstractMultiOperator<T, T> {
    public RandomDrop(Multi<? extends T> upstream) {
        super(upstream);
    }

    @Override
    public void subscribe(MultiSubscriber<? super T> downstream) {
        upstream.subscribe().withSubscriber(new DropProcessor(downstream));
    }

    private class DropProcessor extends MultiOperatorProcessor<T, T> {
        DropProcessor(MultiSubscriber<? super T> downstream) {
            super(downstream);
        }

        @Override
        public void onItem(T item) {
            if (ThreadLocalRandom.current().nextBoolean()) {
                super.onItem(item);
            }
        }
    }
}
```

> **CAUTION**
>
> Custom operators are an advanced feature: when possible please use the existing operators and use helpers such as `stage` to write readable code.
>
> In the case of custom `Multi` operators it is wise to test them against the _Reactive Streams TCK_.
