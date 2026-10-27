# Copyright 2026 QuantumBridge Contributors. Apache-2.0.
"""Actual multi-wire complex math, public precision and complete-job admission."""

from concurrent.futures import ThreadPoolExecutor
import gc

import numpy as np
import pytest

from quantumbridge import Circuit, Parameter
from quantumbridge.devices import StatevectorDevice
from quantumbridge.execution.resource_context import ResourceScope
from quantumbridge.execution.resource_ledger import UnifiedResourceLedger
from quantumbridge.execution.resource_limits import UnifiedExecutionLimits
from quantumbridge.primitives.v2 import StatevectorEstimator
from quantumbridge.utils.math import PauliZ


def three_wire():
    theta, phi = Parameter("theta"), Parameter("phi")
    circuit = Circuit(3).ry(theta, 2).rz(phi, 2)
    values = np.array([[[0.1, 0.2], [0.3, -0.4]], [[0.5, 0.6], [-0.7, 0.8]]])
    # Parameter order is circuit.parameters, not gate insertion assumptions.
    ordered = np.stack([values[..., 0] if p == theta else values[..., 1] for p in circuit.parameters], axis=-1)
    expected = np.stack([np.cos(values[..., 0]), np.sin(values[..., 0])*np.cos(values[..., 1]), np.sin(values[..., 0])*np.sin(values[..., 1])])
    return circuit, ordered, expected


def test_three_wire_complex_state_broadcast_322_matches_independent_math():
    circuit, values, expected = three_wire()
    pub = StatevectorEstimator().run([(circuit, [[["ZII"]], [["XII"]], [["YII"]]], values)]).result()[0]
    assert pub.data.evs.shape == pub.data.stds.shape == pub.data.shape == (3, 2, 2)
    np.testing.assert_allclose(pub.data.evs, expected, atol=3e-14, rtol=0)
    np.testing.assert_array_equal(pub.data.stds, 0)
    assert pub.metadata == {"target_precision": 0.0, "circuit_metadata": {}}


def test_asymmetric_labels_general_observables_and_multiple_pubs():
    circuit = Circuit(3).x(0).h(1).ry(0.4, 2).rz(0.7, 2)
    observables = ["IIZ", "IXI", {"ZII": 0.5, "YXI": -0.3}]
    result = StatevectorEstimator().run([(circuit, observables), (Circuit(1).x(0), PauliZ(0))]).result()
    expected = [-1, 1, 0.5*np.cos(0.4)-0.3*np.sin(0.4)*np.sin(0.7)]
    np.testing.assert_allclose(result[0].data.evs, expected, atol=3e-14, rtol=0)
    np.testing.assert_allclose(result[1].data.evs, -1, atol=3e-14, rtol=0)
    assert result.metadata == {"version": 2}


def test_public_precision_uses_gaussian_noise_not_shots_or_reported_stds():
    circuit = Circuit(1).x(0)
    estimator = StatevectorEstimator(default_precision=0.3, seed=17)
    pubs = [(circuit, ["Z", "X"], None, 0.1), (circuit, "Z")]
    result = estimator.run(pubs, precision=0.2).result()
    np.testing.assert_array_equal(result[0].data.evs, np.random.default_rng(17).normal([-1.0, 0.0], 0.1))
    assert result[1].data.evs == np.random.default_rng(17).normal(-1.0, 0.2)
    assert [pub.metadata["target_precision"] for pub in result] == [0.1, 0.2]
    np.testing.assert_array_equal(result[0].data.stds, 0)
    assert estimator.run([(circuit, "Z")]).result()[0].metadata["target_precision"] == 0.3


