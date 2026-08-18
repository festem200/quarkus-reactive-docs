# Qute Templating Engine

> **Guia oficial:** <https://quarkus.io/guides/qute>  
> **Fuente:** `docs/src/main/asciidoc/qute.adoc` en [quarkusio/quarkus@3.38.2](https://github.com/quarkusio/quarkus/blob/3.38.2/docs/src/main/asciidoc/qute.adoc)  
> **Version documentada:** Quarkus 3.38.2 · **Sincronizado:** 2026-08-17 · **Licencia:** Apache-2.0

Qute is a templating engine developed specifically for Quarkus.
Reflection usage is minimized to reduce the size of native images.
The API combines both the imperative and the non-blocking reactive style of coding.
In development mode, all files located in `src/main/resources/templates` are monitored for changes, and modifications become visible immediately.
Furthermore, we aim to detect most template issues at build time.
In this guide, you will learn how to easily render templates in your application.

## Solution

We recommend that you follow the instructions in the next sections and create the application step by step.
However, you can go right to the completed example.

Clone the Git repository: `git clone https://github.com/quarkusio/quarkus-quickstarts.git`, or download an [archive](https://github.com/quarkusio/quarkus-quickstarts/archive/main.zip).

The solution is located in the `qute-quickstart` [directory](https://github.com/quarkusio/quarkus-quickstarts/tree/main/qute-quickstart).

## Serving Qute templates via HTTP

If you want to serve your templates via HTTP:

1. The Qute Web extension allows you to directly serve via HTTP templates located in `src/main/resources/templates/pub/`. In that case you don’t need any Java code to "plug" the template, for example, the template `src/main/resources/templates/pub/foo.html` will be served from the paths `/foo` and `/foo.html` by default.
2. For finer control, you can combine it with Quarkus REST to control how your template will be served. All files located in the `src/main/resources/templates` directory and its subdirectories are registered as templates and can be injected in a REST resource.

**pom.xml**

```xml
<dependency>
    <groupId>io.quarkiverse.qute.web</groupId>
    <artifactId>quarkus-qute-web</artifactId>
</dependency>
```

**build.gradle**

```gradle
implementation("io.quarkiverse.qute.web:quarkus-qute-web")
```

**📌 NOTE**\
The Qute Web extension, while hosted in the Quarkiverse, is part of the Quarkus Platform and its version is defined in the Quarkus Platform BOM.

### Serving Hello World with Qute

Let’s start with a Hello World template:

**src/main/resources/templates/pub/hello.html**

```
<h1>Hello {http:param('name', 'Quarkus')}!</h1> ①
```
1. `{http:param('name', 'Quarkus')}` is an expression that is evaluated when the template is rendered (Quarkus is the default value).

**📌 NOTE**\
Templates located in the `pub` directory are served via HTTP. This behavior is built-in, no controllers are needed. For example, the template `src/main/resources/templates/pub/foo.html` will be served from the paths `/foo` and `/foo.html` by default.

Once your application is running, you can open your browser and navigate to: http://localhost:8080/hello?name=Martin

For more information about Qute Web options, see the [Qute Web guide](https://docs.quarkiverse.io/quarkus-qute-web/dev/index.html).

### Hello Qute and REST

For finer control, you can combine Qute Web with Quarkus REST (formerly RESTEasy Reactive) or the legacy RESTEasy Classic-based extension to control how your template will be served

Using the `quarkus-rest-qute` extension:

**pom.xml**

```xml
<dependency>
    <groupId>io.quarkus</groupId>
    <artifactId>quarkus-rest-qute</artifactId>
</dependency>
```

**build.gradle**

```gradle
implementation("io.quarkus:quarkus-rest-qute")
```

A very simple text template:

**hello.txt**

```
Hello {name}! ①
```
1. `{name}` is a value expression that is evaluated when the template is rendered.

Now let’s inject the "compiled" template in the resource class.

**HelloResource.java**

```java
package org.acme.quarkus.sample;

import jakarta.inject.Inject;
import jakarta.ws.rs.GET;
import jakarta.ws.rs.Path;
import jakarta.ws.rs.QueryParam;
import jakarta.ws.rs.Produces;
import jakarta.ws.rs.core.MediaType;

import io.quarkus.qute.TemplateInstance;
import io.quarkus.qute.Template;

@Path("hello")
public class HelloResource {

    @Inject
    Template hello; ①

    @GET
    @Produces(MediaType.TEXT_PLAIN)
    public TemplateInstance get(@QueryParam("name") String name) {
        return hello.data("name", name); ② ③
    }
}
```
1. If there is no `@Location` qualifier provided, the field name is used to locate the template. In this particular case, we’re injecting a template with path `templates/hello.txt`.
2. `Template.data()` returns a new template instance that can be customized before the actual rendering is triggered. In this case, we put the name value under the key `name`. The data map is accessible during rendering.
3. Note that we don’t trigger the rendering - this is done automatically by a special `ContainerResponseFilter` implementation provided by `quarkus-rest-qute`.

If your application is running, you can request the endpoint:

```shell
$ curl -w "\n" http://localhost:8080/hello?name=Martin
Hello Martin!
```

## Type-safe templates

There’s an alternate way to declare your templates in your Java code, which relies on the following convention:

* Organize your template files in the `/src/main/resources/templates` directory, by grouping them into one directory per resource class. So, if
  your `FruitResource` class references two templates `apples` and `oranges`, place them at `/src/main/resources/templates/FruitResource/apples.txt`
  and `/src/main/resources/templates/FruitResource/oranges.txt`. Grouping templates per resource class makes it easier to navigate to them.
* In each of your resource class, declare a `@CheckedTemplate static class Template {}` class within your resource class.
* Declare one `public static native TemplateInstance method();` per template file for your resource.
* Use those static methods to build your template instances.

Here’s the previous example, rewritten using this style:

We’ll start with a very simple template:

**HelloResource/hello.txt**

```
Hello {name}! ①
```
1. `{name}` is a value expression that is evaluated when the template is rendered.

Now let’s declare and use this template in the resource class.

**HelloResource.java**

```java
package org.acme.quarkus.sample;

import jakarta.inject.Inject;
import jakarta.ws.rs.GET;
import jakarta.ws.rs.Path;
import jakarta.ws.rs.QueryParam;
import jakarta.ws.rs.Produces;
import jakarta.ws.rs.core.MediaType;

import io.quarkus.qute.TemplateInstance;
import io.quarkus.qute.CheckedTemplate;

@Path("hello")
public class HelloResource {

    @CheckedTemplate
    public static class Templates {
        public static native TemplateInstance hello(String name); ①
    }

    @GET
    @Produces(MediaType.TEXT_PLAIN)
    public TemplateInstance get(@QueryParam("name") String name) {
        return Templates.hello(name); ②
    }
}
```
1. This declares a template with path `templates/HelloResource/hello`.
2. `Templates.hello()` returns a new template instance that is returned from the resource method. Note that we don’t trigger the rendering - this is done automatically by a special `ContainerResponseFilter` implementation provided by `quarkus-rest-qute`.

**📌 NOTE**\
Once you have declared a `@CheckedTemplate` class, we will check that all its methods point to existing templates, so if you try to use a template from your Java code and you forgot to add it, we will let you know at build time :)

Keep in mind this style of declaration allows you to reference templates declared in other resources too:

**GreetingResource.java**

```java
package org.acme.quarkus.sample;

import jakarta.inject.Inject;
import jakarta.ws.rs.GET;
import jakarta.ws.rs.Path;
import jakarta.ws.rs.QueryParam;
import jakarta.ws.rs.Produces;
import jakarta.ws.rs.core.MediaType;

import io.quarkus.qute.TemplateInstance;

@Path("greeting")
public class GreetingResource {

    @GET
    @Produces(MediaType.TEXT_PLAIN)
    public TemplateInstance get(@QueryParam("name") String name) {
        return HelloResource.Templates.hello(name);
    }
}
```

### Top-level type-safe templates

Naturally, if you want to declare templates at the top-level, directly in `/src/main/resources/templates/hello.txt`, for example,
you can declare them in a top-level (non-nested) `Templates` class:

**HelloResource.java**

```java
package org.acme.quarkus.sample;

import io.quarkus.qute.TemplateInstance;
import io.quarkus.qute.Template;
import io.quarkus.qute.CheckedTemplate;

@CheckedTemplate
public class Templates {
    public static native TemplateInstance hello(String name); ①
}
```
1. This declares a template with path `templates/hello`.

## Template Parameter Declarations

If you declare a **parameter declaration** in a template then Qute attempts to validate all expressions that reference this parameter and if an incorrect expression is found the build fails.

Let’s suppose we have a simple class like this:

**Item.java**

```java
public class Item {
    public String name;
    public BigDecimal price;
}
```

And we’d like to render a simple HTML page that contains the item name and price.

Let’s start again with the template:

**ItemResource/item.html**

```html
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>{item.name}</title> ①
</head>
<body>
    <h1>{item.name}</h1>
    <div>Price: {item.price}</div> ②
</body>
</html>
```
1. This expression is validated. Try to change the expression to `{item.nonSense}` and the build should fail.
2. This is also validated.

Finally, let’s create a resource class with type-safe templates:

**ItemResource.java**

```java
package org.acme.quarkus.sample;

import jakarta.inject.Inject;
import jakarta.ws.rs.GET;
import jakarta.ws.rs.Path;
import jakarta.ws.rs.Produces;
import jakarta.ws.rs.core.MediaType;

import io.quarkus.qute.TemplateInstance;
import io.quarkus.qute.Template;
import io.quarkus.qute.CheckedTemplate;

@Path("item")
public class ItemResource {

    @CheckedTemplate
    public static class Templates {
        public static native TemplateInstance item(Item item); ①
    }

    @GET
    @Path("{id}")
    @Produces(MediaType.TEXT_HTML)
    public TemplateInstance get(@PathParam("id") Integer id) {
        return Templates.item(service.findItem(id)); ②
    }
}
```
1. Declare a method that gives us a `TemplateInstance` for `templates/ItemResource/item.html` and declare its `Item item` parameter so we can validate the template.
2. Make the `Item` object accessible in the template.

**📌 NOTE**\
When the `--parameters` compiler argument is enabled, Quarkus REST may infer the parameter names from the method argument names, making the `@PathParam("id")` annotation optional in this case.

### Template parameter declaration inside the template itself

Alternatively, you can declare your template parameters in the template file itself.

Let’s start again with the template:

**item.html**

```html
{@org.acme.Item item} ①
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>{item.name}</title> ②
</head>
<body>
    <h1>{item.name}</h1>
    <div>Price: {item.price}</div>
</body>
</html>
```
1. Optional parameter declaration. Qute attempts to validate all expressions that reference the parameter `item`.
2. This expression is validated. Try to change the expression to `{item.nonSense}` and the build should fail.

Finally, let’s create a resource class.

**ItemResource.java**

```java
package org.acme.quarkus.sample;

import jakarta.inject.Inject;
import jakarta.ws.rs.GET;
import jakarta.ws.rs.Path;
import jakarta.ws.rs.Produces;
import jakarta.ws.rs.core.MediaType;

import io.quarkus.qute.TemplateInstance;
import io.quarkus.qute.Template;

@Path("item")
public class ItemResource {

    @Inject
    ItemService service;

    @Inject
    Template item; ①

    @GET
    @Path("{id}")
    @Produces(MediaType.TEXT_HTML)
    public TemplateInstance get(Integer id) {
        return item.data("item", service.findItem(id)); ②
    }
}
```
1. Inject the template with path `templates/item.html`.
2. Make the `Item` object accessible in the template.

## Template Extension Methods

**Template extension methods** are used to extend the set of accessible properties of data objects.

Sometimes, you’re not in control of the classes that you want to use in your template, and you cannot add methods
to them. Template extension methods allow you to declare new methods for those classes that will be available
from your templates just as if they belonged to the target class.

Let’s keep extending on our simple HTML page that contains the item name, price and add a discounted price.
The discounted price is sometimes called a "computed property".
We will implement a template extension method to render this property easily.
Let’s update our template:

**HelloResource/item.html**

```html
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>{item.name}</title>
</head>
<body>
    <h1>{item.name}</h1>
    <div>Price: {item.price}</div>
    {#if item.price > 100} ①
    <div>Discounted Price: {item.discountedPrice}</div> ②
    {/if}
</body>
</html>
```
1. `if` is a basic control flow section.
2. This expression is also validated against the `Item` class and obviously there is no such property declared. However, there is a template extension method declared on the `TemplateExtensions` class - see below.

Finally, let’s create a class where we put all our extension methods:

**TemplateExtensions.java**

```java
package org.acme.quarkus.sample;

import io.quarkus.qute.TemplateExtension;

@TemplateExtension
public class TemplateExtensions {

    public static BigDecimal discountedPrice(Item item) { ①
        return item.price.multiply(new BigDecimal("0.9"));
    }
}
```
1. A static template extension method can be used to add "computed properties" to a data class. The class of the first parameter is used to match the base object and the method name is used to match the property name.

**📌 NOTE**\
you can place template extension methods in every class if you annotate them with `@TemplateExtension` but we advise to keep them either
grouped by target type, or in a single `TemplateExtensions` class by convention.

## Rendering Periodic Reports

The templating engine can also be very useful for rendering periodic reports.
You’ll need to add the `quarkus-scheduler` and `quarkus-qute` extensions first.
In your `pom.xml` file, add:

```xml
<dependency>
    <groupId>io.quarkus</groupId>
    <artifactId>quarkus-qute</artifactId>
</dependency>
<dependency>
    <groupId>io.quarkus</groupId>
    <artifactId>quarkus-scheduler</artifactId>
</dependency>
```

Let’s suppose we have a `SampleService` bean whose `get()` method returns a list of samples.

**Sample.java**

```java
public class Sample {
    public boolean valid;
    public String name;
    public String data;
}
```

The template is simple:

**report.html**

```html
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>Report {now}</title>
</head>
<body>
    <h1>Report {now}</h1>
    {#for sample in samples} ①
      <h2>{sample.name ?: 'Unknown'}</h2> ②
      <p>
      {#if sample.valid}
        {sample.data}
      {#else}
        <strong>Invalid sample found</strong>.
      {/if}
      </p>
    {/for}
</body>
</html>
```
1. The loop section makes it possible to iterate over iterables, maps and streams.
2. This value expression is using the [elvis operator](https://en.wikipedia.org/wiki/Elvis_operator) - if the name is null the default value is used.

**ReportGenerator.java**

```java
package org.acme.quarkus.sample;

import jakarta.inject.Inject;

import io.quarkus.qute.Template;
import io.quarkus.qute.Location;
import io.quarkus.scheduler.Scheduled;

public class ReportGenerator {

    @Inject
    SampleService service;

    @Location("reports/v1/report_01") ①
    Template report;

    @Scheduled(cron="0 30 * * * ?") ②
    void generate() {
        String result = report
            .data("samples", service.get())
            .data("now", java.time.LocalDateTime.now())
            .render(); ③
        // Write the result somewhere...
    }
}
```
1. In this case, we use the `@Location` qualifier to specify the template path: `templates/reports/v1/report_01.html`.
2. Use the `@Scheduled` annotation to instruct Quarkus to execute this method on the half hour. For more information see the [Scheduler](../06-resiliencia/scheduler.md) guide.
3. The `TemplateInstance.render()` method triggers rendering. Note that this method blocks the current thread.

## Qute Reference Guide

To learn more about Qute, please refer to the [Qute reference guide](qute-reference.md).

## Qute Configuration Reference

**📌 NOTE**\
La tabla de configuracion generada `quarkus-qute` se produce al construir la documentacion y no existe en el codigo fuente. Consulta la referencia de configuracion en https://quarkus.io/guides/all-config
