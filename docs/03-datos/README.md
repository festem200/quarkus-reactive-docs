# Acceso a datos no bloqueante

Quarkus 3.38.2 · sincronizado 2026-08-17 · [volver al indice](../00-INDICE.md)

- [reactive-sql-clients](reactive-sql-clients.md) — The Reactive SQL Clients have a straightforward API focusing on scalability and low-overhead. Currently, the following database servers are supported:
- [hibernate-reactive](hibernate-reactive.md) — Hibernate Reactive is a reactive API for Hibernate ORM, supporting non-blocking database drivers and a reactive style of interaction with the database.
- [hibernate-reactive-panache](hibernate-reactive-panache.md) — Hibernate Reactive is the only reactive Jakarta Persistence (formerly known as JPA) implementation and offers you the full breadth of an Object Relational Mapper allowing you to access your database o…
- [datasource](datasource.md) — Use a unified configuration model to define data sources for Java Database Connectivity (JDBC) and Reactive drivers.
- [transaction](transaction.md) — The quarkus-narayana-jta extension provides a Transaction Manager that coordinates and expose transactions to your applications as described in the Jakarta Transactions specification, formerly known a…
- [mongodb](mongodb.md) — MongoDB is a well known NoSQL Database that is widely used.
- [mongodb-panache](mongodb-panache.md) — MongoDB is a well known NoSQL Database that is widely used, but using its raw API can be cumbersome as you need to express your entities and your queries as a MongoDB Document.
- [mongodb-dev-services](mongodb-dev-services.md) — Quarkus supports a feature called Dev Services that allows you to create various datasources without any config. In the case of MongoDB this support extends to the default MongoDB connection. What tha…
- [redis](redis.md) — This guide demonstrates how your Quarkus application can connect to a Redis server using the Redis Client extension.
- [redis-reference](redis-reference.md) — Redis is an in-memory data store used as a database, cache, streaming engine, and message broker. The Quarkus Redis extension allows integrating Quarkus applications with Redis.
- [redis-dev-services](redis-dev-services.md) — Quarkus supports a feature called Dev Services that allows you to create various datasources without any config. What that means practically, is that if you have docker running and have not configured…
- [cache](cache.md) — In this guide, you will learn how to enable application data caching in any CDI managed bean of your Quarkus application.
- [cache-redis-reference](cache-redis-reference.md) — By default, Quarkus Cache uses Caffeine as backend. It’s possible to use Redis instead.
- [cache-infinispan-reference](cache-infinispan-reference.md) — By default, Quarkus Cache uses Caffeine as backend. It’s possible to use Infinispan instead.
- [infinispan-client](infinispan-client.md) — This guide demonstrates how your Quarkus application can connect to an Infinispan server using the Infinispan Client extension.
- [infinispan-client-reference](infinispan-client-reference.md) — Infinispan is a distributed, in-memory key/value store that provides Quarkus applications with a highly configurable and independently scalable data layer. This extension gives you client functionalit…
- [cassandra](cassandra.md) — Apache Cassandra® is a free and open-source, distributed, wide column store, NoSQL database management system designed to handle large amounts of data across many commodity servers, providing high ava…
- [elasticsearch](elasticsearch.md) — Elasticsearch is a well known full text search engine and NoSQL datastore.
- [databases-dev-services](databases-dev-services.md) — When testing or running in dev mode Quarkus can provide you with a zero-config database out of the box, a feature we refer to as Dev Services. Depending on your database type you may need Docker insta…
- [flyway](flyway.md) — Flyway is a popular database migration tool that is commonly used in JVM environments.
- [liquibase](liquibase.md) — Liquibase is an open source tool for database schema change management.
