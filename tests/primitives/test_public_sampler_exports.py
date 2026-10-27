# Copyright 2026 QuantumBridge Contributors. Apache-2.0.
import inspect
import numpy as np
import pytest

import quantumbridge as qb
import quantumbridge.primitives as primitives
from quantumbridge.primitives.v2 import StatevectorSampler as NativePublicSampler


def test_target_default_is_the_native_public_class_not_a_legacy_alias():
    assert qb.StatevectorSampler is primitives.StatevectorSampler is NativePublicSampler
    assert primitives.LegacySampler is primitives.Sampler is qb.LegacySampler
    assert primitives.StatevectorSampler is not primitives.Sampler
    assert list(inspect.signature(qb.StatevectorSampler).parameters) == ["default_shots", "seed"]
    assert qb.StatevectorSampler.__module__ == "quantumbridge.primitives.v2"
    with pytest.raises(TypeError):
        qb.StatevectorSampler(shots=16)


def test_public_export_executes_and_legacy_container_export_remains_unchanged():
    circuit = qb.Circuit(1, 1).x(0)
    circuit.measure(0, 0)
    job = qb.StatevectorSampler(default_shots=4).run([circuit])
    result = job.result()
    assert isinstance(result[0], primitives.SamplerPubResult)
    np.testing.assert_array_equal(result[0].data.c.array, [[1]]*4)
    legacy = primitives.LegacySampler(shots=4).run([(qb.Circuit(1).x(0),)])
    assert isinstance(legacy, primitives.PrimitiveResult)
    assert legacy.result() is legacy and legacy.job_id() == "quantumbridge-primitive-result"
