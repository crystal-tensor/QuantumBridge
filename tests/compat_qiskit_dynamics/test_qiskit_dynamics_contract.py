# This file is independently implemented for QuantumBridge SDK.
# No source code from Qiskit Dynamics was copied.

from quantumbridge.compat import qiskit_dynamics
from quantumbridge.compat.qiskit_contract_helpers import assert_qiskit_contract


def test_qiskit_dynamics_contract():
    assert_qiskit_contract(qiskit_dynamics, advisory=True)
