# Copyright 2026 QuantumBridge Contributors. Apache-2.0.
"""End-to-end native public Sampler execution, not legacy result aliases."""
from concurrent.futures import ThreadPoolExecutor
import gc
from math import pi

import numpy as np
import pytest

from quantumbridge import Circuit, ClassicalRegister, Parameter
from quantumbridge.devices import StatevectorDevice
from quantumbridge.execution.resource_context import ResourceScope
from quantumbridge.execution.resource_ledger import UnifiedResourceLedger
from quantumbridge.execution.resource_limits import UnifiedExecutionLimits


@pytest.fixture
def sampler_type():
    from quantumbridge.primitives.v2 import StatevectorSampler
    return StatevectorSampler


def measured(angle=None):
    circuit = Circuit(1, 1)
    circuit.x(0) if angle is None else circuit.ry(angle, 0)
    circuit.measure(0, 0)
    return circuit


def test_public_sampler_real_job_and_nd_parameter_shape(sampler_type):
    theta = Parameter("theta")
    values = np.array([[[0.], [pi]], [[pi], [0.]]])
    job = sampler_type(default_shots=5, seed=11).run([(measured(theta), values, 3)], shots=7)
    result = job.result()
    assert job is not result and result is job.result()
    assert job.done() and not job.cancelled() and not job.running()
    assert result.metadata == {"version": 2}
    assert result[0].data.shape == (2, 2)
    bits = result[0].data.c
    assert bits.shape == (2, 2) and bits.num_bits == 1 and bits.num_shots == 3
    assert bits.array.dtype == np.uint8 and bits.array.shape == (2, 2, 3, 1)
    for loc, expected in zip(np.ndindex((2, 2)), ["0", "1", "1", "0"]):
        assert bits.get_bitstrings(loc) == [expected]*3
        assert bits.get_counts(loc) == {expected: 3}
    assert result[0].metadata["shots"] == 3


def test_actual_shots_precedence_multiple_pubs_and_generator(sampler_type):
    sampler = sampler_type(default_shots=5, seed=11)
    assert sampler.run([measured()]).result()[0].data.c.num_shots == 5
    result = sampler.run(iter([measured(), (measured(), None, 13)]), shots=7).result()
    assert [pub.data.c.num_shots for pub in result] == [7, 13]
    assert result[1].data.c.get_counts() == {"1": 13}


def test_nonzero_cross_byte_registers_and_noncontiguous_measurements(sampler_type):
    a, b = ClassicalRegister(2, "alpha"), ClassicalRegister(9, "beta")
    circuit = Circuit(3)
    circuit.add_register(a, b)
    circuit.x(0).x(2)
    circuit.measure(2, a[0]).measure(0, a[1])
    circuit.measure(2, b[8]).measure(0, b[7]).measure(2, b[6]).measure(1, b[1])
    pub = sampler_type(default_shots=4, seed=11).run([circuit]).result()[0]
    assert pub.data.alpha.get_counts() == {"11": 4}
    assert pub.data.beta.get_bitstrings() == ["111000000"]*4
    np.testing.assert_array_equal(pub.data.alpha.array, np.full((4, 1), 3, dtype=np.uint8))
    np.testing.assert_array_equal(pub.data.beta.array, np.tile(np.array([[1, 192]], dtype=np.uint8), (4, 1)))
    assert pub.data.beta.get_counts() == {"111000000": 4}


def test_true_memory_not_sorted_count_expansion_and_integer_seed_repeat(sampler_type):
    circuit = Circuit(1, 1).h(0)
    circuit.measure(0, 0)
    sampler = sampler_type(default_shots=32, seed=11)
    first, second = (sampler.run([circuit]) for _ in range(2))
    memory = first.result()[0].data.c.get_bitstrings()
    assert "0" in memory and "1" in memory and memory != sorted(memory)
    assert memory == second.result()[0].data.c.get_bitstrings()
    assert first.job_id() != second.job_id()
    advanced = sampler_type(default_shots=32, seed=np.random.default_rng(11))
    assert advanced.run([circuit]).result()[0].data.c.get_bitstrings() != advanced.run([circuit]).result()[0].data.c.get_bitstrings()


