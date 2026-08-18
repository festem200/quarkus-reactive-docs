# Chuleta de Mutiny

Referencia rápida de la API que usarás el 95 % del tiempo. La fuente completa está en
[`docs/11-mutiny/`](../11-mutiny/README.md); aquí solo está lo que conviene tener a mano.

Regla mental: **Mutiny se lee como frases**. `onX().accionY()` = "cuando ocurra X, haz Y".
El autocompletado del IDE es parte del diseño: escribe `.on` y deja que te guíe.

## Los dos tipos

| Tipo | Emite | Equivalente aproximado |
| --- | --- | --- |
| `Uni<T>` | 0 o 1 item, o un fallo | `CompletableFuture<T>`, `Mono<T>` |
| `Multi<T>` | 0..n items, luego completado o fallo | `Flux<T>`, `Publisher<T>` |

Ambos son **perezosos**: sin `subscribe()` no ocurre nada. En Quarkus normalmente no te
suscribes tú: devuelves el `Uni`/`Multi` desde el endpoint y el framework se suscribe.

## Crear

```java
Uni.createFrom().item("hola");                 // valor ya disponible
Uni.createFrom().item(() -> calcular());       // valor perezoso (se evalúa al suscribir)
Uni.createFrom().nullItem();
Uni.createFrom().failure(new IllegalStateException("boom"));
Uni.createFrom().completionStage(() -> futuro);// puente desde CompletableFuture
Uni.createFrom().emitter(em -> api.callback(em::complete, em::fail)); // puente con callbacks
Uni.createFrom().voidItem();
Uni.createFrom().deferred(() -> construirUni()); // decide el Uni en el momento de suscribir

Multi.createFrom().items(1, 2, 3);
Multi.createFrom().iterable(lista);
Multi.createFrom().range(0, 10);
Multi.createFrom().ticks().every(Duration.ofSeconds(1));
Multi.createFrom().publisher(publisherReactiveStreams);
Multi.createFrom().emitter(em -> { em.emit(1); em.complete(); });
```

## Transformar

```java
uni.onItem().transform(s -> s.toUpperCase());          // síncrono: T -> R
uni.onItem().transformToUni(id -> repo.buscar(id));    // asíncrono: T -> Uni<R>  (¡el más usado!)
uni.onItem().transformToMulti(id -> repo.stream(id));  // T -> Multi<R>

multi.onItem().transform(x -> x * 2);
multi.onItem().transformToUniAndConcatenate(this::llamar);  // orden garantizado
multi.onItem().transformToUniAndMerge(this::llamar);        // más rápido, orden no garantizado
```

`transform` frente a `transformToUni` es el error clásico: si tu función devuelve un
`Uni` y usas `transform`, acabas con un `Uni<Uni<T>>` que nunca se resuelve.

## Efectos secundarios (sin cambiar el item)

```java
uni.onItem().invoke(item -> log.info("recibido {}", item));   // síncrono, no espera
uni.onItem().call(item -> auditar(item));                     // asíncrono, SÍ espera al Uni devuelto
uni.onFailure().invoke(t -> log.error("falló", t));
uni.onSubscription().invoke(sub -> log.debug("suscrito"));
uni.onTermination().invoke(() -> cerrarRecursos());
```

`invoke` para logging; `call` cuando la acción es asíncrona y debe completarse antes de
continuar (ej. escribir una auditoría antes de responder).

## Filtrar y limitar (Multi)

```java
multi.select().where(x -> x > 10);
multi.select().first(20);
multi.select().first(Duration.ofSeconds(5));
multi.select().distinct();
multi.skip().first(3);
multi.skip().repetitions();          // elimina repeticiones consecutivas
```

## Fallos

