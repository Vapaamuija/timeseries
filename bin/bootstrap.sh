#!/usr/bin/env bash

set -euo pipefail

# Usage: ./bin/bootstrap.sh [PYTHON_VERSION]
# Example: ./bin/bootstrap.sh 3.11.9

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_ROOT"

PY_VERSION="${1:-3.11.9}"
VENV_DIR="${PROJECT_ROOT}/.venv"

echo "==> Project: $(basename "$PROJECT_ROOT")"
echo "==> Using Python ${PY_VERSION} (pyenv)"

# Ensure pyenv exists
if ! command -v pyenv >/dev/null 2>&1; then
  echo "Error: pyenv not found in PATH. Install pyenv first: https://github.com/pyenv/pyenv" >&2
  exit 1
fi

# Install Python via pyenv if missing
if ! pyenv versions --bare | grep -qx "${PY_VERSION}"; then
  echo "==> Installing Python ${PY_VERSION} via pyenv..."
  pyenv install -s "${PY_VERSION}"
fi

echo "==> Setting local Python version"
pyenv local "${PY_VERSION}"

PY_BIN="$(pyenv which python)"
echo "==> Python binary: ${PY_BIN} ($(${PY_BIN} -V))"

echo "==> Creating virtualenv at ${VENV_DIR}"
"${PY_BIN}" -m venv "${VENV_DIR}"

echo "==> Activating virtualenv"
# shellcheck disable=SC1090
source "${VENV_DIR}/bin/activate"

echo "==> Upgrading pip/setuptools/wheel"
pip install -U pip setuptools wheel

echo "==> Installing project dependencies"
pip install -r requirements.txt

echo "==> Installing package in editable mode with dev extras"
pip install -e ".[dev]"

echo "==> Creating runtime directories"
mkdir -p output data/cache logs

echo "==> Verifying CLI"
if ./bin/wt --help >/dev/null 2>&1; then
  echo "✓ CLI available"
else
  echo "⚠ CLI check failed (ensure ./bin/wt is executable)"
fi

echo "\n✅ Bootstrap complete. Next steps:"
echo "  source .venv/bin/activate" 
echo "  make test"
echo "  ./bin/wt --help"


