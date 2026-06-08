from quantumbridge.compiler import CircuitOptimizationPass
from quantumbridge.core import Circuit


def test_circuit_optimization_cancels_adjacent_inverse():
    result = CircuitOptimizationPass().run(Circuit(1).x(0).x(0).rz(0.0, 0))
    assert result.circuit.operations == []
