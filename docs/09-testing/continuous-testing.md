# Continuous Testing

> **Guia oficial:** <https://quarkus.io/guides/continuous-testing>  
> **Fuente:** `docs/src/main/asciidoc/continuous-testing.adoc` en [quarkusio/quarkus@3.38.2](https://github.com/quarkusio/quarkus/blob/3.38.2/docs/src/main/asciidoc/continuous-testing.adoc)  
> **Version documentada:** Quarkus 3.38.2 · **Sincronizado:** 2026-08-17 · **Licencia:** Apache-2.0

Learn how to use continuous testing in your Quarkus Application.

## Prerequisites

To complete this guide, you need:

* Roughly 15 minutes
* An IDE
* JDK 17+ installed with `JAVA_HOME` configured appropriately
* Apache Maven 3.9.16
* Optionally the [Quarkus CLI](../10-extras/cli-tooling.md) if you want to use it
* Optionally Mandrel or GraalVM installed and [configured appropriately](../08-rendimiento-nativo/building-native-image.md#configuring-graalvm) if you want to build a native executable (or Docker if you use a native container build)
* The completed greeter application from the [Getting Started Guide](../10-extras/getting-started.md)

## Introduction

Quarkus supports continuous testing, where tests run immediately after code changes have been saved. This allows you to
get instant feedback on your code changes. Quarkus detects which tests cover which code, and uses this information to
only run the relevant tests when code is changed.

## Solution

Start the [Getting Started](../10-extras/getting-started.md) application (or any other application) using:

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

Quarkus will start in development mode as normal, but down the bottom of the screen you should see the following:

```
--
Tests paused, press [r] to resume, [h] for more options>
```

Press `r` and the tests will start running. You should see the status change down the bottom of the screen as they
are running, and it should finish with:

```
--
Tests all passed, 2 tests were run, 0 were skipped. Tests took 1470ms.
Press [r] to re-run, [v] to view full results, [p] to pause, [h] for more options>
```

**📌 NOTE**\
If you want continuous testing to start automatically you can set `quarkus.test.continuous-testing=enabled` in
`application.properties`. If you don’t want it at all you can change this to `disabled`.

Now you can start making changes to your application. Go into the `GreetingResource` and change the hello endpoint to
return `"hello world"`, and save the file. Quarkus should immediately re-run the test, and you should get output similar
to the following:

```
2021-05-11 14:21:34,338 ERROR [io.qua.test] (Test runner thread) Test GreetingResourceTest#testHelloEndpoint() failed
: java.lang.AssertionError: 1 expectation failed.
Response body doesn't match expectation.
Expected: is "hello"
  Actual: hello world

	at io.restassured.internal.ValidatableResponseImpl.body(ValidatableResponseImpl.groovy)
	at org.acme.getting.started.GreetingResourceTest.testHelloEndpoint(GreetingResourceTest.java:21)

--
Test run failed, 2 tests were run, 1 failed, 0 were skipped. Tests took 295ms
Press [r] to re-run, [v] to view full results, [p] to pause, [h] for more options>
```

Change it back and the tests will run again.

## Controlling Continuous Testing

There are various hotkeys you can use to control continuous testing. Pressing `h` will display the following list
of commands:

```
The following commands are available:
[r] - Re-run all tests
[f] - Re-run failed tests
[b] - Toggle 'broken only' mode, where only failing tests are run (disabled)
[v] - Print failures from the last test run
[p] - Pause tests
[o] - Toggle test output (disabled)
[i] - Toggle instrumentation based reload (disabled)
[l] - Toggle live reload (enabled)
[s] - Force restart
[h] - Display this help
[q] - Quit
```

These are explained below:

* **[r] - Re-run all tests**\
This will re-run every test
* **[f] - Re-run failed tests**\
This will re-run every failing test
* **[b] - Toggle 'broken only' mode, where only failing tests are run**\
Broken only mode will only run tests that have previously failed, even if other tests would normally be affected by a code
change. This can be useful if you are modifying code that is used by lots of tests, but you only want to focus on debugging
the failing one.
* **[v] - Print failures from the last test run**\
Prints the failures to the console again, this can be useful if there has been lots of console output since the last run.
* **[p] - Pause tests**\
Temporarily stops running tests. This can be useful if you are making lots of changes, and don’t want feedback until they
are all done.
* **[o] - Toggle test output**\
By default test output is filtered and not displayed on the console, so that test output and dev mode output is not
interleaved. Enabling test output will print output to the console when tests are run. Even when output is disabled
the filtered output is saved and can be viewed in the Dev UI.
* **[i] - Toggle instrumentation based reload**\
This is not directly related to testing, but allows you to toggle instrumentation based reload. This will allow live reload
to avoid a restart if a change does not affect the structure of a class, which gives a faster reload and allows you to keep
state.
* **[l] - Toggle live reload**\
This is not directly related to testing, but allows you to turn live reload on and off.
* **[s] - Force restart**\
This will force a scan for changed files, and will perform a live reload with and changes. Note that even if there are no
changes the application will still restart. This will still work even if live reload is disabled.

## Continuous Testing Without Dev Mode

It is possible to run continuous testing without starting dev mode. This can be useful if dev mode will interfere with
your tests (e.g. running wiremock on the same port), or if you only want to develop using tests. To start continuous testing
mode, run `mvn quarkus:test` or `gradle quarkusTest`.

**📌 NOTE**\
The Dev UI is not available when running in continuous testing mode, as this is provided by dev mode.

## Selecting Tests to Run

The configuration properties `quarkus.test.include-pattern` and `quarkus.test.exclude-pattern` can be used to select which tests to run.
They are regular expressions matched against the fully qualified class name of the test class.
If `include-patterns` is configured, `exclude-patterns` is ignored.

Alternatively, an approach native to the build system may be used.
In Maven, that is the `-Dtest=...` system property, while in Gradle, it is the `--tests ...` command line option.
These options, when used with `maven quarkus:[dev|test]` or `gradle quarkus[Dev|Test]`, work just like they work with `mvn test` or `gradle test`, except that they filter the set of tests executed during continuous testing.
When these options are used, the `quarkus.test.[include|exclude]-pattern` configuration is ignored.

### Maven

The `-Dtest=...` system property selects given test(s) for continuous testing.
The format of this configuration property is the same as the Maven Surefire `-Dtest=...` [format](https://maven.apache.org/surefire/maven-surefire-plugin/test-mojo.html#test).
Specifically: it is a comma (`,`) separated list of globs of class file paths and/or method names.
Each glob can potentially be prefixed with an exclamation mark (`!`), which makes it an exclusion filter instead of an inclusion filter.
Exclusions have higher priority than inclusions.
The class file path glob is separated from the method name glob by the hash sign (`#`) and multiple method name globs may be present, separated by the plus sign (`+`).

For example:

* `Basic*`: all classes starting with `Basic`
* `???Test`: all classes named with 3 arbitrary characters followed by `Test`
* `!Unstable*`: all classes except classes starting with `Unstable`
* `pkg/**/Ci*leTest`: all classes in the package `pkg` and subpackages, starting with `Ci` and ending with `leTest`
* `*Test#test*One+testTwo?????`: all classes ending with `Test`, and in them, only methods starting with `test` and ending with `One`, or starting with `testTwo` and followed by 5 arbitrary characters
* `#fast*+slowTest`: all classes, and in them, only methods starting with `fast` or methods named `slowTest`

Note that the syntax `%regex[...]` and `%ant[...]` is _NOT_ supported.

### Gradle

The `--tests ...` command line option selects given test(s) for continuous testing.
The format is the same as the `gradle test --tests ...` [format](https://docs.gradle.org/current/userguide/java_testing.html#test_filtering).
Specifically: the option can be passed multiple times, and each item is a simple pattern for the test class name and optionally a method name.
When the pattern starts with an upper case letter, it matches a simple name of the class; otherwise, it matches a fully qualified name of the class.
After the class name, separated by a period (`.`), a method name pattern may be included.
The only wildcard character supported is `\*`, which matches an arbitrary number of characters.
Note that `*` is based purely on text, it doesn’t pay extra attention to package delimiters.

For example:

* `com.example.Basic*`: all classes in package `com.example` starting with `Basic`
* `MyTest*`: all classes whose simple name starts with `MyTest`
* `\*.pkg.Test*`: all classes in package `pkg` (regardless of the parent packages) starting with `Test`
* `MyTest.test*`: all classes whose simple name is `MyTest`, and in them, only methods starting with `test`
* `com.example.IntegTest.fast*`: the class `com.example.IntegTest`, and in it, only methods starting with `fast`

## Multi-module Projects

Note that continuous testing supports multi-module projects, so tests in modules other than the application can still
be run when files are changed. The modules that are run can be controlled using config as listed below.

This is enabled by default, and can be disabled via `quarkus.test.only-test-application-module=true`.

## Configuring Continuous Testing

Continuous testing supports multiple configuration options that can be used to limit the tests that are run, and
to control the output. The configuration properties are shown below:

**📌 NOTE**\
La tabla de configuracion generada `quarkus-core_quarkus.test` se produce al construir la documentacion y no existe en el codigo fuente. Consulta la referencia de configuracion en https://quarkus.io/guides/all-config
