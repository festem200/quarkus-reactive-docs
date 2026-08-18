#!/usr/bin/env python3
"""Espeja la documentacion oficial de SmallRye Mutiny (la API reactiva que usa
Quarkus) dentro de este repositorio.

La fuente ya esta en Markdown (mkdocs), asi que el trabajo consiste en:
  - resolver la macro {{ insert('java/...', 'tag') }} incrustando el codigo real,
  - resolver las variables {{ attributes.* }},
  - convertir las admoniciones de Material (!!! note) a Markdown estandar,
  - reescribir enlaces y rutas para la estructura de este repositorio.

Uso: python3 scripts/build_mutiny.py [--tag 3.3.0]
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import shutil
import subprocess
import sys
import urllib.request
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
DESTINO = RAIZ / "docs" / "11-mutiny"
TRABAJO = RAIZ / ".build" / "mutiny-src"
REPO = "https://github.com/smallrye/smallrye-mutiny.git"
SITIO = "https://smallrye.io/smallrye-mutiny/latest/{}"

SECCIONES = [
    ("tutoriales", "Tutoriales", "tutorials"),
    ("guias", "Guias", "guides"),
    ("referencia", "Referencia", "reference"),
]


def log(msg: str) -> None:
    print(f"[mutiny] {msg}", flush=True)


def sh(cmd: list[str], cwd: Path | None = None) -> str:
    res = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if res.returncode != 0:
        raise RuntimeError(f"fallo {' '.join(cmd)}\n{res.stderr[-2000:]}")
    return res.stdout


def ultimo_tag() -> str:
    url = "https://api.github.com/repos/smallrye/smallrye-mutiny/releases/latest"
    with urllib.request.urlopen(url, timeout=30) as r:
        return json.load(r)["tag_name"]


def clonar(tag: str) -> Path:
    if (TRABAJO / ".git").exists():
        actual = sh(["git", "-C", str(TRABAJO), "describe", "--tags", "--always"]).strip()
        if actual == tag:
            log(f"reutilizando clon existente en {tag}")
            return TRABAJO
        shutil.rmtree(TRABAJO)
    TRABAJO.parent.mkdir(parents=True, exist_ok=True)
    log(f"clonando smallrye/smallrye-mutiny @ {tag}")
    sh(["git", "clone", "--filter=blob:none", "--sparse", "--depth", "1",
        "--branch", tag, REPO, str(TRABAJO)])
    sh(["git", "sparse-checkout", "set", "documentation"], cwd=TRABAJO)
    return TRABAJO


# --------------------------------------------------------------------------- #
# macros de mkdocs
# --------------------------------------------------------------------------- #
RE_INSERT = re.compile(r"\{\{\s*insert\(\s*['\"]([^'\"]+)['\"]\s*(?:,\s*['\"]([^'\"]+)['\"]\s*)?\)\s*\}\}")
RE_IMAGEN = re.compile(r"!\[[^\]]*\]\(([^)\s]+)\)")
RE_ATTR = re.compile(r"\{\{\s*attributes(?:\.([\w.-]+)|\['([^']+)'\])\s*\}\}")


def leer_region(ruta: Path, tag: str | None) -> str:
    texto = ruta.read_text(encoding="utf-8", errors="replace")
    if not tag:
        return texto.rstrip()
    m = re.search(rf"//\s*<{re.escape(tag)}>(.*?)//\s*</{re.escape(tag)}>", texto, re.S)
    if not m:
        return f"// [no se encontro la region '{tag}' en {ruta.name}]"
    lineas = [l for l in m.group(1).splitlines() if l.strip()]
    if not lineas:
        return ""
    sangria = min(len(l) - len(l.lstrip()) for l in lineas)
    return "\n".join(l[sangria:] if len(l) > sangria else l.lstrip()
                     for l in m.group(1).splitlines()).strip("\n")


def resolver_macros(md: str, dir_snippets: Path, atributos: dict) -> str:
    def repl_insert(m: re.Match) -> str:
        ruta = dir_snippets / m.group(1)
        if not ruta.exists():
            return f"// [snippet no disponible: {m.group(1)}]"
        return leer_region(ruta, m.group(2))

    def repl_attr(m: re.Match) -> str:
        clave = m.group(1) or m.group(2)
        valor = atributos
        for parte in clave.split("."):
            if isinstance(valor, dict) and parte in valor:
                valor = valor[parte]
            else:
                return m.group(0)
        return str(valor)

    md = RE_INSERT.sub(repl_insert, md)
    md = RE_ATTR.sub(repl_attr, md)
    return md


# --------------------------------------------------------------------------- #
# sintaxis especifica de Material for MkDocs
# --------------------------------------------------------------------------- #
ETIQUETAS = {"note": "📌 NOTA", "warning": "⚠️ AVISO", "tip": "💡 CONSEJO",
             "danger": "🚨 PELIGRO", "important": "❗ IMPORTANTE",
             "info": "ℹ️ INFO", "example": "🧪 EJEMPLO", "question": "❓ PREGUNTA",
             "success": "✅ OK", "abstract": "📄 RESUMEN", "quote": "❝ CITA",
             "bug": "🐞 BUG", "failure": "❌ FALLO"}


def convertir_admoniciones(md: str) -> str:
    """`!!! note "titulo"` + bloque indentado -> cita Markdown estandar."""
    salida: list[str] = []
    lineas = md.splitlines()
    i = 0
    while i < len(lineas):
        m = re.match(r'^(\s*)(?:!!!|\?\?\?\+?)\s+([\w-]+)\s*(?:"([^"]*)")?\s*$', lineas[i])
        if not m:
            salida.append(lineas[i])
            i += 1
            continue
        base, tipo, titulo = m.group(1), m.group(2).lower(), m.group(3)
        etiqueta = ETIQUETAS.get(tipo, tipo.upper())
        salida.append(f"{base}> **{titulo or etiqueta}**")
        salida.append(f"{base}>")
        i += 1
        while i < len(lineas):
            linea = lineas[i]
            if not linea.strip():
                # una linea en blanco solo corta el bloque si lo siguiente no va indentado
                siguiente = lineas[i + 1] if i + 1 < len(lineas) else ""
                if siguiente.strip() and not siguiente.startswith(base + "    "):
                    break
                salida.append(f"{base}>")
                i += 1
                continue
            if not linea.startswith(base + "    "):
                break
            salida.append(f"{base}> {linea[len(base) + 4:]}")
            i += 1
        salida.append("")
    return "\n".join(salida)


def limpiar(md: str, nombre: str, tag: str, fecha: str, ruta_rel: str) -> str:
    md = re.sub(r"\A---\n.*?\n---\n", "", md, flags=re.S)          # frontmatter de tags
    md = re.sub(r"```(\w+)\s+linenums=\"\d+\"", r"```\1", md)      # opciones de pymdownx
    md = re.sub(r"```(\w+)\s+hl_lines=\"[^\"]*\"", r"```\1", md)
    md = re.sub(r"\{\s*\.[\w-]+\s*\}", "", md)                     # attr_list
    md = convertir_admoniciones(md)
    md = re.sub(r"(?m)(^\s*>\s*$\n)+(?=^\s*>\s*$)", "", md)  # cierres de cita repetidos
    md = re.sub(r"\n{3,}", "\n\n", md)

    lineas = md.lstrip().splitlines()
    titulo = lineas[0] if lineas and lineas[0].startswith("# ") else f"# {nombre}"
    cuerpo = "\n".join(lineas[1:] if lineas and lineas[0].startswith("# ") else lineas)
    web = SITIO.format(ruta_rel.replace(".md", ""))
    cabecera = (
        f"{titulo}\n\n"
        f"> **Documentacion oficial:** <{web}>  \n"
        f"> **Fuente:** `documentation/docs/{ruta_rel}` en "
        f"[smallrye/smallrye-mutiny@{tag}](https://github.com/smallrye/smallrye-mutiny/blob/{tag}/documentation/docs/{ruta_rel})  \n"
        f"> **Version documentada:** Mutiny {tag} · **Sincronizado:** {fecha} · "
        f"**Licencia:** Apache-2.0\n"
    )
    return cabecera + cuerpo.rstrip() + "\n"


def reescribir_enlaces(md: str, seccion: str) -> str:
    """Los enlaces del sitio original son relativos al arbol docs/ de mkdocs."""
    mapa = {"tutorials": "tutoriales", "guides": "guias", "reference": "referencia"}

    def repl(m: re.Match) -> str:
        destino = m.group(1)
        if destino.startswith(("http", "#", "mailto:")):
            return m.group(0)
        limpio = destino.lstrip("./")
        for origen, nuevo in mapa.items():
            if limpio.startswith(origen + "/"):
                resto = limpio[len(origen) + 1:]
                prefijo = "" if nuevo == seccion else f"../{nuevo}/"
                return f"]({prefijo}{resto})"
        if limpio in ("index.md", "../index.md"):
            return "](../README.md)"
        return m.group(0)

    return re.sub(r"\]\(([^)\s]+)\)", repl, md)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", default=None)
    args = ap.parse_args()

    tag = args.tag or ultimo_tag()
    fecha = dt.date.today().isoformat()
    log(f"version objetivo: Mutiny {tag} (snapshot {fecha})")

    src = clonar(tag) / "documentation"
    dir_docs = src / "docs"
    dir_snippets = src / "src" / "test"

    atributos: dict = {}
    fichero_attrs = src / "attributes.yaml"
    if fichero_attrs.exists():
        texto = fichero_attrs.read_text(encoding="utf-8")
        try:
            import yaml  # opcional
            atributos = yaml.safe_load(texto) or {}
        except ImportError:  # fallback sin dependencias: pares clave/valor planos
            atributos = {"attributes": dict(re.findall(r"^\s*([\w.-]+):\s*['\"]?([^'\"\n]+)['\"]?$",
                                                       texto, re.M))}
        atributos = atributos.get("attributes", atributos)

    shutil.rmtree(DESTINO, ignore_errors=True)
    indice = [f"# Mutiny {tag} — documentacion oficial",
              "",
              f"Espejo en Markdown de la documentacion de [SmallRye Mutiny]({SITIO.format('')}), "
              "la biblioteca de programacion reactiva que Quarkus usa como API principal "
              f"(`Uni` / `Multi`). Sincronizado el {fecha} desde el tag `{tag}`.",
              "",
              "[Volver al indice general](../00-INDICE.md)",
              ""]

    total = 0
    for slug, titulo, carpeta in SECCIONES:
        origen = dir_docs / carpeta
        if not origen.exists():
            continue
        (DESTINO / slug).mkdir(parents=True, exist_ok=True)
        indice += [f"## {titulo}", ""]
        for fichero in sorted(origen.glob("*.md")):
            ruta_rel = f"{carpeta}/{fichero.name}"
            md = fichero.read_text(encoding="utf-8", errors="replace")
            md = resolver_macros(md, dir_snippets, atributos)
            md = reescribir_enlaces(md, slug)
            md = limpiar(md, fichero.stem, tag, fecha, ruta_rel)
            (DESTINO / slug / fichero.name).write_text(md, encoding="utf-8")
            for imagen in RE_IMAGEN.findall(md):
                if imagen.startswith(("http", "..", "/")):
                    continue
                fuente_img = origen / imagen
                if fuente_img.exists():
                    shutil.copy2(fuente_img, DESTINO / slug / fuente_img.name)
            primera = next((l for l in md.splitlines() if l.startswith("# ")), fichero.stem)
            indice.append(f"- [{primera[2:]}]({slug}/{fichero.name})")
            total += 1
        indice.append("")

    indice += ["## Licencia y atribucion", "",
               "Contenido original de SmallRye Mutiny, distribuido bajo licencia Apache-2.0. "
               "Este directorio es una copia derivada (conversion de formato) para consulta offline; "
               "la version autoritativa es la del sitio oficial.", ""]
    (DESTINO / "README.md").write_text("\n".join(indice), encoding="utf-8")
    log(f"{total} documentos de Mutiny generados en docs/11-mutiny/")

    instantanea = RAIZ / "SNAPSHOT.json"
    datos = json.loads(instantanea.read_text()) if instantanea.exists() else {}
    datos["mutiny_tag"] = tag
    datos["mutiny_documentos"] = total
    datos["mutiny_fecha_sincronizacion"] = fecha
    instantanea.write_text(json.dumps(datos, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
