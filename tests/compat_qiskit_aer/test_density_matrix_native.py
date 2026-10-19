# Independent QuantumBridge tests. Installed Qiskit/Aer is a test oracle only.

import json

import numpy as np
import pytest

from quantumbridge import Circuit, DensityMatrixDevice
from quantumbridge.compat.qiskit_adapter import circuit_from_qiskit, circuit_to_qiskit
from quantumbridge.compat.qiskit_aer import execute_basic_circuit_native, run_density_matrix_simulator_native
from quantumbridge.noise import AmplitudeDampingChannel
from quantumbridge.schema import DensityMatrixSimulationResult


def test_native_density_aer_result_serializes_and_runs_above_four_qubits():
    circuit = Circuit(5).h(0).t(0).rx(.2, 3).channel(AmplitudeDampingChannel(.3), [0])
    result = run_density_matrix_simulator_native(circuit, shots=20, seed=5, memory=True)
    assert result.backend == "density_matrix"
    assert sum(result.counts.values()) == 20
    assert len(result.metadata["memory"]) == 20
    assert len(result.final_density_matrix) == 32
    restored = DensityMatrixSimulationResult.from_dict(json.loads(result.to_json()))
    np.testing.assert_allclose(restored.final_density_matrix, result.final_density_matrix)
    assert execute_basic_circuit_native(circuit, backend="density_matrix", shots=4).counts


@pytest.mark.parametrize("width,wires", [(1, [0]), (2, [1, 0]), (3, [2, 0])])
def test_native_multiwire_kraus_matches_qiskit_quantum_info(width, wires):
    qi = pytest.importorskip("qiskit.quantum_info")
    reference_channel = qi.Kraus(qi.random_quantum_channel(1 << len(wires), rank=3, seed=width))
    initial = qi.random_density_matrix(1 << width, seed=10 + width).data
    native = Circuit(width).kraus(reference_channel.data, wires)
    actual = DensityMatrixDevice(initial_state=initial).density_matrix(native)
    qargs = [width - 1 - wire for wire in reversed(wires)]
    expected = qi.DensityMatrix(initial).evolve(reference_channel, qargs=qargs).data
    np.testing.assert_allclose(actual, expected, atol=1e-12)


def test_qiskit_unitary_kraus_import_export_preserves_local_order():
    qiskit = pytest.importorskip("qiskit")
    qi = pytest.importorskip("qiskit.quantum_info")
    reference = qiskit.QuantumCircuit(3)
    reference.h(0)
    reference.t(1)
    reference.unitary(qi.random_unitary(4, seed=17), [2, 0])
    reference.append(qi.Kraus(qi.random_quantum_channel(4, rank=3, seed=18)).to_instruction(), [1, 2])
    native = circuit_from_qiskit(reference)
    exported = circuit_to_qiskit(native)
    expected = qi.DensityMatrix.from_instruction(reference).data
    permutation = [int(format(index, "03b")[::-1], 2) for index in range(8)]
    np.testing.assert_allclose(DensityMatrixDevice().density_matrix(native), expected[np.ix_(permutation, permutation)], atol=1e-12)
    np.testing.assert_allclose(qi.DensityMatrix.from_instruction(exported).data, expected, atol=1e-12)


def test_native_dynamic_nonclifford_density_and_counts_match_aer():
    qiskit = pytest.importorskip("qiskit")
    qi = pytest.importorskip("qiskit.quantum_info")
    aer = pytest.importorskip("qiskit_aer")
    reference = qiskit.QuantumCircuit(2, 1)
    reference.ry(.7, 0)
    reference.cx(0, 1)
    reference.append(qi.Kraus(AmplitudeDampingChannel(.3).kraus()).to_instruction(), [1])
    reference.measure(0, 0)
    with reference.if_test((reference.clbits[0], 1)):
        reference.ry(.4, 1)
    reference.reset(0)
    native = circuit_from_qiskit(reference)
    reference.save_density_matrix()
    result = aer.AerSimulator(method="density_matrix").run(reference, shots=16000, seed_simulator=9).result()
    oracle = np.asarray(result.data(0)["density_matrix"])
    permutation = [0, 2, 1, 3]
    actual = DensityMatrixDevice().density_matrix(native)
    np.testing.assert_allclose(actual, oracle[np.ix_(permutation, permutation)], atol=.015)
    exact = DensityMatrixDevice().run(native).probabilities()
    counts = result.get_counts()
    for label, probability in exact.items():
        assert abs(counts.get(label[::-1], 0) / 16000 - probability) < .02
