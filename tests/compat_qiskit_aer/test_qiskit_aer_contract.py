# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit Aer was copied.

from quantumbridge.compat import qiskit_aer
from quantumbridge.compat.qiskit_contract_helpers import assert_qiskit_contract


def test_qiskit_aer_contract():
    assert_qiskit_contract(qiskit_aer)
