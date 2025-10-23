#!/bin/bash

set -euo pipefail

echo "Setting up weather-tool development environment..."

# Ensure we're in project root
if [ ! -f "requirements.txt" ]; then
    echo "Error: Please run this script from the weather-tool project root"
    exit 1
fi

PROJECT_ROOT="$(pwd)"
VENV_DIR="${PROJECT_ROOT}/.venv"

# Optional: use pyenv if available and a version is pinned
if command -v pyenv >/dev/null 2>&1; then
    if [ -f .python-version ]; then
        PY_VERSION="$(cat .python-version | tr -d '\n')"
        if [ -n "${PY_VERSION}" ]; then
            echo "Using pyenv Python ${PY_VERSION}"
            if ! pyenv versions --bare | grep -qx "${PY_VERSION}"; then
                echo "Installing Python ${PY_VERSION} via pyenv..."
                pyenv install -s "${PY_VERSION}"
            fi
            pyenv local "${PY_VERSION}"
        fi
    fi
fi

# Create venv if missing and activate it
if [ ! -d "${VENV_DIR}" ]; then
    echo "Creating virtual environment at ${VENV_DIR}"
    PY_BIN="python3"
    if command -v pyenv >/dev/null 2>&1; then
        PY_BIN="$(pyenv which python)"
    fi
    "${PY_BIN}" -m venv "${VENV_DIR}"
fi

echo "Activating virtual environment"
# shellcheck disable=SC1090
source "${VENV_DIR}/bin/activate"

echo "Upgrading pip/setuptools/wheel"
pip install -U pip setuptools wheel

echo "Installing project dependencies (dev extras)"
pip install -r requirements.txt
pip install -e ".[dev]"

# Create necessary directories
echo "Creating directories..."
mkdir -p output
mkdir -p data/cache
mkdir -p logs

# Configure and verify SVG rendering stack (Cairo/cairocffi)
if [ -f "${PROJECT_ROOT}/setup_svg_rendering.sh" ]; then
    echo "Running SVG rendering setup..."
    bash "${PROJECT_ROOT}/setup_svg_rendering.sh" || {
        echo "Warning: SVG rendering setup reported an issue. You can re-run 'make svg-setup' later." >&2
    }
fi

# Test CLI access
echo "Testing CLI access..."
if ./bin/wt --help > /dev/null 2>&1; then
    echo "✓ CLI access working!"
else
    echo "✗ CLI access failed"
    exit 1
fi

echo ""
echo "✅ Development environment ready!"
echo ""
echo "Usage:"
echo "  source .venv/bin/activate           # Activate virtualenv"
echo "  ./bin/wt --help                     # Show help"
echo "  ./bin/wt plot ENGM --output test.png  # Test plot"
echo "  ./bin/wt search oslo                # Search airports"
echo ""
echo "SVG setup:"
echo "  make svg-setup                      # Configure Cairo + SVG rendering"
echo ""
echo "Short alias:"
echo "  ./bin/wt plot ENGM --style tseries  # T-series meteogram"
echo ""
echo "Happy developing! 🌤️"
