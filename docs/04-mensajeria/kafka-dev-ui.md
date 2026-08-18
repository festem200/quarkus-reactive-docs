# Kafka Dev UI

> **Guia oficial:** <https://quarkus.io/guides/kafka-dev-ui>  
> **Fuente:** `docs/src/main/asciidoc/kafka-dev-ui.adoc` en [quarkusio/quarkus@3.38.2](https://github.com/quarkusio/quarkus/blob/3.38.2/docs/src/main/asciidoc/kafka-dev-ui.adoc)  
> **Version documentada:** Quarkus 3.38.2 · **Sincronizado:** 2026-08-17 · **Licencia:** Apache-2.0

If any Kafka-related extension is present (e.g. `quarkus-messaging-kafka`),
the Quarkus Dev UI is extended with a Kafka broker management UI.
It is connected automatically to the Kafka broker configured for the application.

![kafka-dev-ui-link](../_assets/kafka-dev-ui-link.png)

With the **Kafka Dev UI**, you can directly manage your Kafka cluster and perform tasks, such as:

* Listing and creating topics
* Visualizing records
* Publishing new records
* Inspecting the list of consumer groups and their consumption lag

![kafka-dev-ui-records](../_assets/kafka-dev-ui-records.png)

**❗ IMPORTANT**\
Kafka Dev UI is part of the Quarkus Dev UI and is only available in development mode.
