# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit or PennyLane was copied.

from quantumbridge.compat.pennylane_full.operations_adapter import quantumbridge_ir_fragment_to_pennylane_operation
from quantumbridge.compat.pennylane_full.qos_uqci_bridge import validate_qos_uqci_job_spec


def test_unsupported_ir_fragment_returns_structured_capability():
    unsupported = quantumbridge_ir_fragment_to_pennylane_operation({"op": "unknown_gate", "wires": [0]})
    assert unsupported["supported"] is False
    assert "unknown_gate" in unsupported["reason"]
    assert unsupported["provenance"]["source_code_copied"] is False


def test_invalid_qos_uqci_job_spec_fails_closed():
    try:
        validate_qos_uqci_job_spec({"target": "qos_uqci", "source": "pennylane"})
    except ValueError as exc:
        assert "missing fields" in str(exc)
    else:
        raise AssertionError("invalid QOS-UQCI job spec must not validate")
