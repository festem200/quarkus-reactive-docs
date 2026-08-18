# Reactive SQL Clients

> **Guia oficial:** <https://quarkus.io/guides/reactive-sql-clients>  
> **Fuente:** `docs/src/main/asciidoc/reactive-sql-clients.adoc` en [quarkusio/quarkus@3.38.2](https://github.com/quarkusio/quarkus/blob/3.38.2/docs/src/main/asciidoc/reactive-sql-clients.adoc)  
> **Version documentada:** Quarkus 3.38.2 · **Sincronizado:** 2026-08-17 · **Licencia:** Apache-2.0

The Reactive SQL Clients have a straightforward API focusing on scalability and low-overhead.
Currently, the following database servers are supported:

* IBM Db2
* PostgreSQL
* MariaDB/MySQL
* Microsoft SQL Server
* Oracle

In this guide, you will learn how to implement a simple CRUD application exposing data stored in **PostgreSQL** over a RESTful API.

**📌 NOTE**\
Extension and connection pool class names for each client can be found at the bottom of this document.

**❗ IMPORTANT**\
If you are not familiar with the Quarkus Vert.x extension, consider reading the [Using Eclipse Vert.x](../01-fundamentos/vertx.md) guide first.

The application shall manage fruit entities:

**src/main/java/org/acme/reactive/crud/Fruit.java**

```java
package org.acme.reactive.crud;

import io.smallrye.mutiny.Multi;
import io.smallrye.mutiny.Uni;
import io.vertx.mutiny.sqlclient.Pool;
import io.vertx.mutiny.sqlclient.Row;
import io.vertx.mutiny.sqlclient.RowSet;
import io.vertx.mutiny.sqlclient.Tuple;

public class Fruit {

    public Long id;

    public String name;

    public Fruit() {
        // default constructor.
    }

    public Fruit(String name) {
        this.name = name;
    }

    public Fruit(Long id, String name) {
        this.id = id;
        this.name = name;
    }
}
```

## Prerequisites

To complete this guide, you need:

* Roughly 15 minutes
* An IDE
* JDK 17+ installed with `JAVA_HOME` configured appropriately
* Apache Maven 3.9.16
* A working container runtime (Docker or [Podman](https://quarkus.io/guides/podman))
* Optionally the [Quarkus CLI](../10-extras/cli-tooling.md) if you want to use it
* Optionally Mandrel or GraalVM installed and [configured appropriately](../08-rendimiento-nativo/building-native-image.md#configuring-graalvm) if you want to build a native executable (or Docker if you use a native container build)

<dl><dt><strong>💡 TIP</strong></dt><dd>

If you start the application in dev mode, Quarkus provides you with a [zero-config database](https://quarkus.io/guides/databases-dev-services) out of the box.

You might also start a database up front:

```bash
docker run -it --rm=true --name quarkus_test -e POSTGRES_USER=quarkus_test -e POSTGRES_PASSWORD=quarkus_test -e POSTGRES_DB=quarkus_test -p 5432:5432 docker.io/library/postgres:18
```
</dd></dl>

## Solution

We recommend that you follow the instructions in the next sections and create the application step by step.
However, you can go right to the completed example.

Clone the Git repository: `git clone https://github.com/quarkusio/quarkus-quickstarts.git`, or download an [archive](https://github.com/quarkusio/quarkus-quickstarts/archive/main.zip).

The solution is located in the `getting-started-reactive-crud` [directory](https://github.com/quarkusio/quarkus-quickstarts/tree/main/getting-started-reactive-crud).

## Installing

### Reactive PostgreSQL Client extension

First, make sure your project has the `quarkus-reactive-pg-client` extension enabled.
If you are creating a new project, use the following command:

**CLI**

```bash
quarkus create app org.acme:reactive-pg-client-quickstart \
    --extension='rest,reactive-pg-client' \
    --no-code
cd reactive-pg-client-quickstart
```

To create a Gradle project, add the `--gradle` or `--gradle-kotlin-dsl` option.

For more information about how to install and use the Quarkus CLI, see the [Quarkus CLI](../10-extras/cli-tooling.md) guide.

**Maven**

```bash
mvn io.quarkus.platform:quarkus-maven-plugin:3.38.2:create \
    -DprojectGroupId=org.acme \
    -DprojectArtifactId=reactive-pg-client-quickstart \
    -Dextensions='rest,reactive-pg-client' \
    -DnoCode
cd reactive-pg-client-quickstart
```

To create a Gradle project, add the `-DbuildTool=gradle` or `-DbuildTool=gradle-kotlin-dsl` option.

For Windows users:

* If using cmd, (don’t use backward slash `\` and put everything on the same line)
* If using Powershell, wrap `-D` parameters in double quotes e.g. `"-DprojectArtifactId=reactive-pg-client-quickstart"`

If you have an already created project, the `reactive-pg-client` extension can be added to an existing Quarkus project with the `add-extension` command:

**CLI**

```bash
quarkus extension add reactive-pg-client
```
**Maven**

```bash
./mvnw quarkus:add-extension -Dextensions='reactive-pg-client'
```
**Gradle**

```bash
./gradlew addExtension --extensions='reactive-pg-client'
```

Otherwise, you can manually add the dependency to your build file:

**pom.xml**

```xml
<dependency>
    <groupId>io.quarkus</groupId>
    <artifactId>quarkus-reactive-pg-client</artifactId>
</dependency>
```

**build.gradle**

```gradle
implementation("io.quarkus:quarkus-reactive-pg-client")
```

### Mutiny

Quarkus REST (formerly RESTEasy Reactive) includes supports for Mutiny types (e.g. `Uni` and `Multi`) out of the box.

<dl><dt><strong>💡 TIP</strong></dt><dd>

In this guide, we will use the Mutiny API of the Reactive PostgreSQL Client.
If you are not familiar with Mutiny, check [Mutiny - an intuitive reactive programming library](../01-fundamentos/mutiny-primer.md).
</dd></dl>

### JSON Binding

We will expose `Fruit` instances over HTTP in the JSON format.
Consequently, you must also add the `quarkus-rest-jackson` extension:

**CLI**

```bash
quarkus extension add rest-jackson
```
**Maven**

```bash
./mvnw quarkus:add-extension -Dextensions='rest-jackson'
```
**Gradle**

```bash
./gradlew addExtension --extensions='rest-jackson'
```

If you prefer not to use the command line, manually add the dependency to your build file:

**pom.xml**

```xml
<dependency>
    <groupId>io.quarkus</groupId>
    <artifactId>quarkus-rest-jackson</artifactId>
</dependency>
```

**build.gradle**

```gradle
implementation("io.quarkus:quarkus-rest-jackson")
```

Of course, this is only a requirement for this guide, not any application using the Reactive PostgreSQL Client.

## Configuring

The Reactive PostgreSQL Client can be configured with standard Quarkus datasource properties and a reactive URL:

**src/main/resources/application.properties**

```properties
quarkus.datasource.db-kind=postgresql
quarkus.datasource.username=quarkus_test
quarkus.datasource.password=quarkus_test
quarkus.datasource.reactive.url=postgresql://localhost:5432/quarkus_test
```

With that you can create your `FruitResource` skeleton and inject a `io.vertx.mutiny.sqlclient.Pool` instance:

**src/main/java/org/acme/vertx/FruitResource.java**

```java
package org.acme.reactive.crud;

import java.net.URI;

import jakarta.ws.rs.DELETE;
import jakarta.ws.rs.GET;
import jakarta.ws.rs.POST;
import jakarta.ws.rs.PUT;
import jakarta.ws.rs.Path;
import jakarta.ws.rs.core.Response;
import jakarta.ws.rs.core.Response.ResponseBuilder;
import jakarta.ws.rs.core.Response.Status;

import io.smallrye.mutiny.Multi;
import io.smallrye.mutiny.Uni;
import io.vertx.mutiny.sqlclient.Pool;

@Path("fruits")
public class FruitResource {

    private final Pool client;

    public FruitResource(Pool client) {
        this.client = client;
    }
}
```

## Database schema and seed data

Before we implement the REST endpoint and data management code, we must set up the database schema.
It would also be convenient to have some data inserted up front.

For production, we would recommend to use something like the [Flyway database migration tool](flyway.md).
But for development we can simply drop and create the tables on startup, and then insert a few fruits.

**/src/main/java/org/acme/reactive/crud/DBInit.java**

```java
package org.acme.reactive.crud;

import io.quarkus.runtime.StartupEvent;
import io.vertx.mutiny.sqlclient.Pool;
import org.eclipse.microprofile.config.inject.ConfigProperty;

import jakarta.enterprise.context.ApplicationScoped;
import jakarta.enterprise.event.Observes;

@ApplicationScoped
public class DBInit {

    private final Pool client;
    private final boolean schemaCreate;

    public DBInit(Pool client, @ConfigProperty(name = "myapp.schema.create", defaultValue = "true") boolean schemaCreate) {
        this.client = client;
        this.schemaCreate = schemaCreate;
    }

    void onStart(@Observes StartupEvent ev) {
        if (schemaCreate) {
            initdb();
        }
    }

    private void initdb() {
        // TODO
    }
}
```

**💡 TIP**\
You might override the default value of the `myapp.schema.create` property in the `application.properties` file.

Almost ready!
To initialize the DB in development mode, we will use the client simple `query` method.
It returns a `Uni` and thus can be composed to execute queries sequentially:

```java
client.query("DROP TABLE IF EXISTS fruits").execute()
    .flatMap(r -> client.query("CREATE TABLE fruits (id SERIAL PRIMARY KEY, name TEXT NOT NULL)").execute())
    .flatMap(r -> client.query("INSERT INTO fruits (name) VALUES ('Kiwi')").execute())
    .flatMap(r -> client.query("INSERT INTO fruits (name) VALUES ('Durian')").execute())
    .flatMap(r -> client.query("INSERT INTO fruits (name) VALUES ('Pomelo')").execute())
    .flatMap(r -> client.query("INSERT INTO fruits (name) VALUES ('Lychee')").execute())
    .await().indefinitely();
```

<dl><dt><strong>📌 NOTE</strong></dt><dd>

Wondering why we must block until the latest query is completed?
This code is part of a method that `@Observes` the `StartupEvent` and Quarkus invokes it synchronously.
As a consequence, returning prematurely could lead to serving requests while the database is not ready yet.
</dd></dl>

That’s it!
So far we have seen how to configure a pooled client and execute simple queries.
We are now ready to develop the data management code and implement our RESTful endpoint.

## Using

### Query results traversal

In development mode, the database is set up with a few rows in the `fruits` table.
To retrieve all the data, we will use the `query` method again:

**/src/main/java/org/acme/reactive/crud/Fruit.java**

```java
    public static Multi<Fruit> findAll(Pool client) {
        return client.query("SELECT id, name FROM fruits ORDER BY name ASC").execute()
                .onItem().transformToMulti(set -> Multi.createFrom().iterable(set)) // ①
                .onItem().transform(Fruit::from); // ②
    }

    private static Fruit from(Row row) {
        return new Fruit(row.getLong("id"), row.getString("name"));
    }
```

1. Transform the `io.vertx.mutiny.sqlclient.RowSet` to a `Multi<Row>`.
2. Convert each `io.vertx.mutiny.sqlclient.Row` to a `Fruit`.

The `Fruit#from` method converts a `Row` instance to a `Fruit` instance.
It is extracted as a convenience for the implementation of the other data management methods.

Then, add the endpoint to get all fruits from the backend:

**src/main/java/org/acme/vertx/FruitResource.java**

```java
@GET
public Multi<Fruit> get() {
    return Fruit.findAll(client);
}
```

Now start Quarkus in dev mode with:

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

Lastly, open your browser and navigate to http://localhost:8080/fruits, you should see:

```json
[{"id":2,"name":"Durian"},{"id":1,"name":"Kiwi"},{"id":4,"name":"Lychee"},{"id":3,"name":"Pomelo"}]
```

### Prepared queries

The Reactive PostgreSQL Client can also prepare queries and take parameters that are replaced in the SQL statement at execution time:

```java
client.preparedQuery("SELECT id, name FROM fruits WHERE id = $1").execute(Tuple.of(id))
```

**💡 TIP**\
For PostgreSQL, the SQL string can refer to parameters by position, using `$1`, `$2`, ...etc.
Please refer to the [Database Clients details](#database-clients-details) section for other databases.

Similar to the simple `query` method, `preparedQuery` returns an instance of `PreparedQuery<RowSet<Row>>`.
Equipped with this tooling, we are able to safely use an `id` provided by the user to get the details of a particular fruit:

**src/main/java/org/acme/vertx/Fruit.java**

```java
public static Uni<Fruit> findById(Pool client, Long id) {
    return client.preparedQuery("SELECT id, name FROM fruits WHERE id = $1").execute(Tuple.of(id)) // ①
            .onItem().transform(RowSet::iterator) // ②
            .onItem().transform(iterator -> iterator.hasNext() ? from(iterator.next()) : null); // ③
}
```
1. Create a `Tuple` to hold the prepared query parameters.
2. Get an `Iterator` for the `RowSet` result.
3. Create a `Fruit` instance from the `Row` if an entity was found.

And in the Jakarta REST resource:

**src/main/java/org/acme/vertx/FruitResource.java**

```java
@GET
@Path("{id}")
public Uni<Response> getSingle(Long id) {
    return Fruit.findById(client, id)
            .onItem().transform(fruit -> fruit != null ? Response.ok(fruit) : Response.status(Status.NOT_FOUND)) // ①
            .onItem().transform(ResponseBuilder::build); // ②
}
```
1. Prepare a Jakarta REST response with  either the `Fruit` instance if found or the `404` status code.
2. Build and send the response.

The same logic applies when saving a `Fruit`:

**src/main/java/org/acme/vertx/Fruit.java**

```java
public Uni<Long> save(Pool client) {
    return client.preparedQuery("INSERT INTO fruits (name) VALUES ($1) RETURNING id").execute(Tuple.of(name))
            .onItem().transform(pgRowSet -> pgRowSet.iterator().next().getLong("id"));
}
```

And in the web resource we handle the `POST` request:

**src/main/java/org/acme/vertx/FruitResource.java**

```java
@POST
public Uni<Response> create(Fruit fruit) {
    return fruit.save(client)
            .onItem().transform(id -> URI.create("/fruits/" + id))
            .onItem().transform(uri -> Response.created(uri).build());
}
```

### Result metadata

A `RowSet` does not only hold your data in memory, it also gives you some information about the data itself, such as:

* the number of rows affected by the query (inserted/deleted/updated/retrieved depending on the query type),
* the column names.

Let’s use this to support removal of fruits in the database:

**src/main/java/org/acme/vertx/Fruit.java**

```java
public static Uni<Boolean> delete(Pool client, Long id) {
    return client.preparedQuery("DELETE FROM fruits WHERE id = $1").execute(Tuple.of(id))
            .onItem().transform(pgRowSet -> pgRowSet.rowCount() == 1); // ①
}
```
1. Inspect metadata to determine if a fruit has been actually deleted.

And to handle the HTTP `DELETE` method in the web resource:

**src/main/java/org/acme/vertx/FruitResource.java**

```java
@DELETE
@Path("{id}")
public Uni<Response> delete(Long id) {
    return Fruit.delete(client, id)
            .onItem().transform(deleted -> deleted ? Status.NO_CONTENT : Status.NOT_FOUND)
            .onItem().transform(status -> Response.status(status).build());
}
```

With `GET`, `POST` and `DELETE` methods implemented, we can now create a minimal web page to try the RESTful application out.
We will use [jQuery](https://jquery.com/) to simplify interactions with the backend:

**/src/main/resources/META-INF/resources/fruits.html**

```html
<!doctype html>
<html>
<head>
    <meta charset="utf-8"/>
    <title>Reactive REST - Quarkus</title>
    <script src="https://code.jquery.com/jquery-3.3.1.min.js"
            integrity="sha256-FgpCb/KJQlLNfOu91ta32o/NMZxltwRo8QtmkMRdAu8=" crossorigin="anonymous"></script>
    <script type="application/javascript" src="fruits.js"></script>
</head>
<body>

<h1>Fruits API Testing</h1>

<h2>All fruits</h2>
<div id="all-fruits"></div>

<h2>Create Fruit</h2>
<input id="fruit-name" type="text">
<button id="create-fruit-button" type="button">Create</button>
<div id="create-fruit"></div>

</body>
</html>
```

**💡 TIP**\
Quarkus automatically serves static resources located under the `META-INF/resources` directory.

In the JavaScript code, we need a function to refresh the list of fruits when:

* the page is loaded, or
* a fruit is added, or
* a fruit is deleted.

**/src/main/resources/META-INF/resources/fruits.js**

```javascript
function refresh() {
    $.get('/fruits', function (fruits) {
        var list = '';
        (fruits || []).forEach(function (fruit) { // ①
            list = list
                + '<tr>'
                + '<td>' + fruit.id + '</td>'
                + '<td>' + fruit.name + '</td>'
                + '<td><a href="#" onclick="deleteFruit(' + fruit.id + ')">Delete</a></td>'
                + '</tr>'
        });
        if (list.length > 0) {
            list = ''
                + '<table><thead><th>Id</th><th>Name</th><th></th></thead>'
                + list
                + '</table>';
        } else {
            list = "No fruits in database"
        }
        $('#all-fruits').html(list);
    });
}

function deleteFruit(id) {
    $.ajax('/fruits/' + id, {method: 'DELETE'}).then(refresh);
}

$(document).ready(function () {

    $('#create-fruit-button').click(function () {
        var fruitName = $('#fruit-name').val();
        $.post({
            url: '/fruits',
            contentType: 'application/json',
            data: JSON.stringify({name: fruitName})
        }).then(refresh);
    });

    refresh();
});
```
1. The `fruits` parameter is not defined when the database is empty.

All done!
Navigate to http://localhost:8080/fruits.html and read/create/delete some fruits.

## Database Clients details

| Database | Extension name | Placeholders |
| --- | --- | --- |
| IBM Db2 | `quarkus-reactive-db2-client` | `?` |
| MariaDB/MySQL | `quarkus-reactive-mysql-client` | `?` |
| Microsoft SQL Server | `quarkus-reactive-mssql-client` | `@p1`, `@p2`, etc. |
| Oracle | `quarkus-reactive-oracle-client` | `?` |
| PostgreSQL | `quarkus-reactive-pg-client` | `$1`, `$2`, etc. |

## Transactions

The reactive SQL clients support transactions.
A transaction is started with `io.vertx.mutiny.sqlclient.SqlConnection#begin` and terminated with either `io.vertx.mutiny.sqlclient.Transaction#commit` or `io.vertx.mutiny.sqlclient.Transaction#rollback`.
All these operations are asynchronous:

* `connection.begin()` returns a `Uni<Transaction>`
* `transaction.commit()` and `transaction.rollback()` return `Uni<Void>`

Managing transactions in the reactive programming world can be cumbersome.
Instead of writing repetitive and complex (thus error-prone!) code, you can use the `io.vertx.mutiny.sqlclient.Pool#withTransaction` helper method.

The following snippet shows how to run 2 insertions in the same transaction:

```java
public static Uni<Void> insertTwoFruits(Pool client, Fruit fruit1, Fruit fruit2) {
    return client.withTransaction(conn -> {
        Uni<RowSet<Row>> insertOne = conn.preparedQuery("INSERT INTO fruits (name) VALUES ($1) RETURNING id")
                .execute(Tuple.of(fruit1.name));
        Uni<RowSet<Row>> insertTwo = conn.preparedQuery("INSERT INTO fruits (name) VALUES ($1) RETURNING id")
                .execute(Tuple.of(fruit2.name));

        return Uni.combine().all().unis(insertOne, insertTwo)
                // Ignore the results (the two ids)
                .discardItems();
    });
}
```

In this example, the transaction is automatically committed on success or rolled back on failure.

You can also create dependent actions as follows:

```java
return client.withTransaction(conn -> conn

        .preparedQuery("INSERT INTO person (firstname,lastname) VALUES ($1,$2) RETURNING id")
        .execute(Tuple.of(person.getFirstName(), person.getLastName()))

        .onItem().transformToUni(id -> conn.preparedQuery("INSERT INTO addr (person_id,addrline1) VALUES ($1,$2)")
                .execute(Tuple.of(id.iterator().next().getLong("id"), person.getLastName())))

        .onItem().ignore().andContinueWithNull());
```

## Working with batch query results

When executing batch queries, reactive SQL clients return a `RowSet` that corresponds to the results of the first element in the batch.
To get the results of the following batch elements, you must invoke the `RowSet#next` method until it returns `null`.

Let’s say you want to update some rows and compute the total number of affected rows.
You must inspect each `RowSet`:

```java
PreparedQuery<RowSet<Row>> preparedQuery = client.preparedQuery("UPDATE fruits SET name = $1 WHERE id = $2");

Uni<RowSet<Row>> rowSet = preparedQuery.executeBatch(Arrays.asList(
        Tuple.of("Orange", 1),
        Tuple.of("Pear", 2),
        Tuple.of("Apple", 3)));

Uni<Integer> totalAffected = rowSet.onItem().transform(res -> {
    int total = 0;
    do {
        total += res.rowCount(); // ①
    } while ((res = res.next()) != null); // ②
    return total;
});
```
1. Compute the sum of `RowSet#rowCount`.
2. Invoke `RowSet#next` until it returns `null`.

As another example, if you want to load all the rows you just inserted, you must concatenate the contents of each `RowSet`:

```java
PreparedQuery<RowSet<Row>> preparedQuery = client.preparedQuery("INSERT INTO fruits (name) VALUES ($1) RETURNING *");

Uni<RowSet<Row>> rowSet = preparedQuery.executeBatch(Arrays.asList(
        Tuple.of("Orange"),
        Tuple.of("Pear"),
        Tuple.of("Apple")));

// Generate a Multi of RowSet items
Multi<RowSet<Row>> rowSets = rowSet.onItem().transformToMulti(res -> {
    return Multi.createFrom().generator(() -> res, (rs, emitter) -> {
        RowSet<Row> next = null;
        if (rs != null) {
            emitter.emit(rs);
            next = rs.next();
        }
        if (next == null) {
            emitter.complete();
        }
        return next;
    });
});

// Transform each RowSet into Multi of Row items and Concatenate
Multi<Row> rows = rowSets.onItem().transformToMultiAndConcatenate(Multi.createFrom()::iterable);
```

## Multiple Datasources

The reactive SQL clients support defining several datasources.

A typical configuration with several datasources would look like:

```properties
quarkus.datasource.db-kind=postgresql ①
quarkus.datasource.username=user-default
quarkus.datasource.password=password-default
quarkus.datasource.reactive.url=postgresql://localhost:5432/default

quarkus.datasource."additional1".db-kind=postgresql ②
quarkus.datasource."additional1".username=user-additional1
quarkus.datasource."additional1".password=password-additional1
quarkus.datasource."additional1".reactive.url=postgresql://localhost:5432/additional1

quarkus.datasource."additional2".db-kind=mysql ③
quarkus.datasource."additional2".username=user-additional2
quarkus.datasource."additional2".password=password-additional2
quarkus.datasource."additional2".reactive.url=mysql://localhost:3306/additional2
```
1. The default datasource - using PostgreSQL.
2. A named datasource called `additional1` - using PostgreSQL.
3. A named datasource called `additional2` - using MySQL.

You can then inject the clients as follows:

```java
@Inject ①
Pool defaultClient;

@Inject
@ReactiveDataSource("additional1") ②
Pool additional1Client;

@Inject
@ReactiveDataSource("additional2")
MySQLPool additional2Client;
```
1. Injecting the client for the default datasource does not require anything special.
2. For a named datasource, you use the `@ReactiveDataSource` CDI qualifier with the datasource name as its value.

## UNIX Domain Socket connections

The PostgreSQL and MariaDB/MySQL clients can be configured to connect to the server through a UNIX domain socket.

First make sure that [native transport support](../01-fundamentos/vertx-reference.md#native-transport) is enabled.

Then configure the database connection url.
This step depends on the database type.

### PostgreSQL

PostgreSQL domain socket paths have the following form: `<directory>/.s.PGSQL.<port>`

The database connection url must be configured so that:

* the `host` is the `directory` in the socket path
* the `port` is the `port` in the socket path

Consider the following socket path: `/var/run/postgresql/.s.PGSQL.5432`.

In `application.properties` add:

```properties
quarkus.datasource.reactive.url=postgresql://:5432/quarkus_test?host=/var/run/postgresql
```

### MariaDB/MySQL

The database connection url must be configured so that the `host` is the socket path.

Consider the following socket path: `/var/run/mysqld/mysqld.sock`.

In `application.properties` add:

```properties
quarkus.datasource.reactive.url=mysql:///quarkus_test?host=/var/run/mysqld/mysqld.sock
```

## Load-balancing connections

The reactive PostgreSQL and MariaDB/MySQL clients support defining several connections.

A typical configuration with several connections would look like:

```properties
quarkus.datasource.reactive.url=postgresql://host1:5432/default,postgresql://host2:5432/default,postgresql://host3:5432/default
```

This can also be written with indexed property syntax:

```properties
quarkus.datasource.reactive.url[0]=postgresql://host1:5432/default
quarkus.datasource.reactive.url[1]=postgresql://host2:5432/default
quarkus.datasource.reactive.url[2]=postgresql://host3:5432/default
```

## Pooled connection `idle-timeout`

Reactive datasources can be configured with an `idle-timeout`.
It is the maximum time a connection remains unused in the pool before it is closed.

**📌 NOTE**\
The `idle-timeout` is disabled by default.

For example, you could expire idle connections after 60 minutes:

```properties
quarkus.datasource.reactive.idle-timeout=PT60M
```

## Pooled Connection `max-lifetime`

In addition to `idle-timeout`, reactive datasources can also be configured with a `max-lifetime`.
It is the maximum time a connection remains in the pool before it is closed and replaced as needed.
The `max-lifetime` allows ensuring the pool has fresh connections with up-to-date configuration.

**📌 NOTE**\
The `max-lifetime` is disabled by default but is an important configuration when using a credentials
provider that provides time limited credentials, like the [Vault credentials provider](https://quarkus.io/guides/credentials-provider).

For example, you could ensure connections are recycled after 60 minutes:

```properties
quarkus.datasource.reactive.max-lifetime=PT60M
```

## Customizing pool creation

Sometimes, the database connection pool cannot be configured only by declaration.

For example, you might have to read a specific file only present in production, or retrieve configuration data from a proprietary configuration server.

In this case, you can customize pool creation by creating a class implementing an interface which depends on the target database:

| Database | Pool creator class name |
| --- | --- |
| IBM Db2 | `io.quarkus.reactive.db2.client.DB2PoolCreator` |
| MariaDB/MySQL | `io.quarkus.reactive.mysql.client.MySQLPoolCreator` |
| Microsoft SQL Server | `io.quarkus.reactive.mssql.client.MSSQLPoolCreator` |
| Oracle | `io.quarkus.reactive.oracle.client.OraclePoolCreator` |
| PostgreSQL | `io.quarkus.reactive.pg.client.PgPoolCreator` |

Here’s an example for PostgreSQL:

```java
import jakarta.inject.Singleton;

import io.quarkus.reactive.pg.client.PgPoolCreator;
import io.vertx.pgclient.PgConnectOptions;
import io.vertx.sqlclient.Pool;
import io.vertx.sqlclient.PoolOptions;

@Singleton
public class CustomPgPoolCreator implements PgPoolCreator {

    @Override
    public Pool create(Input input) {
        PgConnectOptions connectOptions = input.pgConnectOptions();
        PoolOptions poolOptions = input.poolOptions();
        // Customize connectOptions, poolOptions or both, as required
        return Pool.pool(input.vertx(), connectOptions, poolOptions);
    }
}
```

## Pipelining

The PostgreSQL and MariaDB/MySQL clients support pipelining of queries at the connection level.
The feature consists in sending multiple queries on the same database connection without waiting for the corresponding responses.

In some use cases, query pipelining can improve database access performance.

Here’s an example for PostgreSQL:

```java
import jakarta.inject.Inject;

import io.smallrye.mutiny.Uni;
import io.vertx.mutiny.sqlclient.Pool;

public class PipeliningExample {

    @Inject
    Pool client;

    public Uni<String> favoriteFruitAndVegetable() {
        // Explicitly acquire a connection
        return client.withConnection(conn -> {
            Uni<String> favoriteFruit = conn.query("SELECT name FROM fruits WHERE preferred IS TRUE").execute()
                    .onItem().transform(rows -> rows.iterator().next().getString("name"));
            Uni<String> favoriteVegetable = conn.query("SELECT name FROM vegetables WHERE preferred IS TRUE").execute()
                    .onItem().transform(rows -> rows.iterator().next().getString("name"));
            // favoriteFruit and favoriteVegetable unis will be subscribed at the same time
            return Uni.combine().all().unis(favoriteFruit, favoriteVegetable)
                    .combinedWith(PipeliningExample::formatMessage);
        });
    }

    private static String formatMessage(String fruit, String vegetable) {
        return String.format("The favorite fruit is %s and the favorite vegetable is %s", fruit, vegetable);
    }
}
```

The maximum number of pipelined queries is configured with the `pipelining-limit` property:

```properties
# For PostgreSQL
quarkus.datasource.reactive.postgresql.pipelining-limit=256
# For MariaDB/MySQL
quarkus.datasource.reactive.mysql.pipelining-limit=256
```

By default, `pipelining-limit` is set to 256.

## Configuration Reference

### Common Datasource

**📌 NOTE**\
La tabla de configuracion generada `quarkus-datasource` se produce al construir la documentacion y no existe en el codigo fuente. Consulta la referencia de configuracion en https://quarkus.io/guides/all-config

### Reactive Datasource

**📌 NOTE**\
La tabla de configuracion generada `quarkus-reactive-datasource` se produce al construir la documentacion y no existe en el codigo fuente. Consulta la referencia de configuracion en https://quarkus.io/guides/all-config

### IBM Db2

**📌 NOTE**\
La tabla de configuracion generada `quarkus-reactive-db2-client` se produce al construir la documentacion y no existe en el codigo fuente. Consulta la referencia de configuracion en https://quarkus.io/guides/all-config

### MariaDB/MySQL

**📌 NOTE**\
La tabla de configuracion generada `quarkus-reactive-mysql-client` se produce al construir la documentacion y no existe en el codigo fuente. Consulta la referencia de configuracion en https://quarkus.io/guides/all-config

### Microsoft SQL Server

**📌 NOTE**\
La tabla de configuracion generada `quarkus-reactive-mssql-client` se produce al construir la documentacion y no existe en el codigo fuente. Consulta la referencia de configuracion en https://quarkus.io/guides/all-config

### Oracle

**📌 NOTE**\
La tabla de configuracion generada `quarkus-reactive-oracle-client` se produce al construir la documentacion y no existe en el codigo fuente. Consulta la referencia de configuracion en https://quarkus.io/guides/all-config

### PostgreSQL

**📌 NOTE**\
La tabla de configuracion generada `quarkus-reactive-pg-client` se produce al construir la documentacion y no existe en el codigo fuente. Consulta la referencia de configuracion en https://quarkus.io/guides/all-config
