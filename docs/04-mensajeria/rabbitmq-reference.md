# Reactive Messaging RabbitMQ Connector Reference Documentation

> **Guia oficial:** <https://quarkus.io/guides/rabbitmq-reference>  
> **Fuente:** `docs/src/main/asciidoc/rabbitmq-reference.adoc` en [quarkusio/quarkus@3.38.2](https://github.com/quarkusio/quarkus/blob/3.38.2/docs/src/main/asciidoc/rabbitmq-reference.adoc)  
> **Version documentada:** Quarkus 3.38.2 · **Sincronizado:** 2026-08-17 · **Licencia:** Apache-2.0

This guide is the companion from the [Getting Started with RabbitMQ](rabbitmq.md).
It explains in more details the configuration and usage of the RabbitMQ connector for reactive messaging.

**💡 TIP**\
This documentation does not cover all the details of the connector.
Refer to the [SmallRye Reactive Messaging website](https://smallrye.io/smallrye-reactive-messaging) for further details.

The RabbitMQ connector allows Quarkus applications to send and receive messages using the AMQP 0.9.1 protocol.
More details about the protocol can be found in [the AMQP 0.9.1 specification](https://www.rabbitmq.com/amqp-0-9-1-reference.html#queue.bind.routing-key).

**❗ IMPORTANT**\
The RabbitMQ connector is specifically designed for AMQP 0-9-1.
While RabbitMQ 4 now supports the AMQP 1.0 protocol, the two protocols are fundamentally different.
If you want to communicate with RabbitMQ using AMQP 1.0, we recommend using the [AMQP 1.0 connector](amqp-reference.md).
Please note that using AMQP 1.0 with RabbitMQ may still have some limitations or reduced functionality compared to native 0-9-1 usage.

<dl><dt><strong><a name="extension-status-note"></a>📌 NOTE</strong></dt><dd>

This technology is considered preview.

## RabbitMQ connector extension

To use the connector, you need to add the `quarkus-messaging-rabbitmq` extension.

You can add the extension to your project using:

```bash
> ./mvnw quarkus:add-extensions -Dextensions="quarkus-messaging-rabbitmq"
```

Or just add the following dependency to your project:

```xml
<dependency>
    <groupId>io.quarkus</groupId>
    <artifactId>quarkus-messaging-rabbitmq</artifactId>
</dependency>
```

Once added to your project, you can map _channels_ to RabbitMQ exchanges or queues by configuring the `connector` attribute:

```properties
# Inbound
mp.messaging.incoming.[channel-name].connector=smallrye-rabbitmq

# Outbound
mp.messaging.outgoing.[channel-name].connector=smallrye-rabbitmq
```

`outgoing` channels are mapped to RabbitMQ exchanges and `incoming` channels are mapped to RabbitMQ queues as required
by the broker.

## Configuring the RabbitMQ Broker access

The RabbitMQ connector connects to RabbitMQ brokers.
To configure the location and credentials of the broker, add the following properties in the `application.properties`:

```properties
rabbitmq-host=amqp # ①
rabbitmq-port=5672 # ②
rabbitmq-username=my-username # ③
rabbitmq-password=my-password # ④

mp.messaging.incoming.prices.connector=smallrye-rabbitmq # ⑤
```
1. Configures the broker host name. You can do it per channel (using the `host` attribute) or globally using `rabbitmq-host`
2. Configures the broker port. You can do it per channel (using the `port` attribute) or globally using `rabbitmq-port`. The default is `5672`.
3. Configures the broker username if required. You can do it per channel (using the `username` attribute) or globally using `rabbitmq-username`.
4. Configures the broker password if required. You can do it per channel (using the `password` attribute) or globally using `rabbitmq-password`.
5. Instructs the prices channel to be managed by the RabbitMQ connector

In dev mode and when running tests, [Dev Services for RabbitMQ](rabbitmq-dev-services.md) automatically starts a RabbitMQ broker.

## Receiving RabbitMQ messages

Let’s imagine your application receives `Message<Double>`.
You can consume the payload directly:

```java
package inbound;

import org.eclipse.microprofile.reactive.messaging.Incoming;

import jakarta.enterprise.context.ApplicationScoped;

@ApplicationScoped
public class RabbitMQPriceConsumer {

    @Incoming("prices")
    public void consume(double price) {
        // process your price.
    }

}
```

Or, you can retrieve the Message&lt;Double>:

```java
package inbound;

import org.eclipse.microprofile.reactive.messaging.Incoming;
import org.eclipse.microprofile.reactive.messaging.Message;

import jakarta.enterprise.context.ApplicationScoped;
import java.util.concurrent.CompletionStage;

@ApplicationScoped
public class RabbitMQPriceMessageConsumer {

    @Incoming("prices")
    public CompletionStage<Void> consume(Message<Double> price) {
        // process your price.

        // Acknowledge the incoming message, marking the RabbitMQ message as `accepted`.
        return price.ack();
    }

}
```

### Inbound Metadata
Messages coming from RabbitMQ contain an instance of `IncomingRabbitMQMetadata` in the metadata.

```java
Optional<IncomingRabbitMQMetadata> metadata = incoming.getMetadata(IncomingRabbitMQMetadata.class);
metadata.ifPresent(meta -> {
    final Optional<String> contentEncoding = meta.getContentEncoding();
    final Optional<String> contentType = meta.getContentType();
    final Optional<String> correlationId = meta.getCorrelationId();
    final Optional<ZonedDateTime> creationTime = meta.getCreationTime(ZoneId.systemDefault());
    final Optional<Integer> priority = meta.getPriority();
    final Optional<String> replyTo = meta.getReplyTo();
    final Optional<String> userId = meta.getUserId();

    // Access a single String-valued header
    final Optional<String> stringHeader = meta.getHeader("my-header", String.class);

    // Access all headers
    final Map<String,Object> headers = meta.getHeaders();
    // ...
});
```

### Deserialization

The connector converts incoming RabbitMQ Messages into Reactive Messaging `Message<T>` instances. The payload type `T` depends on the value of the RabbitMQ received message Envelope `content_type` and `content_encoding` properties.

|     |     |     |
| --- | --- | --- |
| content_encoding | content_type | T |
| _Value present_ | _n/a_ | `byte[]` |
| _No value_ | `text/plain` | `String` |
| _No value_ | `application/json` | a JSON element which can be a [`JsonArray`](https://vertx.io/docs/apidocs/io/vertx/core/json/JsonArray.html), [`JsonObject`](https://vertx.io/docs/apidocs/io/vertx/core/json/JsonObject.html), `String`, ...etc if the buffer contains an array, object, string, ...etc |
| _No value_ | _Anything else_ | `byte[]` |

If you send objects with this RabbitMQ connector (outbound connector), they are encoded as JSON and sent with `content_type` set to `application/json`. You can receive this payload using (Vert.x) JSON Objects, and then map it to the object class you want:

```java
@ApplicationScoped
public static class Generator {

    @Outgoing("to-rabbitmq")
    public Multi<Price> prices() { // ①
        AtomicInteger count = new AtomicInteger();
        return Multi.createFrom().ticks().every(Duration.ofMillis(1000))
                .map(l -> new Price().setPrice(count.incrementAndGet()))
                .onOverflow().drop();
    }

}

@ApplicationScoped
public static class Consumer {

    List<Price> prices = new CopyOnWriteArrayList<>();

    @Incoming("from-rabbitmq")
    public void consume(JsonObject p) { // ②
        Price price = p.mapTo(Price.class); // ③
        prices.add(price);
    }

    public List<Price> list() {
        return prices;
    }
}
```
1. The `Price` instances are automatically encoded to JSON by the connector
2. You can receive it using a `JsonObject`
3. Then, you can reconstruct the instance using the `mapTo` method

**📌 NOTE**\
The `mapTo` method uses the Quarkus Jackson mapper. Check [this guide](../02-web-http/rest-json.md#json) to learn more about the mapper configuration.

### Acknowledgement

When a Reactive Messaging Message associated with a RabbitMQ Message is acknowledged, it informs the broker that the message has been _accepted_.

Whether you need to explicitly acknowledge the message depends on the `auto-acknowledgement` setting for the channel; if that is set to true then your message will be automatically acknowledged on receipt.

### Failure Management

If a message produced from a RabbitMQ message is nacked, a failure strategy is applied. The RabbitMQ connector supports
three strategies, controlled by the failure-strategy channel setting:

* `fail` - fail the application; no more RabbitMQ messages will be processed. The RabbitMQ message is marked as rejected.
* `accept` - this strategy marks the RabbitMQ message as _accepted_. The processing continues, ignoring the failure.
* `reject` - this strategy marks the RabbitMQ message as rejected (default). The processing continues with the next message.

## Sending RabbitMQ messages

### Serialization

When sending a `Message<T>`, the connector converts the message into a RabbitMQ Message. The payload is converted to the RabbitMQ Message body.

|     |     |
| --- | --- |
| T	 | RabbitMQ Message Body |
| primitive types or `UUID`/`String` | String value with `content_type` set to `text/plain` |
| [`JsonObject`](https://vertx.io/docs/apidocs/io/vertx/core/json/JsonObject.html) or [`JsonArray`](https://vertx.io/docs/apidocs/io/vertx/core/json/JsonArray.html) | Serialized String payload with `content_type` set to `application/json` |
| `io.vertx.mutiny.core.buffer.Buffer` | Binary content, with `content_type` set to `application/octet-stream` |
| `byte[]` | Binary content, with `content_type` set to `application/octet-stream` |
| Any other class | The payload is converted to JSON (using a Json Mapper) then serialized with `content_type` set to `application/json` |

If the message payload cannot be serialized to JSON, the message is _nacked_.

### Outbound Metadata

When sending `Messages`, you can add an instance of `OutgoingRabbitMQMetadata`
to influence how the message is handled by RabbitMQ. For example, you can configure the routing key, timestamp and
headers:

```java
final OutgoingRabbitMQMetadata metadata = new OutgoingRabbitMQMetadata.Builder()
        .withHeader("my-header", "xyzzy")
        .withRoutingKey("urgent")
        .withTimestamp(ZonedDateTime.now())
        .build();

// Add `metadata` to the metadata of the outgoing message.
return Message.of("Hello", Metadata.of(metadata));
```

### Acknowledgement

By default, the Reactive Messaging `Message` is acknowledged when the broker acknowledges the message.

## Configuring the RabbitMQ Exchange/Queue

You can configure the RabbitMQ exchange or queue associated with a channel using properties on the channel configuration.
`incoming` channels are mapped to RabbitMQ `queues` and `outgoing` channels are mapped to `RabbitMQ` exchanges.
For example:

```properties
mp.messaging.incoming.prices.connector=smallrye-rabbitmq
mp.messaging.incoming.prices.queue.name=my-queue

mp.messaging.outgoing.orders.connector=smallrye-rabbitmq
mp.messaging.outgoing.orders.exchange.name=my-order-queue
```

If the `exchange.name` or `queue.name` attribute is not set, the connector uses the channel name.

To use an existing queue, you need to configure the `name` and set the exchange’s or queue’s `declare` property to `false`.
For example, if you have a RabbitMQ broker configured with a `people` exchange and queue, you need the following configuration:

```properties
mp.messaging.incoming.people.connector=smallrye-rabbitmq
mp.messaging.incoming.people.queue.name=people
mp.messaging.incoming.people.queue.declare=false

mp.messaging.outgoing.people.connector=smallrye-rabbitmq
mp.messaging.outgoing.people.exchange.name=people
mp.messaging.outgoing.people.exchange.declare=false
```

### Execution model and Blocking processing

Reactive Messaging invokes your method on an I/O thread.
See the [Quarkus Reactive Architecture documentation](../01-fundamentos/quarkus-reactive-architecture.md) for further details on this topic.
But, you often need to combine Reactive Messaging with blocking processing such as database interactions.
For this, you need to use the `@Blocking` annotation indicating that the processing is _blocking_ and should not be run on the caller thread.

For example, The following code illustrates how you can store incoming payloads to a database using Hibernate with Panache:

```java
import io.smallrye.reactive.messaging.annotations.Blocking;
import org.eclipse.microprofile.reactive.messaging.Incoming;

import jakarta.enterprise.context.ApplicationScoped;
import jakarta.transaction.Transactional;

@ApplicationScoped
public class PriceStorage {

    @Incoming("prices")
    @Blocking
    @Transactional
    public void store(int priceInUsd) {
        Price price = new Price();
        price.value = priceInUsd;
        price.persist();
    }

}
```

<dl><dt><strong>📌 NOTE</strong></dt><dd>

There are 2 `@Blocking` annotations:

1. `io.smallrye.reactive.messaging.annotations.Blocking`
2. `io.smallrye.common.annotation.Blocking`

They have the same effect.
Thus, you can use both.
The first one provides more fine-grained tuning such as the worker pool to use and whether it preserves the order.
The second one, used also with other reactive features of Quarkus, uses the default worker pool and preserves the order.
</dd></dl>

<dl><dt><strong>💡 TIP: @RunOnVirtualThread</strong></dt><dd>

For running the blocking processing on Java _virtual threads_, see the [Quarkus Virtual Thread support with Reactive Messaging documentation](messaging-virtual-threads.md).
</dd></dl>

## Customizing the underlying RabbitMQ client

The connector uses the Vert.x RabbitMQ client underneath.
More details about this client can be found in the [Vert.x website](https://vertx.io/docs/vertx-rabbitmq-client/java/).

You can customize the underlying client configuration by producing an instance of `RabbitMQOptions` as follows:

```java
@Produces
@Identifier("my-named-options")
public RabbitMQOptions getNamedOptions() {
  PemKeyCertOptions keycert = new PemKeyCertOptions()
        .addCertPath("./tls/tls.crt")
        .addKeyPath("./tls/tls.key");
  PemTrustOptions trust = new PemTrustOptions().addCertPath("./tlc/ca.crt");
  // You can use the produced options to configure the TLS connection
  return new RabbitMQOptions()
        .setSsl(true)
        .setPemKeyCertOptions(keycert)
        .setPemTrustOptions(trust)
        .setUser("user1")
        .setPassword("password1")
        .setHost("localhost")
        .setPort(5672)
        .setVirtualHost("vhost1")
        .setConnectionTimeout(6000) // in milliseconds
        .setRequestedHeartbeat(60) // in seconds
        .setHandshakeTimeout(6000) // in milliseconds
        .setRequestedChannelMax(5)
        .setNetworkRecoveryInterval(500) // in milliseconds
        .setAutomaticRecoveryEnabled(true);
}
```

This instance is retrieved and used to configure the client used by the connector.
You need to indicate the name of the client using the `client-options-name` attribute:

```properties
mp.messaging.incoming.prices.client-options-name=my-named-options
```

## TLS Configuration

RabbitMQ Messaging extension integrates with the [Quarkus TLS registry](../08-rendimiento-nativo/tls-registry-reference.md) to configure the Vert.x RabbitMQ client.

To configure the TLS for a channel, you need to provide a named TLS configuration in the `application.properties`:

```properties
quarkus.tls.your-tls-config.trust-store.pem.certs=ca.crt,ca2.pem
# ...
mp.messaging.incoming.prices.tls-configuration-name=your-tls-config
```

## Health reporting

If you use the RabbitMQ connector with the `quarkus-smallrye-health` extension, it contributes to the readiness and liveness probes.
The RabbitMQ connector reports the readiness and liveness of each channel managed by the connector.

To disable health reporting, set the `health-enabled` attribute for the channel to false.

On the inbound side (receiving messages from RabbitMQ), the check verifies that the receiver is connected to the broker.

On the outbound side (sending records to RabbitMQ), the check verifies that the sender is not disconnected from the broker; the sender _may_ still be in an initialised state (connection not yet attempted), but this is regarded as live/ready.

Note that a message processing failure nacks the message, which is then handled by the `failure-strategy`.
It’s the responsibility of the `failure-strategy` to report the failure and influence the outcome of the checks.
The `fail` failure strategy reports the failure, and so the check will report the fault.

## Dynamic Credentials

Quarkus and the RabbitMQ connector support [Vault’s RabbitMQ secrets engine](https://www.vaultproject.io/docs/secrets/rabbitmq)
for generating short-lived dynamic credentials. This allows Vault to create and retire RabbitMQ credentials on a regular basis.

First we need to enable Vault’s `rabbitmq` secret engine, configure it with RabbitMQ’s connection and authentication
information, and create a Vault role `my-role` (replace `10.0.0.3` by the actual host that is running the
RabbitMQ container):
```bash
vault secrets enable rabbitmq

vault write rabbitmq/config/connection \
    connection_uri=http://10.0.0.3:15672 \
    username=guest \
    password=guest

vault write rabbitmq/roles/my-role \
    vhosts='{"/":{"write": ".*", "read": ".*"}}'
```

<dl><dt><strong>📌 NOTE</strong></dt><dd>

For this use case, user `guest` configured above needs to be a RabbitMQ admin user with the capability to create
credentials.
</dd></dl>

Then we need to give a read capability to the Quarkus application on path `rabbitmq/creds/my-role`.
```bash
cat <<EOF | vault policy write vault-rabbitmq-policy -
path "secret/data/myapps/vault-rabbitmq-test/*" {
  capabilities = ["read"]
}
path "rabbitmq/creds/my-role" {
  capabilities = [ "read" ]
}
EOF
```

Now that Vault knows how to create users in RabbitMQ, we need to configure Quarkus to use a credentials-provider
for RabbitMQ.

First we tell Quarkus to request dynamic credentials using a credentials-provider named `rabbitmq`.
```
quarkus.rabbitmq.credentials-provider = rabbitmq
```

Next we configure the `rabbitmq` credentials provider. The `credentials-role` option must be set to the name of the
role we created in Vault, in our case `my-role`. The `credentials-mount` option must be set to `rabbitmq`.
```properties
quarkus.vault.credentials-provider.rabbitmq.credentials-role=my-role
quarkus.vault.credentials-provider.rabbitmq.credentials-mount=rabbitmq
```

**📌 NOTE**\
The `credentials-mount` is used directly as the mount of the secret engine in Vault. Here we are using
the default mount path of `rabbitmq`. If the RabbitMQ secret engine was mounted at a custom path, the
`credentials-mount` option must be set to that path instead.

## RabbitMQ Connector Configuration Reference

### Incoming channel configuration

| Attribute (_alias_) | Description | Mandatory | Default |
| --- | --- | --- | --- |
| **username** _(rabbitmq-username)_ | The username used to authenticate to the broker Type: _string_ | false |  |
| **password** _(rabbitmq-password)_ | The password used to authenticate to the broker Type: _string_ | false |  |
| **host** _(rabbitmq-host)_ | The broker hostname Type: _string_ | false | `localhost` |
| **port** _(rabbitmq-port)_ | The broker port Type: _int_ | false | `5672` |
| **ssl** _(rabbitmq-ssl)_ | Whether the connection should use SSL Type: _boolean_ | false | `false` |
| **trust-all** _(rabbitmq-trust-all)_ | Whether to skip trust certificate verification Type: _boolean_ | false | `false` |
| **trust-store-path** _(rabbitmq-trust-store-path)_ | The path to a JKS trust store Type: _string_ | false |  |
| **trust-store-password** _(rabbitmq-trust-store-password)_ | The password of the JKS trust store Type: _string_ | false |  |
| **credentials-provider-name** _(rabbitmq-credentials-provider-name)_ | The name of the RabbitMQ Credentials Provider bean used to provide dynamic credentials to the RabbitMQ client Type: _string_ | false |  |
| **connection-timeout** | The TCP connection timeout (ms); 0 is interpreted as no timeout Type: _int_ | false | `60000` |
| **handshake-timeout** | The AMQP 0-9-1 protocol handshake timeout (ms) Type: _int_ | false | `10000` |
| **automatic-recovery-enabled** | Whether automatic connection recovery is enabled Type: _boolean_ | false | `false` |
| **automatic-recovery-on-initial-connection** | Whether automatic recovery on initial connections is enabled Type: _boolean_ | false | `true` |
| **reconnect-attempts** _(rabbitmq-reconnect-attempts)_ | The number of reconnection attempts Type: _int_ | false | `100` |
| **reconnect-interval** _(rabbitmq-reconnect-interval)_ | The interval (in seconds) between two reconnection attempts Type: _int_ | false | `10` |
| **network-recovery-interval** | How long (ms) will automatic recovery wait before attempting to reconnect Type: _int_ | false | `5000` |
| **user** | The AMQP username to use when connecting to the broker Type: _string_ | false | `guest` |
| **include-properties** | Whether to include properties when a broker message is passed on the event bus Type: _boolean_ | false | `false` |
| **requested-channel-max** | The initially requested maximum channel number Type: _int_ | false | `2047` |
| **requested-heartbeat** | The initially requested heartbeat interval (seconds), zero for none Type: _int_ | false | `60` |
| **use-nio** | Whether usage of NIO Sockets is enabled Type: _boolean_ | false | `false` |
| **virtual-host** _(rabbitmq-virtual-host)_ | The virtual host to use when connecting to the broker Type: _string_ | false | `/` |
| **exchange.name** | The exchange that messages are published to or consumed from. If not set, the channel name is used. If set to `""`, the default exchange is used Type: _string_ | false |  |
| **exchange.durable** | Whether the exchange is durable Type: _boolean_ | false | `true` |
| **exchange.auto-delete** | Whether the exchange should be deleted after use Type: _boolean_ | false | `false` |
| **exchange.type** | The exchange type: direct, fanout, headers or topic (default) Type: _string_ | false | `topic` |
| **exchange.declare** | Whether to declare the exchange; set to false if the exchange is expected to be set up independently Type: _boolean_ | false | `true` |
| **tracing.enabled** | Whether tracing is enabled (default) or disabled Type: _boolean_ | false | `true` |
| **tracing.attribute-headers** | A comma-separated list of headers that should be recorded as span attributes. Relevant only if tracing.enabled=true Type: _string_ | false | `` |
| **queue.name** | The queue from which messages are consumed. Type: _string_ | true |  |
| **queue.durable** | Whether the queue is durable Type: _boolean_ | false | `true` |
| **queue.exclusive** | Whether the queue is for exclusive use Type: _boolean_ | false | `false` |
| **queue.auto-delete** | Whether the queue should be deleted after use Type: _boolean_ | false | `false` |
| **queue.declare** | Whether to declare the queue and binding; set to false if these are expected to be set up independently Type: _boolean_ | false | `true` |
| **queue.ttl** | If specified, the time (ms) for which a message can remain in the queue undelivered before it is dead Type: _long_ | false |  |
| **queue.single-active-consumer** | If set to true, only one consumer can actively consume messages Type: _boolean_ | false | `false` |
| **queue.x-queue-type** | If automatically declare queue, we can choose different types of queue [quorum, classic, stream] Type: _string_ | false | `classic` |
| **queue.x-queue-mode** | If automatically declare queue, we can choose different modes of queue [lazy, default] Type: _string_ | false | `default` |
| **max-incoming-internal-queue-size** | The maximum size of the incoming internal queue Type: _int_ | false |  |
| **connection-count** | The number of RabbitMQ connections to create for consuming from this queue. This might be necessary to consume from a sharded queue with a single client. Type: _int_ | false | `1` |
| **auto-bind-dlq** | Whether to automatically declare the DLQ and bind it to the binder DLX Type: _boolean_ | false | `false` |
| **dead-letter-queue-name** | The name of the DLQ; if not supplied will default to the queue name with '.dlq' appended Type: _string_ | false |  |
| **dead-letter-exchange** | A DLX to assign to the queue. Relevant only if auto-bind-dlq is true Type: _string_ | false | `DLX` |
| **dead-letter-exchange-type** | The type of the DLX to assign to the queue. Relevant only if auto-bind-dlq is true Type: _string_ | false | `direct` |
| **dead-letter-routing-key** | A dead letter routing key to assign to the queue; if not supplied will default to the queue name Type: _string_ | false |  |
| **dlx.declare** | Whether to declare the dead letter exchange binding. Relevant only if auto-bind-dlq is true; set to false if these are expected to be set up independently Type: _boolean_ | false | `false` |
| **dead-letter-queue-type** | If automatically declare DLQ, we can choose different types of DLQ [quorum, classic, stream] Type: _string_ | false | `classic` |
| **dead-letter-queue-mode** | If automatically declare DLQ, we can choose different modes of DLQ [lazy, default] Type: _string_ | false | `default` |
| **failure-strategy** | The failure strategy to apply when a RabbitMQ message is nacked. Accepted values are `fail`, `accept`, `reject` (default) Type: _string_ | false | `reject` |
| **broadcast** | Whether the received RabbitMQ messages must be dispatched to multiple _subscribers_ Type: _boolean_ | false | `false` |
| **auto-acknowledgement** | Whether the received RabbitMQ messages must be acknowledged when received; if true then delivery constitutes acknowledgement Type: _boolean_ | false | `false` |
| **keep-most-recent** | Whether to discard old messages instead of recent ones Type: _boolean_ | false | `false` |
| **routing-keys** | A comma-separated list of routing keys to bind the queue to the exchange Type: _string_ | false | `#` |
| **content-type-override** | Override the content_type attribute of the incoming message, should be a valid MIME type Type: _string_ | false |  |
| **max-outstanding-messages** | The maximum number of outstanding/unacknowledged messages being processed by the connector at a time; must be a positive number Type: _int_ | false |  |

### Outgoing channel configuration

| Attribute (_alias_) | Description | Mandatory | Default |
| --- | --- | --- | --- |
| **automatic-recovery-enabled** | Whether automatic connection recovery is enabled Type: _boolean_ | false | `false` |
| **automatic-recovery-on-initial-connection** | Whether automatic recovery on initial connections is enabled Type: _boolean_ | false | `true` |
| **connection-timeout** | The TCP connection timeout (ms); 0 is interpreted as no timeout Type: _int_ | false | `60000` |
| **default-routing-key** | The default routing key to use when sending messages to the exchange Type: _string_ | false | `` |
| **default-ttl** | If specified, the time (ms) sent messages can remain in queues undelivered before they are dead Type: _long_ | false |  |
| **exchange.auto-delete** | Whether the exchange should be deleted after use Type: _boolean_ | false | `false` |
| **exchange.declare** | Whether to declare the exchange; set to false if the exchange is expected to be set up independently Type: _boolean_ | false | `true` |
| **exchange.durable** | Whether the exchange is durable Type: _boolean_ | false | `true` |
| **exchange.name** | The exchange that messages are published to or consumed from. If not set, the channel name is used. If set to `""`, the default exchange is used Type: _string_ | false |  |
| **exchange.type** | The exchange type: direct, fanout, headers or topic (default) Type: _string_ | false | `topic` |
| **handshake-timeout** | The AMQP 0-9-1 protocol handshake timeout (ms) Type: _int_ | false | `10000` |
| **host** _(rabbitmq-host)_ | The broker hostname Type: _string_ | false | `localhost` |
| **include-properties** | Whether to include properties when a broker message is passed on the event bus Type: _boolean_ | false | `false` |
| **max-inflight-messages** | The maximum number of messages to be written to RabbitMQ concurrently; must be a positive number Type: _long_ | false | `1024` |
| **max-outgoing-internal-queue-size** | The maximum size of the outgoing internal queue Type: _int_ | false |  |
| **network-recovery-interval** | How long (ms) will automatic recovery wait before attempting to reconnect Type: _int_ | false | `5000` |
| **password** _(rabbitmq-password)_ | The password used to authenticate to the broker Type: _string_ | false |  |
| **port** _(rabbitmq-port)_ | The broker port Type: _int_ | false | `5672` |
| **reconnect-attempts** _(rabbitmq-reconnect-attempts)_ | The number of reconnection attempts Type: _int_ | false | `100` |
| **reconnect-interval** _(rabbitmq-reconnect-interval)_ | The interval (in seconds) between two reconnection attempts Type: _int_ | false | `10` |
| **requested-channel-max** | The initially requested maximum channel number Type: _int_ | false | `2047` |
| **requested-heartbeat** | The initially requested heartbeat interval (seconds), zero for none Type: _int_ | false | `60` |
| **ssl** _(rabbitmq-ssl)_ | Whether the connection should use SSL Type: _boolean_ | false | `false` |
| **tracing.attribute-headers** | A comma-separated list of headers that should be recorded as span attributes. Relevant only if tracing.enabled=true Type: _string_ | false | `` |
| **tracing.enabled** | Whether tracing is enabled (default) or disabled Type: _boolean_ | false | `true` |
| **trust-all** _(rabbitmq-trust-all)_ | Whether to skip trust certificate verification Type: _boolean_ | false | `false` |
| **trust-store-password** _(rabbitmq-trust-store-password)_ | The password of the JKS trust store Type: _string_ | false |  |
| **trust-store-path** _(rabbitmq-trust-store-path)_ | The path to a JKS trust store Type: _string_ | false |  |
| **credentials-provider-name** _(rabbitmq-credentials-provider-name)_ | The name of the RabbitMQ Credentials Provider bean used to provide dynamic credentials to the RabbitMQ client Type: _string_ | false |  |
| **use-nio** | Whether usage of NIO Sockets is enabled Type: _boolean_ | false | `false` |
| **user** | The AMQP username to use when connecting to the broker Type: _string_ | false | `guest` |
| **username** _(rabbitmq-username)_ | The username used to authenticate to the broker Type: _string_ | false |  |
| **virtual-host** _(rabbitmq-virtual-host)_ | The virtual host to use when connecting to the broker Type: _string_ | false | `/` |
