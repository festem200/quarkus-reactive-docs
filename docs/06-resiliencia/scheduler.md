# Scheduling Periodic Tasks

> **Guia oficial:** <https://quarkus.io/guides/scheduler>  
> **Fuente:** `docs/src/main/asciidoc/scheduler.adoc` en [quarkusio/quarkus@3.38.2](https://github.com/quarkusio/quarkus/blob/3.38.2/docs/src/main/asciidoc/scheduler.adoc)  
> **Version documentada:** Quarkus 3.38.2 · **Sincronizado:** 2026-08-17 · **Licencia:** Apache-2.0

Modern applications often need to run specific tasks periodically.
In this guide, you learn how to schedule periodic tasks.

**💡 TIP**\
If you need a clustered scheduler use the [Quartz extension](quartz.md).

## Prerequisites

To complete this guide, you need:

* Roughly 15 minutes
* An IDE
* JDK 17+ installed with `JAVA_HOME` configured appropriately
* Apache Maven 3.9.16
* Optionally the [Quarkus CLI](../10-extras/cli-tooling.md) if you want to use it
* Optionally Mandrel or GraalVM installed and [configured appropriately](../08-rendimiento-nativo/building-native-image.md#configuring-graalvm) if you want to build a native executable (or Docker if you use a native container build)

## Architecture

In this guide, we create a straightforward application accessible using HTTP to get the current value of a counter.
This counter is periodically (every 10 seconds) incremented.

![scheduling-task-architecture](../_assets/scheduling-task-architecture.png)

## Solution

We recommend that you follow the instructions in the next sections and create the application step by step.
However, you can go right to the completed example.

Clone the Git repository: `git clone https://github.com/quarkusio/quarkus-quickstarts.git`, or download an [archive](https://github.com/quarkusio/quarkus-quickstarts/archive/main.zip).

The solution is located in the `scheduler-quickstart` [directory](https://github.com/quarkusio/quarkus-quickstarts/tree/main/scheduler-quickstart).

## Creating the Maven project

First, we need a new project. Create a new project with the following command:

**CLI**

```bash
quarkus create app org.acme:scheduler-quickstart \
    --extension='rest,scheduler' \
    --no-code
cd scheduler-quickstart
```

To create a Gradle project, add the `--gradle` or `--gradle-kotlin-dsl` option.

For more information about how to install and use the Quarkus CLI, see the [Quarkus CLI](../10-extras/cli-tooling.md) guide.

**Maven**

```bash
mvn io.quarkus.platform:quarkus-maven-plugin:3.38.2:create \
    -DprojectGroupId=org.acme \
    -DprojectArtifactId=scheduler-quickstart \
    -Dextensions='rest,scheduler' \
    -DnoCode
cd scheduler-quickstart
```

To create a Gradle project, add the `-DbuildTool=gradle` or `-DbuildTool=gradle-kotlin-dsl` option.

For Windows users:

* If using cmd, (don’t use backward slash `\` and put everything on the same line)
* If using Powershell, wrap `-D` parameters in double quotes e.g. `"-DprojectArtifactId=scheduler-quickstart"`

It generates a new project including:

* a landing page accessible on `http://localhost:8080`
* example `Dockerfile` files for both `native` and `jvm` modes
* the application configuration file

The project also imports the Quarkus REST (formerly RESTEasy Reactive) and scheduler extensions.

If you already have your Quarkus project configured, you can add the `scheduler` extension
to your project by running the following command in your project base directory:

**CLI**

```bash
quarkus extension add scheduler
```
**Maven**

```bash
./mvnw quarkus:add-extension -Dextensions='scheduler'
```
**Gradle**

```bash
./gradlew addExtension --extensions='scheduler'
```

This will add the following to your build file:

**pom.xml**

```xml
<dependency>
    <groupId>io.quarkus</groupId>
    <artifactId>quarkus-scheduler</artifactId>
</dependency>
```

**build.gradle**

```gradle
implementation("io.quarkus:quarkus-scheduler")
```

## Creating a scheduled job

In the `org.acme.scheduler` package, create the `CounterBean` class, with the following content:

```java
package org.acme.scheduler;

import java.util.concurrent.atomic.AtomicInteger;
import jakarta.enterprise.context.ApplicationScoped;
import io.quarkus.scheduler.Scheduled;
import io.quarkus.scheduler.ScheduledExecution;

@ApplicationScoped              // ①
public class CounterBean {

    private AtomicInteger counter = new AtomicInteger();

    public int get() {  // ②
        return counter.get();
    }

    @Scheduled(every="10s")     // ③
    void increment() {
        counter.incrementAndGet(); // ④
    }

    @Scheduled(cron="0 15 10 * * ?") ⑤
    void cronJob(ScheduledExecution execution) {
        counter.incrementAndGet();
        System.out.println(execution.getScheduledFireTime());
    }

    @Scheduled(cron = "{cron.expr}") ⑥
    void cronJobWithExpressionInConfig() {
       counter.incrementAndGet();
       System.out.println("Cron expression configured in application.properties");
    }
}
```
1. Declare the bean in the _application_ scope
2. The `get()` method allows retrieving the current value.
3. Use the `@Scheduled` annotation to instruct Quarkus to run this method every 10 seconds provided a worker thread is available
(Quarkus is using 10 worker threads for the scheduler). If it is not available the method invocation should be re-scheduled by default i.e.
it should be invoked as soon as possible. The invocation of the scheduled method does not depend on the status or result of the previous invocation.
4. The code is pretty straightforward. Every 10 seconds, the counter is incremented.
5. Define a job with a cron-like expression. The annotated method is executed at 10:15am every day.
6. Define a job with a cron-like expression `cron.expr` which is configurable in `application.properties`.

## Updating the application configuration file

Edit the `application.properties` file and add the `cron.expr` configuration:
```properties
# By default, the syntax used for cron expressions is based on Quartz - https://www.quartz-scheduler.org/documentation/quartz-2.3.0/tutorials/crontrigger.html
# You can change the syntax using the following property:
# quarkus.scheduler.cron-type=unix
cron.expr=*/5 * * * * ?
```

## Creating the REST resource

Create the `CountResource` class as follows:

```java
package org.acme.scheduler;

import jakarta.inject.Inject;
import jakarta.ws.rs.GET;
import jakarta.ws.rs.Path;
import jakarta.ws.rs.Produces;
import jakarta.ws.rs.core.MediaType;

@Path("/count")
public class CountResource {

    @Inject
    CounterBean counter;            // ①

    @GET
    @Produces(MediaType.TEXT_PLAIN)
    public String hello() {
        return "count: " + counter.get();  // ②
    }
}
```
1. Inject the `CounterBean`
2. Send back the current counter value

## Package and run the application

Run the application with:

**CLI**

```bash
quarkus dev
```
**Maven**

```bash
./mvnw quarkus:dev
```
**Gradle**

```bash
./gradlew --console=plain quarkusDev
```

In another terminal, run `curl localhost:8080/count` to check the counter value.
After a few seconds, re-run `curl localhost:8080/count` to verify the counter has been incremented.

Observe the console to verify that the message `Cron expression configured in application.properties` has been displayed indicating
that the cron job using an expression configured in `application.properties` has been triggered.

As usual, the application can be packaged using:

**CLI**

```bash
quarkus build
```
**Maven**

```bash
./mvnw install
```
**Gradle**

```bash
./gradlew build
```

And executed with `java -jar target/quarkus-app/quarkus-run.jar`.

You can also generate the native executable with:

**CLI**

```bash
quarkus build --native
```
**Maven**

```bash
./mvnw install -Dnative
```
**Gradle**

```bash
./gradlew build -Dquarkus.native.enabled=true
```

## Scheduler Configuration Reference

**📌 NOTE**\
La tabla de configuracion generada `quarkus-scheduler` se produce al construir la documentacion y no existe en el codigo fuente. Consulta la referencia de configuracion en https://quarkus.io/guides/all-config
