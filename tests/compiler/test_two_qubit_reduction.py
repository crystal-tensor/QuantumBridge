from quantumbridge.compiler import TwoQubitGateReductionPass
from quantumbridge.core import Circuit


def test_two_qubit_reduction_cancels_double_cx():
    result = TwoQubitGateReductionPass().run(Circuit(2).cx(0, 1).cx(0, 1))
    assert result.circuit.operations == []