def test_later_invalid_pub_prevents_any_quantum_execution(sampler_type, monkeypatch):
    calls = []
    original = StatevectorDevice.sample

    def observed(*args, **kwargs):
        calls.append(1)
        return original(*args, **kwargs)

    monkeypatch.setattr(StatevectorDevice, "sample", observed)
    theta = Parameter("theta")
    with pytest.raises(ValueError):
        sampler_type().run([measured(), (measured(theta), {Parameter("other"): .2})])
    assert calls == []


def test_later_pub_over_shot_budget_prevents_any_quantum_execution(sampler_type, monkeypatch):
    calls = []
    original = StatevectorDevice.sample

    def observed(*args, **kwargs):
        calls.append(1)
        return original(*args, **kwargs)

    monkeypatch.setattr(StatevectorDevice, "sample", observed)
    resources = UnifiedResourceLedger(UnifiedExecutionLimits(max_total_shots=15))
    with ResourceScope(resources), pytest.raises(MemoryError):
        sampler_type(default_shots=8).run([measured(), measured()])
    assert calls == [] and resources.receipt()["consumed_shots"] == 0


def test_packed_result_memoryview_outlives_job_and_result(sampler_type):
    resources = UnifiedResourceLedger()
    with ResourceScope(resources):
        job = sampler_type(default_shots=4).run([measured()])
        result = job.result()
        view = memoryview(result[0].data.c.array)
    del job, result
    gc.collect()
    assert view.tolist() == [[1]]*4
    assert resources.receipt()["live_memory_bytes"] == 4
    del view
    gc.collect()
    assert resources.receipt()["live_memory_bytes"] == 0


def test_job_failures_release_work_but_preserve_completed_shots(sampler_type, monkeypatch):
    original = StatevectorDevice.sample
    calls = []

    def failing(device, *args, **kwargs):
        calls.append(1)
        if len(calls) == 2:
            raise RuntimeError("Injected native execution failure")
        return original(device, *args, **kwargs)

    monkeypatch.setattr(StatevectorDevice, "sample", failing)
    resources = UnifiedResourceLedger()
    with ResourceScope(resources):
        job = sampler_type(default_shots=4).run([measured(), measured()])
        assert job.in_final_state() and not job.done()
        for _ in range(2):
            with pytest.raises(RuntimeError, match="Injected"):
                job.result()
    gc.collect()
    assert resources.receipt()["consumed_shots"] == 4
    assert resources.receipt()["reserved_shots"] == 0
    assert resources.receipt()["live_memory_bytes"] == 0


def test_concurrent_jobs_and_cached_reads_have_independent_identity(sampler_type):
    sampler = sampler_type(default_shots=4, seed=11)
    with ThreadPoolExecutor(max_workers=4) as pool:
        jobs = list(pool.map(lambda _: sampler.run([measured()]), range(16)))
        results = list(pool.map(lambda job: job.result(), jobs))
    assert len({job.job_id() for job in jobs}) == 16
    assert all(result is job.result() for result, job in zip(results, jobs))


def test_parameterless_and_zero_parameter_point_shapes(sampler_type):
    from quantumbridge.primitives import BindingsArray, SamplerPub
    theta = Parameter("theta")
    pub = SamplerPub(measured(theta), BindingsArray({theta: np.empty((0, 1))}))
    result = sampler_type(default_shots=3).run([pub, Circuit(1)]).result()
    assert result[0].data.c.array.shape == (0, 3, 1)
    assert result[0].data.c.get_counts() == {}
    assert result[1].data.shape == () and list(result[1].data) == []