def test_projector_observables_use_factorized_native_math_without_exponential_expansion():
    from quantumbridge.primitives.v2 import QiskitError, _observable_expectation
    circuit = Circuit(3).x(0).h(1).ry(0.4, 2).rz(0.7, 2)
    labels = ["II1", "I+I", "r+1", "l+1"]
    state = StatevectorDevice().statevector(circuit)
    values = [_observable_expectation(state, 3, {label: 1.0}, None) for label in labels]
    y = np.sin(0.4)*np.sin(0.7)
    np.testing.assert_allclose(values, [1, 1, (1+y)/2, (1-y)/2], atol=3e-14, rtol=0)
    # These installed public StatevectorEstimator versions support Pauli
    # execution only, despite accepting projector labels in the container.
    with pytest.raises(QiskitError, match="II1"):
        StatevectorEstimator().run([(circuit, labels)]).result()


def test_reset_each_output_prepares_own_trajectory_and_legacy_ensemble_unchanged():
    from quantumbridge.primitives import Estimator
    circuit = Circuit(2).h(0).cx(0, 1).reset(0)
    result = StatevectorEstimator(seed=17).run([(circuit, ["IZ", "ZI", "ZZ"])]).result()[0]
    np.testing.assert_allclose(result.data.evs, [1, 1, -1], atol=3e-14, rtol=0)
    np.testing.assert_array_equal(result.data.stds, 0)
    assert abs(Estimator().run(circuit, PauliZ(1)).expectation_value()) < 3e-14
    repeat = StatevectorEstimator(seed=17).run([(circuit, ["IZ", "ZI", "ZZ"])]).result()[0]
    np.testing.assert_array_equal(repeat.data.evs, result.data.evs)


@pytest.mark.parametrize("bad", ["width", "broadcast", "nonfinite", "owner", "precision"])
def test_later_invalid_pub_prevents_any_quantum_execution(bad, monkeypatch):
    calls = []
    monkeypatch.setattr(StatevectorDevice, "statevector", lambda *a, **k: calls.append(1))
    theta = Parameter("theta")
    circuit = Circuit(1).ry(theta, 0)
    invalid = {
        "width": (Circuit(2), "Z"),
        "broadcast": (circuit, ["X", "Y", "Z"], [[0.1], [0.2]]),
        "nonfinite": (Circuit(1), {"Z": float("nan")}),
        "owner": (circuit, "Z", {Parameter("theta"): [0.1]}),
        "precision": (Circuit(1), "Z", None, float("nan")),
    }[bad]
    with pytest.raises((ValueError, TypeError)):
        StatevectorEstimator().run([(Circuit(1), "Z"), invalid])
    assert calls == []


def test_late_work_overbudget_and_zero_points_do_not_execute(monkeypatch):
    calls = []
    monkeypatch.setattr(StatevectorDevice, "statevector", lambda *a, **k: calls.append(1))
    ledger = UnifiedResourceLedger(UnifiedExecutionLimits(max_derivative_work=3))
    with ResourceScope(ledger), pytest.raises(MemoryError):
        StatevectorEstimator().run([(Circuit(1).h(0), "Z"), (Circuit(1).h(0), "Z")])
    assert calls == []
    theta = Parameter("theta")
    result = StatevectorEstimator().run([(Circuit(1).ry(theta, 0), "Z", np.empty((0, 1)))]).result()
    assert result[0].data.evs.shape == (0,) and calls == []


def test_result_and_memoryview_leases_outlive_job_without_workspace_leak():
    ledger = UnifiedResourceLedger()
    with ResourceScope(ledger):
        job = StatevectorEstimator().run([(Circuit(1).x(0), ["Z", "X"])])
        result = job.result()
        assert job is not result and result is job.result()
        view = memoryview(result[0].data.evs)
    del job, result
    gc.collect()
    assert ledger.receipt()["live_memory_bytes"] == 16
    assert view.tolist() == [-1.0, 0.0]
    del view
    gc.collect()
    assert ledger.receipt()["live_memory_bytes"] == 0


