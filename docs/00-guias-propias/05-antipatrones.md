# Antipatrones frecuentes (y cómo corregirlos)

Errores que se repiten en proyectos Quarkus reactivos, con la corrección y la fuente
oficial donde está explicado.

## 1. Bloquear dentro del pipeline

```java
// MAL: JDBC en un endpoint que devuelve Uni -> bloquea el event loop
@GET
public Uni<List<Pedido>> listar() {
    List<Pedido> pedidos = jdbcRepo.findAll();     // bloqueante
    return Uni.createFrom().item(pedidos);
}
```

```java
// BIEN (opción A): cliente reactivo de verdad
@GET
public Uni<List<Pedido>> listar() {
    return Pedido.listAll();                       // Panache reactivo
}

// BIEN (opción B): mantener JDBC pero declarar el bloqueo
@GET
@Blocking
public List<Pedido> listar() {
    return jdbcRepo.findAll();                     // se ejecuta en un worker thread
}
```

Referencia: [modelo de ejecución](02-modelo-de-ejecucion.md) y
[Quarkus REST](../02-web-http/rest.md).

## 2. `await()` para "simplificar"

```java
// MAL
String nombre = clienteRest.buscar(id).await().indefinitely();
```

Convierte una llamada asíncrona en bloqueante y, si ocurre en un event loop, puede
provocar un interbloqueo. Devuelve el `Uni` y encadena:

```java
// BIEN
return clienteRest.buscar(id)
        .onItem().transform(Cliente::getNombre);
```

Referencia: [reactive-to-imperative](../11-mutiny/guias/reactive-to-imperative.md).

## 3. `transform` donde toca `transformToUni`

```java
// MAL: produce Uni<Uni<Pedido>>, nunca se resuelve
uni.onItem().transform(id -> repo.buscar(id));

// BIEN
uni.onItem().transformToUni(id -> repo.buscar(id));
```

Referencia: [transforming items asynchronously](../11-mutiny/tutoriales/transforming-items-asynchronously.md).

## 4. Creer que un `Uni` ya está en ejecución

```java
// MAL: la petición HTTP se lanza dos veces (una por suscripción)
Uni<Token> token = pedirToken();
usarEn(token);
usarTambienEn(token);
```

Un `Uni` es una receta perezosa, no un `CompletableFuture` en vuelo. Si quieres una única
ejecución compartida:

```java
// BIEN
Uni<Token> token = pedirToken().memoize().indefinitely();
// o, si el token caduca:
Uni<Token> token = pedirToken().memoize().atLeast(Duration.ofMinutes(5));
```

## 5. Pipeline sin gestión de fallos ni timeout

```java
// MAL: si el servicio remoto se cuelga, la petición se queda colgada
return cliente.consultar(id);

// BIEN
return cliente.consultar(id)
        .ifNoItem().after(Duration.ofSeconds(3)).fail()
        .onFailure(IOException.class).retry()
            .withBackOff(Duration.ofMillis(200), Duration.ofSeconds(2)).atMost(3)
        .onFailure().recoverWithItem(Respuesta.degradada());
```

Referencia: [handling timeouts](../11-mutiny/guias/handling-timeouts.md),
[retrying](../11-mutiny/tutoriales/retrying.md),
[fault tolerance](../06-resiliencia/smallrye-fault-tolerance.md).

## 6. Acumular un stream ilimitado en memoria

```java
// MAL sobre un topic de Kafka o un cursor grande
return multi.collect().asList();

// BIEN: procesar por lotes, o devolver el stream
return multi.group().intoLists().of(500)
        .onItem().transformToUniAndConcatenate(this::guardarLote)
        .collect().last();
```

Para exponer el stream por HTTP, devuelve `Multi<T>` (Quarkus REST lo serializa como
NDJSON o SSE) en lugar de materializar la lista completa.

## 7. Saltar a hilos propios y perder el contexto

```java
// MAL: se pierde el contexto duplicado (RequestScoped, traza, MDC)
CompletableFuture.supplyAsync(() -> hacerAlgo());
new Thread(() -> hacerAlgo()).start();

// BIEN
Uni.createFrom().item(() -> hacerAlgo())
        .runSubscriptionOn(Infrastructure.getDefaultWorkerPool());
```

Referencia: [duplicated context](../01-fundamentos/duplicated-context.md),
[context propagation](../01-fundamentos/context-propagation.md).

## 8. Mezclar `@Transactional` con transacciones reactivas

```java
// MAL: JTA + Panache reactivo en el mismo pipeline -> UnsupportedOperationException
@Transactional
public Uni<Pedido> crear(Pedido p) { return p.persist(); }

// BIEN
@WithTransaction
public Uni<Pedido> crear(Pedido p) { return p.persist(); }
```

Referencia: [hibernate-reactive-panache](../03-datos/hibernate-reactive-panache.md).

## 9. Excepciones lanzadas en vez de propagadas

```java
// MAL: en un método que construye el pipeline, lanzar rompe el contrato
public Uni<Pedido> buscar(String id) {
    if (id == null) throw new IllegalArgumentException("id nulo");   // fuera del flujo
    return repo.buscar(id);
}

// BIEN
public Uni<Pedido> buscar(String id) {
    if (id == null) {
        return Uni.createFrom().failure(new IllegalArgumentException("id nulo"));
    }
    return repo.buscar(id);
}
```

Dentro de los operadores, en cambio, las excepciones sí se capturan y se convierten en
eventos de fallo. Ver [unchecked exceptions](../11-mutiny/guias/unchecked-exceptions.md)
y [dropped exceptions](../11-mutiny/guias/dropped-exceptions.md).

## 10. Suponer que "reactivo" significa "más rápido"

Con baja concurrencia, un endpoint reactivo puede ser marginalmente **más lento** que uno
imperativo: la ganancia está en el uso de memoria y en la degradación bajo carga, no en la
latencia de una petición aislada. Mide antes de rediseñar
([performance-measure](../08-rendimiento-nativo/performance-measure.md)).

## 11. Pool de conexiones sin dimensionar

Al eliminar los hilos como límite, el límite pasa a ser el pool reactivo
(`quarkus.datasource.reactive.max-size`, 20 por defecto). Miles de peticiones concurrentes
contra 20 conexiones producen encolado invisible: latencia alta sin CPU alta.
Ver [datasource](../03-datos/datasource.md).

## 12. `@RunOnVirtualThread` como bala de plata

Los hilos virtuales no eliminan el *pinning* (bloqueos dentro de `synchronized`), ni el
límite del pool de base de datos, ni la necesidad de contrapresión en streaming. Ver
limitaciones en [virtual-threads](../01-fundamentos/virtual-threads.md).
