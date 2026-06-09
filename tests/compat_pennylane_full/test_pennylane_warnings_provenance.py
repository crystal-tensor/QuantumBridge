# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit or PennyLane was copied.

from quantumbridge.compat.pennylane_full.warnings import adapter_metadata, get_provenance, get_warnings, unsupported


def test_pennylane_warnings_and_provenance_are_explicit():
    warning = get_warnings()[0]
    provenance = get_provenance()
    metadata = adapter_metadata()
    assert "not a full native PennyLane replacement" in warning.message
    assert provenance.token_storage is False
    assert provenance.cloud_access is False
    assert provenance.source_code_copied is False
    assert metadata["production_ready"] is False
    assert metadata["native_implementation"] is False


def test_pennylane_unsupported_has_structured_warning():
    payload = unsupported("not in Stage 8B").to_dict()
    assert payload["supported"] is False
    assert payload["warnings"]