def test_concurrent_jobs_have_real_independent_cached_results():
    estimator = StatevectorEstimator(seed=17)
    with ThreadPoolExecutor(max_workers=4) as pool:
        jobs = list(pool.map(lambda _: estimator.run([(Circuit(1).x(0), "Z")]), range(8)))
    assert len({job.job_id() for job in jobs}) == 8
    for job in jobs:
        assert job.result() is job.result()
        assert job.result()[0].data.evs == -1


def test_actual_default_exports_and_explicit_legacy_identity():
    import quantumbridge as qb
    import quantumbridge.primitives as primitives
    from quantumbridge.primitives.estimator import StatevectorEstimator as ModuleEstimator

    assert qb.StatevectorEstimator is primitives.StatevectorEstimator is ModuleEstimator is StatevectorEstimator
    assert qb.LegacyEstimator is primitives.LegacyEstimator is primitives.Estimator


def test_concurrent_distinct_estimators_collect_storage_inside_execution(monkeypatch):
    original = StatevectorDevice.statevector

    def collecting(*args, **kwargs):
        gc.collect()
        return original(*args, **kwargs)

    monkeypatch.setattr(StatevectorDevice, "statevector", collecting)
    estimators = [StatevectorEstimator(seed=17), StatevectorEstimator(seed=29)]
    with ThreadPoolExecutor(max_workers=4) as pool:
        jobs = list(pool.map(lambda index: estimators[index % 2].run([(Circuit(1).x(0), "Z")]), range(16)))
    assert len({job.job_id() for job in jobs}) == 16
    assert all(job.result()[0].data.evs == -1 for job in jobs)


def test_equal_and_one_below_whole_job_memory_and_parent_child(monkeypatch):
    class RequiredLedger(UnifiedResourceLedger):
        required = 0

        def preflight(self, **amounts):
            self.required = max(self.required, self.receipt()["live_memory_bytes"] + amounts.get("memory_bytes", 0))
            return super().preflight(**amounts)

    probe = RequiredLedger()
    with ResourceScope(probe):
        result = StatevectorEstimator().run([(Circuit(2).h(0), ["IZ", "IX"])]).result()
    budget = probe.required
    del result
    gc.collect()
    exact = UnifiedResourceLedger(UnifiedExecutionLimits(max_total_memory_bytes=budget))
    with ResourceScope(exact):
        job = StatevectorEstimator().run([(Circuit(2).h(0), ["IZ", "IX"])])
        np.testing.assert_allclose(job.result()[0].data.evs, [0, 1], atol=3e-14, rtol=0)
    calls = []
    monkeypatch.setattr(StatevectorDevice, "statevector", lambda *a, **k: calls.append(1))
    parent = UnifiedResourceLedger(UnifiedExecutionLimits(max_total_memory_bytes=budget-1))
    child = UnifiedResourceLedger(parent=parent)
    with ResourceScope(child), pytest.raises(MemoryError):
        StatevectorEstimator().run([(Circuit(2).h(0), ["IZ", "IX"])])
    assert calls == [] and child.receipt()["consumed_tapes"] == 0


def test_runtime_failure_caches_error_and_keeps_completed_work(monkeypatch):
    calls = []
    original = StatevectorDevice.statevector

    def failing(*args, **kwargs):
        calls.append(1)
        if len(calls) == 2:
            raise RuntimeError("injected second cell")
        return original(*args, **kwargs)

    monkeypatch.setattr(StatevectorDevice, "statevector", failing)
    ledger = UnifiedResourceLedger()
    with ResourceScope(ledger):
        job = StatevectorEstimator().run([(Circuit(1).x(0), ["Z", "X"])])
    for _ in range(2):
        with pytest.raises(RuntimeError, match="injected second cell"):
            job.result()
    assert calls == [1, 1]
    gc.collect()
    receipt = ledger.receipt()
    assert receipt["consumed_tapes"] == 1 and receipt["consumed_derivative_work"] > 0
    assert receipt["live_memory_bytes"] == 0
    assert "primitive_failed_estimator_work" in receipt["unavailable"]
