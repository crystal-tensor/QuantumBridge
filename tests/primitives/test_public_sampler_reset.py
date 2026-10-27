# Copyright 2026 QuantumBridge Contributors. Apache-2.0.
"""One public preparation trajectory, then terminal sampling; Legacy stays ensemble."""

import gc
import numpy as np
import pytest

from quantumbridge import Circuit, Parameter
from quantumbridge.execution.control_flow_engine import DynamicExecutionEngine
from quantumbridge.execution.resource_context import ResourceScope
from quantumbridge.execution.resource_ledger import UnifiedResourceLedger
from quantumbridge.primitives import Estimator
from quantumbridge.primitives.v2 import StatevectorSampler
from quantumbridge.utils.math import PauliZ


def bell_reset():
    circuit = Circuit(2, 2).h(0).cx(0, 1).reset(0)
    circuit.measure(0, 0).measure(1, 1)
    return circuit


def test_reset_then_terminal_measurement_is_zero_and_uses_existing_engine(monkeypatch):
    calls = []
    original = DynamicExecutionEngine.trajectories

    def observed(self, shots, seed=None):
        calls.append((shots, seed))
        yield from original(self, shots, seed)

    monkeypatch.setattr(DynamicExecutionEngine, "trajectories", observed)
    circuit = Circuit(1, 1).h(0).reset(0)
    circuit.measure(0, 0)
    assert StatevectorSampler(default_shots=16, seed=11).run([circuit]).result()[
        0
    ].data.c.get_counts() == {"0": 16}
    assert calls == [(1, None)]


@pytest.mark.parametrize("trajectory_seed,expected", [(2, "00"), (0, "10")])
def test_entangled_reset_is_a_single_valid_trajectory_not_per_shot_ensemble(
    monkeypatch, trajectory_seed, expected
):
    original = DynamicExecutionEngine.trajectories
    states = []

    def controlled(self, shots, seed=None):
        assert shots == 1 and seed is None
        for state, bits, rng in original(self, shots, trajectory_seed):
            states.append(state.copy())
            yield state, bits, rng

    monkeypatch.setattr(DynamicExecutionEngine, "trajectories", controlled)
    pub = StatevectorSampler(default_shots=16, seed=11).run([bell_reset()]).result()[0]
    assert pub.data.c.get_counts() == {expected: 16}
    state = states[0]
    reference = np.array(
        [1, 0, 0, 0] if expected == "00" else [0, 1, 0, 0], dtype=complex
    )
    np.testing.assert_allclose(state, reference, atol=3e-14, rtol=0)
    assert np.vdot(state, state).real == pytest.approx(1, abs=3e-14)


def test_multiple_resets_and_parameter_sweeps_keep_batch_and_independent_pubs():
    theta = Parameter("theta")
    circuit = Circuit(2, 2).ry(theta, 0).cx(0, 1).reset(0).reset(1)
    circuit.measure(0, 0).measure(1, 1)
    values = np.array([[[0.2], [0.9]], [[1.7], [2.5]]])
    result = (
        StatevectorSampler(default_shots=4, seed=11)
        .run([(circuit, values), bell_reset()])
        .result()
    )
    assert result[0].data.c.shape == (2, 2)
    assert result[0].data.c.get_counts() == {"00": 16}
    assert sum(result[1].data.c.get_counts().values()) == 4
    assert len(result[1].data.c.get_counts()) == 1


def test_legacy_reset_ensemble_is_unchanged():
    value = (
        Estimator()
        .run(Circuit(2).h(0).cx(0, 1).reset(0), PauliZ(1))
        .expectation_value()
    )
    np.testing.assert_allclose(value, 0, atol=3e-14, rtol=0)


def test_mid_circuit_measurement_is_a_cached_public_job_failure():
    circuit = Circuit(1, 1).h(0)
    circuit.measure(0, 0)
    circuit.x(0)
    job = StatevectorSampler(default_shots=4).run([circuit])
    assert not job.done() and job.in_final_state()
    for _ in range(2):
        with pytest.raises(Exception, match="mid-circuit measurements") as error:
            job.result()
        assert type(error.value).__name__ == "QiskitError"


def test_mid_circuit_failure_in_second_pub_does_not_execute_first(monkeypatch):
    calls = []
    original = DynamicExecutionEngine.trajectories

    def observed(*args, **kwargs):
        calls.append(1)
        yield from original(*args, **kwargs)

    monkeypatch.setattr(DynamicExecutionEngine, "trajectories", observed)
    invalid = Circuit(1, 1).h(0)
    invalid.measure(0, 0)
    invalid.reset(0)
    ledger = UnifiedResourceLedger()
    with ResourceScope(ledger):
        job = StatevectorSampler(default_shots=4).run([bell_reset(), invalid])
        with pytest.raises(Exception, match="mid-circuit measurements"):
            job.result()
    assert calls == [] and ledger.receipt()["consumed_shots"] == 0


def test_reset_result_views_keep_only_packed_storage_alive():
    ledger = UnifiedResourceLedger()
    with ResourceScope(ledger):
        job = StatevectorSampler(default_shots=8).run([bell_reset()])
        view = memoryview(job.result()[0].data.c.array)
    del job
    gc.collect()
    assert ledger.receipt()["live_memory_bytes"] == 8
    del view
    gc.collect()
    assert ledger.receipt()["live_memory_bytes"] == 0
