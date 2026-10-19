# Independent QuantumBridge tests. No upstream source or tests copied.

import json

import numpy as np
import pytest

from quantumbridge import (
    BackendEstimator, BackendSampler, Circuit, DensityMatrixBackend,
    DensityMatrixDevice, Result, ShotSampler, StatevectorDevice, transpile,
)
from quantumbridge.compat.qiskit_adapter import circuit_from_ir
from quantumbridge.compat.qiskit_aer import run_density_matrix_simulator_native
from quantumbridge.information import Chi, Choi, DensityMatrix, Kraus, Operator, PTM, Stinespring, SuperOp
from quantumbridge.noise import (
    AmplitudeDampingChannel, BitFlipChannel, NoiseModel, NoisyEstimator,
    NoisySampler, PhaseFlipChannel, ReadoutError,
)
from quantumbridge.operators import Pauli
from quantumbridge.utils.math import Hamiltonian, PauliX, PauliY, PauliZ, apply_unitary


@pytest.mark.parametrize("width,wires", [(1, [0]), (3, [2, 0]), (4, [1, 3, 0])])
def test_local_density_evolution_matches_explicit_full_operator(width, wires):
    rng = np.random.default_rng(width)
    dimension = 1 << width
    matrix = rng.normal(size=(dimension, dimension)) + 1j * rng.normal(size=(dimension, dimension))
    initial = matrix @ matrix.conj().T
    initial /= np.trace(initial)
    local_size = 1 << len(wires)
    matrix = rng.normal(size=(local_size, local_size)) + 1j * rng.normal(size=(local_size, local_size))
    unitary, _ = np.linalg.qr(matrix)
    basis = np.eye(dimension, dtype=complex)
    full = np.column_stack([apply_unitary(basis[:, index], unitary, tuple(wires), width) for index in range(dimension)])
    circuit = Circuit(width).unitary(unitary, wires)
    device = DensityMatrixDevice(initial_state=initial)
    np.testing.assert_allclose(device.density_matrix(circuit), full @ initial @ full.conj().T, atol=1e-12)


def test_ordered_nonclifford_channels_preserve_coherences_and_gate_position():
    p = .4
    device = DensityMatrixDevice()
    circuit = Circuit(1).h(0).channel(AmplitudeDampingChannel(p), [0])
    expected = np.array([[(1 + p) / 2, np.sqrt(1 - p) / 2], [np.sqrt(1 - p) / 2, (1 - p) / 2]])
    np.testing.assert_allclose(device.density_matrix(circuit), expected, atol=1e-12)
    assert device.expectation(circuit, PauliX(0)) == pytest.approx(np.sqrt(1 - p))
    assert device.expectation(circuit, PauliZ(0)) == pytest.approx(p)
    circuit.h(0)
    assert device.probabilities(circuit)["0"] == pytest.approx((1 + np.sqrt(1 - p)) / 2)
    assert device.variance(circuit, PauliZ(0)) == pytest.approx(p)
    state = device.density_matrix(Circuit(1).h(0).t(0).rx(.2, 0))
    assert DensityMatrix(state).is_valid()


@pytest.mark.parametrize("representation", [Kraus, Choi, Chi, PTM, SuperOp, Stinespring])
def test_native_channel_representations_execute_as_circuit_instructions(representation):
    operators = AmplitudeDampingChannel(.3).kraus()
    channel = representation(Kraus(operators))
    circuit = Circuit(1).x(0).append(channel.to_instruction(), [0])
    np.testing.assert_allclose(DensityMatrixDevice().density_matrix(circuit), np.diag([.3, .7]), atol=1e-12)
    np.testing.assert_allclose(DensityMatrix.from_circuit(circuit).data, np.diag([.3, .7]), atol=1e-12)
    np.testing.assert_allclose(DensityMatrix.from_label("1").evolve(channel).data, np.diag([.3, .7]), atol=1e-12)


def test_quantum_info_reset_measure_and_circuit_evolution_are_callable():
    bell = DensityMatrix.from_circuit(Circuit(2).h(0).cx(0, 1))
    reset = bell.reset([0])
    np.testing.assert_allclose(reset.data, np.diag([.5, .5, 0, 0]), atol=1e-12)
    outcome, collapsed = bell.measure([1], seed=17)
    assert collapsed.probabilities()[outcome * 2] == pytest.approx(1)
    assert bell.purity() == pytest.approx(1)
    evolved = DensityMatrix.from_label("1").evolve(Circuit(1).channel(AmplitudeDampingChannel(.2), [0]))
    np.testing.assert_allclose(evolved.data, np.diag([.2, .8]), atol=1e-12)
    np.testing.assert_allclose(bell.reset().data, np.diag([1, 0, 0, 0]), atol=1e-12)
    embedded = DensityMatrix.from_label("11").evolve(Circuit(1).channel(AmplitudeDampingChannel(.3), [0]), qargs=[0])
    np.testing.assert_allclose(embedded.data, np.diag([0, .3, 0, .7]), atol=1e-12)
    np.testing.assert_allclose(DensityMatrix.from_label("1").evolve(AmplitudeDampingChannel(.3)).data, np.diag([.3, .7]), atol=1e-12)


