# Independent QuantumBridge tests; no upstream source or test cases copied.

import json

import numpy as np
import pytest

from quantumbridge import (
    BackendEstimatorV2, BackendSamplerV2, Circuit, DensityMatrixDevice, MatrixProductState,
    MatrixProductStateBackend, MatrixProductStateDevice, Parameter, Provider, Result,
    StatevectorDevice,
)
from quantumbridge.compat.qiskit_aer import execute_basic_circuit_native, run_matrix_product_state_simulator_native
from quantumbridge.noise import AmplitudeDampingChannel, BitFlipChannel, NoiseModel, NoisyEstimator, NoisySampler, ReadoutError
from quantumbridge.operators import Pauli, SparsePauliOperator
from quantumbridge.qml import QNode
from quantumbridge.utils.math import Hamiltonian, PauliX, PauliY, PauliZ, apply_unitary, gate_matrix


@pytest.mark.parametrize("width,seed", [(1, 1), (3, 4), (5, 9)])
def test_complex_nonadjacent_and_permuted_gates_match_dense_statevector(width, seed):
    rng = np.random.default_rng(seed)
    initial = rng.normal(size=1 << width) + 1j * rng.normal(size=1 << width)
    initial /= np.linalg.norm(initial)
    state = MatrixProductState.from_statevector(initial, cutoff=0)
    expected = initial.copy()
    for _ in range(9):
        wires = tuple(rng.choice(width, size=min(width, 3), replace=False))
        dimension = 1 << len(wires)
        q, _ = np.linalg.qr(rng.normal(size=(dimension, dimension)) + 1j * rng.normal(size=(dimension, dimension)))
        state.apply(q, wires)
        expected = apply_unitary(expected, q, wires, width)
        np.testing.assert_allclose(state.statevector(), expected, atol=2e-12)
    assert state.discarded_weight == 0
    wires = tuple(reversed(range(min(width, 2))))
    reference = DensityMatrixDevice(initial_state=expected)
    np.testing.assert_allclose(state.reduced_density_matrix(wires), _reduced(reference.density_matrix(Circuit(width)), wires, width), atol=2e-12)
    assert state.probabilities(wires) == pytest.approx(reference.probabilities(Circuit(width), wires), abs=2e-12)


def _reduced(matrix, wires, width):
    from quantumbridge.qml.qnode import _partial_density_matrix

    return _partial_density_matrix(matrix, width, wires)


def test_schmidt_truncation_reports_discarded_weight_and_preserves_norm():
    theta = .8
    circuit = Circuit(2).ry(theta, 0).cx(0, 1)
    device = MatrixProductStateDevice(max_bond_dim=1, cutoff=0)
    state = device.matrix_product_state(circuit)
    assert state.bond_dimensions == (1,)
    assert state.truncations == 1
    assert state.discarded_weight == pytest.approx(np.sin(theta / 2) ** 2)
    np.testing.assert_allclose(state.statevector(), [1, 0, 0, 0], atol=1e-12)
    exact = MatrixProductStateDevice(cutoff=0).statevector(circuit)
    assert abs(np.vdot(exact, state.statevector())) ** 2 == pytest.approx(1 - state.discarded_weight)
    cutoff_state = MatrixProductState.from_statevector(exact, cutoff=.2)
    assert cutoff_state.bond_dimensions == (1,)
    assert cutoff_state.discarded_weight == pytest.approx(state.discarded_weight)


def test_compressed_initial_state_roundtrip_and_defensive_copies():
    state = MatrixProductStateDevice().matrix_product_state(Circuit(3).h(2).cx(2, 0).t(0))
    restored = MatrixProductState.from_dict(json.loads(json.dumps(state.to_dict())))
    np.testing.assert_allclose(restored.statevector(), state.statevector(), atol=1e-12)
    exported = restored.tensors
    exported[0][:] = 0
    assert np.linalg.norm(restored.statevector()) == pytest.approx(1)
    device = MatrixProductStateDevice(initial_state=state)
    result = Result.from_json(device.run(Circuit(3).rx(.3, 1)).to_json())
    np.testing.assert_allclose(result.matrix_product_state().statevector(), device.statevector(Circuit(3).rx(.3, 1)), atol=1e-12)
    assert result.statevector() is None
    assert result.probabilities() is None
    assert result.validate_schema()


