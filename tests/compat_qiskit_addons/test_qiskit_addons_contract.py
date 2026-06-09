# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit Addons was copied.

from quantumbridge.compat import qiskit_addons
from quantumbridge.compat.qiskit_contract_helpers import assert_qiskit_contract


def test_qiskit_addons_contract():
    assert_qiskit_contract(qiskit_addons, advisory=True)
