# Controlling the demand

> **Documentacion oficial:** <https://smallrye.io/smallrye-mutiny/latest/guides/controlling-demand>  
> **Fuente:** `documentation/docs/guides/controlling-demand.md` en [smallrye/smallrye-mutiny@3.3.0](https://github.com/smallrye/smallrye-mutiny/blob/3.3.0/documentation/docs/guides/controlling-demand.md)  
> **Version documentada:** Mutiny 3.3.0 · **Sincronizado:** 2026-08-17 · **Licencia:** Apache-2.0

## Pacing the demand

A subscription is used for 2 purposes: cancelling a request and demanding batches of items.

The `Multi.paceDemand()` operator can be used to automatically issue requests at certain points in time.

The following example issues requests of 25 items every 100ms:

```java
FixedDemandPacer pacer = new FixedDemandPacer(25L, Duration.ofMillis(100L));

Multi<Integer> multi = Multi.createFrom().range(0, 100)
        .paceDemand().on(Infrastructure.getDefaultWorkerPool()).using(pacer);
```

`FixedDemandPacer` is a simple _pacer_ with a fixed demand and a fixed delay.

You can create more elaborated pacers by implementing the `DemandPacer` interface.
To do so you provide an initial request and a function to evaluate the next request which is evaluated based on the previous request and the number of items emitted since the last request:

```java
DemandPacer pacer = new DemandPacer() {

    @Override
    public Request initial() {
        return new Request(10L, Duration.ofMillis(100L));
    }

    @Override
    public Request apply(Request previousRequest, long observedItemsCount) {
        return new Request(previousRequest.demand() * 2, previousRequest.delay().plus(10, ChronoUnit.MILLIS));
    }
};
```

The previous example is a custom pacer that doubles the demand and increases the delay for each new request.

## Capping the demand requests

The `capDemandsTo` and `capDemandUsing` operators can be used to cap the demand from downstream subscribers.

The `capDemandTo` operator defines a maximum demand that can flow:

```java
AssertSubscriber<Integer> sub = AssertSubscriber.create();

sub = Multi.createFrom().range(0, 100)
        .capDemandsTo(50L)
        .subscribe().withSubscriber(sub);

// A first batch of 50 (capped), 25 remain outstanding
sub.request(75L).assertNotTerminated();
assertThat(sub.getItems()).hasSize(50);

// Second batch: 25 + 25 = 50
sub.request(25L).assertCompleted();
assertThat(sub.getItems()).hasSize(100);
```

Here we cap requests to 50 items, so it takes 2 requests to get all 100 items of the upstream range.
The first request of 75 items is capped to a request of 50 items, leaving an outstanding demand of 25 items.
The second request of 25 items is added to the outstanding demand, resulting in a request of 50 items and completing the stream.

You can also define a custom function that provides a capping value based on a custom formula, or based on earlier demand observations:

```java
AssertSubscriber<Integer> sub = AssertSubscriber.create();

sub = Multi.createFrom().range(0, 100)
        .capDemandsUsing(n -> {
            if (n > 1) {
                return (long) (((double) n) * 0.75d);
            } else {
                return n;
            }
        })
        .subscribe().withSubscriber(sub);

sub.request(100L).assertNotTerminated();
assertThat(sub.getItems()).hasSize(75);

sub.request(1L).assertNotTerminated();
assertThat(sub.getItems()).hasSize(94);

sub.request(Long.MAX_VALUE).assertCompleted();
assertThat(sub.getItems()).hasSize(100);
```

Here we have a function that requests 75% of the downstream requests.

Note that the function must return a value `n` that satisfies `(0 < n <= requested)` where `requested` is the downstream demand.

## Pausing the demand

The `Multi.pauseDemand()` operator provides fine-grained control over demand propagation in reactive streams.
Unlike cancellation, which terminates the subscription, pausing allows to suspend demand without unsubscribing from the upstream.
This is useful for implementing flow control patterns where item flow needs to be paused based on external conditions.

### Basic pausing and resuming

The `pauseDemand()` operator works with a `DemandPauser` handle that allows to control the stream:

```java
DemandPauser pauser = new DemandPauser();

AssertSubscriber<Integer> sub = AssertSubscriber.create();
Multi.createFrom().range(0, 100)
        .pauseDemand().using(pauser)
        // Throttle the multi
        .onItem().call(i -> Uni.createFrom().nullItem()
                .onItem().delayIt().by(Duration.ofMillis(10)))
        .subscribe().withSubscriber(sub);

// Unbounded request
sub.request(Long.MAX_VALUE);
// Wait for some items
await().untilAsserted(() -> assertThat(sub.getItems()).hasSizeGreaterThan(10));

// Pause the stream
pauser.pause();
assertThat(pauser.isPaused()).isTrue();

int sizeWhenPaused = sub.getItems().size();

// Wait - no new items should arrive (except a few in-flight)
await().pollDelay(Duration.ofMillis(100)).until(() -> true);
assertThat(sub.getItems()).hasSizeLessThanOrEqualTo(sizeWhenPaused + 5);

// Resume the stream
pauser.resume();
assertThat(pauser.isPaused()).isFalse();

// All items eventually arrive
sub.awaitCompletion();
assertThat(sub.getItems()).hasSize(100);
```

The `DemandPauser` provides methods to:

- `pause()`: Stop propagating demand to upstream
- `resume()`: Resume demand propagation and deliver buffered items
- `isPaused()`: Check the current pause state

Note that a few items may still arrive after pausing due to in-flight requests that were already issued to upstream.

### Starting in a paused state

You can create a stream that starts paused and only begins flowing when explicitly resumed:

```java
DemandPauser pauser = new DemandPauser();

AssertSubscriber<Integer> sub = Multi.createFrom().range(0, 50)
        .pauseDemand()
        .paused(true)  // Start paused
        .using(pauser)
        .subscribe().withSubscriber(AssertSubscriber.create(Long.MAX_VALUE));

// No items arrive while paused
await().pollDelay(Duration.ofMillis(100)).until(() -> true);
assertThat(sub.getItems()).isEmpty();
assertThat(pauser.isPaused()).isTrue();

// Resume to start receiving items
pauser.resume();
sub.awaitCompletion();
assertThat(sub.getItems()).hasSize(50);
```

This is useful when you want to prepare a stream but delay its execution until certain conditions are met.

### Late subscription

By default, the upstream subscription happens immediately even when starting paused.
The `lateSubscription()` option delays the upstream subscription until the stream is resumed:

```java
DemandPauser pauser = new DemandPauser();
AtomicBoolean subscribed = new AtomicBoolean(false);

AssertSubscriber<Integer> sub = Multi.createFrom().range(0, 50)
        .onSubscription().invoke(() -> subscribed.set(true))
        .pauseDemand()
        .paused(true)           // Start paused
        .lateSubscription(true) // Delay subscription until resumed
        .using(pauser)
        .subscribe().withSubscriber(AssertSubscriber.create(Long.MAX_VALUE));

// Stream is not subscribed yet
await().pollDelay(Duration.ofMillis(100)).until(() -> true);
assertThat(subscribed.get()).isFalse();
assertThat(sub.getItems()).isEmpty();

// Resume triggers subscription and item flow
pauser.resume();
await().untilAsserted(() -> assertThat(subscribed.get()).isTrue());
sub.awaitCompletion();
assertThat(sub.getItems()).hasSize(50);
```

### Buffer strategies

When a stream is paused, the operator stops requesting new items from upstream.
However, items that were already requested (due to downstream demand) may still arrive.
Buffer strategies control what happens to these in-flight items.

The `pauseDemand()` operator supports three buffer strategies: `BUFFER` (default), `DROP`, and `IGNORE`.
Configuring any other strategy will throw an `IllegalArgumentException`.

#### BUFFER strategy (default)

Already-requested items are buffered while paused and delivered when resumed:

```java
DemandPauser pauser = new DemandPauser();

AssertSubscriber<Long> sub = AssertSubscriber.create(Long.MAX_VALUE);

Multi.createFrom().ticks().every(Duration.ofMillis(10))
        .select().first(100)
        .pauseDemand()
        .bufferStrategy(BackPressureStrategy.BUFFER)
        .bufferSize(20)  // Buffer up to 20 items
        .using(pauser)
        .subscribe().withSubscriber(sub);

// Wait for some items
await().untilAsserted(() -> assertThat(sub.getItems()).hasSizeGreaterThan(5));

// Pause - items buffer up to the limit
pauser.pause();

// Wait for buffer to fill
await().pollDelay(Duration.ofMillis(100))
        .untilAsserted(() -> assertThat(pauser.bufferSize()).isGreaterThan(0));

// Buffer size is capped
assertThat(pauser.bufferSize()).isLessThanOrEqualTo(20);

// Resume drains the buffer
pauser.resume();
await().untilAsserted(() -> assertThat(pauser.bufferSize()).isEqualTo(0));
```

You can configure the buffer size:

- `bufferUnconditionally()`: Unbounded buffer
- `bufferSize(n)`: Buffer up to `n` items, then fail with buffer overflow

When the buffer overflows, the stream fails with an `IllegalStateException`.

**Important**: The buffer only holds items that were already requested from upstream before pausing.
When paused, no new requests are issued to upstream, so the buffer size is bounded by the outstanding demand at the time of pausing.

#### DROP strategy

Already-requested items are dropped while paused:

```java
DemandPauser pauser = new DemandPauser();

AssertSubscriber<Long> sub = Multi.createFrom().ticks().every(Duration.ofMillis(5))
        .select().first(200)
        .pauseDemand()
        .bufferStrategy(BackPressureStrategy.DROP)  // Drop items while paused
        .using(pauser)
        .subscribe().withSubscriber(AssertSubscriber.create(Long.MAX_VALUE));

// Wait for some items
await().untilAsserted(() -> assertThat(sub.getItems()).hasSizeGreaterThan(20));

// Pause - subsequent items are dropped
pauser.pause();
int sizeWhenPaused = sub.getItems().size();

// Wait while items are dropped
await().pollDelay(Duration.ofMillis(200)).until(() -> true);

// Resume - continue from current position
pauser.resume();
await().atMost(Duration.ofSeconds(3))
        .untilAsserted(() -> assertThat(sub.getItems().size()).isGreaterThan(sizeWhenPaused + 20));

sub.awaitCompletion();
// Not all items arrived (some were dropped)
assertThat(sub.getItems()).hasSizeLessThan(200);
```

Items that arrive while paused are discarded, and when resumed, the stream continues requesting fresh items.

#### IGNORE strategy

Already-requested items continue to flow downstream while paused.
This strategy doesn't use any buffers.
It only pauses demand from being issued to upstream, but does not pause the flow of already requested items.

### Buffer management

When using the BUFFER strategy, you can inspect and manage the buffer:

```java
DemandPauser pauser = new DemandPauser();

AssertSubscriber<Long> sub = Multi.createFrom().ticks().every(Duration.ofMillis(10))
        .select().first(100)
        .pauseDemand()
        .bufferStrategy(BackPressureStrategy.BUFFER)
        .bufferUnconditionally()  // Unbounded buffer
        .using(pauser)
        .subscribe().withSubscriber(AssertSubscriber.create(Long.MAX_VALUE));

// Wait for some items
await().untilAsserted(() -> assertThat(sub.getItems()).hasSizeGreaterThan(5));

// Pause and let buffer fill
pauser.pause();
await().pollDelay(Duration.ofMillis(100))
        .untilAsserted(() -> assertThat(pauser.bufferSize()).isGreaterThan(0));

int bufferSize = pauser.bufferSize();
assertThat(bufferSize).isGreaterThan(0);

// Clear the buffer
boolean cleared = pauser.clearBuffer();
assertThat(cleared).isTrue();
assertThat(pauser.bufferSize()).isEqualTo(0);

// Resume - items continue from current position (cleared items are lost)
pauser.resume();
```

The `DemandPauser` provides:

- `bufferSize()`: Returns the current number of buffered items
- `clearBuffer()`: Clears the buffer (only works while paused), returns `true` if successful
