# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit or PennyLane was copied.

import pytest

from quantumbridge.compat.qiskit_runtime.backend_adapter import ADAPTER as BACKEND
from quantumbridge.compat.qiskit_runtime.job_adapter import ADAPTER as JOB
from quantumbridge.compat.qiskit_runtime.runtime_adapter import ADAPTER as RUNTIME


def test_qiskit_runtime_dependency_inventory_and_version():
    assert isinstance(RUNTIME.dependency_available(), bool)
    assert RUNTIME.get_upstream_version() is None or isinstance(RUNTIME.get_upstream_version(), str)
    assert RUNTIME.list_public_api_inventory()


def test_qiskit_runtime_service_and_primitives_availability_or_clear_error():
    if RUNTIME.dependency_available():
        assert RUNTIME.passthrough_class("QiskitRuntimeService") is not None
        inventory_names = {record.public_api for record in RUNTIME.list_public_api_inventory()}
        assert {"SamplerV2", "EstimatorV2"} & inventory_names or {"Sampler", "Estimator"} & inventory_names
    else:
        with pytest.raises(ImportError, match="qiskit-runtime"):
            RUNTIME.passthrough_class("QiskitRuntimeService")


def test_qiskit_runtime_schema_provenance_no_cloud_access():
    wrapped = BACKEND.wrap_result({"backend": "offline-smoke"})
    assert wrapped["schema"] == "quantumbridge.ecosystem.result.v0.1"
    assert wrapped["provenance"]["dependency_extra"] == "qiskit-runtime"
    assert wrapped["provenance"]["official_endorsement"] is False
    assert JOB.to_quantumbridge_schema({"job": "offline"})["is_passthrough"] is True


def test_qiskit_runtime_unsupported_warning():
    with pytest.warns(UserWarning, match="does not implement"):
        RUNTIME.warn_unsupported("IBM cloud execution")