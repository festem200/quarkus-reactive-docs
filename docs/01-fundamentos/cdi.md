# Introduction to Contexts and Dependency Injection (CDI)

> **Guia oficial:** <https://quarkus.io/guides/cdi>  
> **Fuente:** `docs/src/main/asciidoc/cdi.adoc` en [quarkusio/quarkus@3.38.2](https://github.com/quarkusio/quarkus/blob/3.38.2/docs/src/main/asciidoc/cdi.adoc)  
> **Version documentada:** Quarkus 3.38.2 · **Sincronizado:** 2026-08-17 · **Licencia:** Apache-2.0

In this guide we’re going to describe the basic principles of the Quarkus programming model that is based on the [Jakarta Contexts and Dependency Injection 4.1](https://jakarta.ee/specifications/cdi/4.1/jakarta-cdi-spec-4.1.html) specification.
The [CDI reference guide](cdi-reference.md) describes the bean discovery, non-standard features and configuration properties.
The [CDI integration guide](https://quarkus.io/guides/cdi-integration) has more detail on common CDI-related integration use cases, and example code for solutions.

## OK. Let’s start simple. What is a bean?

Well, a bean is a _container-managed_ object that supports a set of basic services, such as injection of dependencies, lifecycle callbacks, and interceptors.

## Wait a minute. What does "container-managed" mean?

Simply put, you don’t control the lifecycle of the object instance directly.
Instead, you can affect the lifecycle through declarative means, such as annotations, configuration, etc.
The container is the _environment_ where your application runs.
It creates and destroys the instances of beans, associates the instances with a designated context, and injects them into other beans.

## What is it good for?

An application developer can focus on the business logic rather than finding out "where and how" to obtain a fully initialized component with all of its dependencies.

**📌 NOTE**\
You’ve probably heard of the _inversion of control_ (IoC) programming principle. Dependency injection is one of the implementation techniques of IoC.

## What does a bean look like?

There are several kinds of beans.
The most common ones are class-based beans:

**Simple Bean Example**

```java
import jakarta.inject.Inject;
import jakarta.enterprise.context.ApplicationScoped;
import io.micrometer.core.annotation.Counted;

@ApplicationScoped ①
public class Translator {

    @Inject
    Dictionary dictionary; ②

    @Counted(value = "translate.method.counted") ③
    String translate(String sentence) {
      // ...
    }
}
```
1. This is a scope annotation. It tells the container which context to associate the bean instance with. In this particular case, a **single bean instance** is created for the application and used by all other beans that inject `Translator`.
2. This is a field injection point. It tells the container that `Translator` depends on the `Dictionary` bean. If there is no matching bean the build fails.
3. This is an interceptor binding annotation. In this case, the annotation comes from Micrometer. The relevant interceptor intercepts the invocation and updates the relevant metrics. We will talk about [interceptors](#interceptors) later.

## Nice. How does the dependency resolution work? I see no names or identifiers.

That’s a good question.
In CDI the process of matching a bean to an injection point is **type-safe**.
Each bean declares a set of bean types.
In our example above, the `Translator` bean has two bean types: `Translator` and `java.lang.Object`.
Subsequently, a bean is assignable to an injection point if the bean has a bean type that matches the _required type_ and has all the _required qualifiers_.
We’ll talk about qualifiers later.
For now, it’s enough to know that the bean above is assignable to an injection point of type `Translator` and `java.lang.Object`.

## Hm, wait a minute. What happens if multiple beans declare the same type?

There is a simple rule: **exactly one bean must be assignable to an injection point, otherwise the build fails**.
If none is assignable the build fails with `UnsatisfiedResolutionException`.
If multiple are assignable the build fails with `AmbiguousResolutionException`.
This is very useful because your application fails fast whenever the container is not able to find an unambiguous dependency for any injection point.

<dl><dt><strong>💡 TIP</strong></dt><dd>

You can use programmatic lookup via  `jakarta.enterprise.inject.Instance` to resolve ambiguities at runtime and even iterate over all beans implementing a given type:

```java
public class Translator {

    @Inject
    Instance<Dictionary> dictionaries; ①

    String translate(String sentence) {
      for (Dictionary dict : dictionaries) { ②
         // ...
      }
    }
}
```
1. This injection point will not result in an ambiguous dependency even if there are multiple beans that implement the `Dictionary` type.
2. `jakarta.enterprise.inject.Instance` extends `Iterable`.
</dd></dl>

## Can I use setter and constructor injection?

Yes, you can.
In fact, in CDI, the "setter injection" is superseded by more powerful [initializer methods](https://jakarta.ee/specifications/cdi/4.1/jakarta-cdi-spec-4.1.html#initializer_methods).
Initializers may accept multiple parameters and don’t have to follow the JavaBean naming conventions.

**Initialized and Constructor Injection Example**

```java
@ApplicationScoped
public class Translator {

    private final TranslatorHelper helper;

    Translator(TranslatorHelper helper) { ①
       this.helper = helper;
    }

    @Inject ②
    void setDeps(Dictionary dic, LocalizationService locService) { ③
      // ...
    }
}
```
1. This is a constructor injection.
In fact, this code would not work in regular CDI implementations where a bean with a normal scope must always declare a no-args constructor and the bean constructor must be annotated with `@Inject`.
However, in Quarkus, we detect the absence of no-args constructor and "add" it directly in the bytecode.
It’s also not necessary to add `@Inject` if there is only one constructor present.
2. An initializer method must be annotated with `@Inject`.
3. An initializer may accept multiple parameters - each one is an injection point.

## You talked about some qualifiers?

[Qualifiers](https://jakarta.ee/specifications/cdi/4.1/jakarta-cdi-spec-4.1.html#qualifiers) are annotations that help the container to distinguish beans that implement the same type.
As we already said, a bean is assignable to an injection point if it has all the required qualifiers.
If you declare no qualifier at an injection point, the `@Default` qualifier is assumed.

A qualifier type is a Java annotation defined as `@Retention(RUNTIME)` and annotated with the `@jakarta.inject.Qualifier` meta-annotation:

**Qualifier Example**

```java
@Qualifier
@Retention(RUNTIME)
@Target({METHOD, FIELD, PARAMETER, TYPE})
public @interface Superior {}
```

The qualifiers of a bean are declared by annotating the bean class or producer method or field with the qualifier types:

**Bean With Custom Qualifier Example**

```java
@Superior ①
@ApplicationScoped
public class SuperiorTranslator extends Translator {

    String translate(String sentence) {
      // ...
    }
}
```
1. `@Superior` is a [qualifier annotation](https://jakarta.ee/specifications/cdi/4.1/jakarta-cdi-spec-4.1.html#defining_qualifier_types).

This bean would be assignable to `@Inject @Superior Translator` and `@Inject @Superior SuperiorTranslator` but not to `@Inject Translator`.
The reason is that `@Inject Translator` is automatically transformed to `@Inject @Default Translator` during typesafe resolution.
And since our `SuperiorTranslator` does not declare `@Default` only the original `Translator` bean is assignable.

**📌 NOTE**\
The `@Named` qualifier, which you might be familiar with, is somewhat different in CDI to all other qualifiers.
See the [corresponding section](cdi-reference.md#string-based-qualifiers) in CDI Reference Guide for why you typically shouldn’t use it.

## Looks good. What is the bean scope?

The scope of a bean determines the lifecycle of its instances, i.e. when and where an instance should be created and destroyed.

**📌 NOTE**\
Every bean has exactly one scope.

## What scopes can I actually use in my Quarkus application?

You can use all the built-in scopes mentioned by the specification except for `jakarta.enterprise.context.ConversationScoped`.

|     |     |
| --- | --- |
| Annotation | Description |
| `@jakarta.enterprise.context.ApplicationScoped` | A single bean instance is used for the application and shared among all injection points. The instance is created lazily, i.e. once a method is invoked upon the [client proxy](#i-dont-understand-the-concept-of-client-proxies). |
| `@jakarta.inject.Singleton` | Just like `@ApplicationScoped` except that no client proxy is used. The instance is created when an injection point that resolves to a @Singleton bean is being injected. |
| `@jakarta.enterprise.context.RequestScoped` | The bean instance is associated with the current _request_ (usually an HTTP request). |
| `@jakarta.enterprise.context.Dependent` | This is a pseudo-scope. The instances are not shared and every injection point spawns a new instance of the dependent bean. The lifecycle of dependent bean is bound to the bean injecting it - it will be created and destroyed along with the bean injecting it. |
| `@jakarta.enterprise.context.SessionScoped` | This scope is backed by a `jakarta.servlet.http.HttpSession` object. It’s only available if the `quarkus-undertow` extension is used. |

**📌 NOTE**\
There can be other custom scopes provided by Quarkus extensions. For example, [`quarkus-narayana-jta`](../03-datos/transaction.md) provides [`jakarta.transaction.TransactionScoped`](../03-datos/transaction.md#transaction-scope).

## `@ApplicationScoped` and `@Singleton` look very similar. Which one should I choose for my Quarkus application?

It depends ;-).

A `@Singleton` bean has no [client proxy](#i-dont-understand-the-concept-of-client-proxies) and hence an instance is _created eagerly_ when the bean is injected. By contrast, an instance of an `@ApplicationScoped` bean is _created lazily_, i.e.
when a method is invoked upon an injected instance for the first time.

Furthermore, client proxies only delegate method invocations and thus you should never read/write fields of an injected `@ApplicationScoped` bean directly.
You can read/write fields of an injected `@Singleton` safely.

`@Singleton` should have a slightly better performance because there is no indirection (no proxy that delegates to the current instance from the context).

On the other hand, you cannot mock `@Singleton` beans using [QuarkusMock](../09-testing/getting-started-testing.md#quarkus_mock).

`@ApplicationScoped` beans can be also destroyed and recreated at runtime.
Existing injection points just work because the injected proxy delegates to the current instance.

Therefore, we recommend to stick with `@ApplicationScoped` by default unless there’s a good reason to use `@Singleton`.

## I don’t understand the concept of client proxies.

Indeed, the [client proxies](https://jakarta.ee/specifications/cdi/4.1/jakarta-cdi-spec-4.1.html#client_proxies) could be hard to grasp, but they provide some useful functionality.
A client proxy is basically an object that delegates all method invocations to a target bean instance.
It’s a container construct that implements `io.quarkus.arc.ClientProxy` and extends the bean class.

**❗ IMPORTANT**\
Client proxies only delegate method invocations. So never read or write a field of a normal scoped bean, otherwise you will work with non-contextual or stale data.

**Generated Client Proxy Example**

```java
@ApplicationScoped
class Translator {

    String translate(String sentence) {
      // ...
    }
}

// The client proxy class is generated and looks like...
class Translator_ClientProxy extends Translator { ①

    String translate(String sentence) {
      // Find the correct translator instance...
      Translator translator = getTranslatorInstanceFromTheApplicationContext();
      // And delegate the method invocation...
      return translator.translate(sentence);
    }
}
```
1. The `Translator_ClientProxy` instance is always injected instead of a direct reference to a [contextual instance](https://jakarta.ee/specifications/cdi/4.1/jakarta-cdi-spec-4.1.html#contextual_instance) of the `Translator` bean.

Client proxies allow for:

* Lazy instantiation - the instance is created once a method is invoked upon the proxy.
* Ability to inject a bean with "narrower" scope to a bean with "wider" scope; i.e. you can inject a `@RequestScoped` bean into an `@ApplicationScoped` bean.
* Circular dependencies in the dependency graph. Having circular dependencies is often an indication that a redesign should be considered, but sometimes it’s inevitable.
* In rare cases it’s practical to destroy the beans manually. A direct injected reference would lead to a stale bean instance.

## OK. You said that there are several kinds of beans?

Yes. In general, we distinguish:

1. Class beans
2. Producer methods
3. Producer fields
4. Synthetic beans

**📌 NOTE**\
Synthetic beans are usually provided by extensions. Therefore, we are not going to cover them in this guide.

Producer methods and fields are useful if you need additional control over instantiation of a bean.
They are also useful when integrating third-party libraries where you don’t control the class source and may not add additional annotations etc.

**Producers Example**

```java
@ApplicationScoped
public class Producers {

    @Produces ①
    double pi = Math.PI; ②

    @Produces ③
    List<String> names() {
       List<String> names = new ArrayList<>();
       names.add("Andy");
       names.add("Adalbert");
       names.add("Joachim");
       return names; ④
    }
}

@ApplicationScoped
public class Consumer {

   @Inject
   double pi;

   @Inject
   List<String> names;

   // ...
}
```
1. The container analyses the field annotations to build a bean metadata.
The _type_ is used to build the set of bean types.
In this case, it will be `double` and `java.lang.Object`.
No scope annotation is declared and so it’s defaulted to `@Dependent`.
2. The container will read this field when creating the bean instance.
3. The container analyses the method annotations to build a bean metadata.
The _return type_ is used to build the set of bean types.
In this case, it will be `List<String>`, `Collection<String>`, `Iterable<String>` and `java.lang.Object`.
No scope annotation is declared and so it’s defaulted to `@Dependent`.
4. The container will call this method when creating the bean instance.

There’s more about producers.
You can declare qualifiers, inject dependencies into the producer methods parameters, etc.
You can read more about producers for example in the [Weld docs](https://docs.jboss.org/weld/reference/latest/en-US/html/producermethods.html).

## OK, injection looks cool. What other services are provided?

### Lifecycle Callbacks

A bean class may declare lifecycle `@PostConstruct` and `@PreDestroy` callbacks:

**Lifecycle Callbacks Example**

```java
import jakarta.annotation.PostConstruct;
import jakarta.annotation.PreDestroy;

@ApplicationScoped
public class Translator {

    @PostConstruct ①
    void init() {
       // ...
    }

    @PreDestroy ②
    void destroy() {
      // ...
    }
}
```
1. This callback is invoked before the bean instance is put into service. It is safe to perform some initialization here.
2. This callback is invoked before the bean instance is destroyed. It is safe to perform some cleanup tasks here.

**💡 TIP**\
It’s a good practice to keep the logic in the callbacks "without side effects", i.e. you should avoid calling other beans inside the callbacks.

### Interceptors

Interceptors are used to separate cross-cutting concerns from business logic.
There is a separate specification - Java Interceptors - that defines the basic programming model and semantics.

**Simple Interceptor Binding Example**

```java
import java.lang.annotation.ElementType;
import java.lang.annotation.Inherited;
import java.lang.annotation.Retention;
import java.lang.annotation.RetentionPolicy;
import java.lang.annotation.Target;
import jakarta.interceptor.InterceptorBinding;

@InterceptorBinding // ①
@Retention(RetentionPolicy.RUNTIME)
@Target({ElementType.TYPE, ElementType.METHOD, ElementType.CONSTRUCTOR}) // ②
@Inherited // ③
public @interface Logged {
}
```
1. This is an interceptor binding annotation. See the following examples for how it’s used.
2. An interceptor binding annotation is always put on the interceptor type, and may be put on target types or methods.
3. Interceptor bindings are often `@Inherited`, but don’t have to be.

**Simple Interceptor Example**

```java
import jakarta.annotation.Priority;
import jakarta.interceptor.AroundInvoke;
import jakarta.interceptor.Interceptor;
import jakarta.interceptor.InvocationContext;

@Logged // ①
@Priority(2020) // ②
@Interceptor // ③
public class LoggingInterceptor {

   @Inject // ④
   Logger logger;

   @AroundInvoke // ⑤
   Object logInvocation(InvocationContext context) {
      // ...log before
      Object ret = context.proceed(); // ⑥
      // ...log after
      return ret;
   }

}
```
1. The interceptor binding annotation is used to bind our interceptor to a bean. Simply annotate a bean class with `@Logged`, as in the following example.
2. `Priority` enables the interceptor and affects the interceptor ordering. Interceptors with smaller priority values are called first.
3. Marks an interceptor component.
4. An interceptor may inject dependencies.
5. `AroundInvoke` denotes a method that interposes on business methods.
6. Proceed to the next interceptor in the interceptor chain or invoke the intercepted business method.

**📌 NOTE**\
Instances of interceptors are dependent objects of the bean instance they intercept, i.e. a new interceptor instance is created for each intercepted bean.

**Simple Example of Interceptor Usage**

```java
import jakarta.enterprise.context.ApplicationScoped;

@Logged // ① ②
@ApplicationScoped
public class MyService {
   void doSomething() {
       ...
   }
}
```
1. The interceptor binding annotation is put on a bean class so that all business methods are intercepted.
    The annotation can also be put on individual methods, in which case, only the annotated methods are intercepted.
2. Remember that the `@Logged` annotation is `@Inherited`.
    If there’s a bean class that inherits from `MyService`, the `LoggingInterceptor` will also apply to it.

### Decorators

Decorators are similar to interceptors, but because they implement interfaces with business semantics, they are able to implement business logic.

**Simple Decorator Example**

```java
import jakarta.decorator.Decorator;
import jakarta.decorator.Delegate;
import jakarta.annotation.Priority;
import jakarta.inject.Inject;
import jakarta.enterprise.inject.Any;
import jakarta.enterprise.inject.Decorated;
import jakarta.enterprise.inject.spi.Bean;

public interface Account {
   void withdraw(BigDecimal amount);
}

@Priority(10) ①
@Decorator ②
public class LargeTxAccount implements Account { ③

   @Inject
   @Any
   @Delegate
   Account delegate; ④

   @Inject
   @Decorated
   Bean<Account> delegateInfo; ⑤

   @Inject
   LogService logService; ⑥

   void withdraw(BigDecimal amount) {
      delegate.withdraw(amount); ⑦
      if (amount.compareTo(1000) > 0) {
         logService.logWithdrawal(delegate, amount);
      }
   }

}
```
1. `@Priority` enables the decorator. Decorators with smaller priority values are called first.
2. `@Decorator` marks a decorator component.
3. The set of decorated types includes all bean types which are Java interfaces, except for `java.io.Serializable`.
4. Each decorator must declare exactly one _delegate injection point_. The decorator applies to beans that are assignable to this delegate injection point.
5. It is possible to obtain information about the decorated bean by using the `@Decorated` qualifier.
6. Decorators can inject other beans.
7. The decorator may invoke any method of the delegate object. And the container invokes either the next decorator in the chain or the business method of the intercepted instance.

**📌 NOTE**\
Instances of decorators are dependent objects of the bean instance they intercept, i.e. a new decorator instance is created for each intercepted bean.

### Events and Observers

Beans may also produce and consume events to interact in a completely decoupled fashion.
Any Java object can serve as an event payload.
The optional qualifiers act as topic selectors.

**Simple Event Example**

```java

class TaskCompleted {
  // ...
}

@ApplicationScoped
class ComplicatedService {

   @Inject
   Event<TaskCompleted> event; ①

   void doSomething() {
      // ...
      event.fire(new TaskCompleted()); ②
   }

}

@ApplicationScoped
class Logger {

   void onTaskCompleted(@Observes TaskCompleted task) { ③
      // ...log the task
   }

}
```
1. `jakarta.enterprise.event.Event` is used to fire events.
2. Fire the event synchronously.
3. This method is notified when a `TaskCompleted` event is fired.

**💡 TIP**\
For more info about events/observers visit [Weld docs](https://docs.jboss.org/weld/reference/latest/en-US/html/events.html).

## Conclusion

In this guide, we’ve covered some basic topics of the Quarkus programming model that is based on the [Jakarta Contexts and Dependency Injection 4.1](https://jakarta.ee/specifications/cdi/4.1/jakarta-cdi-spec-4.1.html) specification.
Quarkus implements the CDI Lite specification, but not CDI Full.
See also [the list of supported features and limitations](cdi-reference.md#supported_features_and_limitations).
There are also quite a few [non-standard features](cdi-reference.md#nonstandard_features) and [Quarkus-specific APIs](cdi-reference.md#build_time_apis).

**💡 TIP**\
If you wish to learn more about Quarkus-specific features and limitations there is a Quarkus [CDI Reference Guide](cdi-reference.md).
We also recommend you to read the [CDI specification](https://jakarta.ee/specifications/cdi/4.1/jakarta-cdi-spec-4.1.html) and the [Weld documentation](https://docs.jboss.org/weld/reference/latest/en-US/html/) (Weld is a CDI Reference Implementation) to get acquainted with more complex topics.
