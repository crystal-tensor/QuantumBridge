# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit Aer was copied.

import pytest

from quantumbridge.compat.qiskit_aer import (
    execute_basic_circuit_native,
    normalize_circuit_to_quantumbridge_ir,
)
from quantumbridge.core import Circuit


def test_execute_basic_circuit_native_dispatches_backends():
    circuit = Circuit(1, 1)
    circuit.x(0).measure(0, 0)

    state = execute_basic_circuit_native(circuit, backend="statevector")
    counts = execute_basic_circuit_native(circuit, backend="qasm", shots=8, seed=9)

    assert state.backend == "statevector"
    assert counts.backend == "qasm"
    assert counts.counts == {"1": 8}


def test_normalize_ir_dict_to_quantumbridge_circuit():
    payload = {
        "name": "dict_ir",
        "registers": {"quantum": {"size": 1}, "classical": {"size": 1}},
        "instructions": [{"op": "h", "targets": [0]}],
        "measurements": [{"wires": [0], "bits": [0]}],
    }

    circuit = normalize_circuit_to_quantumbridge_ir(payload)

    assert circuit.num_qubits == 1
    assert circuit.num_bits == 1
    assert len(circuit.operations) == 1
    assert len(circuit.measurements) == 1


def test_qiskit_quantum_circuit_input_if_installed():
    qiskit = pytest.importorskip("qiskit")
    circuit = qiskit.QuantumCircuit(1, 1)
    circuit.x(0)
    circuit.measure(0, 0)

    result = execute_basic_circuit_native(circuit, backend="qasm", shots=8, seed=10)

    assert result.counts == {"1": 8}
