# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit or PennyLane was copied.

import pytest

from quantumbridge.compat.qiskit_experiments.calibration_adapter import ADAPTER as CALIBRATION
from quantumbridge.compat.qiskit_experiments.experiments_adapter import ADAPTER as EXPERIMENTS
from quantumbridge.compat.qiskit_experiments.tomography_adapter import ADAPTER as TOMOGRAPHY


def test_qiskit_experiments_dependency_inventory_and_version():
    assert isinstance(EXPERIMENTS.dependency_available(), bool)
    assert EXPERIMENTS.get_upstream_version() is None or isinstance(EXPERIMENTS.get_upstream_version(), str)
    assert EXPERIMENTS.list_public_api_inventory()


def test_qiskit_experiments_public_classes_or_clear_error():
    if EXPERIMENTS.dependency_available():
        assert EXPERIMENTS.list_public_api_inventory()
        assert TOMOGRAPHY.list_public_api_inventory()
    else:
        with pytest.raises(ImportError, match="qiskit-experiments"):
            EXPERIMENTS.passthrough_class("BaseExperiment")


def test_qiskit_experiments_schema_provenance():
    wrapped = CALIBRATION.wrap_result({"experiment": "offline-smoke"})
    assert wrapped["schema"] == "quantumbridge.ecosystem.result.v0.1"
    assert wrapped["provenance"]["dependency_extra"] == "qiskit-experiments"


def test_qiskit_experiments_unsupported_warning():
    with pytest.warns(UserWarning, match="does not implement"):
        EXPERIMENTS.warn_unsupported("production calibration workflow")