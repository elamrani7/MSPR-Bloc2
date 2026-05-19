#!/usr/bin/env bash

set -euo pipefail

VENV_DIR=".venv"

if ! command -v python3.11 >/dev/null 2>&1; then
  echo "MISSING python3.11: please install Python 3.11 before running this script."
  exit 1
fi

if [ ! -d "$VENV_DIR" ]; then
  echo "Creating Python virtual environment in $VENV_DIR..."
  python3.11 -m venv "$VENV_DIR"
fi

echo "Installing Python dependencies..."
# shellcheck disable=SC1091
source "$VENV_DIR/bin/activate"
pip install --upgrade pip
pip install -r requirements.txt

echo "Python dependencies installed in $VENV_DIR."
