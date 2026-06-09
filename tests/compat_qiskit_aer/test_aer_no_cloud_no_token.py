# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit Aer was copied.

from quantumbridge.compat.qiskit_aer import run_statevector_simulator_native
from quantumbridge.compat.qiskit_aer.aer_upstream_adapter import validate_aer_dependencies
from quantumbridge.core import Circuit


def test_native_aer_slice_never_uses_cloud_token_or_hardware():
    circuit = Circuit(1)
    circuit.h(0)

    result = run_statevector_simulator_native(circuit)

    assert result.metadata["cloud_access"] is False
    assert result.metadata["token_read"] is False
    assert result.metadata["hardware_access"] is False
    assert result.provenance["cloud_access"] is False
    assert result.provenance["token_read"] is False
    assert result.provenance["hardware_access"] is False


def test_upstream_dependency_report_is_local_only():
    report = validate_aer_dependencies()
    assert report["cloud_access"] is False
    assert report["token_read"] is False
    assert report["hardware_access"] is False
