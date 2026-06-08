# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit or PennyLane was copied.

import pytest

from quantumbridge.compat.qiskit_addons.aqc_adapter import ADAPTER as AQC
from quantumbridge.compat.qiskit_addons.mpf_adapter import ADAPTER as MPF
from quantumbridge.compat.qiskit_addons.obp_adapter import ADAPTER as OBP
from quantumbridge.compat.qiskit_addons.sqd_adapter import ADAPTER as SQD


def test_qiskit_addons_dependency_inventory_and_version():
    for adapter in (SQD, MPF, AQC, OBP):
        assert isinstance(adapter.dependency_available(), bool)
        assert adapter.get_upstream_version() is None or isinstance(adapter.get_upstream_version(), str)
        assert adapter.list_public_api_inventory()


def test_qiskit_addons_imports_or_clear_errors():
    for adapter in (SQD, MPF, AQC, OBP):
        if adapter.dependency_available():
            assert adapter.list_public_api_inventory()
        else:
            with pytest.raises(ImportError, match="qiskit-addons"):
                adapter.passthrough_class("UnavailableAddonObject")


def test_qiskit_addons_schema_provenance():
    wrapped = SQD.wrap_result({"addon": "sqd-smoke"})
    assert wrapped["schema"] == "quantumbridge.ecosystem.result.v0.1"
    assert wrapped["provenance"]["dependency_extra"] == "qiskit-addons"


def test_qiskit_addons_unsupported_warning():
    with pytest.warns(UserWarning, match="does not implement"):
        SQD.warn_unsupported("functional addon parity")