def test_normalization_and_canonicalization_of_noncanonical_input():
    tensors = [np.array([1, 0], complex).reshape(1, 2, 1) * (2j), np.array([1, 0], complex).reshape(1, 2, 1) / (2j)]
    state = MatrixProductState(tensors)
    np.testing.assert_allclose(state.statevector(), [1, 0, 0, 0], atol=1e-12)
    assert state.project(0, 1) == 0
    assert state.measure(0, np.random.default_rng(2)) == 0


def test_pauli_hamiltonian_dense_moments_and_mixed_noise_match_density():
    circuit = Circuit(3).h(0).ry(.6, 2).cx(2, 0).t(1).rx(.3, 1).channel(AmplitudeDampingChannel(.25), [0])
    device, reference = MatrixProductStateDevice(cutoff=0), DensityMatrixDevice()
    observables = [PauliX(0), PauliY(1), Hamiltonian([(.7, PauliX(0)), (-.3, PauliY(2))]),
                   SparsePauliOperator([("XYZ", .4), ("ZYI", -.7)]), np.diag(np.arange(8))]
    for observable in observables:
        assert device.expectation(circuit, observable) == pytest.approx(reference.expectation(circuit, observable), abs=2e-12)
        assert device.variance(circuit, observable) == pytest.approx(reference.variance(circuit, observable), abs=2e-12)
    np.testing.assert_allclose(device.density_matrix(circuit), reference.density_matrix(circuit), atol=2e-12)
    np.testing.assert_allclose(device.reduced_density_matrix(circuit, [2, 0]), _reduced(reference.density_matrix(circuit), [2, 0], 3), atol=2e-12)
    assert device.probabilities(circuit, [2, 0]) == pytest.approx(reference.probabilities(circuit, [2, 0]), abs=2e-12)
    assert device.expectation(Circuit(1).h(0), "X") == pytest.approx(1)
    with pytest.raises(ValueError, match="Hermitian"):
        device.expectation(Circuit(1), Pauli("iX"))


def test_ordered_channels_dynamic_control_reset_and_readout():
    circuit = Circuit(2, 1).ry(.9, 0).cx(0, 1).measure(0, 0).if_else((0, 1), Circuit(2).rx(.4, 1)).reset(0)
    model = NoiseModel().add_channel(BitFlipChannel(.1), wires=[1]).add_readout_error(0, ReadoutError(.2, .3))
    device, reference = MatrixProductStateDevice(noise_model=model), DensityMatrixDevice(noise_model=model)
    np.testing.assert_allclose(device.density_matrix(circuit), reference.density_matrix(circuit), atol=2e-12)
    assert device.run(circuit).probabilities() == pytest.approx(reference.run(circuit).probabilities(), abs=2e-12)
    result = device.run_shots(circuit, shots=1200, seed=19, memory=True)
    assert sum(result.counts().values()) == 1200
    assert len(result.memory()) == 1200
    assert result.counts() == device.run_shots(circuit, shots=1200, seed=19).counts()
    assert result.probabilities() == pytest.approx(reference.run(circuit).probabilities(), abs=.045)
    payload = device.run(circuit).to_dict()
    assert sum(item["weight"] for item in payload["metadata"]["mps_ensemble"]) == pytest.approx(1)
    assert Result.from_json(json.dumps(payload)).probabilities() == pytest.approx(reference.run(circuit).probabilities())


def test_branch_snapshot_survives_overwritten_condition_bits():
    true = Circuit(1, 1).x(0).measure(0, 0).ry(.7, 0)
    circuit = Circuit(1, 1).if_else((0, 0), true, Circuit(1).z(0))
    np.testing.assert_allclose(MatrixProductStateDevice().density_matrix(circuit), DensityMatrixDevice().density_matrix(circuit), atol=1e-12)


@pytest.mark.parametrize("wires", [(3, 0), (1, 3, 0)])
def test_correlated_complex_kraus_channels_preserve_wire_order(wires):
    rng = np.random.default_rng(len(wires))
    dimension = 1 << len(wires)
    isometry, _ = np.linalg.qr(rng.normal(size=(2 * dimension, dimension)) + 1j * rng.normal(size=(2 * dimension, dimension)))
    operators = [isometry[:dimension], isometry[dimension:]]
    circuit = Circuit(4).h(3).ry(.3, 0).cx(3, 1).kraus(operators, wires).rx(.5, 1)
    np.testing.assert_allclose(MatrixProductStateDevice(cutoff=0).density_matrix(circuit), DensityMatrixDevice().density_matrix(circuit), atol=2e-12)


