#!/usr/bin/env python3
"""Genera el corpus Markdown de este repositorio a partir de la documentacion
oficial de Quarkus (AsciiDoc, licencia Apache-2.0).

Flujo:
  1. Clona (sparse, shallow) quarkusio/quarkus en el tag indicado.
  2. Resuelve atributos AsciiDoc contra las propiedades Maven del propio tag.
  3. Resuelve los include:: (incluidos tags parciales) para no perder contenido.
  4. Convierte a Markdown con downdoc (Node).
  5. Reescribe enlaces cruzados, copia imagenes y genera indices.

Uso:
  python3 scripts/build_docs.py                # ultimo release estable
  python3 scripts/build_docs.py --tag 3.33.2   # una version concreta (LTS)
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import shutil
import subprocess
import sys
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from catalogo import CATEGORIAS, mapa_docs  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
DIR_DOCS = RAIZ / "docs"
DIR_ASSETS = DIR_DOCS / "_assets"
DIR_TRABAJO = RAIZ / ".build"
REPO_UPSTREAM = "https://github.com/quarkusio/quarkus.git"
GUIA_URL = "https://quarkus.io/guides/{}"

POMS = [
    "pom.xml",
    "build-parent/pom.xml",
    "bom/application/pom.xml",
    "docs/pom.xml",
]


# --------------------------------------------------------------------------- #
# utilidades
# --------------------------------------------------------------------------- #
def log(msg: str) -> None:
    print(f"[build] {msg}", flush=True)


def sh(cmd: list[str], cwd: Path | None = None) -> str:
    res = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if res.returncode != 0:
        raise RuntimeError(f"fallo {' '.join(cmd)}\n{res.stderr[-2000:]}")
    return res.stdout


def ultimo_tag() -> str:
    url = "https://api.github.com/repos/quarkusio/quarkus/releases/latest"
    with urllib.request.urlopen(url, timeout=30) as r:
        return json.load(r)["tag_name"]


# --------------------------------------------------------------------------- #
# 1. obtener las fuentes
# --------------------------------------------------------------------------- #
def clonar(tag: str) -> Path:
    destino = DIR_TRABAJO / "quarkus-src"
    if (destino / ".git").exists():
        actual = sh(["git", "-C", str(destino), "describe", "--tags", "--always"]).strip()
        if actual == tag:
            log(f"reutilizando clon existente en {tag}")
            return destino
        shutil.rmtree(destino)
    destino.parent.mkdir(parents=True, exist_ok=True)
    log(f"clonando quarkusio/quarkus @ {tag} (sparse, shallow)")
    sh(["git", "clone", "--filter=blob:none", "--sparse", "--depth", "1",
        "--branch", tag, REPO_UPSTREAM, str(destino)])
    sh(["git", "sparse-checkout", "set", "docs/src/main/asciidoc"], cwd=destino)
    return destino


def propiedades_maven(tag: str) -> dict[str, str]:
    """Propiedades <properties> de los pom.xml relevantes del tag."""
    props: dict[str, str] = {}
    for pom in POMS:
        url = f"https://raw.githubusercontent.com/quarkusio/quarkus/{tag}/{pom}"
        try:
            with urllib.request.urlopen(url, timeout=60) as r:
                texto = r.read().decode("utf-8", "replace")
        except Exception as exc:  # pragma: no cover
            log(f"aviso: no se pudo leer {pom} ({exc})")
            continue
        for bloque in re.findall(r"<properties>(.*?)</properties>", texto, re.S):
            for k, v in re.findall(r"<([\w.\-]+)>([^<]*)</\1>", bloque):
                props.setdefault(k, v.strip())
    props["project.version"] = tag
    props["quarkus.version"] = tag
    props.setdefault("quarkus-base-url", "https://github.com/quarkusio/quarkus")
    props.setdefault("quarkus-home-url", "https://quarkus.io")
    props.setdefault("proposed-maven-version", props.get("maven.version", "3.9.9"))

    # resolver ${...} anidados
    for _ in range(6):
        cambios = False
        for k, v in list(props.items()):
            nuevo = re.sub(r"\$\{([\w.\-]+)\}", lambda m: props.get(m.group(1), m.group(0)), v)
            if nuevo != v:
                props[k] = nuevo
                cambios = True
        if not cambios:
            break
    return props


# --------------------------------------------------------------------------- #
# 2. atributos AsciiDoc
# --------------------------------------------------------------------------- #
def atributos(dir_adoc: Path, props: dict[str, str], tag: str) -> dict[str, str]:
    attrs: dict[str, str] = {}
    for fichero in ("_attributes.adoc", "_attributes-local.adoc"):
        ruta = dir_adoc / fichero
        if not ruta.exists():
            continue
        for linea in ruta.read_text(encoding="utf-8").splitlines():
            m = re.match(r"^:([\w!-]+?):\s*(.*)$", linea)
            if m:
                attrs[m.group(1)] = m.group(2).strip()

    for k, v in list(attrs.items()):
        attrs[k] = re.sub(r"\$\{([\w.\-]+)\}", lambda m: props.get(m.group(1), m.group(0)), v)

    attrs["quarkus-version"] = tag
    attrs["project-name"] = "Quarkus"
    attrs["quarkus-home-url"] = "https://quarkus.io"
    attrs["quarkus-base-url"] = "https://github.com/quarkusio/quarkus"
    attrs["quarkus-blob-url"] = f"https://github.com/quarkusio/quarkus/blob/{tag}"
    attrs["quarkus-tree-url"] = f"https://github.com/quarkusio/quarkus/tree/{tag}"
    attrs["quarkus-clone-url"] = "https://github.com/quarkusio/quarkus.git"
    attrs["quarkus-archive-url"] = "https://github.com/quarkusio/quarkus/archive/main.zip"
    attrs["imagesdir"] = "images"
    # atributos que el sitio quarkus.io define fuera del repositorio de codigo
    attrs.setdefault("quarkusio-guides", "https://quarkus.io/guides")
    attrs["quarkusio-guides"] = "https://quarkus.io/guides"
    attrs["Thread"] = ("https://docs.oracle.com/en/java/javase/21/docs/api/"
                       "java.base/java/lang/Thread.html")
    return attrs


def cabecera_atributos(attrs: dict[str, str]) -> list[str]:
    """Lineas ':nombre: valor' listas para inyectar en la cabecera del documento."""
    salida = []
    for k, v in attrs.items():
        if k in {"toc", "generated-dir", "includes", "doc-examples"}:
            continue
        if "${" in v:  # propiedad Maven no resuelta: mejor omitirla
            continue
        salida.append(f":{k}: {v}" if v else f":{k}:")
    return salida


# --------------------------------------------------------------------------- #
# 3. resolucion de include::
# --------------------------------------------------------------------------- #
RE_INCLUDE = re.compile(r"^include::([^\[\]]+)\[(.*)\]\s*$")


def sanear_adoc(texto: str) -> str:
    """Corrige erratas puntuales del AsciiDoc original que rompen la conversion
    (por ejemplo delimitadores de bloque escritos como `----]`)."""
    return re.sub(r"^-{4,}\]\s*$", "----", texto, flags=re.M)


def extraer_tags(texto: str, tags: list[str]) -> str:
    """Devuelve solo las regiones marcadas con // tag::nombre[] ... // end::nombre[]"""
    fuera = []
    activos: list[str] = []
    for linea in texto.splitlines():
        m_ini = re.search(r"(?://|#|/\*)\s*tag::([\w.-]+)\[\]", linea)
        m_fin = re.search(r"(?://|#|/\*)\s*end::([\w.-]+)\[\]", linea)
        if m_ini:
            if m_ini.group(1) in tags:
                activos.append(m_ini.group(1))
            continue
        if m_fin:
            if m_fin.group(1) in activos:
                activos.remove(m_fin.group(1))
            continue
        if activos:
            fuera.append(linea)
    return "\n".join(fuera)


