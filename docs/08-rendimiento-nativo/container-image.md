# Container Images

> **Guia oficial:** <https://quarkus.io/guides/container-image>  
> **Fuente:** `docs/src/main/asciidoc/container-image.adoc` en [quarkusio/quarkus@3.38.2](https://github.com/quarkusio/quarkus/blob/3.38.2/docs/src/main/asciidoc/container-image.adoc)  
> **Version documentada:** Quarkus 3.38.2 · **Sincronizado:** 2026-08-17 · **Licencia:** Apache-2.0

Quarkus provides extensions for building (and pushing) container images. Currently, it supports:

* [Jib](#jib)
* [Docker](#docker)
* [Podman](#podman)
* [OpenShift](#openshift)
* [Buildpack](#buildpack)

## Container Image extensions

### Jib

The extension `quarkus-container-image-jib` is powered by [Jib](https://github.com/GoogleContainerTools/jib) for performing container image builds.
The major benefit of using Jib with Quarkus is that all the dependencies (everything found under `target/lib`) are cached in a different layer than the actual application making rebuilds really fast and small (when it comes to pushing).
Another important benefit of using this extension is that it provides the ability to create a container image without having to have any dedicated client side tooling (like Docker) or running daemon processes (like the Docker daemon)
when all that is needed is the ability to push to a container image registry.

To use this feature, add the following extension to your project:

**CLI**

```bash
quarkus extension add quarkus-container-image-jib
```
**Maven**

```bash
./mvnw quarkus:add-extension -Dextensions='quarkus-container-image-jib'
```
**Gradle**

```bash
./gradlew addExtension --extensions='quarkus-container-image-jib'
```

**⚠️ WARNING**\
In situations where all that is needed to build a container image and no push to a registry is necessary (essentially by having set `quarkus.container-image.build=true` and left `quarkus.container-image.push` unset - it defaults to `false`), then this extension creates a container image and registers
it with the Docker daemon. This means that although Docker isn’t used to build the image, it is nevertheless necessary. Also note that using this mode, the built container image **will**
show up when executing `docker images`.

#### Including extra files

There are cases when additional files (other than ones produced by the Quarkus build) need to be added to a container image.
To support these cases, Quarkus copies any file under `src/main/jib` into the built container image (which is essentially the same
idea that the Jib Maven and Gradle plugins support).
For example, the presence of `src/main/jib/foo/bar` would result in  `/foo/bar` being added into the container filesystem.

#### JVM Debugging

There are cases where the built container image may need to have Java debugging conditionally enabled at runtime.

When the base image has not been changed (and therefore `ubi9/openjdk-17-runtime`, or `ubi9/openjdk-21-runtime` is used), then the `quarkus.jib.jvm-additional-arguments` configuration property can be used in order to
make the JVM listen on the debug port at startup.

The exact configuration is:

```properties
quarkus.jib.jvm-additional-arguments=-agentlib:jdwp=transport=dt_socket\\,server=y\\,suspend=n\\,address=*:5005
```

Other base images might provide launch scripts that enable debugging when an environment variable is set, in which case you would set that environment variable when launching the container.

#### Custom Entrypoint

The `quarkus.jib.jvm-entrypoint` configuration property can be used to completely override the container entry point and can thus be used to either hard code the JVM debug configuration or point to a script that handles the details.

For example, if the base images `ubi9/openjdk-17-runtime` or  `ubi9/openjdk-21-runtime` are used to build the container, the entry point can be hard-coded on the application properties file.

**Example application.properties**

```properties
quarkus.jib.jvm-entrypoint=java,-Dcustom.param=custom_value,-jar,quarkus-run.jar
```

Or a custom start-up script can be created and referenced on the properties file. This approach works better if there’s a need to set application params using environment variables:

**Example application.properties**

```properties
quarkus.jib.jvm-entrypoint=/bin/sh,run-java.sh
```

**Example src/main/jib/home/jboss/run-java.sh**

```shell
java \
  -Djavax.net.ssl.trustStore=/deployments/truststore \
  -Djavax.net.ssl.trustStorePassword="$TRUST_STORE_PASSWORD" \
  -jar quarkus-run.jar
```

**📌 NOTE**\
`/home/jboss` is the WORKDIR for all quarkus binaries in the base images `ubi9/openjdk-17-runtime` and `ubi9/openjdk-21-runtime` ([Dockerfile for ubi9/openjdk-17-runtime](https://catalog.redhat.com/software/containers/ubi9/openjdk-21-runtime/6501ce769a0d86945c422d5f?container-tabs=dockerfile))

#### Multi-module projects and layering

When building a multi-module project containing a Quarkus application as one module and various supporting project dependencies as other modules,
Quarkus supports placing these supporting modules in a separate container image layer from the rest of the application dependencies, with the expectation
that these supporting modules will change more frequently than the regular application dependencies - thus making a rebuild faster if the
application dependencies have not changed.

To enable this feature, the property `quarkus.bootstrap.workspace-discovery` needs to be set to `true` either as a system property
when invoking the build tool, either as a build tool property. Setting this property in `application.properties` will ***not*** work because
this property needs to be known very early on in the build process.

#### AppCDS

Quarkus supports generating and including AOT caches (including [Application Class Data Sharing](https://docs.oracle.com/en/java/javase/17/docs/specs/man/java.html#application-class-data-sharing) archives) when generating container images.
See the [AOT Caching documentation](https://quarkus.io/guides/aot) for more details.

### Docker

The extension `quarkus-container-image-docker` is using the Docker binary and the generated Dockerfiles under `src/main/docker` in order to perform Docker builds.

To use this feature, add the following extension to your project.

**CLI**

```bash
quarkus extension add quarkus-container-image-docker
```
**Maven**

```bash
./mvnw quarkus:add-extension -Dextensions='quarkus-container-image-docker'
```
**Gradle**

```bash
./gradlew addExtension --extensions='quarkus-container-image-docker'
```

The `quarkus-container-image-docker` extension is capable of [creating multi-platform (or multi-arch)](https://docs.docker.com/buildx/working-with-buildx/#build-multi-platform-images/) images using [`docker buildx build`](https://docs.docker.com/engine/reference/commandline/buildx_build/). See the `quarkus.docker.buildx.*` configuration items in the [Docker Options](#docker-options) section below.

<dl><dt><strong>📌 NOTE</strong></dt><dd>

`docker buildx build` ONLY supports [loading the result of a build](https://docs.docker.com/engine/reference/commandline/buildx_build/#load) to `docker images` when building for a single platform. Therefore, if you specify more than one argument in the `quarkus.docker.buildx.platform` property, the resulting images will not be loaded into `docker images`. If `quarkus.docker.buildx.platform` is omitted or if only a single platform is specified, it will then be loaded into `docker images`.

This means that if you want to build images for more than one platform at a time (i.e. `quarkus.docker.buildx.platform=linux/amd64,linux/arm64`), you need to push the images (`quarkus.container-image.push=true`) directly as part of the build process. Docker buildx does not support loading into the local registry when building multi-platform images.
</dd></dl>

### Podman

The extension `quarkus-container-image-podman` uses [Podman](https://podman.io/) and the generated `Dockerfiles` under `src/main/docker` in order to perform container builds.

To use this feature, add the following extension to your project.

**CLI**

```bash
quarkus extension add quarkus-container-image-podman
```
**Maven**

```bash
./mvnw quarkus:add-extension -Dextensions='quarkus-container-image-podman'
```
**Gradle**

```bash
./gradlew addExtension --extensions='quarkus-container-image-podman'
```

<dl><dt><strong>💡 TIP: When to use Docker vs Podman extension</strong></dt><dd>

The [Docker extension](#docker) is and has always been backwards-compatible with Podman because Podman exposes a [Docker-compatible API](https://podman.io/docs/installation). You can build container images with Podman using the Docker extension (see the [Using Podman with Quarkus guide](https://quarkus.io/guides/podman)).

Use either the `quarkus-container-image-docker` or `quarkus-container-image-podman` extension when doing things specific to either Docker or Podman, respectively.

For example, building multi-platform images is implemented differently for Docker and Podman. Docker uses [the buildx plugin](https://docs.docker.com/engine/reference/commandline/buildx_build/) whereas Podman can build multi-platform images [natively](https://docs.podman.io/en/latest/markdown/podman-build.1.html#platform-os-arch-variant). Because of this, you would need to use the specific extension to perform that function.
</dd></dl>

### OpenShift

The extension `quarkus-container-image-openshift` is using OpenShift binary builds in order to perform container builds inside the OpenShift cluster.
The idea behind the binary build is that you just upload the artifact and its dependencies to the cluster and during the build they will be merged to a builder image (defaults to `ubi9/openjdk-17` or `ubi9/openjdk-21`).

The benefit of this approach, is that it can be combined with OpenShift’s `DeploymentConfig` that makes it easy to roll out changes to the cluster.

To use this feature, add the following extension to your project.

**CLI**

```bash
quarkus extension add quarkus-container-image-openshift
```
**Maven**

```bash
./mvnw quarkus:add-extension -Dextensions='quarkus-container-image-openshift'
```
**Gradle**

```bash
./gradlew addExtension --extensions='quarkus-container-image-openshift'
```

OpenShift builds require creating a `BuildConfig` and two `ImageStream` resources, one for the builder image and one for the output image.
The creation of such objects is being taken care of by the Quarkus Kubernetes extension.

### Buildpack

The extension `quarkus-container-image-buildpack` is using buildpacks in order to perform container image builds.
Under the hood buildpacks will use a Docker daemon for the actual build.
While buildpacks support alternatives to Docker, this extension will only work with Docker.

Additionally, the user will have to configure which build image to use (no default image is provided). For example:

```properties
quarkus.buildpack.jvm-builder-image=<jvm builder image>
```

or for native:

```properties
quarkus.buildpack.native-builder-image=<native builder image>
```

To use this feature, add the following extension to your project.

**CLI**

```bash
quarkus extension add quarkus-container-image-buildpack
```
**Maven**

```bash
./mvnw quarkus:add-extension -Dextensions='quarkus-container-image-buildpack'
```
**Gradle**

```bash
./gradlew addExtension --extensions='quarkus-container-image-buildpack'
```

**📌 NOTE**\
When using the buildpack container image extension it is strongly advised to avoid adding `quarkus.container-image.build=true` in your properties configuration as it might trigger nesting builds within builds. It’s preferable to pass it as an option to the build command instead.

## Building

To build a container image for your project, `quarkus.container-image.build=true` needs to be set using any of the ways that Quarkus supports.

**CLI**

```bash
quarkus build
quarkus deploy openshift
```
**Maven**

```bash
./mvnw install -Dquarkus.container-image.build=true
```
**Gradle**

```bash
./gradlew build -Dquarkus.container-image.build=true
```

**📌 NOTE**\
If you ever want to build a native container image and already have an existing native image you can set `-Dquarkus.native.reuse-existing=true` and the native image build will not be re-run.

## Using @QuarkusIntegrationTest

To run tests on the resulting image, `quarkus.container-image.build=true` needs to be set using any of the ways that Quarkus supports.

**Maven**

```bash
./mvnw verify -Dquarkus.container-image.build=true
```
**Gradle**

```bash
./gradlew quarkusIntTest -Dquarkus.container-image.build=true
```

## Pushing

To push a container image for your project, `quarkus.container-image.push=true` needs to be set using any of the ways that Quarkus supports.

**CLI**

```bash
quarkus build
quarkus deploy openshift
```
**Maven**

```bash
./mvnw install -Dquarkus.container-image.push=true
```
**Gradle**

```bash
./gradlew build -Dquarkus.container-image.push=true
```

**📌 NOTE**\
If no registry is set (using `quarkus.container-image.registry`) then `docker.io` will be used as the default.

## Selecting among multiple extensions

It does not make sense to use multiple extension as part of the same build. When multiple container image extensions are present, an error will be raised to inform the user. The user can either remove the unneeded extensions or select one using `application.properties`.

For example, if both `container-image-docker` and `container-image-podman` are present and the user needs to use `container-image-docker`:

```properties
quarkus.container-image.builder=docker
```

## Integrating with `systemd-notify`

If you are building a container image in order to deploy your Quarkus application as a Linux service with Podman and Systemd, you might want to consider including the [Quarkus Systemd Notify Extension](https://docs.quarkiverse.io/quarkus-systemd-notify/dev/index.html) as part of your application, with:

**CLI**

```bash
quarkus extension add io.quarkiverse.systemd.notify:quarkus-systemd-notify
```
**Maven**

```bash
./mvnw quarkus:add-extension -Dextensions='io.quarkiverse.systemd.notify:quarkus-systemd-notify'
```
**Gradle**

```bash
./gradlew addExtension --extensions='io.quarkiverse.systemd.notify:quarkus-systemd-notify'
```

## Customizing

The following properties can be used to customize the container image build process.

### Container Image Options

**📌 NOTE**\
La tabla de configuracion generada `quarkus-container-image` se produce al construir la documentacion y no existe en el codigo fuente. Consulta la referencia de configuracion en https://quarkus.io/guides/all-config

#### Using CI Environments

Various CI environments provide a ready to use container-image registry which can be combined with the container-image Quarkus extensions in order to
effortlessly create and push a Quarkus application to said registry.

For example, [GitLab](https://gitlab.com/) provides such a registry and in the provided CI environment,
makes available the `CI_REGISTRY_IMAGE` environment variable
(see GitLab’s [documentation](https://docs.gitlab.com/ee/ci/variables/)) for more information), which can be used in Quarkus like so:

```properties
quarkus.container-image.image=${CI_REGISTRY_IMAGE}
```

**📌 NOTE**\
See [this](../01-fundamentos/config-reference.md#with-environment-variables) for more information on how to combine properties with environment variables.

### Jib Options

In addition to the generic container image options, the `container-image-jib` also provides the following options:

**📌 NOTE**\
La tabla de configuracion generada `quarkus-container-image-jib` se produce al construir la documentacion y no existe en el codigo fuente. Consulta la referencia de configuracion en https://quarkus.io/guides/all-config

### Docker Options

In addition to the generic container image options, the `container-image-docker` also provides the following options:

**📌 NOTE**\
La tabla de configuracion generada `quarkus-container-image-docker` se produce al construir la documentacion y no existe en el codigo fuente. Consulta la referencia de configuracion en https://quarkus.io/guides/all-config

### Podman Options

In addition to the generic container image options, the `container-image-podman` also provides the following options:

**📌 NOTE**\
La tabla de configuracion generada `quarkus-container-image-podman` se produce al construir la documentacion y no existe en el codigo fuente. Consulta la referencia de configuracion en https://quarkus.io/guides/all-config

### OpenShift  Options

In addition to the generic container image options, the `container-image-openshift` also provides the following options:

**📌 NOTE**\
La tabla de configuracion generada `quarkus-container-image-openshift_quarkus.openshift` se produce al construir la documentacion y no existe en el codigo fuente. Consulta la referencia de configuracion en https://quarkus.io/guides/all-config

### Buildpack Options

In addition to the generic container image options, the `container-image-buildpack` also provides the following options:

**📌 NOTE**\
La tabla de configuracion generada `quarkus-container-image-buildpack_quarkus.buildpack` se produce al construir la documentacion y no existe en el codigo fuente. Consulta la referencia de configuracion en https://quarkus.io/guides/all-config
