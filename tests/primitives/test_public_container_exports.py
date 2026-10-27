# Copyright 2026 QuantumBridge Contributors. Apache-2.0.
"""Canonical public result types and explicit, unchanged Legacy behavior."""

import inspect

import pytest

import quantumbridge as qb
import quantumbridge.primitives as primitives
from quantumbridge.primitives import containers, legacy_containers, v2
from quantumbridge.providers import Backend
from quantumbridge.utils.math import PauliZ


@pytest.mark.parametrize(
    "name", ["BitArray", "DataBin", "PubResult", "SamplerPubResult", "PrimitiveResult", "PrimitiveJob"]
)
def test_canonical_public_type_has_one_actual_native_class(name):
    expected = getattr(v2, name)
    assert getattr(primitives, name) is getattr(qb, name) is expected
    if name != "PrimitiveJob":
        assert getattr(containers, name) is expected
    circuit = qb.Circuit(1, 1).x(0)
    circuit.measure(0, 0)
    job = primitives.StatevectorSampler(default_shots=4, seed=17).run([circuit])
    result = job.result()
    pub = result[0]
    value = dict(BitArray=pub.data.c, DataBin=pub.data, PubResult=pub,
                 SamplerPubResult=pub, PrimitiveResult=result, PrimitiveJob=job)[name]
    assert isinstance(value, expected)
    assert pub.data.c.get_counts() == {"1": 4}
    assert expected.__module__.startswith("quantumbridge.primitives.")


def test_public_constructors_are_not_shape_selected_legacy_facades():
    assert str(inspect.signature(primitives.BitArray)) == "(array, num_bits)"
    assert str(inspect.signature(primitives.DataBin)) == "(*, shape=(), **fields)"
    assert issubclass(primitives.SamplerPubResult, primitives.PubResult)
    for name in ("BitArray", "DataBin", "PubResult", "PrimitiveResult"):
        legacy = getattr(legacy_containers, name)
        assert getattr(primitives, "Legacy" + name) is legacy
        assert getattr(qb, "Legacy" + name) is legacy
        assert legacy is not getattr(primitives, name)
        assert legacy.__module__ == "quantumbridge.primitives.legacy_containers"


def test_explicit_legacy_container_keeps_original_dict_list_and_identity():
    data = legacy_containers.DataBin(
        counts={"1": 10}, quasi_dists={"1": 1.0},
        meas=legacy_containers.BitArray.from_counts({"1": 10}, num_bits=1),
    )
    result = legacy_containers.PrimitiveResult([
        legacy_containers.PubResult(data, {"pub_index": 0})
    ], {"primitive": "SamplerV2"})
    assert len(result) == 1 and len(result[0].data) == 3
    assert result[0].data.counts == {"1": 10}
    assert result[0].data["quasi_dists"] == {"1": 1.0}
    assert result[0].data.meas.get_counts() == {"1": 10}
    assert result.to_dict()["results"][0]["metadata"]["pub_index"] == 0
    assert result.tolist()[0] is result[0]
    assert result.result() is result and result.job_id() == "quantumbridge-primitive-result"


@pytest.mark.parametrize("backend", [False, True])
def test_legacy_internal_callers_use_explicit_legacy_types(backend):
    sampler = primitives.BackendSampler(Backend(max_qubits=1), shots=8) if backend else primitives.Sampler(shots=8)
    estimator = primitives.BackendEstimator(Backend(max_qubits=1)) if backend else primitives.Estimator()
    sample = sampler.run_pubs([(qb.Circuit(1).x(0),)])
    estimate = estimator.run_pubs([(qb.Circuit(1).x(0), PauliZ(0))])
    for result in (sample, estimate):
        assert isinstance(result, legacy_containers.PrimitiveResult)
        assert isinstance(result[0], legacy_containers.PubResult)
        assert isinstance(result[0].data, legacy_containers.DataBin)
        assert result.result() is result and result.job_id() == "quantumbridge-primitive-result"
    assert sample[0].data.meas.get_counts() == {"1": 8}
    assert isinstance(sample[0].data.meas, legacy_containers.BitArray)
    assert estimate[0].data.evs == -1.0
