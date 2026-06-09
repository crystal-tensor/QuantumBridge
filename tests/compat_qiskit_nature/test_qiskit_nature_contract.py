# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit Nature was copied.

from quantumbridge.compat import qiskit_nature
from quantumbridge.compat.qiskit_contract_helpers import assert_qiskit_contract


def test_qiskit_nature_contract():
    assert_qiskit_contract(qiskit_nature)
    assert "band-gap" not in qiskit_nature.get_dependency_report()["warnings"][0].lower()
