# Observability Dev Services

> **Guia oficial:** <https://quarkus.io/guides/observability-devservices>  
> **Fuente:** `docs/src/main/asciidoc/observability-devservices.adoc` en [quarkusio/quarkus@3.38.2](https://github.com/quarkusio/quarkus/blob/3.38.2/docs/src/main/asciidoc/observability-devservices.adoc)  
> **Version documentada:** Quarkus 3.38.2 · **Sincronizado:** 2026-08-17 · **Licencia:** Apache-2.0

We are already familiar with [Dev Service](../09-testing/dev-services.md) concept, but in the case of Observability we need a way to orchestrate and connect more than a single Dev Service, usually a whole stack of them; e.g. a metrics agent periodically scraping application for metrics, pushing them into timeseries database, and Grafana feeding graphs of this timeseries data.

With this in mind, we added a new concept of Dev Resource, an adapter between Dev Service concept and [Testcontainers](https://testcontainers.com/). And since we now have fine-grained services - with the Dev Resource per container, we can take this even further, allowing the user to choose the way to use this new Dev Resource concept:

**📌 NOTE**\
Each Dev Resource implementation is an `@QuarkusTestResourceLifecycleManager` implementation as well

* leave it to Dev Services to pick-up various Dev Resources from classpath, and apply [Dev Service](../09-testing/dev-services.md) concept to it
* explicitly disable Dev Services and enable Dev Resources and use less-heavy concept of starting and stopping Dev Resources
* explicitly disable both Dev Services and Dev Resources, and use Quarkus' `@QuarkusTestResource` testing concept (see Note)

You can either add Observability extension dependency along with needed Dev Resources dependencies, or you use existing `sinks` - pom.xml files which add Observability extension dependency along with other required dependencies for certain technology stacks; e.g. `victoriametrics` sink would have `quarkus-observability-devresource-victoriametrics` and `quarkus-victoriametrics-client` dependencies already included in the `pom.xml`.

<dl><dt><strong>📌 NOTE</strong></dt><dd>

Make sure you set the `scope` of these sink dependencies to `provided`, otherwise libraries such as Testcontainers will end-up in your app’s production libraries:
```xml
        <dependency>
            <groupId>io.quarkus</groupId>
            <artifactId>quarkus-observability-devservices-...</artifactId>
            <scope>provided</scope> <!-- !! -->
        </dependency>
```
</dd></dl>

Let’s see how all of this looks in practice, with the usual `all-in-one` Grafana usage, in the form of [OTel-LGTM](https://github.com/grafana/docker-otel-lgtm) Docker image.

* [Getting Started with Grafana-OTel-LGTM](observability-devservices-lgtm.md)
