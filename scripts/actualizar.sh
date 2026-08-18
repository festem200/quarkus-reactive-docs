#!/usr/bin/env bash
# Re-sincroniza todo el repositorio con la ultima version publicada de Quarkus y Mutiny.
#
#   ./scripts/actualizar.sh              # ultimas versiones estables
#   ./scripts/actualizar.sh 3.33.2 3.3.0 # versiones concretas (Quarkus, Mutiny)
set -euo pipefail

cd "$(dirname "$0")/.."

QUARKUS_TAG="${1:-}"
MUTINY_TAG="${2:-}"

echo "==> Instalando dependencias de conversion (downdoc)"
npm --prefix ./scripts install --no-audit --no-fund

echo "==> Sincronizando guias de Quarkus"
if [ -n "$QUARKUS_TAG" ]; then
  python3 scripts/build_docs.py --tag "$QUARKUS_TAG"
else
  python3 scripts/build_docs.py
fi

echo "==> Sincronizando documentacion de Mutiny"
if [ -n "$MUTINY_TAG" ]; then
  python3 scripts/build_mutiny.py --tag "$MUTINY_TAG"
else
  python3 scripts/build_mutiny.py
fi

echo "==> Verificando enlaces internos"
python3 scripts/verificar_enlaces.py

echo "==> Listo. Revisa git diff y haz commit del snapshot."