```java
uni.onFailure().recoverWithItem(valorPorDefecto);
uni.onFailure().recoverWithItem(t -> fallback(t));
uni.onFailure().recoverWithUni(t -> servicioAlternativo());
uni.onFailure(NotFoundException.class).recoverWithNull();
uni.onFailure().transform(t -> new ApiException("no disponible", t));
uni.onFailure().retry().atMost(3);
uni.onFailure().retry().withBackOff(Duration.ofMillis(200), Duration.ofSeconds(5)).atMost(5);
uni.onFailure().retry().until(t -> t instanceof IOException);
uni.onItem().ifNull().failWith(() -> new NotFoundException());
uni.onItem().ifNull().continueWith(Collections.emptyList());
```

Se puede filtrar por clase de excepción o por predicado, lo que evita reintentar errores
que nunca se van a arreglar solos (un 400, por ejemplo).

## Tiempos

```java
uni.ifNoItem().after(Duration.ofSeconds(2)).fail();
uni.ifNoItem().after(Duration.ofSeconds(2)).recoverWithItem(cacheado);
uni.onItem().delayIt().by(Duration.ofMillis(100));
```

## Combinar

```java
// esperar a varios en paralelo
Uni.combine().all().unis(uniA, uniB).asTuple();
Uni.combine().all().unis(uniA, uniB).with((a, b) -> new Resultado(a, b));

// el primero que responda gana
Uni.combine().any().of(uniPrimario, uniReplica);
Uni.join().first(a, b, c).withItem();            // primer item válido, ignorando fallos
Uni.join().all(a, b, c).andFailFast();           // Uni<List<T>>, aborta al primer fallo

// unir streams
Multi.createBy().merging().streams(multiA, multiB);       // intercalado
Multi.createBy().concatenating().streams(multiA, multiB); // uno detrás de otro
```

## Agrupar y recolectar

```java
multi.group().intoLists().of(100);                        // lotes de 100
multi.group().intoLists().every(Duration.ofSeconds(1));   // ventanas temporales
multi.group().by(item -> item.getTipo());

multi.collect().asList();      // Uni<List<T>>  — cuidado: acumula en memoria
multi.collect().first();       // Uni<T>
multi.collect().with(Collectors.counting());
```

## Hilos

```java
uni.emitOn(Infrastructure.getDefaultExecutor());            // dónde se emiten los eventos hacia abajo
uni.runSubscriptionOn(Infrastructure.getDefaultWorkerPool()); // dónde se ejecuta el trabajo de origen
```

Detalles y diagramas: [emitOn vs runSubscriptionOn](../11-mutiny/guias/emit-on-vs-run-subscription-on.md).

## Suscribirse (solo cuando no lo hace el framework)

```java
uni.subscribe().with(
    item -> log.info("ok {}", item),
    fallo -> log.error("ko", fallo));

Cancellable c = multi.subscribe().with(item -> procesar(item));
c.cancel();
```

## Bloquear (casi siempre, un error)

```java
String valor = uni.await().indefinitely();          // ¡nunca en un event loop!
String v2 = uni.await().atMost(Duration.ofSeconds(3));
```

Sólo aceptable en tests, en `main()` de una aplicación en modo comando o en código que
ya sabes que corre en un worker o en un hilo virtual. Ver
[reactive-to-imperative](../11-mutiny/guias/reactive-to-imperative.md).

## Memoización y reutilización

```java
Uni<Config> cache = cargarConfig().memoize().indefinitely();
Uni<Token> token = pedirToken().memoize().atLeast(Duration.ofMinutes(5));
```

Sin `memoize`, cada suscripción vuelve a ejecutar el trabajo: un `Uni` no es un
`CompletableFuture` ya lanzado, es una receta que se ejecuta al suscribirse.

## Testing

```java
UniAssertSubscriber<String> sub = uni.subscribe()
        .withSubscriber(UniAssertSubscriber.create());
sub.awaitItem().assertItem("esperado");

AssertSubscriber<Integer> s = multi.subscribe()
        .withSubscriber(AssertSubscriber.create(10));
s.awaitCompletion().assertItems(1, 2, 3);
```

Guía completa: [testing de Mutiny](../11-mutiny/guias/testing.md) y
[spies](../11-mutiny/guias/spies.md).
