# Scheduling Periodic Tasks with Quartz

> **Guia oficial:** <https://quarkus.io/guides/quartz>  
> **Fuente:** `docs/src/main/asciidoc/quartz.adoc` en [quarkusio/quarkus@3.38.2](https://github.com/quarkusio/quarkus/blob/3.38.2/docs/src/main/asciidoc/quartz.adoc)  
> **Version documentada:** Quarkus 3.38.2 · **Sincronizado:** 2026-08-17 · **Licencia:** Apache-2.0

Modern applications often need to run specific tasks periodically.
In this guide, you learn how to schedule periodic clustered tasks using the [Quartz](http://www.quartz-scheduler.org/) extension.

**💡 TIP**\
If you only need to run in-memory scheduler use the [Scheduler](scheduler.md) extension.

## Prerequisites

To complete this guide, you need:

* Roughly 15 minutes
* An IDE
* JDK 17+ installed with `JAVA_HOME` configured appropriately
* Apache Maven 3.9.16
* Docker and Docker Compose or [Podman](https://quarkus.io/guides/podman), and Docker Compose
* Optionally the [Quarkus CLI](../10-extras/cli-tooling.md) if you want to use it
* Optionally Mandrel or GraalVM installed and [configured appropriately](../08-rendimiento-nativo/building-native-image.md#configuring-graalvm) if you want to build a native executable (or Docker if you use a native container build)

## Architecture

In this guide, we are going to expose one Rest API `tasks` to visualise the list of tasks created by a Quartz job running every 10 seconds.

## Solution

We recommend that you follow the instructions in the next sections and create the application step by step.
However, you can go right to the completed example.

Clone the Git repository: `git clone https://github.com/quarkusio/quarkus-quickstarts.git`, or download an [archive](https://github.com/quarkusio/quarkus-quickstarts/archive/main.zip).

The solution is located in the `quartz-quickstart` [directory](https://github.com/quarkusio/quarkus-quickstarts/tree/main/quartz-quickstart).

## Creating the Maven project

First, we need a new project. Create a new project with the following command:

**CLI**

```bash
quarkus create app org.acme:quartz-quickstart \
    --extension='rest-jackson,quartz,hibernate-orm-panache,flyway,jdbc-postgresql' \
    --no-code
cd quartz-quickstart
```

To create a Gradle project, add the `--gradle` or `--gradle-kotlin-dsl` option.

For more information about how to install and use the Quarkus CLI, see the [Quarkus CLI](../10-extras/cli-tooling.md) guide.

**Maven**

```bash
mvn io.quarkus.platform:quarkus-maven-plugin:3.38.2:create \
    -DprojectGroupId=org.acme \
    -DprojectArtifactId=quartz-quickstart \
    -Dextensions='rest-jackson,quartz,hibernate-orm-panache,flyway,jdbc-postgresql' \
    -DnoCode
cd quartz-quickstart
```

To create a Gradle project, add the `-DbuildTool=gradle` or `-DbuildTool=gradle-kotlin-dsl` option.

For Windows users:

* If using cmd, (don’t use backward slash `\` and put everything on the same line)
* If using Powershell, wrap `-D` parameters in double quotes e.g. `"-DprojectArtifactId=quartz-quickstart"`

It generates:

* the Maven structure
* a landing page accessible on `http://localhost:8080`
* example `Dockerfile` files for both `native` and `jvm` modes
* the application configuration file

The Maven project also imports the Quarkus Quartz extension.

If you already have your Quarkus project configured, you can add the `quartz` extension
to your project by running the following command in your project base directory:

**CLI**

```bash
quarkus extension add quartz
```
**Maven**

```bash
./mvnw quarkus:add-extension -Dextensions='quartz'
```
**Gradle**

```bash
./gradlew addExtension --extensions='quartz'
```

This will add the following to your build file:

**pom.xml**

```xml
<dependency>
    <groupId>io.quarkus</groupId>
    <artifactId>quarkus-quartz</artifactId>
</dependency>
```

**build.gradle**

```gradle
implementation("io.quarkus:quarkus-quartz")
```

<dl><dt><strong>💡 TIP</strong></dt><dd>

To use a JDBC store, the `quarkus-agroal` extension, which provides the datasource support, is also required.
</dd></dl>

## Creating the Task Entity

In the `org.acme.quartz` package, create the `Task` class, with the following content:

```java
package org.acme.quartz;

import jakarta.persistence.Entity;
import java.time.Instant;
import jakarta.persistence.Table;

import io.quarkus.hibernate.orm.panache.PanacheEntity;

@Entity
@Table(name="TASKS")
public class Task extends PanacheEntity { ①
    public Instant createdAt;

    public Task() {
        createdAt = Instant.now();
    }

    public Task(Instant time) {
        this.createdAt = time;
    }
}
```
1. Declare the entity using [Panache](https://quarkus.io/guides/hibernate-orm-panache)

## Creating a scheduled job

In the `org.acme.quartz` package, create the `TaskBean` class, with the following content:

```java
package org.acme.quartz;

import jakarta.enterprise.context.ApplicationScoped;

import jakarta.transaction.Transactional;

import io.quarkus.scheduler.Scheduled;

@ApplicationScoped ①
public class TaskBean {

    @Transactional
    @Scheduled(every = "10s", identity = "task-job") ②
    void schedule() {
        Task task = new Task(); ③
        task.persist(); ④
    }
}
```
1. Declare the bean in the _application_ scope
2. Use the `@Scheduled` annotation to instruct Quarkus to run this method every 10 seconds and set the unique identifier for this job.
3. Create a new `Task` with the current start time.
4. Persist the task in database using [Panache](https://quarkus.io/guides/hibernate-orm-panache).

**💡 TIP**\
The `@Scheduled#description()` value, if set, is stored in the `DESCRIPTION` column of the `QRTZ_JOB_DETAILS` table.

### Scheduling Jobs Programmatically

An injected `io.quarkus.scheduler.Scheduler` can be used to [schedule a job programmatically](scheduler-reference.md#programmatic_scheduling).
However, it is also possible to leverage the Quartz API directly.
You can inject the underlying `org.quartz.Scheduler` in any bean:

```java
package org.acme.quartz;

@ApplicationScoped
public class TaskBean {

    @Inject
    org.quartz.Scheduler quartz; ①

    void onStart(@Observes StartupEvent event) throws SchedulerException {
       JobDetail job = JobBuilder.newJob(MyJob.class)
                         .withIdentity("myJob", "myGroup")
                         .build();
       Trigger trigger = TriggerBuilder.newTrigger()
                            .withIdentity("myTrigger", "myGroup")
                            .startNow()
                            .withSchedule(
                               SimpleScheduleBuilder.simpleSchedule()
                                  .withIntervalInSeconds(10)
                                  .repeatForever())
                            .build();
       quartz.scheduleJob(job, trigger); ②
    }

    @Transactional
    void performTask() {
        Task task = new Task();
        task.persist();
    }

    // A new instance of MyJob is created by Quartz for every job execution
    public static class MyJob implements Job {

       @Inject
       TaskBean taskBean;

       public void execute(JobExecutionContext context) throws JobExecutionException {
          taskBean.performTask(); ③
       }

    }
}
```
1. Inject the underlying `org.quartz.Scheduler` instance.
2. Schedule a new job using the Quartz API.
3. Invoke the `TaskBean#performTask()` method from the job. Jobs are also [container-managed](../01-fundamentos/cdi.md) beans if they belong to a [bean archive](../01-fundamentos/cdi-reference.md).

**📌 NOTE**\
By default, the scheduler is not started unless a `@Scheduled` business method is found. You may need to force the start of the scheduler for "pure" programmatic scheduling. See also [Quartz Configuration Reference](#quartz-configuration-reference).

## Updating the application configuration file

Edit the `application.properties` file and add the below configuration:
```properties
# Quartz configuration
quarkus.quartz.clustered=true ①
quarkus.quartz.store-type=jdbc-cmt ②
quarkus.quartz.misfire-policy.task-job=ignore-misfire-policy ③

# Datasource configuration.
quarkus.datasource.db-kind=postgresql
quarkus.datasource.username=quarkus_test
quarkus.datasource.password=quarkus_test
quarkus.datasource.jdbc.url=jdbc:postgresql://localhost/quarkus_test

# Hibernate configuration
quarkus.hibernate-orm.schema-management.strategy=none
quarkus.hibernate-orm.log.sql=true
quarkus.hibernate-orm.sql-load-script=no-file

# flyway configuration
quarkus.flyway.connect-retries=10
quarkus.flyway.table=flyway_quarkus_history
quarkus.flyway.migrate-at-start=true
quarkus.flyway.baseline-on-migrate=true
quarkus.flyway.baseline-version=1.0
quarkus.flyway.baseline-description=Quartz
```
1. Indicate that the scheduler will be run in clustered mode
2. Use the database store to persist job related information so that they can be shared between nodes
3. The misfire policy can be configured for each job. `task-job` is the identity of the job.

Valid misfire policy for cron jobs are: `smart-policy`, `ignore-misfire-policy`, `fire-now` and `cron-trigger-do-nothing`.
Valid misfire policy for interval jobs are: `smart-policy`, `ignore-misfire-policy`, `fire-now`, `simple-trigger-reschedule-now-with-existing-repeat-count`, `simple-trigger-reschedule-now-with-remaining-repeat-count`, `simple-trigger-reschedule-next-with-existing-count` and `simple-trigger-reschedule-next-with-remaining-count`.

## Creating a REST resource and a test

Create the `org.acme.quartz.TaskResource` class with the following content:

```java
package org.acme.quartz;

import java.util.List;

import jakarta.ws.rs.GET;
import jakarta.ws.rs.Path;
import jakarta.ws.rs.Produces;
import jakarta.ws.rs.core.MediaType;

@Path("/tasks")
public class TaskResource {

    @GET
    public List<Task> listAll() {
        return Task.listAll(); ①
    }
}
```
1. Retrieve the list of created tasks from the database

You also have the option to create a `org.acme.quartz.TaskResourceTest` test with the following content:

```java
package org.acme.quartz;

import io.quarkus.test.junit.QuarkusTest;

import static org.hamcrest.Matchers.greaterThanOrEqualTo;

import org.junit.jupiter.api.Test;

import static io.restassured.RestAssured.given;
import static org.hamcrest.CoreMatchers.is;

@QuarkusTest
public class TaskResourceTest {

    @Test
    public void tasks() throws InterruptedException {
        Thread.sleep(1000); // wait at least a second to have the first task created
        given()
                .when().get("/tasks")
                .then()
                .statusCode(200)
                .body("size()", is(greaterThanOrEqualTo(1))); ①
    }
}
```
1. Ensure that we have a `200` response and at least one task created

## Creating Quartz Tables

Add a SQL migration file named `src/main/resources/db/migration/V2.0.0\__QuarkusQuartzTasks.sql` with the content copied from
file with the content from [V2.0.0__QuarkusQuartzTasks.sql](https://github.com/quarkusio/quarkus-quickstarts/blob/main/quartz-quickstart/src/main/resources/db/migration/V2.0.0__QuarkusQuartzTasks.sql).

## Configuring the load balancer

In the root directory, create a `nginx.conf` file with the following content:

```conf
user  nginx;

events {
    worker_connections   1000;
}

http {
        server {
              listen 8080;
              location / {
                proxy_pass http://tasks:8080; ①
              }
        }
}
```
1. Route all traffic to our tasks application

## Setting Application Deployment

In the root directory, create a `docker-compose.yml` file with the following content:

```yaml
version: '3'

services:
  tasks: ①
    image: quarkus-quickstarts/quartz:1.0
    build:
      context: ./
      dockerfile: src/main/docker/Dockerfile.${QUARKUS_MODE:-jvm}
    environment:
      QUARKUS_DATASOURCE_URL: jdbc:postgresql://postgres/quarkus_test
    networks:
      - tasks-network
    depends_on:
      - postgres

  nginx: ②
    image: nginx:latest
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
    depends_on:
      - tasks
    ports:
      - 8080:8080
    networks:
      - tasks-network

  db: ③
    image: docker.io/library/postgres:18
    container_name: quarkus_test
    environment:
      - POSTGRES_USER=quarkus_test
      - POSTGRES_PASSWORD=quarkus_test
      - POSTGRES_DB=quarkus_test
    ports:
      - 5432:5432
    networks:
      - tasks-network

networks:
  tasks-network:
    driver: bridge
```
1. Define the tasks service
2. Define the nginx load balancer to route incoming traffic to an appropriate node
3. Define the configuration to run the database

## Running the database

In a separate terminal, run the below command:

```bash
docker-compose up postgres ①
```
1. Start the database instance using the configuration options supplied in the `docker-compose.yml` file

## Run the application in Dev Mode

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

After a few seconds, open another terminal and run `curl localhost:8080/tasks` to verify that we have at least one task created.

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

and executed with `java -jar target/quarkus-app/quarkus-run.jar`.

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

## Packaging the application and run several instances

The application can be packaged using:

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

Once the build is successful, run the below command:

```bash
docker-compose up --scale tasks=2 --scale nginx=1 ①
```
1. Start two instances of the application and a load balancer

After a few seconds, in another terminal, run `curl localhost:8080/tasks` to verify that tasks were only created at different instants and in an interval of 10 seconds.

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

**⚠️ WARNING**\
It’s the responsibility of the deployer to clear/remove the previous state, i.e. stale jobs and triggers. Moreover, the applications that form the "Quartz cluster" should be identical, otherwise an unpredictable result may occur.

## Configuring the Instance ID

By default, the scheduler is configured with a simple instance ID generator using the machine hostname and the current timestamp, so you don’t need to worry about setting a appropriate `instance-id` for each node when running in clustered mode. However, you can define a specific `instance-id` by yourself setting a configuration property reference or using other generators.

```properties
quarkus.quartz.instance-id=${HOST:AUTO} ①
```
1. This will expand the `HOST` environment variable and use `AUTO` as the default value if `HOST` is not set.

The example below configure the generator `org.quartz.simpl.HostnameInstanceIdGenerator` named as `hostname`, so you can use its name as `instance-id` to be used. That generator uses just the machine hostname and can be appropriate in environments providing unique names for the nodes.

```properties
quarkus.quartz.instance-id=hostname
quarkus.quartz.instance-id-generators.hostname.class=org.quartz.simpl.HostnameInstanceIdGenerator
```

**⚠️ WARNING**\
It’s the responsibility of the deployer to define appropriate instance identifiers. Moreover, the applications that form the "Quartz cluster" should contain unique instance identifiers, otherwise an unpredictable result may occur. It’s recommended to use an appropriate instance ID generator rather than specifying explicit identifiers.

## Registering Plugin and Listeners

You can register `plugins`, `job-listeners` and `trigger-listeners` through Quarkus configuration.

The example below registers the plugin `org.quartz.plugins.history.LoggingJobHistoryPlugin` named as `jobHistory` with the property `jobSuccessMessage` defined as `Job [{1}.{0}] execution complete and reports: {8}`

```properties
quarkus.quartz.plugins.jobHistory.class=org.quartz.plugins.history.LoggingJobHistoryPlugin
quarkus.quartz.plugins.jobHistory.properties.jobSuccessMessage=Job [{1}.{0}] execution complete and reports: {8}
```

You can also register a listener programmatically with an injected `org.quartz.Scheduler`:

```java
public class MyListenerManager {
    void onStart(@Observes StartupEvent event, org.quartz.Scheduler scheduler) throws SchedulerException {
        scheduler.getListenerManager().addJobListener(new MyJogListener());
        scheduler.getListenerManager().addTriggerListener(new MyTriggerListener());
    }
}
```

## Run scheduled methods on virtual threads

Methods annotated with `@Scheduled` can also be annotated with `@RunOnVirtualThread`.
In this case, the method is invoked on a virtual thread.

The method must return `void` and your Java runtime must provide support for virtual threads.
Read [the virtual thread guide](../01-fundamentos/virtual-threads.md) for more details.

**⚠️ WARNING**\
This feature cannot be combined with the `run-blocking-method-on-quartz-thread` option.
If `run-blocking-method-on-quartz-thread` is set, the scheduled method runs on a (platform) thread managed by Quartz.

## Quartz Configuration Reference

**📌 NOTE**\
La tabla de configuracion generada `quarkus-quartz` se produce al construir la documentacion y no existe en el codigo fuente. Consulta la referencia de configuracion en https://quarkus.io/guides/all-config
