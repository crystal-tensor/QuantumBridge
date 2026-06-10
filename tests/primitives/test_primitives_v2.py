# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
# This file is part of QuantumBridge SDK.
# This implementation is developed for the QuantumBridge native architecture.

from math import cos, pi

from quantumbridge import Circuit, Parameter
from quantumbridge.primitives import DataBin, Estimator, PrimitiveResult, PubResult, Sampler
from quantumbridge.utils.math import PauliX, PauliZ


def test_primitive_result_container_protocol_and_dict_round_trip():
    data = DataBin(counts={"1": 10}, quasi_dists={"1": 1.0})
    result = PrimitiveResult([PubResult(data, {"pub_index": 0})], {"primitive": "SamplerV2"})

    assert len(result) == 1
    assert result[0].data.counts == {"1": 10}
    assert result[0].data["quasi_dists"] == {"1": 1.0}
    assert result.to_dict()["results"][0]["metadata"]["pub_index"] == 0


def test_sampler_v2_accepts_pub_sequence_shots_and_parameter_batches():
    theta = Parameter("theta")
    circuit = Circuit(1).ry(theta, 0)

    result = Sampler(shots=64, seed=7).run(
        [
            {"circuit": Circuit(1).x(0), "shots": 32},
            (circuit, [{"theta": 0.0}, {"theta": pi}], 48),
        ]
    )

    assert isinstance(result, PrimitiveResult)
    assert result.metadata["primitive"] == "SamplerV2"
    assert result[0].data.num_shots == 32
    assert result[0].data.counts == {"1": 32}
    assert result[1].data.num_shots == 48
    assert result[1].data.counts[0] == {"0": 48}
    assert result[1].data.counts[1] == {"1": 48}
    assert result[1].metadata["num_parameter_sets"] == 2


def test_sampler_v2_run_pubs_supports_single_tuple_pub():
    theta = Parameter("theta")
    circuit = Circuit(1).ry(theta, 0)

    result = Sampler(shots=20, seed=3).run_pubs((circuit, {"theta": pi}))

    assert len(result) == 1
    assert result[0].data.counts == {"1": 20}
    assert result[0].metadata["shots"] == 20


def test_estimator_v2_accepts_observable_batches_parameter_batches_and_precision():
    theta = Parameter("theta")
    circuit = Circuit(1).ry(theta, 0)

    result = Estimator(default_precision=0.01).run(
        [
            (circuit, PauliZ(0), [{"theta": 0.0}, {"theta": pi / 3}], 0.001),
            {"circuit": Circuit(1).h(0), "observables": [PauliZ(0), PauliX(0)]},
        ]
    )

    assert isinstance(result, PrimitiveResult)
    assert abs(result[0].data.evs[0] - 1.0) < 1e-12
    assert abs(result[0].data.evs[1] - cos(pi / 3)) < 1e-12
    assert result[0].metadata["precision"] == 0.001
    assert abs(result[1].data.evs[0]) < 1e-12
    assert abs(result[1].data.evs[1] - 1.0) < 1e-12
    assert result[1].metadata["num_observables"] == 2


def test_legacy_primitive_calls_still_return_result_objects():
    assert Sampler(shots=12, seed=1).run(Circuit(1).x(0)).counts() == {"1": 12}
    assert abs(Estimator().run(Circuit(1), PauliZ(0)).expectation_value() - 1.0) < 1e-12
