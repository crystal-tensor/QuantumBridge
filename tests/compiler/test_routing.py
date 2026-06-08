from quantumbridge.compiler import BasicRoutingPass, CouplingMap, SwapInsertionPass
from quantumbridge.core import Circuit


def test_basic_routing_reports_unsupported_interaction():
    circuit = Circuit(3).cx(0, 2)
    result = BasicRoutingPass(CouplingMap([(0, 1), (1, 2)])).run(circuit)
    assert result.analyses["routing_required"]


def test_swap_insertion_adds_swap_for_nonlocal_gate():
    circuit = Circuit(3).cx(0, 2)
    result = SwapInsertionPass(CouplingMap([(0, 1), (1, 2)])).run(circuit)
    assert result.analyses["inserted_swaps"] == 1
