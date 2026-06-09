# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit Machine Learning was copied.

from quantumbridge.compat import qiskit_machine_learning
from quantumbridge.compat.qiskit_contract_helpers import assert_qiskit_contract


def test_qiskit_machine_learning_contract():
    assert_qiskit_contract(qiskit_machine_learning)
    assert qiskit_machine_learning.production_ready is False