def test_mixed_initial_state_and_quantum_observables():
    initial = np.diag([.2, .8])
    device = DensityMatrixDevice(initial_state=initial)
    assert device.expectation(Circuit(1), Pauli("Z")) == pytest.approx(-.6)
    assert device.variance(Circuit(1), Pauli("Z")) == pytest.approx(.64)
    assert device.expectation(Circuit(1), Hamiltonian([(2, PauliX(0)), (.5, PauliZ(0))])) == pytest.approx(-.3)
    with pytest.raises(ValueError, match="pure"):
        device.statevector(Circuit(1))
    np.testing.assert_allclose(initial, np.diag([.2, .8]))


def test_dynamic_nonclifford_feedback_and_reset_match_closed_forms():
    device = DensityMatrixDevice()
    circuit = Circuit(2, 1).h(0).cx(0, 1).reset(0)
    np.testing.assert_allclose(device.density_matrix(circuit), np.diag([.5, .5, 0, 0]), atol=1e-12)
    circuit = Circuit(1, 1).h(0).measure(0, 0).h(0)
    np.testing.assert_allclose(device.density_matrix(circuit), np.eye(2) / 2, atol=1e-12)
    feedback = Circuit(1, 1).ry(.7, 0).measure(0, 0).if_else((0, 1), Circuit(1).x(0)).rz(.3, 0)
    np.testing.assert_allclose(device.density_matrix(feedback), np.diag([1, 0]), atol=1e-12)
    block = Circuit(1, 1).if_else((0, 0), Circuit(1, 1).x(0).measure(0, 0).ry(.6, 0), Circuit(1, 1).x(0))
    expected = StatevectorDevice().density_matrix(Circuit(1).x(0).ry(.6, 0))
    np.testing.assert_allclose(device.density_matrix(block), expected, atol=1e-12)


def test_analytic_merging_handles_repeated_classical_overwrites():
    circuit = Circuit(1, 1)
    for _ in range(24):
        circuit.h(0).measure(0, 0).reset(0)
    device = DensityMatrixDevice(max_branches=2)
    np.testing.assert_allclose(device.density_matrix(circuit), np.diag([1, 0]), atol=1e-12)
    np.testing.assert_allclose(list(device.run(circuit).probabilities().values()), [.5, .5], atol=1e-12)


def test_dead_branch_snapshots_do_not_cause_exponential_history_growth():
    circuit = Circuit(1, 1)
    for _ in range(16):
        circuit.h(0).measure(0, 0).if_else((0, 1), Circuit(1).x(0), inplace=True)
    device = DensityMatrixDevice(max_branches=2)
    np.testing.assert_allclose(device.density_matrix(circuit), np.diag([1, 0]), atol=1e-12)
    np.testing.assert_allclose(list(device.run(circuit).probabilities().values()), [.5, .5], atol=1e-12)


def test_trajectory_sampling_does_not_require_enumerating_classical_histories():
    circuit = Circuit(1, 18)
    for bit in range(18):
        circuit.h(0).measure(0, bit)
    device = DensityMatrixDevice(max_branches=2)
    with pytest.raises(RuntimeError, match="max_branches"):
        device.run(circuit)
    result = device.run_shots(circuit, 20, seed=41, memory=True)
    assert sum(result.counts().values()) == 20
    assert all(len(label) == 18 for label in result.memory())
    assert result.memory() == device.run_shots(circuit, 20, seed=41, memory=True).memory()


def test_result_and_channel_ir_roundtrips_are_json_safe():
    circuit = Circuit(1).h(0).channel(AmplitudeDampingChannel(.3), [0]).unitary(np.array([[1, 0], [0, 1j]]), [0])
    device = DensityMatrixDevice()
    result = device.run(circuit)
    assert result.validate_schema()
    np.testing.assert_allclose(Result.from_json(result.to_json()).density_matrix(), result.density_matrix())
    copied = result.density_matrix()
    copied[:] = 0
    assert np.trace(result.density_matrix()) == pytest.approx(1)
    expected = device.density_matrix(circuit)
    np.testing.assert_allclose(device.density_matrix(circuit_from_ir(circuit.to_ir())), expected, atol=1e-12)
    payload = json.loads(json.dumps(circuit.to_ir().to_dict()))
    actual = run_density_matrix_simulator_native(payload)
    np.testing.assert_allclose(actual.final_density_matrix, expected, atol=1e-12)
    for level in (0, 1, 2, 3):
        compiled = transpile(circuit, optimization_level=level, basis_gates=["h", "unitary"])
        np.testing.assert_allclose(device.density_matrix(compiled), expected, atol=1e-12)


