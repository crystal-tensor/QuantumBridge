from quantumbridge.compiler import GateDecompositionPass
from quantumbridge.core import Circuit


def test_gate_decomposition_phase_to_rz():
    result = GateDecompositionPass({"rz"}).run(Circuit(1).phase(0.2, 0))
    assert [op.name for op in result.circuit.operations] == ["rz"]
    assert result.changed
