# Configure data sources in Quarkus

> **Guia oficial:** <https://quarkus.io/guides/datasource>  
> **Fuente:** `docs/src/main/asciidoc/datasource.adoc` en [quarkusio/quarkus@3.38.2](https://github.com/quarkusio/quarkus/blob/3.38.2/docs/src/main/asciidoc/datasource.adoc)  
> **Version documentada:** Quarkus 3.38.2 · **Sincronizado:** 2026-08-17 · **Licencia:** Apache-2.0

Use a unified configuration model to define data sources for Java Database Connectivity (JDBC) and Reactive drivers.

Applications use datasources to access relational databases.
Quarkus provides a unified configuration model to define datasources for Java Database Connectivity (JDBC) and Reactive database drivers.

Quarkus uses [Agroal](https://agroal.github.io/) and [Vert.x](https://vertx.io/) to provide high-performance, scalable datasource connection pooling for JDBC and reactive drivers.
The `quarkus-jdbc-\*` and `quarkus-reactive-*-client` extensions provide build-time optimizations and integrate configured datasources with Quarkus features such as security, health checks, and metrics.

For more information about consuming and using a reactive datasource, see the Quarkus [Reactive SQL clients](reactive-sql-clients.md) guide.

Additionally, refer to the Quarkus [Hibernate ORM](https://quarkus.io/guides/hibernate-orm) guide for information about consuming and using a JDBC datasource.

## Get started with configuring `datasources` in Quarkus

For users familiar with the fundamentals, this section provides an overview and code samples to set up datasources quickly.

For more advanced configuration with examples, see [References](#references).

### Zero-config setup in development mode

Quarkus simplifies database configuration by offering the Dev Services feature, enabling zero-config database setup for testing or running in development (dev) mode.
In dev mode, the suggested approach is to use DevServices and let Quarkus handle the database for you, whereas for production mode, you provide explicit database configuration details pointing to a database managed outside of Quarkus.

To use Dev Services, add the appropriate driver extension, such as `jdbc-postgresql`, for your desired database type to the `pom.xml` file.
In dev mode, if you do not provide any explicit database connection details, Quarkus automatically handles the database setup and provides the wiring between the application and the database.

When you provide user credentials, Quarkus configures the database to use them.
This helps when you connect to the database with an external tool.

To use this feature, ensure a Docker or Podman container runtime is installed, depending on the database type.
Certain databases, such as H2, operate in in-memory mode and do not require a container runtime.

**💡 TIP**\
Prefix the actual connection details for prod mode with `%prod.` to ensure they are not applied in dev mode.
For more information, see the [Profiles](../01-fundamentos/config-reference.md#profiles) section of the "Configuration reference" guide.

For more information about Dev Services, see [Dev Services overview](../09-testing/dev-services.md).

For more details and optional configurations, see [Dev Services for databases](databases-dev-services.md).

### Configure a JDBC datasource

1. Add the correct JDBC extension for the database of your choice.
   * `quarkus-jdbc-db2`
   * `quarkus-jdbc-h2`
   * `quarkus-jdbc-mariadb`
   * `quarkus-jdbc-mssql`
   * `quarkus-jdbc-mysql`
   * `quarkus-jdbc-oracle`
   * `quarkus-jdbc-postgresql`
2. Configure your JDBC datasource:

   ```properties
   quarkus.datasource.db-kind=postgresql ①
   quarkus.datasource.username=<your username>
   quarkus.datasource.password=<your password>

   quarkus.datasource.jdbc.url=jdbc:postgresql://localhost:5432/hibernate_orm_test
   quarkus.datasource.jdbc.max-size=16
   ```
   1. This configuration value is only required if there is more than one database extension on the classpath.

If only one viable extension is available, Quarkus assumes this is the correct one.
When you add a driver to the test scope, Quarkus automatically includes it in testing.

#### JDBC connection pool size adjustment

To protect your database from overload during load peaks, size the pool appropriately to throttle the database load.
The optimal pool size depends on many factors, such as the number of parallel application users or the nature of the workload.

Be aware that setting the pool size too low might cause some requests to time out while waiting for a connection.

For more information about pool size adjustment properties, see the [JDBC configuration reference](#jdbc-configuration-reference) section.

### Configure a reactive datasource

1. Add the correct reactive extension for the database of your choice.
   * `quarkus-reactive-db2-client`
   * `quarkus-reactive-mssql-client`
   * `quarkus-reactive-mysql-client`
   * `quarkus-reactive-oracle-client`
   * `quarkus-reactive-pg-client`
2. Configure your reactive datasource:

   ```properties
   quarkus.datasource.db-kind=postgresql ①
   quarkus.datasource.username=<your username>
   quarkus.datasource.password=<your password>

   quarkus.datasource.reactive.url=postgresql:///your_database
   quarkus.datasource.reactive.max-size=20
   ```
   1. This configuration value is only required if there is more than one Reactive driver extension on the classpath.

## Configure datasources

The following section describes the configuration for single or multiple datasources.
For simplicity, we will reference a single datasource as the default (unnamed) datasource.

### Configure a single datasource

A datasource can be JDBC, reactive, or both.
This depends on the configuration and the selection of project extensions.

1. Define a datasource with the following configuration property, where `db-kind` defines which database platform to connect to, for example, `h2`:

   ```properties
   quarkus.datasource.db-kind=h2
   ```

   Quarkus derives the JDBC driver class from the `db-kind` database platform value.

   <dl><dt><strong>📌 NOTE</strong></dt><dd>

   This step is required only if your application depends on multiple database drivers.
   If the application uses a single driver, Quarkus detects that driver automatically.
   </dd></dl>

   Quarkus currently includes the following built-in database kinds:
   * DB2: `db2`
   * H2: `h2`
   * MariaDB: `mariadb`
   * Microsoft SQL Server: `mssql`
   * MySQL: `mysql`
   * Oracle: `oracle`
   * PostgreSQL: `postgresql`, `pgsql` or `pg`
   * To use a database kind that is not built-in, use `other` and define the JDBC driver explicitly

     <dl><dt><strong>📌 NOTE</strong></dt><dd>

     You can use any JDBC driver in a Quarkus app in JVM mode as described in [Custom databases and drivers](#custom-databases-and-drivers).
     However, using a non-built-in database kind is unlikely to work when compiling your application to a native executable.

     For native executable builds, it is recommended to either use the available JDBC Quarkus extensions or contribute a custom extension for your specific driver.
     </dd></dl>
2. Configure the following properties to define credentials:

   ```properties
   quarkus.datasource.username=<your username>
   quarkus.datasource.password=<your password>
   ```

   You can also retrieve the password from Vault by [using a credential provider](https://docs.quarkiverse.io/quarkus-vault/dev/vault-datasource.html) for your datasource.

Until now, the configuration has been the same regardless of whether you are using a JDBC or a reactive driver.
After you define the database kind and credentials, the rest depends on the driver you are using.
It is possible to use JDBC and a reactive driver simultaneously.

#### JDBC datasource

JDBC is the most common database connection pattern, typically needed when used in combination with non-reactive Hibernate ORM.

1. To use a JDBC datasource, start by adding the necessary dependencies:
   1. For use with a built-in JDBC driver, choose and add the Quarkus extension for your relational database driver from the list below:

      * H2 - `quarkus-jdbc-h2`

        <dl><dt><strong>📌 NOTE</strong></dt><dd>

        You can configure H2 databases to run in "embedded mode"

        For suggestions regarding integration testing, see [Testing with in-memory databases](#testing-with-in-memory-databases) .
        </dd></dl>
      * DB2 - `quarkus-jdbc-db2`
      * MariaDB - `quarkus-jdbc-mariadb`
      * Microsoft SQL Server - `quarkus-jdbc-mssql`
      * MySQL - `quarkus-jdbc-mysql`
      * Oracle - `quarkus-jdbc-oracle`
      * PostgreSQL - `quarkus-jdbc-postgresql`
      * Other JDBC extensions, such as [SQLite](https://github.com/quarkiverse/quarkus-jdbc-sqlite) and its [documentation](https://docs.quarkiverse.io/quarkus-jdbc-sqlite/dev/index.html), can be found in the [Quarkiverse](https://github.com/quarkiverse).

        For example, to add the PostgreSQL driver dependency:

        ```bash
        ./mvnw quarkus:add-extension -Dextensions="jdbc-postgresql"
        ```

        <dl><dt><strong>📌 NOTE</strong></dt><dd>

        When you add a built-in JDBC driver extension, Quarkus also adds the `quarkus-agroal` extension.
        Agroal provides the JDBC connection pool for built-in and custom JDBC drivers.
        When you use a custom JDBC driver, add `quarkus-agroal` explicitly.
        </dd></dl>
   2. For use with a custom JDBC driver, add the `quarkus-agroal` dependency to your project alongside the extension for your relational database driver:

      ```bash
      ./mvnw quarkus:add-extension -Dextensions="agroal"
      ```

      To use a JDBC driver for another database, [use a database with no built-in extension or with a different driver](#custom-databases-and-drivers).
2. Configure the JDBC connection by defining the JDBC URL property:

   ```properties
   quarkus.datasource.jdbc.url=jdbc:postgresql://localhost:5432/hibernate_orm_test
   ```

   <dl><dt><strong>📌 NOTE</strong></dt><dd>

   Note the `jdbc` prefix in the property name.
   All JDBC-specific configuration properties have the `jdbc` prefix.
   For reactive datasources, the prefix is `reactive`.
   </dd></dl>

For more information about configuring JDBC, see [JDBC URL format reference](#jdbc-url-reference) and [Quarkus extensions and database drivers reference](#quarkus-extensions-and-database-drivers-reference).

##### Custom databases and drivers

If Quarkus does not provide a JDBC extension for your database, or you need to use a different JDBC driver, such as one for OpenTelemetry, you can configure the JDBC driver explicitly.

Without an extension, JDBC drivers are expected to work correctly in JVM mode.
However, they are unlikely to function when compiling your application into a native executable.
To build a native executable, use an existing Quarkus JDBC extension or contribute a new extension for your driver.

```properties
quarkus.datasource.db-kind=other
quarkus.datasource.jdbc.driver=oracle.jdbc.driver.OracleDriver
quarkus.datasource.jdbc.url=jdbc:oracle:thin:@192.168.1.12:1521/ORCL_SVC
quarkus.datasource.username=scott
quarkus.datasource.password=tiger
```

For details about JDBC configuration options and configuring other aspects, such as the connection pool size, refer to the [JDBC configuration reference](#jdbc-configuration-reference) section.

##### Consuming the datasource

With Hibernate ORM, the Hibernate layer automatically picks up the datasource and uses it.

For the in-code access to the datasource, obtain it as any other bean as follows:

```java
@Inject
AgroalDataSource defaultDataSource;
```

In the above example, the type is `AgroalDataSource`, a `javax.sql.DataSource` subtype.
Because of this, you can also use `javax.sql.DataSource` as the injected type.

##### Oracle considerations

As documented in [issue #36265](https://github.com/quarkusio/quarkus/issues/36265), Oracle unexpectedly commits uncommitted transactions when closing a connection.
This means that when stopping Quarkus, in-progress transactions might be committed even if they are incomplete.

Because this behavior is unexpected and can lead to data loss, an interceptor rolls back any unfinished transactions when closing a connection.
However, if you use XA transactions, the transaction manager handles the rollback.

If the behavior introduced in 3.18 causes issues for your workload, deactivate it by setting the `-Dquarkus-oracle-no-automatic-rollback-on-connection-close` system property to `true`.
Make sure to report your use case in the [issue tracker](https://github.com/quarkusio/quarkus/issues) so we can adjust this behavior if needed, for example, with more permanent settings.

#### Reactive datasource

Quarkus offers several reactive clients for use with a reactive datasource.

1. Add the corresponding extension to your application:

   * DB2: `quarkus-reactive-db2-client`
   * MariaDB/MySQL: `quarkus-reactive-mysql-client`
   * Microsoft SQL Server: `quarkus-reactive-mssql-client`
   * Oracle: `quarkus-reactive-oracle-client`
   * PostgreSQL: `quarkus-reactive-pg-client`

     The installed extension must be consistent with the `quarkus.datasource.db-kind` you define in your datasource configuration.
2. After adding the driver, configure the connection URL and define a proper size for your connection pool.

   ```properties
   quarkus.datasource.reactive.url=postgresql:///your_database
   quarkus.datasource.reactive.max-size=20
   ```

##### Reactive connection pool size adjustment

To protect your database from overload during load peaks, set the pool size to throttle database load.
The correct pool size depends on factors such as the number of concurrent users and the workload type.

Be aware that setting the pool size too low might cause some requests to time out while waiting for a connection.

For more information about pool size adjustment properties, see the [Reactive datasource configuration reference](#reactive-datasource-configuration-reference) section.

#### JDBC and reactive datasources simultaneously

When you add both a JDBC extension and a reactive datasource extension for the same `db-kind`, Quarkus creates both JDBC and reactive datasources by default.

* To use the [JDBC](#jdbc-datasource) and [reactive](#reactive-datasource) datasources simultaneously:

  ```properties
  %prod.quarkus.datasource.reactive.url=postgresql:///your_database
  %prod.quarkus.datasource.jdbc.url=jdbc:postgresql://localhost:5432/hibernate_orm_test
  ```

If you do not want to have both a JDBC datasource and a reactive datasource created, use the following configuration.

* To disable the JDBC datasource explicitly:

  ```properties
  quarkus.datasource.jdbc=false
  ```
* To disable the reactive datasource explicitly:

  ```properties
  quarkus.datasource.reactive=false
  ```

  <dl><dt><strong>💡 TIP</strong></dt><dd>

  In most cases, the configuration above will be optional as either a JDBC driver or a reactive datasource extension will be present, not both.
  </dd></dl>

### Configure multiple datasources

<dl><dt><strong>📌 NOTE</strong></dt><dd>

The Hibernate ORM extension supports defining [persistence units](https://quarkus.io/guides/hibernate-orm#multiple-persistence-units) by using configuration properties.
For each persistence unit, point to the datasource of your choice.
</dd></dl>

Defining multiple datasources works like defining a single datasource, with one important change - you have to specify a name (configuration property) for each datasource.

The following example provides three different datasources:

* the default one
* a datasource named `users`
* a datasource named `inventory`

Each with its configuration:

```properties
quarkus.datasource.db-kind=h2
quarkus.datasource.username=username-default
quarkus.datasource.jdbc.url=jdbc:h2:mem:default
quarkus.datasource.jdbc.max-size=13

quarkus.datasource.users.db-kind=h2
quarkus.datasource.users.username=username1
quarkus.datasource.users.jdbc.url=jdbc:h2:mem:users
quarkus.datasource.users.jdbc.max-size=11

quarkus.datasource.inventory.db-kind=h2
quarkus.datasource.inventory.username=username2
quarkus.datasource.inventory.jdbc.url=jdbc:h2:mem:inventory
quarkus.datasource.inventory.jdbc.max-size=12
```

Notice there is an extra section in the configuration property.
The syntax is as follows: `quarkus.datasource.[optional name.][datasource property]`.

<dl><dt><strong>📌 NOTE</strong></dt><dd>

Even when you install only one database extension, named datasources must set at least one build-time property so Quarkus can detect them.
In most cases, set `db-kind`.

You can also set Dev Services properties to create named datasources as described in the [Dev Services for Databases](databases-dev-services.md) guide.
</dd></dl>

#### Named datasource injection

When you configure multiple datasources, each `DataSource` also has the `io.quarkus.agroal.DataSource` qualifier with the datasource name as the value.

After you configure three datasources as described in the previous section, inject each datasource as follows:

```java
@Inject
AgroalDataSource defaultDataSource;

@Inject
@DataSource("users")
AgroalDataSource usersDataSource;

@Inject
@DataSource("inventory")
AgroalDataSource inventoryDataSource;
```

### Activate or deactivate datasources

When a datasource is configured at build time, and its URL is set at runtime, it is active by default.
Quarkus starts the corresponding JDBC connection pool or reactive client when the application starts.

To deactivate a datasource at runtime, either:

* Do not set `quarkus.datasource[.optional name].jdbc.url` or `quarkus.datasource[.optional name].reactive.url`.
* Set `quarkus.datasource[.optional name].active` to `false`.

If a datasource is not active:

* The datasource does not attempt to connect to the database during application startup.
* The datasource does not contribute a [health check](#datasource-health-check).
* Static CDI injection points involving the datasource, such as `@Inject DataSource ds` or `@Inject Pool pool`, cause application startup to fail.
* Dynamic retrieval of the datasource, such as through `CDI.getBeanContainer()`, `Arc.instance()`, or an injected `Instance<DataSource>`, causes an exception to be thrown.
* Other Quarkus extensions that consume the datasource may cause application startup to fail.

  In this case, you must also deactivate those other extensions.
  To see an example of this scenario, refer to the [Activate/deactivate persistence units](https://quarkus.io/guides/hibernate-orm#persistence-unit-active) section of the Hibernate ORM guide.
  For Hibernate ORM, Quarkus deactivates the persistence unit when the datasource is inactive.

This feature is especially useful when the application must select one datasource from a predefined set at runtime.

```properties
quarkus.datasource."pg".db-kind=postgres
quarkus.datasource."pg".active=false
quarkus.datasource."pg".jdbc.url=jdbc:postgresql:///your_database

quarkus.datasource."oracle".db-kind=oracle
quarkus.datasource."oracle".active=false
quarkus.datasource."oracle".jdbc.url=jdbc:oracle:thin:@localhost:1521/your_database
```

Setting `quarkus.datasource."pg".active=true` [at runtime](../01-fundamentos/config-reference.md#configuration-sources) makes only the PostgreSQL datasource available.
Setting `quarkus.datasource."oracle".active=true` at runtime makes only the Oracle datasource available.

<dl><dt><strong>💡 TIP</strong></dt><dd>

[Custom configuration profiles](../01-fundamentos/config-reference.md#custom-profiles) simplify this setup.
By appending the following profile-specific configuration to the one above, you can select a persistence unit or datasource at runtime by [setting `quarkus.profile`](../01-fundamentos/config-reference.md#multiple-profiles).
For example, use `quarkus.profile=prod,pg` or `quarkus.profile=prod,oracle`.

```properties
%pg.quarkus.hibernate-orm."pg".active=true
%pg.quarkus.datasource."pg".active=true
# Add any PostgreSQL-related runtime configuration here, prefixed with "%pg."

%oracle.quarkus.hibernate-orm."oracle".active=true
%oracle.quarkus.datasource."oracle".active=true
# Add any Oracle-related runtime configuration here, prefixed with "%oracle."
```
</dd></dl>

With this setup, ensure that only the _active_ datasource is accessed.
To achieve this, inject an `InjectableInstance<DataSource>` or `InjectableInstance<Pool>` with an `@Any` qualifier and call [`getActive()`](https://quarkus.io/guides/cdi-integration#inactive-synthetic-beans).

```java
import io.quarkus.arc.InjectableInstance;
@ApplicationScoped
public class MyConsumer {
    @Inject
    @Any
    InjectableInstance<DataSource> dataSource;

    public void doSomething() {
        DataSource activeDataSource = dataSource.getActive();
        // ...
    }
}
```

Alternatively, define a [CDI bean producer](../01-fundamentos/cdi.md#ok-you-said-that-there-are-several-kinds-of-beans) for the default datasource.
The bean producer redirects to the active named datasource.
The application can then inject the default datasource directly, as shown below:

```java
public class MyProducer {
    @Inject
    @DataSource("pg")
    InjectableInstance<DataSource> pgDataSourceBean; // ①

    @Inject
    @DataSource("oracle")
    InjectableInstance<DataSource> oracleDataSourceBean;

    @Produces // ②
    @ApplicationScoped
    public DataSource dataSource() {
        if (pgDataSourceBean.getHandle().getBean().isActive()) { // ③
            return pgDataSourceBean.get();
        } else if (oracleDataSourceBean.getHandle().getBean().isActive()) { // ③
            return oracleDataSourceBean.get();
        } else {
            throw new RuntimeException("No active datasource!");
        }
    }
}

@ApplicationScoped
public class MyConsumer {
    @Inject
    DataSource dataSource; // ④

    public void doSomething() {
        // .. just use the injected datasource ...
    }
}
```
1. Do not inject a `DataSource` or `AgroalDatasource` directly.
Injecting inactive beans causes a startup failure.
Instead, inject `InjectableInstance<DataSource>` or `InjectableInstance<AgroalDataSource>`.
2. Declare a CDI producer method to define the default datasource.
It selects either PostgreSQL or Oracle, depending on which one is active.
3. Check if a bean is active before retrieving it.
4. Injects the only active datasource.

### Use multiple datasources in a single transaction

By default, XA support on datasources is disabled.
Therefore, a transaction may include no more than one datasource.
Attempting to access multiple non-XA datasources in the same transaction results in an exception similar to the following:

```
...
Caused by: java.sql.SQLException: Exception in association of connection to existing transaction
        at io.agroal.narayana.NarayanaTransactionIntegration.associate(NarayanaTransactionIntegration.java:130)
        ...
Caused by: java.sql.SQLException: Failed to enlist. Check if a connection from another datasource is already enlisted to the same transaction
        at io.agroal.narayana.NarayanaTransactionIntegration.associate(NarayanaTransactionIntegration.java:121)
        ...
```

To allow using multiple JDBC datasources in the same transaction:

1. Make sure your JDBC driver supports XA.
All [supported JDBC drivers do](#quarkus-extensions-and-database-drivers-reference), but [other JDBC drivers](#custom-databases-and-drivers) might not.
2. Make sure your database server is configured to enable XA.
3. Enable XA support explicitly for each relevant datasource by setting [`quarkus.datasource[.optional name](#quarkus-agroal_quarkus-datasource-jdbc-transactions).jdbc.transactions`] to `xa`.

Using XA, a rollback in one datasource will trigger a rollback in every other datasource enrolled in the transaction.

<dl><dt><strong>📌 NOTE</strong></dt><dd>

XA transactions on reactive datasources are not supported at the moment.
</dd></dl>

<dl><dt><strong>📌 NOTE</strong></dt><dd>

If your transaction involves non-datasource resources, be aware that they might not support XA transactions or might require additional configuration.
</dd></dl>

If XA cannot be enabled for one of your datasources:

* Be aware that enabling XA for all datasources _except one_ (and only one) is still supported through [Last Resource Commit Optimization (LRCO)](https://www.narayana.io/docs/project/index.html#_last_resource_commit_optimization_lrco).
* If you do not need a rollback for one datasource to trigger a rollback for other datasources, consider splitting your code into multiple transactions.
To do so, use [`QuarkusTransaction.requiringNew()`](transaction.md#programmatic-approach)/[`@Transactional(REQUIRES_NEW)`](transaction.md#declarative-approach) (preferably) or [`UserTransaction`](transaction.md#legacy-api-approach) (for more complex use cases).

<dl><dt><strong>🔥 CAUTION</strong></dt><dd>

If no other solution works and compatibility with Quarkus 3.8 or earlier is required, set `quarkus.transaction-manager.unsafe-multiple-last-resources` to `allow` to enable unsafe transaction handling across multiple non-XA datasources.

With this property set to `allow`, a transaction rollback might only apply to the last non-XA datasource, while other non-XA datasources may have already committed their changes.
This can leave the system in an inconsistent state.

Alternatively, allow the same unsafe behavior but with warnings when it occurs:

* Setting the property to `warn-each` logs a warning for **each** offending transaction.
* Setting the property to `warn-first` logs a warning for the **first** offending transaction.

We do not recommend using this configuration property and plan to remove it in the future.
You should update your application accordingly.
If you believe your use case justifies keeping this option, open an issue in the [Quarkus tracker](https://github.com/quarkusio/quarkus/issues/new?assignees=&labels=kind%2Fenhancement&projects=&template=feature_request.yml) explaining why.
</dd></dl>

## Datasource integrations

### Datasource health check

If you use the [`quarkus-smallrye-health`](https://quarkus.io/extensions/io.quarkus/quarkus-smallrye-health) extension, the `quarkus-agroal` and reactive client extensions automatically add a readiness health check to validate the datasource.

When you access your application’s health readiness endpoint, `/q/health/ready` by default, you receive information about the datasource validation status.
If you have multiple datasources, all datasources are checked, and if a single datasource validation failure occurs, the status changes to `DOWN`.

You can disable this behavior by setting `quarkus.datasource.health.enabled=false`.

To exclude only a particular datasource from the health check:

```properties
quarkus.datasource."datasource-name".health-exclude=true
```

### Datasource metrics

When you add the [`quarkus-micrometer`](../07-observabilidad/telemetry-micrometer.md) extension, `quarkus-agroal` can publish datasource metrics to the metrics registry.
To enable these metrics, set `quarkus.datasource.metrics.enabled=true`.

For the published metrics to report values, Agroal must enable its internal metrics collection.
By default, Agroal enables internal metrics collection for all datasources when a metrics extension is present and `quarkus.datasource.metrics.enabled` is set to `true`.

To disable metrics for a specific datasource, set `quarkus.datasource.jdbc.metrics.enabled=false`.
For a named datasource, set `quarkus.datasource.<datasource name>.jdbc.metrics.enabled=false`.
This setting stops internal metrics collection and stops exposing datasource metrics at the `/q/metrics` endpoint.

To enable internal metrics collection explicitly for the default data source, set `quarkus.datasource.jdbc.metrics.enabled=true`.
To enable internal metrics collection explicitly for a named data source, set `quarkus.datasource.<datasource name>.jdbc.metrics.enabled=true`.
This enables internal metrics collection even when you do not add a metrics extension.
You can access the collected metrics programmatically by calling `dataSource.getMetrics()` on an injected `AgroalDataSource` instance.

When metrics collection is disabled for a data source, all metric values are zero.

### Datasource tracing

To use tracing with a datasource, you need to add the [`quarkus-opentelemetry`](../07-observabilidad/opentelemetry-tracing.md) extension to your project.

You do not need to declare a different driver to enable tracing.
If you use a JDBC driver, you need to follow [the instructions in the OpenTelemetry extension](../07-observabilidad/opentelemetry-tracing.md#jdbc).

Even with all the tracing infrastructure in place, the datasource tracing is not enabled by default, and you need to enable it by setting this property:
```properties
# enable tracing
quarkus.datasource.jdbc.telemetry=true
```

By default, only SQL statement executions are traced.
Connection acquisition from the datasource (`getConnection()` calls) is not traced.
To also trace connection acquisition, enable it explicitly:
```properties
quarkus.datasource.jdbc.telemetry.trace-connection=true
```

### Narayana transaction manager integration

Integration is automatic if the Narayana JTA extension is also available.

You can override this by setting the `transactions` configuration property:

* `quarkus.datasource.jdbc.transactions` for default unnamed datasource
* `quarkus.datasource._<datasource-name>_.jdbc.transactions` for named datasource

When a datasource is configured for XA transactions by setting `quarkus.datasource[.optional name].jdbc.transactions=xa` and the transaction recovery system is enabled by using `quarkus.transaction-manager.enable-recovery=true`, the datasource is automatically registered for recovery.
This is the preferred and safe default.
You can override this behavior for individual datasources by setting `quarkus.datasource.jdbc.enable-recovery=false` or `quarkus.datasource."datasource-name".jdbc.enable-recovery=false`.

<dl><dt><strong>❗ IMPORTANT</strong></dt><dd>

Change this setting only in advanced use cases and only if you are certain recovery is not required.
Incorrect configuration can lead to data loss, data unavailability, or both, due to resources remaining locked indefinitely.
</dd></dl>

For more information, see the [Configuration reference](#common-datasource-configuration-reference) section below.
To facilitate the storage of transaction logs in a database by using JDBC, see the [Configuring transaction logs to be stored in a datasource](transaction.md#jdbcstore) section of the [Using transactions in Quarkus](transaction.md) guide.

### Testing with in-memory databases

The recommended approach for testing against databases is to use the same database as production to get test results that match production behavior as closely as possible.
[Dev Services](databases-dev-services.md) simplifies this approach by requiring no configuration and starting quickly.

For scenarios where neither Dev Services nor a custom database setup is possible, you can use a JVM based database such as H2 in embedded mode.

#### Support and limitations

Embedded databases such as H2 work in JVM mode.

In native mode, embedding H2 in the native image is not recommended.
Use a remote connection to a separate database, or use Dev Services to run the database outside the native image.

#### Run an integration test

1. Add a dependency on the artifacts providing the additional tools that are under the following Maven coordinates:

   * `io.quarkus:quarkus-test-h2` for H2

     You can test your application even when it is compiled into a native executable, while the database will run as a JVM process.
2. Add the following annotation to any class in your integration tests to run the tests on both the JVM and native executables:

   * `@QuarkusTestResource(H2DatabaseTestResource.class)`

     This ensures that the test suite starts and terminates the managed database in a separate process as required for test execution.

     **H2 example**

     ```java
     package my.app.integrationtests.db;

     import io.quarkus.test.common.QuarkusTestResource;
     import io.quarkus.test.h2.H2DatabaseTestResource;

     @QuarkusTestResource(H2DatabaseTestResource.class)
     public class TestResources {
     }
     ```
3. Configure the connection to the managed database:

   ```properties
   quarkus.datasource.db-kind=h2
   quarkus.datasource.jdbc.url=jdbc:h2:tcp://localhost/mem:test
   ```

## References

### Common datasource configuration reference

**📌 NOTE**\
La tabla de configuracion generada `quarkus-datasource` se produce al construir la documentacion y no existe en el codigo fuente. Consulta la referencia de configuracion en https://quarkus.io/guides/all-config

### JDBC configuration reference

**📌 NOTE**\
La tabla de configuracion generada `quarkus-agroal` se produce al construir la documentacion y no existe en el codigo fuente. Consulta la referencia de configuracion en https://quarkus.io/guides/all-config

### JDBC URL reference

Each supported database has its own JDBC URL configuration options.
The following sections describe each JDBC URL and provide a link to the official documentation.

#### DB2

`jdbc:db2://<serverName>[:<portNumber>]/<databaseName>[:<key1>=<value>;[<key2>=<value2>;]]`

* **Example**\
`jdbc:db2://localhost:50000/MYDB:user=dbadm;password=dbadm;`

For more information on URL syntax and additional supported options, see the [official documentation](https://www.ibm.com/support/knowledgecenter/SSEPGG_11.5.0/com.ibm.db2.luw.apdv.java.doc/src/tpc/imjcc_r0052342.html).

#### H2

`jdbc:h2:{ {.|mem:}[name] | [file:]fileName | {tcp|ssl}:[//]server[:port][,server2[:port]]/name }[;key=value...]`

* **Example**\
`jdbc:h2:tcp://localhost/~/test`, `jdbc:h2:mem:myDB`

H2 is a database that can run in embedded or server mode.
It can use a file storage or run entirely in memory.
All of these options are available as listed above.

For more information, see the [official documentation](https://h2database.com/html/features.html#database_url).

#### MariaDB

`jdbc:mariadb:[replication:|failover:|sequential:|aurora:]//<hostDescription>[,<hostDescription>...]/[database][?<key1>=<value1>[&<key2>=<value2>]]`
hostDescription:: `<host>[:<portnumber>] or address=(host=<host>)[(port=<portnumber>)][(type=(master|slave))]`

* **Example**\
`jdbc:mariadb://localhost:3306/test`

For more information, see the [official documentation](https://mariadb.com/kb/en/library/about-mariadb-connector-j/).

#### Microsoft SQL server

`jdbc:sqlserver://[serverName[\instanceName][:portNumber]][;property=value[;property=value]]`

* **Example**\
`jdbc:sqlserver://localhost:1433;databaseName=AdventureWorks`

For more information, see the [official documentation](https://docs.microsoft.com/en-us/sql/connect/jdbc/connecting-to-sql-server-with-the-jdbc-driver?view=sql-server-2017).

#### MySQL

`jdbc:mysql:[replication:|failover:|sequential:|aurora:]//<hostDescription>[,<hostDescription>...]/[database][?<key1>=<value1>[&<key2>=<value2>]]`
hostDescription:: `<host>[:<portnumber>] or address=(host=<host>)[(port=<portnumber>)][(type=(master|slave))]`

* **Example**\
`jdbc:mysql://localhost:3306/test`

For more information, see the [official documentation](https://dev.mysql.com/doc/connector-j/en/).

##### MySQL limitations

When you compile an application into a native image, the following limitations apply to MySQL Connector/J integrations:

* Quarkus disables Java Management Extensions (JMX) support because it does not work in native mode.
* Quarkus disables Oracle Cloud Infrastructure (OCI) integration because it does not work in native mode.
* Quarkus disables the MySQL Connector/J OpenTelemetry integration and relies on the Agroal integration instead.

  If you need the MySQL Connector/J OpenTelemetry integration, enable it explicitly by setting `quarkus.datasource.jdbc.additional-jdbc-properties.openTelemetry=PREFERRED`.
  For more information, see [MySQL Connector/J documentation](https://dev.mysql.com/doc/connector-j/en/connector-j-connp-props-debugging-profiling.html#cj-conn-prop_openTelemetry).

  When you enable this option and also add the `quarkus-opentelemetry` extension, the application can fail to start and throw a `java.lang.IllegalStateException: GlobalOpenTelemetry.set has already been called.` error.

#### Oracle

`jdbc:oracle:driver_type:@database_specifier`

* **Example**\
`jdbc:oracle:thin:@localhost:1521/ORCL_SVC`

For more information, see the [official documentation](https://docs.oracle.com/en/database/oracle/oracle-database/21/jjdbc/data-sources-and-URLs.html#GUID-AEA8E228-1B21-4111-AF4C-B1F33744CA08).

#### PostgreSQL

`jdbc:postgresql:[//][host][:port][/database][?key=value...]`

* **Example**\
`jdbc:postgresql://localhost/test`

The defaults for the different parts are as follows:

* **`host`**\
localhost
* **`port`**\
5432
* **`database`**\
same name as the username

For more information about additional parameters, see the [official documentation](https://jdbc.postgresql.org/documentation/head/connect.html).

### Quarkus extensions and database drivers reference

The following tables list the built-in `db-kind` values, the corresponding Quarkus extensions, and the JDBC drivers used by those extensions.

When using one of the built-in datasource kinds, the JDBC and Reactive drivers are resolved automatically to match the values from these tables.

**Database platform kind to JDBC driver mapping**

| Database kind | Quarkus extension | Drivers |
| :-: | :-: | --- |
| `db2` | `quarkus-jdbc-db2` | * JDBC: `com.ibm.db2.jcc.DB2Driver` * XA: `com.ibm.db2.jcc.DB2XADataSource` |
| `h2` | `quarkus-jdbc-h2` | * JDBC: `org.h2.Driver` * XA: `org.h2.jdbcx.JdbcDataSource` |
| `mariadb` | `quarkus-jdbc-mariadb` | * JDBC: `org.mariadb.jdbc.Driver` * XA: `org.mariadb.jdbc.MariaDbDataSource` |
| `mssql` | `quarkus-jdbc-mssql` | * JDBC: `com.microsoft.sqlserver.jdbc.SQLServerDriver` * XA: `com.microsoft.sqlserver.jdbc.SQLServerXADataSource` |
| `mysql` | `quarkus-jdbc-mysql` | * JDBC: `com.mysql.cj.jdbc.Driver` * XA: `com.mysql.cj.jdbc.MysqlXADataSource` |
| `oracle` | `quarkus-jdbc-oracle` | * JDBC: `oracle.jdbc.driver.OracleDriver` * XA: `oracle.jdbc.xa.client.OracleXADataSource` |
| `postgresql` | `quarkus-jdbc-postgresql` | * JDBC: `org.postgresql.Driver` * XA: `org.postgresql.xa.PGXADataSource` |

**Database kind to Reactive driver mapping**

| Database kind | Quarkus extension | Driver |
| :-: | :-: | --- |
| `oracle` | `reactive-oracle-client` | `io.vertx.oracleclient.spi.OracleDriver` |
| `mysql` | `reactive-mysql-client` | `io.vertx.mysqlclient.spi.MySQLDriver` |
| `mssql` | `reactive-mssql-client` | `io.vertx.mssqlclient.spi.MSSQLDriver` |
| `postgresql` | `reactive-pg-client` | `io.vertx.pgclient.spi.PgDriver` |
| `db2` | `reactive-db2-client` | `io.vertx.db2client.spi.DB2Driver` endif::no-quarkus-reactive-db2-client[] |

<dl><dt><strong>💡 TIP</strong></dt><dd>

This automatic resolution is applicable in most cases so that driver configuration is not needed.
</dd></dl>

### Reactive datasource configuration reference

**📌 NOTE**\
La tabla de configuracion generada `quarkus-reactive-datasource` se produce al construir la documentacion y no existe en el codigo fuente. Consulta la referencia de configuracion en https://quarkus.io/guides/all-config

#### Reactive DB2 configuration

**📌 NOTE**\
La tabla de configuracion generada `quarkus-reactive-db2-client` se produce al construir la documentacion y no existe en el codigo fuente. Consulta la referencia de configuracion en https://quarkus.io/guides/all-config

#### Reactive MariaDB/MySQL specific configuration

**📌 NOTE**\
La tabla de configuracion generada `quarkus-reactive-mysql-client` se produce al construir la documentacion y no existe en el codigo fuente. Consulta la referencia de configuracion en https://quarkus.io/guides/all-config

#### Reactive Microsoft SQL server-specific configuration

**📌 NOTE**\
La tabla de configuracion generada `quarkus-reactive-mssql-client` se produce al construir la documentacion y no existe en el codigo fuente. Consulta la referencia de configuracion en https://quarkus.io/guides/all-config

#### Reactive Oracle-specific configuration

**📌 NOTE**\
La tabla de configuracion generada `quarkus-reactive-oracle-client` se produce al construir la documentacion y no existe en el codigo fuente. Consulta la referencia de configuracion en https://quarkus.io/guides/all-config

#### Reactive PostgreSQL-specific configuration

**📌 NOTE**\
La tabla de configuracion generada `quarkus-reactive-pg-client` se produce al construir la documentacion y no existe en el codigo fuente. Consulta la referencia de configuracion en https://quarkus.io/guides/all-config

### Reactive datasource URL reference

#### DB2

`db2://[user[:[password]]@]host[:port][/database][?<key1>=<value1>[&<key2>=<value2>]]`

* **Example**\
`db2://dbuser:secretpassword@database.server.com:50000/mydb`

Currently, the client supports the following parameter keys:

* `host`
* `port`
* `user`
* `password`
* `database`

**📌 NOTE**\
Configuring parameters in the connection URL overrides the default properties.

#### Microsoft SQL server

`sqlserver://[user[:[password]]@]host[:port][/database][?<key1>=<value1>[&<key2>=<value2>]]`

* **Example**\
`sqlserver://dbuser:secretpassword@database.server.com:1433/mydb`

Currently, the client supports the following parameter keys:

* `host`
* `port`
* `user`
* `password`
* `database`

**📌 NOTE**\
Configuring parameters in the connection URL overrides the default properties.

#### MySQL / MariaDB

`mysql://[user[:[password]]@]host[:port][/database][?<key1>=<value1>[&<key2>=<value2>]]`

* **Example**\
`mysql://dbuser:secretpassword@database.server.com:3211/mydb`

Currently, the client supports the following parameter keys (case-insensitive):

* `host`
* `port`
* `user`
* `password`
* `schema`
* `socket`
* `useAffectedRows`

**📌 NOTE**\
Configuring parameters in the connection URL overrides the default properties.

#### Oracle

##### EZConnect format

`oracle:thin:@[[protocol:]//]host[:port][/service_name][:server_mode][/instance_name][?connection properties]`

* **Example**\
`oracle:thin:@mydbhost1:5521/mydbservice?connect_timeout=10sec`

##### TNS alias format

`oracle:thin:@<alias_name>[?connection properties]`

* **Example**\
`oracle:thin:@prod_db?TNS_ADMIN=/work/tns/`

#### PostgreSQL

`postgresql://[user[:[password]]@]host[:port][/database][?<key1>=<value1>[&<key2>=<value2>]]`

* **Example**\
`postgresql://dbuser:secretpassword@database.server.com:5432/mydb`

Currently, the client supports:

* Following parameter keys:
  * `host`
  * `port`
  * `user`
  * `password`
  * `dbname`
  * `sslmode`
* Additional properties, such as:
  * `application_name`
  * `fallback_application_name`
  * `search_path`
  * `options`

**📌 NOTE**\
Configuring parameters in the connection URL overrides the default properties.
