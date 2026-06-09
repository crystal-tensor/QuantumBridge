# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit, PennyLane, or PennyLane-Qiskit was copied.

import subprocess
import sys
from pathlib import Path

from quantumbridge.compat.pennylane_qiskit.examples import (
    run_bridge_equivalence_example,
    run_pennylane_to_qiskit_example,
    run_qiskit_to_pennylane_example,
)

ROOT = Path(__file__).resolve().parents[2]


def test_bridge_examples_return_native_and_optional_upstream_results():
    for helper in (
        run_qiskit_to_pennylane_example,
        run_pennylane_to_qiskit_example,
        run_bridge_equivalence_example,
    ):
        results = helper()
        assert set(results) == {"native", "upstream"}
        assert results["native"].validate() is True
        assert results["native"].production_ready is False


def test_bridge_example_scripts_execute():
    scripts = [
        "examples/pennylane_qiskit_qiskit_to_pennylane_quantumbridge.py",
        "examples/pennylane_qiskit_pennylane_to_qiskit_quantumbridge.py",
        "examples/pennylane_qiskit_bridge_equivalence_quantumbridge.py",
    ]
    for script in scripts:
        completed = subprocess.run(
            [sys.executable, str(ROOT / script)],
            cwd=ROOT,
            check=True,
            text=True,
            capture_output=True,
        )
        assert "QuantumBridge native PennyLane-Qiskit bridge" in completed.stdout
        assert "cloud_access: False" in completed.stdout
        assert "full_plugin_parity_claim: False" in completed.stdout