def resolver_includes(texto: str, dir_adoc: Path, attrs: dict[str, str],
                      lineas_attrs: list[str], profundidad: int = 0,
                      attrs_inyectados: list[bool] | None = None) -> str:
    if attrs_inyectados is None:
        attrs_inyectados = [False]
    if profundidad > 6:
        return texto

    salida: list[str] = []
    for linea in texto.splitlines():
        m = RE_INCLUDE.match(linea)
        if not m:
            salida.append(linea)
            continue

        destino, opciones = m.group(1).strip(), m.group(2)

        if destino.endswith("_attributes.adoc"):
            if not attrs_inyectados[0]:
                salida.extend(lineas_attrs)
                attrs_inyectados[0] = True
            continue

        if "{generated-dir}" in destino:
            nombre = Path(destino).stem
            salida.append("")
            salida.append(
                "NOTE: La tabla de configuracion generada `%s` se produce al construir "
                "la documentacion y no existe en el codigo fuente. Consulta la referencia "
                "de configuracion en https://quarkus.io/guides/all-config" % nombre
            )
            salida.append("")
            continue

        ruta = destino
        for clave, valor in (("{includes}", "_includes"), ("{doc-examples}", "_examples")):
            ruta = ruta.replace(clave, valor)
        ruta = re.sub(r"\{([\w-]+)\}", lambda mm: attrs.get(mm.group(1), mm.group(0)), ruta)
        ruta_fs = (dir_adoc / ruta).resolve()

        if not ruta_fs.exists():
            salida.append(f"// [omitido] include no disponible: {destino}")
            continue

        contenido = ruta_fs.read_text(encoding="utf-8", errors="replace")

        m_tags = re.search(r"tags?=([^,\]]+)", opciones)
        if m_tags:
            tags = [t.strip().lstrip("!") for t in m_tags.group(1).split(";") if t.strip() not in ("*", "**")]
            if tags:
                contenido = extraer_tags(contenido, tags)

        if ruta_fs.suffix == ".adoc":
            contenido = resolver_includes(contenido, ruta_fs.parent, attrs, lineas_attrs,
                                          profundidad + 1, attrs_inyectados)
        else:  # ejemplo de codigo incrustado
            lenguaje = {".java": "java", ".xml": "xml", ".properties": "properties",
                        ".yaml": "yaml", ".yml": "yaml", ".json": "json",
                        ".proto": "proto", ".sql": "sql", ".kt": "kotlin"}.get(ruta_fs.suffix, "")
            contenido = f"[source,{lenguaje}]\n----\n{contenido.rstrip()}\n----"

        salida.append(contenido)

    return "\n".join(salida)


