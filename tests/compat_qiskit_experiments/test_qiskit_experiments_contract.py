# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit Experiments was copied.

from quantumbridge.compat import qiskit_experiments
from quantumbridge.compat.qiskit_contract_helpers import assert_qiskit_contract


def test_qiskit_experiments_contract():
    assert_qiskit_contract(qiskit_experiments, advisory=True, offline_only=True)
