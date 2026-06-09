# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit Finance was copied.

from quantumbridge.compat import qiskit_finance
from quantumbridge.compat.qiskit_contract_helpers import assert_qiskit_contract


def test_qiskit_finance_contract():
    assert_qiskit_contract(qiskit_finance)
    assert qiskit_finance.production_ready is False
