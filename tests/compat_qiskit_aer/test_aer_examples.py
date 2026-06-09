# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit Aer was copied.

import subprocess
import sys
from pathlib import Path

from quantumbridge.compat.qiskit_aer.examples import (
    run_noisy_counts_example,
    run_qasm_counts_example,
    run_statevector_example,
)


ROOT = Path(__file__).resolve().parents[2]


def test_aer_examples_helpers_return_native_and_upstream_results():
    for helper in (run_statevector_example, run_qasm_counts_example, run_noisy_counts_example):
        results = helper()
        assert set(results) == {"native", "upstream"}
        assert results["native"].production_ready is False
        assert results["native"].metadata["cloud_access"] is False


def test_aer_example_scripts_execute():
    scripts = [
        "examples/qiskit_aer_statevector_quantumbridge.py",
        "examples/qiskit_aer_qasm_counts_quantumbridge.py",
        "examples/qiskit_aer_noisy_counts_quantumbridge.py",
    ]
    for script in scripts:
        completed = subprocess.run(
            [sys.executable, str(ROOT / script)],
            cwd=ROOT,
            check=True,
            text=True,
            capture_output=True,
        )
        assert "QuantumBridge native Aer-style" in completed.stdout
        assert "production_simulator: False" in completed.stdout
