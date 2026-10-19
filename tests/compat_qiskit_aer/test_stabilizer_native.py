# Independently implemented QuantumBridge tests; installed Aer is an oracle only.

import numpy as np
import pytest

from quantumbridge import Circuit, StabilizerDevice, transpile
from quantumbridge.compat.qiskit_adapter import circuit_from_qiskit, circuit_to_qiskit
from quantumbridge.compat.qiskit_aer import execute_basic_circuit_native, run_stabilizer_simulator_native
from quantumbridge.schema.aer_results import QasmSimulationResult


def test_native_aer_stabilizer_path_has_no_four_qubit_cap():
    circuit = Circuit(32).h(0)
    for wire in range(1, 32):
        circuit.cx(0, wire)
    circuit.measure_all()
    result = run_stabilizer_simulator_native(circuit, shots=10, seed=9, memory=True)
    assert result.backend == "stabilizer"
    assert result.native_implementation
    assert set(result.counts) <= {"0" * 32, "1" * 32}
    assert sum(result.counts.values()) == 10
    assert len(result.metadata["memory"]) == 10
    assert QasmSimulationResult.from_dict(result.to_dict()).counts == result.counts
    assert execute_basic_circuit_native(circuit.to_ir(), backend="stabilizer", shots=10, seed=9).counts == result.counts
    assert execute_basic_circuit_native(circuit.to_ir().to_dict(), backend="stabilizer", shots=10, seed=9).counts == result.counts


@pytest.mark.parametrize("level", [0, 1, 2, 3])
def test_dynamic_transpile_preserves_measurement_boundaries_and_branch_entry(level):
    device = StabilizerDevice()
    circuit = Circuit(1, 2).h(0).measure(0, 0).h(0).measure(0, 1)
    compiled = transpile(circuit, optimization_level=level)
    assert device.run(compiled).probabilities() == device.run(circuit).probabilities()
    branch = Circuit(1, 1).if_else((0, 0), Circuit(1, 1).x(0).measure(0, 0).sdg(0), Circuit(1, 1).x(0)).measure(0, 0)
    compiled_branch = transpile(branch, optimization_level=level, basis_gates=["x", "s", "h", "rx", "ry", "rz", "cx", "cz", "swap"])
    assert device.run(compiled_branch).probabilities() == {"1": 1}
    assert compiled.metadata["transpile"]["analyses"]["dynamic_execution_order"]
    static = transpile(Circuit(1).h(0).h(0).measure_all(), optimization_level=level)
    assert device.run(static).probabilities() == {"0": 1}


def test_dynamic_routing_and_unsupported_exports_are_not_silently_changed():
    circuit = Circuit(2, 1).h(0).measure(0, 0).cx(0, 1)
    with pytest.raises(ValueError, match="routing"):
        transpile(circuit, coupling_map=[(0, 1)])
    conditional = Circuit(1, 1).x(0).c_if(0, 1)
    with pytest.raises(ValueError, match="conditional"):
        conditional.to_openqasm()


def test_qiskit_import_export_preserves_midcircuit_read_order():
    qiskit = pytest.importorskip("qiskit")
    circuit = qiskit.QuantumCircuit(2, 2)
    circuit.h(0)
    circuit.measure(0, 0)
    circuit.s(1)
    circuit.reset(0)
    circuit.x(0)
    circuit.measure(0, 1)
    native = circuit_from_qiskit(circuit)
    exported = circuit_to_qiskit(native)
    assert [item.operation.name for item in exported.data] == [item.operation.name for item in circuit.data]
    assert StabilizerDevice().run(native).probabilities() == {"01": .5, "11": .5}


def test_qiskit_nested_if_else_import_and_snapshot():
    qiskit = pytest.importorskip("qiskit")
    circuit = qiskit.QuantumCircuit(2, 2)
    with circuit.if_test((circuit.clbits[0], 0)) as otherwise:
        circuit.x(0)
        circuit.measure(0, 0)
        with circuit.if_test((circuit.clbits[1], 0)):
            circuit.x(1)
    with otherwise:
        circuit.x(0)
    circuit.measure([0, 1], [0, 1])
    native = circuit_from_qiskit(circuit)
    assert StabilizerDevice().run(native).probabilities() == {"11": 1}
    with pytest.raises(ValueError, match="conditional"):
        circuit_to_qiskit(native)


def test_clifford_midmeasurement_reset_counts_match_installed_aer():
    qiskit = pytest.importorskip("qiskit")
    aer = pytest.importorskip("qiskit_aer")
    reference = qiskit.QuantumCircuit(2, 3)
    reference.h(0)
    reference.cx(0, 1)
    reference.measure(0, 0)
    reference.reset(0)
    reference.h(1)
    reference.measure(1, 1)
    reference.measure(0, 2)
    native = circuit_from_qiskit(reference)
    expected = StabilizerDevice().run(native).probabilities()
    oracle = aer.AerSimulator(method="stabilizer").run(reference, shots=4096, seed_simulator=11).result().get_counts()
    for label, probability in expected.items():
        assert abs(oracle.get(label[::-1], 0) / 4096 - probability) < .04


def test_readout_and_clifford_noise_match_installed_aer():
    qiskit = pytest.importorskip("qiskit")
    aer = pytest.importorskip("qiskit_aer")
    aer_noise = pytest.importorskip("qiskit_aer.noise")
    from quantumbridge.noise import BitFlipChannel, NoiseModel, ReadoutError

    reference = qiskit.QuantumCircuit(1, 1)
    reference.h(0)
    reference.id(0)
    reference.measure(0, 0)
    native = circuit_from_qiskit(reference)
    model = NoiseModel().add_channel(BitFlipChannel(.2)).add_readout_error(0, ReadoutError(.1, .3))
    expected = StabilizerDevice(noise_model=model).run(native).probabilities()
    oracle_model = aer_noise.NoiseModel()
    oracle_model.add_all_qubit_quantum_error(aer_noise.pauli_error([("X", .2), ("I", .8)]), ["id"])
    oracle_model.add_all_qubit_readout_error(aer_noise.ReadoutError([[.9, .1], [.3, .7]]))
    counts = aer.AerSimulator(method="stabilizer", noise_model=oracle_model).run(reference, shots=4096, seed_simulator=3).result().get_counts()
    np.testing.assert_allclose([expected.get("0", 0), expected.get("1", 0)], [counts.get("0", 0) / 4096, counts.get("1", 0) / 4096], atol=.04)
