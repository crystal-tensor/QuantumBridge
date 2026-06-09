# This file is independently implemented for QuantumBridge SDK.
# No source code from PennyLane-Qiskit was copied.

from quantumbridge.compat.pennylane_qiskit import (
    dependency_available,
    run_with_upstream_pennylane_qiskit_if_available,
    validate_pennylane_qiskit_dependencies,
)


def test_upstream_plugin_passthrough_is_optional_and_explicit():
    dependency = validate_pennylane_qiskit_dependencies()
    result = run_with_upstream_pennylane_qiskit_if_available()
    assert dependency["required_by_default"] is False
    assert result.validate() is True
    assert result.production_ready is False
    if dependency_available():
        assert result.unsupported_reason is None
    else:
        assert "not installed" in result.unsupported_reason
