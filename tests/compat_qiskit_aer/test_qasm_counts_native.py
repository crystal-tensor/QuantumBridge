# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit Aer was copied.

from quantumbridge.compat.qiskit_aer import run_qasm_simulator_native
from quantumbridge.core import Circuit
from quantumbridge.schema.aer_results import QasmSimulationResult


def test_qasm_counts_native_seeded_bell_sampling():
    circuit = Circuit(2, 2)
    circuit.h(0).cx(0, 1).measure(0, 0).measure(1, 1)

    first = run_qasm_simulator_native(circuit, shots=64, seed=11)
    second = run_qasm_simulator_native(circuit, shots=64, seed=11)

    assert isinstance(first, QasmSimulationResult)
    assert first.counts == second.counts
    assert sum(first.counts.values()) == 64
    assert set(first.counts) <= {"00", "11"}
    assert first.shots == 64
    assert first.seed == 11


def test_qasm_counts_native_unmeasured_uses_all_qubits():
    circuit = Circuit(1)
    circuit.x(0)

    result = run_qasm_simulator_native(circuit, shots=8, seed=5)

    assert result.counts == {"1": 8}
