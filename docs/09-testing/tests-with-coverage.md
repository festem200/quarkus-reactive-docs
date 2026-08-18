# Measuring the coverage of your tests

> **Guia oficial:** <https://quarkus.io/guides/tests-with-coverage>  
> **Fuente:** `docs/src/main/asciidoc/tests-with-coverage.adoc` en [quarkusio/quarkus@3.38.2](https://github.com/quarkusio/quarkus/blob/3.38.2/docs/src/main/asciidoc/tests-with-coverage.adoc)  
> **Version documentada:** Quarkus 3.38.2 · **Sincronizado:** 2026-08-17 · **Licencia:** Apache-2.0

Learn how to measure the test coverage of your application. This guide covers:

* Measuring the coverage of your Unit Tests
* Measuring the coverage of your Integration Tests
* Separating the execution of your Unit Tests and Integration Tests
* Consolidating the coverage for all your tests

Please note that code coverage is not supported in native mode.

## Prerequisites

To complete this guide, you need:

* Roughly 15 minutes
* An IDE
* JDK 17+ installed with `JAVA_HOME` configured appropriately
* Apache Maven 3.9.16
* Optionally the [Quarkus CLI](../10-extras/cli-tooling.md) if you want to use it
* Optionally Mandrel or GraalVM installed and [configured appropriately](../08-rendimiento-nativo/building-native-image.md#configuring-graalvm) if you want to build a native executable (or Docker if you use a native container build)
* Having completed the [Testing your application guide](getting-started-testing.md)

## Architecture

The application built in this guide is just a Jakarta REST endpoint (hello world) that relies on dependency injection to use a service.
The service will be tested with JUnit and the endpoint will be annotated via a `@QuarkusTest` annotation.

## Solution

We recommend that you follow the instructions in the next sections and create the application step by step. However, you can go right to the completed example.
Clone the Git repository: `git clone https://github.com/quarkusio/quarkus-quickstarts.git`, or download an [archive](https://github.com/quarkusio/quarkus-quickstarts/archive/main.zip).

The solution is located in the `tests-with-coverage-quickstart` [directory](https://github.com/quarkusio/quarkus-quickstarts/tree/main/tests-with-coverage-quickstart).

## Starting from a simple project and two tests

Let’s start from an empty application created with the Quarkus Maven plugin:

**CLI**

```bash
quarkus create app org.acme:tests-with-coverage-quickstart \
    --extension='rest' \
    --no-code
cd tests-with-coverage-quickstart
```

To create a Gradle project, add the `--gradle` or `--gradle-kotlin-dsl` option.

For more information about how to install and use the Quarkus CLI, see the [Quarkus CLI](../10-extras/cli-tooling.md) guide.

**Maven**

```bash
mvn io.quarkus.platform:quarkus-maven-plugin:3.38.2:create \
    -DprojectGroupId=org.acme \
    -DprojectArtifactId=tests-with-coverage-quickstart \
    -Dextensions='rest' \
    -DnoCode
cd tests-with-coverage-quickstart
```

To create a Gradle project, add the `-DbuildTool=gradle` or `-DbuildTool=gradle-kotlin-dsl` option.

For Windows users:

* If using cmd, (don’t use backward slash `\` and put everything on the same line)
* If using Powershell, wrap `-D` parameters in double quotes e.g. `"-DprojectArtifactId=tests-with-coverage-quickstart"`

Now we’ll be adding all the elements necessary to have an application that is properly covered with tests.

First, a Jakarta REST resource serving a hello endpoint:

```java
package org.acme.testcoverage;

import jakarta.inject.Inject;
import jakarta.ws.rs.GET;
import jakarta.ws.rs.Path;
import jakarta.ws.rs.Produces;
import jakarta.ws.rs.core.MediaType;

@Path("/hello")
public class GreetingResource {

    private final GreetingService service;

    @Inject
    public GreetingResource(GreetingService service) {
        this.service = service;
    }

    @GET
    @Produces(MediaType.TEXT_PLAIN)
    @Path("/greeting/{name}")
    public String greeting(String name) {
        return service.greeting(name);
    }

    @GET
    @Produces(MediaType.TEXT_PLAIN)
    public String hello() {
        return "hello";
    }
}
```

This endpoint uses a greeting service:

```java
package org.acme.testcoverage;

import jakarta.enterprise.context.ApplicationScoped;

@ApplicationScoped
public class GreetingService {

    public String greeting(String name) {
        return "hello " + name;
    }

}
```

The project will also need a test:

```java
package org.acme.testcoverage;

import io.quarkus.test.junit.QuarkusTest;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.Tag;

import java.util.UUID;

import static io.restassured.RestAssured.given;
import static org.hamcrest.CoreMatchers.is;

@QuarkusTest
public class GreetingResourceTest {

    @Test
    public void testHelloEndpoint() {
        given()
          .when().get("/hello")
          .then()
             .statusCode(200)
             .body(is("hello"));
    }

    @Test
    public void testGreetingEndpoint() {
        String uuid = UUID.randomUUID().toString();
        given()
          .pathParam("name", uuid)
          .when().get("/hello/greeting/{name}")
          .then()
            .statusCode(200)
            .body(is("hello " + uuid));
    }
}
```

## Setting up JaCoCo

Now we need to add JaCoCo to our project. To do this we need to add the following to the build file:

**pom.xml**

```xml
<dependency>
  <groupId>io.quarkus</groupId>
  <artifactId>quarkus-jacoco</artifactId>
  <scope>test</scope>
</dependency>
```

**build.gradle**

```gradle
testImplementation("io.quarkus:quarkus-jacoco")
```

This Quarkus extension takes care of everything that would usually be done via the JaCoCo Maven plugin, so no additional
config is required.

**⚠️ WARNING**\
Using both the extension and the plugin requires special configuration, if you add both you will get lots of errors about classes
already being instrumented. The configuration needed is detailed below.

## Working with multi-module projects

Up until `3.2`, `data-file` and `report-location` were always relative to the module’s build output directory, which prevented from
working with multi-module projects where you want to aggregate all coverages into a single parent directory. Starting in `3.3`,
specifying a `data-file` or `report-location` will assume the path as is. Here is an example on how to set up the `surefire` plugin:

```xml
<plugin>
  <artifactId>maven-surefire-plugin</artifactId>
  <configuration>
    <systemPropertyVariables>
      <quarkus.jacoco.data-file>${maven.multiModuleProjectDirectory}/target/jacoco.exec</quarkus.jacoco.data-file>
      <quarkus.jacoco.reuse-data-file>true</quarkus.jacoco.reuse-data-file>
      <quarkus.jacoco.report-location>${maven.multiModuleProjectDirectory}/target/coverage</quarkus.jacoco.report-location>
    </systemPropertyVariables>
  </configuration>
</plugin
```

**⚠️ WARNING**\
If you need to configure the `argLine` property of the Surefire plugin (e.g. for setting memory parameters), you need to use [Maven late property evaluation](https://maven.apache.org/surefire/maven-surefire-plugin/faq.html#late-property-evaluation), otherwise the Jacoco agent will not be correctly added, and regular JUnit tests and Quarkus `ComponentTest` will not get covered. Example: `<argLine>@{argLine} -your -extra -arguments</argLine>`.

## Running the tests with coverage

Run `mvn verify`, the tests will be run and the results will end up in `target/jacoco-reports`. This is all that is needed,
the `quarkus-jacoco` extension allows JaCoCo to just work out of the box.

There are some config options that affect this:

**📌 NOTE**\
La tabla de configuracion generada `quarkus-jacoco` se produce al construir la documentacion y no existe en el codigo fuente. Consulta la referencia de configuracion en https://quarkus.io/guides/all-config

<dl><dt><strong>💡 TIP</strong></dt><dd>

When working with a multi-module project, then for code coverage to work properly, the upstream modules need to be properly [indexed](../01-fundamentos/cdi-reference.md#bean_discovery).
</dd></dl>

## Coverage for tests not using @QuarkusTest

The Quarkus automatic JaCoCo config will only work for tests that are annotated with `@QuarkusTest`. If you want to check
the coverage of other tests as well then you will need to fall back to the JaCoCo maven plugin.

In addition to including the `quarkus-jacoco` extension in your `pom.xml` you will need the following config:

**pom.xml**

```xml
<project>
    <build>
        <plugins>
            ...
            <plugin>
                <groupId>org.jacoco</groupId>
                <artifactId>jacoco-maven-plugin</artifactId>
                <version>${jacoco.version}</version>
                <executions>
                   <execution>
                      <id>default-prepare-agent</id>
                      <goals>
                           <goal>prepare-agent</goal>
                      </goals>
                      <configuration>
                        <exclClassLoaders>*QuarkusClassLoader</exclClassLoaders>  ①
                        <destFile>${project.build.directory}/jacoco-quarkus.exec</destFile>
                        <append>true</append>
                      </configuration>
                   </execution>
                </executions>
            </plugin>
        </plugins>
    </build>
</project>
```
1. This config tells it to ignore `@QuarkusTest` related classes, as they are loaded by `QuarkusClassLoader`

**build.gradle**

```gradle
plugins {
    id 'jacoco' ①
}

test {
    finalizedBy jacocoTestReport
    jacoco {
        excludeClassLoaders = ["*QuarkusClassLoader"] ②
        destinationFile = layout.buildDirectory.file("jacoco-quarkus.exec").get().asFile ②
    }
    jacocoTestReport.enabled = false ③
}
```
1. Add the `jacoco` gradle plugin
2. This config tells it to ignore `@QuarkusTest` related classes, as they are loaded by `QuarkusClassLoader`
3. Set this config to `false` if you are also using the `quarkus-jacoco` extension and have at least one `@QuarkusTest`.  The default `jacocoTestReport` task can be skipped since `quarkus-jacoco` will generate the combined report of regular unit tests and `@QuarkusTest` classes since the execution data is recorded in the same file.

**⚠️ WARNING**\
This config will only work if at least one `@QuarkusTest` is being run. If you are not using `@QuarkusTest` then
you can simply use the JaCoCo plugin in the standard manner with no additional config.

### Coverage for Integration Tests

To get code coverage data from integration tests, the following requirements need to be met:

* The built artifact is a jar (and not a container or native binary).
* JaCoCo needs to be configured in your build tool.
* The application must have been built with `quarkus.package.write-transformed-bytecode-to-build-output` set to `true`

**⚠️ WARNING**\
Setting `quarkus.package.write-transformed-bytecode-to-build-output=true` should be done with caution and only if subsequent builds are done in a clean environment - i.e. the build tool’s output directory has been completely cleaned.

In the `pom.xml`, you can add the following plugin configuration for JaCoCo. This will append integration test data into the same destination file as unit tests,
re-build the JaCoCo report after the integration tests are complete, and thus produce a comprehensive code-coverage report.

```xml
<build>
    ...
    <plugins>
        ...
        <plugin>
            <groupId>org.jacoco</groupId>
            <artifactId>jacoco-maven-plugin</artifactId>
            <version>${jacoco.version}</version>
            <executions>
                ... ①

                <execution>
                    <id>default-prepare-agent-integration</id>
                    <goals>
                        <goal>prepare-agent-integration</goal>
                    </goals>
                    <configuration>
                        <destFile>${project.build.directory}/jacoco-quarkus.exec</destFile>
                        <append>true</append>
                    </configuration>
                </execution>
                <execution>
                    <id>report</id>
                    <phase>post-integration-test</phase>
                    <goals>
                        <goal>report</goal>
                    </goals>
                    <configuration>
                        <dataFile>${project.build.directory}/jacoco-quarkus.exec</dataFile>
                        <outputDirectory>${project.build.directory}/jacoco-report</outputDirectory>
                    </configuration>
                </execution>
            </executions>
        </plugin>
        ...
    </plugins>
    ...
</build>
```
1. All executions should be in the same `<plugin>` definition so make sure you concatenate all of them.

In order to run the integration tests as a jar with the JaCoCo agent, add the following to your `pom.xml`.
```xml
<build>
    ...
    <plugins>
        ...
        <plugin>
            <artifactId>maven-failsafe-plugin</artifactId>
            <version>${surefire-plugin.version}</version>
            <executions>
                <execution>
                    <goals>
                        <goal>integration-test</goal>
                        <goal>verify</goal>
                    </goals>
                    <configuration>
                        <systemPropertyVariables>
                            <java.util.logging.manager>org.jboss.logmanager.LogManager</java.util.logging.manager>
                            <maven.home>${maven.home}</maven.home>
                            <quarkus.test.arg-line>${argLine}</quarkus.test.arg-line>
                        </systemPropertyVariables>
                    </configuration>
                </execution>
            </executions>
        </plugin>
        ...
    </plugins>
    ...
</build>

```

**⚠️ WARNING**\
Sharing the same value for `quarkus.test.arg-line` might break integration test runs that test different types of Quarkus artifacts. In such cases, the use of Maven profiles is advised.

## Setting coverage thresholds

You can set thresholds for code coverage using the JaCoCo Maven plugin. Note the element `<dataFile>${project.build.directory}/jacoco-quarkus.exec</dataFile>`.
You must set it matching your choice for `quarkus.jacoco.data-file`.

**pom.xml**

```xml
<build>
    ...
    <plugins>
        ...
        <plugin>
            <groupId>org.jacoco</groupId>
            <artifactId>jacoco-maven-plugin</artifactId>
            <version>${jacoco.version}</version>
            <executions>
                ... ①

                <execution>
                    <id>jacoco-check</id>
                    <goals>
                        <goal>check</goal>
                    </goals>
                    <phase>post-integration-test</phase>
                    <configuration>
                        <dataFile>${project.build.directory}/jacoco-quarkus.exec</dataFile>
                        <rules>
                            <rule>
                                <element>BUNDLE</element>
                                <limits>
                                    <limit>
                                        <counter>LINE</counter>
                                        <value>COVEREDRATIO</value>
                                        <minimum>0.8</minimum>
                                    </limit>
                                    <limit>
                                        <counter>BRANCH</counter>
                                        <value>COVEREDRATIO</value>
                                        <minimum>0.72</minimum>
                                    </limit>
                                </limits>
                            </rule>
                        </rules>
                    </configuration>
                </execution>
            </executions>
        </plugin>
        ...
    </plugins>
    ...
</build>
```
1. All executions should be in the same `<plugin>` definition so make sure you concatenate all of them.

**build.gradle**

```gradle
jacocoTestCoverageVerification {
    executionData.setFrom("$project.buildDir/jacoco-quarkus.exec")
    violationRules {
        rule {
            limit {
                counter = 'INSTRUCTION'
                value = 'COVEREDRATIO'
                minimum = 0.80
            }
            limit {
                counter = 'BRANCH'
                value = 'COVEREDRATIO'
                minimum = 0.72
            }
        }
    }
}
check.dependsOn jacocoTestCoverageVerification
```

Excluding classes from the verification task can be configured as following:

```gradle
jacocoTestCoverageVerification {
    afterEvaluate { ①
        classDirectories.setFrom(files(classDirectories.files.collect { ②
            fileTree(dir: it, exclude: [
                    "org/example/package/**/*" ③
            ])
        }))
    }
}
```
1. `classDirectories` needs to be read after evaluation phase in Gradle
2. Currently, there is a bug in Gradle JaCoCo which requires the `excludes` to be specified in this manner - https://github.com/gradle/gradle/issues/14760.  Once this issue is fixed, excludes
3. Exclude all classes in `org/example/package` package

## Conclusion

You now have all the information you need to study the coverage of your tests!
But remember, some code that is not covered is certainly not well tested. But some code that is covered is not necessarily **well** tested. Make sure to write good tests!