def test_noisy_sampler_and_estimator_dispatch_to_native_mps():
    model = NoiseModel().add_channel(AmplitudeDampingChannel(.4)).add_readout_error(0, ReadoutError(.2, .3))
    circuit = Circuit(1).h(0)
    device = MatrixProductStateDevice()
    reference = DensityMatrixDevice(noise_model=model)
    sampler = NoisySampler(20, model, base_device=device, seed=4)
    assert sampler.probabilities(circuit) == pytest.approx(reference.run(circuit).probabilities())
    assert sum(sampler.run(circuit).counts().values()) == 20
    assert NoisyEstimator(model, base_device=device).expectation(circuit, PauliX(0)) == pytest.approx(np.sqrt(.6))


def test_shot_trajectories_do_not_require_analytic_branch_enumeration():
    circuit = Circuit(4, 4)
    for wire in range(4):
        circuit.h(wire).measure(wire, wire)
    device = MatrixProductStateDevice(max_branches=2)
    with pytest.raises(RuntimeError, match="max_branches"):
        device.run(circuit)
    assert sum(device.run_shots(circuit, shots=40, seed=4).counts().values()) == 40
    assert device.sample(Circuit(1), shots=0) == []


def test_hundred_qubit_ghz_runs_without_dense_expansion(monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError("Dense expansion was attempted")

    monkeypatch.setattr(StatevectorDevice, "statevector", forbidden)
    monkeypatch.setattr(MatrixProductState, "statevector", forbidden)
    monkeypatch.setattr(DensityMatrixDevice, "density_matrix", forbidden)
    circuit = Circuit(100).h(0)
    for wire in range(99):
        circuit.cx(wire, wire + 1)
    device = MatrixProductStateDevice(max_memory_mb=2)
    state = device.matrix_product_state(circuit)
    assert max(state.bond_dimensions) == 2
    assert sum(tensor.nbytes for tensor in state.tensors) < 20_000
    assert state.expectation_pauli("X" * 100) == pytest.approx(1, abs=1e-12)
    assert device.expectation(circuit, PauliZ(99)) == pytest.approx(0, abs=1e-12)
    assert device.probabilities(circuit, [99, 0]) == pytest.approx({"00": .5, "01": 0, "10": 0, "11": .5}, abs=1e-12)
    np.testing.assert_allclose(device.reduced_density_matrix(circuit, [0, 99]), np.diag([.5, 0, 0, .5]), atol=1e-12)
    counts = device.counts(circuit, shots=16, seed=7)
    assert set(counts) <= {"0" * 100, "1" * 100}
    assert sum(counts.values()) == 16
    assert device.run(circuit).matrix_product_state().num_qubits == 100


def test_native_backend_jobs_v2_primitives_and_per_run_options():
    theta = Parameter("theta")
    circuit = Circuit(2).ry(theta, 1).cx(1, 0)
    backend = MatrixProductStateBackend()
    assert np.trace(backend.device.density_matrix(circuit, {theta: .8})) == pytest.approx(1)
    result = backend.run([circuit, circuit], parameter_values=[{theta: 0}, {theta: .8}]).result()
    assert len(result) == 2
    assert result[1].matrix_product_state().bond_dimensions == (2,)
    truncated = backend.run(circuit, parameter_values={theta: .8}, max_bond_dim=1).result()
    assert truncated.metadata()["max_discarded_weight"] > .1
    assert backend.device.state_options["max_bond_dim"] is None
    assert Provider().get_backend("matrix_product_state").configuration()["conditional"] is True
    measured = Circuit(2, 2).h(0).cx(0, 1).measure(1, 0).measure(0, 1)
    sampled = BackendSamplerV2(backend=backend).run([measured], shots=16).result()[0]
    assert sum(sampled.data.meas.get_counts().values()) == 16
    estimation = BackendEstimatorV2(backend=backend).run([(Circuit(1).ry(.4, 0), ["Z"])], precision=0).result()[0]
    assert np.asarray(estimation.data.evs).item() == pytest.approx(np.cos(.4))
    truncated_pub = BackendEstimatorV2(backend=backend, options={"max_bond_dim": 1}).run([(circuit, ["ZZ"], {theta: .8})], precision=0).result()[0]
    assert truncated_pub.metadata["mps_truncation"][0][0]["max_discarded_weight"] > .1


@pytest.mark.parametrize("precision", [-.1, np.nan, np.inf, True, "0"])
def test_estimator_precision_rejects_invalid_values(precision):
    with pytest.raises(ValueError, match="finite and non-negative"):
        BackendEstimatorV2(MatrixProductStateBackend()).run([(Circuit(1), ["Z"])], precision=precision)


def test_qnode_state_reduced_measurements_and_finite_differences():
    def program(tape, angle):
        tape.ry(angle, 0)
        tape.cx(0, 2)
        return tape.state(), tape.density_matrix([2, 0]), tape.expval(PauliZ(0)), tape.var(PauliZ(0)), tape.counts(wires=[2, 0])

    node = QNode(program, 3, device=MatrixProductStateDevice(), shots=30, seed=4)
    state, density, ev, variance, counts = node(.7)
    assert state.shape == (8,)
    assert density.shape == (4, 4)
    assert ev == pytest.approx(np.cos(.7))
    assert variance == pytest.approx(np.sin(.7) ** 2)
    assert set(counts) <= {"00", "11"}
    def reduced(tape):
        tape.h(0)
        tape.cx(0, 99)
        return tape.density_matrix([99]), tape.expval(PauliX(0))
    rho, value = QNode(reduced, 100, device=MatrixProductStateDevice(max_memory_mb=2))()
    np.testing.assert_allclose(rho, np.eye(2) / 2, atol=1e-12)
    assert value == pytest.approx(0, abs=1e-12)
    derivative = (node(.7 + 1e-5)[2] - node(.7 - 1e-5)[2]) / 2e-5
    assert derivative == pytest.approx(-np.sin(.7), abs=1e-9)


def test_native_aer_dispatch_ir_roundtrip_and_mps_result_data():
    circuit = Circuit(6).h(5).cx(5, 0).t(0)
    result = run_matrix_product_state_simulator_native(json.loads(json.dumps(circuit.to_ir().to_dict())), shots=None)
    state = MatrixProductState.from_dict(result.to_dict()["data"]["matrix_product_state"])
    np.testing.assert_allclose(state.statevector(), StatevectorDevice().statevector(circuit), atol=1e-12)
    result = execute_basic_circuit_native(circuit, backend="matrix_product_state", shots=20, seed=3)
    assert sum(result.counts.values()) == 20
    assert result.metadata["hardware_access"] is False


@pytest.mark.parametrize("options", [{"max_bond_dim": 0}, {"max_bond_dim": True}, {"cutoff": -1}, {"cutoff": np.nan}, {"max_memory_mb": -1}, {"max_branches": 0}, {"max_qubits": True}])
def test_invalid_configuration_is_explicit(options):
    with pytest.raises(ValueError):
        MatrixProductStateDevice(**options)


def test_invalid_states_wires_operators_and_resource_limits():
    with pytest.raises(ValueError, match="connected"):
        MatrixProductState([np.zeros((2, 2, 1))])
    with pytest.raises(ValueError, match="normalized"):
        MatrixProductState([np.zeros((1, 2, 1))])
    with pytest.raises(ValueError, match="normalized"):
        MatrixProductState.from_statevector([1, 1])
    state = MatrixProductState.zero(2)
    with pytest.raises(ValueError, match="wires"):
        state.apply(np.eye(4), [0, 0])
    with pytest.raises(ValueError, match="dimensions"):
        state.apply(np.eye(3), [0])
    with pytest.raises(ValueError, match="zero MPS"):
        state.apply(np.zeros((2, 2)), [0])
    with pytest.raises(MemoryError):
        MatrixProductState.zero(100, max_memory_mb=2).statevector()
    with pytest.raises(MemoryError):
        MatrixProductState.zero(100, max_memory_mb=2).probabilities()
    with pytest.raises(MemoryError):
        MatrixProductState.zero(100, max_memory_mb=2).reduced_density_matrix()
    device = MatrixProductStateDevice()
    with pytest.raises(ValueError, match="single MPS"):
        device.statevector(Circuit(1).reset(0))
    with pytest.raises(ValueError, match="shots"):
        device.run_shots(Circuit(1), shots=2.5)
    with pytest.raises(ValueError, match="width"):
        MatrixProductStateDevice(initial_state=MatrixProductState.zero(2)).run(Circuit(1))
