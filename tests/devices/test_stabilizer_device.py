# Independently implemented QuantumBridge tests; no upstream source copied.

import numpy as np
import pytest

from quantumbridge import (
    BackendEstimator, BackendSampler, Circuit, Parameter, Result, ShotSampler,
    StabilizerBackend, StabilizerDevice,
)
from quantumbridge.information import Clifford, StabilizerState
from quantumbridge.noise import (
    AmplitudeDampingChannel, BitFlipChannel, DepolarizingChannel, KrausChannel,
    NoiseModel, PhaseDampingChannel, PhaseFlipChannel, ReadoutError,
)
from quantumbridge.operators import Pauli, SparsePauliOperator
from quantumbridge.providers import JobError, Provider
from quantumbridge.utils.math import Hamiltonian, PauliX, PauliZ


def test_exact_expectation_variance_and_explicit_dense_conversion():
    device = StabilizerDevice()
    circuit = Circuit(2).h(0).cx(0, 1)
    assert device.expectation(circuit, Pauli("XX")) == 1
    assert device.expectation(circuit, "YY") == -1
    assert device.expectation(circuit, PauliZ(0)) == 0
    assert device.variance(circuit, PauliZ(0)) == 1
    assert device.expectation(circuit, Hamiltonian([(2, PauliZ(0))])) == 0
    observable = SparsePauliOperator([("XI", 1), ("ZI", 1)])
    assert device.variance(Circuit(2).h(0), observable) == 1
    np.testing.assert_allclose(device.density_matrix(circuit), np.outer(device.statevector(circuit), device.statevector(circuit).conj()), atol=1e-12)
    assert device.stabilizer_state(circuit.measure_all()).equiv(StabilizerState(Circuit(2).h(0).cx(0, 1)))


def test_measurement_record_and_wire_order_are_distinct():
    device = StabilizerDevice()
    circuit = Circuit(3, 3).x(0).measure(0, 2).x(0)
    assert device.run(circuit).probabilities() == {"001": 1}
    assert device.run_shots(circuit, 10).counts() == {"001": 10}
    assert device.counts(circuit, shots=10) == {"000": 10}
    assert device.sample(Circuit(3).x(0), wires=[2, 0], shots=2) == ["01", "01"]
    assert device.probabilities(Circuit(3).x(0), wires=[2, 0]) == {"01": 1}


def test_midmeasurement_dephasing_reset_and_classical_feedback():
    device = StabilizerDevice()
    circuit = Circuit(1, 2).h(0).measure(0, 0).h(0).measure(0, 1)
    assert device.run(circuit).probabilities() == {"00": .25, "01": .25, "10": .25, "11": .25}
    reset = Circuit(2).h(0).cx(0, 1).reset(0)
    assert device.probabilities(reset) == {"00": .5, "01": .5}
    np.testing.assert_allclose(np.diag(device.density_matrix(reset)), [.5, .5, 0, 0], atol=1e-12)
    feedback = Circuit(1, 1).h(0).measure(0, 0).if_else((0, 1), Circuit(1).x(0), Circuit(1).id(0))
    assert device.probabilities(feedback) == {"0": 1}
    assert device.run(feedback).probabilities() == {"0": .5, "1": .5}


def test_branch_entry_snapshot_survives_condition_bit_overwrite():
    device = StabilizerDevice()
    true = Circuit(1, 1).x(0).measure(0, 0)
    circuit = Circuit(1, 1).if_else((0, 0), true, Circuit(1, 1).x(0))
    assert device.probabilities(circuit) == {"1": 1}
    assert device.probabilities(Circuit(1, 1).append(circuit.to_instruction(), [0], clbits=[0])) == {"1": 1}
    circuit.measure(0, 0)
    assert device.run_shots(circuit, shots=16, seed=2).counts() == {"1": 16}


def test_repeated_nested_and_empty_if_else_blocks():
    device = StabilizerDevice()
    block = Circuit(1, 1).if_else((0, 0), Circuit(1, 1).x(0).measure(0, 0), Circuit(1, 1).x(0))
    repeated = block.compose(block).measure(0, 0)
    assert device.run(repeated).probabilities() == {"0": 1}
    inner = Circuit(1, 1).if_else((0, 0), Circuit(1, 1).x(0), Circuit(1, 1).z(0))
    nested = Circuit(1, 1).if_else((0, 0), inner, Circuit(1, 1).id(0)).measure(0, 0)
    assert device.run(nested).probabilities() == {"1": 1}
    assert device.run(Circuit(1, 1).if_else((0, 1), Circuit(1), Circuit(1).x(0)).measure(0, 0)).probabilities() == {"1": 1}
    remapped = Circuit(2, 2).compose(nested, qubits=[1], clbits=[1])
    assert device.run(remapped).probabilities() == {"01": 1}