# --------------------------------------------------------------------------- #
# 4. post-proceso del Markdown
# --------------------------------------------------------------------------- #
RE_XREF = re.compile(r"\((?:\./)?([a-z0-9][a-z0-9._-]*)\.adoc(#[^)\s]*)?\)")
RE_IMG = re.compile(r"\]\((?:\./)?images/([^)\s]+)\)")


RE_IFEVAL = re.compile(r'^ifeval::\[\s*"([^"]*)"\s*(==|!=)\s*"([^"]*)"\s*\]\s*$')
RE_IFDEF = re.compile(r"^if(n?def)::[^\[]*\[\s*\]\s*$")
RE_ENDIF = re.compile(r"^endif::[^\[]*\[\s*\]\s*$")


def resolver_condicionales(md: str) -> str:
    """downdoc deja pasar algunos ifeval/ifdef. Los evaluamos aqui: los ifeval
    con operandos ya sustituidos se resuelven de verdad; para ifdef/ifndef, que no
    podemos evaluar sin el contexto completo, conservamos el cuerpo y quitamos la
    directiva (preferimos no perder contenido)."""
    salida: list[str] = []
    pila: list[bool] = []
    for linea in md.splitlines():
        desnuda = linea.strip()
        m = RE_IFEVAL.match(desnuda)
        if m:
            izq, op, der = m.groups()
            pila.append(izq == der if op == "==" else izq != der)
            continue
        if RE_IFDEF.match(desnuda):
            pila.append(True)
            continue
        if RE_ENDIF.match(desnuda):
            if pila:
                pila.pop()
            continue
        if all(pila):
            salida.append(linea)
    return "\n".join(salida)


def sustituir_atributos(md: str, attrs: dict[str, str]) -> str:
    """Sustituye los {atributos} conocidos que downdoc no alcanzo (tablas, URLs).
    Solo se tocan claves definidas en _attributes.adoc, nunca placeholders de
    ejemplos como {name} o {price}."""
    def repl(m: re.Match) -> str:
        valor = attrs.get(m.group(1))
        return valor if valor and "${" not in valor else m.group(0)
    return re.sub(r"\{([A-Za-z][A-Za-z0-9-]{2,})\}", repl, md)


def limpiar(md: str) -> str:
    # atributos de enlace AsciiDoc (window="_blank", role=...) que acaban en el texto
    md = re.sub(r"\[([^\]]*?),\s*(?:window|role|opts|title)=\"[^\"]*\"\]", r"[\1]", md)
    md = re.sub(r"\n{3,}", "\n\n", md)
    return md


