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

section "qiskit-aer-extra"
if has_module qiskit_aer; then
  "$PYTEST_BIN" -q -rs tests/compat_qiskit_aer
else
  echo "qiskit-aer unavailable; compatibility subset not executed."
fi

section "qiskit-finance-extra"
if has_module qiskit_finance; then
  "$PYTEST_BIN" -q -rs tests/compat_qiskit_finance
else
  echo "qiskit-finance unavailable; compatibility subset not executed."
fi

section "qiskit-optimization-extra"
if has_module qiskit_optimization; then
  "$PYTEST_BIN" -q -rs tests/compat_qiskit_optimization
else
  echo "qiskit-optimization unavailable; compatibility subset not executed."
fi

section "qiskit-machine-learning-extra"
if has_module qiskit_machine_learning; then
  "$PYTEST_BIN" -q -rs tests/compat_qiskit_machine_learning
else
  echo "qiskit-machine-learning unavailable; compatibility subset not executed."
fi

section "qiskit-nature-extra"
if has_module qiskit_nature; then
  "$PYTEST_BIN" -q -rs tests/compat_qiskit_nature
else
  echo "qiskit-nature unavailable; compatibility subset not executed."
fi

section "qiskit-algorithms-extra"
if has_module qiskit_algorithms; then
  "$PYTEST_BIN" -q -rs tests/compat_qiskit_algorithms
else
  echo "qiskit-algorithms unavailable; compatibility subset not executed."
fi

section "qiskit-dynamics-extra"
if has_module qiskit_dynamics; then
  "$PYTEST_BIN" -q -rs tests/compat_qiskit_dynamics
else
  echo "qiskit-dynamics unavailable; advisory compatibility subset not executed."
fi

section "qiskit-metal-extra"
if has_module qiskit_metal; then
  "$PYTEST_BIN" -q -rs tests/compat_qiskit_metal
else
  echo "qiskit-metal unavailable; advisory compatibility subset not executed."
fi

section "qiskit-runtime-extra"
if has_module qiskit_ibm_runtime; then
  "$PYTEST_BIN" -q -rs tests/compat_qiskit_runtime
else
  echo "qiskit-ibm-runtime unavailable; compatibility subset not executed."
fi

section "qiskit-experiments-extra"
if has_module qiskit_experiments; then
  "$PYTEST_BIN" -q -rs tests/compat_qiskit_experiments
else
  echo "qiskit-experiments unavailable; compatibility subset not executed."
fi

section "qiskit-addons-extra"
if has_module qiskit_addon_sqd || has_module qiskit_addon_mpf || has_module qiskit_addon_aqc_tensor || has_module qiskit_addon_obp; then
  "$PYTEST_BIN" -q -rs tests/compat_qiskit_addons
else
  echo "qiskit-addons unavailable; compatibility subset not executed."
fi

section "pennylane-full-extra"
if has_module pennylane; then
  "$PYTEST_BIN" -q -rs tests/compat_pennylane_full
else
  echo "pennylane unavailable; full compatibility subset not executed."
fi

section "mqt-compat"
"$PYTEST_BIN" -q -rs tests/compat_mqt

section "torchquantum-compat"
"$PYTEST_BIN" -q -rs tests/compat_torchquantum

section "ecosystem-inventory"
"$PYTHON_BIN" scripts/inventory_qiskit_core_api.py
"$PYTHON_BIN" scripts/inventory_qiskit_aer_api.py
"$PYTHON_BIN" scripts/inventory_qiskit_ibm_runtime_api.py
"$PYTHON_BIN" scripts/inventory_qiskit_finance_api.py
"$PYTHON_BIN" scripts/inventory_qiskit_optimization_api.py
"$PYTHON_BIN" scripts/inventory_qiskit_machine_learning_api.py
"$PYTHON_BIN" scripts/inventory_qiskit_experiments_api.py
"$PYTHON_BIN" scripts/inventory_qiskit_addons_api.py
"$PYTHON_BIN" scripts/inventory_qiskit_nature_api.py
"$PYTHON_BIN" scripts/inventory_qiskit_algorithms_api.py
"$PYTHON_BIN" scripts/inventory_qiskit_dynamics_api.py
"$PYTHON_BIN" scripts/inventory_qiskit_metal_api.py
"$PYTHON_BIN" scripts/inventory_pennylane_full_api.py
"$PYTEST_BIN" -q -rs tests/ecosystem

section "dev"
"$PYTEST_BIN" -q -rs
if "$PYTEST_BIN" --help | grep -q -- '--cov'; then
  "$PYTEST_BIN" --cov=quantumbridge
else
  echo "pytest-cov unavailable; coverage not executed."
fi

section "chemistry-core"
"$PYTEST_BIN" -q -rs \
  tests/chemistry/test_molecule.py \
  tests/chemistry/test_fermionic_op.py \
  tests/chemistry/test_jordan_wigner.py \
  tests/chemistry/test_qubit_hamiltonian.py \
  tests/chemistry/test_chemistry_result_schema.py

section "chemistry-extra"
if has_module qiskit_nature || has_module pyscf || has_module openfermion || has_module qiskit_algorithms; then
  "$PYTEST_BIN" -q -rs tests/chemistry tests/algorithms_compat tests/compat_inventory
else
  echo "chemistry optional dependencies unavailable; installed-environment adapter subsets not executed."
fi

section "qiskit-nature-p2-extra"
if has_module qiskit_nature; then
  "$PYTHON_BIN" scripts/inventory_qiskit_nature_api.py
  "$PYTEST_BIN" -q -rs \
    tests/chemistry/test_qiskit_nature_driver_optional.py \
    tests/chemistry/test_qiskit_nature_driver_installed.py \
    tests/chemistry/test_h2_installed_workflow.py \
    tests/compat_inventory/test_qiskit_nature_inventory_generated.py
else
  echo "qiskit_nature unavailable; qiskit-nature-p2 subset not executed."
fi

section "algorithms-extra"
if has_module qiskit_algorithms; then
  "$PYTHON_BIN" scripts/inventory_qiskit_algorithms_api.py
  "$PYTEST_BIN" -q -rs tests/algorithms_compat
else
  echo "qiskit_algorithms unavailable; algorithms-extra subset not executed."
fi

section "openfermion-extra"
if has_module openfermion; then
  "$PYTEST_BIN" -q -rs tests/chemistry/test_openfermion_adapter_installed.py
else
  echo "openfermion unavailable; openfermion-extra subset not executed."
fi