def test_backend_options_jobs_v2_and_noise_configuration_are_isolated():
    backend = DensityMatrixBackend()
    excited = backend.run(Circuit(1), initial_state=[0, 1]).result()
    np.testing.assert_allclose(excited.density_matrix(), np.diag([0, 1]))
    np.testing.assert_allclose(backend.run(Circuit(1)).result().density_matrix(), np.diag([1, 0]))
    model = NoiseModel().add_channel(AmplitudeDampingChannel(.4))
    estimator = BackendEstimator(backend, options={"noise_model": model})
    pub = estimator.run([(Circuit(1).h(0), [Pauli("X"), Pauli("Z")])])[0]
    np.testing.assert_allclose(pub.data.evs, [np.sqrt(.6), .4], atol=1e-12)
    assert pub.metadata["simulation"] == "exact_density_matrix"
    circuit = Circuit(2, 1).x(0).measure(0, 0)
    samples = BackendSampler(backend, options={"shots": 8}).run([(circuit,)])[0]
    assert samples.data.counts == {"1": 8} and samples.data.meas.num_bits == 1
    assert ShotSampler(8, base_device=DensityMatrixDevice()).run(Circuit(1).x(0)).counts() == {"1": 8}


def test_noisy_estimator_no_longer_ignores_x_y_and_hamiltonian_noise():
    damp = NoiseModel().add_channel(AmplitudeDampingChannel(.4))
    assert NoisyEstimator(damp).expectation(Circuit(1).h(0), PauliX(0)) == pytest.approx(np.sqrt(.6))
    flip = NoiseModel().add_channel(PhaseFlipChannel(.3))
    circuit = Circuit(1).h(0).phase(np.pi / 2, 0)
    assert NoisyEstimator(flip).expectation(circuit, PauliY(0)) == pytest.approx(.4)
    hamiltonian = Hamiltonian([(2, PauliY(0)), (.5, PauliZ(0))])
    assert NoisyEstimator(flip).expectation(circuit, hamiltonian) == pytest.approx(.8)
    readout = NoiseModel().add_readout_error(0, ReadoutError(.2, .4))
    assert NoisyEstimator(readout).expectation(Circuit(1), PauliZ(0)) == 1
    assert NoisySampler(100, readout).probabilities(Circuit(1))["1"] == pytest.approx(.2)


def test_memory_guard_fails_before_allocating_density_state(monkeypatch):
    device = DensityMatrixDevice(max_memory_mb=1)
    monkeypatch.setattr(device, "_initial", lambda *args: pytest.fail("Allocated oversized state"))
    with pytest.raises(MemoryError, match="max_memory_mb"):
        device.density_matrix(Circuit(16))


@pytest.mark.parametrize("initial", [[1, 1], [[.2, 0], [0, .2]], [[1.000001, 0], [0, 0]], [[1, 1], [0, 0]], [[1.1, 0], [0, -.1]], [[np.nan, 0], [0, 1]]])
def test_invalid_initial_states_are_rejected(initial):
    with pytest.raises(ValueError):
        DensityMatrixDevice(initial_state=initial).density_matrix(Circuit(1))


@pytest.mark.parametrize("operators", [[], [np.eye(3)], [np.ones((2, 2))], [np.eye(2), np.eye(4)], [np.full((2, 2), np.nan)]])
def test_nonphysical_circuit_channels_are_rejected(operators):
    with pytest.raises(ValueError):
        Circuit(1).kraus(operators, [0])


def test_invalid_shots_limits_wires_and_observables_are_rejected():
    device = DensityMatrixDevice()
    for action in (
        lambda: DensityMatrixDevice(max_qubits=0), lambda: DensityMatrixDevice(max_branches=0),
        lambda: DensityMatrixDevice(max_memory_mb=0), lambda: device.run_shots(Circuit(1), 0),
        lambda: device.run_shots(Circuit(1), 2.5), lambda: device.sample(Circuit(1), shots=True),
        lambda: device.probabilities(Circuit(1), wires=[0, 0]),
        lambda: device.expectation(Circuit(1), np.array([[0, 1], [0, 0]])),
        lambda: device.expectation(Circuit(1), np.eye(4)),
    ):
        with pytest.raises(ValueError):
            action()