def enlazar(md: str, doc_actual: str, mapa: dict[str, str]) -> str:
    cat_actual = mapa[doc_actual]

    def repl(m: re.Match) -> str:
        objetivo, ancla = m.group(1), m.group(2) or ""
        if objetivo in mapa:
            cat = mapa[objetivo]
            rel = f"{objetivo}.md" if cat == cat_actual else f"../{cat}/{objetivo}.md"
            return f"({rel}{ancla})"
        return f"({GUIA_URL.format(objetivo)}{ancla})"

    md = RE_XREF.sub(repl, md)

    def repl_ancla(m: re.Match) -> str:
        """xref a otra guia que downdoc dejo sin extension: `otra-guia#seccion`."""
        objetivo, ancla = m.group(1), m.group(2)
        if objetivo not in mapa:
            return m.group(0)
        cat = mapa[objetivo]
        rel = f"{objetivo}.md" if cat == cat_actual else f"../{cat}/{objetivo}.md"
        return f"({rel}#{ancla})"

    md = re.sub(r"\((?:\./)?([a-z0-9][a-z0-9._-]*)#([^)\s]+)\)", repl_ancla, md)
    md = re.sub(r"\(\+\+(https?://[^)\s]+?)\+\+\)", r"(\1)", md)          # passthrough AsciiDoc
    md = re.sub(r"\](\(/[a-z0-9][^)\s]*\))",
                lambda m: "](https://quarkus.io" + m.group(1)[1:], md)      # rutas del sitio
    md = re.sub(r"\]\((?!https?://|#|\.\./|mailto:)([a-z0-9][a-z0-9._-]*\.(?:py|sh|zip|jar|yaml|yml|json))\)",
                r"](https://quarkus.io/guides/\1)", md)                    # adjuntos del sitio
    return md


def postprocesar(md: str, doc: str, mapa: dict[str, str], tag: str,
                 fecha: str, imagenes: set[str], attrs: dict[str, str]) -> str:
    md = resolver_condicionales(md)
    md = sustituir_atributos(md, attrs)
    md = limpiar(md)
    md = enlazar(md, doc, mapa)

    for nombre in RE_IMG.findall(md):
        imagenes.add(nombre)
    md = RE_IMG.sub(lambda m: f"](../_assets/{m.group(1)})", md)

    lineas = md.splitlines()
    titulo = lineas[0] if lineas and lineas[0].startswith("# ") else f"# {doc}"
    cuerpo = "\n".join(lineas[1:] if lineas and lineas[0].startswith("# ") else lineas)

    cabecera = (
        f"{titulo}\n\n"
        f"> **Guia oficial:** <{GUIA_URL.format(doc)}>  \n"
        f"> **Fuente:** `docs/src/main/asciidoc/{doc}.adoc` en "
        f"[quarkusio/quarkus@{tag}](https://github.com/quarkusio/quarkus/blob/{tag}/docs/src/main/asciidoc/{doc}.adoc)  \n"
        f"> **Version documentada:** Quarkus {tag} · **Sincronizado:** {fecha} · "
        f"**Licencia:** Apache-2.0\n"
    )
    return cabecera + cuerpo.rstrip() + "\n"


def primer_parrafo(md: str) -> str:
    cuerpo = md.split("\n", 1)[1] if "\n" in md else ""
    cuerpo = re.sub(r"^>.*$", "", cuerpo, flags=re.M)
    for parrafo in re.split(r"\n\s*\n", cuerpo):
        p = parrafo.strip()
        if not p or p.startswith(("#", ">", "|", "```", "*", "-", "!", "<")):
            continue
        p = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", p)
        p = re.sub(r"[*_`]", "", p).replace("\n", " ").strip()
        if len(p) > 20:
            return (p[:200] + "…") if len(p) > 200 else p
    return ""


