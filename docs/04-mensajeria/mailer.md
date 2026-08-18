# Sending emails using SMTP

> **Guia oficial:** <https://quarkus.io/guides/mailer>  
> **Fuente:** `docs/src/main/asciidoc/mailer.adoc` en [quarkusio/quarkus@3.38.2](https://github.com/quarkusio/quarkus/blob/3.38.2/docs/src/main/asciidoc/mailer.adoc)  
> **Version documentada:** Quarkus 3.38.2 · **Sincronizado:** 2026-08-17 · **Licencia:** Apache-2.0

This guide demonstrates how your Quarkus application can send emails using an SMTP server.
This is a getting started guide.
Check the [Quarkus Mailer Reference documentation](mailer-reference.md) for more complete explanation about the mailer and its usage.

## Prerequisites

To complete this guide, you need:

* Roughly 15 minutes
* An IDE
* JDK 17+ installed with `JAVA_HOME` configured appropriately
* Apache Maven 3.9.16
* Optionally the [Quarkus CLI](../10-extras/cli-tooling.md) if you want to use it
* Optionally Mandrel or GraalVM installed and [configured appropriately](../08-rendimiento-nativo/building-native-image.md#configuring-graalvm) if you want to build a native executable (or Docker if you use a native container build)
* The SMTP hostname, port and credentials, and an email address
* cURL

## Architecture

In this guide, we will build an application:

1. exposing an HTTP endpoint,
2. sending email when the endpoint receives an HTTP request.

The application will demonstrate how to send emails using the _imperative_ and _reactive_ mailer APIs.

Attachments, inlined attachments, templating, testing and more advanced configuration are covered in the [Mailer Reference documentation](mailer-reference.md).

## Solution

We recommend that you follow the instructions in the next sections and create the application step by step.
However, you can go right to the completed example.

Clone the Git repository: `git clone https://github.com/quarkusio/quarkus-quickstarts.git`, or download an [archive](https://github.com/quarkusio/quarkus-quickstarts/archive/main.zip).

The solution is located in the `mailer-quickstart` [directory](https://github.com/quarkusio/quarkus-quickstarts/tree/main/mailer-quickstart).

## Create the Maven Project

First, we need a new project. Create a new project with the following command:

**CLI**

```bash
quarkus create app org.acme:mailer-quickstart \
    --extension='rest,mailer,qute' \
    --no-code
cd mailer-quickstart
```

To create a Gradle project, add the `--gradle` or `--gradle-kotlin-dsl` option.

For more information about how to install and use the Quarkus CLI, see the [Quarkus CLI](../10-extras/cli-tooling.md) guide.

**Maven**

```bash
mvn io.quarkus.platform:quarkus-maven-plugin:3.38.2:create \
    -DprojectGroupId=org.acme \
    -DprojectArtifactId=mailer-quickstart \
    -Dextensions='rest,mailer,qute' \
    -DnoCode
cd mailer-quickstart
```

To create a Gradle project, add the `-DbuildTool=gradle` or `-DbuildTool=gradle-kotlin-dsl` option.

For Windows users:

* If using cmd, (don’t use backward slash `\` and put everything on the same line)
* If using Powershell, wrap `-D` parameters in double quotes e.g. `"-DprojectArtifactId=mailer-quickstart"`

This command generates a Maven structure including the following extensions:

* Quarkus REST (formerly RESTEasy Reactive) used to expose REST endpoints
* Mailer so that we can send emails
* Qute, our template engine

If you already have your Quarkus project configured, you can add the `mailer` extension
to your project by running the following command in your project base directory:

**CLI**

```bash
quarkus extension add mailer
```
**Maven**

```bash
./mvnw quarkus:add-extension -Dextensions='mailer'
```
**Gradle**

```bash
./gradlew addExtension --extensions='mailer'
```

This will add the following to your `pom.xml`:

**pom.xml**

```xml
<dependency>
    <groupId>io.quarkus</groupId>
    <artifactId>quarkus-mailer</artifactId>
</dependency>
```

**build.gradle**

```gradle
implementation("io.quarkus:quarkus-mailer")
```

Open the generated project in your IDE.
In a terminal, navigate to the project and start your application in dev mode:

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

### Implement the HTTP endpoint

First, create the `src/main/java/org/acme/MailResource.java` file, with the following content:

```java
package org.acme;

import io.quarkus.mailer.Mail;
import io.quarkus.mailer.Mailer;
import io.smallrye.common.annotation.Blocking;

import jakarta.inject.Inject;
import jakarta.ws.rs.GET;
import jakarta.ws.rs.Path;

@Path("/mail")                                                          // ①
public class MailResource {

    @Inject Mailer mailer;                                              // ②

    @GET                                                                // ③
    @Blocking                                                           // ④
    public void sendEmail() {
        mailer.send(
                Mail.withText("quarkus@quarkus.io",                     // ⑤
                    "Ahoy from Quarkus",
                    "A simple email sent from a Quarkus application."
                )
        );
    }

}
```
1. Configure the root path of our HTTP endpoint
2. Inject the `Mailer` object managed by Quarkus
3. Create a method that will handle the HTTP GET request on `/mail`
4. Because we are using Quarkus REST and the _imperative_ mailer, we need to add the `@Blocking` annotation. We will see later the reactive variant.
5. Create a `Mail` object by configuring the _to_ recipient, the subject and body

The `MailResource` class implements the HTTP API exposed by our application.
It handles `GET` request on `http://localhost:8080/mail.

So, if in another terminal, you run:

```bash
> curl http://localhost:8080/mail
```

You should see in the application log something like:

```text
INFO  [quarkus-mailer] (executor-thread-0) Sending email Ahoy from Quarkus from null to [quarkus@quarkus.io], text body:
A simple email sent from a Quarkus application.
html body:
<empty>
```

As the application runs in _dev mode_, it simulates the sending of the emails.
It prints it in the log, so you can check that what was about to be sent.

**📌 NOTE**\
This section used the _imperative_ mailer API.
It blocks the caller thread until the mail is sent.

<dl><dt><strong>💡 TIP</strong></dt><dd>

The [Quarkus Mailpit](https://github.com/quarkiverse/quarkus-mailpit) extension is very handy for testing emails.
It provides Dev Services for [Mailpit](https://github.com/axllent/mailpit), a nice UI for testing and debugging email sending.
</dd></dl>

## Using the reactive mailer

The last section use the _imperative_ mailer.
Quarkus also offers a reactive API.

<dl><dt><strong>💡 TIP: Mutiny</strong></dt><dd>

The reactive mailer uses Mutiny reactive types.
If you are not familiar with Mutiny, check [Mutiny - an intuitive reactive programming library](../01-fundamentos/mutiny-primer.md).
</dd></dl>

In the same class, add:

```java
@Inject
ReactiveMailer reactiveMailer;                          // ①

@GET
@Path("/reactive")                                      // ②
public Uni<Void> sendEmailUsingReactiveMailer() {       // ③
    return reactiveMailer.send(                         // ④
                Mail.withText("quarkus@quarkus.io",
                    "Ahoy from Quarkus",
                    "A simple email sent from a Quarkus application using the reactive API."
                )
        );
}
```
1. Inject the reactive mailer. The class to import is `io.quarkus.mailer.reactive.ReactiveMailer`.
2. Configure the path to handle GET request on `/mail/reactive`. Note that because we are using the reactive API, we don’t need `@Blocking`
3. The method returns a `Uni<Void>` which completes when the mail is sent. It does not block the caller thread.
4. The API is similar to the _imperative_ one except that the `send` method returns a `Uni<Void>`.

Now, in your terminal, run

```bash
> curl http://localhost:8080/mail/reactive
```

You should see in the application log something like:

```text
INFO  [quarkus-mailer] (vert.x-eventloop-thread-11) Sending email Ahoy from Quarkus from null to [quarkus@quarkus.io], text body:
A simple email sent from a Quarkus application using the reactive API.
html body:
<empty>
```

## Configuring the mailer

It’s time to configure the mailer to not simulate the sending of the emails.
The Quarkus mailer is using SMTP, so make sure you have access to an SMTP server.

In the `src/main/resources/application.properties` file, you need to configure the host, port, username, password as well as the other configuration aspect.
Note that the password can also be configured using system properties and environment variables.
See the [configuration reference guide](../01-fundamentos/config-reference.md) for details.

Configuration of popular mail services is covered in [the reference guide](mailer-reference.md#popular).

Once you have configured the mailer, if you call the HTTP endpoint as shown above, you will send emails.

## Conclusion

This guide has shown how to send emails from your Quarkus application.
The [mailer reference guide](mailer-reference.md) provides more details about the mailer usage and configuration such as:

* [how to add attachments](mailer-reference.md#attachments)
* [how to format the email as HTML and use inline attachments](mailer-reference.md#html)
* [how to use Qute templates](mailer-reference.md#templates)
* [how to test applications sending emails](mailer-reference.md#testing)
* [how to configure the mailer for popular email services (e.g. Gmail, AWS SES)](mailer-reference.md#popular)
