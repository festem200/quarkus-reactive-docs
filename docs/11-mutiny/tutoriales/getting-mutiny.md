# Getting started with Mutiny

> **Documentacion oficial:** <https://smallrye.io/smallrye-mutiny/latest/tutorials/getting-mutiny>  
> **Fuente:** `documentation/docs/tutorials/getting-mutiny.md` en [smallrye/smallrye-mutiny@3.3.0](https://github.com/smallrye/smallrye-mutiny/blob/3.3.0/documentation/docs/tutorials/getting-mutiny.md)  
> **Version documentada:** Mutiny 3.3.0 · **Sincronizado:** 2026-08-17 · **Licencia:** Apache-2.0

## Using Mutiny in a Java application

Add the _dependency_ to your project using your preferred build tool:

=== "Apache Maven"

    ```xml
    <dependency>
        <groupId>io.smallrye.reactive</groupId>
        <artifactId>mutiny</artifactId>
        <version>3.3.0</version>
    </dependency>
    ```

=== "Gradle (Groovy)"

    ```groovy
    implementation 'io.smallrye.reactive:mutiny:3.3.0'
    ```

=== "Gradle (Kotlin)"

    ```kotlin
    implementation("io.smallrye.reactive:mutiny:3.3.0")
    ```

=== "JBang"

    ```java
    //DEPS io.smallrye.reactive:mutiny:3.3.0
    ```

## Using Mutiny with Quarkus

Most of the [Quarkus](https://quarkus.io) extensions with reactive capabilities already depend on Mutiny.

You can also add the `quarkus-mutiny` dependency explicitly from the command-line:

```bash
mvn quarkus:add-extension -Dextensions=mutiny
```

or by editing the `pom.xml` file and adding:

```xml
<dependency>
  <groupId>io.quarkus</groupId>
  <artifactId>quarkus-mutiny</artifactId>
</dependency>
```

## Using Mutiny with Vert.x

Most of the [Eclipse Vert.x](https://vertx.io) stack modules are available through the [SmallRye Mutiny Vert.x Bindings](https://smallrye.io/smallrye-mutiny-vertx-bindings/) project.

Bindings for Vert.x modules are named by prepending `smallrye-mutiny-`.
As an example here's how to add a dependency to the `vertx-core` Mutiny bindings:

=== "Apache Maven"

    ```xml
    <dependency>
        <groupId>io.smallrye.reactive</groupId>
        <artifactId>smallrye-mutiny-vertx-core</artifactId>
        <version>4.0.0-beta2</version>
    </dependency>
    ```

=== "Gradle (Groovy)"

    ```groovy
    implementation 'io.smallrye.reactive:smallrye-mutiny-vertx-core:4.0.0-beta2'
    ```

=== "Gradle (Kotlin)"

    ```kotlin
    implementation("io.smallrye.reactive:smallrye-mutiny-vertx-core:4.0.0-beta2")
    ```

=== "JBang"

    ```java
    //DEPS io.smallrye.reactive:smallrye-mutiny-vertx-core:4.0.0-beta2
    ```