# --------------------------------------------------------------------------- #
# main
# --------------------------------------------------------------------------- #
def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", default=None, help="tag de quarkusio/quarkus (por defecto: ultimo release)")
    ap.add_argument("--keep", action="store_true", help="conservar directorio .build")
    args = ap.parse_args()

    tag = args.tag or ultimo_tag()
    fecha = dt.date.today().isoformat()
    log(f"version objetivo: Quarkus {tag} (snapshot {fecha})")

    src = clonar(tag)
    dir_adoc = src / "docs" / "src" / "main" / "asciidoc"
    props = propiedades_maven(tag)
    attrs = atributos(dir_adoc, props, tag)
    lineas_attrs = cabecera_atributos(attrs)
    mapa = mapa_docs()

    pre = DIR_TRABAJO / "pre"
    conv = DIR_TRABAJO / "md"
    for d in (pre, conv):
        shutil.rmtree(d, ignore_errors=True)
        d.mkdir(parents=True, exist_ok=True)

    faltantes = []
    for doc in mapa:
        origen = dir_adoc / f"{doc}.adoc"
        if not origen.exists():
            faltantes.append(doc)
            continue
        texto = sanear_adoc(origen.read_text(encoding="utf-8", errors="replace"))
        (pre / f"{doc}.adoc").write_text(
            resolver_includes(texto, dir_adoc, attrs, lineas_attrs), encoding="utf-8")

    if faltantes:
        log(f"aviso: {len(faltantes)} guias del catalogo no existen en {tag}: {', '.join(faltantes)}")

    log(f"convirtiendo {len(mapa) - len(faltantes)} guias con downdoc")
    subprocess.run(["node", str(RAIZ / "scripts" / "convert.js"), str(pre), str(conv)], check=True)

    for slug, _titulo, _docs in CATEGORIAS:
        (DIR_DOCS / slug).mkdir(parents=True, exist_ok=True)
    DIR_ASSETS.mkdir(parents=True, exist_ok=True)

    imagenes: set[str] = set()
    resumenes: dict[str, str] = {}
    generados = 0
    for doc, cat in mapa.items():
        origen = conv / f"{doc}.md"
        if not origen.exists():
            continue
        md = postprocesar(origen.read_text(encoding="utf-8"), doc, mapa, tag, fecha,
                          imagenes, attrs)
        (DIR_DOCS / cat / f"{doc}.md").write_text(md, encoding="utf-8")
        resumenes[doc] = primer_parrafo(md)
        generados += 1

    copiadas = 0
    for nombre in imagenes:
        candidato = dir_adoc / "images" / nombre
        if candidato.exists():
            destino = DIR_ASSETS / nombre
            destino.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(candidato, destino)
            copiadas += 1
    log(f"{generados} ficheros Markdown, {copiadas} imagenes copiadas")

    generar_indices(tag, fecha, resumenes, faltantes)

    if not args.keep:
        shutil.rmtree(DIR_TRABAJO / "pre", ignore_errors=True)
        shutil.rmtree(DIR_TRABAJO / "md", ignore_errors=True)

    (RAIZ / "SNAPSHOT.json").write_text(json.dumps({
        "quarkus_tag": tag,
        "fecha_sincronizacion": fecha,
        "guias_generadas": generados,
        "guias_no_encontradas": faltantes,
        "fuente": "https://github.com/quarkusio/quarkus",
        "licencia_fuente": "Apache-2.0",
    }, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    log("listo")
    return 0


def generar_indices(tag: str, fecha: str, resumenes: dict[str, str], faltantes: list[str]) -> None:
    lineas = [
        "# Indice de la documentacion oficial",
        "",
        f"Documentacion oficial de Quarkus **{tag}**, sincronizada el **{fecha}**, "
        "convertida a Markdown desde el AsciiDoc original (Apache-2.0).",
        "",
        "Las guias escritas para este repositorio (en espanol) estan en "
        "[`00-guias-propias/`](00-guias-propias/README.md): ruta de aprendizaje, modelo de "
        "ejecucion, chuleta de Mutiny, mejores practicas, antipatrones, matriz de extensiones, "
        "checklist de produccion y glosario.",
        "",
        "La documentacion oficial de **Mutiny** (la API `Uni`/`Multi` que usa Quarkus) esta en "
        "[`11-mutiny/`](11-mutiny/README.md).",
        "",
    ]
    for slug, titulo, docs in CATEGORIAS:
        presentes = [d for d in docs if (DIR_DOCS / slug / f"{d}.md").exists()]
        if not presentes:
            continue
        lineas += [f"## {titulo}", "", "| Guia | De que trata |", "| --- | --- |"]
        for d in presentes:
            desc = resumenes.get(d, "").replace("|", "\\|")
            lineas.append(f"| [{d}]({slug}/{d}.md) | {desc} |")
        lineas.append("")

        cat_lineas = [f"# {titulo}", "",
                      f"Quarkus {tag} · sincronizado {fecha} · [volver al indice](../00-INDICE.md)", ""]
        for d in presentes:
            cat_lineas.append(f"- [{d}]({d}.md) — {resumenes.get(d, '')}")
        cat_lineas.append("")
        (DIR_DOCS / slug / "README.md").write_text("\n".join(cat_lineas), encoding="utf-8")

    if faltantes:
        lineas += ["## No disponibles en esta version", "",
                   "Estas guias del catalogo no existen en el tag sincronizado: "
                   + ", ".join(f"`{f}`" for f in faltantes), ""]
    (DIR_DOCS / "00-INDICE.md").write_text("\n".join(lineas), encoding="utf-8")


if __name__ == "__main__":
    sys.exit(main())
