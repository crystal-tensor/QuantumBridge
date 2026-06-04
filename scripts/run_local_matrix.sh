#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

PYTHON_BIN="${PYTHON:-python3}"
PYTEST_BIN="${PYTEST:-pytest}"

section() {
  printf '\n== %s ==\n' "$1"
}

has_module() {
  "$PYTHON_BIN" - "$1" <<'PY'
import importlib.util
import sys

sys.exit(0 if importlib.util.find_spec(sys.argv[1]) is not None else 1)
PY
}

section "core-only"
"$PYTEST_BIN" -q -rs

section "qiskit-extra"
if has_module qiskit; then
  "$PYTEST_BIN" -q -rs \
    tests/compat/test_qiskit_adapter_realistic.py \
    tests/compat/test_qiskit_import_basic_circuit.py \
    tests/compat/test_qiskit_export_basic_circuit.py \
    tests/compat/test_qiskit_roundtrip_ir.py
else
  echo "qiskit unavailable; adapter subset not executed."
fi

section "pennylane-extra"
if has_module pennylane; then
  "$PYTEST_BIN" -q -rs \
    tests/compat/test_pennylane_adapter_realistic.py \
    tests/compat/test_pennylane_installed_environment.py \
    tests/qml/test_pennylane_observable_bridge.py \
    tests/qml/test_pennylane_qnode_basic.py
else
  echo "pennylane unavailable; adapter subset not executed."
fi

section "dev"
"$PYTEST_BIN" -q -rs
if "$PYTEST_BIN" --help | grep -q -- '--cov'; then
  "$PYTEST_BIN" --cov=quantumbridge
else
  echo "pytest-cov unavailable; coverage not executed."
fi
