# Update projects to the latest Quarkus version

> **Guia oficial:** <https://quarkus.io/guides/update-quarkus>  
> **Fuente:** `docs/src/main/asciidoc/update-quarkus.adoc` en [quarkusio/quarkus@3.38.2](https://github.com/quarkusio/quarkus/blob/3.38.2/docs/src/main/asciidoc/update-quarkus.adoc)  
> **Version documentada:** Quarkus 3.38.2 · **Sincronizado:** 2026-08-17 · **Licencia:** Apache-2.0

You can update or upgrade your Quarkus projects to the latest version of Quarkus by using an update command.

The update command primarily employs OpenRewrite recipes to automate updates for most project dependencies, source code, and documentation.

<dl><dt><strong>❗ IMPORTANT</strong></dt><dd>

The update command automates only a subset of the migration.
Always review the [Migration Guides](https://github.com/quarkusio/quarkus/wiki/Migration-Guides) for your target version to identify any additional steps that require manual changes.
</dd></dl>

Post-update, if expected updates are missing, consider the following reasons:

* The recipe might not include a specific item in your project.
* Your project might use an extension that is incompatible with the latest Quarkus version.

## Prerequisites

To complete this guide, you need:

* Roughly 30 minutes
* An IDE
* JDK 17+ installed with `JAVA_HOME` configured appropriately
* Apache Maven 3.9.16
* Optionally the [Quarkus CLI](cli-tooling.md) if you want to use it
* Optionally Mandrel or GraalVM installed and [configured appropriately](../08-rendimiento-nativo/building-native-image.md#configuring-graalvm) if you want to build a native executable (or Docker if you use a native container build)
* A project based on Quarkus version 2.13 or later.

## Procedure

1. Create a working branch for your project by using your version control system.
2. To use the Quarkus CLI in the next step, [install the latest version of the Quarkus CLI](cli-tooling.md#installing-the-cli).
Confirm the version number using `quarkus -v`.
3. Go to the project directory and update the project to the latest stream:

   **Using Quarkus CLI**

   ```bash
   quarkus update
   ```
   Optional: To specify a particular stream, use the `--stream` option; for example: `--stream=3.2`

   **Using Maven**

   ```bash
   ./mvnw io.quarkus.platform:quarkus-maven-plugin:3.38.2:update -N
   ```
   Optional: To specify a particular stream, use the `-Dstream` option; for example: `-Dstream=3.2`
4. Analyze the update command output for potential instructions and perform the suggested tasks if necessary.
5. Use a diff tool to inspect all changes.
6. Review the [Migration Guides](https://github.com/quarkusio/quarkus/wiki/Migration-Guides) for your target version and apply any additional steps not covered by the update command.
7. Ensure the project builds without errors, all tests pass, and the application functions as required before deploying to production.

## Update recipes

The OpenRewrite recipes used by the update command are maintained in the [Quarkus Updates](https://github.com/quarkusio/quarkus-updates) repository.
If you find that a recipe is missing or incorrect, you can contribute improvements there.
Refer to the [README.md](https://github.com/quarkusio/quarkus-updates/blob/main/README.md) and the [CONTRIBUTING.md](https://github.com/quarkusio/quarkus-updates/blob/main/CONTRIBUTING.md) guide for detailed instructions on how to write and test recipes.
