# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit Metal was copied.

from quantumbridge.compat import qiskit_metal
from quantumbridge.compat.qiskit_contract_helpers import assert_qiskit_contract


def test_qiskit_metal_advisory_contract():
    assert_qiskit_contract(qiskit_metal, advisory=True)
    warning_text = " ".join(warning.message for warning in qiskit_metal.get_warnings()).lower()
    assert "chip fabrication" in warning_text
    assert "em solver" in warning_text
