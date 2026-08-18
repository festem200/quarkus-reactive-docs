# Resiliencia, service discovery y scheduling

Quarkus 3.38.2 · sincronizado 2026-08-17 · [volver al indice](../00-INDICE.md)

- [smallrye-fault-tolerance](smallrye-fault-tolerance.md) — One of the challenges brought by the distributed nature of microservices is that communication with external systems is inherently unreliable. This increases demand on resiliency of applications. To s…
- [stork](stork.md) — The essence of distributed systems resides in the interaction between services. In modern architecture, you often have multiple instances of your service to share the load or improve the resilience by…
- [stork-reference](stork-reference.md) — This guide is the companion from the Stork Getting Started Guide. It explains the configuration and usage of SmallRye Stork integration in Quarkus.
- [stork-registration](stork-registration.md) — This guide explains how to enable automatic registration and deregistration of a Quarkus application using SmallRye Stork and Consul, with minimal or no configuration.
- [stork-manual-service-registration](stork-manual-service-registration.md) — This guide explains how to implement a custom service registrar for SmallRye Stork and use it to programmatically register service instances at startup.
- [stork-kubernetes](stork-kubernetes.md) — This guide explains how to use Stork with Kubernetes for service discovery and load balancing.
- [load-shedding-reference](load-shedding-reference.md) — This technology is considered experimental.
- [smallrye-health](smallrye-health.md) — This guide demonstrates how your Quarkus application can use SmallRye Health an implementation of the MicroProfile Health specification.
- [scheduler](scheduler.md) — Modern applications often need to run specific tasks periodically. In this guide, you learn how to schedule periodic tasks.
- [scheduler-reference](scheduler-reference.md) — Modern applications often need to run specific tasks periodically. There are two scheduler extensions in Quarkus. The quarkus-scheduler extension brings the API and a lightweight in-memory scheduler i…
- [quartz](quartz.md) — Modern applications often need to run specific tasks periodically. In this guide, you learn how to schedule periodic clustered tasks using the Quartz extension.
- [lra](lra.md) — The LRA (short for Long Running Action) participant extension is useful in microservice based designs where different services can benefit from a relaxed notion of distributed consistency.
- [lra-dev-services](lra-dev-services.md) — If the Narayana LRA extension is present (quarkus-narayana-lra), the Dev Services for Narayana LRA coordinator automatically starts the Narayana LRA coordinator in dev mode and when running tests. So,…
- [software-transactional-memory](software-transactional-memory.md) — Software Transactional Memory (STM) has been around in research environments since the late 1990’s and has relatively recently started to appear in products and various programming languages. We won’t…