@pytest.mark.parametrize("channel,expected", [
    (BitFlipChannel(.2), .6), (PhaseFlipChannel(.2), 1),
    (DepolarizingChannel(.3), .6), (PhaseDampingChannel(.4), 1),
])
def test_clifford_noise_exact_ensemble(channel, expected):
    device = StabilizerDevice(noise_model=NoiseModel().add_channel(channel, wires=[0]))
    assert device.expectation(Circuit(1), Pauli("Z")) == pytest.approx(expected)
    assert np.trace(device.density_matrix(Circuit(1))) == pytest.approx(1)
    counts = device.counts(Circuit(1), shots=1500, seed=7)
    assert abs(counts.get("0", 0) / 1500 - (1 + expected) / 2) < .05
    with pytest.raises(ValueError, match="single stabilizer state"):
        device.stabilizer_state(Circuit(1))


def test_general_clifford_mixture_and_phase_damping_coherence():
    h = np.array([[1, 1], [1, -1]]) / np.sqrt(2)
    mixture = KrausChannel([np.sqrt(.3) * np.eye(2), np.sqrt(.7) * h])
    device = StabilizerDevice(noise_model=NoiseModel().add_channel(mixture))
    np.testing.assert_allclose(device.probabilities(Circuit(1))["0"], .65)
    phase = StabilizerDevice(noise_model=NoiseModel().add_channel(PhaseDampingChannel(.4)))
    assert phase.expectation(Circuit(1).h(0), "X") == pytest.approx(np.sqrt(.6))


def test_asymmetric_readout_and_noisy_feedback():
    noise = NoiseModel().add_readout_error(0, ReadoutError(.2, .4))
    device = StabilizerDevice(noise_model=noise)
    assert device.run(Circuit(1, 1).measure(0, 0)).probabilities() == {"0": .8, "1": .2}
    assert device.run(Circuit(1)).probabilities() == {"0": .8, "1": .2}
    feedback = Circuit(1, 1).measure(0, 0).if_else((0, 1), Circuit(1).x(0))
    assert device.probabilities(feedback)["1"] == pytest.approx(.2)
    counts = device.run_shots(Circuit(1, 1).x(0).measure(0, 0), 1500, seed=11).counts()
    assert abs(counts.get("1", 0) / 1500 - .6) < .05


def test_seeded_memory_and_serialization_preserve_shot_order():
    device = StabilizerDevice()
    circuit = Circuit(2, 1).h(0).measure(0, 0)
    result = device.run_shots(circuit, 50, seed=15, memory=True)
    assert result.memory() == device.run_shots(circuit, 50, seed=15, memory=True).memory()
    assert result.memory() != sorted(result.memory())
    assert result.counts() == device._counts(result.memory())
    assert Result.from_json(result.to_json()).memory() == result.memory()
    assert result.validate_schema()
    copied = result.memory()
    copied.clear()
    assert len(result.memory()) == 50
    assert device.run_shots(circuit, 1).memory() is None


def test_backend_jobs_parameter_binding_and_v2_memory_width():
    backend = Provider().get_backend("stabilizer")
    assert isinstance(backend, StabilizerBackend)
    theta = Parameter("theta")
    results = backend.run([Circuit(1).rx(theta, 0), Circuit(1).x(0)], shots=8,
                          parameter_values=[{"theta": 0}, {}]).result()
    assert [result.counts() for result in results] == [{"0": 8}, {"1": 8}]
    circuit = Circuit(3, 1).h(0).measure(0, 0)
    sampler = BackendSampler(backend, options={"shots": 30, "seed_simulator": 4})
    result = sampler.run([(circuit,)])[0]
    assert result.data.meas.num_bits == 1
    assert result.data.meas.num_shots == 30
    assert result.data.meas.get_counts() == result.data.counts
    assert list(result.data.meas) != sorted(result.data.meas)
    estimator = BackendEstimator(backend)
    ev = estimator.run([(Circuit(2).h(0).cx(0, 1), [Pauli("XX"), Pauli("YY")])])[0]
    assert ev.data.evs == [1, -1]
    assert ev.metadata["simulation"] == "exact_stabilizer"
    assert backend.run(Circuit(1).x(0), observable=Pauli("Z")).result().expectation_value() == -1


