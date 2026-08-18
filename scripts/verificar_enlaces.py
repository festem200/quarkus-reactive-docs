#!/usr/bin/env python3
"""Comprueba que los enlaces internos entre ficheros Markdown del repositorio existen.

Uso: python3 scripts/verificar_enlaces.py
Salida: lista de enlaces rotos y codigo 1 si hay alguno.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
RE_ENLACE = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")


def main() -> int:
    rotos: list[str] = []
    total = 0
    for md in sorted(RAIZ.rglob("*.md")):
        if ".build" in md.parts or "node_modules" in md.parts:
            continue
        for destino in RE_ENLACE.findall(md.read_text(encoding="utf-8", errors="replace")):
            if destino.startswith(("http://", "https://", "#", "mailto:")):
                continue
            total += 1
            ruta = (md.parent / destino.split("#")[0]).resolve()
            if not ruta.exists():
                rotos.append(f"{md.relative_to(RAIZ)} -> {destino}")

    print(f"enlaces internos comprobados: {total}")
    if rotos:
        print(f"ROTOS: {len(rotos)}")
        for r in rotos[:80]:
            print("  ", r)
        return 1
    print("sin enlaces internos rotos")
    return 0


if __name__ == "__main__":
    sys.exit(main())
