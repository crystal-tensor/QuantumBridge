# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit Algorithms was copied.

from quantumbridge.compat import qiskit_algorithms
from quantumbridge.compat.qiskit_contract_helpers import assert_qiskit_contract


def test_qiskit_algorithms_contract():
    assert_qiskit_contract(qiskit_algorithms)
