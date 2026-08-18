# Centralized log management (Graylog, Logstash, Fluentd)

> **Guia oficial:** <https://quarkus.io/guides/centralized-log-management>  
> **Fuente:** `docs/src/main/asciidoc/centralized-log-management.adoc` en [quarkusio/quarkus@3.38.2](https://github.com/quarkusio/quarkus/blob/3.38.2/docs/src/main/asciidoc/centralized-log-management.adoc)  
> **Version documentada:** Quarkus 3.38.2 · **Sincronizado:** 2026-08-17 · **Licencia:** Apache-2.0

This guide explains how you can send your logs to a centralized log management system like Graylog, Logstash (inside the Elastic Stack or ELK - Elasticsearch, Logstash, Kibana) or
Fluentd (inside EFK - Elasticsearch, Fluentd, Kibana).

This document is part of the [Observability in Quarkus reference guide](observability.md) which features this and other observability related components.

There are a lot of different ways to centralize your logs (if you are using Kubernetes, the simplest way is to log to the console and ask your cluster administrator to integrate a central log manager inside your cluster).
In this guide, we will expose how to send them to an external tool using supported Quarkus extensions in supported standard formats like Graylog Extended Log Format (GELF), Elastic Common Schema (ECS) or the OpenTelemetry Log signal.

## Prerequisites

To complete this guide, you need:

* Roughly 15 minutes
* An IDE
* JDK 17+ installed with `JAVA_HOME` configured appropriately
* Apache Maven 3.9.16
* Docker and Docker Compose or [Podman](https://quarkus.io/guides/podman), and Docker Compose
* Optionally the [Quarkus CLI](../10-extras/cli-tooling.md) if you want to use it
* Optionally Mandrel or GraalVM installed and [configured appropriately](../08-rendimiento-nativo/building-native-image.md#configuring-graalvm) if you want to build a native executable (or Docker if you use a native container build)

## Example application

The following examples will all be based on the same example application that you can create with the following steps.

Create an application with the REST extension. You can use the following command to create it:

**CLI**

```bash
quarkus create app org.acme:centralized-logging \
    --extension='rest' \
    --no-code
cd centralized-logging
```

To create a Gradle project, add the `--gradle` or `--gradle-kotlin-dsl` option.

For more information about how to install and use the Quarkus CLI, see the [Quarkus CLI](../10-extras/cli-tooling.md) guide.

**Maven**

```bash
mvn io.quarkus.platform:quarkus-maven-plugin:3.38.2:create \
    -DprojectGroupId=org.acme \
    -DprojectArtifactId=centralized-logging \
    -Dextensions='rest' \
    -DnoCode
cd centralized-logging
```

To create a Gradle project, add the `-DbuildTool=gradle` or `-DbuildTool=gradle-kotlin-dsl` option.

For Windows users:

* If using cmd, (don’t use backward slash `\` and put everything on the same line)
* If using Powershell, wrap `-D` parameters in double quotes e.g. `"-DprojectArtifactId=centralized-logging"`

For demonstration purposes, we create an endpoint that does nothing but log a sentence. You don’t need to do this inside your application.

```java
import jakarta.enterprise.context.ApplicationScoped;
import jakarta.ws.rs.GET;
import jakarta.ws.rs.Path;

import org.jboss.logging.Logger;

@Path("/logging")
@ApplicationScoped
public class LoggingResource {
    private static final Logger LOG = Logger.getLogger(LoggingResource.class);

    @GET
    public void log() {
        LOG.info("Some useful log message");
    }

}
```

## Send logs to the Elastic Stack (ELK) in the ECS (Elastic Common Schema) format with the Socket handler

You can send your logs to Logstash using a TCP input in the [ECS](https://www.elastic.co/guide/en/ecs-logging/overview/current/intro.html) format.
To achieve this, we will use the `quarkus-logging-json` extension to format the logs in JSON format and the socket handler to send them to Logstash.

Create the following file  in `$HOME/pipelines/ecs.conf`:

```
input {
  tcp {
    port => 4560
    codec => json
  }
}

filter {
  if ![span][id] and [mdc][spanId] {
    mutate { rename => { "[mdc][spanId]" => "[span][id]" } }
  }
  if ![trace][id] and [mdc][traceId] {
    mutate { rename => {"[mdc][traceId]" => "[trace][id]"} }
  }
}

output {
  stdout {}
  elasticsearch {
    hosts => ["http://elasticsearch:9200"]
  }
}
```

Then configure your application to log in JSON format

**pom.xml**

```xml
<dependency>
    <groupId>io.quarkus</groupId>
    <artifactId>quarkus-logging-json</artifactId>
</dependency>
```

**build.gradle**

```gradle
implementation("io.quarkus:quarkus-logging-json")
```

and specify the host and port of your Logstash endpoint. To be ECS compliant, specify the log format.

```properties
# to keep the logs in the usual format in the console
quarkus.log.console.json.enabled=false

quarkus.log.socket.enable=true
quarkus.log.socket.json.enabled=true
quarkus.log.socket.endpoint=localhost:4560

# to have the exception serialized into a single text element
quarkus.log.socket.json.exception-output-type=formatted

# specify the format of the produced JSON log
quarkus.log.socket.json.log-format=ECS
```

Finally, launch the components that compose the Elastic Stack:

* Elasticsearch
* Logstash
* Kibana

You can do this via the following `docker-compose.yml` file that you can launch via `docker-compose up -d`:

```yaml
# Launch Elasticsearch
version: '3.2'

services:
  elasticsearch:
    image: docker.io/elastic/elasticsearch:9.4.1
    ports:
      - "9200:9200"
      - "9300:9300"
    environment:
      ES_JAVA_OPTS: "-Xms512m -Xmx512m"
      discovery.type: "single-node"
      cluster.routing.allocation.disk.threshold_enabled: false
    networks:
      - elk

  logstash:
    image: docker.io/elastic/logstash:9.4.1
    volumes:
      - source: $HOME/pipelines
        target: /usr/share/logstash/pipeline
        type: bind
    ports:
      - "12201:12201/udp"
      - "5000:5000"
      - "9600:9600"
    networks:
      - elk
    depends_on:
      - elasticsearch

  kibana:
    image: docker.io/elastic/kibana:9.4.1
    ports:
      - "5601:5601"
    networks:
      - elk
    depends_on:
      - elasticsearch

networks:
  elk:
    driver: bridge

```

Launch your application, you should see your logs arriving inside the Elastic Stack; you can use Kibana available at http://localhost:5601/ to access them.

## Send logs to Fluentd with the Syslog handler

You can send your logs to Fluentd using a Syslog input.
As opposed to the GELF input, the Syslog input will not render multiline logs in one event.

First, you need to create a Fluentd image with the Elasticsearch plugin.
You can use the following Dockerfile that should be created inside a `fluentd` directory.

```dockerfile
FROM fluent/fluentd:v1.3-debian
RUN ["gem", "install", "fluent-plugin-elasticsearch", "--version", "3.7.0"]
```

Then, you need to create a Fluentd configuration file inside `$HOME/fluentd/fluent.conf`

```
<source>
  @type syslog
  port 5140
  bind 0.0.0.0
  message_format rfc5424
  tag system
</source>

<match **>
  @type elasticsearch
  host elasticsearch
  port 9200
  logstash_format true
</match>
```

Then, launch the components that compose the EFK Stack:

* Elasticsearch
* Fluentd
* Kibana

You can do this via the following `docker-compose.yml` file that you can launch via `docker-compose up -d`:

```yaml
version: '3.2'

services:
  elasticsearch:
    image: docker.io/elastic/elasticsearch:9.4.1
    ports:
      - "9200:9200"
      - "9300:9300"
    environment:
      ES_JAVA_OPTS: "-Xms512m -Xmx512m"
      discovery.type: "single-node"
      cluster.routing.allocation.disk.threshold_enabled: false
    networks:
      - efk

  fluentd:
    build: fluentd
    ports:
      - "5140:5140/udp"
    volumes:
      - source: $HOME/fluentd
        target: /fluentd/etc
        type: bind
    networks:
      - efk
    depends_on:
      - elasticsearch

  kibana:
    image: docker.io/elastic/kibana:9.4.1
    ports:
      - "5601:5601"
    networks:
      - efk
    depends_on:
      - elasticsearch

networks:
  efk:
    driver: bridge
```

Finally, configure your application to send logs to EFK using Syslog:

```properties
quarkus.log.syslog.enable=true
quarkus.log.syslog.endpoint=localhost:5140
quarkus.log.syslog.protocol=udp
quarkus.log.syslog.app-name=quarkus
quarkus.log.syslog.hostname=quarkus-test
```

Launch your application, you should see your logs arriving inside EFK: you can use Kibana available at http://localhost:5601/ to access them.

## Send logs with OpenTelemetry Logging

OpenTelemetry Logging is able to send logs to a compatible OpenTelemetry collector. Its usage is described in the guide [Using OpenTelemetry Logging](opentelemetry-logging.md).

## Send logs with the `logging-gelf` extension

**⚠️ WARNING**\
This extension is deprecated, we advise considering the alternatives described above in this guide.

The `quarkus-logging-gelf` extension will add a GELF log handler to the underlying logging backend that Quarkus uses (jboss-logmanager).
By default, it is disabled, if you enable it but still use another handler (by default the console handler is enabled), your logs will be sent to both handlers.

You can add the `logging-gelf` extension to your project by running the following command in your project base directory:

**CLI**

```bash
quarkus extension add logging-gelf
```
**Maven**

```bash
./mvnw quarkus:add-extension -Dextensions='logging-gelf'
```
**Gradle**

```bash
./gradlew addExtension --extensions='logging-gelf'
```

This will add the following dependency to your build file:

**pom.xml**

```xml
<dependency>
    <groupId>io.quarkus</groupId>
    <artifactId>quarkus-logging-gelf</artifactId>
</dependency>
```

**build.gradle**

```gradle
implementation("io.quarkus:quarkus-logging-gelf")
```

Configure the GELF log handler to send logs to an external UDP endpoint on port 12201:

```properties
quarkus.log.handler.gelf.enabled=true
quarkus.log.handler.gelf.host=localhost
quarkus.log.handler.gelf.port=12201
```

### Send logs to Graylog

**📌 NOTE**\
It is advised to use the Syslog handler instead.

To send logs to Graylog, you first need to launch the components that compose the Graylog stack:

* MongoDB
* Elasticsearch
* Graylog

You can do this via the following `docker-compose.yml` file that you can launch via `docker-compose up -d`:

```yaml
version: '3.2'

services:
  elasticsearch:
    image: docker.io/elastic/elasticsearch:9.4.1
    ports:
      - "9200:9200"
    environment:
      ES_JAVA_OPTS: "-Xms512m -Xmx512m"
      discovery.type: "single-node"
      cluster.routing.allocation.disk.threshold_enabled: false
    networks:
      - graylog

  mongo:
    image: mongo:4.0
    networks:
      - graylog

  graylog:
    image: graylog/graylog:4.3.0
    ports:
      - "9000:9000"
      - "12201:12201/udp"
      - "1514:1514"
    environment:
      GRAYLOG_HTTP_EXTERNAL_URI: "http://127.0.0.1:9000/"
      # CHANGE ME (must be at least 16 characters)!
      GRAYLOG_PASSWORD_SECRET: "forpasswordencryption"
      # Password: admin
      GRAYLOG_ROOT_PASSWORD_SHA2: "8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918"
    networks:
      - graylog
    depends_on:
      - elasticsearch
      - mongo

networks:
  graylog:
    driver: bridge
```

Then, you need to create a UDP input in Graylog.
You can do it from the Graylog web console (System -> Input -> Select GELF UDP) available at http://localhost:9000 or via the API.

This curl example will create a new Input of type GELF UDP, it uses the default login from Graylog (admin/admin).

```bash
curl -H "Content-Type: application/json" -H "Authorization: Basic YWRtaW46YWRtaW4=" -H "X-Requested-By: curl" -X POST -v -d \
'{"title":"udp input","configuration":{"recv_buffer_size":262144,"bind_address":"0.0.0.0","port":12201,"decompress_size_limit":8388608},"type":"org.graylog2.inputs.gelf.udp.GELFUDPInput","global":true}' \
http://localhost:9000/api/system/inputs
```

Launch your application, you should see your logs arriving inside Graylog.

### Send logs to Logstash / the Elastic Stack (ELK)

**📌 NOTE**\
It is advised to use [OpenTelemetry Logging](opentelemetry-logging.md) or the Socket handler instead.

Logstash comes by default with an Input plugin that can understand the GELF format, we will first create a pipeline that enables this plugin.

Create the following file  in `$HOME/pipelines/gelf.conf`:

```
input {
  gelf {
    port => 12201
  }
}
output {
  stdout {}
  elasticsearch {
    hosts => ["http://elasticsearch:9200"]
  }
}
```

Finally, launch the components that compose the Elastic Stack:

* Elasticsearch
* Logstash
* Kibana

You can do this via the following `docker-compose.yml` file that you can launch via `docker-compose up -d`:

```yaml
# Launch Elasticsearch
version: '3.2'

services:
  elasticsearch:
    image: docker.io/elastic/elasticsearch:9.4.1
    ports:
      - "9200:9200"
      - "9300:9300"
    environment:
      ES_JAVA_OPTS: "-Xms512m -Xmx512m"
      discovery.type: "single-node"
      cluster.routing.allocation.disk.threshold_enabled: false
    networks:
      - elk

  logstash:
    image: docker.io/elastic/logstash:9.4.1
    volumes:
      - source: $HOME/pipelines
        target: /usr/share/logstash/pipeline
        type: bind
    ports:
      - "12201:12201/udp"
      - "5000:5000"
      - "9600:9600"
    networks:
      - elk
    depends_on:
      - elasticsearch

  kibana:
    image: docker.io/elastic/kibana:9.4.1
    ports:
      - "5601:5601"
    networks:
      - elk
    depends_on:
      - elasticsearch

networks:
  elk:
    driver: bridge

```

Launch your application, you should see your logs arriving inside the Elastic Stack; you can use Kibana available at http://localhost:5601/ to access them.

### Send logs to Fluentd (EFK)

**📌 NOTE**\
It is advised to use [OpenTelemetry Logging](opentelemetry-logging.md) or the Socket handler instead.

First, you need to create a Fluentd image with the needed plugins: elasticsearch and input-gelf.
You can use the following Dockerfile that should be created inside a `fluentd` directory.

```dockerfile
FROM fluent/fluentd:v1.3-debian
RUN ["gem", "install", "fluent-plugin-elasticsearch", "--version", "3.7.0"]
RUN ["gem", "install", "fluent-plugin-input-gelf", "--version", "0.3.1"]
```

You can build the image or let docker-compose build it for you.

Then you need to create a fluentd configuration file inside `$HOME/fluentd/fluent.conf`

```
<source>
  type gelf
  tag example.gelf
  bind 0.0.0.0
  port 12201
</source>

<match example.gelf>
  @type elasticsearch
  host elasticsearch
  port 9200
  logstash_format true
</match>
```

Finally, launch the components that compose the EFK Stack:

* Elasticsearch
* Fluentd
* Kibana

You can do this via the following `docker-compose.yml` file that you can launch via `docker-compose up -d`:

```yaml
version: '3.2'

services:
  elasticsearch:
    image: docker.io/elastic/elasticsearch:9.4.1
    ports:
      - "9200:9200"
      - "9300:9300"
    environment:
      ES_JAVA_OPTS: "-Xms512m -Xmx512m"
      discovery.type: "single-node"
      cluster.routing.allocation.disk.threshold_enabled: false
    networks:
      - efk

  fluentd:
    build: fluentd
    ports:
      - "12201:12201/udp"
    volumes:
      - source: $HOME/fluentd
        target: /fluentd/etc
        type: bind
    networks:
      - efk
    depends_on:
      - elasticsearch

  kibana:
    image: docker.io/elastic/kibana:9.4.1
    ports:
      - "5601:5601"
    networks:
      - efk
    depends_on:
      - elasticsearch

networks:
  efk:
    driver: bridge
```

Launch your application, you should see your logs arriving inside EFK: you can use Kibana available at http://localhost:5601/ to access them.

### Elasticsearch indexing consideration

Be careful that, by default, Elasticsearch will automatically map unknown fields (if not disabled in the index settings) by detecting their type.
This can become tricky if you use log parameters (which are included by default), or if you enable MDC inclusion (disabled by default),
as the first log will define the type of the message parameter (or MDC parameter) field inside the index.

Imagine the following case:

```java
LOG.info("some {} message {} with {} param", 1, 2, 3);
LOG.info("other {} message {} with {} param", true, true, true);
```

With log message parameters enabled, the first log message sent to Elasticsearch will have a `MessageParam0` parameter with an `int` type;
this will configure the index with a field of type `integer`.
When the second message will arrive to Elasticsearch, it will have a `MessageParam0` parameter with the boolean value `true`, and this will generate an indexing error.

To work around this limitation, you can disable sending log message parameters via `logging-gelf` by configuring `quarkus.log.handler.gelf.include-log-message-parameters=false`,
or you can configure your Elasticsearch index to store those fields as text or keyword, Elasticsearch will then automatically make the translation from int/boolean to a String.

See the following documentation for Graylog (but the same issue exists for the other central logging stacks): [Custom Index Mappings](https://docs.graylog.org/en/3.2/pages/configuration/elasticsearch.html#custom-index-mappings).

### Configuration Reference

Configuration is done through the usual `application.properties` file.

**📌 NOTE**\
La tabla de configuracion generada `quarkus-logging-gelf` se produce al construir la documentacion y no existe en el codigo fuente. Consulta la referencia de configuracion en https://quarkus.io/guides/all-config

This extension uses the `logstash-gelf` library that allow more configuration options via system properties,
you can access its documentation here: https://logging.paluch.biz/.
