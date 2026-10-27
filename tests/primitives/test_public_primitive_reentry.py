# Copyright 2026 QuantumBridge Contributors. Apache-2.0.
"""Real nested execution, failure recovery and cross-instance lock ordering."""

import gc
import subprocess
import sys
from threading import local

import pytest

from quantumbridge import Circuit, StatevectorEstimator, StatevectorSampler
from quantumbridge.devices import StatevectorDevice


@pytest.mark.parametrize("same_instance", [True, False])
def test_nested_estimator_run_preserves_outer_and_inner_jobs(same_instance, monkeypatch):
    outer = StatevectorEstimator()
    inner = outer if same_instance else StatevectorEstimator()
    original, depth, nested = StatevectorDevice.statevector, local(), []

    def reenter(*args, **kwargs):
        if not getattr(depth, "active", False):
            depth.active = True
            try:
                nested.append(inner.run([(Circuit(1).x(0), "Z")]))
                gc.collect()
            finally:
                depth.active = False
        return original(*args, **kwargs)

    monkeypatch.setattr(StatevectorDevice, "statevector", reenter)
    job = outer.run([(Circuit(1), "Z")])
    assert job.result()[0].data.evs == 1 and nested[0].result()[0].data.evs == -1
    assert job.job_id() != nested[0].job_id() and not outer._pending and not inner._pending


def test_nested_failed_job_releases_locks_and_preserves_later_execution(monkeypatch):
    estimator = StatevectorEstimator()
    original, depth, nested = StatevectorDevice.statevector, local(), []

    def fail_nested(*args, **kwargs):
        if getattr(depth, "active", False):
            raise RuntimeError("nested injected failure")
        depth.active = True
        try:
            failed = estimator.run([(Circuit(1), "Z")])
            nested.append(failed)
            for _ in range(2):
                with pytest.raises(RuntimeError, match="nested injected failure"):
                    failed.result()
        finally:
            depth.active = False
        gc.collect()
        return original(*args, **kwargs)

    monkeypatch.setattr(StatevectorDevice, "statevector", fail_nested)
    assert estimator.run([(Circuit(1), "Z")]).result()[0].data.evs == 1
    monkeypatch.setattr(StatevectorDevice, "statevector", original)
    assert estimator.run([(Circuit(1).x(0), "Z")]).result()[0].data.evs == -1
    assert not estimator._pending


def test_nested_sampler_and_estimator_share_reentrant_execution_boundary(monkeypatch):
    estimator, sampler = StatevectorEstimator(), StatevectorSampler(seed=17)
    original, depth, nested = StatevectorDevice.statevector, local(), []

    def sampling(*args, **kwargs):
        if not getattr(depth, "active", False):
            depth.active = True
            try:
                nested.append(sampler.run([Circuit(1).x(0).measure_all()], shots=3))
            finally:
                depth.active = False
        return original(*args, **kwargs)

    monkeypatch.setattr(StatevectorDevice, "statevector", sampling)
    assert estimator.run([(Circuit(1), "Z")]).result()[0].data.evs == 1
    assert next(iter(nested[0].result()[0].data.values())).get_counts() == {"1": 3}


def test_two_threads_cross_instance_nested_jobs_terminate_with_correct_results():
    # A subprocess bounds a genuine cyclic-lock regression, including its
    # worker cleanup. The barrier is only a rendezvous opportunity: serialized
    # execution is allowed and must not require another admitted worker.
    code = '''
import faulthandler
import gc
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier, BrokenBarrierError, local
from quantumbridge import Circuit, StatevectorEstimator
from quantumbridge.devices import StatevectorDevice
faulthandler.dump_traceback_later(3)
estimators = [StatevectorEstimator(), StatevectorEstimator()]
barrier, depth = Barrier(2), local()
original = StatevectorDevice.statevector
def nested(circuit, *args, **kwargs):
    if not getattr(depth, "active", False):
        depth.active = True
        try:
            try:
                barrier.wait(timeout=0.25)
            except BrokenBarrierError:
                pass
            job = estimators[1-depth.index].run([(Circuit(1).x(0), "Z")])
            assert job.result()[0].data.evs == -1
            gc.collect()
        finally:
            depth.active = False
    return original(circuit, *args, **kwargs)
StatevectorDevice.statevector = nested
def run(index):
    depth.index = index
    return estimators[index].run([(Circuit(1), "Z")]).result()[0].data.evs.item()
with ThreadPoolExecutor(max_workers=2) as pool:
    assert list(pool.map(run, (0, 1))) == [1, 1]
faulthandler.cancel_dump_traceback_later()
print("nested-cross-instance-complete")
'''
    try:
        result = subprocess.run([sys.executable, "-s", "-c", code], capture_output=True,
                                text=True, timeout=6, check=False)
    except subprocess.TimeoutExpired as error:
        pytest.fail("Cross-instance nested execution did not terminate: " + str(error.stderr))
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "nested-cross-instance-complete"
