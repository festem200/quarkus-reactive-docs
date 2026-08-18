# Cross-Origin Resource Sharing (CORS)

> **Guia oficial:** <https://quarkus.io/guides/security-cors>  
> **Fuente:** `docs/src/main/asciidoc/security-cors.adoc` en [quarkusio/quarkus@3.38.2](https://github.com/quarkusio/quarkus/blob/3.38.2/docs/src/main/asciidoc/security-cors.adoc)  
> **Version documentada:** Quarkus 3.38.2 · **Sincronizado:** 2026-08-17 · **Licencia:** Apache-2.0

Enable and configure CORS in Quarkus to specify allowed origins, methods, and headers, guiding browsers in handling cross-origin requests safely.

Cross-Origin Resource Sharing (CORS) uses HTTP headers to manage browser requests for resources from external origins securely.
By specifying permitted origins, methods, and headers, Quarkus servers can use the CORS filter to enable browsers to request resources across domains while maintaining controlled access.
This mechanism enhances security and supports legitimate cross-origin requests.
For more on origin definitions, see the [Web Origin Concept](https://datatracker.ietf.org/doc/html/rfc6454).

## Enabling the CORS filter

To enforce CORS policies in your application, enable the Quarkus CORS filter by adding the following line to the `src/main/resources/application.properties` file:

```properties
quarkus.http.cors.enabled=true
```

The filter intercepts all incoming HTTP requests to identify cross-origin requests and applies the configured policy.
The filter then adds CORS headers to the HTTP response, informing browsers about allowed origins and access parameters.
For preflight requests, the filter returns an HTTP response immediately.
For regular CORS requests, the filter denies access with an HTTP 403 status if the request violates the configured policy; otherwise, the filter forwards the request to the destination if the policy allows it.

<dl><dt><strong>📌 NOTE</strong></dt><dd>

Despite its name, the CORS filter can also prevent CSRF attacks based on [Origin verification](https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html#using-standard-headers-to-verify-origin).
Therefore, since the browser is expected to set an [Origin header](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Origin) for cross-origin JavaScript and HTML form requests, you might want to consider using the CORS filter instead of the [REST CSRF filter](https://quarkus.io/guides/security-csrf-prevention).

You must confirm that the browser sets an `Origin` header for cross-origin requests when accessing your application, especially with HTML forms, before using the CORS filter to prevent CSRF through [Origin verification](https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html#using-standard-headers-to-verify-origin).
</dd></dl>

For detailed configuration options, see the following Configuration Properties section.

**📌 NOTE**\
La tabla de configuracion generada `quarkus-vertx-http_quarkus.http.cors` se produce al construir la documentacion y no existe en el codigo fuente. Consulta la referencia de configuracion en https://quarkus.io/guides/all-config

## Example CORS configuration

The following example shows a complete CORS filter configuration, including a regular expression to define one of the origins.

```properties
quarkus.http.cors.enabled=true ①
quarkus.http.cors.origins=http://example.com,http://www.example.io,/https://([a-z0-9\\-_]+)\\\\.app\\\\.mydomain\\\\.com/ ②
quarkus.http.cors.methods=GET,PUT,POST ③
quarkus.http.cors.headers=X-Custom ④
quarkus.http.cors.exposed-headers=Content-Disposition ⑤
quarkus.http.cors.access-control-max-age=24H ⑥
quarkus.http.cors.access-control-allow-credentials=true ⑦
```

1. Enables the CORS filter.
2. Specifies allowed origins, including a regular expression. When not specified, CORS is not permitted, and only same-origin requests are allowed.
3. Lists allowed HTTP methods for cross-origin requests.
4. Declares custom headers that clients can include in requests.
5. Identifies response headers that clients can access.
6. Sets how long preflight request results are cached.
7. Allows cookies or credentials in cross-origin requests.

When using regular expressions in an `application.properties` file, escape special characters with four backward slashes (`\\\\`) to ensure proper behavior.
For example:

* `\\\\.` matches a literal `.` character.
* `\\.` matches any single character as a regular expression metadata character.

<dl><dt><strong>❗ IMPORTANT</strong></dt><dd>

Incorrectly escaped patterns can lead to unintended behavior or security vulnerabilities.
Always verify regular expression syntax before deployment.
</dd></dl>

## When to accept all origins

<dl><dt><strong>⚠️ WARNING</strong></dt><dd>

Allowing unrestricted origins with `quarkus.http.cors.origins=*` in production environments poses severe security risks, such as unauthorized data access or resource abuse.
For production, define explicit origins in the `quarkus.http.cors.origins` property.
</dd></dl>

The only exception where accepting all origins might be appropriate in production is for read-only public API applications that have no side effects of any kind, such as managing cookies, saving request data on the disk, or similar operations.
In such cases, to improve the HTTP cache performance, you might want to return a literal `*` origin by setting `quarkus.http.cors.return-exact-origins=false` to avoid the `Vary: Origin` response header.

Also, since configuring origins during development can be challenging, consider allowing all origins in development mode:

```properties
quarkus.http.cors.enabled=true
%dev.quarkus.http.cors.origins=/.*/
```

## Configuring the CORS filter programmatically

To enforce CORS policies in your application, enable the Quarkus CORS filter with the `io.quarkus.vertx.http.security.HttpSecurity` CDI event:

```java
package org.acme.http.security;

import io.quarkus.vertx.http.security.HttpSecurity;
import jakarta.enterprise.event.Observes;

public class CorsProgrammaticConfig {
    void configure(@Observes HttpSecurity httpSecurity) {
        httpSecurity.cors("https://example.com");
    }
}
```

The `io.quarkus.vertx.http.security.CORS` builder allows you to create a complete CORS configuration:

```java
package org.acme.http.security;

import io.quarkus.vertx.http.security.CORS;
import io.quarkus.vertx.http.security.HttpSecurity;
import jakarta.enterprise.event.Observes;

public class CorsProgrammaticConfig {
    void configure(@Observes HttpSecurity httpSecurity) {
        httpSecurity.cors(CORS.builder()
                .origin("https://example.com")
                .method("POST")
                .build());
    }
}
```

## References

* [Quarkus Security overview](https://quarkus.io/guides/security-overview)
* [Quarkus HTTP Reference](http-reference.md)
* [Mozilla HTTP CORS documentation](https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS)