def test_exact_and_one_below_whole_job_memory_admission(sampler_type, monkeypatch):
    from quantumbridge.execution.derivative_status import ResourceLimitError
    observed = UnifiedResourceLedger()
    with ResourceScope(observed):
        first = sampler_type(default_shots=4).run([measured()])
        assert first.result()[0].data.c.get_counts() == {"1": 4}
    budget = observed.receipt()["estimated"]["memory_bytes"]
    with ResourceScope(UnifiedResourceLedger(UnifiedExecutionLimits(max_total_memory_bytes=budget))):
        assert sampler_type(default_shots=4).run([measured()]).result()[0].data.c.get_counts() == {"1": 4}
    calls = []
    original = StatevectorDevice.sample

    def counted(*args, **kwargs):
        calls.append(1)
        return original(*args, **kwargs)

    monkeypatch.setattr(StatevectorDevice, "sample", counted)
    parent = UnifiedResourceLedger(UnifiedExecutionLimits(max_total_memory_bytes=budget-1))
    child = UnifiedResourceLedger(parent=parent)
    with ResourceScope(child), pytest.raises(ResourceLimitError):
        sampler_type(default_shots=4).run([measured()])
    assert calls == []
    assert child.receipt()["live_memory_bytes"] == parent.receipt()["live_memory_bytes"] == 0


def test_uuid_collision_is_detected_without_a_shared_global_counter(sampler_type, monkeypatch):
    from quantumbridge.primitives import v2
    monkeypatch.setattr(v2, "uuid4", lambda: "injected-repeat")
    sampler = sampler_type(default_shots=1)
    first = sampler.run([measured()])
    with pytest.raises(RuntimeError, match="collision"):
        sampler.run([measured()])
    assert first.result()[0].data.c.get_counts() == {"1": 1}


def test_unsupported_statevector_width_is_rejected_before_sampling(sampler_type, monkeypatch):
    calls = []
    original = StatevectorDevice.sample

    def counted(*args, **kwargs):
        calls.append(1)
        return original(*args, **kwargs)

    monkeypatch.setattr(StatevectorDevice, "sample", counted)
    with pytest.raises(MemoryError):
        sampler_type(default_shots=1).run([Circuit(128)])
    assert calls == []


def test_zero_points_do_not_materialize_an_unneeded_huge_state(sampler_type):
    from quantumbridge.primitives import BindingsArray, SamplerPub
    theta = Parameter("theta")
    circuit = Circuit(128, 1).ry(theta, 0)
    circuit.measure(0, 0)
    pub = SamplerPub(circuit, BindingsArray({theta: np.empty((0, 1))}))
    bits = sampler_type(default_shots=3).run([pub]).result()[0].data.c
    assert bits.shape == (0,) and bits.array.shape == (0, 3, 1)


def test_excess_parameter_points_are_denied_before_snapshot_copy(sampler_type, monkeypatch):
    from quantumbridge.primitives import BindingsArray
    theta = Parameter("theta")
    calls = []
    original = BindingsArray.as_array

    def counted(*args, **kwargs):
        calls.append(1)
        return original(*args, **kwargs)

    monkeypatch.setattr(BindingsArray, "as_array", counted)
    with pytest.raises(MemoryError):
        sampler_type(default_shots=1).run([(measured(theta), np.zeros((20001, 1)))])
    assert calls == []


def test_shared_parent_serial_admission_and_escaped_result_storage(sampler_type):
    # Use one observed admission requirement plus room for all retained outputs.
    probe = UnifiedResourceLedger()
    with ResourceScope(probe):
        job = sampler_type(default_shots=4).run([measured()])
        job.result()
    budget = probe.receipt()["estimated"]["memory_bytes"]+16*4
    shared = UnifiedResourceLedger(UnifiedExecutionLimits(max_total_memory_bytes=budget))
    sampler = sampler_type(default_shots=4, seed=11)

    def execute(_):
        with ResourceScope(UnifiedResourceLedger(parent=shared)):
            return sampler.run([measured()])

    with ThreadPoolExecutor(max_workers=4) as pool:
        jobs = list(pool.map(execute, range(16)))
    assert len({item.job_id() for item in jobs}) == 16
    assert shared.receipt()["live_memory_bytes"] == 64
    assert shared.receipt()["consumed_shots"] == 64
    assert shared.receipt()["peak_memory_bytes"] <= budget
    del jobs
    gc.collect()
    assert shared.receipt()["live_memory_bytes"] == 0
