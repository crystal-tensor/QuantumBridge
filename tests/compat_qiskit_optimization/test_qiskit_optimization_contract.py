# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit Optimization was copied.

from quantumbridge.compat import qiskit_optimization
from quantumbridge.compat.qiskit_contract_helpers import assert_qiskit_contract


def test_qiskit_optimization_contract():
    assert_qiskit_contract(qiskit_optimization)
