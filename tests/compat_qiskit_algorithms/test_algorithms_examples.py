# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit Algorithms was copied.

import subprocess
import sys

from quantumbridge.compat.qiskit_algorithms import run_all_native_algorithm_examples


def test_algorithms_examples_execute():
    for path in (
        "examples/qiskit_algorithms_vqe_quantumbridge.py",
        "examples/qiskit_algorithms_qaoa_quantumbridge.py",
        "examples/qiskit_algorithms_grover_quantumbridge.py",
    ):
        completed = subprocess.run(
            [sys.executable, path],
            check=True,
            capture_output=True,
            text=True,
        )
        assert "QuantumBridge" in completed.stdout
        assert "Optional upstream" in completed.stdout


def test_native_algorithm_examples_aggregate_entrypoint():
    payload = run_all_native_algorithm_examples()
    assert set(payload) == {"vqe", "qaoa", "grover"}
    assert payload["vqe"]["algorithm"] == "VQE"
    assert payload["qaoa"]["algorithm"] == "QAOA"
    assert payload["grover"]["algorithm"] == "Grover"
