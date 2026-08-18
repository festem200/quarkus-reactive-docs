# Using Hibernate Reactive

> **Guia oficial:** <https://quarkus.io/guides/hibernate-reactive>  
> **Fuente:** `docs/src/main/asciidoc/hibernate-reactive.adoc` en [quarkusio/quarkus@3.38.2](https://github.com/quarkusio/quarkus/blob/3.38.2/docs/src/main/asciidoc/hibernate-reactive.adoc)  
> **Version documentada:** Quarkus 3.38.2 · **Sincronizado:** 2026-08-17 · **Licencia:** Apache-2.0

[Hibernate Reactive](https://hibernate.org/reactive/) is a reactive API for Hibernate ORM, supporting non-blocking database drivers
and a reactive style of interaction with the database.

<dl><dt><strong>📌 NOTE</strong></dt><dd>

Hibernate Reactive is not a replacement for [Hibernate ORM](https://quarkus.io/guides/hibernate-orm) or the future of Hibernate ORM.
It is a different stack tailored for reactive use cases where you need high-concurrency.

Also, using Quarkus REST (formerly RESTEasy Reactive), our default REST layer, does not require the use of Hibernate Reactive.
It is perfectly valid to use Quarkus REST with Hibernate ORM,
and if you do not need high-concurrency, or are not accustomed to the reactive paradigm, it is recommended to use Hibernate ORM.
</dd></dl>

<dl><dt><strong>📌 NOTE</strong></dt><dd>

Hibernate Reactive works with the same annotations and most of the configuration described in the
[Hibernate ORM guide](https://quarkus.io/guides/hibernate-orm). This guide will only focus on what’s specific
for Hibernate Reactive.
</dd></dl>

<dl><dt><strong><a name="extension-status-note"></a>📌 NOTE</strong></dt><dd>

This technology is considered preview.

## Solution

We recommend that you follow the instructions in the next sections and create the application step by step.
However, you can go right to the completed example.

Clone the Git repository: `git clone https://github.com/quarkusio/quarkus-quickstarts.git`, or download an [archive](https://github.com/quarkusio/quarkus-quickstarts/archive/main.zip).

The solution is located in the `hibernate-reactive-quickstart` [directory](https://github.com/quarkusio/quarkus-quickstarts/tree/main/hibernate-reactive-quickstart).

## Setting up and configuring Hibernate Reactive

When using Hibernate Reactive in Quarkus, you need to:

* add your configuration settings in `application.properties`
* annotate your entities with `@Entity` and any other mapping annotations as usual

Other configuration needs have been automated: Quarkus will make some opinionated choices and educated guesses.

Add the following dependencies to your project:

* the Hibernate Reactive extension: `io.quarkus:quarkus-hibernate-reactive`
* the [Reactive SQL client extension](reactive-sql-clients.md) for the database of your choice; the following options are available:
  * `quarkus-reactive-pg-client`: [the client for PostgreSQL or CockroachDB](https://vertx.io/docs/vertx-pg-client/java)
  * `quarkus-reactive-mysql-client`: [the client MySQL or MariaDB](https://vertx.io/docs/vertx-mysql-client/java)
  * `quarkus-reactive-mssql-client`: [the client for Microsoft SQL Server](https://vertx.io/docs/vertx-mssql-client/java)
  * `quarkus-reactive-db2-client`: [the client for IBM Db2](https://vertx.io/docs/vertx-db2-client/java)
  * `quarkus-reactive-oracle-client`: [the client for Oracle](https://vertx.io/docs/vertx-oracle-client/java)

For instance:

**pom.xml**

```xml
<!-- Hibernate Reactive dependency -->
<dependency>
    <groupId>io.quarkus</groupId>
    <artifactId>quarkus-hibernate-reactive</artifactId>
</dependency>

<!-- Reactive SQL client for PostgreSQL -->
<dependency>
    <groupId>io.quarkus</groupId>
    <artifactId>quarkus-reactive-pg-client</artifactId>
</dependency>
```

**build.gradle**

```gradle
// Hibernate Reactive dependency
implementation("io.quarkus:quarkus-hibernate-reactive")

Reactive SQL client for PostgreSQL
implementation("io.quarkus:quarkus-reactive-pg-client")
```

Annotate your persistent objects with `@Entity`,
then add the relevant configuration properties in `application.properties`:

**Example `application.properties`**

```properties
quarkus.datasource.db-kind = postgresql ①

%prod.quarkus.datasource.username = hibernate
%prod.quarkus.datasource.password = hibernate
%prod.quarkus.datasource.reactive.url = vertx-reactive:postgresql://localhost/quarkus_test ②
%prod.quarkus.hibernate-orm.schema-management.strategy=create ③
```
1. [Configure the datasource](datasource.md) for production, relying on [Dev Services](datasource.md#dev-services) for connection information in tests / dev mode.
2. The only different property from a Hibernate ORM configuration
3. Configure Hibernate ORM to create the schema on startup in production, which is useful for experimentation, but rely on [convenient defaults in tests / dev mode](https://quarkus.io/guides/hibernate-orm#dev-mode).

Note that these configuration properties are not the same ones as in your typical Hibernate Reactive configuration file.
They will often map to Hibernate Reactive configuration properties but could have different names and don’t necessarily map 1:1 to each other.

Blocking (non-reactive) and reactive configuration [can be mixed together in the same project](#hibernate-orm-and-reactive-extensions-simultaneously).

**⚠️ WARNING**\
Configuring Hibernate Reactive using the standard `persistence.xml` configuration file is not supported.

See section [Configuration Reference for Hibernate Reactive](#configuration-reference-for-hibernate-reactive) for the list of properties you can set in `application.properties`.

A `Mutiny.SessionFactory` will be created based on the Quarkus `datasource` configuration as long as the Hibernate Reactive extension is listed among your project dependencies.

The dialect will be selected based on the Reactive SQL client - unless you set one explicitly.

**📌 NOTE**\
For more information on dialect selection and database versions,
see [the corresponding section of the Hibernate ORM guide](https://quarkus.io/guides/hibernate-orm#hibernate-dialect).

You can then happily inject your `Mutiny.SessionFactory`:

**Example application bean using Hibernate Reactive**

```java
@ApplicationScoped
public class SantaClausService {
    @Inject
    Mutiny.SessionFactory sf; ①

    public Uni<Void> createGift(String giftDescription) {
	Gift gift = new Gift();
        gift.setName(giftDescription);
	return sf.withTransaction(session -> session.persist(gift)) ②
    }
}
```

1. Inject your session factory and have fun
2. `.withTransaction()` will automatically flush at commit

**⚠️ WARNING**\
Make sure to wrap methods modifying your database (e.g. `session.persist(entity)`) within a transaction.

**Example of an Entity**

```java
@Entity
public class Gift {
    private Long id;
    private String name;

    @Id
    @SequenceGenerator(name = "giftSeq", sequenceName = "gift_id_seq", allocationSize = 1, initialValue = 1)
    @GeneratedValue(generator = "giftSeq")
    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }
}
```

To load SQL statements when Hibernate Reactive starts, add an `import.sql` file in your `src/main/resources/` directory.
This script can contain any SQL DML statements.
Make sure to terminate each statement with a semicolon.

This is useful to have a data set ready for your tests or demos.

### Using `@Transactional` with Hibernate Reactive

You can use the standard `jakarta.transaction.Transactional` annotation with Hibernate Reactive.
This provides a more familiar programming model for developers coming from Hibernate ORM.

While defining transaction handling using the annotation, you should inject `Mutiny.Session` or `Mutiny.StatelessSession` using CDI and use them in methods annotated with `@Transactional`.

Here’s an example showing how to use `@Transactional` in a REST resource:

**Example REST resource using @Transactional**

```java
@Path("/fruits")
public class FruitResource {

    @Inject
    Mutiny.Session session; ①

    @GET
    @Path("/{id}")
    public Uni<Fruit> getFruit(Long id) {
        return session.find(Fruit.class, id);
    }

    @POST
    @Transactional ②
    public Uni<Fruit> createFruit(Fruit fruit) {
        return session.persist(fruit)
                .chain(() -> session.find(Fruit.class, fruit.getId()));
    }

    @PUT
    @Path("/{id}")
    @Transactional ③
    public Uni<Fruit> updateFruit(Long id, @QueryParam("name") String newName) {
        return session.find(Fruit.class, id)
                .map(fruit -> {
                    fruit.setName(newName);
                    return fruit;
                });
    }

}
```

1. Inject the reactive session directly
2. Use `@Transactional` for persist operations - creates new entities in the database
3. Use `@Transactional` for update operations - modifies existing entities

The `@Transactional` interceptor will:

* Lazily open a Hibernate Reactive session when first accessed
* Begin a transaction automatically
* Commit the transaction when the `Uni` completes successfully
* Roll back the transaction if an exception is thrown or the `Uni` is cancelled
* Close the session and release the database connection when the reactive chain completes

<dl><dt><strong>❗ IMPORTANT</strong></dt><dd>

There are some limitations when using `@Transactional` with Hibernate Reactive, in particular not being able to use a specific `TxType`, not being able to use multiple persistence units / datasources, or non-functional `Uni.combine()`/`Uni.joining()`.

See [Limitations and other things you should know](#limitations-and-other-things-you-should-know) for more information.
</dd></dl>

### Hibernate Reactive configuration properties

There are various optional properties useful to refine your session factory or guide Quarkus' guesses.

When no properties are set, Quarkus can typically infer everything it needs to set up Hibernate Reactive
and will have it use the default datasource.

The configuration properties listed here allow you to override such defaults, and customize and tune various aspects.

Hibernate Reactive uses the same properties you would use for Hibernate ORM: see [Configuration Reference for Hibernate Reactive](#configuration-reference-for-hibernate-reactive).

### Hibernate ORM and Reactive extensions simultaneously

If you add both Hibernate ORM and Hibernate Reactive extensions to your Quarkus app, they can be mixed together in the same project.

This is useful if your app normally uses Hibernate ORM (which is blocking), but you want to try Hibernate Reactive to see if it works better for your case.

By adding the second extension, you can use the reactive API in another part of your code - without needing to create a separate app.

**📌 NOTE**\
Hibernate ORM and Hibernate Reactive won’t share the same persistence context, so it’s recommended you stick to one or the other in a given method. For example use Hibernate ORM in blocking REST endpoints, and use Hibernate Reactive in reactive REST endpoints.

* To use the both extension simultaneously, add both extension to the `pom.xml` file:

  ```xml
          <!-- Hibernate reactive -->
          <dependency>
              <groupId>io.quarkus</groupId>
              <artifactId>quarkus-hibernate-reactive</artifactId>
          </dependency>
          <dependency>
              <groupId>io.quarkus</groupId>
              <artifactId>quarkus-reactive-pg-client</artifactId>
          </dependency>

          <!-- Hibernate ORM -->
          <dependency>
              <groupId>io.quarkus</groupId>
              <artifactId>quarkus-jdbc-postgresql</artifactId>
          </dependency>
          <dependency>
              <groupId>io.quarkus</groupId>
              <artifactId>quarkus-hibernate-orm</artifactId>
          </dependency>
  ```
* Also update the `applications.properties` file:
```properties
%prod.quarkus.datasource.reactive.url=postgresql:///your_database
%prod.quarkus.datasource.jdbc.url=jdbc:postgresql://localhost:5432/hibernate_orm_test
```
* The presence of the JDBC driver will enable Hibernate ORM. If you want to disable it, and only use Hibernate Reactive, you can use:

  ```properties
  quarkus.hibernate-orm.blocking=false
  ```

Quarkus will set many Hibernate Reactive configuration settings automatically, and will often use more modern defaults.

#### CDI integration

If you are familiar with using Hibernate Reactive in Quarkus, you probably already have injected the `Mutiny.SessionFactory` using CDI:

```java
@Inject
Mutiny.SessionFactory sessionFactory;
```

This will inject the `Mutiny.SessionFactory` of the default persistence unit.

**📌 NOTE**\
Prior to Quarkus 3.0 it was also possible to inject a `@RequestScoped` bean for `Mutiny.Session`. However, the lifecycle of a reactive session does not fit the lifecycle of the CDI request context. Therefore, this bean is removed in Quarkus 3.0.

### Activate/deactivate persistence units

When a persistence unit is configured at build time, and it is assigned entity types or an [active datasource](datasource.md#datasource-active), the persistence unit is active by default.
Quarkus starts the corresponding Hibernate Reactive `SessionFactory` when the application starts.

To deactivate a persistence unit at runtime, see [the corresponding section of the Hibernate ORM guide](https://quarkus.io/guides/hibernate-orm#persistence-unit-active).

<dl><dt><strong>📌 NOTE</strong></dt><dd>

If you decide to follow the example from the Hibernate ORM guide to declare a custom CDI bean for the active persistence unit,
but you use Hibernate Reactive,
make sure to work with the `Mutiny.SessionFactory` type instead of `Session`:
this is one way Hibernate Reactive’s API entrypoint differs from Hibernate ORM’s.

See [CDI integration](#cdi-integration) for details.
</dd></dl>

## Automatically transitioning to Flyway to Manage Schemas

Hibernate Reactive can be used in the same application as Flyway.
See [this section of the Flyway extension documentation](flyway.md#reactive-datasources)
for details regarding configuration of Flyway in a reactive application.

<dl><dt><strong>💡 TIP</strong></dt><dd>

If you have the [Flyway extension](flyway.md) installed when running in development mode,
Quarkus provides a simple way to initialize your Flyway configuration
using the schema generated automatically by Hibernate Reactive.

See [the Hibernate ORM guide](https://quarkus.io/guides/hibernate-orm#flyway) for more details.
</dd></dl>

### Testing

Using Hibernate Reactive in a `@QuarkusTest` is slightly more involved than using Hibernate ORM due to the asynchronous nature of the APIs and the fact that all operations need to run on a Vert.x Event Loop.

Two components are necessary to write these tests:

* The use of `@io.quarkus.test.vertx.RunOnVertxContext` or `@io.quarkus.test.TestReactiveTransaction` on the test methods
* The use of `io.quarkus.test.vertx.UniAsserter` as a test method parameter.

**❗ IMPORTANT**\
These classes are provided by the `quarkus-test-vertx` dependency.

A very simple example usage looks like:

```java
@QuarkusTest
public class SomeTest {

    @Inject
    Mutiny.SessionFactory sessionFactory;

    @Test
    @RunOnVertxContext
    public void testQuery(UniAsserter asserter) {
        asserter.assertThat(() -> sessionFactory.withSession(s -> s.createQuery(
                "from Gift g where g.name = :name").setParameter("name", "Lego").getResultList()),
                list -> org.junit.jupiter.api.Assertions.assertEquals(list.size(), 1));
    }

}
```

**📌 NOTE**\
See the Javadoc of `UniAsserter` for a full description of the various methods that can be used for creating assertions.

<dl><dt><strong>💡 TIP</strong></dt><dd>

You can also extend the `io.quarkus.test.vertx.UniAsserterInterceptor` to wrap the injected `UniAsserter` and customize the default behavior. For example, the interceptor can be used to execute the assert methods within a separate database transaction.:

```java
@QuarkusTest
public class SomeTest {

   @Test
   @RunOnVertxContext
   public void testEntity(UniAsserter asserter) {
      asserter = new UniAsserterInterceptor(asserter) {
         @Override
         protected <T> Supplier<Uni<T>> transformUni(Supplier<Uni<T>> uniSupplier) {
            return () -> Panache.withTransaction(uniSupplier);
         }
      };
      asserter.execute(() -> new MyEntity().persist());
      asserter.assertEquals(() -> MyEntity.count(), 1l);
      asserter.execute(() -> MyEntity.deleteAll());
   }
}
```
</dd></dl>

### Multiple persistence units

#### Setting up multiple persistence units

In a similar fashion to Hibernate ORM, Hibernate Reactive supports multiple persistence units.

You can define multiple persistence units and datasources, and they can mix blocking and reactive datasources.
To ensure that a datasource supports reactive, you need to set the `reactive` property to `true`.

**Example `application.properties`**

```properties
quarkus.datasource."users".reactive.url=vertx-reactive:postgresql://localhost/users ①
quarkus.datasource."users".db-kind=postgresql
%prod.quarkus.datasource."users".username=hibernate_orm_test
%prod.quarkus.datasource."users".password=hibernate_orm_test

quarkus.datasource."inventory".reactive.url=vertx-reactive:postgresql://localhost/inventory ②
quarkus.datasource."inventory".db-kind=postgresql
%prod.quarkus.datasource."inventory".username=hibernate_orm_test
%prod.quarkus.datasource."inventory".password=hibernate_orm_test

quarkus.hibernate-orm."users".datasource=users ③
quarkus.hibernate-orm."users".packages=io.quarkus.hibernate.reactive.multiplepersistenceunits.model.config.user

quarkus.hibernate-orm."inventory".datasource=inventory ④
quarkus.hibernate-orm."inventory".packages=io.quarkus.hibernate.orm.multiplepersistenceunits.model.config.inventory
```
1. Define a reactive datasource named `users`.
2. Define a reactive datasource named `inventory`.
3. Define a persistence unit named `users` and specify the datasource.
4. Define a persistence unit named `inventory` and specify the datasource.

When using named persistence units, you must set the `datasource` property to the name of the corresponding datasource.

## Limitations and other things you should know

Quarkus does not modify the libraries it uses; this rule applies to Hibernate Reactive as well: when using
this extension you will mostly have the same experience as using the original library.

But while they share the same code, Quarkus does configure some components automatically and inject custom implementations
for some extension points; this should be transparent and useful but if you’re an expert of Hibernate Reactive you might want to
know what is being done.

### General limitations

* Hibernate Reactive is not configurable via a `persistence.xml` file.
* This extension only considers the default persistence unit at the moment:
it’s not possible to configure multiple persistence units,
or even a single named persistence unit.
* This extension does not support [database-based multitenancy](https://quarkus.io/guides/hibernate-orm#database-approach)
or [schema-based multitenancy](https://quarkus.io/guides/hibernate-orm#schema-approach) at the moment.
[Discriminator-based multitenancy](https://quarkus.io/guides/hibernate-orm#discriminator-approach), on the other hand, is expected to work correctly.
See https://github.com/quarkusio/quarkus/issues/15959.
* Integration with the Envers extension is not supported.

### Transaction management: choosing between `@Transactional` and Panache annotations

With the introduction of the `quarkus-reactive-transactions` extension, you now have two options for managing transactions in Hibernate Reactive applications:

1. Use `jakarta.transaction.Transactional` for declarative transaction management
2. Use Panache’s transaction annotations (`@WithTransaction`, `@WithSession`, `@WithSessionOnDemand`, or the programmatic `Panache.withTransaction()`)

You must choose one approach and use it consistently throughout your application.
Mixing both transaction management styles in the same reactive pipeline is not supported and will result in an `UnsupportedOperationException`.
In the future, we’ll deprecate the previous annotations provided by Panache and and support only `@Transactional`.

You can inject either `Mutiny.Session` or `Mutiny.StatelessSession`.
Mixing both session types in the same transaction should work, but should be reserved for exotic use cases implemented by advanced users, as the (stateful) session will not be aware of changes operated through the stateless session, which could thus conflict or be silently erased by (stateful) session writes.

### Using Declarative Transaction Management in different reactive pipelines

When using declarative transaction management with Vert.x context-based interceptors (`@Transactional`, `@WithTransaction`, `@WithSession`, `@WithSessionOnDemand`) in multiple methods and combining such methods with either `Uni.combine().all().unis()` or `Uni.join().all()` the same transaction might be shared by different reactive pipelines causing unpredictable behavior.

For this reason, ***avoid using declarative transactional management with those methods***.

### Other Declarative Transactional Management limitations

Reactive transactions does not use `TransactionManager`, thus they are local only and do not support XA transactions. Every parameter defined on the `TransactionManager` (such as `quarkus.transaction-manager.default-transaction-timeout`) will be ignored. Only a single datasource can participate in a transaction.

Reactive transactions also work exclusively within the reactive pipeline.
If blocking code is executed (for example on a worker thread) as part of that pipeline, it will not be able to participate in the transaction.

Declarative reactive transactions with `@Transactional` can only be applied to methods returning `Uni`, not `Multi`, `CompletionStage`, or `CompletableFuture`.

Currently, only `Transactional.TxType.REQUIRED` is supported with reactive transactions. Other transaction types (`REQUIRES_NEW`, `MANDATORY`, etc.) will throw an `UnsupportedOperationException`.

## Simplifying Hibernate Reactive with Panache

The [Hibernate Reactive with Panache](hibernate-reactive-panache.md) extension facilitates the usage of Hibernate Reactive
by providing active record style entities (and repositories) and focuses on making your entities trivial and fun to write in Quarkus.

## Validation modes and Hibernate Validator integration

To find out more on how the [`quarkus.hibernate-orm.validation.mode` configuration property](#quarkus-hibernate-orm_quarkus-hibernate-orm-validation-mode).
influence your Hibernate Reactive application see the [corresponding Hibernate ORM guide](https://quarkus.io/guides/hibernate-orm#validator_integration),
as these modes work the same in both cases.

## Configuration Reference for Hibernate Reactive

<dl><dt><strong>💡 TIP</strong></dt><dd>

You will notice that some properties
contain "jdbc" in their name: this is because Hibernate ORM refers to its "data access" layer as "JDBC" for historical reasons. Hibernate Reactive uses Vert.x Reactive SQL clients for its data access layer rather than JDBC.

Regardless of their name, these properties still make sense for Hibernate Reactive.
</dd></dl>

**📌 NOTE**\
La tabla de configuracion generada `quarkus-hibernate-orm` se produce al construir la documentacion y no existe en el codigo fuente. Consulta la referencia de configuracion en https://quarkus.io/guides/all-config
