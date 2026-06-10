# Copyright 2026 QuantumBridge Contributors.
# Licensed under the Apache License, Version 2.0.
# This file is part of QuantumBridge SDK.
# This implementation is developed for the QuantumBridge native architecture.

from math import pi

import pytest

from quantumbridge import Circuit, Parameter
from quantumbridge.providers import Backend, BackendV2, JobStatus, Options, Provider, QiskitBackendNotFoundError
from quantumbridge.utils.math import PauliZ


def test_provider_discovers_named_backends_and_raises_not_found():
    provider = Provider()

    assert provider.backend_names() == ["qasm_simulator", "statevector"]
    assert provider.get_backend("statevector").name == "statevector"
    assert [backend.name for backend in provider.backends(simulator=True)] == ["statevector", "qasm_simulator"]

    with pytest.raises(QiskitBackendNotFoundError):
        provider.get_backend("missing")


def test_backend_options_configuration_status_and_properties_are_queryable():
    backend = BackendV2(name="limited", max_qubits=3, basis_gates=["x", "h", "cx"], shots=128)
    backend.set_options(memory=True, seed_simulator=11)

    assert backend.options.shots == 128
    assert backend.options.memory is True
    assert backend.configuration()["basis_gates"] == ["x", "h", "cx"]
    assert backend.status()["operational"] is True
    assert len(backend.properties()["qubits"]) == 3


def test_backend_run_returns_qiskit_style_immediate_job_for_statevector_path():
    backend = Provider().get_backend("statevector")
    theta = Parameter("theta")
    circuit = Circuit(1).ry(theta, 0)

    job = backend.run(circuit, parameter_values={"theta": pi}, observable=PauliZ(0))

    assert job.job_id().startswith("statevector-local-")
    assert job.status == "DONE"
    assert job.status() == JobStatus.DONE
    assert job.done()
    assert job.backend() is backend
    assert abs(job.result().expectation_value() + 1.0) < 1e-12
    assert job.to_dict()["status"] == "DONE"


def test_backend_run_supports_shots_batch_circuits_and_per_circuit_parameters():
    backend = Provider().get_backend("qasm_simulator")
    theta = Parameter("theta")
    circuits = [Circuit(1).x(0), Circuit(1).ry(theta, 0)]

    job = backend.run(circuits, shots=20, seed_simulator=2, parameter_values=[{}, {"theta": 0.0}])
    results = job.result()

    assert isinstance(results, list)
    assert results[0].counts() == {"1": 20}
    assert results[1].counts() == {"0": 20}
    assert job.metadata()["num_circuits"] == 2


def test_options_mapping_copy_and_update_protocol():
    options = Options(shots=100)
    options.update_options(seed_simulator=5)
    copied = options.copy()
    copied.shots = 25

    assert options.to_dict() == {"shots": 100, "seed_simulator": 5}
    assert copied.get("shots") == 25