def test_backend_noise_run_options_are_isolated():
    backend = StabilizerBackend()
    noise = NoiseModel().add_channel(BitFlipChannel(1))
    assert backend.run(Circuit(1), shots=6, noise_model=noise).result().counts() == {"1": 6}
    assert backend.run(Circuit(1), shots=6).result().counts() == {"0": 6}
    assert backend.device.noise_model is None
    assert ShotSampler(6, base_device=backend.device).run(Circuit(1).x(0)).counts() == {"1": 6}
    with pytest.raises(JobError):
        backend.run(Circuit(1).t(0)).result()
    backend.set_options(noise_model=noise)
    assert BackendEstimator(backend).run([(Circuit(1), Pauli("Z"))])[0].data.evs == -1
    assert BackendEstimator(backend, options={"noise_model": None}).run([(Circuit(1), Pauli("Z"))])[0].data.evs == 1


def test_statevector_backend_sampler_also_preserves_classical_memory_mapping():
    from quantumbridge import Backend

    backend = Backend()
    circuit = Circuit(3, 2).x(0).measure(0, 1)
    result = BackendSampler(backend, options={"shots": 6}).run([(circuit,)])[0]
    assert result.data.counts == {"01": 6}
    assert result.data.meas.num_bits == 2
    assert list(result.data.meas) == ["01"] * 6
    assert not backend.configuration()["conditional"]
    assert StabilizerBackend().configuration()["conditional"]


def test_large_backend_never_enumerates_probabilities_or_dense_states(monkeypatch):
    def reject(*args, **kwargs):
        pytest.fail("Dense state or probability enumeration in a shot workflow")

    monkeypatch.setattr(StabilizerState, "probabilities_dict", reject)
    monkeypatch.setattr(StabilizerState, "to_statevector", reject)
    monkeypatch.setattr(Clifford, "to_matrix", reject)
    circuit = Circuit(64)
    for wire in range(64):
        circuit.h(wire)
    result = StabilizerBackend().run(circuit, shots=12, seed_simulator=1, memory=True).result()
    assert sum(result.counts().values()) == 12
    assert len(result.memory()) == 12
    assert all(len(label) == 64 for label in result.memory())
    assert len(result.counts()) == 12
    assert ShotSampler(4, base_device=StabilizerDevice()).run(circuit).counts()
    assert BackendEstimator(StabilizerBackend()).run([(circuit, Pauli("X" * 64))])[0].data.evs == 1


def test_exact_branch_budget_does_not_limit_shot_execution():
    device = StabilizerDevice(max_branches=2)
    circuit = Circuit(2).h(0).h(1).measure_all()
    with pytest.raises(RuntimeError, match="max_branches"):
        device.run(circuit)
    assert sum(device.run_shots(circuit, shots=5).counts().values()) == 5


@pytest.mark.parametrize("action", [
    lambda: StabilizerDevice(max_qubits=0), lambda: StabilizerDevice(max_branches=0),
    lambda: StabilizerDevice(max_qubits=1).sample(Circuit(2)),
    lambda: StabilizerDevice().run(Circuit(1).t(0)),
    lambda: StabilizerDevice().run(Circuit(1).rx(.2, 0)),
    lambda: StabilizerDevice().sample(Circuit(1), shots=-1),
    lambda: StabilizerDevice().run_shots(Circuit(1), shots=0),
    lambda: StabilizerDevice().sample(Circuit(1), wires=[0, 0]),
    lambda: StabilizerDevice().expectation(Circuit(1), Pauli("iX")),
    lambda: StabilizerDevice().expectation(Circuit(1), Pauli("XX")),
    lambda: StabilizerDevice().expectation(Circuit(1), np.eye(2)),
    lambda: StabilizerDevice(noise_model={}).run(Circuit(1)),
    lambda: StabilizerDevice(noise_model=NoiseModel().add_channel(AmplitudeDampingChannel(.2))).run(Circuit(1)),
    lambda: StabilizerDevice(noise_model=NoiseModel().add_channel(KrausChannel([.5 * np.eye(2)]))).run(Circuit(1)),
    lambda: StabilizerDevice(noise_model=NoiseModel().add_channel(KrausChannel([np.eye(4)]))).run(Circuit(2)),
])
def test_invalid_execution_is_rejected_explicitly(action):
    with pytest.raises((ValueError, TypeError)):
        action()
