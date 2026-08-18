# Dev Services for Databases

> **Guia oficial:** <https://quarkus.io/guides/databases-dev-services>  
> **Fuente:** `docs/src/main/asciidoc/databases-dev-services.adoc` en [quarkusio/quarkus@3.38.2](https://github.com/quarkusio/quarkus/blob/3.38.2/docs/src/main/asciidoc/databases-dev-services.adoc)  
> **Version documentada:** Quarkus 3.38.2 · **Sincronizado:** 2026-08-17 · **Licencia:** Apache-2.0

When testing or running in dev mode Quarkus can provide you with a zero-config database out of the box, a feature we refer to as Dev Services.
Depending on your database type you may need Docker installed in order to use this feature.
Dev Services is supported for the following databases:

* DB2 (container) (requires [license acceptance](#proprietary-databases---license-acceptance))
* H2 (in-process)
* MariaDB (container)
* Microsoft SQL Server (container) (requires [license acceptance](#proprietary-databases---license-acceptance))
* MySQL (container)
* Oracle Express Edition (container)
* PostgreSQL (container)

If you want to use Dev Services then all you need to do is include the relevant extension for the type of database you want (either reactive or JDBC, or both).
Don’t configure a database URL, username and password - Quarkus will provide the database and you can just start coding without worrying about config.

Production databases need to be configured as normal, so if you want to include a production database config in your
`application.properties` and continue to use Dev Services we recommend that you use the `%prod.` profile to define your database settings.

## Enabling / Disabling Dev Services for Database

Dev Services for databases automatically starts a database server in dev mode and when running tests.
So, you don’t have to start a server manually.
The application is configured automatically.

You can disable the automatic database start in `application.properties` via:

```properties
quarkus.devservices.enabled=false
# OR
quarkus.datasource.devservices.enabled=false
```

Dev Services for databases relies on Docker to start the server (except for H2 which is run in process).
If your environment does not support Docker, you will need to start the server manually, or connect to an already running server.

### Proprietary Databases - License Acceptance

If you are using a proprietary database such as DB2 or MSSQL you will need to accept the license agreement.
To do this create a `src/main/resources/container-license-acceptance.txt` files in your project and add a line with the image name and tag of the database.
By default, Quarkus uses the default image for the current version of Testcontainers, if you attempt to start Quarkus the resulting failure will tell you the exact image name in use for you to add to the file.

An example file is shown below:

**src/main/resources/container-license-acceptance.txt**

```
icr.io/db2_community/db2:12.1.0.0
mcr.microsoft.com/mssql/server:2025-latest
```

Alternatively, add these entries to your `application.properties`:

```properties
# For mssql
quarkus.datasource.devservices.container-env.ACCEPT_EULA=Y

# For db2
quarkus.datasource.devservices.container-env.LICENSE=accept
```

### Capturing Logs

By default, logs of the underlying database are not exposed.
By capturing the logs, they become visible amongst other log statements:

```properties
quarkus.datasource.devservices.show-logs=true
```

## Automatic Image Selection

The container image used by Dev Services is determined by the database kind of your [datasource](datasource.md),
which is implicit if you include only one kind of JDBC or Reactive SQL client extension in your project.

For certain databases, Quarkus can further refine the image selection based on specific database features required by your application.
For example, with PostgreSQL:

* If you use Hibernate Spatial, Quarkus will automatically use a PostGIS-enabled image instead of the standard PostgreSQL image
* If you use Hibernate ORM vector types, Quarkus will automatically use a pgvector-enabled image

This automatic feature-based selection is transparent and requires no configuration.
Extensions that require specific database capabilities will declare their requirements,
and Dev Services will select the most appropriate image automatically.

Explicitly setting the image name always takes precedence over automatic selection:

```properties
quarkus.datasource.devservices.image-name=<custom-image>
```

## Reusing Dev Services

### General case

Within a dev mode session or test suite execution,
Quarkus will always reuse database Dev Services as long as their configuration
(username, password, environment, port bindings, ...) did not change.

When the configuration of any database Dev Services changes,
Quarkus will always restart all database Dev Services.

When a dev mode session or test suite execution ends,
Quarkus will (by default) stop all database Dev Services.

### Reusing Dev Service containers across runs

Assuming you rely on Dev Services based on containers (unlike H2),
if you want to keep Dev Service containers running **after a dev mode session or test suite execution**
to reuse them in the next dev mode session or test suite execution,
this is possible as well.
Just enable [TestContainers reuse](https://java.testcontainers.org/features/reuse/)
by inserting this line in one of your
[TestContainers configuration file](https://java.testcontainers.org/features/configuration/)
(generally `~/.testcontainers.properties` or `C:/Users/myuser/.testcontainers.properties`):

```properties
testcontainers.reuse.enable=true
```

<dl><dt><strong>📌 NOTE</strong></dt><dd>

Even with container reuse enabled, containers will only be reused if their startup command did not change:
same environment variables (username/password in particular), same port bindings, same volume mounts, ...
</dd></dl>

<dl><dt><strong>⚠️ WARNING</strong></dt><dd>

Reusing containers implies reusing their internal state,
including the database schema and the content of tables.

If that’s not what you want -- and if your tests write to the database, that’s probably not what you want --
consider [configuring Hibernate ORM appropriately](https://quarkus.io/guides/hibernate-orm#dev-mode),
or using [Flyway](flyway.md) or [Liquibase](liquibase.md).
</dd></dl>

<dl><dt><strong>⚠️ WARNING</strong></dt><dd>

With container reuse enabled, old containers (especially with obsolete configuration)
might be left running indefinitely, even after starting a new Quarkus dev mode session or test suite execution.

In that case, you will need to stop and remove these containers manually.
</dd></dl>

If you want to reuse containers for some Quarkus applications but not all of them,
or some Dev Services but not all of them,
you can disable this feature for a specific Dev Service by setting the configuration property
[`quarkus.datasource.devservices.reuse`/`quarkus.datasource."datasource-name".devservices.reuse`](#quarkus-datasource_quarkus-datasource-devservices_quarkus-datasource-devservices-reuse)
to `false`.

## Mapping volumes into Dev Services for Database

Mapping volumes from the Docker host’s filesystem to the containers is handy to provide files like scripts or configuration, but also to preserve database data and reuse it after an application restart.

<dl><dt><strong>📌 NOTE</strong></dt><dd>

Mapping volumes will only work in Dev Services with a container-based database like PostgreSQL.
</dd></dl>

Dev Services volumes can be mapped to the filesystem or the classpath:

```properties
# Using a filesystem volume:
quarkus.datasource.devservices.volumes."/path/from"=/container/to ①
# Using a classpath volume:
quarkus.datasource.devservices.volumes."classpath\:./file"=/container/to ②
```

1. The file or folder "/path/from" from the local machine will be accessible at "/container/to" in the container.
2. When using classpath volumes, the location has to start with "classpath:". The file or folder "./file" from the project’s classpath will be accessible at "/container/to" in the container.

**🔥 CAUTION**\
The colon character `:` needs to be escaped in `.properties` files as `\:`, or it will be interpreted as a key/value separator.

**❗ IMPORTANT**\
when using a classpath volume, the container will only be granted read permission. On the other hand, when using a filesystem volume, the container will be granted read and write permission.

### Example of mapping volumes to persist the database data

Let’s see an example using PostgreSQL where we’ll map a file system volume to keep the database data permanently and use it:

```properties
quarkus.datasource.db-kind=postgresql
quarkus.datasource.devservices.volumes."/local/test/data"=/var/lib/postgresql/data
```

The appropriate in-container location varies depending on the database vendor. For PostgreSQL is "/var/lib/postgresql/data", but for MySQL, you would need this configuration instead:

```properties
quarkus.datasource.db-kind=mysql
quarkus.datasource.devservices.volumes."/local/test/data"=/var/lib/mysql
```

When starting Dev Services (for example, in tests or in dev mode), you will see that the folder "/local/test/data" will be created at your file sytem and that will contain all the database data. When rerunning again the same Dev Services, this data will contain all the data you might have created beforehand.

<dl><dt><strong>❗ IMPORTANT</strong></dt><dd>

When using Dev Services with Hibernate ORM, by default Quarkus will wipe out the database on application startup, which will wipe out the database data on your Docker host’s filesystem.
Configure `quarkus.hibernate-orm.schema-management.strategy=none` or `quarkus.hibernate-orm.schema-management.strategy=validate` to avoid this behavior.

Also, using Flyway to migrate your schema when starting the application will modify the database data on your Docker hosts’s file system.
</dd></dl>

## Database Vendor Specific Configuration

All services based on containers are run using Testcontainers but Quarkus is not using the Testcontainers JDBC driver.
Thus, even though extra JDBC URL properties can be set in your `application.properties` file, specific properties supported by the Testcontainers JDBC driver such as `TC_INITSCRIPT`, `TC_INITFUNCTION`, `TC_DAEMON`, `TC_TMPFS` are not supported.

Quarkus can support **specific** properties sent to the container itself though, e.g. this is the case for `TC_MY_CNF` which allows to override the MariaDB/MySQL configuration file.

Overriding the MariaDB/MySQL configuration would be done as follows:

```properties
quarkus.datasource.devservices.container-properties.TC_MY_CNF=testcontainers/mysql-conf
```

This support is database specific and needs to be implemented in each Dev Service specifically.

## Connect To Database Run as a Dev Service

You can connect to a database running as a Dev Service as you would do with any database running inside a Docker container.

Login credentials are the same for most databases, except when the database requirements don’t allow it:

| Database | Username | Password | Database name |
| --- | --- | --- | --- |
| PostgreSQL, MariaDB, MySQL, IBM Db2, H2 | `quarkus` | `quarkus` | `quarkus` for the default datasource or name of the datasource |
| Microsoft SQL Server | `sa` | `Quarkus123` |  |

<dl><dt><strong>📌 NOTE</strong></dt><dd>

The Microsoft SQL Server Testcontainer doesn’t support defining the username or database name.
It also requires a strong password.
</dd></dl>

<dl><dt><strong>💡 TIP</strong></dt><dd>

For databases supporting it
(i.e. all of them except Microsoft SQL Server for which it is only possible to override the password),
you can override the database name, username and password used by the Dev Service.

See [Configuration Reference](#configuration-reference) for more information.
</dd></dl>

Keep in mind that, except if configured otherwise (see below), a Dev Service runs on a random port.
For instance, when you run PostgreSQL as a Dev Service and have `psql` installed on the host, you can connect via:

```bash
psql -h localhost -p <random port> -U quarkus
```

The random port can be found with `docker ps`

```bash
docker ps

# returns something like this:

CONTAINER ID   IMAGE           [..]    PORTS                                         [..]
b826e3a168c4   docker.io/library/postgres:18   [..]    0.0.0.0:49174->5432/tcp, :::49174->5432/tcp   [..] ①
```
1. The random port is `49174`.

You can require a fixed port for a database Dev Service using:

```properties
quarkus.datasource.devservices.port=<your fixed port> ①

quarkus.datasource."datasource-name".devservices.port=<your fixed port> ②
```
1. Fixed port for the default datasource.
2. Fixed port for a named datasource.

<dl><dt><strong>💡 TIP</strong></dt><dd>

`docker ps` allows for more advanced retrieval of container information using the `--format` argument.
For example, to get the running container ID, the image, the labels and the ports, the following command can be used:

```bash
docker ps --format "table {{.ID}}\t{{.Image}}\t{{.Labels}}\t{{.Ports}}
```

An example output using Dev Services for PostgreSQL is the following:

```bash
CONTAINER ID   IMAGE          LABELS                                                                        PORTS
a7034c91a392   docker.io/library/postgres:18     org.testcontainers.sessionId=xyz,datasource=default,org.testcontainers=true   0.0.0.0:49154->5432/tcp, :::49154->5432/tcp
```

In the labels tab, we see that Quarkus added the datasource label, which can be very useful in differentiating containers when multiple
Dev Services have been started.
</dd></dl>

## Compose

The Database Dev Services supports [Compose Dev Services](https://quarkus.io/guides/compose-dev-services).
It relies on a `compose-devservices.yml`, such as:

```yaml
name: <application name>
services:
  postgresql:
    image: docker.io/library/postgres:18
    ports:
      - "5432"
    environment:
      POSTGRES_USER: quarkus
      POSTGRES_PASSWORD: quarkus
      POSTGRES_DB: quarkus
  oracle:
    image: docker.io/gvenzl/oracle-free:23-slim-faststart
    ports:
      - "1521"
    environment:
      ORACLE_PASSWORD: quarkus
      ORACLE_DATABASE: quarkus
      APP_USER: quarkus
      APP_USER_PASSWORD: quarkus
    labels:
      io.quarkus.devservices.compose.wait_for.logs: .*DATABASE IS READY TO USE.*
  mssql:
    image: mcr.microsoft.com/mssql/server:2025-latest
    ports:
      - "1433"
    environment:
      ACCEPT_EULA: "Y"
      MSSQL_SA_PASSWORD: Quarkus123
    labels:
      io.quarkus.devservices.compose.jdbc.parameters: trustServerCertificate=true
```

## Configuration Reference

Dev Services for Databases support the following configuration options:

**📌 NOTE**\
La tabla de configuracion generada `quarkus-datasource_quarkus.datasource.devservices` se produce al construir la documentacion y no existe en el codigo fuente. Consulta la referencia de configuracion en https://quarkus.io/guides/all-config
